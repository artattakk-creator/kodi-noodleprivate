"""Opt-in four/eight hour process samples; bounded private numeric-only JSONL."""
import gc,json,os,sys,threading,time,uuid,math
from pathlib import Path
import service_runtime as runtime

_worker=None;_stop=threading.Event();_guard=threading.Lock();_next=0
PHASES=('IDLE','LIVE','FILM','SERIES','EPG','USB','SMB','UPDATE')


def path(name='session.json'):
    from utils import addon_data_dir
    return Path(addon_data_dir())/('stability_'+name)


def config():
    try:
        with path().open(encoding='utf-8') as stream:raw=stream.read(2049)
        value=json.loads(raw) if len(raw)<=2048 else {}
        if not isinstance(value,dict) or any(not isinstance(value.get(k),(int,float)) or not math.isfinite(value[k]) for k in ('start','end')):return {}
        return value
    except (OSError,ValueError):return {}


def start(hours=4,phase='IDLE'):
    value=dict(id=uuid.uuid4().hex,start=time.time(),end=time.time()+min(8,max(1,int(hours)))*3600,phase=phase if phase in PHASES else 'IDLE')
    save(value);return value


def save(value):
    target=path();temporary=target.with_name('.stability-'+uuid.uuid4().hex)
    descriptor=os.open(str(temporary),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        with os.fdopen(descriptor,'w',encoding='utf-8') as stream:json.dump(value,stream);stream.flush();os.fsync(stream.fileno())
        os.replace(str(temporary),str(target))
    finally:
        if temporary.exists():temporary.unlink()


def sample():
    data=dict(runtime.counters(),**runtime.memory(),time=int(time.time()),python_threads=threading.active_count(),gc_generation_counts=list(gc.get_count()),pointer_bits=__import__('struct').calcsize('P')*8,pressure=runtime.pressure())
    try:
        with open('/proc/self/smaps_rollup') as stream:
            for line in stream:
                if line.startswith('Pss:'):data['pss_kib']=int(line.split()[1]);break
    except (OSError,ValueError):data['pss_kib']=None
    try:data['fd_count']=len(os.listdir('/proc/self/fd'))
    except OSError:data['fd_count']=None
    art=sys.modules.get('media_art')
    data['art_inbox']=len(getattr(art,'_inbox',{})) if art else None
    return data


def append(data):
    target=path('samples.jsonl')
    if target.exists() and target.stat().st_size>512*1024:os.replace(str(target),str(path('samples.previous.jsonl')))
    descriptor=os.open(str(target),os.O_WRONLY|os.O_APPEND|os.O_CREAT,0o600)
    with os.fdopen(descriptor,'a',encoding='utf-8') as stream:stream.write(json.dumps(data,sort_keys=True)+'\n')


def _run():
    import xbmc
    monitor=xbmc.Monitor()
    while not _stop.is_set() and not monitor.abortRequested():
        value=config()
        if not value or time.time()>=value.get('end',0):return
        try:append(dict(sample(),phase=value.get('phase') if value.get('phase') in PHASES else 'IDLE',elapsed_s=max(0,int(time.time()-value.get('start',time.time())))))
        except (OSError,MemoryError):runtime.note_pressure()
        if _stop.wait(60):return


def ensure():
    global _next,_worker
    if _stop.is_set() or time.monotonic()<_next:return
    _next=time.monotonic()+5
    value=config()
    if not value or time.time()>=value.get('end',0):return
    with _guard:
        if _worker is None or not _worker.is_alive():
            _worker=threading.Thread(target=_run,name='XCMate-stability',daemon=True);_worker.start()


def shutdown():
    _stop.set()
    if _worker is not None and _worker is not threading.current_thread():_worker.join(.05)


def show():
    import xbmcgui
    from localization import tr
    from capture_ui import work
    dialog=xbmcgui.Dialog();choice=dialog.select(tr(34800),[tr(n) for n in (34801,34802,34803,34804,34805)])
    if choice in (0,1):work(lambda:start(4 if choice==0 else 8));dialog.ok('XCMate',tr(34806))
    elif choice==2:
        phase=dialog.select(tr(34803),list(PHASES))
        if 0<=phase<len(PHASES):
            value=work(config)
            if value:value['phase']=PHASES[phase];work(lambda:save(value))
    elif choice==3:
        def report():
            text=json.dumps(sample(),indent=2)
            try:
                with path('samples.jsonl').open(encoding='utf-8') as stream:text+='\n'+stream.read(524289)[-65536:]
            except OSError:pass
            return text
        dialog.textviewer(tr(34800),work(report))
    elif choice==4:
        value=work(config)
        if value:value['end']=time.time();work(lambda:save(value))
