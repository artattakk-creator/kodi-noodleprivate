"""Visible honest per-row loading status, driven by actual existing worker work."""
import hashlib,json,math,threading,time
KEY='XCMate.Home85.'
_records={}
_lock=threading.RLock()
TEXT={'LOADING_CATALOG':{'vod':'Filme werden geladen …','series':'Serien werden geladen …'},'LOADING_ART':'Cover werden geladen …','READY_PARTIAL':'Weitere Cover werden nachgeladen …','READY':'','EMPTY':{'vod':'Keine Filme in dieser Auswahl','series':'Keine Serien in dieser Auswahl'},'ERROR_RETRYABLE':'Katalog/Bilder momentan nicht erreichbar · Erneut versuchen'}
def update(portal,kind,rows,code,images=0,pending=False):
 if kind not in ('vod','series'):return
 from epg_handoff63 import identity
 import xbmcgui
 now=time.monotonic();key=identity(portal['id'],kind);prior=_records.get(key,{})
 material=hashlib.sha256(json.dumps([[r.get('sid'),r.get('cover'),r.get('name'),r.get('_no_art86',False)] for r in rows[:24]],sort_keys=True).encode()).hexdigest()
 since=prior.get('since',now) if prior.get('generation')==material else now
 count=len(rows);wanted=sum(not r.get('_no_art86') for r in visible(portal,kind,rows));busy=bool(pending and now-since<60)
 if not count:state='EMPTY' if code in ('READY','CACHE','READ_ONLY') else 'LOADING_CATALOG' if busy else 'ERROR_RETRYABLE'
 elif images>=wanted:state='READY'
 elif images:state='READY_PARTIAL'
 else:state='LOADING_ART' if busy else 'ERROR_RETRYABLE'
 record=dict(generation=material,since=since,state=state,count=count,images=images,busy=busy and state in ('LOADING_CATALOG','LOADING_ART','READY_PARTIAL'))
 with _lock:
  _records[key]=record
  while len(_records)>16:_records.pop(next(iter(_records)))
  text=TEXT[state];text=text.get(kind,'') if isinstance(text,dict) else text
  window=xbmcgui.Window(10000)
  window.setProperty(KEY+kind+'.Deadline',str(since+60))
  window.setProperty(KEY+kind+'.Kind',kind)
  window.setProperty(KEY+kind+'.Text',text);window.setProperty(KEY+kind+'.State',state);window.setProperty(KEY+kind+'.Busy','true' if record['busy'] else '')
 return record

def expire():
 """RAM/native-only deadline, even when the data worker pauses or restarts."""
 import xbmcgui
 now=time.monotonic();window=xbmcgui.Window(10000)
 with _lock:
  for kind in ('vod','series'):
   prefix=KEY+kind+'.'
   if window.getProperty(prefix+'Busy')!='true':continue
   try:deadline=float(window.getProperty(prefix+'Deadline'))
   except (ValueError,TypeError):deadline=0
   if math.isfinite(deadline) and 0<deadline-now<=60:continue
   window.setProperty(prefix+'Busy','')
   if window.getProperty(prefix+'State') in ('LOADING_CATALOG','LOADING_ART','READY_PARTIAL'):
    window.setProperty(prefix+'State','ERROR_RETRYABLE')
    window.setProperty(prefix+'Text',TEXT['ERROR_RETRYABLE'])


def visible(portal,kind,rows):
 from home_schedule75 import focus
 value=focus()
 if value.get('kind')!=kind:
  try:
   from home_schedule75 import FOCUS
   from epg_handoff63 import profile_scope
   import xbmcgui
   raw=xbmcgui.Window(10000).getProperty(FOCUS+'.viewport85.'+kind)
   value=json.loads(raw) if raw and len(raw)<4096 else {}
   if value.get('profile')!=profile_scope() or not 0<=time.monotonic()-value.get('at',0)<3600:value={}
  except (ValueError,TypeError):value={}
 left=value.get('left',0) if value.get('kind')==kind and value.get('pid')==str(portal['id']) else 0
 try:left=max(0,min(int(left),max(0,len(rows)-1)))
 except (ValueError,TypeError):left=0
 return rows[left:left+12]
