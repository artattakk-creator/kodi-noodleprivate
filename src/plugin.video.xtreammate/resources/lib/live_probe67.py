"""Explicit selected-source GET probe; 1 KiB, 3 seconds, no redirects/retries."""
import hashlib,json,threading,time,urllib.request,urllib.error
_gate=threading.Lock()
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None
def probe(url,headers=None,opener=None):
 from urllib.parse import urlsplit
 try:p=urlsplit(url.partition('|')[0])
 except ValueError:return dict(code='UNSAFE_SOURCE',status=0,mime='OTHER')
 if p.scheme not in ('http','https') or not p.hostname or p.username or p.password or p.fragment:return dict(code='UNSAFE_SOURCE',status=0,mime='OTHER')
 headers=dict(headers or {})
 if any(not isinstance(k,str) or not isinstance(v,str) or any(x in k+v for x in ('\r','\n')) for k,v in headers.items()):return dict(code='UNSAFE_HEADER',status=0,mime='OTHER')
 headers.update(Range='bytes=0-1023',**{'Accept-Encoding':'identity'})
 response=None
 try:
  request=urllib.request.Request(url.partition('|')[0],headers=headers,method='GET')
  response=(opener or urllib.request.build_opener(NoRedirect(),urllib.request.ProxyHandler({}))).open(request,timeout=3)
  raw=response.read(1024);body=raw.lstrip()
  detected='HLS' if body.startswith(b'#EXTM3U') else 'MPEG_TS' if len(raw)>376 and raw[0]==raw[188]==raw[376]==71 else 'HTML' if body[:15].lower().startswith((b'<!doctype html',b'<html')) else 'JSON' if body.startswith((b'{',b'[')) else 'UNKNOWN'
  mime={'video/mp2t':'MPEG_TS','application/vnd.apple.mpegurl':'HLS','application/x-mpegurl':'HLS','application/dash+xml':'DASH','text/html':'HTML','application/json':'JSON','application/octet-stream':'OCTET'}.get(str(response.headers.get('Content-Type','')).partition(';')[0].lower(),'OTHER')
  return dict(code='STREAM_PREFIX' if detected in ('HLS','MPEG_TS') else 'NOT_A_STREAM' if detected in ('HTML','JSON') else 'UNCONFIRMED_FORMAT',status=response.status,mime=mime,detected=detected,bytes=len(raw))
 except urllib.error.HTTPError as e:
  status=e.code if type(e.code) is int and 100<=e.code<=599 else 0
  e.close();return dict(code='HTTP_'+str(status),status=status,mime='OTHER')
 except TimeoutError:return dict(code='TIMEOUT',status=0,mime='OTHER')
 except Exception:return dict(code='NETWORK_ERROR',status=0,mime='OTHER')
 finally:
  if response:response.close()
def launch(router):
 import xbmc,xbmcgui
 from portals import get_by_id
 from library_index import Reader
 from source_adapters import for_portal
 from player import _build_header_string
 from urllib.parse import parse_qsl
 portal=get_by_id(router._params.get('pid',''))
 if not portal or not portal.get('enabled',True):return
 rows,_=Reader(portal['id']).page('live',category=portal.get('start_group_id') or None,limit=200)
 from menu_icons45 import select
 i=select(xbmcgui.Dialog(),'Live-Stream prüfen – kein Wiedergabestart',[r['name'] for r in rows],default='live')
 if not isinstance(i,int) or not 0<=i<len(rows) or not _gate.acquire(blocking=False):return
 result=[];progress=xbmcgui.DialogProgress()
 def work():
  try:
   uri,extra=for_portal(portal).play_uri('live',rows[i]['sid']);base,encoded=_build_header_string(uri,extra)
   value=probe(base,dict(parse_qsl(encoded)))
   identity=hashlib.sha256((str(portal['id'])+'|'+rows[i]['sid']).encode()).hexdigest()[:12]
   xbmc.log('[XCMate][LIVE67] request=EXPLICIT_GET channel='+identity+' '+json.dumps(value,sort_keys=True),xbmc.LOGINFO);result.append(value)
  except Exception:result.append(dict(code='SOURCE_UNAVAILABLE',status=0,mime='OTHER'))
  finally:_gate.release()
 try:
  progress.create('XCMate Live-Diagnose','Ein begrenzter GET; keine Zugangsdaten in der Ausgabe.')
  threading.Thread(target=work,name='XCMate-live-probe67',daemon=True).start()
  deadline=time.monotonic()+5;monitor=xbmc.Monitor()
  while not result and time.monotonic()<deadline:
   if progress.iscanceled() or monitor.waitForAbort(.05):return
 finally:progress.close()
 value=result[0] if result else dict(code='TIMEOUT',status=0,mime='OTHER')
 xbmcgui.Dialog().ok('XCMate – Live-Diagnose','HTTP '+str(value['status'])+' · '+value['code']+' · '+value['mime']+'\nPräfixtest ist kein vollständiger Playback-Nachweis. Redirects werden nur gemeldet. Keine Weitergabe von Zugangsdaten an andere Hosts.')
