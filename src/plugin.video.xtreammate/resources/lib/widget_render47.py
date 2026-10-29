"""Prepare one native widget page from a common local read snapshot."""
def values(portal,kind,rows,approved):
    import sqlite3
    from programme_read47 import session
    from programme_assets47 import read_many
    from widget_items45 import describe
    with session():
        if kind=='live':
            from widget_group46 import infos
            try:epg=infos(portal,rows)
            except (OSError,sqlite3.Error,ValueError,TypeError):
                epg={}
                from widget_diagnostics47 import note
                note(portal['id'],kind,'ASSETS','LOCAL_EPG_UNAVAILABLE',selected=len(rows))
        else:epg={}
        assets=read_many(portal['id'],kind,rows)
        return [describe(portal,kind,row,approved,epg.get(row['sid']),
                         assets47=assets.get(str(row['sid']))) for row in rows]
