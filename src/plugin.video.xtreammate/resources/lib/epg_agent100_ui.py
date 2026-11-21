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
    """Interactive, per-device token provisioning plus isolated private readback."""
    import xbmcaddon
    import xbmcgui
    from menu_icons45 import select
    from epg_agent100 import profile
    from epg_agent_credentials import NAME, clear_token, store_token
    from epg_agent_github import DeliveryError, stage_full_candidate

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
            "Privates GitHub-Zugriffstoken eingeben",
            "Geschuetzten XMLTV-Testfeed pruefen (kein Live-Import)",
            "Lokal gespeichertes Zugriffstoken entfernen",
            tr(39103) + " · " + short_status(),
        ])
        actions.extend(["token", "demo", "clear", "activity"])
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
            value = dialog.input("Privates GitHub-Read-only-Token", type=xbmcgui.INPUT_ALPHANUM,
                                 option=xbmcgui.ALPHANUM_HIDE_INPUT)
            if not value:
                continue
            try:
                store_token(profile(), value)
            except (DeliveryError, OSError):
                dialog.notification(SOURCE_NAME, "Token ungueltig oder nicht speicherbar")
            else:
                dialog.notification(SOURCE_NAME, "Token lokal gespeichert. Rechte bitte mit Test pruefen.")
            finally:
                del value
        elif action == "demo":
            try:
                # Separate directory; never hand synthetic data to the real guide importer.
                result = stage_full_candidate(profile() / "demo-readback",
                                              profile() / NAME, demo=True)
            except (DeliveryError, OSError, InterruptedError) as exc:
                reason = exc.code if isinstance(exc, DeliveryError) else "DEMO_READBACK_ERROR"
                dialog.notification(SOURCE_NAME, "Privater EPG-Test fehlgeschlagen: " + reason)
            else:
                if result["status"] not in ("STAGED_FULL_CANDIDATE", "UNCHANGED"):
                    dialog.notification(SOURCE_NAME, "Unerwarteter Demo-Status")
                    continue
                dialog.textviewer(SOURCE_NAME,
                    "Privater GitHub-XMLTV-Abruf erfolgreich.\\n"
                    "Ausschliesslich synthetische Testdaten; kein Live-Import.\\n\\n"
                    "Datei: demo/xcmate-epg.xml.gz\\n"
                    "Authentifizierung: OK\\n"
                    "GZIP/XMLTV/SHA256: OK\\n"
                    "Sender: {}\\nSendungen: {}\\nPruefsumme: {}".format(
                        result["channels"], result["programmes"], result["generation"][:16]))
        elif action == "clear":
            if dialog.yesno(SOURCE_NAME,
                    "Lokales Zugriffstoken entfernen? Zur vollstaendigen Sperrung "
                    "das Token zusaetzlich bei GitHub widerrufen."):
                try:
                    clear_token(profile())
                except (DeliveryError, OSError):
                    dialog.notification(SOURCE_NAME, "Token konnte nicht entfernt werden")
                else:
                    dialog.notification(SOURCE_NAME, "Lokales Token entfernt")
        else:
            dialog.textviewer(SOURCE_NAME, details(portal))
