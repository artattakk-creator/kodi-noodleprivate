"""Optional, one-time credential import from authenticated Google Drive or private GitHub.

This module carries no embedded file ID, repository path, bearer credential,
Drive refresh token, client secret, or TMDB token. The installer never stores
remote bearer credentials. It is explicitly NOT an automatic Drive login:
the user must first authorize the private file and supply an OAuth access
token with permission to read that file. Google TV device OAuth by itself
only permits drive.file/appdata, not arbitrary existing Drive files.
"""
import base64
import binascii
import http.client
import json
import re
import ssl
import threading
import time
from urllib.parse import quote

MAX_SOURCE_BYTES=4097
MAX_JSON_BYTES=16384
_PUBLIC=frozenset(('SKIPPED','PAIRED','AUTH_FAILED','SERVER_UNAVAILABLE'))
_busy=threading.Lock()

class ImportError528(ValueError):
    def __init__(self,code):
        self.code=code
        super().__init__(code)

def destination_available():
    """No overwrite of existing, invalid, legacy or opted-out credentials."""
    import xbmcaddon
    import tmdb_token61 as tokenlib
    addon=xbmcaddon.Addon('plugin.video.xtreammate')
    if addon.getSetting('programme_tmdb_optout77').lower()=='true':
        return False
    try:
        existing=tokenlib.read(tokenlib.location(),missing=True)
        return existing is None and not addon.getSetting('tmdb_read_token43').strip()
    except (tokenlib.TokenError,OSError):
        return False

def _bearer(value):
    if not isinstance(value,str) or not 10<=len(value)<=4096:
        raise ImportError528('AUTH_FAILED')
    if any(ord(c)<33 or ord(c)>126 for c in value):
        raise ImportError528('AUTH_FAILED')
    return value

def _locator(provider,locator):
    """Only fixed hosts and strictly bounded provider-owned path formats."""
    if not isinstance(locator,str) or len(locator)>480 or any(ord(c)<33 for c in locator):
        raise ImportError528('SOURCE_INVALID')
    if provider=='drive':
        if not re.fullmatch(r'[A-Za-z0-9_-]{15,160}',locator):
            raise ImportError528('SOURCE_INVALID')
        return 'www.googleapis.com','/drive/v3/files/'+quote(locator,safe='')+'?alt=media'
    if provider=='github':
        parts=locator.split('/')
        if not 3<=len(parts)<=12 or not all(re.fullmatch(r'[A-Za-z0-9._-]{1,100}',p) and p not in ('.','..') for p in parts):
            raise ImportError528('SOURCE_INVALID')
        if not parts[-1].lower().endswith('.txt'):
            raise ImportError528('SOURCE_INVALID')
        owner,repo=parts[:2]
        return ('api.github.com','/repos/'+quote(owner,safe='')+'/'+quote(repo,safe='')+
                '/contents/'+'/'.join(quote(p,safe='') for p in parts[2:])+'?ref=main')
    raise ImportError528('SOURCE_INVALID')

def _https(host,path,bearer,limit,cancel):
    """No redirects, no arbitrary hosts/IPs, size bounded before JSON parsing."""
    if host not in ('www.googleapis.com','api.github.com') or cancel():
        raise ImportError528('USER_CANCELLED' if cancel() else 'SOURCE_INVALID')
    conn=http.client.HTTPSConnection(host,443,timeout=6,context=ssl.create_default_context())
    headers={'Authorization':'Bearer '+_bearer(bearer),
             'Accept': 'application/vnd.github+json' if host=='api.github.com' else 'application/octet-stream',
             'Accept-Encoding':'identity','Cache-Control':'no-store',
             'User-Agent':'GS-Media-Setup-Cloud-Token-Import/0.5.28'}
    try:
        conn.request('GET',path,headers=headers)
        response=conn.getresponse()
        if response.status in (401,403,404):
            raise ImportError528('AUTH_FAILED')
        if response.status!=200:  # Never follow redirects to an untrusted origin.
            raise ImportError528('SOURCE_UNAVAILABLE')
        if response.getheader('Content-Encoding','identity')!='identity':
            raise ImportError528('SOURCE_INVALID')
        declared=response.getheader('Content-Length','')
        if declared and (not declared.isdigit() or int(declared)>limit):
            raise ImportError528('SOURCE_TOO_LARGE')
        kind=(response.getheader('Content-Type','') or '').lower().split(';')[0].strip()
        if kind=='text/html':
            raise ImportError528('SOURCE_INVALID')
        parts=[];size=0
        while True:
            if cancel():raise ImportError528('USER_CANCELLED')
            chunk=response.read(min(2048,limit-size+1))
            if not chunk:break
            size+=len(chunk)
            if size>limit:raise ImportError528('SOURCE_TOO_LARGE')
            parts.append(chunk)
        return b''.join(parts)
    except ImportError528:raise
    except (OSError,TimeoutError,ssl.SSLError,http.client.HTTPException):
        raise ImportError528('SOURCE_UNAVAILABLE') from None
    finally:conn.close()

