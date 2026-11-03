"""Kodi 21 one-button installer with nonmodal progress and safe stop/resume.

The progress bar measures completed Kodi installs, not invented download bytes.
Kodi itself handles package transfers and approval dialogs.
"""
import os
import re
from pathlib import Path

from setup_auto50 import (new_state, next_step, after_request, after_confirm,
                          after_retry, stop, resume, rows, count_done, advance_stage)
from setup_auto_store50 import load, save
from setup_inventory import snapshot
from setup_install_pilot import protected_existing, _version
from setup_origin_guard52 import restore as restore_origin_policy


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
    """Separate action callable from Kodi's GS Media Setup program menu."""
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
    if inspect_new_profile(shortcut_dir, inventory) not in ("READY", "ALREADY_APPLIED"):
        return "SKIN_SHORTCUTS_CONFLICT"
    backup_root = os.path.join(profile, "skinpatch-050")
    patched = apply_skin(package_root, skin_root, backup_root, "2.2.3",
                         user_approved=True)
    if patched.get("code") not in ("APPLIED_AND_VERIFIED", "ALREADY_PATCHED"):
        return "SKIN_PATCH_FAILED"
    layout = apply_new_profile(shortcut_dir, inventory, user_approved=True)
    if layout not in ("APPLIED", "ALREADY_APPLIED"):
        return "SKIN_LAYOUT_FAILED"
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


