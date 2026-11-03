"""Activate Titan BINGIE MOD on Kodi 21.3 only after all patch guards pass.

Kodi's built-in skin change confirmation remains entirely native. On refused,
failed or timed-out change this step stops instead of declaring completion.
Do not bypass the active-skin UI prompt or change any unrelated settings.
"""
import json

SKIN_ID = "skin.titan.bingie.mod"
SETTING = "lookandfeel.skin"


def _rpc(execute, method, params):
    try:
        raw = execute(json.dumps({"jsonrpc": "2.0", "id": 51011,
                                  "method": method, "params": params}))
        result = json.loads(raw)
    except (TypeError, ValueError, RuntimeError, AttributeError):
        return {"error": "RPC_UNAVAILABLE"}
    if not isinstance(result, dict) or "error" in result or "result" not in result:
        return {"error": "RPC_ERROR"}
    return {"result": result["result"]}


def get_current_skin(execute):
    reply = _rpc(execute, "Settings.GetSettingValue", {"setting": SETTING})
    data = reply.get("result")
    if not isinstance(data, dict) or not isinstance(data.get("value"), str):
        return None
    return data["value"]


def activate(execute, inventory, patch_status, shortcut_status, wait=None):
    """Return code; activated only after read-back and Kodi confirmation window."""
    if not isinstance(inventory, dict) or inventory.get("code") != "READY":
        return "SKIN_INVENTORY_UNAVAILABLE"
    sk = inventory.get("addons", {}).get(SKIN_ID, {})
    if sk.get("version") != "2.2.3" or sk.get("enabled") is not True:
        return "BINGIE_VERSION_OR_ENABLED_INVALID"
    sc = inventory.get("addons", {}).get("script.skinshortcuts", {})
    if not str(sc.get("version", "")).startswith("2.") or sc.get("enabled") is not True:
        return "SKINSHORTCUTS_UNAVAILABLE"
    if patch_status.get("code") != "READY" or patch_status.get("pending"):
        return "BINGIE_PATCH_NOT_VERIFIED"
    if shortcut_status != "ALREADY_APPLIED":
        return "BINGIE_WIDGET_FILES_NOT_VERIFIED"

    old = get_current_skin(execute)
    if old is None:
        return "SKIN_SETTING_UNREADABLE"
    if old == SKIN_ID:
        return "ALREADY_ACTIVE"

    write = _rpc(execute, "Settings.SetSettingValue",
                 {"setting": SETTING, "value": SKIN_ID})
    if write.get("result") is not True:
        return "SKIN_SWITCH_REJECTED"

    # Kodi 21 displays its own keep-new-skin confirmation; the installer's
    # nonmodal progress lets the user answer it. Do not bypass this dialog.
    if wait is not None:
        wait(12)
    if get_current_skin(execute) != SKIN_ID:
        return "SKIN_SWITCH_NOT_CONFIRMED"

    # Kodi exposes the actual GUI skin independently of the stored setting.
    gui = _rpc(execute, "GUI.GetProperties", {"properties": ["skin"]})
    skin = gui.get("result", {}).get("skin") if isinstance(gui.get("result"), dict) else None
    if not isinstance(skin, dict) or skin.get("id") != SKIN_ID:
        return "SKIN_GUI_NOT_ACTIVE"
    return "ACTIVE_AND_VERIFIED"