def download(provider,locator,bearer,cancel=lambda:False):
    host,path=_locator(provider,locator)
    response=_https(host,path,bearer,MAX_JSON_BYTES if provider=='github' else MAX_SOURCE_BYTES,cancel)
    if provider=='github':
        try:
            data=json.loads(response)
            if (not isinstance(data,dict) or data.get('encoding')!='base64'
                or not isinstance(data.get('content'),str) or
                not isinstance(data.get('size'),int) or not 1<=data['size']<=MAX_SOURCE_BYTES):
                raise ValueError()
            raw=base64.b64decode(data['content'],validate=False)
            if len(raw)!=data['size'] or len(raw)>MAX_SOURCE_BYTES:raise ValueError()
            return raw
        except (ValueError,UnicodeError,KeyError,TypeError,binascii.Error):
            raise ImportError528('SOURCE_INVALID') from None
    return response

def perform(provider,locator,bearer,cancel=lambda:False):
    """Only XCMate's own atomic private writer may store the verified token."""
    import tmdb_token61 as tokens
    if cancel():return 'USER_CANCELLED'
    if not destination_available():return 'SKIPPED'
    raw=download(provider,locator,bearer,cancel)
    try:value=tokens.validate(raw)
    except tokens.TokenError:return 'TOKEN_INVALID'
    if cancel():return 'USER_CANCELLED'
    from media_sources43 import TMDB,SourceError
    from tmdb_connection60 import request
    try:
        response=request(TMDB+'/configuration',token=value,cancel=cancel)
        images=response.get('images') if isinstance(response,dict) else None
        if (not isinstance(images,dict) or
            images.get('secure_base_url')!='https://image.tmdb.org/t/p/' or
            not images.get('backdrop_sizes')):
            return 'TOKEN_INVALID'
    except SourceError as error:
        return 'AUTH_FAILED' if error.code in ('HTTP_AUTH','INVALID_TOKEN') else 'SOURCE_UNAVAILABLE'
    if cancel():return 'USER_CANCELLED'
    if not destination_available():return 'SKIPPED'
    try:
        result=tokens.import_bytes((value+'\n').encode(),None,target=tokens.location())
        return 'PAIRED' if result in ('IMPORTED','IMPORTED_SYNC_WARNING') else 'WRITE_FAILED'
    except (tokens.TokenError,OSError):
        return 'WRITE_FAILED'

def _work(provider,locator,bearer,progress):
    """All network work runs off the Kodi GUI thread. Only result codes escape."""
    import xbmc
    if not _busy.acquire(False):return 'WORKER_BUSY'
    stop=threading.Event();finished=threading.Event();box={}
    def worker():
        try:box['code']=perform(provider,locator,bearer,stop.is_set)
        except ImportError528 as exc:box['code']=exc.code
        except Exception:box['code']='SOURCE_UNAVAILABLE'
        finally:_busy.release();finished.set()
    try:threading.Thread(target=worker,name='GS-TMDB-Import528',daemon=True).start()
    except (RuntimeError,MemoryError):
        _busy.release();return 'WORKER_BUSY'
    monitor=xbmc.Monitor();deadline=time.monotonic()+20
    while not finished.wait(.05):
        if progress.iscanceled() or monitor.abortRequested() or time.monotonic()>deadline:
            stop.set()
            return 'USER_CANCELLED' if progress.iscanceled() else 'SOURCE_UNAVAILABLE'
    return box.get('code','SOURCE_UNAVAILABLE')

