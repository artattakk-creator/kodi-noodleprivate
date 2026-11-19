"""Reminder-only reentrant lease; never monopolizes the portal profile lock."""
import contextlib,hashlib,os,threading,time
_guard=threading.RLock();_local=threading.local();_last=0
@contextlib.contextmanager
def writing(timeout=.2):
 start=time.monotonic()
 if not _guard.acquire(timeout=timeout):raise TimeoutError('reminder write busy')
 fd=None
 try:
  if getattr(_local,'depth',0):
   _local.depth+=1
   try:yield
   finally:_local.depth-=1
   return
  import fcntl
  from utils import addon_data_dir
  fd=os.open(os.path.join(addon_data_dir(),'.xcmate-reminders95.lock'),os.O_CREAT|os.O_RDWR|getattr(os,'O_NOFOLLOW',0),0o600)
  end=start+timeout
  while True:
   try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);break
   except BlockingIOError:
    if time.monotonic()>=end:raise TimeoutError('reminder write busy')
    time.sleep(.005)
  acquired=time.monotonic();_local.depth=1
  try:yield
  finally:
   _local.depth=0
   __import__('profile_transaction').observe95('REMINDER_LOCK',acquired-start,time.monotonic()-acquired)
 finally:
  if fd is not None:os.close(fd)
  _guard.release()
