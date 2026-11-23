"""Skin, branding and restart verification shared by the wizard and startup service."""
from contextlib import contextmanager
import os
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

from setup_auto50 import installed
from setup_backup27 import atomic, atomic_json, path_at, roots
from setup_bingie_apply import apply_new_profile, inspect_new_profile
from setup_compat27 import BINGIE, BRANDING, Blocked, count_confirmed
from setup_patch import FILES, _manifest, apply as apply_patch, digest, inspect as inspect_patch
from setup_skin_activate_0511 import _rpc, get_current_skin, SETTING

MARKER = "setup-0527-finish.json"
ID = re.compile(r"skin\.[A-Za-z0-9_.-]{1,100}")
SUCCESS = ("restart_pending", "complete")
APPEARANCE = ("lookandfeel.skintheme", "lookandfeel.skincolors", "lookandfeel.font")


def appearance(xbmc):
    preferences = {}
    for setting in APPEARANCE:
        result = _rpc(xbmc.executeJSONRPC, "Settings.GetSettingValue", {"setting": setting}).get("result")
        value = result.get("value") if isinstance(result, dict) else None
        if not isinstance(value, str) or len(value) > 256:
            raise Blocked("SKIN_PREFERENCES_UNAVAILABLE")
        preferences[setting] = value
    return preferences


def preserve_appearance(xbmc, values):
    if set(values) != set(APPEARANCE):
        raise Blocked("SKIN_PREFERENCES_UNAVAILABLE")
    for setting in APPEARANCE:
        if appearance(xbmc)[setting] == values[setting]:
            continue
        written = _rpc(xbmc.executeJSONRPC, "Settings.SetSettingValue",
                       {"setting": setting, "value": values[setting]})
        if written.get("result") is not True:
            raise Blocked("SKIN_PREFERENCES_RESTORE_FAILED")
    if appearance(xbmc) != values:
        raise Blocked("SKIN_PREFERENCES_RESTORE_FAILED")



def marker_path(profile):
    return path_at(Path(profile).resolve(), MARKER)


def read_marker(profile):
    import json
    path = marker_path(profile)
    if not path.exists():
        return None
    if path.stat().st_size > 4096:
        raise ValueError("FINISH_JOURNAL_TOO_LARGE")
    value = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(value, dict) or not ID.fullmatch(value.get("previous_skin", ""))
            or value.get("status") not in ("pending", "rolled_back", "restart_pending", "complete", "failed")):
        raise ValueError("FINISH_JOURNAL_INVALID")
    preferences = value.get("preferences")
    if (not isinstance(preferences, dict) or set(preferences) != set(APPEARANCE)
            or any(not isinstance(text, str) or len(text) > 256 for text in preferences.values())):
        raise ValueError("FINISH_JOURNAL_PREFERENCES_INVALID")
    if value["status"] in (*SUCCESS, "failed") and (
            type(value.get("pid")) is not int or not ID.fullmatch(value.get("selected_skin", ""))):
        raise ValueError("FINISH_JOURNAL_INVALID")
    return value


def write_marker(profile, record, **changes):
    updated = dict(record, **changes)
    atomic_json(marker_path(profile), updated)
    if read_marker(profile) != updated:
        raise Blocked("FINISH_JOURNAL_READBACK_FAILED")
    return updated


def selected_skin(xbmc):
    current = get_current_skin(xbmc.executeJSONRPC)
    actual = xbmc.getSkinDir()
    if current == actual and isinstance(actual, str) and ID.fullmatch(actual):
        return actual
    raise Blocked("KODI_SKIN_STATE_UNAVAILABLE")


