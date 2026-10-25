"""RAM-only allowed-group/current-channel selection; never mutates settings."""

def target(portal,index,enabled,current_sid=''):
    allowed=[cid for cid in index.groups if enabled is None or cid in enabled]
    current=index.by_sid.get(str(current_sid))
    current_group=str(current.extra.get('category_id') or '') if current else ''
    start=index.by_sid.get(str(portal.get('start_stream_id') or ''))
    saved=str(portal.get('start_group_id') or '')
    category=(current_group if current_group in allowed else saved if saved in allowed else
              str(start.extra.get('category_id') or '') if start and str(start.extra.get('category_id') or '') in allowed else
              allowed[0] if allowed else '')
    rows,positions=index.selection(category,enabled)
    position=positions.get(str(current_sid),positions.get(str(portal.get('start_stream_id') or ''),0))
    return category,position,bool(rows)
