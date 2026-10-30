"""Remote-friendly opt-in and read-only API probe, exclusively under Experimentell."""
from localization import tr


def show():
    import xbmcaddon
    import xbmcgui
    from menu_icons45 import select
    from tvmaze59 import enabled, search_title

    dialog = xbmcgui.Dialog()
    while True:
        active = enabled()
        choice = select(dialog, tr(36681), [
            tr(36682 if active else 36683),
            tr(36684), tr(36685)],
            actions=['check', 'activity', 'info'])
        if choice not in (0, 1, 2):
            return
        if choice == 0:
            # Explicit consent before even an anonymous show-title request.
            if dialog.yesno('XCMate · TVmaze', tr(36686 if active else 36687)):
                xbmcaddon.Addon().setSetting('programme_tvmaze59', 'false' if active else 'true')
                dialog.notification('XCMate · TVmaze', tr(36682 if not active else 36683))
        elif choice == 1:
            if not active:
                dialog.ok('XCMate · TVmaze', tr(36688))
                continue
            try:
                matches = search_title('Tatort')
                # Never interpret this diagnostic query as an EPG mapping.
                exact = [row for row in matches if str(row.get('name', '')).casefold() == 'tatort']
                info = ('TVmaze API: ' + ('OK' if matches else 'NO_RESULTS') +
                        '\nTatort: ' + str(len(exact)) + ' exact show entries' +
                        '\nArtwork: ' + ('AVAILABLE' if any(row.get('image') for row in exact) else 'NOT_AVAILABLE') +
                        '\nhttps://www.tvmaze.com/api')
            except Exception as exc:
                info = 'TVmaze API: ' + getattr(exc, 'code', 'UNAVAILABLE')
            dialog.textviewer(tr(36684), info)
        else:
            dialog.textviewer(tr(36685),
                'TVmaze · https://www.tvmaze.com/api\n\n'
                'Free public JSON API; no token. CC BY-SA attribution and share-alike.\n'
                'Episode images require an exact series and episode match.\n'
                'TVmaze is optional; existing provider/XMLTV EPG always takes precedence.\n'
                'No TVmaze metadata is requested for provider VOD or series widgets.')


def status_label(code):
    """Human-readable EPG image status; never a disruptive popup."""
    ids = {
        'TVMAZE_NO_MATCH': 36689,
        'TVMAZE_NO_IMAGE': 36690,
        'TVMAZE_AMBIGUOUS': 36691,
        'TVMAZE_MOVIE_UNAVAILABLE': 36692,
        'TVMAZE_TYPE_MISMATCH': 36693,
        'TVMAZE_EPISODE_UNCERTAIN': 36694,
        'TVMAZE_RATE_LIMIT': 36695,
        'TVMAZE_NETWORK_ERROR': 36696,
        'TVMAZE_NOT_FOUND': 36689,
    }
    return tr(ids.get(code, 36697)) if str(code).startswith('TVMAZE_') else str(code)
