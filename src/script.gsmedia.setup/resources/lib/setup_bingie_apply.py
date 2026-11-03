"""GS Media BINGIE v2 skinshortcuts layout migration for NEW Kodi profiles.

Writes only two script.skinshortcuts userdata files. Refuses to overwrite ANY
pre-existing main menu or properties file. BINGIE 2.2.3 and Skin Shortcuts
2.x are required; v3 userdata JSON uses a different schema and is blocked.
No skin root XML changes or destructive review-patch application.
"""
import ast
import os
import tempfile
from pathlib import Path
import xml.etree.ElementTree as ET
from setup_layout import MENU, WIDGETS, verify as layout_verify

SKIN_ID = "skin.titan.bingie.mod"
MENU_FILENAME = "skin.titan.bingie.mod-mainmenu.DATA.xml"
PROPS_FILENAME = "skin.titan.bingie.mod.properties"
MAIN_IDS = ("xcmate", "filme", "serien", "netflix", "amazonprimevideo",
            "disneyplus", "paramountplus", "appletv", "xxx", "radio",
            "mp3echo", "xvault", "ezmaintenance", "cabertoss")
OLD_STYLE = ("2.",)


def _target_action(label, target):
    if target.startswith("plugin://"):
        if label.startswith("Radio") or label.startswith("MP3 Streams"):
            return 'ActivateWindow(Music,"' + target + '",return)'
        return 'ActivateWindow(Videos,"' + target + '",return)'
    if target.startswith("RunScript(script."):
        return target
    raise ValueError("Untrusted shortcut action")


def _group_id(label, index):
    if index == 0:
        return "xcmate"
    return MAIN_IDS[index] if index < len(MAIN_IDS) else "gsmedia" + str(index)


def render():
    source = layout_verify()
    root = ET.Element("shortcuts")
    properties = []
    for index, row in enumerate(source["menu"]):
        shortcut = ET.SubElement(root, "shortcut")
        ident = _group_id(row["label"], index)
        for key, value in (
            ("defaultID", ident), ("label", row["label"]),
            ("label2", "XC Mate"), ("icon", "DefaultShortcut.png"),
            ("thumb", ""), ("action", _target_action(row["label"], row["target"]))
        ):
            ET.SubElement(shortcut, key).text = value
        # The BINGIE v2 archived widget entries are stored in the .properties
        # list keyed by the group's stable defaultID, with .1, .2 indexes.
        widgets = source["widgets"][:3] if index == 0 else (
            [x for x in source["widgets"][3:] if x[0].lower() == row["label"].lower()]
        )
        for n, (_category, title, url, _state) in enumerate(widgets):
            suffix = "" if n == 0 else "." + str(n)
            props = (
                ("widget" + suffix, "Addon"),
                ("widgetName" + suffix, title),
                ("widgetType" + suffix,
                 "audio" if url.startswith("plugin://plugin.audio.") else "videos"),
                ("widgetTarget" + suffix,
                 "music" if url.startswith("plugin://plugin.audio.") else "videos"),
                ("widgetPath" + suffix, url),
            )
            for key, value in props:
                properties.append(["mainmenu", ident, key, value])
    result = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    return {MENU_FILENAME: result, PROPS_FILENAME:
            repr(properties).encode("utf-8")}


def validate(menu_bytes, props_bytes):
    root = ET.fromstring(menu_bytes)
    if root.tag != "shortcuts":
        return False
    rows = root.findall("shortcut")
    if len(rows) != len(MENU):
        return False
    props = ast.literal_eval(props_bytes.decode("utf-8"))
    if not isinstance(props, list):
        return False
    xcmate = [x for x in props if x[0] == "mainmenu" and x[1] == "xcmate"]
    links = [x[3] for x in xcmate if x[2] in ("widgetPath", "widgetPath.1", "widgetPath.2")]
    expected = [x[2] for x in WIDGETS[:3]]
    return links == expected


def compatible(inventory):
    if not isinstance(inventory, dict) or inventory.get("code") != "READY":
        return False
    addons = inventory.get("addons", {})
    skin = addons.get(SKIN_ID, {})
    shortcuts = addons.get("script.skinshortcuts", {})
    return (skin.get("version") == "2.2.3" and skin.get("enabled") is True and
            str(shortcuts.get("version", "")).startswith(OLD_STYLE) and
            shortcuts.get("enabled") is True)


def inspect_new_profile(folder, inventory):
    """Read-only safety check BEFORE touching any BINGIE XML files."""
    if not compatible(inventory):
        return "VERSION_OR_SKIN_NOT_SUPPORTED"
    original = Path(folder)
    if original.is_symlink():
        return "SYMLINK_BLOCKED"
    dest = original.resolve()
    if dest.name != "script.skinshortcuts":
        return "UNTRUSTED_PATH"
    payload = render()
    if not validate(payload[MENU_FILENAME], payload[PROPS_FILENAME]):
        return "INVALID_TEMPLATE"
    if any((dest / name).is_symlink() for name in payload):
        return "SYMLINK_BLOCKED"
    try:
        for name, raw in payload.items():
            target = dest / name
            if target.exists() and (not target.is_file() or target.read_bytes() != raw):
                return "EXISTING_SKIN_DATA_PRESERVED"
        return "ALREADY_APPLIED" if all((dest / name).exists() for name in payload) else "READY"
    except (OSError, ValueError):
        return "INSPECTION_FAILED"


def apply_new_profile(folder, inventory, user_approved=False):
    """Idempotent if our exact files already exist. Never replace user files."""
    if not user_approved:
        return "NOT_AUTHORIZED"
    status = inspect_new_profile(folder, inventory)
    if status == "ALREADY_APPLIED":
        return status
    if status != "READY":
        return status
    dest = Path(folder).resolve()
    payload = render()
    try:
        dest.mkdir(parents=True, exist_ok=True)
    except OSError:
        return "WRITE_FAILED"
    to_write = [(dest / name, raw) for name, raw in payload.items()
                if not (dest / name).exists()]
    created = []
    try:
        for target, raw in to_write:
            with target.open("xb") as f:
                f.write(raw)
            created.append(target)
    except (OSError, ValueError):
        # Roll back only files we created, never user data.
        for p in created:
            p.unlink(missing_ok=True)
        return "WRITE_FAILED"
    return "APPLIED" if to_write else "ALREADY_APPLIED"
