"""Kodi-owned profile anchor; never relax private-child or final-file guards."""
import errno,os,stat,uuid
SUBCODES=frozenset(('NONE','MISSING_PARENT','ACCESS_DENIED','READ_ONLY','SYMLINK_OR_NOT_DIRECTORY','NOT_REGULAR','IO_ERROR','DIRECTORY_UNSUPPORTED','PROFILE_CHANGED','RECOVERY_CHANGED','RECOVERY_DECLINED','UNSAFE_PATH'))
class Cancelled65(Exception):pass
def subcode(error):
 number=getattr(error,'errno',0) or 0
 return {errno.ENOENT:'MISSING_PARENT',errno.EACCES:'ACCESS_DENIED',errno.EPERM:'ACCESS_DENIED',errno.EROFS:'READ_ONLY',errno.ELOOP:'SYMLINK_OR_NOT_DIRECTORY',errno.ENOTDIR:'SYMLINK_OR_NOT_DIRECTORY',errno.EIO:'IO_ERROR',errno.EINVAL:'DIRECTORY_UNSUPPORTED',errno.ENOTSUP:'DIRECTORY_UNSUPPORTED',errno.ENOSYS:'DIRECTORY_UNSUPPORTED'}.get(number,'UNSAFE_PATH')
def failure(code,error=None,detail=None):
 from tmdb_token61 import TokenError
 value=TokenError(code);value.errno=getattr(error,'errno',0) or 0
 value.subcode=detail or subcode(error)
 return value
def _directory(path,dir_fd=None):
 if not hasattr(os,'O_NOFOLLOW'):raise failure('TOKEN_PATH',detail='DIRECTORY_UNSUPPORTED')
 flags=os.O_RDONLY|os.O_NOFOLLOW|getattr(os,'O_NONBLOCK',0)
 directory=getattr(os,'O_DIRECTORY',0)
 attempts=[flags|directory]
 # O_PATH allows search without listing a legitimate Kodi-owned directory.
 # Every opened descriptor is checked before it can serve as a parent.
 if hasattr(os,'O_PATH'):attempts.append(os.O_PATH|os.O_NOFOLLOW|directory)
 if directory:attempts.append(flags)
 for index,mode in enumerate(dict.fromkeys(attempts)):
  try:
   fd=os.open(path,mode,dir_fd=dir_fd)
   if not stat.S_ISDIR(os.fstat(fd).st_mode):
    os.close(fd);raise failure('TOKEN_PATH',detail='SYMLINK_OR_NOT_DIRECTORY')
   return fd
  except OSError as error:
   retry=error.errno in (errno.EINVAL,errno.ENOTSUP,errno.ENOSYS,errno.EACCES,errno.EPERM)
   if not retry or index==len(dict.fromkeys(attempts))-1:raise failure('TOKEN_UNREADABLE',error) from None
 raise failure('TOKEN_PATH',detail='DIRECTORY_UNSUPPORTED')
def descriptor(path,create=False):
 import tmdb_token61 as tokens
 suffix='/addon_data/plugin.video.xtreammate/'+tokens.NAME
 if not isinstance(path,str) or not path.endswith(suffix):return None
 if path!=tokens.location():
  if create:raise failure('TOKEN_CHANGED',detail='PROFILE_CHANGED')
  return None
 anchor=path[:-len(suffix)]
 if not os.path.isabs(anchor) or anchor=='/' or '..' in anchor.split('/'):raise failure('TOKEN_PATH',detail='UNSAFE_PATH')
 # location() canonicalizes only Kodi's authoritative profile anchor.
 # Upstream mount aliases belong to Kodi; private descendants never do.
 fd=None
 try:
  fd=_directory(anchor)
  for child in ('addon_data','plugin.video.xtreammate'):
   if create:
    try:os.mkdir(child,0o700,dir_fd=fd)
    except FileExistsError:pass
   try:nxt=_directory(child,dir_fd=fd)
   except tokens.TokenError as error:
    if error.errno==errno.ENOENT:raise FileNotFoundError(errno.ENOENT,'private parent absent') from None
    raise
   os.close(fd);fd=nxt
  if tokens.location()!=path:raise failure('TOKEN_CHANGED',detail='PROFILE_CHANGED')
  result=fd;fd=None
  return result,tokens.NAME
 except FileNotFoundError:raise
 except OSError as error:raise failure('TOKEN_WRITE' if create else 'TOKEN_UNREADABLE',error) from None
 finally:
  if fd is not None:os.close(fd)
def identity(info):return (info.st_dev,info.st_ino,info.st_mode,info.st_size,info.st_mtime_ns)
def recovery_state(path):
 import tmdb_token61 as tokens
 selected=descriptor(path)
 if selected is None:return None
 fd,name=selected
 try:
  info=os.stat(name,dir_fd=fd,follow_symlinks=False)
  return identity(info) if stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode) else None
 except OSError:return None
 finally:os.close(fd)
def quarantine(path,expected):
 import tmdb_token61 as tokens
 selected=descriptor(path)
 if selected is None:raise failure('TOKEN_PATH',detail='UNSAFE_PATH')
 fd,name=selected;backup='.tmdb-preserved65-'+uuid.uuid4().hex
 try:
  if tokens.location()!=path or identity(os.stat(name,dir_fd=fd,follow_symlinks=False))!=expected:raise failure('TOKEN_CHANGED',detail='RECOVERY_CHANGED')
  try:os.stat(backup,dir_fd=fd,follow_symlinks=False)
  except FileNotFoundError:pass
  else:raise failure('TOKEN_CHANGED',detail='RECOVERY_CHANGED')
  os.rename(name,backup,src_dir_fd=fd,dst_dir_fd=fd)
  if identity(os.stat(backup,dir_fd=fd,follow_symlinks=False))!=expected:raise failure('TOKEN_CHANGED',detail='RECOVERY_CHANGED')
  # The old entry is preserved, including symlinks without following targets.
  # No archive cleanup or automatic deletion. New import still compares None.
 finally:os.close(fd)
def pre_read(tokens,path,dialog,gui):
 from token_write64 import read_destination,note
 from localization import tr
 try:return read_destination(tokens,path,initialize=True)
 except tokens.TokenError as original:
  try:expected=recovery_state(path)
  except tokens.TokenError:raise original
  if expected is None:raise
  if not dialog.yesno(tr(36620),tr(36700),defaultbutton=getattr(gui,'DLG_YESNO_NO_BTN',10)):
   raise Cancelled65()
  try:quarantine(path,expected)
  except OSError as error:
   failed=failure('TOKEN_WRITE',error);failed.stage='PRIVATE_DESTINATION_READ';raise failed from None
  note('PRIVATE_DESTINATION_READ','OK',subcode='NONE')
  return read_destination(tokens,path,initialize=True)
