# -*- coding: utf-8 -*-
"""XCMate Media Center Setup — minimal Kodi 21.3 installation entrypoint.

Exactly one primary action. A second log action appears only after an actual
setup/post-restart error. Advanced pilots and diagnostics remain in source but
are deliberately NOT exposed in the normal installer menu.
"""
from pathlib import Path
import sys

LIB = Path(__file__).resolve().parent / "resources" / "lib"
sys.path.insert(0, str(LIB))
TITLE = "XCMate Media Center Setup – v0.5.13 – Kodi 21.3 Omega"


def _profile():
    import xbmcaddon
    import xbmcvfs
    return xbmcvfs.translatePath(
        xbmcaddon.Addon("script.gsmedia.setup").getAddonInfo("profile"))


def _error(profile):
    from setup_auto_store50 import load as load_auto
    from setup_finish_0512 import read as read_handoff
    state = load_auto(profile)
    marker = read_handoff(profile)
    reason = state.get("last_error", "") if state and state.get("stopped") else ""
    if marker and marker.get("status") == "failed":
        reason = reason or marker.get("error", "")
    return reason, state, marker


def run():
    import xbmcgui
    dlg = xbmcgui.Dialog()
    try:
        profile = _profile()
    except (ValueError, OSError, RuntimeError, AttributeError):
        dlg.ok(TITLE, "Kodi-Profil konnte nicht gelesen werden. Keine Installation gestartet.")
        return
    while True:
        try:
            reason, state, marker = _error(profile)
        except (ValueError, OSError, RuntimeError, KeyError):
            dlg.ok(TITLE, "Installationsprotokoll ist beschädigt oder unzugänglich. "
                         "Bitte nicht zurücksetzen; Kodi-Log prüfen.")
            return
        choices = ["Installation starten"]
        if reason:
            choices.append("Fehlerprotokoll anzeigen")
        selection = dlg.select(TITLE, choices)
        if selection == -1:
            return
        if selection == 1 and reason:
            done = len(state.get("completed", [])) if state else 0
            details = [
                "XCMate Media Center Setup – Diagnose",
                "Kodi-Zielversion: 21.3 Omega",
                "Installationsstatus: " + (state.get("stage", "") if state else "nicht lesbar"),
                "Bestätigte Einträge im Journal: " + str(done),
                "Fehler: " + reason,
                "Kodi-Log: special://logpath/kodi.log",
                "GitHub: artattakk-creator/kodi-noodleprivate",
                "Keine Daten gelöscht. Nach Korrektur Installation starten.",
            ]
            if marker and marker.get("error") and marker["error"] != reason:
                details.append("Neustart-Prüfung: " + marker["error"])
            dlg.textviewer("XCMate – Fehlerprotokoll", "\n".join(details), usemono=True)
            continue
        if selection == 0:
            from setup_auto_ui50 import run as run_auto
            run_auto()
            # On failures the menu reopens with a dedicated diagnostic action.
            # On successful completion the wizard displays one reboot OK dialog.
            try:
                reason_after, _state, _marker = _error(profile)
                if reason_after:
                    continue
            except (ValueError, OSError, RuntimeError, KeyError):
                pass
            return


if __name__ == "__main__":
    run()