def offer(profile=None,manual=False):
    """Optional, explicit, owner-thread source choice. No token in setup logs."""
    import xbmcaddon,xbmcgui
    if not destination_available():return 'SKIPPED'
    addon=xbmcaddon.Addon('plugin.video.xtreammate')
    dlg=xbmcgui.Dialog()
    if not manual and not dlg.yesno('TMDB-Token importieren',
            'Optional: TMDB-Token jetzt aus einer privaten Quelle importieren? '
            'Ohne Freigabe überspringen und später fortsetzen.',
            defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):
        return 'SKIPPED'
    choices=['Privates GitHub-Repository (einmaliger Lesezugang)',
             'Google Drive (bereits autorisierter OAuth-Zugriff)',
             'Joomla-API (vorbereitet – Backend/Freigabe fehlt)',
             'Geschütztes Webverzeichnis (vorbereitet – Authentifizierung fehlt)',
             'Abbrechen / später importieren']
    selected=dlg.select('TMDB-Token importieren',choices)
    if selected in (2,3):
        dlg.ok('TMDB-Token · Quelle vorbereitet',
               'Diese Quelle wird erst aktiv, sobald eine geschützte HTTPS-API '
               'und eine individuelle Zugriffsfreigabe eingerichtet und '
               'getestet sind. Kein öffentlicher TMDB-Token-Link. '
               'Bitte vorerst GitHub/Drive mit privater Berechtigung nutzen.')
        return 'SKIPPED'
    if selected not in (0,1):return 'SKIPPED'
    provider='github' if selected==0 else 'drive'
    if provider=='github':
        locator=dlg.input('GitHub: Eigentümer/Repository/Pfad/Token.txt',
                          type=getattr(xbmcgui,'INPUT_ALPHANUM',0))
        prompt='GitHub Lesetoken (nur einmal, wird NICHT gespeichert)'
    else:
        locator=dlg.input('Google Drive: Datei-ID (privates Konto)',
                          type=getattr(xbmcgui,'INPUT_ALPHANUM',0))
        prompt='Google OAuth Zugriffstoken (bereits autorisiert, einmalig)'
    if not locator:return 'SKIPPED'
    bearer=dlg.input(prompt,type=getattr(xbmcgui,'INPUT_ALPHANUM',0),
              option=getattr(xbmcgui,'ALPHANUM_HIDE_INPUT',1))
    if not bearer:return 'SKIPPED'
    progress=xbmcgui.DialogProgress()
    try:
        progress.create('Importiere TMDB-Token',
                        'Prüfe privaten Zugriff, TMDB-Berechtigung und sichere lokale Ablage …')
        code=_work(provider,locator,bearer,progress)
    finally:
        progress.close()
        # Never save locator or remote bearer in addon settings, properties,
        # Kodi's setup state or diagnostic logs.
        bearer=''
    if code=='PAIRED':
        try:
            from tmdb_access61 import activate
            activate(addon,automatic=True)
        except Exception:pass # Valid private file remains installed.
        dlg.ok('TMDB-Token','TMDB-Verbindung geprüft. Token sicher lokal importiert.')
        return 'PAIRED'
    if code=='SKIPPED':return 'SKIPPED'
    message={
       'AUTH_FAILED':'Kein Zugriff auf die private Datei. Bitte Berechtigung prüfen.',
       'TOKEN_INVALID':'Die geladene Datei enthält keinen gültigen TMDB Read Access Token.',
       'SOURCE_INVALID':'Datei-ID/Repository-Pfad oder Dateiantwort ungültig.',
       'SOURCE_TOO_LARGE':'Die Quelldatei ist zu groß.',
       'WRITE_FAILED':'Der sichere lokale Token-Speicher ist momentan nicht schreibbar.',
       'USER_CANCELLED':'Der Import wurde abgebrochen.',
       'WORKER_BUSY':'Ein weiterer Import läuft bereits.',
       'SOURCE_UNAVAILABLE':'Quelle momentan nicht erreichbar. Installation bleibt erhalten.'
    }.get(code,'Quelle momentan nicht erreichbar.')
    dlg.ok('TMDB-Token',message)
    return 'AUTH_FAILED' if code in ('AUTH_FAILED','TOKEN_INVALID','SOURCE_INVALID') else 'SERVER_UNAVAILABLE'
