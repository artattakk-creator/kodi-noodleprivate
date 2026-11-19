"""GS Media Setup 0.5.28 entry point."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "resources/lib"))


def run():
    import xbmc
    import xbmcgui

    from setup_auto_store50 import load
    from setup_auto_ui50 import TITLE, _context, _lock, exclusive, request_stop, rollback
    from setup_auto_ui50 import run as install
    from setup_compat27 import Blocked, current_platform
    from setup_finish27 import read_marker
    from setup_options27 import configure

    dialog = xbmcgui.Dialog()
    profile = _context()
    try:
        state, marker = load(profile), read_marker(profile)
        if not current_platform(xbmc):
            install()
            return
        if _lock().getProperty("GS_MEDIA_050_RUNNING") == "1":
            if dialog.select(TITLE, ["Installation sicher anhalten"]) == 0:
                request_stop()
            return
        if marker and marker["status"] in ("pending", "failed"):
            labels = ["Gesicherte Konfiguration wiederherstellen"]
            actions = [rollback]
        else:
            action = "Installation starten"
            if marker and marker["status"] == "restart_pending":
                action = "Kodi neu starten"
            elif marker and marker["status"] == "complete":
                action = "Installationsstatus anzeigen"
            elif state and (state["pending"] or state["stopped"]):
                action = "Installation fortsetzen"
            labels, actions = [action], [install]
            if marker and marker["status"] == "complete":
                def optional():
                    with exclusive(profile):
                        configure()
                labels.append("TMDB, Bild-EPG und Speicher einrichten")
                actions.append(optional)
        error = (state or {}).get("last_error") or (marker or {}).get("error")
        if error:
            labels.append("Fehlerdiagnose anzeigen")
            actions.append(lambda: dialog.ok(TITLE, error))
        choice = dialog.select(TITLE, labels)
        if 0 <= choice < len(actions):
            actions[choice]()
    except (Blocked, OSError, TypeError, ValueError, RuntimeError, KeyError):
        dialog.ok(TITLE, "Einrichtungsjournal nicht verfügbar. Bitte nach Behebung erneut öffnen.")


if __name__ == "__main__":
    run()
