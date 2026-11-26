"""Resolve one configured, enabled station without hydrating a whole catalogue."""


def channel(portal, client):
    from library_index import Reader, IndexReadError
    sid=str(portal.get('start_stream_id') or '')
    if not sid or portal.get('type')!='xtream' or not portal.get('enabled',True):return None
    from group_selection import enabled_ids, filter_entries
    group=str(portal.get('start_group_id') or '*')
    selected=group!='*'
    if selected and group not in enabled_ids(portal['id'],'live',[{'category_id':group}]):
        return None
    reader=Reader(portal['id'],timeout=.15,query_seconds=1)
    try:
        indexed=reader.state('live') is not None
        if indexed:
            row=reader.get('live',sid)
            if row and (not selected or str(row.get('category_id'))==group):
                return dict(row,stream_id=row['sid'],stream_icon=row.get('stream_icon',''))
            if not selected:return None
    except IndexReadError:
        return None
    finally:
        close=getattr(reader,'close',None)
        if close:close()
    if callable(getattr(client,'iter_catalog',None)):
        entries=client.iter_catalog('get_live_streams',cached_only=True)
    else:
        entries=client.get_cached_catalog('get_live_streams') or []
    # Legacy/cold profiles retain their existing cache, read at most once.
    try:
        for count,row in enumerate(entries):
            if count>=50000:return None
            if (isinstance(row,dict) and str(row.get('stream_id'))==sid
                    and (not selected or str(row.get('category_id'))==group)
                    and filter_entries([row],portal['id'],'live')):
                return row
    except (OSError,ValueError,TypeError):return None
    return None


def resolve(portal, client):
    """A temporarily unreadable index is never evidence of invalid settings."""
    if not portal.get('start_stream_id'):
        return dict(code='START_NOT_CONFIGURED', channel=None)
    row=channel(portal,client)
    return dict(code='READY' if row else 'START_TEMPORARILY_UNAVAILABLE',channel=row)
