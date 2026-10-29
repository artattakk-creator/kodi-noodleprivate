"""Read existing catalogues without acquiring a snapshot-publication lease.

No cache publication, importer, schema migration or writable DB connection.
The cache lock protects writers, not these pinned SQLite RO transactions.
"""
def read(portal,kind):
    import sqlite3
    from library_index import IndexReadError
    from widget_movie47 import MovieReader
    if not portal.get('include_'+kind,True):return [],'DISABLED'
    reader=MovieReader(portal['id'],kind=kind)
    try:
        if not reader.state(kind):return [],'INDEX_MISSING'
        if kind=='live':
            from widget_home50 import rows
            values,code=rows(portal)
            return values,'READ_ONLY' if code=='READY' else code
        return reader.small(kind,limit=24),'READ_ONLY'
    except (IndexReadError,sqlite3.Error,OSError,ValueError,TypeError) as exc:
        return [],getattr(exc,'code','UNAVAILABLE')
    finally:reader.close()
