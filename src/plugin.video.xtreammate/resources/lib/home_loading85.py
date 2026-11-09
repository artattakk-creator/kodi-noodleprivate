"""Visible honest per-row loading status, driven by actual existing worker work."""
import hashlib,json,time
KEY='XCMate.Home85.'
_records={}
TEXT={'LOADING_CATALOG':{'vod':'Filme werden geladen …','series':'Serien werden geladen …'},'LOADING_ART':'Cover werden geladen …','READY_PARTIAL':'Weitere Cover werden nachgeladen …','READY':'','EMPTY':{'vod':'Keine Filme in dieser Auswahl','series':'Keine Serien in dieser Auswahl'},'ERROR_RETRYABLE':'Katalog/Bilder momentan nicht erreichbar · Erneut versuchen'}
def update(portal,kind,rows,code,images=0,pending=False):
 if kind not in ('vod','series'):return
 from epg_handoff63 import identity
 import xbmcgui
 now=time.monotonic();key=identity(portal['id'],kind);prior=_records.get(key,{})
 material=hashlib.sha256(json.dumps([[r.get('sid'),r.get('cover'),r.get('name')] for r in rows[:24]],sort_keys=True).encode()).hexdigest()
 since=prior.get('since',now) if prior.get('generation')==material else now
 count=len(rows);wanted=min(12,count);busy=bool(pending and now-since<60)
 if not count:state='EMPTY' if code in ('READY','CACHE','READ_ONLY') else 'LOADING_CATALOG' if busy else 'ERROR_RETRYABLE'
 elif images>=wanted:state='READY'
 elif images:state='READY_PARTIAL'
 else:state='LOADING_ART' if busy else 'ERROR_RETRYABLE'
 record=dict(generation=material,since=since,state=state,count=count,images=images,busy=busy and state in ('LOADING_CATALOG','LOADING_ART','READY_PARTIAL'))
 _records[key]=record
 while len(_records)>16:_records.pop(next(iter(_records)))
 text=TEXT[state];text=text.get(kind,'') if isinstance(text,dict) else text
 window=xbmcgui.Window(10000)
 window.setProperty(KEY+kind+'.Text',text);window.setProperty(KEY+kind+'.State',state);window.setProperty(KEY+kind+'.Busy','true' if record['busy'] else '')
 return record

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
