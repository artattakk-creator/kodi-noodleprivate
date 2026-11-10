"""Independent provider-logo manifest. No EPG, artwork SQLite or mode migration.

The existing chosen local logo volume and complete reserve are authoritative.
No probing of private USB/SMB targets, no automatic relocation or deletions.
"""
import hashlib,json,os,tempfile,time
LIMIT=512*1024
_due={}
def context(portal):
 from widget_data41 import policy
 from epg_handoff63 import profile_scope
 return hashlib.sha256(json.dumps([profile_scope(),policy(portal,'live'),[portal.get(k) for k in ('id','type','xc_host','xc_user','xc_pass')]],sort_keys=True).encode()).hexdigest()
def source(row):
 from media_art import poster_candidates
 values=poster_candidates(row)
 return values[0] if values else ''
def key(portal,row,scope=None):
 return hashlib.sha256(((scope or context(portal))+'|'+str(row['sid'])+'|'+source(row)).encode()).hexdigest()
def location():
 from artwork_backend import active_backend,LocalArtworkStorage
 backend=active_backend('logos')
 if not isinstance(backend,LocalArtworkStorage):raise OSError('EXTERNAL_UNAVAILABLE')
 return backend,os.path.join(backend.root,'manifest86.json')
def load(portal,all_records=False):
 try:
  backend,path=location()
  if os.path.islink(path) or os.path.getsize(path)>LIMIT:return {}
  with open(path,'rb') as stream:data=json.load(stream)
  if data.get('format')!=1:return {}
  records=data.get('records',{});scope=context(portal)
  return {k:v for k,v in records.items() if isinstance(v,dict) and (all_records or v.get('context')==scope)} if isinstance(records,dict) and len(records)<=512 else {}
 except (OSError,ValueError,TypeError,AttributeError):return {}
def read(portal,rows,with_fallback=True):
 records=load(portal);result={};scope=context(portal)
 # Existing Kodi-local decoded logos remain valid without adopting/deleting files.
 from widget_cache79 import load as cached,valid
 from media_art import poster_candidates
 refs=cached(portal,'live').get('refs',{}) if with_fallback else {}
 for row in rows:
  value=refs.get(str(row['sid']),{}).get('poster',{})
  if value.get('source') in poster_candidates(row) and valid(value,value.get('source')):result[str(row['sid'])]=value['file']
 # Bootstrap pre-.86 source-addressed local archives without per-item SQL,
 # decoding or network. These are references; Kodi pixel proof stays separate.
 if with_fallback:
  from artwork_backend import active_backend,LocalArtworkStorage
  try:
   archive=active_backend('media')
   if isinstance(archive,LocalArtworkStorage):
    for row in rows:
     sid=str(row['sid'])
     if sid in result:continue
     for uri in poster_candidates(row):
      file=archive.resolve_target(hashlib.sha256(uri.encode()).hexdigest())
      try:
       if not os.path.islink(file) and 0<os.stat(file).st_size<=3*1024*1024:
        # Match the legacy bounded header guard; never run Pillow/SQL here.
        from media_art import dimensions,MAX_PIXELS
        with open(file,'rb') as stream:width,height=dimensions(stream.read(65536))
        if not 0<width<=4096 or not 0<height<=4096 or width*height>MAX_PIXELS:continue
        result[sid]=file;break
      except (OSError,ValueError,TypeError,__import__('struct').error):continue
  except (OSError,ValueError):pass
 try:backend,_=location()
 except OSError:return result
 for row in rows:
  record=records.get(key(portal,row,scope),{})
  try:
   file=backend.resolve_target(record['sha256'])
   if os.path.islink(file):continue
   stat=os.stat(file)
   if record.get('stamp')==[stat.st_mtime_ns,stat.st_size] and record.get('width',0)>0 and record.get('height',0)>0:result[str(row['sid'])]=file
  except (KeyError,OSError,ValueError,TypeError):continue
 return result
