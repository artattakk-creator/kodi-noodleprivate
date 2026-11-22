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
    """One user-facing Agent panel: toggle, countries, refresh, read-only status."""
    import xbmcaddon
    import xbmcgui
    from menu_icons45 import select
    from epg_agent_hub4 import selected as countries
    addon = xbmcaddon.Addon()
    dialog = xbmcgui.Dialog()
    selected_row = 0

    def on(key):
        return addon.getSetting(key) == "true"

    while True:
        active = enabled()
        rows = ["EPG-Agent aktivieren · " + ("Ein" if active else "Aus")]
        actions = ["toggle"]
        if active:
            for code, label in (("de", "Deutschland"), ("at", "Österreich"),
                                ("all", "Alle Länder (Gesamt-EPG)")):
                rows.append(label + " · " + ("Ein" if on("epg_agent_country_" + code) else "Aus"))
                actions.append("country_" + code)
            rows.append("Jetzt aktualisieren")
            actions.append("refresh")
        rows.append("Status · " + short_status())
        actions.append("status")
        selected_row = select(dialog, "EPG-Agent", rows, actions=actions,
                              preselect=min(selected_row, len(rows) - 1))
        if not isinstance(selected_row, int) or selected_row < 0 or selected_row >= len(rows):
            return
        action = actions[selected_row]
        if action == "toggle":
            addon.setSetting(SETTING, "false" if active else "true")
            request_check()
        elif action.startswith("country_") and active:
            key = "epg_agent_" + action
            addon.setSetting(key, "false" if on(key) else "true")
            request_check()
        elif action == "refresh":
            if not countries():
                dialog.notification("EPG-Agent", "Bitte zuerst mindestens ein Land auswählen.")
            else:
                request_check()
                dialog.notification("EPG-Agent", tr(39119))
        elif action == "status":
            dialog.textviewer("EPG-Agent", "Gewählte Länder: " +
                              (", ".join(countries()) or "Keine") + "\n\n" + details(portal))
