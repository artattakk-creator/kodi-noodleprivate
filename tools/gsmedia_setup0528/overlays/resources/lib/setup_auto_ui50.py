"""One consent, the full 0.5.26 package plan, and recoverable configuration."""
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET

from setup_auto50 import (after_confirm, after_request, installed, new_state,
                          next_step, reconcile_restart, resume, stop, upgrade_bridge_for)
from setup_auto_store50 import load, migrate, save
from setup_backup27 import path_at, restore_config, roots, start, writable_preflight
from setup_catalog_0516 import probe as probe_kodi_catalog
from setup_compat27 import (BINGIE, BRANDING, SKIN_SHORTCUTS, XCMATE, Blocked, check_closure, count_confirmed, current_platform,
                            manifest, probe_pillow, read_catalog, rpc, version)
from setup_finish27 import (SUCCESS, appearance, apply_config, native_decision, package_path, preserve_appearance, read_marker,
                            selected_skin, verify_config, write_marker)
from setup_inventory import snapshot
from setup_omega26 import (_context, _diag, _lock, _native_pilot_bridge,
                           request_stop)
from setup_origin_guard52 import TemporaryOfficialAddonSource, restore as restore_origin_policy
from setup_source27 import catalog_revision, confirm_catalog_duplicate, upgrade_metadata, verify_source

TITLE = "GS Media Setup 0.5.28"
PILOT = "repository.gsmedia.pilot"
BRANDING_MIN = "0.2.0"
ICONS = "resource.images.skinicons.wide"
SLYGUY = "slyguy.dependencies"
ESTUARY = "skin.estuary"
ERRORS = (Blocked, OSError, ValueError, TypeError, RuntimeError, AttributeError, KeyError, ET.ParseError)


