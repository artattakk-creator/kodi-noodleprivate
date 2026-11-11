"""Coherent last-known-good widget frames and cross-interpreter publication.

Policy binds account/profile/selection, source revision binds catalogue content.
Transient art/EPG misses never authorize removing catalogue rows or active EPG.
No network, image archive, skin setting or user database mutation.
"""
import contextlib,functools,hashlib,json,os,threading,time
_local=threading.local()

def source(portal,kind,rows):
    from widget_data41 import files,policy,read
    source89=__import__('widget_snapshot85').source89(portal,kind,rows)
    if source89 is not None:return source89
    value=read(files(portal['id'],kind)[0],policy(portal,kind))
    if not value:return None
    if [r.get('sid') for r in value['rows']]!=[r.get('sid') for r in rows]:return None
    return value.get('revision44')

def old_frame(portal,kind):
    from widget_refresh45 import read
    value=read(portal['id'],kind)
    from widget_data41 import policy
    return value if value and value.get('policy')==policy(portal,kind) else None

def merge(portal,kind,items,rows,old=None):
    revision=source(portal,kind,rows)
    if not old:return items,revision
    if revision is None and old.get('source_revision74') is not None:
        from widget_data41 import read,files,policy
        current=read(files(portal['id'],kind)[0],policy(portal,kind))
        if current is not None and [r.get('sid') for r in current['rows']]!=[r.get('sid') for r in rows]:
            note(portal,kind,'HOLD_STALE_SOURCE',old,len(items),revision,new_art_status=art_status(items))
            return list(old['items']),old['source_revision74']
    prior=list(old['items']);by_id={v['props'].get('XCMate.MediaId'):v for v in prior}
    if revision is not None and old.get('source_revision74') is not None and revision!=old['source_revision74']:
        # A new complete catalogue revision permits real removals/replacements.
        keep_missing=False
    else:keep_missing=True
    current={v['props'].get('XCMate.MediaId') for v in items}
    if keep_missing and len(current)<len(by_id):
        # No authoritative source change: keep the complete known row set.
        # A selection/account change already invalidates old_frame's policy.
        note(portal,kind,'HOLD_PARTIAL',old,len(items),revision,new_art_status=art_status(items))
        return prior,old.get('source_revision74')
    result=[];now=time.time();current_sources=source_refs(rows);rows_by_id={str(r.get('sid')):r for r in rows}
    for item in items:
        sid=item['props'].get('XCMate.MediaId');previous=by_id.get(sid)
        if kind in ('vod','series') and item['props'].get('XCMate.NoImage86')=='true':
            item['art']={k:'' for k in ('poster','thumb','icon','fanart','landscape')};item['_provider80']={}
            result.append(item);continue
        if kind in ('vod','series') and item['props'].get('XCMate.ManualArt86')=='true':
            result.append(item);continue
        if previous:
            from widget_assets69 import renderable
            for role,uri in previous.get('art',{}).items():
                if not renderable(item['art'].get(role)) and renderable(uri):
                    # Only retain a source with matching current provider proof.
                    from widget_refs74 import read as retained
                    row=rows_by_id.get(sid)
                    permitted=retained(portal,kind,[row]).get(sid,{}) if row else {}
                    if uri in permitted.values() or (old.get('source_refs74',{}).get(sid)==current_sources.get(sid) and sid in current_sources and os.path.isabs(uri) and os.path.isfile(uri) and not os.path.islink(uri)):item['art'][role]=uri
            if kind=='live':
                props=item['props'];oldprops=previous['props']
                try:active=float(oldprops.get('XtreamMate.Start',0))<=now<float(oldprops.get('XtreamMate.Stop',0))
                except (TypeError,ValueError):active=False
                if active and not props.get('XtreamMate.Now'):
                    # Current event only, same channel/account, until its end.
                    # Explicit EPG source/mapping invalidation is checked below.
                    from epg_status import revision as epg_revision
                    if old.get('epg_revision74')==epg_revision(portal['id']):
                        for key,value in oldprops.items():
                            if key.startswith(('XtreamMate.','XCMate.Programme','XCMate.Epg','XCMate.ArtProof')):props[key]=value
                        item['info']['plot']=previous['info'].get('plot','')
            row80=rows_by_id.get(sid)
            if row80:__import__('home_publication80').reconcile(portal,kind,item,previous,row80,same_revision82=revision is not None and revision==old.get('source_revision74'))
        result.append(item)
    return result,revision

