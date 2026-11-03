"""Collision-safe BINGIE Skin Shortcuts reconciliation for Kodi 21.3.

Never delete, replace or alter an existing menu entry or property value.
Missing XCMate entries are appended. Conflicting IDs use a new namespaced
XCMate entry, leaving the user's existing entry and widgets untouched.
Both original files are backed up before a transactional write. No arbitrary
code execution: XML and bounded Python literal property lists only.
"""
import ast
import copy
import os
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET

BACKUP_SUFFIX = ".xcmate-0513.bak"
MAX_BYTES = 1048576
MAX_ROWS = 2500


def _decode(menu, props):
    if len(menu) > MAX_BYTES or len(props) > MAX_BYTES:
        raise ValueError("OVERSIZED_SKIN_SHORTCUTS")
    root = ET.fromstring(menu)
    if root.tag != "shortcuts":
        raise ValueError("UNSUPPORTED_MENU_XML")
    items = root.findall("shortcut")
    if len(items) > MAX_ROWS:
        raise ValueError("TOO_MANY_MENU_ITEMS")
    ids = {}
    for row in items:
        ident = row.findtext("defaultID")
        if not ident or ident in ids:
            raise ValueError("MISSING_OR_DUPLICATE_ID")
        ids[ident] = row
    parsed = ast.literal_eval(props.decode("utf-8"))
    if not isinstance(parsed, list) or len(parsed) > MAX_ROWS:
        raise ValueError("INVALID_PROPERTIES_LIST")
    propmap = {}
    for row in parsed:
        if (not isinstance(row, (list, tuple)) or len(row) != 4
                or any(not isinstance(x, str) for x in row)):
            raise ValueError("INVALID_PROPERTIES_ROW")
        key = tuple(row[:3])
        if key in propmap:
            raise ValueError("DUPLICATE_PROPERTIES_KEY")
        propmap[key] = row[3]
    return root, ids, parsed, propmap


def _clone_entry(entry, new_id, alternate):
    node = copy.deepcopy(entry)
    field = node.find("defaultID")
    if field is None:
        raise ValueError("MISSING_DEFAULT_ID")
    field.text = new_id
    if alternate:
        label = node.find("label")
        if label is not None:
            label.text = "XCMate – " + (label.text or new_id)
    return node


def plan(menu, props, template):
    """Pure, no-write plan returning code and precise merged bytes."""
    from setup_bingie_apply import MENU_FILENAME, PROPS_FILENAME
    try:
        actual_root, actual_ids, old_props, old_values = _decode(menu, props)
        expected_root, expected_ids, expected_props, _ = _decode(
            template[MENU_FILENAME], template[PROPS_FILENAME])
        additional_properties = []
        new_menus = 0
        for desired in expected_root.findall("shortcut"):
            base = desired.findtext("defaultID")
            if not base:
                return {"code": "INVALID_TEMPLATE"}
            needs = [p for p in expected_props if p[0] == "mainmenu" and p[1] == base]
            if not needs and base != "xcmate":
                # Menus without widgets still need their original action.
                pass

            def acceptable(dest):
                existing = actual_ids.get(dest)
                if existing is not None and existing.findtext("action") != desired.findtext("action"):
                    return False
                return all((("mainmenu", dest, p[2]) not in old_values or
                            old_values[("mainmenu", dest, p[2])] == p[3])
                           for p in needs)

            alias = "xcmate_auto_" + base
            if acceptable(base):
                target = base
            elif acceptable(alias):
                target = alias
            else:
                return {"code": "CONFLICT", "detail": "CONFLICTING_XCMATE_MENU_" + base}
            if target not in actual_ids:
                node = _clone_entry(desired, target, target != base)
                actual_root.append(node)
                actual_ids[target] = node
                new_menus += 1
            for p in needs:
                key = ("mainmenu", target, p[2])
                if key not in old_values:
                    new_entry = ["mainmenu", target, p[2], p[3]]
                    additional_properties.append(new_entry)
                    old_values[key] = p[3]
        if not additional_properties and not new_menus:
            return {"code": "NO_CHANGE", "menu": menu, "props": props}
        old_props.extend(additional_properties)
        return {"code": "READY",
                "menu": (ET.tostring(actual_root, encoding="utf-8",
                                     xml_declaration=True) if new_menus else menu),
                "props": repr(old_props).encode("utf-8"),
                "detail": "NEW_MENU_" + str(new_menus) + "_NEW_WIDGET_FIELDS_" +
                          str(len(additional_properties))}
    except (ValueError, TypeError, SyntaxError, UnicodeError, ET.ParseError) as exc:
        return {"code": "UNSUPPORTED_FORMAT", "detail": str(exc)[:100]}


