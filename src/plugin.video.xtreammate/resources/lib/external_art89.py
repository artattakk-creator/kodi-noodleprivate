"""Selected USB/SD/Kodi-SMB image backend; databases remain in userdata.

All remote IO is worker-only. Readers use bounded local receipts. No automatic
target selection, mount creation, internal image fallback, eviction or cleanup.
The existing backend owns authentication, collision guards and SHA readback.
"""
import hashlib,json,time,threading
from pathlib import Path
_pending={};_due={};_checked={};_lock=threading.RLock()
ROLES={'logo':('logos',16*1024**2),'poster':('media',24*1024**2),'programme':('fanart',32*1024**2)}

def enabled():
 from artwork_config import read
 return read().get('mode')=='external'

def selected(role,config=None):
 from artwork_config import read
 from artwork_vfs import backend_for,StorageFailure
 config=read() if config is None else config
 if config.get('mode')!='external':raise StorageFailure('EXTERNAL_NOT_SELECTED')
 value=backend_for(config['target'],config['profile'],ROLES[role][0])
 if role!='logo':
  from artwork_vfs import VFSArtworkStorage,ExternalLocalStorage
  root=value.root+('/verified_posters89' if role=='poster' else '/programmes89')
  value=(VFSArtworkStorage if value.kind=='KODI_VFS' else ExternalLocalStorage)(root,value.owner_marker)
 return value

def backend(role,config=None):
 from artwork_vfs import StorageFailure
 value=selected(role,config)
 if value.availability()!='AVAILABLE':raise StorageFailure('STORAGE_OFFLINE')
 return value

def path(role,config=None):
 from artwork_config import read
 from utils import addon_data_dir
 config=read() if config is None else config
 target=config.get('target') if config.get('archive_mode',config.get('mode'))=='external' else 'INTERNAL'
 tag=hashlib.sha256(json.dumps([target,config.get('profile'),role]).encode()).hexdigest()[:24]
 return Path(addon_data_dir())/('xcmate_external89_'+tag+'.json')

def records(role,config=None):
 try:
  file=path(role,config)
  if file.is_symlink() or file.stat().st_size>512*1024:return {}
  value=json.loads(file.read_bytes())
  if value.get('format')!=1 or not isinstance(value.get('records'),dict) or len(value['records'])>512:return {}
  return {k:v for k,v in value['records'].items() if isinstance(k,str) and len(k)<=128 and isinstance(v,dict)}
 except (OSError,ValueError,KeyError,TypeError):return {}

def store(role,key,body,receipt,cancel=lambda:False,config=None):
 from profile_transaction import writing
 from artwork_vfs import image_valid,StorageFailure
 from media_sources43 import validate_image
 from logo_store89 import atomic
 with writing(timeout=.2):
  if cancel():raise InterruptedError('CANCELLED')
  storage=backend(role,config);quota=ROLES[role][1]
  if not image_valid(body):raise StorageFailure('INVALID_IMAGE')
  width,height=validate_image(body);digest=hashlib.sha256(body).hexdigest()
  if role!='logo':
   if storage.kind=='KODI_VFS':
    import xbmcvfs
    if not xbmcvfs.exists(storage.root+'/') and not xbmcvfs.mkdirs(storage.root+'/'):raise StorageFailure('TARGET_WRITE_FAILED')
   else:Path(storage.root).mkdir(exist_ok=True)
  if storage.kind=='KODI_VFS':
   import xbmcvfs
   directories,files=xbmcvfs.listdir(storage.root)
   if directories or len(files)>1024:raise StorageFailure('EXTERNAL_IMAGE_QUOTA')
   physical=0
   for name in files:
    try:size=xbmcvfs.Stat(storage.root+'/'+name).st_size()
    except (AttributeError,RuntimeError,OSError):raise StorageFailure('EXTERNAL_QUOTA_UNVERIFIED') from None
    if type(size) is not int or size<0:raise StorageFailure('EXTERNAL_QUOTA_UNVERIFIED')
    physical+=size
    if physical+len(body)>quota+512*1024:raise StorageFailure('EXTERNAL_IMAGE_QUOTA')
    # Never ignore crash leftovers when accounting a bounded NAS namespace.
    # The current exact hash may be safely finished by write_verified; all
    # other uncommitted images/parts require explicit transfer recovery.
    if name.endswith('.img') and not xbmcvfs.exists(storage.root+'/'+name+'.ok') and name!=digest+'.img':raise StorageFailure('EXTERNAL_TRANSFER_INCOMPLETE')
    if '.part.' in name:raise StorageFailure('EXTERNAL_TRANSFER_INCOMPLETE')
  # Count the selected owned namespace, including pre-existing legacy images.
  used=count=0
  for item in storage.enumerate_for_migration():
   count+=1;used+=item['bytes']
   if count>512 or used>quota:raise StorageFailure('EXTERNAL_IMAGE_QUOTA')
  if used+(0 if storage.exists(digest) else len(body))>quota:raise StorageFailure('EXTERNAL_IMAGE_QUOTA')
  from art_storage import check
  facts=check(len(body),limit=0,backend=storage)
  values=records(role,config);record=dict(receipt,sha256=digest,width=width,height=height,bytes=len(body),at=time.time())
  values[key]=record;raw=json.dumps(dict(format=1,records=values),separators=(',',':')).encode()
  if len(values)>512 or len(raw)>512*1024:raise StorageFailure('EXTERNAL_RECEIPT_QUOTA')
  from metadata_store89 import check as metadata_check
  file=path(role,config);metadata_check(file,len(raw)+65536)
  storage.write_verified(digest,body,image_valid)
  if storage.read(digest,len(body)+1)!=body:raise StorageFailure('IMAGE_VERIFY_FAILED')
  if cancel():raise InterruptedError('CANCELLED')
  # Recheck the selected namespace before publishing its local receipt.
  again=backend(role,config)
  if again.resolve_target()!=storage.resolve_target():raise StorageFailure('TARGET_VOLUME_UNVERIFIED')
  atomic(file,raw)
  if records(role,config).get(key)!=record:raise StorageFailure('EXTERNAL_RECEIPT_READBACK')
  _checked[(str(file),digest)]=time.monotonic()+300
  return storage.make_display_uri(digest),facts

