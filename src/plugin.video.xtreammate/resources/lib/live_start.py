"""Resolve one configured, enabled station without hydrating a whole catalogue."""


def channel(portal, client):
    from library_index import Reader, IndexReadError
    sid=str(portal.get('start_stream_id') or '')
    if not sid or portal.get('type')!='xtream' or not portal.get('enabled',True):return None
    reader=Reader(portal['id'],timeout=.15,query_seconds=1)
    try:
        if reader.state('live') is not None:
            # An indexed but absent/disabled sender is authoritative. Falling
            # back to a global file here would bypass the user's checkboxes.
            row=reader.get('live',sid)
            return dict(row,stream_id=row['sid'],stream_icon=row.get('stream_icon','')) if row else None
    except IndexReadError:
        return None  # No expensive fallback behind a locked/corrupt index.
    from group_selection import filter_entries
    if callable(getattr(client,'iter_catalog',None)):
        entries=client.iter_catalog('get_live_streams',cached_only=True)
    else:
        entries=client.get_cached_catalog('get_live_streams') or []
    # Legacy/cold profiles retain their existing cache, read at most once.
    try:
        for count,row in enumerate(entries):
            if count>=50000:return None
            if isinstance(row,dict) and str(row.get('stream_id'))==sid:
                return row if filter_entries([row],portal['id'],'live') else None
    except (OSError,ValueError,TypeError):return None
    return None
