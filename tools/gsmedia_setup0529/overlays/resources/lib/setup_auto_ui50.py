"""Kodi 21 one-button installer with nonmodal progress and safe stop/resume.

The progress bar measures completed Kodi installs, not invented download bytes.
Kodi itself handles package transfers and approval dialogs.
"""
import os
import re
from contextlib import nullcontext
from pathlib import Path

from setup_auto50 import (new_state, next_step, after_request, after_confirm,
                          after_retry, stop, resume, rows, count_done, advance_stage,
                          reconcile_restart)
from setup_auto_store50 import load, save
from setup_inventory import snapshot
from setup_catalog_0516 import probe as probe_kodi_catalog
from setup_install_pilot import protected_existing, _version
from setup_origin_guard52 import TemporaryOfficialAddonSource, restore as restore_origin_policy



def _diag(event, ident, version=""):
    """Write only allowlisted IDs and short versions, never private Kodi data."""
    import xbmc
    if not re.fullmatch(r"[A-Za-z0-9._-]{3,100}", str(ident)):
        return
    v = str(version)[:64]
    v = v if re.fullmatch(r"[A-Za-z0-9._+-]{0,64}", v) else "unknown"
    xbmc.log("[XC Mate Setup] {} addon={} version={}".format(event, ident, v),
             xbmc.LOGINFO)


def _context():
    import xbmcaddon
    import xbmcvfs
    profile = xbmcvfs.translatePath(
        xbmcaddon.Addon("script.gsmedia.setup").getAddonInfo("profile"))
    return profile


def _stage_text(step, done, total):
    code = step["code"]
    label = step.get("id", "")
    return "Schritt {} von {} | {} | {}".format(
        done + 1, total, "Repository" if code == "INSTALL_REPOSITORY"
        else "Add-on", label)


def _persist(profile, state):
    save(profile, state)
    return state


def _lock():
    import xbmcgui
    return xbmcgui.Window(10000)


def request_stop():
    """Request safe stop without resetting the installation journal."""
    window = _lock()
    window.setProperty("GS_MEDIA_050_CANCEL", "1")


def _apply_skin(profile, inventory):
    import xbmcaddon
    import xbmcvfs
    from setup_patch import inspect as inspect_skin, apply as apply_skin
    from setup_bingie_apply import inspect_new_profile, apply_new_profile
    addon = xbmcaddon.Addon("skin.titan.bingie.mod")
    skin_root = xbmcvfs.translatePath(addon.getAddonInfo("path"))
    package_root = os.path.join(
        xbmcvfs.translatePath(xbmcaddon.Addon("script.gsmedia.setup").getAddonInfo("path")),
        "resources", "skinpatch")
    status = inspect_skin(package_root, skin_root, "2.2.3")
    if status.get("code") != "READY":
        return "SKIN_PATCH_HASH_OR_VERSION_BLOCKED"
    shortcut_dir = xbmcvfs.translatePath("special://profile/addon_data/script.skinshortcuts/")
    status_layout = inspect_new_profile(shortcut_dir, inventory)
    if status_layout not in ("READY", "ALREADY_APPLIED", "OWNED_UPGRADE_READY", "SAFE_MERGE_READY"):
        return "SKIN_SHORTCUTS_CONFLICT:" + status_layout
    backup_root = os.path.join(profile, "skinpatch-060")
    patched = apply_skin(package_root, skin_root, backup_root, "2.2.3",
                         user_approved=True)
    if patched.get("code") not in ("APPLIED_AND_VERIFIED", "ALREADY_PATCHED"):
        return "SKIN_PATCH_FAILED:" + patched.get("code", "UNKNOWN")
    layout = apply_new_profile(shortcut_dir, inventory, user_approved=True)
    if layout not in ("APPLIED", "ALREADY_APPLIED", "UPGRADED", "MERGED"):
        return "SKIN_LAYOUT_FAILED:" + layout
    return "OK"



SPACE_BLUE_ID = "script.gsmedia.xcmate.branding"
SPACE_BLUE_MINIMUM = "0.2.0"


def _space_blue_verified(result):
    """A successful branding installation requires files AND colors."""
    return (isinstance(result, dict) and result.get("state") == "active"
            and isinstance(result.get("total"), int) and result["total"] > 0
            and result.get("matched") == result["total"]
            and isinstance(result.get("color_total"), int)
            and result["color_total"] > 0
            and result.get("color_matched") == result["color_total"])


