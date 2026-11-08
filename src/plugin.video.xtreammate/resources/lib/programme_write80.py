"""One owned programme-DB writer per file across threads/interpreters.

Nonblocking admission defers optional metadata to its existing retry lane.
SQLite connections/transactions keep their normal API; read handles do not
take this lease. Kodi video databases and guide files are never targets.
"""
import os,sqlite3,time
try:import fcntl
except ImportError:fcntl=None

class Connection(sqlite3.Connection):
 def close(self):
  lease=getattr(self,'_lease80',None)
  try:super().close()
  finally:
   if lease is not None:self._lease80=None;os.close(lease)

def connect(filename,timeout=.05):
 # Preserve the original bounded SQLite admission on non-POSIX Kodi hosts.
 if fcntl is None:return sqlite3.connect(filename,timeout=timeout)
 flags=os.O_CREAT|os.O_RDWR|getattr(os,'O_NOFOLLOW',0)
 lease=os.open(filename+'.writer80.lock',flags,0o600)
 try:
  try:fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:
   from programme_writes69 import Deferred
   raise Deferred('SQLITE_BUSY_LOCKED',time.time()+1)
  db=sqlite3.connect(filename,timeout=timeout,factory=Connection);db._lease80=lease
  return db
 except BaseException:os.close(lease);raise
