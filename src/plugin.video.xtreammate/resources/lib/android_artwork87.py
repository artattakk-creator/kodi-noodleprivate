"""Explicit .87 Android migration gates. No automatic relocation or cleanup."""
import hashlib,json,os,re,tempfile,time
from artwork_vfs import StorageFailure
RESERVE=1024**3

def preflight(target,upcoming=4096,source_config=None):
 from android_storage83 import inventory,relation,public
 from artwork_config import read
 from art_storage import WRITE_HEADROOM
 config=source_config if source_config is not None else read()
 rows=inventory(target,config);destination=rows[-1]
 roles=('ACTIVE_MEDIA','ACTIVE_LOGOS','PROGRAMME_IMAGES') if config.get('archive_mode',config['mode'])=='external' else ('INTERNAL_MEDIA','INTERNAL_LOGOS','PROGRAMME_IMAGES')
 sources=[row for row in rows[:-1] if row['role'] in roles]
 relations=[relation(row,destination) if not row.get('error') else 'TARGET_VOLUME_UNVERIFIED' for row in sources]
 code='NO_SEPARATE_WRITABLE_VOLUME' if 'TARGET_SAME_CAPACITY_POOL' in relations else 'TARGET_VOLUME_UNVERIFIED' if len(sources)!=len(roles) or 'TARGET_VOLUME_UNVERIFIED' in relations else 'SEPARATE_POOL_VERIFIED'
 destination['reserve']=max(RESERVE,destination.get('reserve',RESERVE))
 if destination['mount'].get('readonly'):code='TARGET_NOT_WRITABLE'
 if code=='SEPARATE_POOL_VERIFIED' and destination['available']<destination['reserve']+max(0,upcoming)+WRITE_HEADROOM:code='TARGET_RESERVE_BLOCKED'
 if code!='SEPARATE_POOL_VERIFIED':
  error=StorageFailure(code);error.receipt=public(rows);raise error
 return dict(target=destination['path'],volume=destination['volume'],mount_key=destination['mount_key'],code=code,rows=public(rows))

def probe(target,profile,*,confirmed=False):
 if confirmed is not True:raise StorageFailure('TARGET_PROBE_CONFIRMATION_REQUIRED')
 from artwork_vfs import prepare_target
 from android_storage83 import failure
 receipt=preflight(target);filename=published=None
 try:
  storage=prepare_target(receipt['target'],profile);payload=os.urandom(4096)
  fd,filename=tempfile.mkstemp(prefix='.probe87-',dir=storage.root)
  with os.fdopen(fd,'wb') as stream:stream.write(payload);stream.flush();os.fsync(stream.fileno())
  published=filename+'.verified';os.replace(filename,published);filename=None
  directory=os.open(storage.root,os.O_RDONLY)
  try:os.fsync(directory)
  finally:os.close(directory)
  with open(published,'rb') as stream:readback=stream.read(4097)
  if readback!=payload:raise StorageFailure('TARGET_PROBE_VERIFY_FAILED')
  after=preflight(target)
  if (receipt['volume'],receipt['mount_key'])!=(after['volume'],after['mount_key']):raise StorageFailure('TARGET_VOLUME_UNVERIFIED')
  import xbmcgui
  xbmcgui.Window(10000).setProperty('XCMate.Storage87.LastProbe',json.dumps(dict(volume=receipt['volume'],at=time.time(),code='WRITE_FSYNC_RENAME_READBACK')))
  return receipt
 except StorageFailure:raise
 except OSError as error:raise StorageFailure(failure(error)) from None
 finally:
  for own in (filename,published):
   if own and os.path.exists(own):os.unlink(own)

def programme_root(config=None):
 from artwork_config import read,root
 config=read() if config is None else config
 target=config.get('programme_target87')
 if target and config['mode']=='external' and target==config.get('target'):
  from artwork_vfs import backend_for
  return os.path.join(os.path.dirname(os.path.dirname(backend_for(target,config['profile'],'logos').root)),'programme_images87',config['profile'])
 return os.path.join(root(),'programme_images46')

def activate_programmes(target):
 # Only the existing migrator calls this after full source/target SHA and
 # explicit render verification. No settings/token/SQLite moves.
 from artwork_config import locked,read,_write
 with locked():
  config=read()
  if config['mode']!='external' or config.get('target')!=target:raise StorageFailure('TARGET_VOLUME_UNVERIFIED')
  config['programme_target87']=target;_write(config)

def public_status():
 from artwork_backend import active_backend
 from android_storage83 import measure
 from artwork_config import read
 import xbmcgui
 row=measure(active_backend('logos').root,'ACTIVE_LOGOS')
 reserve=max(RESERVE,row['reserve'])
 try:probe=json.loads(xbmcgui.Window(10000).getProperty('XCMate.Storage87.LastProbe') or '{}')
 except ValueError:probe={}
 return dict(active_mount=row['mount_key'],filesystem=row['fs'],total=row['total'],available=row['available'],reserve=reserve,budget=max(0,row['available']-reserve-256*1024),last_write_readback=probe,programme_external=bool(read().get('programme_target87')))