def source_refs(rows):
    from programme_assets47 import sources
    return {str(row['sid']):hashlib.sha256(json.dumps(sources(row,provider_only=True),sort_keys=True).encode()).hexdigest() for row in rows}

def art_status(items):
    # Reference readiness, never a claim that Kodi decoded/displayed the image.
    from widget_assets69 import renderable
    total=len(items)
    if not total:return 'EMPTY'
    ready=sum(bool(renderable(item.get('art',{}).get('poster'))) for item in items)
    return 'REFERENCE_READY' if ready==total else 'REFERENCE_PARTIAL' if ready else 'REFERENCE_PENDING'

def note(portal,kind,reason,old,new_count,revision,new_generation='',new_art_status='UNKNOWN'):
    try:
        import xbmc
        pid=hashlib.sha256(str(portal['id']).encode()).hexdigest()[:12]
        oldrev=old.get('source_revision74') if old else None
        statuses=('EMPTY','REFERENCE_READY','REFERENCE_PARTIAL','REFERENCE_PENDING')
        old_status=old.get('art_status74','UNKNOWN') if old else 'EMPTY'
        old_status=old_status if old_status in statuses else 'UNKNOWN'
        new_status=new_art_status if new_art_status in statuses else 'UNKNOWN'
        digest=lambda v:hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest()[:12]
        xbmc.log('[XCMate][HOME74] portal='+pid+' kind='+kind+' reason='+reason+
            ' old_generation='+str(old.get('signature','')[:12] if old else '')+
            ' new_generation='+str(new_generation[:12])+' old_count='+str(len(old['items']) if old else 0)+' new_count='+str(new_count)+
            ' source_revision='+digest(revision)+' old_revision='+digest(oldrev)+
            ' old_art_status='+old_status+' new_art_status='+new_status,xbmc.LOGINFO)
    except (ImportError,AttributeError,RuntimeError,ValueError,TypeError):pass

def signature(items,kind):
    # Wall-clock lease/progress bookkeeping is not a catalogue change. Progress
    # remains a real per-minute update for Live, not a two-second publication.
    stripped=[]
    for item in items:
        copy=dict({k:v for k,v in item.items() if not k.startswith('_')},props={k:v for k,v in item['props'].items() if k not in ('XtreamMate.Progress','XCMate.EpgPercent41','XCMate.EpgAt64','XCMate.ArtProof69','XCMate.Source85')})
        stripped.append(copy)
    minute=0  # focused progress is updated by the existing Hero GUI pump
    return hashlib.sha256(json.dumps([stripped,minute],sort_keys=True).encode()).hexdigest()

def serialized(call):
    @functools.wraps(call)
    def run(portal,*args,**kwargs):
        kind=(args[0] if args else kwargs['kind']) if call.__module__=='widget_refresh45' else 'live'
        from widget_refresh45 import path,trace
        filename=path(portal['id'],kind)+'.publish74.lock'
        active=getattr(_local,'active',set())
        if filename in active:return call(portal,*args,**kwargs)
        import fcntl
        fd=os.open(filename,os.O_CREAT|os.O_RDWR|getattr(os,'O_NOFOLLOW',0),0o600)
        try:
            try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:trace('DEFERRED',kind);return False
            _local.active=active|{filename}
            return call(portal,*args,**kwargs)
        finally:
            _local.active=active;os.close(fd)
    return run