def confirm(role,key,record):
 """Worker-only cold/periodic SHA check, separate from pure UI readers."""
 if record.get('invalid'):return False
 tag=(str(path(role)),record.get('sha256'))
 storage=backend(role)
 if time.monotonic()<_checked.get(tag,0):return True
 try:
  data=storage.read(record['sha256'],3*1024*1024+1)
  if hashlib.sha256(data).hexdigest()!=record['sha256']:raise OSError('IMAGE_VERIFY_FAILED')
 except OSError as error:
  if getattr(error,'code',str(error)) not in ('IMAGE_VERIFY_FAILED','UNVERIFIED_IMAGE'):raise
  from profile_transaction import writing
  from logo_store89 import atomic
  from metadata_store89 import check
  with writing(timeout=.2):
   values=records(role)
   if values.get(key,{}).get('sha256')!=record.get('sha256'):return False
   values[key]=dict(record,invalid=True)
   raw=json.dumps(dict(format=1,records=values),separators=(',',':')).encode();file=path(role);check(file,len(raw)+65536);atomic(file,raw)
  return False
 _checked[tag]=time.monotonic()+300
 while len(_checked)>512:_checked.pop(next(iter(_checked)))
 return True

def key(portal,kind,row,role='poster'):
 if kind=='logo':return __import__('logo_store89').identity(portal,row)
 return __import__('poster_store89').identity(portal,kind,row,role)

def references(portal,kind,rows,internal=False):
 if not enabled() and not internal:return {}
 from widget_refs74 import revoked
 role='logo' if kind=='logo' else 'poster';values=records(role)
 # No SMB existence/read/stat in a GUI or DirectoryProvider reader.
 try:
  if enabled():storage=selected(role)
  else:
   from artwork_config import read
   storage=migration_backend(read(),'poster' if role=='poster' else 'logo')
 except (OSError,ValueError,TypeError):return {}
 result={}
 for row in rows[:256 if kind=='logo' else 24]:
  if row.get('_no_art86') or row.get('_manual_art43'):continue
  for image_role in ('poster',) if kind=='logo' else ('poster','fanart'):
   record=values.get(key(portal,kind,row,image_role),{})
   if not record or record.get('invalid') or revoked(record.get('source','')):continue
   if kind=='logo' and revoked(__import__('station_logos87').source(row)):continue
   digest=record.get('sha256','')
   if len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):continue
   uri=storage.make_display_uri(digest)
   if kind=='logo':result[str(row['sid'])]=uri
   else:result.setdefault(str(row['sid']),{})[image_role]=uri
 return result

def ready_count(portal,kind,rows,refs):
 import os
 confirmed=references(portal,kind,rows,internal=True);count=0
 for row in rows:
  sid=str(row['sid']);uri=row.get('_manual_art43',{}).get('poster') or refs.get(sid,{}).get('poster') or refs.get(sid,{}).get('thumb') or ''
  count+=int(os.path.isabs(uri) or bool(uri and uri==confirmed.get(sid,{}).get('poster')))
 return count

def archive_programme(event,value,body):
 """Already verified bytes are queued AFTER display admission; no GUI IO."""
 if not enabled() or value.get('provisional85'):return
 from event_cache88 import receipt
 proof=receipt(value)
 if not proof:return
 tag=__import__('programme_lock89').key(event)
 if tag in records('programme') or time.monotonic()<_due.get(tag,0):return
 with _lock:
  if len(_pending)>=5 or sum(len(v[2]) for v in _pending.values())+len(body)>12*1024**2:return
  _pending[tag]=(dict(event),proof,body,context())

def context():
 from artwork_config import read
 from epg_handoff63 import profile_scope
 value=read();return [profile_scope(),value.get('target'),value.get('profile')]

