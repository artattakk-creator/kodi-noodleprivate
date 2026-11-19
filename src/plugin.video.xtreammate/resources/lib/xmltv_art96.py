"""Existing local facts only: source/channel/event/revision-bound XMLTV choices.

No XMLTV download/parse, no source settings mutations and no GUI SQL calls.
Search runs in the existing manual-work service lane.
"""
import hashlib,json,sqlite3,time
from media_sources43 import SourceError

def identity(event):
 return [str(event.get(k,'')) for k in ('pid','sid','canonical','start','stop')]+[__import__('programme_store46').title_hash(event.get('title',''))]
def key(event):
 from epg_handoff63 import profile_scope
 from programme_display84 import _account
 return hashlib.sha256(json.dumps([profile_scope(),_account(event.get('pid')),'xmltv-event96',identity(event),event.get('source_key46'),event.get('epg_source46')],sort_keys=True).encode()).hexdigest()
def valid_proof(proof):
 return isinstance(proof,dict) and set(proof)=={'event','source','channel','revision'} and isinstance(proof['event'],list) and len(proof['event'])==6 and all(isinstance(v,str) for v in proof['event']) and all(isinstance(proof[k],str) and 0<len(proof[k])<=512 for k in ('source','channel','revision'))
def search(event,cancel=lambda:False):
 from artwork_sources96 import enabled
 if not enabled('xmltv'):raise SourceError('SOURCE_DISABLED')
 if not event.get('canonical') or not event.get('pid') or not event.get('sid'):return dict(code='ZERO_RESULTS',rows=[],more=False)
 from programme_index46 import connect
 from programme_store46 import title_hash
 from programme_urls55 import safe,OPTIONS
 from portals import get_by_id
 from epg_binding48 import sources
 portal=get_by_id(str(event['pid']))
 allowed={s['id'] for s in sources(portal)} if portal else set()
 db=None;rows=[]
 try:
  db=connect(False)
  if db is None:return dict(code='ZERO_RESULTS',rows=[],more=False)
  until=time.monotonic()+.3;db.set_progress_handler(lambda:int(cancel() or time.monotonic()>until),500)
  records=db.execute('SELECT source_id,fingerprint,data FROM facts WHERE pid=? AND cid=? AND start=? AND stop=? AND titlehash=? ORDER BY source_id LIMIT 32',(str(event['pid']),str(event['canonical']),int(event['start']),int(event['stop']),title_hash(event['title']))).fetchall()
  for source,revision,raw in records:
   if cancel():raise SourceError('CANCELLED')
   if source not in allowed or len(raw)>16384:continue
   fact=json.loads(raw);url=fact.get('xmltv_image')
   if not url or not safe(url) or fact.get('epg_source46')!=source:continue
   proof=dict(event=identity(event),source=source,channel=str(event['canonical']),revision=revision)
   ident=int(hashlib.sha256(json.dumps(proof,sort_keys=True).encode()).hexdigest()[:13],16)+1
   rows.append(dict(id=ident,source='xmltv_event',title=event['title'],year=int(fact.get('year') or 0),country=[],overview=str(fact.get('description') or fact.get('descr') or '')[:1000],media_type86='event',url=url,thumb86=url+OPTIONS,poster='',role='backdrop',verified85=True,xmltv96=proof,attribution='XMLTV – konfigurierte Eventquelle',match='EXACT_EVENT'))
  return dict(code='READY' if rows else 'ZERO_RESULTS',rows=rows,more=False)
 except sqlite3.Error as exc:
  raise SourceError('SQLITE_BUSY' if (getattr(exc,'sqlite_errorcode',0)&255) in (5,6) else 'EPG_READ_BUDGET') from None
 finally:
  if db is not None:db.close()

def details(event,selected,cancel=lambda:False):
 proof=selected.get('xmltv96')
 if not valid_proof(proof) or proof['event']!=identity(event):raise SourceError('EPG_REVISION_CHANGED')
 for row in search(event,cancel)['rows']:
  if row['id']==selected.get('id') and row['xmltv96']==proof:return row
 raise SourceError('EPG_REVISION_CHANGED')

def mapped(event,record,cancel=lambda:False):
 """Independently revalidate the source fact; caller URLs are never trusted."""
 if not record or record.get('source')!='xmltv_event':return None
 try:return dict(details(event,record,cancel),manual85=True)
 except SourceError:return None

_checked={}
def proof_key(proof):return hashlib.sha256(json.dumps(proof,sort_keys=True).encode()).hexdigest()
def invalidate(proof):
 if valid_proof(proof):__import__('xbmcgui').Window(10000).setProperty('XCMate.XMLTV96.Invalid.'+proof_key(proof),'true')
def display_allowed(art,event=None):
 if 'xmltv96' not in art:return True # Legacy automatic XMLTV references.
 proof=art.get('xmltv96')
 return valid_proof(proof) and (event is None or proof['event']==identity(event)) and __import__('xbmcgui').Window(10000).getProperty('XCMate.XMLTV96.Invalid.'+proof_key(proof))!='true'
def checked_mapping(event,record,cancel=lambda:False):
 """Worker-only, fact-file-generation cached revalidation, no GUI SQL."""
 from programme_index46 import path
 import os
 stamps=[]
 for filename in (path(),path()+'-wal'):
  try:
   s=os.stat(filename);stamps.append((s.st_dev,s.st_ino,s.st_mtime_ns,s.st_size))
  except FileNotFoundError:stamps.append(None)
 tag=(key(event),proof_key(record.get('xmltv96')),tuple(stamps))
 if tag in _checked:return _checked[tag]
 try:value=dict(details(event,record,cancel),manual85=True)
 except SourceError as exc:
  if exc.code in ('SQLITE_BUSY','EPG_READ_BUDGET','CANCELLED'):raise
  invalidate(record.get('xmltv96'));value=None
 _checked[tag]=value
 while len(_checked)>64:_checked.pop(next(iter(_checked)))
 return value
