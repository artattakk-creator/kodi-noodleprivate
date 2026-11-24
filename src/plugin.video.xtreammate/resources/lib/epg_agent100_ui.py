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
    phase = receipt.get("remote_phase")
    http = receipt.get("remote_http_status")
    if phase in {"manifest", "asset"} and type(http) is int:
        lines.append(("Manifest" if phase == "manifest" else "EPG-Datei") + f" · HTTP {http}")
    if enabled() and code:
        reason = receipt.get("remote_reason") if code == "PRIVATE_PENDING" else ""
        lines.append(" · ".join(dict.fromkeys(filter(None, (code, reason, selected.get("code"))))))
    return "\n".join(lines)


def show(portal):
    """A single remote-friendly menu; countries come from the live manifest."""
    import xbmcaddon
    import xbmcgui
    from menu_icons45 import select
    from epg_agent_hub5 import selection, save_selection
    from epg_agent100 import profile

    addon = xbmcaddon.Addon()
    dialog = xbmcgui.Dialog()
    names = {"all": "Gesamt-EPG (alle Länder)", "de": "Deutschland",
             "at": "Österreich", "en": "Englisch",
             "es": "Spanisch", "pl": "Polnisch",
             "fr": "Französisch", "it": "Italienisch",
             "tr": "Türkisch", "ar": "Arabisch"}
    row_index = 0
    while True:
        active = enabled()
        current, variant = selection(profile())
        remote = state().get("available_profiles") or ["de", "at"]
        choices = tuple(p for p in remote if isinstance(p, str))
        rows = ["EPG-Agent aktivieren · " + ("Ein" if active else "Aus")]
        actions = [("enable", None)]
        if active:
            for p in choices:
                rows.append(names.get(p, p.upper()) + " · " +
                            ("Ein" if p in current else "Aus"))
                actions.append(("profile", p))
            rows.append("Bildinformationen · " +
                        ("Mit Bildern" if variant == "artwork" else "Standard"))
            actions.append(("variant", None))
            rows.append("Jetzt auf neue EPG-Daten prüfen")
            actions.append(("refresh", None))
        rows.append("Status · " + short_status())
        actions.append(("status", None))
        row_index = select(dialog, "EPG-Agent", rows, actions=[a[0] for a in actions],
                           preselect=min(row_index, len(rows) - 1))
        if not isinstance(row_index, int) or not 0 <= row_index < len(rows):
            return
        action, value = actions[row_index]
        if action == "enable":
            addon.setSetting(SETTING, "false" if active else "true")
            request_check()
        elif action == "profile":
            selected = set(current)
            if value in selected:
                selected.remove(value)
            else:
                selected.add(value)
                if value == "all":
                    selected = {"all"}
                else:
                    selected.discard("all")
            save_selection([x for x in choices if x in selected], variant, profile())
            request_check()
        elif action == "variant":
            save_selection(current,
                           "standard" if variant == "artwork" else "artwork",
                           profile())
            request_check()
        elif action == "refresh":
            if not current:
                dialog.notification("EPG-Agent",
                                    "Bitte zuerst mindestens ein EPG-Profil auswählen.")
            else:
                request_check()
                dialog.notification("EPG-Agent", tr(39119))
        elif action == "status":
            info = "Auswahl: " + (", ".join(current) or "Keine") + "\n"
            info += "Variante: " + variant + "\n\n" + details(portal)
            dialog.textviewer("EPG-Agent", info)
