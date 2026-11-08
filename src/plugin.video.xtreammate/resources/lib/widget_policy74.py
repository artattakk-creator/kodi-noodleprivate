"""Stable selection/account identity; catalogue revision is separate evidence.

A WAL timestamp from an unrelated film/EPG write is not a Live source change.
No SQLite/network access in policy consumers.
"""
import hashlib,json,os

def signature(portal,kind,offset=0):
    from utils import addon_data_dir,setting_int
    from epg_handoff63 import profile_scope
    from group_selection import _state,_read
    selected=_state(_read(),portal['id'],kind)
    selection={'enabled':sorted(selected['enabled']),'auto_new':selected['auto_new'],'known':sorted(selected['known']) if selected['auto_new'] else None} if selected else None
    identity=[portal.get(k) for k in ('id','type','xc_host','xc_user','xc_pass','enabled')]
    value=['CONTEXT74',profile_scope(),identity,kind,portal.get('include_'+kind,True),
        portal.get('start_group_id'),portal.get('start_stream_id'),selection,offset,setting_int('recent_keep',100)]
    return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