def _save(backend,path,records):
 from art_storage import check
 from profile_transaction import writing
 raw=json.dumps(dict(format=1,records=records),sort_keys=True,separators=(',',':')).encode()
 if len(records)>512 or len(raw)>LIMIT:raise OSError('LOGO_MANIFEST_LIMIT')
 with writing(timeout=.1):
  check(len(raw)+65536,limit=0,backend=backend)
  if os.path.islink(path):raise OSError('LOGO_MANIFEST_UNSAFE')
  os.makedirs(backend.root,exist_ok=True)
  fd,tmp=tempfile.mkstemp(prefix='.logo86-',dir=backend.root)
  try:
   with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
   with open(tmp,'rb') as stream:
    if stream.read()!=raw:raise OSError('LOGO_MANIFEST_READBACK')
   os.replace(tmp,path)
   directory=os.open(backend.root,os.O_RDONLY)
   try:os.fsync(directory)
   finally:os.close(directory)
  finally:
   if os.path.exists(tmp):os.unlink(tmp)
def prepare(portal,rows,cancel=lambda:False):
 """Existing provider worker calls bounded incremental recovery/downloads."""
 from art_storage import check
 from widget_assets69 import safe
 from programme_transport77 import verified
 from media_sources43 import SourceError,validate_image
 try:backend,path=location()
 except OSError:return 'EXTERNAL_UNAVAILABLE'
 records=load(portal,all_records=True);hit=read(portal,rows,with_fallback=False);fallback=read(portal,rows);changed=False;attempts=0;started=time.monotonic()
 for row in rows[:256]:
  if cancel() or time.monotonic()-started>2:break
  tag=key(portal,row);uri=source(row)
  if str(row['sid']) in hit or not uri or time.monotonic()<_due.get(tag,0):continue
  if attempts>=2:break
  attempts+=1;_due[tag]=time.monotonic()+60
  try:
   # Check before networking; actual reserve failure is never disguised as success.
   check(3*1024*1024+65536,limit=0,backend=backend)
   if not safe(portal,uri):continue
   existing=fallback.get(str(row['sid']),'')
   if existing.startswith('/'):
    with open(existing,'rb') as stream:body=stream.read(3*1024*1024+1)
    width,height=validate_image(body);checked=dict(width=width,height=height)
   else:
    checked=verified(uri,cancel=cancel,keep_data81=True);body=checked['_body81']
   digest=hashlib.sha256(body).hexdigest()
   backend.write_verified(digest,body,lambda raw:bool(validate_image(raw)))
   stat=os.stat(backend.resolve_target(digest))
   records[tag]=dict(context=context(portal),sha256=digest,stamp=[stat.st_mtime_ns,stat.st_size],width=checked['width'],height=checked['height'])
   changed=True
  except (OSError,ValueError,TypeError,SourceError):continue
 while len(_due)>512:_due.pop(next(iter(_due)))
 if changed:
  try:_save(backend,path,records)
  except (OSError,TimeoutError):return 'EXTERNAL_UNAVAILABLE'
 return 'READY' if len(hit)==len(rows) else 'PARTIAL' if hit or changed else 'EXTERNAL_UNAVAILABLE'


def remote(portal,rows):
 """Public provider leases already approved by the existing worker; RAM only."""
 from widget_assets69 import identity,profile,PREFIX,safe
 from artwork_visible import KODI_OPTIONS
 from widget_refs74 import revoked
 import xbmcgui
 win=xbmcgui.Window(10000);result={}
 for row in rows:
  uri=source(row)
  if not uri or not safe(portal,uri) or revoked(uri):continue
  tag=identity(portal,'live',row,'poster',uri)
  try:
   raw=win.getProperty(PREFIX+tag);value=json.loads(raw) if raw and len(raw)<4096 else {}
   if value.get('key')==tag and value.get('profile')==profile() and 0<value.get('until',0)-time.time()<=30 and value.get('uri')==uri+KODI_OPTIONS:result[str(row['sid'])]=(value['uri'],tag)
  except (ValueError,TypeError):continue
 return result

def reference(props):
 from portals import get_by_id
 from artwork_visible import KODI_OPTIONS
 uri=props.get('XCMate.ProgrammeLogo46','');tag=props.get('XCMate.LogoProof86','')
 if not uri.endswith(KODI_OPTIONS) or not tag:return ''
 portal=get_by_id(str(props.get('XCMate.PortalId')))
 if not portal:return ''
 row=dict(sid=str(props.get('XCMate.MediaId')),cover=uri[:-len(KODI_OPTIONS)],kind='live')
 return uri if remote(portal,[row]).get(row['sid'])==(uri,tag) else ''
