"""Kodi 21 one-button installer with nonmodal progress and safe stop/resume.

The progress bar measures completed Kodi installs, not invented download bytes.
Kodi itself handles package transfers and approval dialogs.
"""
import os
import re
from pathlib import Path

from setup_auto50 import (new_state, next_step, after_request, after_confirm,
                          after_retry, stop, resume, rows, count_done)
from setup_auto_store50 import load, save
from setup_inventory import snapshot


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
    if inventory.get("code") != "READY":
        dialog.ok("GS Media – Sicherheitsstopp",
                  "Die Kodi-Inventur ist nicht verfügbar. Keine Installation.")
        return
    if first:
        if not dialog.yesno(
            "GS Media Setup 0.5.0 – Test",
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
        state = _persist(profile, resume(state))

    window = _lock()
    if window.getProperty("GS_MEDIA_050_RUNNING") == "1":
        dialog.ok("GS Media", "Installation läuft bereits. Keine zweite "
                  "Instanz starten.")
        return
    window.setProperty("GS_MEDIA_050_RUNNING", "1")
    window.clearProperty("GS_MEDIA_050_CANCEL")
    progress = xbmcgui.DialogProgressBG()
    progress.create("GS Media Setup 0.5.0", "Systemprüfung")
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
            if code in ("INSTALL_REPOSITORY", "INSTALL_ADDON"):
                ident = step["id"]
                if not re.fullmatch(r"[A-Za-z0-9._-]{3,100}", ident):
                    raise ValueError("Invalid add-on ID")
                state = _persist(profile, after_request(state, ident))
                xbmc.executebuiltin("InstallAddon(" + ident + ")")
                # This does NOT claim an installation succeeded or report fake
                # network percentages. Kodi may show its own transfer dialog.
                wait = 0
                while wait < 240:
                    if monitor.waitForAbort(2):
                        break
                    if window.getProperty("GS_MEDIA_050_CANCEL") == "1":
                        break
                    wait += 2
                    inv = snapshot()
                    if next_step(state, inv)["code"] == "CONFIRM":
                        break
                    progress.update(percent,
                                    "GS Media: {} / {} Komponenten".format(done, total),
                                    "{} – Kodi Download/Installation ({} s)".format(ident, wait))
                if monitor.abortRequested() or window.getProperty("GS_MEDIA_050_CANCEL") == "1":
                    reason = "CANCELLED_OR_SHUTDOWN"
                    state = _persist(profile, stop(state, reason))
                    break
                if next_step(state, snapshot())["code"] != "CONFIRM":
                    reason = "KODI_INSTALL_NOT_CONFIRMED:" + ident
                    state = _persist(profile, stop(state, reason[:200]))
                    break
                state = _persist(profile, after_confirm(state, snapshot()))
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
                # Complete skin/Player stages still require original hashes,
                # detailed per-file checks, and author-approved package sources.
                # Do not auto-enable a broken BINGIE skin or fake final success.
                progress.update(96, "GS Media: alle Pakete erkannt",
                                "Skin/Player-/Herkunftsprüfung folgt")
                reason = "APPS_INSTALLED_SKIN_AND_SOURCE_GATES_PENDING"
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
            state = _persist(profile, stop(state, reason))
        except (OSError, ValueError):
            pass
    finally:
        progress.close()
        window.clearProperty("GS_MEDIA_050_RUNNING")
        window.clearProperty("GS_MEDIA_050_CANCEL")

    done, total = count_done(snapshot())
    if reason == "APPS_INSTALLED_SKIN_AND_SOURCE_GATES_PENDING":
        dialog.ok("GS Media – Apps installiert",
                  "{} von {} Komponenten bestätigt. Für Skinpatch, "
                  "Player und Abschluss bleiben Sicherheitsprüfungen offen."
                  .format(done, total))
    elif reason:
        dialog.ok("GS Media – sicher angehalten",
                  "{} von {} Komponenten geprüft. Grund: {}. "
                  "Keine Daten gelöscht. Nach Korrektur wiederaufnehmen."
                  .format(done, total, reason))
