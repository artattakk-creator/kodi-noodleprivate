"""Explicit user work mappings; private bounded atomic journal, no EPG writes.

Only the manager/worker reads files. UI policy checks read a Home property.
"""
import hashlib,json,os,tempfile,time
from pathlib import Path
MAX_BYTES=512*1024;MAX_RECORDS=256
PREFIX='XCMate.ManualWork85.'

def name(value):
 from epg_events import title_key
 import re
 text=str(value or '')
 if re.fullmatch(r'\s*M[.*\s]*A[.*\s]*S[.*\s]*H[.*\s]*',text,re.I):return 'mash'
 return title_key(text)
def namespace(event):
 from epg_handoff63 import profile_scope
 from programme_display84 import _account
 # Broadcast timestamp/revision/subtitle are deliberately not work identity.
 facts=[source_scope(event),profile_scope(),_account(event.get('pid')),str(event.get('pid')),str(event.get('sid')),event.get('canonical'),event.get('source_key46'),event.get('epg_source46'),name(event.get('title')),event.get('year'),event.get('country'),event.get('work_id'),event.get('external_ids'),any(v in str(event.get('genre','')).casefold() for v in ('film','movie'))]
 if event.get('media_kind86'):facts+=['media86',event['media_kind86']]
 return hashlib.sha256(json.dumps(facts,sort_keys=True).encode()).hexdigest()
def path():
 from utils import addon_data_dir
 return Path(os.path.realpath(addon_data_dir()))/'programme_manual85.json'
def window():
 import xbmcgui
 return xbmcgui.Window(10000)
def policy():return window().getProperty(PREFIX+'Epoch')
def read():
 filename=path()
 if filename.is_symlink():raise OSError('MANUAL_UNSAFE_FILE')
 if not filename.exists():return dict(format=1,records={},epochs={})
 if filename.stat().st_size>MAX_BYTES:raise OSError('MANUAL_LIMIT')
 data=json.loads(filename.read_bytes())
 if data.get('format')!=1 or not isinstance(data.get('records'),dict) or len(data['records'])>MAX_RECORDS or not isinstance(data.get('epochs',{}),dict) or len(data.get('epochs',{}))>MAX_RECORDS:raise ValueError('MANUAL_SCHEMA')
 for key,record in data['records'].items():
  if not __import__('re').fullmatch('[a-f0-9]{64}',str(key)) or not isinstance(record,dict) or type(record.get('hidden')) is not bool:raise ValueError('MANUAL_SCHEMA')
  if not record['hidden'] and (record.get('source') not in ('tmdb','tvmaze','user_local86') or type(record.get('id')) is not int or record['id']<=0):raise ValueError('MANUAL_SCHEMA')
 if any(not __import__('re').fullmatch('[a-f0-9]{64}',str(k)) or type(v) is not int or not 0<=v<=10**9 for k,v in data.get('epochs',{}).items()):raise ValueError('MANUAL_SCHEMA')
 return data
def publish(data):
 from epg_handoff63 import profile_scope
 safe=json.dumps(data,separators=(',',':'),sort_keys=True)
 window().setProperty(PREFIX+'Records',safe);window().setProperty(PREFIX+'Profile',profile_scope());window().setProperty(PREFIX+'Epoch',hashlib.sha256(safe.encode()).hexdigest())
_loaded={}
def _reload85():
 try:
  filename=path();stat=filename.stat() if filename.exists() else None;stamp=(stat.st_ino,stat.st_size,stat.st_mtime_ns) if stat else None
  from epg_handoff63 import profile_scope
  if _loaded.get(str(filename),object())==stamp and window().getProperty(PREFIX+'Profile')==profile_scope():return True
  publish(read());_loaded[str(filename)]=stamp
  while len(_loaded)>8:_loaded.pop(next(iter(_loaded)))
  return True
 except (OSError,ValueError,TypeError):return False
def current(event):
 from epg_handoff63 import profile_scope
 if window().getProperty(PREFIX+'Profile')!=profile_scope():return None
 raw=window().getProperty(PREFIX+'Records')
 try:
  if not raw or len(raw.encode())>MAX_BYTES:return None
  records=parsed85(raw).get('records',{})
  if not records:return None
  record=records.get(namespace(event))
  return dict(record) if isinstance(record,dict) else None
 except (ValueError,TypeError):return None