def inspect(folder, template):
    """Read-only: distinguishes mergeable profile from an unknown format."""
    from setup_bingie_apply import MENU_FILENAME, PROPS_FILENAME
    dest = Path(folder)
    if dest.is_symlink() or dest.resolve().name != "script.skinshortcuts":
        return {"code": "UNTRUSTED_FOLDER"}
    paths = (dest / MENU_FILENAME, dest / PROPS_FILENAME)
    if not all(p.is_file() and not p.is_symlink() for p in paths):
        return {"code": "MISSING_OR_LINK"}
    try:
        return plan(paths[0].read_bytes(), paths[1].read_bytes(), template)
    except (OSError, ValueError) as exc:
        return {"code": "INSPECTION_FAILED", "detail": type(exc).__name__}


def _atomic_write(path, data):
    fd, temporary = tempfile.mkstemp(dir=str(path.parent), prefix=".xcmate-merge-")
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, str(path))
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def apply(folder, template, user_approved=False):
    """Back up original pair; append only new rows; roll back on failure."""
    from setup_bingie_apply import MENU_FILENAME, PROPS_FILENAME
    if not user_approved:
        return "NOT_AUTHORIZED"
    dest = Path(folder)
    if dest.is_symlink() or dest.resolve().name != "script.skinshortcuts":
        return "UNTRUSTED_FOLDER"
    paths = (dest / MENU_FILENAME, dest / PROPS_FILENAME)
    try:
        if any(p.is_symlink() or not p.is_file() for p in paths):
            return "MISSING_OR_LINK"
        original = [p.read_bytes() for p in paths]
        candidate = plan(original[0], original[1], template)
        if candidate["code"] == "NO_CHANGE":
            return "ALREADY_APPLIED"
        if candidate["code"] != "READY":
            return candidate["code"] + ":" + candidate.get("detail", "")[:75]

        backups = [p.with_name(p.name + BACKUP_SUFFIX) for p in paths]
        for p, raw in zip(backups, original):
            if p.is_symlink():
                return "BACKUP_PATH_BLOCKED"
            if p.exists() and (not p.is_file() or p.read_bytes() != raw):
                return "EXISTING_BACKUP_PRESERVED"
        for backup, raw in zip(backups, original):
            if not backup.exists():
                with backup.open("xb") as output:
                    output.write(raw)
                    output.flush()
                    os.fsync(output.fileno())
        if any(p.read_bytes() != raw for p, raw in zip(paths, original)):
            return "CONCURRENT_USER_CHANGE"

        try:
            for p, raw in zip(paths, (candidate["menu"], candidate["props"])):
                if p.read_bytes() != raw:
                    _atomic_write(p, raw)
            checked = plan(paths[0].read_bytes(), paths[1].read_bytes(), template)
            if checked["code"] == "NO_CHANGE":
                return "MERGED"
            raise ValueError("POST_WRITE_VERIFICATION_FAILED")
        except (ValueError, OSError):
            for p, raw in zip(paths, original):
                try:
                    _atomic_write(p, raw)
                except OSError:
                    return "ROLLBACK_FAILED_MANUAL_RESTORE_REQUIRED"
            return "WRITE_FAILED_ROLLED_BACK"
    except (OSError, ValueError):
        return "WRITE_FAILED"
