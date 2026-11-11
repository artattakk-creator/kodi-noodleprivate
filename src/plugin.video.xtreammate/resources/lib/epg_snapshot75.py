"""Optional bounded cold-start checkpoint of existing Now/Next records.

Worker only. Not another guide or mapping store. Restores only the exact saved
profile/provider/configuration and unexpired events; an actual guide read wins.
An invalid/full/unwritable checkpoint cannot break the authoritative reader.
"""
import hashlib,json,os,tempfile,time
MAX_BYTES=2*1024*1024
_saved={}
_due85={}
_page90={}

def _configuration(pid):
    from epg_sources import configuration
    from portals import get_by_id
    from live_warm68 import portal_key
    portal=get_by_id(str(pid))
    if not portal:return ''
    return hashlib.sha256(json.dumps([portal_key(portal),configuration(pid)],sort_keys=True,separators=(',',':')).encode()).hexdigest()

def _path(pid):
    from utils import addon_data_dir
    from epg_handoff63 import identity
    return os.path.join(addon_data_dir(),'home_epg75_'+identity(pid,'snapshot')[:32]+'.json')

def checkpoint(pid,rows):
    from epg_handoff63 import PREFIX,identity,meta_key,profile_scope,MAX_BYTES as ROW_BYTES
    from epg_status import revision
    import xbmcgui
    marker=xbmcgui.Window(10000);records=[]
    try:
        for row in rows[:512]:
            from programme_prefetch48 import station90
            sid=station90(row)
            if not sid:continue
            key=identity(pid,sid);start=int(key[:8],16)%512
            for offset in range(8):
                raw=marker.getProperty(PREFIX+str((start+offset)%512))
                if not raw or len(raw.encode())>ROW_BYTES:continue
                value=json.loads(raw)
                if value.get('key')==key and value.get('revision')==revision(pid):
                    records.append((sid,value));break
        if not records:return False
        value=dict(profile=profile_scope(),pid=str(pid),revision=revision(pid),configuration=_configuration(pid),
                   guide=marker.getProperty(meta_key(pid)),records=records)
        path=_path(pid)
        semantic90=hashlib.sha256(json.dumps([value['configuration'],[(sid,record.get('revision'),record.get('guide_tag'),record.get('binding'),record.get('info',{}).get('events'),record.get('info',{}).get('canonical46')) for sid,record in records]],sort_keys=True).encode()).hexdigest()
        if time.monotonic()<_due85.get(str(pid),0) and _page90.get(path)==semantic90:return False
        # A later visible viewport must not erase the valid start viewport.
        # Merge only the exact profile/account/source/guide generation; the
        # one SQLite guide remains authoritative, not this optional checkpoint.
        try:
            if os.path.islink(path):return False
            with open(path,encoding='utf-8') as stream:old_raw90=stream.read(MAX_BYTES+1)
            old90=json.loads(old_raw90) if len(old_raw90.encode())<=MAX_BYTES else {}
            previous90=old90.get('records',[])
            if all(old90.get(k)==value[k] for k in ('profile','pid','revision','configuration','guide')) and isinstance(previous90,list) and len(previous90)<=512:
                merged90={}
                for item90 in previous90:
                    if not isinstance(item90,list) or len(item90)!=2:continue
                    sid90,record90=item90
                    if not isinstance(sid90,str) or not isinstance(record90,dict) or record90.get('key')!=identity(pid,sid90) or record90.get('revision')!=value['revision'] or record90.get('guide_tag')!=value['guide']:continue
                    if not 0<=time.time()-record90.get('at',0)<6*3600:continue
                    merged90[sid90]=record90
                merged90.update(dict(records));value['records']=list(merged90.items())[-512:]
        except (OSError,ValueError,TypeError,KeyError):pass
        raw=json.dumps(value,separators=(',',':'),allow_nan=False).encode()
        digest=hashlib.sha256(raw).hexdigest()
        if len(raw)>MAX_BYTES or _saved.get(path)==digest:return False
        from import_budget import check_space
        check_space(path,len(raw)+65536)
        fd,tmp=tempfile.mkstemp(prefix='.home-epg75-',dir=os.path.dirname(path))
        try:
            with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
            with open(tmp,'rb') as stream:
                if stream.read()!=raw:raise OSError('EPG_CHECKPOINT_READBACK')
            os.replace(tmp,path);_saved[path]=digest;_page90[path]=semantic90;_due85[str(pid)]=time.monotonic()+60
            while len(_due85)>8:_due85.pop(next(iter(_due85)))
            while len(_page90)>8:_page90.pop(next(iter(_page90)))
        finally:
            if os.path.exists(tmp):os.unlink(tmp)
        while len(_saved)>8:_saved.pop(next(iter(_saved)))
        return True
    except (OSError,ValueError,TypeError,KeyError):return False

def restore(pid):
    from epg_handoff63 import PREFIX,identity,meta_key,profile_scope,MAX_BYTES as ROW_BYTES,get
    from epg_status import revision
    import xbmcgui
    try:
        with open(_path(pid),encoding='utf-8') as stream:raw=stream.read(MAX_BYTES+1)
        if len(raw.encode())>MAX_BYTES:return 0
        data=json.loads(raw);marker=xbmcgui.Window(10000)
        if (data.get('profile')!=profile_scope() or data.get('pid')!=str(pid)
                or data.get('configuration')!=_configuration(pid)):return 0
        existing=marker.getProperty(meta_key(pid));guide=data.get('guide','')
        cold=not existing and not revision(pid)
        if not cold and data.get('revision')!=revision(pid):return 0
        if not isinstance(guide,str) or len(guide)>512 or existing and existing!=guide:return 0
        records=data.get('records',[])
        if not isinstance(records,list) or len(records)>512:return 0
        valid=[]
        for sid,record in records:
            key=identity(pid,sid)
            if record.get('key')!=key or record.get('revision')!=data.get('revision'):continue
            if cold:record=dict(record,revision=revision(pid))
            if not 0<=time.time()-record.get('at',0)<6*3600:continue
            if record.get('guide_tag')!=guide:continue
            encoded=json.dumps(record,separators=(',',':'),allow_nan=False)
            if len(encoded.encode())<=ROW_BYTES:valid.append((sid,key,encoded))
        if not existing and valid:marker.setProperty(meta_key(pid),guide)
        restored=0
        for sid,key,encoded in valid:
            if get(pid,sid) is not None:continue
            start=int(key[:8],16)%512
            for offset in range(8):
                slot=PREFIX+str((start+offset)%512);prior=marker.getProperty(slot)
                if not prior or json.loads(prior).get('key')==key:
                    marker.setProperty(slot,encoded)
                    if get(pid,sid) is not None:restored+=1
                    else:marker.clearProperty(slot)
                    break
        if restored:__import__('startup_diag90').note('EPG_LASTGOOD_AGE',count=restored,age_ms=int(max(0,time.time()-min(json.loads(raw90)['at'] for _,_,raw90 in valid))*1000))
        return restored
    except (OSError,ValueError,TypeError,KeyError,OverflowError):return 0
