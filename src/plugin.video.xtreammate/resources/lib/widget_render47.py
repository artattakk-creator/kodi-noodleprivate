"""Prepare one native widget page from a common local read snapshot."""
def values(portal,kind,rows,approved):
    import sqlite3
    from programme_read47 import session
    from programme_assets47 import read_many
    from widget_items45 import describe
    if kind in ('vod','series'):
        rows=__import__('media_overrides43').widget_rows86(portal['id'],kind,rows)
    with session():
        if kind=='live':
            from widget_group46 import infos
            try:epg=infos(portal,rows)
            except (OSError,sqlite3.Error,ValueError,TypeError):
                epg={}
                from widget_diagnostics47 import note
                note(portal['id'],kind,'ASSETS','LOCAL_EPG_UNAVAILABLE',selected=len(rows))
        else:epg={}
        assets=read_many(portal['id'],kind,rows,provider_only=kind in ('vod','series'))
        values=[describe(portal,kind,row,approved,epg.get(row['sid']),
                         assets47=assets.get(str(row['sid']))) for row in rows]
        # Artwork admission must never remove a valid catalogue row.
        return values
