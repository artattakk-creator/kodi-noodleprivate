"""Read-only installed add-on inventory via Kodi JSON-RPC.

Does not inspect secrets or private profile directories; never mutates Kodi state.
An RPC failure is UNKNOWN, never equivalent to "not installed".
"""
import json
import re

ADDON_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,127}$")
MAX_RPC_BYTES = 3 * 1024 * 1024


def collect(execute_json_rpc):
    """Return {"code": READY|UNKNOWN, "addons": {id: info}}."""
    request = {"jsonrpc": "2.0", "method": "Addons.GetAddons",
               "params": {"installed": True, "enabled": "all",
                          "properties": ["version", "enabled"]},
               "id": 1}
    try:
        raw = execute_json_rpc(json.dumps(request))
        if not isinstance(raw, str) or len(raw) > MAX_RPC_BYTES:
            return {"code": "UNKNOWN", "addons": {}, "reason": "RPC_RESPONSE_INVALID"}
        document = json.loads(raw)
        if not isinstance(document, dict) or document.get("error"):
            return {"code": "UNKNOWN", "addons": {}, "reason": "RPC_ERROR"}
        response = document.get("result", {}).get("addons", [])
        if not isinstance(response, list):
            return {"code": "UNKNOWN", "addons": {}, "reason": "RPC_SCHEMA"}
        items = {}
        for addon in response[:10000]:
            if not isinstance(addon, dict):
                continue
            addon_id = addon.get("addonid")
            if not isinstance(addon_id, str) or not ADDON_ID.fullmatch(addon_id):
                continue
            version = addon.get("version")
            items[addon_id] = {
                "version": version[:60] if isinstance(version, str) else "",
                "enabled": addon.get("enabled") if isinstance(addon.get("enabled"), bool) else None,
            }
        return {"code": "READY", "addons": items, "reason": ""}
    except (AttributeError, TypeError, ValueError, RuntimeError, OSError):
        return {"code": "UNKNOWN", "addons": {}, "reason": "RPC_UNAVAILABLE"}


def snapshot():
    """Call only from a Kodi action, never automatically on Kodi boot."""
    try:
        import xbmc
        return collect(xbmc.executeJSONRPC)
    except (ImportError, AttributeError, RuntimeError):
        return {"code": "UNKNOWN", "addons": {}, "reason": "KODI_UNAVAILABLE"}
