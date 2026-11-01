"""Staged private token transaction; fixed diagnostics contain no secret data."""
import errno,hashlib,os,uuid
STAGES=frozenset(('SOURCE_SELECTION','VFS_READ','UTF8_FORMAT_VALIDATION','PROFILE_ANCHOR','PRIVATE_DESTINATION_READ','PRIVATE_DIRECTORY','TEMP_CREATE','TEMP_WRITE','FILE_FSYNC','ATOMIC_RENAME','DIRECTORY_FSYNC','POSTWRITE_VERIFY','STATUS_VERIFY','TEMP_CLEANUP'))
def note(stage,code='OK',error=0,committed=False,subcode='NONE'):
 if stage not in STAGES:return
 if code not in ('OK','FAILED','UNSUPPORTED','SYNC_WARNING','VERIFIED','CANCELLED'):code='FAILED'
 try:
  import xbmc
  from token_destination65 import SUBCODES
  subcode=subcode if subcode in SUBCODES else 'UNSAFE_PATH'
  xbmc.log('[XCMate][TOKEN64] schema=65 subcode='+subcode+' stage='+stage+' code='+code+' errno='+str(error if type(error) is int and 0<=error<4096 else 0)+' committed='+str(int(bool(committed))),xbmc.LOGINFO)
 except (ImportError,AttributeError,RuntimeError):pass

def read_destination(tokens,path,initialize=False):
 try:
  if initialize:
   fd,_=tokens.private_parent(path);os.close(fd);note('PRIVATE_DIRECTORY')
  return tokens.read(path,missing=True)
 except tokens.TokenError as error:
  error.stage='PRIVATE_DESTINATION_READ';note(error.stage,'FAILED',getattr(error,'errno',0),subcode=getattr(error,'subcode','UNSAFE_PATH'));raise
 except OSError as error:
  failure=tokens.TokenError('TOKEN_UNREADABLE');failure.stage='PRIVATE_DESTINATION_READ'
  note(failure.stage,'FAILED',error.errno or 0);raise failure from None

def diagnostic(tokens):
 try:
  tokens.effective_tmdb_read_token(force=True)
  return dict(code=tokens.status(),stage='STATUS_VERIFY')
 except tokens.TokenError as error:
  return dict(code=error.code,stage='PRIVATE_DESTINATION_READ')

def import_bytes(raw,expected,target=None):
 import tmdb_token61 as tokens
 fd=None;temp=None;committed=False;stage='UTF8_FORMAT_VALIDATION';sync_error=0
 try:
  value=tokens.validate(raw);note(stage)
  stage='PROFILE_ANCHOR';path=tokens.location()
  if target is not None and target!=path:raise tokens.TokenError('TOKEN_CHANGED')
  note(stage)
  stage='PRIVATE_DIRECTORY';fd,name=tokens.private_parent(path);note(stage)
  stage='PRIVATE_DESTINATION_READ';before=tokens.read(path,missing=True)
  digest=hashlib.sha256(before).hexdigest() if before is not None else None
  if digest!=expected:raise tokens.TokenError('TOKEN_CHANGED')
  note(stage)
  temp='.tmdb64-'+uuid.uuid4().hex
  stage='TEMP_CREATE';out=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fd);note(stage)
  with os.fdopen(out,'wb') as stream:
   stage='TEMP_WRITE';stream.write((value+'\n').encode());stream.flush();note(stage)
   stage='FILE_FSYNC';os.fsync(stream.fileno());note(stage)
  stage='PRIVATE_DESTINATION_READ';current=tokens.read(path,missing=True)
  if (hashlib.sha256(current).hexdigest() if current is not None else None)!=expected:raise tokens.TokenError('TOKEN_CHANGED')
  stage='PROFILE_ANCHOR'
  if tokens.location()!=path:raise tokens.TokenError('TOKEN_CHANGED')
  stage='ATOMIC_RENAME';os.replace(temp,name,src_dir_fd=fd,dst_dir_fd=fd);committed=True;note(stage,committed=True)
  stage='DIRECTORY_FSYNC'
  try:os.fsync(fd);note(stage,committed=True)
  except OSError as error:
   sync_error=error.errno or errno.EIO
   note(stage,'UNSUPPORTED' if sync_error in (errno.EINVAL,errno.ENOTSUP,getattr(errno,'EOPNOTSUPP',errno.ENOTSUP)) else 'SYNC_WARNING',sync_error,True)
  stage='POSTWRITE_VERIFY'
  if tokens.location()!=path:raise tokens.TokenError('TOKEN_CHANGED')
  after=tokens.read(path)
  if after!=(value+'\n').encode() or tokens.validate(after)!=value:raise tokens.TokenError('TOKEN_COMMIT_UNVERIFIED')
  note(stage,'VERIFIED',committed=True)
  stage='STATUS_VERIFY'
  if tokens.location()!=path or tokens.effective_tmdb_read_token(force=True)!=value:raise tokens.TokenError('TOKEN_COMMIT_UNVERIFIED')
  note(stage,'VERIFIED',committed=True)
  return 'IMPORTED_SYNC_WARNING' if sync_error else 'IMPORTED'
 except (tokens.TokenError,OSError,NotImplementedError,RuntimeError) as error:
  code=error.code if isinstance(error,tokens.TokenError) else 'TOKEN_WRITE'
  if committed and code!='TOKEN_CHANGED':code='TOKEN_COMMIT_UNVERIFIED'
  failure=tokens.TokenError(code);failure.stage=stage;failure.committed=committed
  failure.errno=getattr(error,'errno',0) or 0
  failure.subcode=getattr(error,'subcode','UNSAFE_PATH')
  note(stage,'FAILED',failure.errno,committed,subcode=failure.subcode)
  raise failure from None
 finally:
  if fd is not None:
   if temp:
    try:os.unlink(temp,dir_fd=fd)
    except FileNotFoundError:pass
    except OSError as error:note('TEMP_CLEANUP','FAILED',error.errno or 0,committed)
   os.close(fd)