@contextmanager
def exclusive(profile):
    folder = Path(profile).resolve()
    if folder.name != "script.gsmedia.setup":
        raise Blocked("SETUP_PROFILE_INVALID")
    folder.mkdir(mode=0o700, parents=True, exist_ok=True)
    # Share the .27 lease: both versions still own the same finish/rollback marker.
    fd = os.open(path_at(folder, ".setup-0527.lock"), os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise Blocked("SETUP_ALREADY_RUNNING") from None
        yield
    finally:
        os.close(fd)


def _approve(dialog, state):
    if state is None:
        return dialog.yesno(TITLE, "Vollständige GS-Media-Installation mit 48 Komponenten starten?\n"
                            "Kodi kann eigene Sicherheitsdialoge anzeigen. Geprüfte Abhängigkeiten "
                            "können vorübergehend die Kodi-Quelleneinstellung ändern. "
                            "Persönliche Daten und Einstellungen werden vor der Konfiguration gesichert.")
    if state["stopped"] or state["pending"]:
        return dialog.yesno(TITLE, "Installation nach Behebung fortsetzen? Bereits bestätigte "
                            "Komponenten werden erneut geprüft und bleiben installiert.")
    return True


class Setup:
    def __init__(self, xbmc, gui, profile, platform, progress, window, monitor):
        self.xbmc, self.gui = xbmc, gui
        self.profile, self.platform = profile, platform
        self.progress, self.window, self.monitor = progress, window, monitor
        self.execute = xbmc.executeJSONRPC
        self.xcmate_version = ""

    def _cancelled(self):
        return self.monitor.abortRequested() or self.window.getProperty("GS_MEDIA_050_CANCEL") == "1"

    def wait(self, seconds):
        if self._cancelled() or self.monitor.waitForAbort(seconds) or self._cancelled():
            raise Blocked("CANCELLED_OR_SHUTDOWN")

    def inventory(self):
        result = snapshot()
        if result.get("code") != "READY":
            raise Blocked("KODI_INVENTORY_UNAVAILABLE")
        installed_xcmate = result["addons"].get(XCMATE, {}).get("version", "")
        if self.xcmate_version and (not installed_xcmate
                                    or version(installed_xcmate) < version(self.xcmate_version)):
            raise Blocked("XCMATE_DOWNGRADE_DETECTED", XCMATE)
        self.xcmate_version = installed_xcmate
        return result

    def report(self, inventory, message, percent=None):
        done, total = count_confirmed(inventory)
        fraction = min(94, int(95 * done / total))
        self.progress.update(percent if percent is not None else fraction,
                             "{} · {}/{} Pakete bestätigt".format(TITLE, done, total), message)

    def enable(self, inventory, ident, minimum):
        if self.platform == "webos":
            check_closure(ident, inventory, self.execute, allow_disabled_root=True)
        result = rpc(self.execute, "Addons.SetAddonEnabled", {"addonid": ident, "enabled": True})
        if result not in (True, "OK") or not installed(self.inventory(), ident, minimum):
            raise Blocked("ENABLE_NOT_CONFIRMED", ident)

    def _catalog_diagnostic(self, event):
        self.xbmc.log(TITLE + " catalogue " + json.dumps(event, sort_keys=True, separators=(",", ":")),
                      self.xbmc.LOGINFO)

    def _webos_catalog(self, validate=None):
        if self._cancelled():
            raise Blocked("CANCELLED_OR_SHUTDOWN")
        with catalog_revision() as revision:
            return read_catalog(self.execute, cancelled=self._cancelled, wait=self.wait, revision=revision,
                                diagnose=self._catalog_diagnostic, confirm_duplicate=confirm_catalog_duplicate,
                                validate=validate)

    def _catalog(self, ident, install_id, minimum, parent):
        for attempt in range(6):
            if installed(self.inventory(), ident, minimum):
                return None
            if install_id != ident and installed(self.inventory(), install_id):
                raise Blocked("NATIVE_BRIDGE_PRESENT_DEPENDENCY_UNMET", ident, install_id)
            if attempt in (0, 3):
                self.xbmc.executebuiltin("UpdateAddonRepos")
            self.wait(5)
            if self.platform == "webos":
                candidates = self._webos_catalog()
                candidate = candidates.get(install_id)
                if candidate is None:
                    continue
                if (ident == BINGIE and candidate.get("version") != "2.2.3"
                        or version(candidate["version"]) < version(parent or minimum or "0")):
                    raise Blocked("BLOCKED_INCOMPATIBLE_DEPENDENCY", ident, install_id)
                return candidates
            listing = probe_kodi_catalog(self.execute, install_id)
            if listing["code"] != "AVAILABLE":
                continue
            if parent or minimum:
                # Preserve Omega's tested native source and minimum rules.
                from setup_install_pilot import _version
                if _version(listing.get("version", "")) < _version(parent or minimum):
                    raise Blocked("KODI_CATALOG_VERSION_TOO_OLD", ident)
            if ident == BINGIE and listing.get("version") != "2.2.3":
                raise Blocked("BINGIE_PATCH_VERSION_UNAVAILABLE", BINGIE)
            if ident == SLYGUY and install_id != ident:
                dependency = probe_kodi_catalog(self.execute, SLYGUY)
                if dependency["code"] != "AVAILABLE":
                    continue
                if _version(dependency.get("version", "")) < (0, 0, 30):
                    raise Blocked("SLYGUY_CATALOG_DEPENDENCY_TOO_OLD", ident)
            return {}
        reason = ("BLOCKED_INCOMPATIBLE_DEPENDENCY" if self.platform == "webos"
                  else "KODI_CATALOG_NOT_READY")
        raise Blocked(reason, ident, install_id if install_id != ident else "NOT_LISTED_BY_KODI")

    def install(self, inventory, step, state=None):
        ident = step["id"]
        code = step["code"]
        source = step.get("source", "")
        minimum = step.get("minimum") or ("2.0.1" if ident == "repository.titan.bingie.mod" else "")
        pilot = _native_pilot_bridge(code, step, upgrade_bridge_for)
        shortcuts = ident == SKIN_SHORTCUTS and source == PILOT and minimum == "2.1.0"
        icons = ident == ICONS and source == PILOT and minimum == "1.0.5"
        slyguy = code == "INSTALL_ADDON" and ident == SLYGUY and source == "repository.slyguy"
        upgrade = code == "INSTALL_UPGRADE" or bool(pilot) or shortcuts or icons
        install_id, parent = ident, ""
        if upgrade:
            install_id = ("script.gsmedia.skinshortcuts.bridge" if shortcuts
                          else "script.gsmedia.upgrade." + ICONS if icons
                          else pilot or step.get("bridge", ""))
            if not install_id or source not in (
                    PILOT, "repository.titan.bingie.mod", "repository.xbmc.org",
                    "repository.slyguy", "repository.xvault"):
                raise Blocked("UPGRADE_SOURCE_BLOCKED", ident)
            parent = "0.1.0"
        elif slyguy:
            install_id, parent = "script.module.slyguy", "0.87.6"
        candidates = self._catalog(ident, install_id, minimum, parent)
        if candidates is None:
            return
        guard_id = SLYGUY if slyguy else ICONS if icons else ident if pilot else SKIN_SHORTCUTS
        from contextlib import nullcontext
        scope = (TemporaryOfficialAddonSource(self.profile, self.execute, addon_id=guard_id)
                 if upgrade or slyguy else nullcontext())
        with scope:
            if upgrade:
                self.xbmc.executebuiltin("UpdateAddonRepos")
                self.wait(4)
            if self.platform == "webos":
                expected_source = (PILOT if upgrade or source == "GS_MEDIA_APPROVED_TEST_CATALOG"
                                   else source)
                sources = {row["id"]: row["repo"] for row in manifest()}

                def validate(catalog):
                    effective = catalog.get(install_id, {}).get("version", "")
                    if not effective or version(effective) < version(parent or minimum or "0"):
                        raise Blocked("BLOCKED_INCOMPATIBLE_DEPENDENCY", ident, install_id)
                    closure = check_closure(
                        install_id, self.inventory(), self.execute, catalog,
                        prefer_candidate=True, protected=self.xcmate_version,
                        available_update=lambda dependency: upgrade_metadata(dependency, expected_source, sources))
                    verify_source(ident, install_id, expected_source, closure, sources, rpc_catalog=catalog)

                self._webos_catalog(validate=validate)
            if state is not None:
                save(self.profile, after_request(state, ident))
            self.report(inventory, "Kodi installiert und prüft " + ident)
            _diag("KODI_INSTALL_REQUESTED", install_id)
            self.xbmc.executebuiltin("InstallAddon(" + install_id + ")")
            for elapsed in range(2, 241, 2):
                self.wait(2)
                current = self.inventory()
                if installed(current, ident, minimum):
                    _diag("KODI_INSTALL_CONFIRMED", ident)
                    if code == "INSTALL_REPOSITORY":
                        self.xbmc.executebuiltin("UpdateAddonRepos")
                    return
                self.report(current, "{} · warte auf Kodi ({} s)".format(ident, elapsed))
        raise Blocked("KODI_INSTALL_NOT_CONFIRMED", ident)

    def packages(self):
        plan = {row["id"]: row for row in manifest()}
        for _ in range(300):
            if self._cancelled():
                raise Blocked("CANCELLED_OR_SHUTDOWN")
            inventory = self.inventory()
            state = load(self.profile)
            step = next_step(state, inventory)
            code, ident = step["code"], step.get("id", "")
            self.report(inventory, "Prüfe " + ident if ident else "Prüfe vollständigen Paketstand")
            if code == "CONFIRM":
                save(self.profile, after_confirm(state, inventory))
            elif code == "ENABLE_ADDON":
                self.enable(inventory, ident, step.get("minimum") or plan.get(ident, {}).get("minimum", ""))
            elif code in ("INSTALL_REPOSITORY", "INSTALL_ADDON", "INSTALL_UPGRADE"):
                minimum = step.get("minimum") or plan.get(ident, {}).get("minimum", "")
                if code == "INSTALL_REPOSITORY" and ident in inventory["addons"]:
                    repo = inventory["addons"][ident]
                    if minimum and version(repo.get("version", "0")) < version(minimum):
                        raise Blocked("NATIVE_REPOSITORY_UPDATE_REQUIRED", ident)
                    self.enable(inventory, ident, minimum)
                else:
                    self.install(inventory, dict(step, minimum=minimum), state)
            elif code == "APPS_PRESENT":
                if inventory["addons"][BINGIE]["version"] != "2.2.3":
                    raise Blocked("BINGIE_PATCH_VERSION_UNAVAILABLE", BINGIE)
                if not inventory["addons"][SKIN_SHORTCUTS]["version"].startswith("2."):
                    raise Blocked("BLOCKED_INCOMPATIBLE_DEPENDENCY", BINGIE, SKIN_SHORTCUTS)
                return inventory
            else:
                raise Blocked(code, ident, step.get("reason", ""))
        raise Blocked("SAFETY_STEP_LIMIT")

    def configure(self, inventory):
        self.report(inventory, "Prüfe Space-Blue-Abhängigkeit", 95)
        if not installed(inventory, PILOT):
            raise Blocked("PILOT_CATALOG_NOT_INSTALLED", PILOT)
        if not installed(inventory, BRANDING, BRANDING_MIN):
            branding = inventory["addons"].get(BRANDING, {})
            if branding.get("version"):
                if version(branding["version"]) < version(BRANDING_MIN):
                    raise Blocked("SPACE_BLUE_MANAGER_TOO_OLD", BRANDING)
                self.enable(inventory, BRANDING, BRANDING_MIN)
            else:
                self.install(inventory, dict(id=BRANDING, code="INSTALL_ADDON",
                                            source=PILOT, minimum=BRANDING_MIN))
        inventory = self.inventory()
        if self.platform == "webos":
            self.report(inventory, "Prüfe Piers-Abhängigkeiten und Pillow", 96)
            for row in (*manifest(), {"id": BRANDING}):
                check_closure(row["id"], inventory, self.execute)
            probe_pillow()

        previous = selected_skin(self.xbmc)
        if self.xbmc.getCondVisibility("Player.HasMedia"):
            raise Blocked("CLOSE_PLAYBACK_BEFORE_CONFIG")
        if previous == BINGIE and not installed(inventory, ESTUARY):
            raise Blocked("ESTUARY_FALLBACK_UNAVAILABLE", ESTUARY)
        mapping = roots(self.profile)
        self.report(inventory, "Sichere lokale Profile, Datenbanken und Konfiguration", 97)
        writable_preflight(mapping)
        prior_preferences = appearance(self.xbmc)
        record = write_marker(self.profile, start(self.profile, mapping, previous, self._cancelled),
                              preferences=prior_preferences)
        self.wait(0.01)
        self.report(inventory, "Prüfe BINGIE-Hash, Widgets, Space Blue und xVAULT", 98)
        apply_config(self.xbmc, self.profile, mapping, package_path(), inventory)
        target = ESTUARY if previous == BINGIE else BINGIE
        message = ("Kodi-Dialog für Estuary: Ja = Estuary, Nein = BINGIE MOD."
                   if previous == BINGIE else "Im Kodi-Dialog: Soll das BINGIE-MOD-Theme beibehalten werden?")
        self.report(inventory, message, 99)
        self.wait(0.01)
        self.progress.close()
        self.progress = None
        if previous == BINGIE:
            self.gui.Dialog().notification(TITLE, message)
        chosen = native_decision(self.xbmc, self.monitor, previous, target)
        if chosen == previous:
            preserve_appearance(self.xbmc, prior_preferences)
        verify_config(self.xbmc, mapping, package_path(), self.inventory())
        # Save the selected skin across restart. The startup service performs a
        # fresh readback and cannot change or re-activate the user's skin.
        write_marker(self.profile, record, status="restart_pending",
                     selected_skin=chosen, pid=os.getpid())
        state = dict(load(self.profile), stage="done")
        save(self.profile, state)
        return chosen


def _run(xbmc, gui, profile, platform):
    dialog = gui.Dialog()
    restore_origin_policy(profile, xbmc.executeJSONRPC)
    record = read_marker(profile)
    if record and record["status"] in SUCCESS:
        if record["status"] == "restart_pending":
            _restart_instructions(xbmc, dialog, platform, record["selected_skin"])
        else:
            dialog.ok(TITLE, "48 Pakete und gewählter Skin nach Kodi-Neustart bestätigt. "
                             "Sichtprüfung von Startseite und EPG bleibt ausstehend.")
        return
    if record and record["status"] in ("pending", "failed"):
        raise Blocked("CONFIGURATION_ROLLBACK_REQUIRED")
    state = load(profile)
    if not _approve(dialog, state):
        return
    migrate(profile)
    if state is None:
        save(profile, new_state())
    elif state["stopped"] or state["pending"]:
        stopped = state if state["stopped"] else stop(state, "PREVIOUS_INSTALL_NOT_VERIFIED")
        save(profile, resume(reconcile_restart(stopped, snapshot())))
    window = _lock()
    progress = gui.DialogProgressBG()
    window.setProperty("GS_MEDIA_050_RUNNING", "1")
    window.clearProperty("GS_MEDIA_050_CANCEL")
    setup = Setup(xbmc, gui, profile, platform, progress, window, xbmc.Monitor())
    try:
        progress.create(TITLE, "Kodi " + ("22 Piers · LG webOS" if platform == "webos" else "21 Omega · Android"))
        chosen = setup.configure(setup.packages())
    finally:
        if setup.progress is not None:
            progress.close()
        window.clearProperty("GS_MEDIA_050_RUNNING")
        window.clearProperty("GS_MEDIA_050_CANCEL")
    _restart_instructions(xbmc, dialog, platform, chosen)


def _restart_instructions(xbmc, dialog, platform, skin):
    target = "über die LG-webOS-Startseite" if platform == "webos" else "über den Android-Startbildschirm"
    if dialog.ok(TITLE, "48 Pakete und Konfiguration bestätigt. Gewählter Skin: " + skin
                 + ". Mit OK Kodi vollständig beenden. Anschließend Kodi " + target + " erneut öffnen."):
        xbmc.executebuiltin("Quit")


def run():
    import xbmc
    import xbmcgui
    dialog = xbmcgui.Dialog()
    platform = current_platform(xbmc)
    if platform is None:
        dialog.ok(TITLE, "Unterstützte Ziele sind Kodi 21 Omega auf Android und Kodi 22 Piers auf LG webOS.")
        return
    profile = _context()
    try:
        with exclusive(profile):
            try:
                _run(xbmc, xbmcgui, profile, platform)
            except ERRORS as error:
                reason = str(error) if isinstance(error, Blocked) else "SETUP_" + type(error).__name__
                state = load(profile, legacy=False)
                if state is not None and state["stage"] != "done":
                    save(profile, stop(state, reason))
                raise Blocked(reason) from None
    except ERRORS as error:
        reason = str(error) if isinstance(error, Blocked) else "SETUP_JOURNAL_UNAVAILABLE"
        done, total = count_confirmed(snapshot())
        dialog.ok(TITLE, "{}/{} Pakete bestätigt. Einrichtung angehalten. {}\n"
                  "Nach Behebung im Setup-Menü fortsetzen.".format(done, total, reason))


def rollback():
    import xbmc
    import xbmcgui
    dialog = xbmcgui.Dialog()
    profile = _context()
    try:
        with exclusive(profile):
            record = read_marker(profile)
            if not record or record["status"] not in ("pending", "failed"):
                return
            if not dialog.yesno(TITLE, "Gesicherte Skin-, Widget- und Player-Konfiguration wiederherstellen?"):
                return
            # Work on inactive skin files. A currently used BINGIE skin owns
            # the settings file in RAM, and could overwrite a disk-only restore.
            if selected_skin(xbmc) == BINGIE:
                dialog.ok(TITLE, "Vor der Wiederherstellung in Kodi zu Estuary wechseln und den Wechsel bestätigen.")
                return
            mapping = roots(profile)
            restore_config(profile, record, mapping)
            if selected_skin(xbmc) != record["previous_skin"]:
                restored = native_decision(xbmc, xbmc.Monitor(), selected_skin(xbmc), record["previous_skin"])
                if restored != record["previous_skin"]:
                    raise Blocked("PREVIOUS_SKIN_NOT_RESTORED")
            preserve_appearance(xbmc, record["preferences"])
            state = load(profile)
            if state is not None:
                save(profile, stop(dict(state, stage="apps"), "CONFIGURATION_ROLLED_BACK"))
            write_marker(profile, record, status="rolled_back")
            dialog.ok(TITLE, "Gesicherte Konfiguration zurückgespielt. Bitte Kodi vollständig neu öffnen.")
    except ERRORS:
        dialog.ok(TITLE, "Wiederherstellung angehalten. Die lokale Sicherung bleibt erhalten.")
