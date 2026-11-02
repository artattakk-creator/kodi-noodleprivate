"""GS Media 0.4.0 – guided full setup on a clean Kodi 21 profile.

No silent third-party ZIP installation. Kodi owns all repository/addon
installation UI and may require user action. Fully installed applications
are followed by a hash-pinned BINGIE patch, skinshortcuts configuration,
TMDB xVAULT player setup and a verified post-reboot XCMate handoff.
"""
import os
from pathlib import Path

import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs

from setup_inventory import snapshot
from setup_full import (new_session, load, save, decide, mark_requested,
                        mark_installed, clear_retry, advance, SOURCES,
                        requirements, verify_complete, manifest)
from setup_install_pilot import protected_existing
from setup_bingie_apply import apply_new_profile
from setup_tmdb_apply import apply as apply_player, verify as verify_player
from setup_patch import apply as patch_skin, inspect as inspect_patch

ADDON_ID = "script.gsmedia.setup"


def _profile():
    return xbmcvfs.translatePath(xbmcaddon.Addon(ADDON_ID).getAddonInfo("profile"))


def _skin_root():
    return xbmcvfs.translatePath(xbmcaddon.Addon("skin.titan.bingie.mod").getAddonInfo("path"))


def _shortcuts_folder():
    return xbmcvfs.translatePath("special://profile/addon_data/script.skinshortcuts/")


def _patch_payload():
    return str(Path(xbmcvfs.translatePath(xbmcaddon.Addon(ADDON_ID).getAddonInfo("path"))) / "resources" / "skinpatch")


def _player_paths():
    root = xbmcvfs.translatePath(xbmcaddon.Addon("plugin.video.xvault").getAddonInfo("path"))
    profile = xbmcvfs.translatePath(xbmcaddon.Addon("plugin.video.themoviedb.helper").getAddonInfo("profile"))
    return root, profile, xbmcaddon.Addon("plugin.video.themoviedb.helper")


def _info(dialog, title, content):
    dialog.textviewer(title, content, usemono=True)


def _record(profile, state):
    try:
        save(profile, state)
        return True
    except (OSError, ValueError, TypeError):
        return False