def _ensure_space_blue_manager(monitor):
    """Ensure approved Pilot branding 0.2.0 is enabled and Kodi-confirmed."""
    import json
    import xbmc
    from setup_auto50 import installed as verified
    current = snapshot()
    if current.get("code") != "READY":
        return "SPACE_BLUE_INVENTORY_UNKNOWN"
    if not verified(current, "repository.gsmedia.pilot"):
        return "SPACE_BLUE_PILOT_REPOSITORY_MISSING"
    if verified(current, SPACE_BLUE_ID, SPACE_BLUE_MINIMUM):
        _diag("SPACE_BLUE_MANAGER_ALREADY_VERIFIED", SPACE_BLUE_ID,
              current["addons"][SPACE_BLUE_ID]["version"])
        return "OK"
    item = current.get("addons", {}).get(SPACE_BLUE_ID, {})
    if isinstance(item, dict) and item.get("version"):
        if _version(item["version"]) < _version(SPACE_BLUE_MINIMUM):
            return "SPACE_BLUE_MANAGER_TOO_OLD"
        if item.get("enabled") is False:
            rpc = json.loads(xbmc.executeJSONRPC(json.dumps({
                "jsonrpc": "2.0", "method": "Addons.SetAddonEnabled",
                "params": {"addonid": SPACE_BLUE_ID, "enabled": True}, "id": 326})))
            if rpc.get("error") or rpc.get("result") != "OK":
                return "SPACE_BLUE_ENABLE_FAILED"
            return ("OK" if verified(snapshot(), SPACE_BLUE_ID,
                                      SPACE_BLUE_MINIMUM)
                    else "SPACE_BLUE_ENABLE_NOT_CONFIRMED")
        return "SPACE_BLUE_MANAGER_NOT_ENABLED"
    from setup_catalog_0516 import probe as catalog_probe
    for attempt in range(6):
        if monitor.abortRequested() or monitor.waitForAbort(4):
            return "SPACE_BLUE_CANCELLED"
        if attempt in (0, 3):
            xbmc.executebuiltin("UpdateAddonRepos")
        if verified(snapshot(), SPACE_BLUE_ID, SPACE_BLUE_MINIMUM):
            return "OK"
        listing = catalog_probe(xbmc.executeJSONRPC, SPACE_BLUE_ID)
        if listing.get("code") == "AVAILABLE":
            if _version(listing.get("version", "")) < _version(SPACE_BLUE_MINIMUM):
                return "SPACE_BLUE_CATALOG_VERSION_TOO_OLD"
            break
    else:
        return "SPACE_BLUE_CATALOG_NOT_READY"
    _diag("SPACE_BLUE_INSTALL_REQUESTED", SPACE_BLUE_ID)
    xbmc.executebuiltin("InstallAddon(" + SPACE_BLUE_ID + ")")
    for _ in range(80):
        if monitor.waitForAbort(2):
            return "SPACE_BLUE_CANCELLED"
        fresh = snapshot()
        if verified(fresh, SPACE_BLUE_ID, SPACE_BLUE_MINIMUM):
            _diag("SPACE_BLUE_INSTALL_CONFIRMED", SPACE_BLUE_ID,
                  fresh["addons"][SPACE_BLUE_ID]["version"])
            return "OK"
    return "SPACE_BLUE_INSTALL_NOT_CONFIRMED"


def _apply_space_blue_branding():
    """Apply and confirm reversible Space Blue on activated BINGIE 2.2.3."""
    import sys
    import xbmc
    import xbmcaddon
    import xbmcvfs
    if xbmc.getSkinDir() != "skin.titan.bingie.mod":
        return "SPACE_BLUE_SKIN_NOT_ACTIVE"
    skin = xbmcaddon.Addon("skin.titan.bingie.mod")
    addon = xbmcaddon.Addon(SPACE_BLUE_ID)
    if _version(addon.getAddonInfo("version")) < _version(SPACE_BLUE_MINIMUM):
        return "SPACE_BLUE_MANAGER_VERSION_INVALID"
    skin_root = xbmcvfs.translatePath(skin.getAddonInfo("path"))
    addon_root = xbmcvfs.translatePath(addon.getAddonInfo("path"))
    user_root = xbmcvfs.translatePath(addon.getAddonInfo("profile"))
    lib = os.path.join(addon_root, "resources", "lib")
    if not os.path.isdir(lib):
        return "SPACE_BLUE_LIBRARY_MISSING"
    def get_color(key):
        return xbmc.getInfoLabel("Skin.String({})".format(key)).strip()
    def set_color(key, value):
        if value:
            xbmc.executebuiltin("Skin.SetString({},{})".format(key, value))
        else:
            xbmc.executebuiltin("Skin.Reset({})".format(key))
    sys.path.insert(0, lib)
    try:
        from branding_patch import (BrandingError, status, apply as apply_brand,
                                   supported, MODE_VIDEOS)
        current = status(skin_root, user_root, get_color)
        if _space_blue_verified(current):
            _diag("SPACE_BLUE_ALREADY_APPLIED", SPACE_BLUE_ID, "0.2.0")
            return "OK"
        if current.get("state") != "not_installed":
            return "SPACE_BLUE_EXISTING_PATCH_INCOMPLETE"
        if not supported(skin_root):
            return "SPACE_BLUE_BINGIE_223_NOT_VERIFIED"
        if xbmc.getCondVisibility("Player.HasMedia"):
            return "SPACE_BLUE_PLAYER_ACTIVE"
        mode = xbmc.getInfoLabel("Skin.String(splash_screen)").strip() or "netflix_default"
        if mode not in MODE_VIDEOS:
            return "SPACE_BLUE_INTRO_MODE_NOT_ENABLED"
        try:
            apply_brand(skin_root, addon_root, user_root, mode,
                        get_color, set_color)
        except (BrandingError, OSError, ValueError, RuntimeError) as exc:
            _diag("SPACE_BLUE_APPLY_FAILED", SPACE_BLUE_ID, type(exc).__name__)
            return "SPACE_BLUE_APPLY_FAILED"
        updated = status(skin_root, user_root, get_color)
        if not _space_blue_verified(updated):
            return "SPACE_BLUE_POSTCONDITION_NOT_CONFIRMED"
        _diag("SPACE_BLUE_APPLIED_AND_VERIFIED", SPACE_BLUE_ID, "0.2.0")
        return "OK"
    except (ImportError, OSError, ValueError, RuntimeError) as exc:
        _diag("SPACE_BLUE_RUNTIME_ERROR", SPACE_BLUE_ID, type(exc).__name__)
        return "SPACE_BLUE_RUNTIME_ERROR"
    finally:
        sys.path.remove(lib)