class InactiveSkinSettings:
    """Read/write Kodi's skin-specific settings XML while that skin is inactive."""
    def __init__(self, path, xbmc):
        self.path = path
        self.xbmc = xbmc
        self.dirty = False
        self.original = path.read_bytes() if path.exists() else None
        if self.original is not None:
            if len(self.original) > 1024 * 1024 or b"<!DOCTYPE" in self.original.upper():
                raise Blocked("BINGIE_SETTINGS_FORMAT")
            self.root = ET.fromstring(self.original, parser=ET.XMLParser(
                target=ET.TreeBuilder(insert_comments=True)))
        else:
            self.root = ET.Element("settings")
        if self.root.tag != "settings":
            raise Blocked("BINGIE_SETTINGS_FORMAT")

    def _item(self, key):
        # Kodi stores unprefixed IDs within the skin-owned settings file.
        name = key
        matches = [node for node in self.root.findall("setting")
                   if (node.get("id") or node.get("name") or "").lower() == name.lower()]
        if len(matches) > 1 or matches and matches[0].get("type") != "string":
            raise Blocked("BINGIE_SETTINGS_FORMAT")
        return matches[0] if matches else None

    def get(self, key):
        item = self._item(key)
        return (item.text or "") if item is not None else ""

    def set(self, key, value):
        item = self._item(key)
        if item is None:
            item = ET.SubElement(self.root, "setting", id=key, type="string")
        item.text = value
        self.dirty = True

    def flush(self):
        if not self.dirty:
            return
        latest = self.path.read_bytes() if self.path.exists() else None
        if self.xbmc.getSkinDir() == BINGIE or latest != self.original:
            raise Blocked("BINGIE_SETTINGS_CHANGED")
        data = ET.tostring(self.root, encoding="utf-8", xml_declaration=True)
        atomic(self.path, lambda stream: stream.write(data))
        if self.path.read_bytes() != data:
            raise Blocked("BINGIE_SETTINGS_READBACK_FAILED")


@contextmanager
def branding_module():
    from setup_compat27 import installed_addon
    root, _ = installed_addon(BRANDING)
    library = str(root / "resources/lib")
    sys.path.insert(0, library)
    try:
        import branding_patch
        yield branding_patch, root
    finally:
        sys.path.remove(library)


def colors(xbmc, mapping):
    if xbmc.getSkinDir() == BINGIE:
        getter = lambda key: xbmc.getInfoLabel("Skin.String({})".format(key))
        setter = lambda key, value: xbmc.executebuiltin(
            "Skin.SetString({},{})".format(key, value) if value else "Skin.Reset({})".format(key),
            True)
        return getter, setter, lambda: None
    config = InactiveSkinSettings(path_at(mapping["skin_settings"], "settings.xml"), xbmc)
    return config.get, config.set, config.flush


def _branding_matches(module, mapping, package, xbmc):
    getter, _, _ = colors(xbmc, mapping)
    skin, profile = mapping["skin"], mapping["branding"]
    summary = module.status(skin, profile, getter)
    if not (summary.get("state") == "active" and summary["total"] > 0
            and summary["total"] == summary["matched"] and summary["color_total"] > 0
            and summary["color_total"] == summary["color_matched"]):
        return False
    ownership = module._load(profile)
    originals = {row["relative"]: row["old_sha256"] for row in ownership["files"]}
    expected = _manifest(package)["files"]
    for name in FILES:
        target = path_at(skin, name)
        payload = path_at(package, name)
        if digest(payload) != expected[name]["after"]:
            return False
        if (name in originals and originals[name] != expected[name]["after"]
                or name not in originals and digest(target) != expected[name]["after"]):
            return False
    return True


def verify_config(xbmc, mapping, package, inventory):
    from setup_tmdb_apply import verify
    from setup_compat27 import installed_addon
    import xbmcaddon
    done, expected = count_confirmed(inventory)
    if done != expected or expected != 48 or not installed(inventory, BRANDING, "0.2.0"):
        raise Blocked("PACKAGE_VERIFICATION_INCOMPLETE")
    if inspect_new_profile(mapping["shortcuts"], inventory) != "ALREADY_APPLIED":
        raise Blocked("BINGIE_WIDGET_FILES_NOT_VERIFIED")
    xvault, _ = installed_addon("plugin.video.xvault")
    tmdb = xbmcaddon.Addon("plugin.video.themoviedb.helper")
    from setup_tmdb_apply import _paths, _choice, validate_source, MOVIE_SETTING, EPISODE_SETTING
    player_paths = _paths(xvault, mapping["tmdb"])
    if player_paths is None:
        raise Blocked("TMDB_PLAYER_LOCATION_UNVERIFIED")
    source, primary, alt = player_paths
    raw = source.read_bytes()
    if not validate_source(raw):
        raise Blocked("TMDB_PLAYER_SOURCE_UNVERIFIED")
    if not verify(xvault, mapping["tmdb"], tmdb):
        choice = _choice(primary, alt, raw)
        if choice is not None:
            _, movie, episode = choice
            if (tmdb.getSetting(MOVIE_SETTING) in ("", movie)
                    and tmdb.getSetting(EPISODE_SETTING) in ("", episode)):
                raise Blocked("TMDB_PLAYER_NOT_VERIFIED")
    with branding_module() as (module, _):
        if not _branding_matches(module, mapping, package, xbmc):
            raise Blocked("SPACE_BLUE_NOT_VERIFIED")