def set_mapping(event,candidate=None,hidden=False,automatic=False,cancel=lambda:False):
 from import_budget import check_space
 from profile_transaction import writing
 key=namespace(event);filename=path()
 with writing(timeout=.2):
  if cancel():raise __import__('media_sources43').SourceError('CANCELLED')
  data=read()
  epochs=data.setdefault('epochs',{})
  epochs[key]=int(epochs.get(key,0))+1
  if len(epochs)>MAX_RECORDS:raise OSError('MANUAL_LIMIT')
  if automatic:data['records'].pop(key,None)
  else:
   if not hidden and (not isinstance(candidate,dict) or candidate.get('source') not in ('tmdb','tvmaze','user_local86') or type(candidate.get('id')) is not int or candidate['id']<=0 or not candidate.get('verified85')):raise ValueError('MANUAL_UNVERIFIED')
   data['records'][key]=dict(hidden=bool(hidden),source=candidate.get('source') if candidate else '',id=candidate.get('id') if candidate else None,year=candidate.get('year') if candidate else None,country=candidate.get('country') if candidate else None,local86=candidate.get('local86') if candidate else None,media_type86=candidate.get('media_type86','tv') if candidate else 'tv',at=int(time.time()),provenance='USER_CONFIRMED' if not hidden else 'USER_HIDDEN')
  if not automatic and candidate and candidate.get('verified85'):
   from programme_urls55 import safe
   data['records'][key]['work87']=dict(title=str(candidate.get('title') or '')[:200],role=candidate.get('role') if candidate.get('role') in ('poster','backdrop') else '',**{k:candidate[k] for k in ('url','poster') if candidate.get(k) and safe(candidate[k])})
  if len(data['records'])>MAX_RECORDS:raise OSError('MANUAL_LIMIT')
  raw=json.dumps(data,separators=(',',':'),sort_keys=True).encode()
  if len(raw)>MAX_BYTES:raise OSError('MANUAL_LIMIT')
  check_space(str(filename),len(raw)+65536)
  fd,tmp=tempfile.mkstemp(prefix='.manual85-',dir=filename.parent)
  try:
   with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
   # Verify the candidate bytes before activating; keep last valid file intact.
   if json.loads(Path(tmp).read_bytes())!=data:raise OSError('MANUAL_READBACK')
   if cancel():raise __import__('media_sources43').SourceError('CANCELLED')
   os.replace(tmp,filename)
   directory=os.open(filename.parent,os.O_RDONLY)
   try:os.fsync(directory)
   finally:os.close(directory)
   if read()!=data:raise OSError('MANUAL_READBACK')
   publish(data)
  finally:
   if os.path.exists(tmp):os.unlink(tmp)
 return True

def epoch(event):
 if not event.get('pid'):return 0
 from epg_handoff63 import profile_scope
 if window().getProperty(PREFIX+'Profile')!=profile_scope():return 0
 raw=window().getProperty(PREFIX+'Records')
 try:
  if not raw or len(raw.encode())>MAX_BYTES:return 0
  epochs=parsed85(raw).get('epochs',{})
  if not epochs:return 0
  value=epochs.get(namespace(event),0)
  return value if type(value) is int and value>=0 else 0
 except (TypeError,ValueError):return 0

_source_due={}
def refresh_sources(portal_id):
 """Worker-only config read. Publish only hashes; never credentials/URLs."""
 from epg_handoff63 import profile_scope
 tag=profile_scope()+str(portal_id);now=time.monotonic()
 if now<_source_due.get(tag,0):return
 from epg_sources import configuration
 state=configuration(portal_id)
 sources=[[s.get(k) for k in ('id','uri','enabled','local')] for s in state.get('sources',[])]
 material=[sources,dict(state.get('mappings',{})),state.get('source_mappings48',{})]
 digest=hashlib.sha256(json.dumps(material,sort_keys=True).encode()).hexdigest() if any(material) else ''
 window().setProperty(PREFIX+'Sources.'+tag,digest)
 _source_due[tag]=now+30
 while len(_source_due)>8:_source_due.pop(next(iter(_source_due)))
def source_scope(event):
 if event.get('source_key46') or event.get('epg_source46'):return ''
 from epg_handoff63 import profile_scope
 return window().getProperty(PREFIX+'Sources.'+profile_scope()+str(event.get('pid')))


def reload():
 # Shared read lease serializes publication with the manager's atomic writer.
 # reading() creates no file in a legacy/space-blocked profile.
 from profile_transaction import reading
 try:
  with reading(timeout=.1):return _reload85()
 except (OSError,TimeoutError):return False

_parsed85=(None,{})
def parsed85(raw):
 global _parsed85
 if raw==_parsed85[0]:return _parsed85[1]
 value=json.loads(raw)
 if not isinstance(value,dict):raise ValueError('MANUAL_SCHEMA')
 _parsed85=(raw,value)
 return value
