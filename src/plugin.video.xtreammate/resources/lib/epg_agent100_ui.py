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
    if enabled() and code:
        lines.append(" · ".join(dict.fromkeys(filter(None, (code, selected.get("code"))))))
    return "\n".join(lines)


def show(portal):
    import xbmcaddon
    import xbmcgui
    from menu_icons45 import select
    addon = xbmcaddon.Addon()
    dialog = xbmcgui.Dialog()
    selected = 0
    while True:
        active = enabled()
        rows = [tr(39101) + " · " + tr(36029 if active else 36028)]
        actions = ["check" if active else "back"]
        if active:
            rows.append(tr(39102))
            actions.append("refresh")
        rows.append(tr(39103) + " · " + short_status())
        actions.append("activity")
        selected = select(dialog, SOURCE_NAME, rows, actions=actions,
                          preselect=min(selected, len(rows) - 1))
        if not isinstance(selected, int) or selected < 0 or selected >= len(rows):
            return
        if selected == 0:
            addon.setSetting(SETTING, "false" if active else "true")
            if enabled() == active:
                dialog.notification(SOURCE_NAME, tr(39122))
            elif not active:
                request_check()
        elif active and selected == 1:
            request_check()
            dialog.notification(SOURCE_NAME, tr(39119))
        else:
            dialog.textviewer(SOURCE_NAME, details(portal))