def run():
    import xbmc
    import xbmcgui
    dialog = xbmcgui.Dialog()
    if not (xbmc.getInfoLabel("System.BuildVersion") or "").startswith("21."):
        dialog.ok("GS Media Setup", "Nur Kodi 21 wird unterstützt.")
        return
    try:
        profile = _context()
        state = load(profile)
        first = state is None
        inventory = snapshot()
    except (ValueError, OSError, RuntimeError, KeyError) as exc:
        dialog.ok("GS Media – Sicherheitsstopp", "Systemprüfung fehlgeschlagen. "
                  "Keine Installation ausgeführt.")
        return
    # Crash recovery is mandatory before any other install work.
    try:
        restore_origin_policy(profile, xbmc.executeJSONRPC)
    except (RuntimeError, OSError, ValueError, TypeError):
        dialog.ok("GS Media – Schutz-Einstellungen",
                  "Kodi konnte die vorige Quelleneinstellung nicht "
                  "automatisch zurücksetzen. Keine Installation wird "
                  "ausgeführt. Details im Kodi-Log.")
        return
    if inventory.get("code") != "READY":
        dialog.ok("GS Media – Sicherheitsstopp",
                  "Die Kodi-Inventur ist nicht verfügbar. Keine Installation.")
        return
    if first:
        protected = protected_existing(inventory)
        if protected:
            dialog.ok("GS Media – Bestandsinstallation geschützt",
                      "Gefundene bereits konfigurierte Add-ons: " +
                      ", ".join(protected) +
                      ". Vollautomatische Ersteinrichtung hier nicht gestartet. "
                      "Bestehende Daten bleiben unverändert.")
            return
        if not dialog.yesno(
            "GS Media Setup 0.5.3 – Test",
            "Alle 11 Apps und ihre Abhängigkeiten aus geprüften Repositories "
            "mit Kodi installieren? Bereits vorhandene Add-ons werden nicht "
            "überschrieben. Fremdquellen und ungeprüfte Pakete bleiben gesperrt. "
            "Skin/Player erst nach weiterer Bestätigung einrichten?"
        ):
            return
        state = new_state()
        _persist(profile, state)
    elif state["stopped"]:
        if not dialog.yesno("GS Media Setup", "Unterbrochene Installation "
                            "ab dem letzten verifizierten Schritt fortsetzen?"):
            return
        if state["pending"]:
            pending = state["pending"]
            if not dialog.yesno("GS Media – unvollständiger Schritt",
                                "Kodi hat {} nicht als installiert bestätigt. "
                                "Nur nach Abbruch der vorherigen Installation "
                                "erneut anfordern?".format(pending)):
                return
            state = _persist(profile, after_retry(state, pending))
        state = _persist(profile, resume(state))

    window = _lock()
    if window.getProperty("GS_MEDIA_050_RUNNING") == "1":
        dialog.ok("GS Media", "Installation läuft bereits. Keine zweite "
                  "Instanz starten.")
        return
    window.setProperty("GS_MEDIA_050_RUNNING", "1")
    window.clearProperty("GS_MEDIA_050_CANCEL")
    progress = xbmcgui.DialogProgressBG()
    progress.create("GS Media Setup 0.5.3", "Systemprüfung")
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
            progress.update(percent, "GS Media: {} / {} Komponenten".format(done, total),
                            _stage_text(step, done, total))
            if code == "CONFIRM":
                state = _persist(profile, after_confirm(state, inventory))
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
                native_upgrade = (
                    code == "INSTALL_UPGRADE"
                    and ident == "script.skinshortcuts"
                    and step.get("source") == "repository.gsmedia.pilot"
                    and _version(step.get("actual", "")) < (2, 1, 0)
                    and step.get("minimum") == "2.1.0"
                )
                if code == "INSTALL_UPGRADE" and not native_upgrade:
                    reason = "UNSUPPORTED_UPGRADE:" + ident
                    state = _persist(profile, stop(state, reason))
                    break

                install_id = "script.gsmedia.skinshortcuts.bridge" if native_upgrade else ident
                if native_upgrade:
                    if not dialog.yesno(
                        "GS Media – Skin Shortcuts automatisch aktualisieren",
                        "Kodi hat Skin Shortcuts 2.0.3 bereits installiert. "
                        "GS Media wird jetzt den originalen Skin Shortcuts "
                        "2.1.0 als Pflichtabhaengigkeit eines kleinen "
                        "GS-Media-Testpakets ueber Kodi installieren. "
                        "Die globale Kodi-Sicherheitsregel bleibt unveraendert. "
                        "Fortfahren?"
                    ):
                        reason = "NATIVE_UPGRADE_NOT_APPROVED"
                        state = _persist(profile, stop(state, reason))
                        break

                state = _persist(profile, after_request(state, ident))
                wait = 0
                xbmc.executebuiltin("InstallAddon(" + install_id + ")")

                # InstallAddon displays a native modal Kodi prompt, and Kodi
                # owns the actual ZIP download and dependency resolution.
                # Never claim elapsed time is a download percentage.
                while wait < (100 if native_upgrade else 240):
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
                        "GS Media: {} / {} Komponenten".format(done, total),
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
                        reason = "NATIVE_DEPENDENCY_UPGRADE_FAILED:{} ist={} soll=2.1.0".format(
                            ident, actual or "nicht ermittelt")
                    else:
                        reason = "KODI_INSTALL_NOT_CONFIRMED:" + ident
                    state = _persist(profile, stop(state, reason[:200]))
                    break

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
                reason = code + ":" + step.get("id", "")
                state = _persist(profile, stop(state, reason[:200]))
                break
            if code == "APPS_PRESENT":
                state = _persist(profile, advance_stage(state, "apps"))
                continue
            if code == "STAGE_SKIN":
                progress.update(96, "GS Media – BINGIE",
                                "Prüfe originalen Skin und sichere XML-Dateien")
                if not dialog.yesno(
                    "GS Media – BINGIE-Konfiguration",
                    "BINGIE MOD 2.2.3 nur bei exaktem Dateihash sichern "
                    "und XCMate-Menüs/Widgets einrichten? Bestehende "
                    "Änderungen werden nicht überschrieben."
                ):
                    reason = "SKIN_PATCH_NOT_APPROVED"
                    state = _persist(profile, stop(state, reason))
                    break
                code_ = _apply_skin(profile, inventory)
                if code_ != "OK":
                    reason = code_
                    state = _persist(profile, stop(state, reason))
                    break
                state = _persist(profile, advance_stage(state, "skin"))
                continue
            if code == "STAGE_PLAYER":
                progress.update(97, "GS Media – TMDB",
                                "Prüfe xVAULT-Player für Filme und Serien")
                if not dialog.yesno("GS Media – Standardplayer",
                                    "xVAULT als TMDB-Helper-Player für Filme UND "
                                    "Serien konfigurieren? Vorhandene fremde "
                                    "Einstellungen bleiben geschützt."):
                    reason = "TMDB_PLAYER_NOT_APPROVED"
                    state = _persist(profile, stop(state, reason))
                    break
                code_ = _apply_tmdb_player()
                if code_ != "OK":
                    reason = code_
                    state = _persist(profile, stop(state, reason))
                    break
                state = _persist(profile, advance_stage(state, "player"))
                continue
            if code == "STAGE_CHECK":
                progress.update(98, "GS Media – Abschlussprüfung",
                                "Quellen und Android-Gerätetest erforderlich")
                reason = "RELEASE_SOURCE_AND_ANDROID_GATES_PENDING"
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
    if reason == "RELEASE_SOURCE_AND_ANDROID_GATES_PENDING":
        dialog.ok("GS Media – Apps installiert",
                  "{} von {} Komponenten bestätigt. BINGIE und TMDB-Player "
                  "eingerichtet; Quellnachweis und Android-Abnahme bleiben offen."
                  .format(done, total))
    elif reason.startswith("NATIVE_DEPENDENCY_UPGRADE_FAILED:"):
        dialog.ok("GS Media – Kodi Abhaengigkeitsinstallation blockiert",
                  reason + "\n\nDer BINGIE-kompatible Skin Shortcuts 2.1.0 "
                  "ist im GS Media Test-Katalog. Kodi hat das native "
                  "Abhaengigkeits-Upgrade nicht abgeschlossen. "
                  "Keine Daten geloescht, alle bisherigen Schritte bleiben "
                  "erhalten. Bitte Kodi-Log fuer genaue Ursache sichern. "
                  "Setup nicht wiederholt ohne neue Diagnose starten.")
    elif reason:
        dialog.ok("GS Media – sicher angehalten",
                  "{} von {} Komponenten geprüft. Grund: {}. "
                  "Keine Daten gelöscht. Nach Korrektur wiederaufnehmen."
                  .format(done, total, reason))