def _apply_tmdb_player():
    import xbmcaddon
    import xbmcvfs
    from setup_tmdb_apply import apply as apply_player, verify as verify_player
    xvault = xbmcaddon.Addon("plugin.video.xvault")
    tmdb = xbmcaddon.Addon("plugin.video.themoviedb.helper")
    source = xbmcvfs.translatePath(xvault.getAddonInfo("path"))
    target = xbmcvfs.translatePath(tmdb.getAddonInfo("profile"))
    if verify_player(source, target, tmdb):
        return "OK"
    code = apply_player(source, target, tmdb, fresh_profile=True, user_approved=True)
    return "OK" if code == "APPLIED" and verify_player(source, target, tmdb) else "TMDB_PLAYER_" + str(code)[:80]


def _activate_bingie_runtime(inventory, monitor):
    """Verify the installed skin, XML patch and shortcut files before switching."""
    import xbmc
    import xbmcaddon
    import xbmcvfs
    from setup_patch import inspect as inspect_skin
    from setup_bingie_apply import inspect_new_profile, apply_new_profile
    from setup_skin_activate_0511 import activate
    skin_root = xbmcvfs.translatePath(xbmcaddon.Addon(
        "skin.titan.bingie.mod").getAddonInfo("path"))
    setup_root = xbmcvfs.translatePath(xbmcaddon.Addon(
        "script.gsmedia.setup").getAddonInfo("path"))
    package_root = os.path.join(setup_root, "resources", "skinpatch")
    shortcut_dir = xbmcvfs.translatePath(
        "special://profile/addon_data/script.skinshortcuts/")
    patch_status = inspect_skin(package_root, skin_root, "2.2.3")
    shortcut_status = inspect_new_profile(shortcut_dir, inventory)
    if shortcut_status in ("READY", "OWNED_UPGRADE_READY", "SAFE_MERGE_READY"):
        # A fresh shortcut install may be regenerated by Kodi skinshortcuts.
        # Recreate only missing files or upgrade our exact old .properties;
        # never replace customised menus or properties.
        repaired = apply_new_profile(shortcut_dir, inventory, user_approved=True)
        if repaired in ("APPLIED", "ALREADY_APPLIED", "UPGRADED", "MERGED"):
            shortcut_status = inspect_new_profile(shortcut_dir, inventory)
        else:
            shortcut_status = repaired
    if shortcut_status != "ALREADY_APPLIED":
        return "WIDGETS_" + shortcut_status
    return activate(xbmc.executeJSONRPC, inventory, patch_status,
                    shortcut_status, wait=monitor.waitForAbort)


PILOT_BRIDGE_TARGETS = frozenset((
    "script.bingie.helper",
    "script.module.jurialmunkey",
    "script.module.resolveurl",
    "script.module.resolveurl.xxx",
    "plugin.audio.m3sr2019",
    "script.ezmaintenanceplus",
    "plugin.video.cumination",
))


def _native_pilot_bridge(code, step, bridge_lookup):
    """Use an audited, Pilot-owned native dependency parent, never global
    Kodi's lower-version direct target for an approved Pilot-only package.
    No arbitrary Addon ID or unofficial source is admitted.
    """
    if (code not in ("INSTALL_ADDON", "INSTALL_UPGRADE") or
            step.get("source") != "repository.gsmedia.pilot" or
            step.get("id") not in PILOT_BRIDGE_TARGETS):
        return ""
    bridge = bridge_lookup(step["id"], step.get("source", ""),
                           step.get("minimum", ""))
    expected = "script.gsmedia.upgrade." + step["id"]
    return bridge if bridge == expected else ""


def _player_result_reusable(code):
    """Existing user defaults must not block setup or be silently overwritten."""
    return code in ("OK", "TMDB_PLAYER_EXISTING_DEFAULTS_PRESERVED",
                    "TMDB_PLAYER_EXISTING_PLAYER_PRESERVED")