def apply_config(xbmc, profile, mapping, package, inventory):
    from setup_omega26 import _apply_tmdb_player, _player_result_reusable
    skin = mapping["skin"]
    with branding_module() as (module, root):
        getter, setter, flush = colors(xbmc, mapping)
        current = module.status(skin, mapping["branding"], getter)
        if current["state"] == "not_installed":
            inspected = inspect_patch(package, skin, "2.2.3")
            if inspected.get("code") != "READY":
                raise Blocked("BINGIE_PATCH_" + inspected["code"], BINGIE,
                              inspected.get("file", ""))
            result = apply_patch(package, skin, mapping["patch"], "2.2.3", user_approved=True)
            if result.get("code") not in ("APPLIED_AND_VERIFIED", "ALREADY_PATCHED"):
                raise Blocked("BINGIE_PATCH_" + result["code"], BINGIE)
            mode = getter("splash_screen") or "netflix_default"
            try:
                module.apply(skin, root, mapping["branding"], mode, getter, setter)
                flush()
            except (module.BrandingError, OSError, ValueError, RuntimeError):
                raise Blocked("SPACE_BLUE_APPLY_FAILED", BRANDING) from None
        elif not _branding_matches(module, mapping, package, xbmc):
            raise Blocked("SPACE_BLUE_EXISTING_PATCH_INCOMPLETE", BRANDING)

    layout = apply_new_profile(mapping["shortcuts"], inventory, user_approved=True)
    if layout not in ("APPLIED", "ALREADY_APPLIED", "UPGRADED", "MERGED"):
        raise Blocked("BINGIE_WIDGETS_" + layout, BINGIE)
    player = _apply_tmdb_player()
    if not _player_result_reusable(player):
        raise Blocked(player)
    verify_config(xbmc, mapping, package, inventory)


def native_result(old, new, observations, stable_samples=1):
    """Use Kodi's keep-skin dialog and independent persisted/GUI observations."""
    observed_dialog = False
    stable = None
    samples = 0
    for configured, actual, visible in observations:
        if configured == new and actual == new and visible:
            observed_dialog = True
        if observed_dialog and not visible and configured == actual and actual in (old, new):
            samples = samples + 1 if stable == actual else 1
            stable = actual
            if samples >= stable_samples:
                return actual
        else:
            stable, samples = None, 0
    return None


def native_decision(xbmc, monitor, old, target):
    # JSON-RPC initiates the real Kodi confirmation. A transient new GUI, a
    # silent fallback, or a successful RPC write alone cannot certify a choice.
    reply = _rpc(xbmc.executeJSONRPC, "Settings.SetSettingValue",
                 {"setting": SETTING, "value": target})
    if reply.get("result") is not True:
        raise Blocked("NATIVE_SKIN_SWITCH_REJECTED", target)

    def observations():
        for _ in range(120):
            if monitor.waitForAbort(0.25):
                return
            yield (get_current_skin(xbmc.executeJSONRPC), xbmc.getSkinDir(),
                   xbmc.getCondVisibility("Window.IsVisible(yesnodialog)"))

    result = native_result(old, target, observations(), stable_samples=4)
    if result is None:
        raise Blocked("NATIVE_SKIN_DECISION_UNVERIFIED", target)
    return result


def package_path():
    return Path(__file__).resolve().parents[1] / "skinpatch"


def postboot(xbmc, monitor, profile, inventory, record):
    """Confirm the chosen skin and package/config readback after a full restart."""
    if record["status"] != "restart_pending" or record["pid"] == os.getpid():
        return
    for _ in range(15):
        if monitor.waitForAbort(1):
            return
        try:
            if selected_skin(xbmc) == record["selected_skin"]:
                verify_config(xbmc, roots(profile), package_path(), inventory())
                write_marker(profile, record, status="complete")
                return
        except (Blocked, OSError, RuntimeError, ValueError, ET.ParseError):
            continue
    write_marker(profile, record, status="failed", error="POSTBOOT_VERIFICATION_FAILED")
