"""Home-only provider-category allowlist. Library selections never change."""
import hashlib
import json
from utils import setting
KEY='home_vod_groups92'

def context(pid):
    from portals import get_by_id
    from epg_handoff63 import profile_scope
    portal=get_by_id(str(pid)) or {}
    identity=[profile_scope(),str(pid)]+[portal.get(k) for k in ('id','xc_host','xc_user','xc_pass','type')]
    return hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()

def read():
    raw=setting(KEY,'')
    if not raw:return {}
    if len(raw.encode())>65536:raise ValueError('HOME_FILTER_LIMIT')
    value=json.loads(raw)
    if not isinstance(value,dict) or len(value)>32:raise ValueError('HOME_FILTER_INVALID')
    for key,ids in value.items():
        if len(key)!=64 or not isinstance(ids,list) or len(ids)>2048 or any(not isinstance(i,str) or len(i)>160 for i in ids):raise ValueError('HOME_FILTER_INVALID')
    return value

def selected(pid):return read().get(context(pid))
def allowed(pid,ids):
    chosen=selected(pid)
    return set(ids) if chosen is None else set(ids).intersection(chosen)

def signature(pid):
    value=selected(pid)
    return '' if value is None else hashlib.sha256(json.dumps(sorted(value)).encode()).hexdigest()

def save(pid,ids):
    import xbmcaddon
    value=read();value[context(pid)]=sorted(set(map(str,ids)))
    raw=json.dumps(value,sort_keys=True,separators=(',',':'))
    if len(raw.encode())>65536 or len(value)>32:raise ValueError('HOME_FILTER_LIMIT')
    addon=xbmcaddon.Addon('plugin.video.xtreammate');addon.setSetting(KEY,raw)
    if json.loads(addon.getSetting(KEY))!=value:raise OSError('HOME_FILTER_READBACK')

def manage(portal):
    import xbmcgui
    from artwork_ui import job
    from localization import tr
    def groups(cancel,progress):
        from library_index import Reader
        return Reader(portal['id']).groups('vod')
    rows=job(groups)
    if rows is None:return
    chosen=selected(portal['id']);ids=[str(g['cid']) for g in rows]
    preselect=[i for i,cid in enumerate(ids) if chosen is None or cid in chosen]
    result=xbmcgui.Dialog().multiselect(tr(38729),[str(g.get('title') or g.get('name') or g['cid']) for g in rows],preselect=preselect)
    if result is None:return
    save(portal['id'],[ids[i] for i in result if type(i) is int and 0<=i<len(ids)])
