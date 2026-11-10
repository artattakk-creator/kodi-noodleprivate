"""Read-only storage pressure receipt; display is independent of the archive.

Only workers measure capacity. GUI readers use a bounded Home property. No
mode/limit changes, filesystem writes, new queue, grants or credentials.
"""
import json
import time
_due={}
PREFIX='XCMate.Display84.Pressure.'
CODES={'READY','RESERVE_BLOCKED','METADATA_RESERVE_BLOCKED','STORAGE_OFFLINE','CAPACITY_UNKNOWN'}
_seen={}


def _context():
    from epg_handoff63 import profile_scope
    return profile_scope()


def state():
    try:
        import xbmcgui
        context=_context()
        raw=xbmcgui.Window(10000).getProperty(PREFIX+context)
        value=json.loads(raw) if raw and len(raw)<2048 else {}
        if value.get('profile')==context and 0<=time.time()-value.get('at',0)<90 and value.get('code') in CODES:
            return value
    except (ImportError,ValueError,TypeError,AttributeError,RuntimeError):pass
    return {}


def enabled():
    return state().get('code') in CODES-{'READY'}


def observe(force=False):
    """Existing artwork worker only. No SQLite open or archive adoption."""
    context=_context();now=time.monotonic()
    if not force and now<_due.get(context,0):return enabled()
    _due[context]=now+5
    while len(_due)>8:_due.pop(next(iter(_due)))
    from art_storage import capacity,WRITE_HEADROOM
    from import_budget import RESERVE
    from utils import addon_data_dir
    code='CAPACITY_UNKNOWN';facts={}
    try:
        target=capacity();metadata=capacity(location=addon_data_dir())
        available=target.get('free');local=metadata.get('free')
        if target.get('storage_availability')=='STORAGE_OFFLINE':code='STORAGE_OFFLINE'
        elif isinstance(local,(int,float)) and local<RESERVE+65536:code='METADATA_RESERVE_BLOCKED'
        elif isinstance(available,(int,float)):
            code='RESERVE_BLOCKED' if available<target['reserve']+3*1024*1024+WRITE_HEADROOM else 'READY'
        facts={k:target[k] for k in ('free','total','reserve') if type(target.get(k)) is int}
    except OSError:pass
    import xbmcgui
    xbmcgui.Window(10000).setProperty(PREFIX+context,json.dumps(dict(profile=context,at=time.time(),code=code,**facts)))
    note('all',code)
    return code!='READY'


def note(kind,code,**counts):
    if kind not in ('live','vod','series','event','all'):return
    allowed=CODES|{'SOURCE_MISSING','SOURCE_BLOCKED','DNS_UNAVAILABLE','URL_APPROVED','METADATA_WRITE_DEFERRED','REFERENCE_HANDED','IMAGE_DECODED','RAM_ONLY','TEXTURE_VERIFIED','TEXTURE_FAILED'}
    if code not in allowed:return
    try:context=_context()
    except (ImportError,AttributeError,RuntimeError):return
    now=time.monotonic();key=(context,kind,code)
    if now-_seen.get(key,-1e9)<30:return
    _seen[key]=now
    while len(_seen)>128:_seen.pop(next(iter(_seen)))
    safe={k:v for k,v in counts.items() if k in ('count','sources','approved','local','handed','width','height') and type(v) is int and 0<=v<=100000}
    import xbmc
    try:xbmc.log('[XCMate][DISPLAY84] kind='+kind+' code='+code+' '+json.dumps(safe,separators=(',',':')),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass


def metadata_allowed():
    """Pure receipt check, not authorization to bypass ordinary write guards."""
    return not enabled()


def logo_proof(portal,row,uri):
    """A reference to the existing per-account/source DNS lease, not pixels."""
    from widget_assets69 import identity,read
    from artwork_visible import KODI_OPTIONS
    if not isinstance(uri,str) or not uri.endswith(KODI_OPTIONS):return ''
    source=uri[:-len(KODI_OPTIONS)]
    if read(portal,'live',[row]).get(str(row['sid']),{}).get('poster')!=uri:return ''
    return identity(portal,'live',row,'poster',source)


def logo_reference(props):
    """GUI-safe existing property lookup; current cached portal binds account."""
    if props.get('XCMate.LogoProof86'):return __import__('logo_manifest86').reference(props)
    from widget_assets69 import identity,read
    from artwork_visible import KODI_OPTIONS
    from portals import get_by_id
    uri=props.get('XCMate.ProgrammeLogo46','');tag=props.get('XCMate.LogoProof84','')
    if not uri.endswith(KODI_OPTIONS) or not tag:return ''
    source=uri[:-len(KODI_OPTIONS)];pid=props.get('XCMate.PortalId','');sid=props.get('XCMate.MediaId','')
    portal=get_by_id(str(pid))
    if not portal:return ''
    row=dict(sid=str(sid),cover=source,kind='live')
    if tag!=identity(portal,'live',row,'poster',source):return ''
    current=read(portal,'live',[row]).get(str(sid),{}).get('poster','')
    # A decoded exact-source Kodi file survives the short remote lease and
    # remains the fast offline logo until the correct event image is ready.
    if __import__('os').path.isabs(current):return current
    return uri if current==uri else ''
