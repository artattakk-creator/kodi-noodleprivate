"""Kodi UI for safe, explicitly confirmed repository installation pilot.

This is an opt-in feature and may install only script.cabertoss,
plugin.audio.shoutcast and plugin.video.xtreammate. It never treats launching
InstallAddon as success, never imports arbitrary ZIPs, and never edits skin.
"""
from setup_install_pilot import (
    APPROVED, APPROVED_IDS, blank_state, load, save, assess, after_request,
    after_confirm, retry_explicitly, plan, protected_existing,
)
from setup_inventory import snapshot


def _profile():
    import xbmcaddon
    import xbmcvfs
    addon = xbmcaddon.Addon("script.gsmedia.setup")
    return xbmcvfs.translatePath(addon.getAddonInfo("profile"))


def _message(dialog, text):
    dialog.textviewer("GS Media – Installationspilot", text, usemono=True)


def run():
    import xbmc
    import xbmcgui
    dialog = xbmcgui.Dialog()
    try:
        profile = _profile()
        state = load(profile)
    except (ValueError, OSError, TypeError, KeyError, RuntimeError) as exc:
        _message(dialog, "JOURNAL_UNLESBAR. Es werden keine Pakete installiert.\n"
                 "Bitte den Fehler zuerst untersuchen.\n" + type(exc).__name__)
        return

    inventory = snapshot()
    if inventory.get("code") != "READY":
        _message(dialog, "Kodi Add-on Inventur nicht verfügbar. Installationspilot blockiert.")
        return
    if state is None:
        protected = protected_existing(inventory)
        if protected:
            _message(dialog, "BESTANDSBOX-SCHUTZ: Der Installationspilot verweigert "
                     "eine erste Installation, weil bestehende Add-ons erkannt "
                     "wurden: " + ", ".join(protected) + ".\n"
                     "Vorhandene Konfigurationen dürfen nicht überschrieben "
                     "werden. Nur neue, noch nicht eingerichtete Testbox verwenden.")
            return
        rows = plan(inventory)
        if not dialog.yesno(
            "GS Media – begrenzter Installationspilot",
            "Es werden NUR die offiziell verfügbaren Apps Caber Toss, "
            "SHOUTcast und XCMate aus bereits eingerichteten Kodi/GS-Media-"
            "Repositories nacheinander angefordert. "
            "Kodi kann Rückfragen anzeigen. Die übrigen Pflichtprogramme "
            "werden NICHT installiert. Keine Skin-Einstellungen werden geändert. "
            "Diesen Test auf einer NEUEN Kodi-Box starten?"
        ):
            return
        state = blank_state()
        try:
            save(profile, state)
        except (ValueError, OSError, TypeError, KeyError) as exc:
            _message(dialog, "Journal konnte nicht sicher angelegt werden: "
                     + type(exc).__name__)
            return

    result = assess(state, inventory)
    code = result["code"]
    addon_id = result.get("addon_id", "")

    if code == "CONFIRM_INSTALLED":
        try:
            state = after_confirm(state, addon_id)
            save(profile, state)
        except (ValueError, OSError, TypeError, KeyError) as exc:
            _message(dialog, "Erfolgsprüfung nicht speicherbar: " + type(exc).__name__)
            return
        _message(dialog, addon_id + " ist durch Kodi als installiert UND aktiviert "
                 "und mit ausreichender Version bestätigt.\n"
                 "Nächster Schritt: Installationspilot erneut im Menü öffnen.")
        return

    if code == "AWAITING_KODI_INSTALL":
        if dialog.yesno(
            "GS Media – Kodi-Installation prüfen",
            "Kodi meldet " + addon_id + " noch nicht als installiert und aktiviert. "
            "Möglicherweise läuft die Installation noch oder wurde abgebrochen. "
            "Installation ausdrücklich ERNEUT anfordern? "
            "Bei NEIN keine Änderungen, später erneut prüfen."
        ):
            try:
                updated = retry_explicitly(state, addon_id)
                save(profile, updated)
            except (ValueError, OSError, TypeError) as exc:
                _message(dialog, "Erneuter Installationsversuch blockiert: "
                         + type(exc).__name__)
                return
            state = updated
            result = assess(state, snapshot())
            code = result["code"]
            addon_id = result.get("addon_id", "")
        else:
            return

    if code == "REQUEST_INSTALL":
        if addon_id not in APPROVED_IDS:
            _message(dialog, "Paket außerhalb der freigegebenen Installationsliste.")
            return
        packages = {x[0]: x for x in APPROVED}
        source = packages[addon_id][1]
        if not dialog.yesno(
            "GS Media – Kodi-Paketinstallation",
            "Jetzt " + addon_id + " aus einem in Kodi vorhandenen Repository "
            "anfordern? Geprüfte erwartete Quelle: " + source + ". "
            "Die tatsächliche Quellzuordnung und alle Kodi-Sicherheitsdialoge "
            "müssen beachtet werden. "
            "Nach diesem Schritt Installationspilot erneut öffnen."
        ):
            return
        try:
            # Persist BEFORE requesting an asynchronous Kodi operation to
            # prevent accidental endless reattempts after a process restart.
            state = after_request(state, addon_id)
            save(profile, state)
        except (ValueError, OSError, TypeError) as exc:
            _message(dialog, "Installationsjournal konnte nicht gespeichert werden: "
                     + type(exc).__name__)
            return
        try:
            xbmc.executebuiltin("InstallAddon(" + addon_id + ")")
        except (RuntimeError, TypeError, ValueError) as exc:
            _message(dialog, "Kodi-Installationsanfrage fehlgeschlagen: "
                     + type(exc).__name__ + "\n"
                     "Der Status wird NICHT als installiert gemeldet. "
                     "Später ausdrücklich erneut anfordern.")
            return
        # Notification cannot obscure Kodi's native installation UI.
        dialog.notification("GS Media Setup", "InstallAddon: " + addon_id +
                            " – Kodi-Dialoge beachten, danach erneut prüfen.",
                            time=5500)
        return

    if code == "PILOT_DONE_NOT_FULL_SETUP":
        _message(dialog, "Alle drei Pilotpakete wurden von Kodi als installiert und "
                 "aktiviert bestätigt.\n\n"
                 "Das ist KEINE vollständige GS-Media-Einrichtung: "
                 "BINGIE MOD, Cumination, xVAULT, TMDB Helper, SlyGuy, "
                 "YouTube, MP3 Streams Echoed, EZ Maintenance und alle "
                 "Skin-/Player-Einstellungen müssen noch freigegeben und "
                 "installiert werden. Kein Kodi-Neustart und kein "
                 "XCMate-Autostart durch diesen Pilot.")
        return

    if code == "REPOSITORY_UNAVAILABLE":
        _message(dialog, "BLOCKIERT: Quelle " + result["repository"]
                 + " ist laut Kodi nicht installiert/aktiviert.\n"
                 "Bitte das offizielle Repository bzw. GS Media separat "
                 "über die Kodi-Add-on-Verwaltung aktivieren. "
                 "Kein externer ZIP-Download oder Repository-Eingriff "
                 "wird automatisch ausgeführt.")
        return

    _message(dialog, "Installationspilot gestoppt: " + code
             + "\nKeine weiteren Änderungen durchgeführt.")