def run():
    dialog = xbmcgui.Dialog()
    try:
        profile = _profile()
        state = load(profile)
        inventory = snapshot()
    except (OSError, ValueError, KeyError, RuntimeError):
        _info(dialog, "GS Media – Sicherheitsstopp", "Setupjournal unlesbar oder Kodi-Inventur ausgefallen. Keine Änderung.\nBitte Diagnose und Backup prüfen.")
        return
    if inventory.get("code") != "READY":
        _info(dialog, "GS Media – Keine Inventur", "Kodi kann installierte Add-ons nicht zuverlässig melden. Bitte Kodi neu starten und erneut prüfen.")
        return
    if state is None:
        protected = protected_existing(inventory)
        if protected:
            _info(dialog, "GS Media – Bestandsbox geschützt",
                  "Bestehende Add-ons erkannt: " + ", ".join(protected) +
                  "\nNeuinstallation nur auf FRISCHER Kodi-Box. "
                  "Vorhandene Profile und Player bleiben unverändert.")
            return
        if not dialog.yesno("GS Media – vollständige Neuinstallation",
                            "Alle 11 Pflichtprogramme installieren, BINGIE MOD und "
                            "TMDB Player konfigurieren und NACH Abschluss/Neustart "
                            "XCMate-Einrichtung einmalig öffnen. "
                            "Drittanbieter-Repositories können manuelle Kodi-Dialoge "
                            "erfordern. Nur auf leerem Kodi-Profil fortsetzen?"):
            return
        state = new_session(os.getpid())
        if not _record(profile, state):
            _info(dialog, "GS Media – STOP", "Fortschrittsjournal kann nicht sicher angelegt werden.")
            return

    phase = state.get("phase")
    if phase == "apps":
        result = decide(state, inventory)
        code = result.get("code", "")
        ident = result.get("addon_id", "")
        if code == "ALL_APPS_PRESENT":
            if _record(profile, advance(state, "apps", inventory)):
                dialog.ok("GS Media", "Alle 11 Pflichtprogramme samt bekannten Abhängigkeiten sind laut Kodi aktiv. "
                          "Nächster Schritt: BINGIE-Skinpatch und Widgets.")
            return
        if code == "CONFIRM_INSTALLED":
            if _record(profile, mark_installed(state, ident, inventory)):
                dialog.notification("GS Media", ident + " von Kodi bestätigt.", time=4500)
            return
        if code == "WAIT_FOR_KODI":
            if dialog.yesno("GS Media – Kodi-Installation läuft",
                            ident + " wurde noch nicht als installiert UND aktiviert bestätigt. "
                            "Erneut anfordern? Bei Nein keine Änderung."):
                if _record(profile, clear_retry(state, ident)):
                    dialog.ok("GS Media", "Wiederholung freigegeben. Setup erneut öffnen.")
            return
        if code == "RETRY_CONSENT_REQUIRED":
            if dialog.yesno("GS Media – Installation wiederholen",
                            ident + " wurde früher bereits angefordert. "
                            "Erneuten Versuch ausdrücklich erlauben?"):
                if _record(profile, clear_retry(state, ident)):
                    dialog.ok("GS Media", "Wiederholung freigegeben. Bitte erneut fortsetzen.")
            return
        if code in ("REPOSITORY_REQUIRED", "MANUAL_SOURCE_REQUIRED"):
            url = result.get("url", "") or "Original-Repositoryquelle bitte prüfen"
            repo = result.get("repo", "")
            _info(dialog, "GS Media – Originalquelle benötigt",
                  "Fehlendes Add-on: " + ident + "\n"
                  "Quelltyp: " + repo + "\n"
                  "Offizieller Einstieg: " + url + "\n\n"
                  "Bitte Original-Repository beziehungsweise Original-ZIP "
                  "über Kodi Add-ons → Aus ZIP installieren hinzufügen. "
                  "Bei Sicherheitswarnungen selbst zustimmen und das Setup "
                  "danach erneut öffnen. Keine unüberprüfte Datei wird durch "
                  "GS Media automatisch heruntergeladen.")
            if dialog.yesno("GS Media – Kodi-Installationsdialog",
                            "Jetzt Kodis Dialog 'Aus ZIP installieren' öffnen? "
                            "Du wählst die zuvor heruntergeladene Original-ZIP selbst aus."):
                xbmc.executebuiltin("InstallFromZip")
            return
        if code == "INSTALL_READY":
            if not dialog.yesno("GS Media – Add-on installieren",
                                ident + " aus dem vorhandenen Repository " +
                                result["repo"] + " über Kodi installieren? "
                                "Kodi darf dazu nötige Abhängigkeiten auflösen. "
                                "Nach jedem Schritt muss die Installation bestätigt werden."):
                return
            if not _record(profile, mark_requested(state, ident)):
                _info(dialog, "GS Media", "Journal nicht speicherbar: keine Installation.")
                return
            xbmc.executebuiltin("InstallAddon(" + ident + ")")
            dialog.notification("GS Media", ident + " angefordert. Nach Kodi-Dialog erneut Setup öffnen.", time=5000)
            return
        _info(dialog, "GS Media – Installationsstopp", str(result))
        return

    if phase == "bingie":
        try:
            skin_root = _skin_root()
            package_root = _patch_payload()
            status = inspect_patch(package_root, skin_root, "2.2.3")
        except (OSError, RuntimeError, ValueError):
            status = {"code": "SKIN_NOT_AVAILABLE"}
        if status["code"] not in ("READY",):
            _info(dialog, "GS Media – BINGIE-Patch blockiert", str(status) +
                  "\nKeine Skin-Datei wurde überschrieben. Unpassende Skinversion/"
                  "Hash → nicht reparieren ohne geprüfte neue Patchbasis.")
            return
        if not dialog.yesno("GS Media – BINGIE patchen",
                            "BINGIE 2.2.3 auf exakt geprüfte XCMate-XMLs patchen? "
                            "Alle 4 Originaldateien werden PRIVAT gesichert. "
                            "Bei Fremdmodifikationen wird abgebrochen."):
            return
        backup = str(Path(profile) / "skinpatch-060")
        patched = patch_skin(package_root, skin_root, backup, "2.2.3", user_approved=True)
        if patched["code"] not in ("APPLIED_AND_VERIFIED", "ALREADY_PATCHED"):
            _info(dialog, "GS Media – Skin-Patch abgebrochen", str(patched))
            return
        skinlayout = apply_new_profile(_shortcuts_folder(), inventory, user_approved=True)
        if skinlayout not in ("APPLIED", "ALREADY_APPLIED"):
            _info(dialog, "GS Media – Menü nicht verändert", "Skinpatchstatus: " +
                  patched["code"] + "\nMenüstatus: " + skinlayout +
                  "\nKeine vorhandenen Skinshortcuts-Dateien überschrieben.")
            return
        updated = advance(state, "bingie", inventory)
        updated["steps"]["bingie_patches_applied"] = True
        if _record(profile, updated):
            dialog.ok("GS Media", "BINGIE-Dateien gehasht und gesichert; "
                      "XCMate-Live-TV/Filme/Serien plus die archivierten Menüs/Widgets konfiguriert. "
                      "Nächster Schritt: TMDB Helper Player.")
        return

    if phase == "tmdb_xvault":
        try:
            src, dest, addon = _player_paths()
        except (RuntimeError, OSError):
            _info(dialog, "GS Media – Player", "xVAULT oder TMDB Helper fehlen. Kein Player wird verstellt.")
            return
        if not dialog.yesno("GS Media – TMDB Helper",
                            "xVAULT als Standardplayer für Filme UND Serien in einem "
                            "frischen TMDB Helper Profil einrichten? Vorhandene "
                            "abweichende Konfiguration bleibt geschützt."):
            return
        status = apply_player(src, dest, addon, fresh_profile=True, user_approved=True)
        if status != "APPLIED" or not verify_player(src, dest, addon):
            _info(dialog, "GS Media – Player nicht eingerichtet", status +
                  "\nKonfiguration nicht als erfolgreich bewertet.")
            return
        if _record(profile, advance(state, "tmdb_xvault", inventory)):
            dialog.ok("GS Media", "xVAULT für Filme und Episoden eingetragen. "
                      "Nächster Schritt: Abschlussprüfung und Kodi-Neustart.")
        return

    if phase == "verification":
        try:
            status = inspect_patch(_patch_payload(), _skin_root(), "2.2.3")
            patch_ok = status.get("code") == "READY" and not status.get("pending")
            src, dest, addon = _player_paths()
            player_ok = verify_player(src, dest, addon)
        except (RuntimeError, OSError, ValueError):
            patch_ok, player_ok = False, False
        from setup_bingie_apply import render, MENU_FILENAME, PROPS_FILENAME
        config_dir = Path(_shortcuts_folder())
        menu_files = render()
        layout_ok = all((config_dir / name).is_file() and
                        (config_dir / name).read_bytes() == value
                        for name, value in menu_files.items())
        checked = verify_complete(state, inventory, patch_ok and layout_ok, player_ok,
                                  packages_verified=False)
        _info(dialog, "GS Media – Abschlussprüfung",
              "11 Pflichtprogramme und Abhängigkeiten: " +
              str(all(r["addon_id"] in inventory.get("addons", {}) for r in requirements())) +
              "\nBINGIE-Dateien/Widgets: " + str(patch_ok and layout_ok) +
              "\nTMDB → xVAULT: " + str(player_ok) +
              "\nPaket-SHA/Urheberherkunft: noch nicht lückenlos geprüft\n"
              "Gesamtstatus: " + checked["code"] +
              "\n\nAutomatischer Neustart und XCMate-Ersteinrichtung bleiben "
              "blockiert, solange das vollständige Paket-Freigabegate fehlt.")
        return

    _info(dialog, "GS Media – Zustand", "Status: " + str(phase) +
          "\nKein automatischer Eingriff bei unklarem Installationszustand.")