def run():
    import xbmc
    import xbmcgui
    dialog = xbmcgui.Dialog()
    if not (xbmc.getInfoLabel("System.BuildVersion") or "").startswith("21."):
        dialog.ok("XCMate Media Center Setup", "Nur Kodi 21 wird unterstützt.")
        return
    try:
        profile = _context()
        state = load(profile)
        first = state is None
        inventory = snapshot()
    except (ValueError, OSError, RuntimeError, KeyError) as exc:
        dialog.ok("XCMate – Sicherheitsstopp", "Systemprüfung fehlgeschlagen. "
                  "Keine Installation ausgeführt.")
        return
    # Crash recovery is mandatory before any other install work.
    try:
        restore_origin_policy(profile, xbmc.executeJSONRPC)
    except (RuntimeError, OSError, ValueError, TypeError):
        dialog.ok("XCMate – Schutz-Einstellungen",
                  "Kodi konnte die vorige Quelleneinstellung nicht "
                  "automatisch zurücksetzen. Keine Installation wird "
                  "ausgeführt. Details im Kodi-Log.")
        return
    if inventory.get("code") != "READY":
        dialog.ok("XCMate – Sicherheitsstopp",
                  "Die Kodi-Inventur ist nicht verfügbar. Keine Installation.")
        return
    if first:
        protected = protected_existing(inventory)
        if protected:
            # Existing add-ons are not a fatal condition. User consent below
            # remains mandatory, and existing personal profiles remain intact.
            for addon_id in protected:
                _diag("PREINSTALLED_COMPONENT_PRESERVED", addon_id,
                      inventory["addons"].get(addon_id, {}).get("version", ""))
        from setup_auto50 import installed as _verified_component
        for item in rows():
            if _verified_component(inventory, item["id"], item["minimum"]):
                _diag("ALREADY_INSTALLED_VERIFIED", item["id"],
                      inventory["addons"][item["id"]]["version"])
        # Optional image add-ons are preserved, not guessed from display names.
        for addon_id, data in inventory.get("addons", {}).items():
            if "ximage" in addon_id.lower() and isinstance(data, dict):
                _diag("OPTIONAL_EXISTING_ADDON_PRESERVED", addon_id,
                      data.get("version", ""))
        if not dialog.yesno(
            "XCMate – Vollautomatische Einrichtung 0.5.26",
            "Kodi-Einrichtung starten? Vorhandene Add-ons bleiben unverändert; " 
            "fehlende Pakete werden ergänzt. Alle geprüften "
            "Repositories, 48 Komponenten und Abhängigkeiten werden "
            "nacheinander ohne zusätzliche Wizard-Abfragen installiert. "
            "BINGIE 2.2.3 wird nur bei exaktem Datei-Hash gesichert und "
            "eingerichtet. xVAULT als TMDB-Standardplayer nur einrichten, "
            "wenn keine persönlichen Player-Vorgaben überschrieben werden. "
            "Der Space-Blue-Patch (Logo, Splash, Intro und Farbschema) "
            "wird nach BINGIE-Aktivierung mit Sicherung der Originale "
            "verpflichtend installiert; ohne Prüfung kein Abschluss. "
            "Für geprüfte Plugin-Abhängigkeiten kann Kodi die Updatequelle "
            "während eines Installationsschritts kurzzeitig auf alle "
            "Repositories setzen; der alte Zustand wird danach "
            "wiederhergestellt. Systemfreigaben von Kodi und echte Fehler "
            "können zusätzliche Eingaben oder einen sicheren Stopp erfordern. "
            "Jetzt einmalig zustimmen?"
        ):
            return
        from setup_storage92 import initialize as storage92_initialize
        storage92_initialize(profile,True)
        state = new_state()
        _persist(profile, state)
    elif state["stopped"]:
        if not dialog.yesno("XCMate Media Center Setup", "Bisher geprüfte Komponenten "
                            "behalten und die restliche Einrichtung automatisch "
                            "fortsetzen? Space Blue inklusive Intro, Splash und Farben "
                            "wird vor dem Abschluss gesichert und geprüft. "
                            "Für geprüfte Abhängigkeiten kann die "
                            "Kodi-Updatequelle kurzzeitig auf alle Repositories "
                            "gesetzt und anschließend wiederhergestellt werden. "
                            "Die Hash-Schutzprüfungen bleiben aktiv; Kodi-"
                            "Systemfreigaben können separat erscheinen."):
            return
        # Recheck fresh Kodi state before retrying any interrupted request.
        # Already confirmed components are preserved; only failed markers
        # are cleared after this explicit resume approval.
        state = _persist(profile, reconcile_restart(state, inventory))
        state = _persist(profile, resume(state))

    if state.get("stage") == "done" and not state.get("stopped"):
        dialog.ok("XCMate Media Center Setup",
                  "Die Einrichtung wurde bereits geprüft. Kein erneuter "
                  "Download erforderlich. Nach dem Neustart BINGIE aufrufen.")
        return
    window = _lock()
    if window.getProperty("GS_MEDIA_050_RUNNING") == "1":
        dialog.ok("XC Mate", "Installation läuft bereits. Keine zweite "
                  "Instanz starten.")
        return
    window.setProperty("GS_MEDIA_050_RUNNING", "1")
    window.clearProperty("GS_MEDIA_050_CANCEL")
    progress = xbmcgui.DialogProgressBG()
    progress.create("XCMate Media Center Setup – v0.5.26 – Kodi 21.3 Omega", "Systemprüfung")
    monitor = xbmc.Monitor()
    reason = ""
    try:
        for iteration in range(400):
            if monitor.abortRequested() or window.getProperty("GS_MEDIA_050_CANCEL") == "1":
                reason = "CANCELLED_OR_SHUTDOWN"
                state = _persist(profile, stop(state, reason))
                break
            inventory = snapshot()
            step = next_step(state, inventory)
            code = step["code"]
            done, total = count_done(inventory)
            percent = min(96, int(95 * done / max(total, 1)))
            progress.update(percent, "XC Mate: {} / {} Komponenten".format(done, total),
                            _stage_text(step, done, total))
            if code == "CONFIRM":
                state = _persist(profile, after_confirm(state, inventory))
                continue
            if code == "ENABLE_ADDON":
                ident = step["id"]
                # This operation is consented to only on a fresh test device
                # and only for an exact, version-compliant required component.
                import json
                rpc = json.loads(xbmc.executeJSONRPC(json.dumps({
                    "jsonrpc": "2.0", "method": "Addons.SetAddonEnabled",
                    "params": {"addonid": ident, "enabled": True}, "id": 1
                })))
                if rpc.get("error") or rpc.get("result") != "OK":
                    reason = "ENABLE_NOT_CONFIRMED:" + ident
                    state = _persist(profile, stop(state, reason))
                    break
                refreshed = snapshot()
                minimum = step.get("minimum") or next((row["minimum"] for row in rows()
                                if row["id"] == ident), "")
                from setup_auto50 import installed as verified
                if not verified(refreshed, ident, minimum):
                    reason = "ENABLE_NOT_CONFIRMED:" + ident
                    state = _persist(profile, stop(state, reason))
                    break
                continue
            if code in ("INSTALL_REPOSITORY", "INSTALL_ADDON", "INSTALL_UPGRADE"):
                ident = step["id"]
                if not re.fullmatch(r"[A-Za-z0-9._-]{3,100}", ident):
                    raise ValueError("Invalid add-on ID")

                # Kodi Omega InstallAddon(id) is INSTALL-ONLY: if an add-on is
                # already installed, InstallModal returns false without doing
                # an upgrade. For this exact verified BINGIE requirement use
                # a fresh first-party parent addon whose required dependency
                # is Skin Shortcuts >=2.1.0. Kodi's native dependency resolver
                # then installs the newer version from the PARENT repository.
                native_shortcuts = (
                    code in ("INSTALL_ADDON", "INSTALL_UPGRADE")
                    and ident == "script.skinshortcuts"
                    and step.get("source") == "repository.gsmedia.pilot"
                    and _version(step.get("actual", "")) < (2, 1, 0)
                    and step.get("minimum") == "2.1.0"
                )
                # Kodi's global index can show official 1.0.3 rather than
                # BINGIE's required 1.0.5. Use the existing, Pilot-owned
                # native upgrade bridge for missing and older installations.
                native_skinicons = (
                    code in ("INSTALL_ADDON", "INSTALL_UPGRADE")
                    and ident == "resource.images.skinicons.wide"
                    and step.get("source") == "repository.gsmedia.pilot"
                    and step.get("minimum") == "1.0.5"
                    and _version(step.get("actual", "")) < (1, 0, 5)
                )
                # All of these 7 packages and their >=minimum/0.1.0 parent
                # bridges are confirmed in GS Media Pilot's XML and ZIP tree.
                # Choose the original Pilot parent even if the global Kodi
                # Addons.GetAddons query returns an older system package.
                from setup_auto50 import upgrade_bridge_for
                native_pilot_bridge = _native_pilot_bridge(
                    code, step, upgrade_bridge_for)
                native_upgrade = (code == "INSTALL_UPGRADE" or
                                  native_shortcuts or native_skinicons or
                                  bool(native_pilot_bridge))
                native_slyguy_origin_parent = (
                    code == "INSTALL_ADDON"
                    and ident == "slyguy.dependencies"
                    and step.get("source") == "repository.slyguy"
                )
                if native_upgrade:
                    install_id = (
                        "script.gsmedia.skinshortcuts.bridge" if native_shortcuts
                        else "script.gsmedia.upgrade.resource.images.skinicons.wide"
                        if native_skinicons else
                        native_pilot_bridge or step.get("bridge", "")
                    )
                    if (not install_id or
                            step.get("source") not in (
                                "repository.gsmedia.pilot",
                                "repository.titan.bingie.mod",
                                "repository.xbmc.org",
                                "repository.slyguy", "repository.xvault")):
                        reason = "UPGRADE_SOURCE_BLOCKED:" + ident
                        state = _persist(profile, stop(state, reason))
                        break
                else:
                    install_id = ident
                    if native_slyguy_origin_parent:
                        # Kodi Omega CAddonRepos::FindDependencyByParentRepo
                        # searches ONLY the parent's repository for non-Kodi
                        # dependencies. The xcMate 0.5.19 bootstrap originated
                        # in repository.gsmedia.pilot, so it could not resolve
                        # slyguy.dependencies from repository.slyguy.
                        # The ORIGINAL SlyGuy Common has an original requires
                        # on slyguy.dependencies>=0.0.30 and is hosted in
                        # repository.slyguy itself. Installing this parent
                        # first uses Kodi's original same-repository resolver.
                        # No original SlyGuy binaries are redistributed.
                        install_id = "script.module.slyguy"
                    # .22: native Kodi install of the ORIGINAL repository as
                    # its own package. Never request the legacy pilot-origin
                    # script.gsmedia.bingie.bootstrap (dual dependency tree).
                    # After Kodi confirms it, the Helper is a SEPARATE step.
                    if ident == "repository.titan.bingie.mod":
                        _diag("BINGIE_ORIGINAL_REPOSITORY_STAGED", install_id)
                # Kodi 21 GetAddons(installed=true) confirms finished installs;
                # its distinct GetAddons(installed=false) checks the async repo
                # catalog. UpdateAddonRepos queues a refresh; it does not wait
                # for completion. Do not call InstallAddon until visible.
                from setup_auto50 import installed as confirmed
                _diag("CATALOG_REFRESH_REQUESTED", install_id)
                visible = {"code": "NOT_LISTED"}
                missing_catalog_id = install_id
                already_complete = False
                for catalog_attempt in range(6):
                    if monitor.abortRequested() or window.getProperty("GS_MEDIA_050_CANCEL") == "1":
                        reason = "CANCELLED_OR_SHUTDOWN"
                        break
                    if catalog_attempt in (0, 3):
                        xbmc.executebuiltin("UpdateAddonRepos")
                    if monitor.waitForAbort(5):
                        reason = "CANCELLED_OR_SHUTDOWN"
                        break
                    fresh = snapshot()
                    required = step.get("minimum", "")
                    if confirmed(fresh, ident, required):
                        _diag("INSTALLED_WHILE_WAITING_FOR_CATALOG", ident)
                        already_complete = True
                        break
                    if native_shortcuts and confirmed(fresh, install_id):
                        reason = "SHORTCUTS_BRIDGE_PRESENT_DEPENDENCY_UNMET:" + ident
                        _diag("SHORTCUTS_BRIDGE_ALREADY_PRESENT", install_id)
                        break
                    if native_skinicons and confirmed(fresh, install_id):
                        reason = "SKINICONS_BRIDGE_PRESENT_DEPENDENCY_UNMET:" + ident
                        _diag("SKINICONS_BRIDGE_ALREADY_PRESENT", install_id)
                        break
                    if native_pilot_bridge and confirmed(fresh, install_id):
                        # A preinstalled dependency parent cannot be
                        # reinstalled by InstallAddon. Its mere presence is
                        # NOT proof that the required module is satisfactory.
                        reason = "PILOT_BRIDGE_PRESENT_DEPENDENCY_UNMET:" + ident
                        _diag("PILOT_BRIDGE_ALREADY_PRESENT", install_id)
                        break
                    if native_slyguy_origin_parent and confirmed(
                            fresh, install_id):
                        reason = "SLYGUY_PARENT_PRESENT_DEPENDENCY_MISSING:" + ident
                        _diag("SLYGUY_PARENT_ALREADY_INSTALLED", install_id)
                        break
                    visible = probe_kodi_catalog(xbmc.executeJSONRPC, install_id)
                    missing_catalog_id = install_id
                    # The global Kodi catalog may expose an older version.
                    # Fail closed before any request rather than claim PASS.
                    expected = ("0.1.0" if native_upgrade else (step.get("minimum", "") or
                                ("2.0.1" if ident == "repository.titan.bingie.mod"
                                 else "1.1.2" if ident == "script.bingie.helper"
                                 else "")))
                    if (visible["code"] == "AVAILABLE" and expected and
                            _version(visible.get("version", "")) < _version(expected)):
                        reason = "KODI_CATALOG_VERSION_TOO_OLD:" + ident
                        _diag("CATALOG_VERSION_TOO_OLD", ident,
                              visible.get("version", ""))
                        break
                    if visible["code"] == "AVAILABLE" and native_slyguy_origin_parent:
                        dependency = probe_kodi_catalog(
                            xbmc.executeJSONRPC, "slyguy.dependencies")
                        if dependency["code"] != "AVAILABLE":
                            visible = dependency
                            missing_catalog_id = "slyguy.dependencies"
                            _diag("SLYGUY_ORIGINAL_DEP_NOT_VISIBLE", missing_catalog_id)
                        elif (_version(visible.get("version", "")) < (0, 87, 6)
                              or _version(dependency.get("version", "")) < (0, 0, 30)):
                            reason = "SLYGUY_ORIGINAL_CATALOG_VERSION_TOO_OLD"
                            _diag("SLYGUY_ORIGINAL_CATALOG_OLD", install_id,
                                  visible.get("version", ""))
                            break
                        else:
                            _diag("SLYGUY_ORIGINAL_SAME_REPO_PARENT", install_id,
                                  visible.get("version", ""))
                            _diag("SLYGUY_ORIGINAL_DEP_VISIBLE", "slyguy.dependencies",
                                  dependency.get("version", ""))
                    if visible["code"] == "AVAILABLE":
                        _diag("CATALOG_PACKAGE_VISIBLE", install_id,
                              visible.get("version", ""))
                        break
                    _diag("CATALOG_NOT_VISIBLE_TRY_" + str(catalog_attempt + 1),
                          missing_catalog_id)
                if reason:
                    state = _persist(profile, stop(state, reason))
                    break
                if already_complete:
                    continue
                if visible["code"] != "AVAILABLE":
                    reason = "KODI_CATALOG_NOT_READY:" + missing_catalog_id
                    _diag("CATALOG_STOP_NO_INSTALL_REQUEST", missing_catalog_id)
                    state = _persist(profile, stop(state, reason[:200]))
                    break
                # One-time setup consent (initial or resumed) also covers
                # the allowlisted, temporary Kodi dependency source scope.
                # Kodi's own native system prompts cannot be suppressed.
                state = _persist(profile, after_request(state, ident))
                wait = 0
                scope = (
                    TemporaryOfficialAddonSource(
                        profile, xbmc.executeJSONRPC,
                        addon_id="slyguy.dependencies" if native_slyguy_origin_parent
                        else "resource.images.skinicons.wide" if native_skinicons
                        else ident if native_pilot_bridge
                        else "script.skinshortcuts")
                    if (native_upgrade or native_slyguy_origin_parent)
                    else nullcontext()
                )
                # Kodi Omega FindDependency explicitly prefers the OFFICIAL
                # 2.0.3, even for a parent installed from our pilot. Both
                # the temporary consented ANY_REPOSITORY setting AND a fresh
                # bridge dependency are necessary. The scope restores the
                # original Kodi update settings in success, error, and cancel.
                with scope:
                    if native_upgrade:
                        # The bridge's source is this test repository, but Kodi
                        # resolves its pinned original dependency natively.
                        # Refresh repository metadata before asking the resolver.
                        xbmc.executebuiltin("UpdateAddonRepos")
                        if monitor.waitForAbort(4):
                            reason = "CANCELLED_OR_SHUTDOWN"
                            state = _persist(profile, stop(state, reason))
                            break
                    _diag("KODI_INSTALL_REQUESTED", install_id)
                    xbmc.executebuiltin("InstallAddon(" + install_id + ")")

                    # Kodi owns native downloads; these seconds are a wait.
                    while wait < (150 if native_upgrade else 240):
                        if monitor.waitForAbort(2):
                            break
                        if window.getProperty("GS_MEDIA_050_CANCEL") == "1":
                            break
                        wait += 2
                        inv = snapshot()
                        if next_step(state, inv)["code"] == "CONFIRM":
                            break
                        progress.update(
                            percent,
                            "XC Mate: {} / {} Komponenten".format(done, total),
                            "{} – Kodi-Paketpruefung ({} s)".format(ident, wait))

                if (monitor.abortRequested() or
                        window.getProperty("GS_MEDIA_050_CANCEL") == "1"):
                    reason = "CANCELLED_OR_SHUTDOWN"
                    state = _persist(profile, stop(state, reason))
                    break

                final_inventory = snapshot()
                if next_step(state, final_inventory)["code"] != "CONFIRM":
                    actual = final_inventory.get("addons", {}).get(ident, {}).get("version", "")
                    if native_upgrade:
                        reason = "NATIVE_DEPENDENCY_UPGRADE_NOT_CONFIRMED:{} ist={} soll={}".format(
                            ident, actual or "nicht ermittelt",
                            step.get("minimum", "unbekannt"))
                    else:
                        reason = "KODI_INSTALL_NOT_CONFIRMED:" + ident
                    _diag("KODI_INSTALL_NOT_CONFIRMED", ident, actual)
                    state = _persist(profile, stop(state, reason[:200]))
                    break

                _diag("KODI_INSTALL_CONFIRMED", ident)
                state = _persist(profile, after_confirm(state, final_inventory))
                if code == "INSTALL_REPOSITORY":
                    xbmc.executebuiltin("UpdateAddonRepos")
                    monitor.waitForAbort(3)
                continue
            if code == "WAITING":
                # A Kodi process may have terminated during a previous request.
                # Do not automatically repeat installs or create a retry loop.
                reason = "PREVIOUS_INSTALL_NOT_VERIFIED:" + step["id"]
                state = _persist(profile, stop(state, reason[:200]))
                break
            if code in ("SOURCE_BLOCKED", "RETRY_REQUIRED", "INVENTORY_UNAVAILABLE"):
                reason = code + ":" + step.get("id", "") + (
                    ":" + step.get("reason", "") if step.get("reason") else "")
                state = _persist(profile, stop(state, reason[:200]))
                break
            if code == "APPS_PRESENT":
                state = _persist(profile, advance_stage(state, "apps"))
                continue
            if code == "STAGE_SKIN":
                # Installed components are complete. Close the installer modal
                # before XCMate owns its separate native storage dialog.
                progress.close()
                from setup_storage92 import run as storage92_run
                storage92_run(profile)
                progress.create("XCMate – Einrichtung", "Speicherwahl abgeschlossen oder ausdrücklich vertagt")
                progress.update(96, "XCMate – BINGIE",
                                "Prüfe originalen Skin und sichere XML-Dateien")
                # The one-time user approval explicitly covers this
                # hash-verified, rollback-capable first-install skin patch.
                code_ = _apply_skin(profile, inventory)
                if code_ != "OK":
                    reason = code_
                    state = _persist(profile, stop(state, reason))
                    break
                state = _persist(profile, advance_stage(state, "skin"))
                continue
            if code == "STAGE_PLAYER":
                progress.update(97, "XCMate – TMDB",
                                "Prüfe xVAULT-Player für Filme und Serien")
                # Non-destructive TMDB player configuration is covered by
                # the single start confirmation. No separate per-step dialog.
                code_ = _apply_tmdb_player()
                if _player_result_reusable(code_) and code_ != "OK":
                    # Installation of xVAULT is verified in apps stage. User-
                    # selected player preferences must remain unchanged.
                    _diag("TMDB_USER_PLAYER_PREFERENCES_PRESERVED",
                          "plugin.video.xvault")
                if not _player_result_reusable(code_):
                    reason = code_
                    state = _persist(profile, stop(state, reason))
                    break
                state = _persist(profile, advance_stage(state, "player"))
                continue
            if code == "STAGE_CHECK":
                # Do not mark setup as complete just because Kodi reported
                # 43 installed/verified addon IDs.
                player_result = _apply_tmdb_player()
                if not _player_result_reusable(player_result):
                    reason = "TMDB_XVAULT_MANDATORY_UNMET:" + player_result
                    state = _persist(profile, stop(state, reason))
                    break
                progress.update(98, "XCMate – Space Blue vorbereiten",
                                "Verifizierten Space-Blue-Manager installieren")
                branding_manager = _ensure_space_blue_manager(monitor)
                if branding_manager != "OK":
                    reason = branding_manager
                    state = _persist(profile, stop(state, reason))
                    break
                progress.update(98, "XCMate – BINGIE MOD aktivieren",
                                "Kodi kann das Beibehalten des Skins bestätigen lassen")
                skin_result = _activate_bingie_runtime(inventory, monitor)
                if skin_result not in ("ACTIVE_AND_VERIFIED", "ALREADY_ACTIVE"):
                    reason = "BINGIE_NOT_ACTIVE:" + skin_result
                    state = _persist(profile, stop(state, reason))
                    break
                progress.update(99, "XCMate – Space Blue",
                                "Intro, Splash, Logo und Farbpalette sichern und prüfen")
                branding_result = _apply_space_blue_branding()
                if branding_result != "OK":
                    reason = branding_result
                    state = _persist(profile, stop(state, reason))
                    break
                progress.update(99, "XCMate – Abschlussprüfung",
                                "48 Komponenten, xVAULT, BINGIE und Space Blue geprüft")
                from setup_finish_0512 import mark_restart_pending
                # Only once *all* mandatory local checks have passed.
                completion = dict(state)
                completion["stage"] = "done"
                # Persist the post-boot marker first; if that fails, the
                # original CHECK stage remains recoverable, never fake DONE.
                mark_restart_pending(profile)
                state = _persist(profile, completion)
                progress.update(100, "XCMate – Einrichtung vollständig",
                                "Neustart zur Aktivierung der Startoberfläche erforderlich")
                reason = "RESTART_PENDING_VERIFIED"
                break
            reason = "UNEXPECTED_STEP:" + code
            state = _persist(profile, stop(state, reason[:200]))
            break
        else:
            reason = "SAFETY_STEP_LIMIT"
            state = _persist(profile, stop(state, reason))
    except (OSError, KeyError, TypeError, ValueError, RuntimeError) as exc:
        reason = "INSTALLER_EXCEPTION:" + type(exc).__name__
        try:
            from setup_origin_guard52 import _read_marker
            if _read_marker(profile) is not None:
                reason = "KODI_SOURCE_RESTORE_NOT_VERIFIED"
        except (OSError, ValueError):
            reason = "KODI_SOURCE_RESTORE_NOT_VERIFIED"
        try:
            state = _persist(profile, stop(state, reason))
        except (OSError, ValueError):
            pass
    finally:
        progress.close()
        window.clearProperty("GS_MEDIA_050_RUNNING")
        window.clearProperty("GS_MEDIA_050_CANCEL")

    done, total = count_done(snapshot())
    if reason == "RESTART_PENDING_VERIFIED":
        dialog.ok("XCMate Media Center Setup – Installation abschließen",
                  "{} von {} Komponenten bestätigt. xVAULT berücksichtigt, "
                  "BINGIE MOD aktiviert und Space Blue geprüft. ".format(done, total) +
                  "Um die Installation abzuschließen, muss Kodi neu "
                  "gestartet werden. Mit OK wird Kodi beendet. "
                  "Bitte Kodi auf Android danach erneut öffnen.")
        # RestartApp is not implemented on Android. Quit is the supported
        # Kodi action; the user launches Kodi again from their Android home.
        xbmc.executebuiltin("Quit")
    elif reason.startswith("NATIVE_DEPENDENCY_UPGRADE_FAILED:"):
        dialog.ok("XCMate – Kodi Abhaengigkeitsinstallation blockiert",
                  reason + "\n\nDer BINGIE-kompatible Skin Shortcuts 2.1.0 "
                  "ist im XC Mate Test-Katalog. Kodi hat das native "
                  "Abhaengigkeits-Upgrade nicht abgeschlossen. "
                  "Keine Daten geloescht, alle bisherigen Schritte bleiben "
                  "erhalten. Bitte Kodi-Log fuer genaue Ursache sichern. "
                  "Setup nicht wiederholt ohne neue Diagnose starten.")
    elif reason:
        dialog.ok("XCMate – sicher angehalten",
                  "{} von {} Komponenten geprüft. Grund: {}. "
                  "Keine Daten gelöscht. Nach Korrektur wiederaufnehmen."
                  .format(done, total, reason))
