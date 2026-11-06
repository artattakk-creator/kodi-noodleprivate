"""Explicit connection/opt-in diagnostic; no token, host or path in output."""
from localization import tr

def check(cancel=lambda:False):
    from programme_outcomes70 import settings
    from programme_consent77 import ensure
    migration77=ensure(force=True)
    gates=settings();result=dict(gates=gates,migration77=migration77)
    from tmdb_connection60 import test_connection
    result['tmdb']=test_connection(cancel)
    if not gates['tvmaze']:result['tvmaze']='DISABLED'
    elif cancel():result['tvmaze']='CANCELLED'
    else:
        from media_sources43 import get,SourceError
        try:
            value=get('https://api.tvmaze.com/shows/1',api=True,cancel=cancel)
            result['tvmaze']='TVMAZE_OK' if value.get('id')==1 else 'INVALID_RESPONSE'
        except SourceError as error:result['tvmaze']=error.code
    result['image']=active_image(cancel)
    from widget_skin77 import inspect as skin77
    result['skin77']=skin77()
    import xbmcgui,json
    try:result['render77']=json.loads(xbmcgui.Window(10000).getProperty('XCMate.Home77.Render') or '{}')
    except (ValueError,TypeError):result['render77']={}
    from kodi_schema75 import inspect
    result['kodi_library']=inspect()
    return result

def active_image(cancel=lambda:False):
    # Explicit diagnostic, worker only. Existing active/start channel and the
    # common exact-event resolver; no new token, forced consent or global scan.
    from portals import get_active
    from library_index import Reader
    from programme_events46 import load
    from programme_urls55 import resolve
    from programme_image69 import eligible
    for portal in get_active()[:4]:
        if cancel():return 'CANCELLED'
        reader=Reader(portal['id'],timeout=.03,query_seconds=.1)
        row=reader.get('live',str(portal.get('start_stream_id') or ''))
        if not row:continue
        event=load(portal,row)
        if event.get('code') not in ('LOCAL_EVENT','CACHED_EVENT'):return 'NO_ACTIVE_EVENT'
        art=resolve(event,allow_lookup=True,cancel=cancel,url_mode69=True)
        if eligible(art,event):
            from programme_pipeline77 import texture
            return 'IMAGE_REFERENCE_VERIFIED / '+texture(event,art)['code']
        return str(art.get('code','NO_CONFIRMED_IMAGE'))
    return 'NO_ACTIVE_CHANNEL'

def show():
    import xbmcgui,xbmc,threading,time
    progress=xbmcgui.DialogProgress();progress.create(tr(38100),tr(38101))
    values=[];cancelled=threading.Event()
    def worker():
        try:values.append(check(cancelled.is_set))
        except Exception:values.append(dict(tmdb='UNAVAILABLE',tvmaze='UNAVAILABLE',gates={}))
    threading.Thread(target=worker,name='XCMate-picture-test74',daemon=True).start()
    started=time.monotonic();monitor=xbmc.Monitor()
    try:
        while not values and time.monotonic()-started<30:
            if progress.iscanceled() or monitor.waitForAbort(.05):cancelled.set();return
    finally:progress.close();cancelled.set()
    result=values[0] if values else dict(tmdb='TIMEOUT',tvmaze='TIMEOUT',gates={})
    gates=result['gates']
    text='TMDB: '+result['tmdb']+'\nTVMaze: '+result['tvmaze']+'\n'+tr(38106,result.get('image','NOT_TESTED'))+'\n\n'
    text+=tr(38102,tr(38103 if gates.get('own') else 38104),tr(38103 if gates.get('tvmaze') else 38104))
    text+='\n'+tr(38105)
    library=result.get('kodi_library',{})
    if library:text+='\n\nKodi library (read-only): '+library.get('code','NOT_TESTED')
    from programme_settings68 import state
    gates75=state()
    text+='\nSOURCE_FACTS → ARTWORK_OPT_IN → TOKEN → MATCH → FETCH → CACHE → WIDGET_RENDER'
    text+='\nMigration: '+result.get('migration77','NOT_TESTED')
    text+='\nHome: '+result.get('skin77',{}).get('code','NOT_TESTED')+' / '+result.get('render77',{}).get('code','NOT_TESTED')
    if result.get('skin77',{}).get('code')=='ADAPTER_APPROVAL_REQUIRED':text+='\nHome-Adapter: Einstellungen → Aussehen → Widgets → BINGIE-Integration; Vorschau und Sicherung vor Aktivierung.'
    text+='\nBildreferenz / Texturecache / tatsächlich sichtbares Android-Bild sind getrennte Nachweise.'
    if library.get('missing'):text+='\nKodi-Views fehlen: '+', '.join(library['missing'])+'. Keine automatische Reparatur oder Löschung.'
    xbmcgui.Dialog().ok(tr(38100),text)
