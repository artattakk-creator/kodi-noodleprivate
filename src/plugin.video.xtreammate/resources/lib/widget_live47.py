"""Avoid rebuilding an unchanged live group every five seconds.

Only the background service uses this gate. Directory requests and the public
publish API retain their existing behavior. Real guide/policy/art changes and
the next event boundary invalidate immediately; progress is refreshed per minute.
"""
import hashlib,json,os,time
_published={}


def signature(portal,rows):
    from utils import addon_data_dir
    from guide_store import path
    from widget_data41 import policy
    import programme_art46,programme_assets47
    from programme_store46 import path as metadata_path
    digest=hashlib.sha256()
    for row in rows:
        digest.update(json.dumps([row.get(k) for k in ('sid','name','category_id','epg_channel_id',
            'stream_icon','cover','backdrop_path','_manual_art43')],sort_keys=True).encode())
    for filename in (path(),path()+'-wal',metadata_path(),metadata_path()+'-wal',os.path.join(addon_data_dir(),'xtreammate_epg_sources.json')):
        try:stat=os.stat(filename);stamp=(stat.st_mtime_ns,stat.st_size)
        except OSError:stamp=None
        digest.update(repr(stamp).encode())
    digest.update(json.dumps([policy(portal,'live'),int(time.time()//60),
        getattr(programme_art46,'_visual_revision47',0),getattr(programme_assets47,'_visual_revision47',0),programme_art46.fingerprint({})]).encode())
    return digest.hexdigest()


def publish(portal,kind,rows,code='READY'):
    from widget_refresh45 import publish as publish_all,read,trace
    if kind!='live' or code not in ('READY','CACHE') or not rows:
        return publish_all(portal,kind,rows,code)
    from utils import addon_data_dir
    key=(addon_data_dir(),str(portal['id']))
    stamp=signature(portal,rows);now=time.time();old=_published.get(key)
    if old and old[0]==stamp and now<old[1]:
        trace('UNCHANGED','live',len(rows));return False
    if not publish_all(portal,kind,rows,code):return False
    frame=read(portal['id'],'live')
    if frame is None:return True
    due=(int(now//60)+1)*60
    for item in frame['items']:
        for name in ('XtreamMate.Stop','XCMate.ProgrammeNextStart47'):
            try:value=float(item['props'].get(name,0))
            except (TypeError,ValueError):continue
            if now<value<due:due=value
    # Keep the PRE-publication revision: an image can finish while an earlier
    # page is already rendered and must trigger the next tick, not be swallowed.
    _published[key]=(stamp,due)
    if len(_published)>16:_published.pop(next(iter(_published)))
    return True
