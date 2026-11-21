"""Skin-independent Agent opt-in and status from the last service receipt."""
import time
from localization import tr
from epg_agent100 import SETTING, SOURCE_NAME, enabled, request_check, state

LABELS = {
    "CURRENT": 39104,
    "CHECKING": 39105,
    "IMPORTING": 39105,
    "PRIVATE_ENDPOINT_NETWORK_ERROR": 39106,
    "PRIVATE_ENDPOINT_TEMPORARILY_UNAVAILABLE": 39106,
    "PRIVATE_PENDING": 39109,
    "AUTH_NOT_PROVISIONED": 39110,
    "IMPORT_PENDING": 39111,
}


def _when(value):
    return time.strftime("%d.%m.%Y %H:%M", time.localtime(value)) if value else "–"


def short_status():
    if not enabled():
        return tr(39108)
    code = state().get("code")
    return tr(LABELS.get(code, 39107)) if code else tr(39120)


def details(portal):
    receipt = state()
    selected = receipt.get("portals", {}).get(str((portal or {}).get("id", "")), {})
    code = receipt.get("code", "")
    lines = [
        short_status(),
        f"{tr(39112)}  {_when(receipt.get('last_checked'))}",
        f"{tr(39113)}  {_when(receipt.get('next_check'))}",
        f"{tr(39114)}  {_when(selected.get('last_success'))}",
        f"{tr(39115)}  {selected.get('generation', '')[:16] or '–'}",
        f"{tr(39116)}  {receipt.get('channels', 0)} / {receipt.get('programmes', 0)} / {receipt.get('artwork_records', 0)}",
        f"{tr(39117)}  {selected.get('matched', 0)} / {selected.get('mapped_channels', 0)}",
        f"{tr(39118)}  {selected.get('read', 0)} / {selected.get('committed', 0)} / {selected.get('verified', 0)}",
        tr(39121), tr(39123),
    ]
    images = receipt.get("image_counts", {})
    if images:
        lines.append(f"{tr(39124)}  {images.get('poster', 0)} / {images.get('backdrop', 0)} / "
                     f"{images.get('still', 0)} / {images.get('channel_logo', 0)}")
    if enabled() and code:
        reason = receipt.get("remote_reason") if code == "PRIVATE_PENDING" else ""
        lines.append(" · ".join(dict.fromkeys(filter(None, (code, reason, selected.get("code"))))))
    return "\n".join(lines)


def show(portal):
    """Owner-entered private credentials; validated regular manifest only."""
    import xbmcaddon
    import xbmcgui
    from menu_icons45 import select
    from epg_agent100 import profile
    from epg_agent_credentials import NAME, clear_token, import_token_file, store_token
    from epg_agent_github import DeliveryError, probe

    addon = xbmcaddon.Addon()
    dialog = xbmcgui.Dialog()
    selected = 0
    while True:
        active = enabled()
        rows = [tr(39101) + " · " + tr(36029 if active else 36028)]
        actions = ["toggle"]
        if active:
            rows.append(tr(39102))
            actions.append("refresh")
        rows.extend([
            "Privaten GitHub-Zugang eingeben",
            "Token-Datei importieren (USB / interner Speicher / Netzwerk)",
            "Geschuetzten EPG-Serverstatus abfragen",
            "Gespeichertes Zugriffstoken entfernen",
            tr(39103) + " · " + short_status(),
        ])
        actions.extend(["token", "import", "probe", "clear", "activity"])
        selected = select(dialog, SOURCE_NAME, rows, actions=actions,
                          preselect=min(selected, len(rows) - 1))
        if not isinstance(selected, int) or selected < 0 or selected >= len(rows):
            return
        action = actions[selected]
        if action == "toggle":
            addon.setSetting(SETTING, "false" if active else "true")
            if enabled() == active:
                dialog.notification(SOURCE_NAME, tr(39122))
            elif not active:
                request_check()
        elif action == "refresh":
            request_check()
            dialog.notification(SOURCE_NAME, tr(39119))
        elif action == "token":
            value = dialog.input("GitHub-Read-only-Token", type=xbmcgui.INPUT_ALPHANUM,
                                 option=xbmcgui.ALPHANUM_HIDE_INPUT)
            if not value:
                continue
            try:
                store_token(profile(), value)
            except (DeliveryError, OSError):
                dialog.notification(SOURCE_NAME, "Token ungueltig oder nicht speicherbar")
            else:
                dialog.notification(SOURCE_NAME, "Token nur lokal gespeichert. Rechte pruefen.")
            finally:
                del value
        elif action == "import":
            # Kodi's native VFS browser traverses local, USB and configured
            # SMB/NFS sources. This never uploads the file to GitHub.
            try:
                path = dialog.browseSingle(
                    1, "Token-Datei wählen: USB / intern / Netzwerk",
                    "", "", False, False, "")
            except (OSError, RuntimeError, ValueError):
                dialog.notification(SOURCE_NAME, "Dateiauswahl nicht verfügbar")
                continue
            if not path:
                continue
            try:
                import_token_file(profile(), path)
            except (DeliveryError, OSError) as exc:
                reason = exc.code if isinstance(exc, DeliveryError) else "TOKEN_FILE_READ_FAILED"
                dialog.notification(SOURCE_NAME, "Token-Import fehlgeschlagen: " + reason)
                continue
            # A valid syntax is not proof of GitHub permissions; probe once.
            try:
                result = probe(profile() / NAME)
            except DeliveryError as exc:
                dialog.notification(SOURCE_NAME,
                    "Token lokal importiert; Zugriff ungeprüft: " + exc.code)
            else:
                dialog.textviewer(SOURCE_NAME,
                    "Token-Datei erfolgreich lokal importiert.\n"
                    "Privater GitHub-Zugriff bestätigt.\n"
                    "EPG-Status: {}\n\n"
                    "Die Quelldatei auf USB oder Netzwerk wurde nicht gelöscht. "
                    "Bitte sicher aufbewahren oder eigenständig entfernen.".format(
                        result["status"]))
        elif action == "probe":
            try:
                status = probe(profile() / NAME)
            except DeliveryError as exc:
                dialog.notification(SOURCE_NAME, "EPG-Pruefung: " + exc.code)
            else:
                if status["status"] == "PRIVATE_PENDING":
                    dialog.textviewer(SOURCE_NAME,
                        "Privates Repository erreichbar, EPG aber noch nicht freigegeben.\n"
                        "Produktionsstatus: PRIVATE_PENDING.\n"
                        "Keine echte EPG-XMLTV-Datei vorhanden.\n"
                        "Anbieter-EPG bleibt unveraendert.")
                else:
                    dialog.textviewer(SOURCE_NAME,
                        "Geschuetzter Produktiv-EPG authentifiziert.\n"
                        "Status: {}\nSender: {}\nSendungen: {}\nSHA256: {}".format(
                            status["status"], status["channel_count"],
                            status["programme_count"], status["sha256"][:16]))
        elif action == "clear":
            if dialog.yesno(SOURCE_NAME,
                    "Lokales Token entfernen? Fuer vollstaendigen Widerruf "
                    "Token zusaetzlich bei GitHub deaktivieren."):
                try:
                    clear_token(profile())
                except (DeliveryError, OSError):
                    dialog.notification(SOURCE_NAME, "Token konnte nicht entfernt werden")
                else:
                    dialog.notification(SOURCE_NAME, "Lokales Token entfernt")
        else:
            dialog.textviewer(SOURCE_NAME, details(portal))
