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
            dialog.ok("XCMate – Bestandsinstallation geschützt",
                      "Gefundene bereits konfigurierte Add-ons: " +
                      ", ".join(protected) +
                      ". Vollautomatische Ersteinrichtung hier nicht gestartet. "
                      "Bestehende Daten bleiben unverändert.")
            return
        if not dialog.yesno(
            "XCMate – Vollautomatische Einrichtung 0.5.18",
            "Gesamte Kodi-Ersteinrichtung jetzt starten? Alle geprüften "
            "Repositories, 48 Komponenten und Abhängigkeiten werden "
            "nacheinander ohne zusätzliche Wizard-Abfragen installiert. "
            "BINGIE 2.2.3 wird nur bei exaktem Datei-Hash gesichert und "
            "eingerichtet. xVAULT als TMDB-Standardplayer nur einrichten, "
            "wenn keine persönlichen Player-Vorgaben überschrieben werden. "
            "Für Skin Shortcuts kann Kodi die Updatequelle kurzzeitig "
            "auf alle Repositories setzen; der vorherige Wert wird danach "
            "wiederhergestellt. Systemfreigaben von Kodi und echte Fehler "
            "können zusätzliche Eingaben oder einen sicheren Stopp erfordern. "
            "Jetzt einmalig zustimmen?"
        ):
            return
        state = new_state()
        _persist(profile, state)
    elif state["stopped"]:
        if not dialog.yesno("XCMate Media Center Setup", "Bisher geprüfte Komponenten "
                            "behalten und die restliche Einrichtung automatisch "
                            "fortsetzen? Die Hash-Schutzprüfungen bleiben aktiv; "
                            "Kodi-Systemfreigaben können separat erscheinen."):
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
    progress.create("XCMate Media Center Setup – v0.5.15 – Kodi 21.3 Omega", "Systemprüfung")
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
                minimum = next((row["minimum"] for row in rows()
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
                    code == "INSTALL_UPGRADE"
                    and ident == "script.skinshortcuts"
                    and step.get("source") == "repository.gsmedia.pilot"
                    and _version(step.get("actual", "")) < (2, 1, 0)
                    and step.get("minimum") == "2.1.0"
                )
                native_upgrade = code == "INSTALL_UPGRADE"
                native_slyguy_bootstrap = (
                    code == "INSTALL_ADDON"
                    and ident == "slyguy.dependencies"
                    and step.get("source") == "repository.slyguy"
                )
                if native_upgrade:
                    install_id = ("script.gsmedia.skinshortcuts.bridge"
                                  if native_shortcuts else step.get("bridge", ""))
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
                    if native_slyguy_bootstrap:
                        # Kodi dependency resolver installs the ORIGINAL
                        # SlyGuy Dependencies/Common/Trailers from their own
                        # already installed official SlyGuy repository.
                        # Our test repo includes ONLY this inert MIT bridge.
                        install_id = "script.gsmedia.slyguy.bootstrap"
                    # One Kodi-managed parent install resolves BOTH exact,
                    # original BINGIE packages through its immutable requires:
                    # repo 2.0.1 + helper 1.1.2. Neither addon is manually
                    # installed from a separate source or by an Android APK.
                    if (code == "INSTALL_REPOSITORY" and
                            ident == "repository.titan.bingie.mod" and
                            step.get("source") == "GS_MEDIA_APPROVED_TEST_CATALOG"):
                        install_id = "script.gsmedia.bingie.bootstrap"
                # Kodi 21 GetAddons(installed=true) confirms finished installs;
                # its distinct GetAddons(installed=false) checks the async repo
                # catalog. UpdateAddonRepos queues a refresh; it does not wait
                # for completion. Do not call InstallAddon until visible.
                from setup_auto50 import installed as confirmed
                _diag("CATALOG_REFRESH_REQUESTED", install_id)
                visible = {"code": "NOT_LISTED"}
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
                    visible = probe_kodi_catalog(xbmc.executeJSONRPC, install_id)
                    if visible["code"] == "AVAILABLE":
                        _diag("CATALOG_PACKAGE_VISIBLE", install_id,
                              visible.get("version", ""))
                        break
                    _diag("CATALOG_NOT_VISIBLE_TRY_" + str(catalog_attempt + 1),
                          install_id)
                if reason:
                    state = _persist(profile, stop(state, reason))
                    break
                if already_complete:
                    continue
                if visible["code"] != "AVAILABLE":
                    reason = "KODI_CATALOG_NOT_READY:" + install_id
                    _diag("CATALOG_STOP_NO_INSTALL_REQUEST", install_id)
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
                        addon_id="slyguy.dependencies" if native_slyguy_bootstrap
                        else "script.skinshortcuts")
                    if (native_upgrade or native_slyguy_bootstrap)
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
                if code_ in ("TMDB_PLAYER_EXISTING_DEFAULTS_PRESERVED",
                              "TMDB_PLAYER_EXISTING_PLAYER_PRESERVED"):
                    # xVAULT is mandatory, not an optional preference.
                    # Preserve foreign user defaults, fail closed and allow
                    # an explicit remedial approval on a later run.
                    reason = "TMDB_XVAULT_MANDATORY_UNMET:" + code_
                    state = _persist(profile, stop(state, reason))
                    break
                if code_ != "OK":
                    reason = code_
                    state = _persist(profile, stop(state, reason))
                    break
                state = _persist(profile, advance_stage(state, "player"))
                continue
            if code == "STAGE_CHECK":
                # Do not mark setup as complete just because Kodi reported
                # 43 installed/verified addon IDs.
                player_result = _apply_tmdb_player()
                if player_result != "OK":
                    reason = "TMDB_XVAULT_MANDATORY_UNMET:" + player_result
                    state = _persist(profile, stop(state, reason))
                    break
                progress.update(98, "XCMate – BINGIE MOD aktivieren",
                                "Kodi kann das Beibehalten des Skins bestätigen lassen")
                skin_result = _activate_bingie_runtime(inventory, monitor)
                if skin_result not in ("ACTIVE_AND_VERIFIED", "ALREADY_ACTIVE"):
                    reason = "BINGIE_NOT_ACTIVE:" + skin_result
                    state = _persist(profile, stop(state, reason))
                    break
                progress.update(99, "XCMate – Abschlussprüfung",
                                "48 Pakete, xVAULT und aktiver BINGIE geprüft")
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
                  "43 von 48 Komponenten bestätigt. xVAULT für Filme und "
                  "Serien konfiguriert; BINGIE MOD aktiviert. "
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
