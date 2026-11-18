"""Read Piers' native compatibility-filtered catalog and installed dependencies."""
import importlib
from io import BytesIO
import json
import re
import sys
import sysconfig
from pathlib import Path
import xml.etree.ElementTree as ET

from setup_auto50 import installed, rows
from setup_inventory import ADDON_ID

BINGIE = "skin.titan.bingie.mod"
XCMATE = "plugin.video.xtreammate"
SKIN_SHORTCUTS = "script.skinshortcuts"
PILLOW = "script.module.pil"
BRANDING = "script.gsmedia.xcmate.branding"
MAGIC = ("xbmc.", "kodi.")
PAGE = 200
MAX_PAGES = 12


class Blocked(Exception):
    def __init__(self, reason, addon_id="", dependency=""):
        super().__init__(":".join(part for part in (reason, addon_id, dependency) if part))


def platform(build, condition):
    match = re.match(r"^(\d+)\.\d+(?=[.\s+\-]|$)", (build or "").strip())
    if not match:
        return None
    webos = condition("System.Platform.WebOS")
    if webos:
        return "webos" if match[1] == "22" else None
    if match[1] == "21" and condition("System.Platform.Android"):
        return "android"
    return None


def current_platform(xbmc):
    return platform(xbmc.getInfoLabel("System.BuildVersion"), xbmc.getCondVisibility)


def version(value):
    """Sort by Kodi's epoch, upstream and revision rules."""
    if not isinstance(value, str):
        raise ValueError("UNSUPPORTED_KODI_DEPENDENCY_VERSION")
    match = re.fullmatch(r"(?:(\d+):)?([a-zA-Z0-9.+_@~]+)(?:-([a-zA-Z0-9.+_@~]+))?", value)
    if not match:
        raise ValueError("UNSUPPORTED_KODI_DEPENDENCY_VERSION")

    def component(part):
        ordered = []
        for token in re.findall(r"\d+|\D", (part or "").lower()):
            if token == "~":
                ordered.append((-2, 0))
            elif token.isdigit():
                ordered.append((0, int(token)))
            else:
                ordered.append((1, ord(token)))
        ordered.append((-1, 0))
        return tuple(ordered)

    return int(match[1] or 0), component(match[2]), component(match[3])


def rpc(execute, method, params):
    try:
        raw = execute(json.dumps(dict(jsonrpc="2.0", id=527, method=method, params=params)))
        if len(raw) > 4 * 1024 * 1024:
            raise ValueError
        response = json.loads(raw)
        if "error" in response:
            raise ValueError
        return response["result"]
    except (ValueError, TypeError, RuntimeError, KeyError, OSError):
        raise Blocked("KODI_COMPATIBILITY_RPC_UNAVAILABLE") from None


def details(execute, addon_id):
    response = rpc(execute, "Addons.GetAddonDetails", {
        "addonid": addon_id, "properties": ["version", "dependencies", "broken", "path"],
    })
    addon = response.get("addon")
    if not isinstance(addon, dict) or addon.get("addonid") != addon_id:
        raise Blocked("KODI_COMPATIBILITY_METADATA_UNAVAILABLE", addon_id)
    return addon


def read_catalog(execute):
    """Kodi filters the list by platform and core API before exposing candidates."""
    result = {}
    catalog_total = None
    seen = set()
    for page in range(MAX_PAGES):
        start = PAGE * page
        payload = rpc(execute, "Addons.GetAddons", {
            "installed": False, "enabled": "all", "limits": {"start": start, "end": start + PAGE},
            "properties": ["version", "dependencies", "broken"],
        })
        limits = payload.get("limits", {})
        items = payload.get("addons", [])
        total = limits.get("total")
        if (type(total) is not int or total < 0 or catalog_total not in (None, total)
                or not isinstance(items, list) or limits.get("start") != start
                or limits.get("end") != start + len(items)):
            raise Blocked("KODI_COMPATIBILITY_CATALOG_UNSTABLE")
        catalog_total = total
        for row in items:
            ident = row.get("addonid") if isinstance(row, dict) else None
            if not isinstance(ident, str) or not ADDON_ID.fullmatch(ident):
                raise Blocked("KODI_COMPATIBILITY_CATALOG_UNSTABLE")
            candidate_version = row.get("version", "")
            key = ident, candidate_version
            if key in seen:
                raise Blocked("KODI_COMPATIBILITY_CATALOG_UNSTABLE")
            seen.add(key)
            if ident not in result or version(candidate_version) > version(result[ident]["version"]):
                result[ident] = row
        if start + len(items) >= total:
            return result
        if not items:
            raise Blocked("KODI_COMPATIBILITY_CATALOG_UNSTABLE")
    raise Blocked("KODI_COMPATIBILITY_CATALOG_TOO_LARGE")


def core_addon(addon_id):
    import xbmcvfs
    if not ADDON_ID.fullmatch(addon_id):
        raise ValueError
    path = Path(xbmcvfs.translatePath("special://xbmc/addons/" + addon_id + "/addon.xml"))
    node = ET.parse(path).getroot()
    if node.get("id") != addon_id:
        raise ValueError
    return node


def backward_abi(node):
    backward = node.find("backwards-compatibility")
    return backward.get("abi", "0") if backward is not None else node.get("minversion", "0")


def installed_addon(addon_id):
    import xbmcaddon
    return read_installed_path(addon_id, xbmcaddon.Addon(addon_id).getAddonInfo("path"))


