"""Read Piers' native compatibility-filtered catalog and installed dependencies."""
import importlib
from io import BytesIO
import json
import re
import sys
import sysconfig
from uuid import uuid4
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
MAX_ATTEMPTS = 3
RETRY_DELAY = 0.5
UNSTABLE = "KODI_COMPATIBILITY_CATALOG_UNSTABLE"
# Kodi Piers AddonInfoBuilder accepts these additional characters. They
# belong to the native pagination stream, never to our InstallAddon input.
NATIVE_ADDON_ID = re.compile(r"[a-zA-Z0-9_.@!$-]+")


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


class _CatalogFault(Exception):
    def __init__(self, code, *, retry=False, reason=UNSTABLE):
        super().__init__(code)
        self.code, self.retry, self.reason = code, retry, reason
        self.context = {}


def _cancel_if_requested(cancelled):
    if cancelled is not None and cancelled():
        raise Blocked("CANCELLED_OR_SHUTDOWN")


def _native_page(payload, requested_start, requested_end, previous_total, diagnostic):
    """Use Piers CJSONUtils::HandleLimits and its half-open interval."""
    diagnostic["schema"] = {"response": type(payload).__name__}
    if not isinstance(payload, dict):
        raise _CatalogFault("RESPONSE_SCHEMA")
    limits, items = payload.get("limits"), payload.get("addons", [])
    diagnostic["schema"].update(limits=type(limits).__name__,
                                addons=type(items).__name__ if "addons" in payload else "absent")
    if not isinstance(limits, dict) or not isinstance(items, list):
        raise _CatalogFault("RESPONSE_SCHEMA")
    total = limits.get("total")
    diagnostic["count"] = len(items)
    for key in ("total", "start", "end"):
        value = limits.get(key)
        diagnostic[key] = value if type(value) is int and -10**9 <= value <= 10**9 else None
    if type(total) is not int or total < 0:
        raise _CatalogFault("TOTAL_INVALID")
    end = min(requested_end, total)
    start = min(requested_start, end)
    # The schema allows omitted start/end. They can be inferred only when
    # the first response alone proves complete coverage, never mid-scan.
    complete = requested_start == 0 and total <= requested_end and len(items) == total
    if not complete and ("start" not in limits or "end" not in limits):
        raise _CatalogFault("PAGE_MARKERS_MISSING")
    for key, expected in (("start", start), ("end", end)):
        if key in limits and (type(limits[key]) is not int or limits[key] != expected):
            raise _CatalogFault("PAGE_RANGE_INVALID")
    if len(items) != end - start:
        raise _CatalogFault("PAGE_ROW_COUNT")
    if previous_total is not None and total != previous_total:
        raise _CatalogFault("TOTAL_CHANGED", retry=True)
    if total > PAGE * MAX_PAGES:
        raise _CatalogFault("ROW_LIMIT", reason="KODI_COMPATIBILITY_CATALOG_TOO_LARGE")
    return total, end, items


def _candidate(item):
    ident = item.get("addonid") if isinstance(item, dict) else None
    if not isinstance(ident, str) or not NATIVE_ADDON_ID.fullmatch(ident):
        raise _CatalogFault("ADDON_ID_INVALID")
    if not ADDON_ID.fullmatch(ident):
        return None, None
    try:
        parsed = version(item["version"])
    except (KeyError, ValueError, TypeError):
        raise _CatalogFault("ADDON_VERSION_INVALID") from None
    if (not isinstance(item.get("path"), str)
            or not isinstance(item.get("dependencies"), list)
            or type(item.get("broken")) not in (bool, str)):
        raise _CatalogFault("ADDON_METADATA_SCHEMA")
    return ident, parsed


def _scan(execute, cancelled, emit, confirm_duplicate):
    catalog, versions, seen = {}, {}, {}
    total = None
    start = 0
    for page in range(1, MAX_PAGES + 1):
        _cancel_if_requested(cancelled)
        end = start + PAGE
        diagnostic = {"page": page, "requested_start": start, "requested_end": end,
                      "total": None, "start": None, "end": None, "count": None}
        try:
            try:
                payload = rpc(execute, "Addons.GetAddons", {
                    "installed": False, "enabled": "all",
                    "limits": {"start": start, "end": end},
                    "properties": ["version", "dependencies", "broken", "path"],
                })
            except Blocked:
                raise _CatalogFault("RPC_ERROR", reason="KODI_COMPATIBILITY_RPC_UNAVAILABLE") from None
            _cancel_if_requested(cancelled)
            total, start, items = _native_page(payload, start, end, total, diagnostic)
            for index, item in enumerate(items):
                ident, parsed = _candidate(item)
                if ident is None:
                    continue
                pair = (ident, item["version"])
                if pair in seen:
                    first_page, first = seen[pair]
                    diagnostic["duplicate"] = {"first_page": first_page, "row": index + 1,
                                               "same_metadata": item == first}
                    if first_page != page:
                        raise _CatalogFault("PAGE_OVERLAP", retry=True)
                    if item != first:
                        raise _CatalogFault("DUPLICATE_CONFLICT")
                    if confirm_duplicate is None or not confirm_duplicate(item):
                        raise _CatalogFault("DUPLICATE_UNVERIFIED")
                    continue
                seen[pair] = (page, item)
                if ident in versions and parsed == versions[ident]:
                    raise _CatalogFault("ADDON_VERSION_AMBIGUOUS")
                if ident not in versions or parsed > versions[ident]:
                    catalog[ident], versions[ident] = item, parsed
        except _CatalogFault as error:
            error.context = diagnostic
            raise
        emit("PAGE_OK", **diagnostic)
        if start == total:
            return catalog
    raise _CatalogFault("ROW_LIMIT", reason="KODI_COMPATIBILITY_CATALOG_TOO_LARGE")


def read_catalog(execute, *, cancelled=None, wait=None, revision=None, diagnose=None,
                 confirm_duplicate=None, validate=None):
    """Discard all pages after observed drift, and retry a bounded full scan."""
    debug_id = uuid4().hex[:12]
    for attempt in range(1, MAX_ATTEMPTS + 1):
        def emit(code, **fields):
            if diagnose is not None:
                diagnose(dict(debug_id=debug_id, attempt=attempt, code=code, **fields))

        _cancel_if_requested(cancelled)
        beginning = revision() if revision is not None else None
        try:
            catalog = _scan(execute, cancelled, emit, confirm_duplicate)
            if revision is not None and revision() != beginning:
                raise _CatalogFault("REPOSITORY_CHANGED", retry=True)
            _cancel_if_requested(cancelled)
            if validate is not None:
                try:
                    validate(catalog)
                except Blocked as error:
                    if (str(error) != "CANCELLED_OR_SHUTDOWN" and revision is not None
                            and revision() != beginning):
                        raise _CatalogFault("REPOSITORY_CHANGED", retry=True) from None
                    raise
            if revision is not None and revision() != beginning:
                raise _CatalogFault("REPOSITORY_CHANGED", retry=True)
            _cancel_if_requested(cancelled)
            return catalog
        except _CatalogFault as error:
            will_retry = error.retry and attempt < MAX_ATTEMPTS
            emit(error.code, retry=will_retry, **error.context)
            if not will_retry:
                raise Blocked(error.reason, error.code, debug_id) from None
        _cancel_if_requested(cancelled)
        if wait is not None:
            wait(RETRY_DELAY)


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