def drain(cancel=lambda:False):
 if not enabled():return
 with _lock:
  if not _pending:return
  tag=next(iter(_pending));event,proof,body,owner=_pending.pop(tag)
 if owner!=context() or tag!=__import__('programme_lock89').key(event):return
 try:store('programme',tag,body,dict(proof=proof),cancel)
 except (OSError,ValueError,TypeError,RuntimeError):_due[tag]=time.monotonic()+300
 while len(_due)>128:_due.pop(next(iter(_due)))

def recover_programme(event):
 values=records('programme')
 if not values:return None
 tag=__import__('programme_lock89').key(event);record=values.get(tag)
 if not record:return None
 from event_cache88 import clean,admitted
 try:
  proof=clean(record['proof'])
  if not admitted(proof,event):return None
  if enabled():storage=backend('programme')
  else:
   from artwork_config import read
   storage=migration_backend(read(),'programme')
  data=storage.read(record['sha256'],3*1024*1024+1)
  if hashlib.sha256(data).hexdigest()!=record['sha256']:return None
  value=dict(proof,code='READY',decoded77=True,image_width77=record['width'],image_height77=record['height'])
  value['attribution']='TMDB · '+__import__('tmdb_connection60').ATTRIBUTION if proof['source'].startswith('tmdb') else 'TVmaze · Daten CC BY-SA; Bildrechte beim Rechteinhaber' if proof['source'].startswith('tvmaze') else 'XMLTV' if proof['source']=='xmltv_event' else 'Provider'
  return __import__('sticky_art88').publish89(event,value,data)
 except (OSError,ValueError,TypeError,KeyError,RuntimeError):return None

class MigrationImages89:
 """Use the existing transfer journal for the new owned hash-image folders."""
 def __init__(self,storage):self.storage=storage
 def __getattr__(self,name):return getattr(self.storage,name)
 def enumerate_for_migration(self):
  storage=self.storage
  if storage.kind=='KODI_VFS':
   import xbmcvfs
   if storage.availability()!='AVAILABLE':raise OSError('STORAGE_OFFLINE')
   if not xbmcvfs.exists(storage.root+'/'):return
  yield from storage.enumerate_for_migration()
 def write_verified(self,ident,data,validate):
  storage=self.storage
  if storage.kind=='KODI_VFS':
   import xbmcvfs
   if storage.availability()!='AVAILABLE':raise OSError('STORAGE_OFFLINE')
   if not xbmcvfs.exists(storage.root+'/') and not xbmcvfs.mkdirs(storage.root+'/'):raise OSError('TARGET_WRITE_FAILED')
  else:
   if getattr(storage,'is_external',False) and storage.availability()!='AVAILABLE':raise OSError('STORAGE_OFFLINE')
   Path(storage.root).mkdir(parents=not getattr(storage,'is_external',False),exist_ok=True)
  return storage.write_verified(ident,data,validate)

def migration_backend(config,role):
 if config.get('archive_mode',config['mode'])=='external':
  return MigrationImages89(selected(role,dict(config,mode='external')))
 from artwork_backend import LocalArtworkStorage
 from utils import addon_data_dir
 root=Path(addon_data_dir())/({'logo':'tv_logos','poster':'media_art_v1/verified_posters89','programme':'programme_external89'}[role])
 return MigrationImages89(LocalArtworkStorage(str(root)))

def migrate_receipts(source,target,verified):
 """Only after the existing full SHA/render gates, before target activation."""
 from utils import addon_data_dir
 from metadata_store89 import check
 from logo_store89 import atomic
 for role,kind in (('logo','logos'),('poster','posters89'),('programme','programme89')):
  if source.get('archive_mode',source['mode'])=='external':incoming=records(role,dict(source,mode='external'))
  else:
   filename=Path(addon_data_dir())/('tv_logos/manifest86.json' if role=='logo' else 'media_art_v1/verified_posters89/manifest89.json')
   incoming={}
   if role!='programme' and filename.is_file() and not filename.is_symlink() and filename.stat().st_size<=512*1024:
    value=json.loads(filename.read_bytes());incoming=value.get('records',{}) if value.get('format')==1 else {}
    if role=='logo':incoming={r['stable89']:r for r in incoming.values() if r.get('stable89')}
  outgoing=records(role,target);changed=False
  for key,record in list(incoming.items())[:512]:
   proof=verified.get((kind,record.get('sha256')))
   if not proof or proof['sha']!=record.get('sha256'):continue
   outgoing[key]={k:v for k,v in record.items() if k not in ('stamp','context','stable89','storage89')};outgoing[key]['bytes']=proof['bytes'];changed=True
  if not changed:continue
  raw=json.dumps(dict(format=1,records=outgoing),separators=(',',':')).encode();file=path(role,target)
  if len(outgoing)>512 or len(raw)>512*1024:raise OSError('EXTERNAL_RECEIPT_QUOTA')
  check(file,len(raw)+65536);atomic(file,raw)
  if file.read_bytes()!=raw:raise OSError('EXTERNAL_RECEIPT_READBACK')