def read_installed_path(addon_id, location):
    import xbmcvfs
    path = Path(xbmcvfs.translatePath(location))
    if not path.is_absolute() or path.name != addon_id or path.is_symlink():
        raise ValueError
    node = ET.parse(path / "addon.xml").getroot()
    if node.get("id") != addon_id:
        raise ValueError
    return path, node


def check_closure(ident, inventory, execute, candidates=None, core=core_addon,
                  installed_manifest=installed_addon, prefer_candidate=False,
                  protected="", allow_disabled_root=False, available_update=lambda _: None):
    """Return before requests with unresolved mandatory dependencies or core ABI."""
    active = inventory["addons"]
    visited = set()
    planned = {}

    def check(addon_id, minimum="0", required="0", prefer=False):
        entry = active.get(addon_id, {})
        have = (entry.get("enabled") is True or allow_disabled_root and addon_id == ident
                or candidates is not None and bool(entry)) and not prefer
        try:
            if addon_id.startswith(MAGIC):
                node = core(addon_id)
                if (version(node.get("version")) < version(minimum)
                        or version(required) < version(backward_abi(node))):
                    raise ValueError
                return
            from_disk = False
            if have and entry.get("version") and version(entry["version"]) >= version(minimum):
                candidate = details(execute, addon_id)
                if entry.get("enabled") is True or installed_manifest is not installed_addon:
                    _, node = installed_manifest(addon_id)
                else:
                    _, node = read_installed_path(addon_id, candidate.get("path", ""))
                compatible_from = backward_abi(node)
                from_disk = version(required) >= version(compatible_from)
            if not from_disk:
                if addon_id == XCMATE and protected:
                    raise ValueError
                candidate = (candidates or {}).get(addon_id)
                if not candidate and candidates is not None and entry:
                    candidate = available_update(addon_id)
                if not candidate:
                    raise ValueError
                # Kodi validates API minversion for the selected repository
                # instance. JSON-RPC exposes only candidate dependency ranges.
                compatible_from = "0"
                planned[addon_id] = candidate.get("version")
            if (version(candidate["version"]) < version(minimum)
                    or version(required) < version(compatible_from)
                    or candidate.get("broken") is not False):
                raise ValueError
            if (addon_id == BINGIE and candidate["version"] != "2.2.3"
                    or addon_id == SKIN_SHORTCUTS and not candidate["version"].startswith("2.")):
                raise ValueError
            if addon_id in visited:
                return
            visited.add(addon_id)
            deps = candidate["dependencies"]
            if not isinstance(deps, list):
                raise ValueError
        except (OSError, ValueError, KeyError, TypeError, RuntimeError, ET.ParseError):
            raise Blocked("BLOCKED_INCOMPATIBLE_DEPENDENCY", ident, addon_id) from None
        for dep in deps:
            if not isinstance(dep, dict) or type(dep.get("optional")) is not bool:
                raise Blocked("KODI_COMPATIBILITY_METADATA_UNAVAILABLE", addon_id)
            child = dep.get("addonid")
            if not isinstance(child, str) or not ADDON_ID.fullmatch(child):
                raise Blocked("KODI_COMPATIBILITY_METADATA_UNAVAILABLE", addon_id)
            if dep["optional"] and child not in active:
                continue
            # Kodi supplies both the nominal API and earliest acceptable version.
            check(child, dep.get("minversion") or dep.get("version") or "0",
                  dep.get("version") or "0")

    # A top-level verification has no caller-specified maximum/minimum ABI.
    check(ident, required="99999:99999", prefer=prefer_candidate)
    return planned


def probe_pillow(installed_manifest=installed_addon):
    """Exercise the actual Kodi Pillow extension, bundled or add-on-local."""
    try:
        root, node = installed_manifest(PILLOW)
        extension = node.find("./extension[@point='xbmc.python.module']")
        directory = (root / extension.get("library", "lib")).resolve()
        if root.resolve() not in directory.parents:
            raise ValueError
        # webOS bundles Pillow in the compiled-in Python's site-packages.
        trusted = {directory, *(Path(sysconfig.get_path(key)).resolve()
                                for key in ("purelib", "platlib"))}
        use_addon_dir = directory.is_dir()
        if use_addon_dir:
            sys.path.insert(0, str(directory))
        try:
            image = importlib.import_module("PIL.Image")
            native = importlib.import_module("PIL._imaging")
            if any(not trusted.intersection(Path(module.__file__).resolve().parents)
                   for module in (image, native)):
                raise ValueError
            png = BytesIO()
            image.new("RGB", (1, 1), (1, 2, 3)).save(png, format="PNG")
            png.seek(0)
            with image.open(png) as sample:
                if sample.getpixel((0, 0)) != (1, 2, 3):
                    raise ValueError
        finally:
            if use_addon_dir:
                sys.path.remove(str(directory))
    except (AttributeError, OSError, ImportError, ValueError, RuntimeError, TypeError, ET.ParseError):
        raise Blocked("BLOCKED_INCOMPATIBLE_DEPENDENCY", PILLOW, "PILLOW_NATIVE_ABI") from None


def manifest():
    return tuple(dict(row, minimum="2.2.3" if row["id"] == BINGIE else row["minimum"])
                 for row in rows())


def count_confirmed(inventory):
    plan = manifest()
    addons = inventory.get("addons", {})
    return sum(installed(inventory, row["id"], row["minimum"])
               and (row["id"] != BINGIE or addons[BINGIE]["version"] == "2.2.3")
               and (row["id"] != SKIN_SHORTCUTS
                    or addons[SKIN_SHORTCUTS]["version"].startswith("2."))
               for row in plan), len(plan)
