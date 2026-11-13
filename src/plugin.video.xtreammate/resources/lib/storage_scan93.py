"""Resumable read-only class traversal. A budget exhaustion never means empty."""
import os,time,threading,stat
from pathlib import Path

class Scan:
    def __init__(self,path):
        self.todo=[Path(path)];self.iterator=None;self.files=self.bytes=self.allocated=0
        self.errors=0;self.status='PENDING';self.started=time.monotonic()
    def close(self):
        if self.iterator is not None:self.iterator.close();self.iterator=None
    def step(self,deadline,maximum=100000):
        try:
            while self.todo or self.iterator is not None:
                if time.monotonic()>=deadline or self.files>=maximum:break
                if self.iterator is not None:
                    try:entry=next(self.iterator)
                    except StopIteration:self.close();continue
                    if not entry.is_symlink():
                        if len(self.todo)>=maximum:self.status='ENTRY_LIMIT';break
                        self.todo.append(Path(entry.path))
                    continue
                current=self.todo.pop()
                try:
                    st=current.lstat()
                    if stat.S_ISLNK(st.st_mode):continue
                    if stat.S_ISDIR(st.st_mode):self.iterator=os.scandir(current)
                    elif stat.S_ISREG(st.st_mode):
                        self.files+=1;self.bytes+=st.st_size
                        self.allocated+=getattr(st,'st_blocks',(st.st_size+511)//512)*512
                except FileNotFoundError:pass
                except OSError:self.errors+=1
        except OSError:self.errors+=1;self.close()
        done=not self.todo and self.iterator is None
        self.status='UNREADABLE' if self.errors else 'COMPLETE' if done else 'PARTIAL'
        return dict(files=self.files,bytes=self.bytes,allocated_bytes=self.allocated,
                    complete=done and not self.errors,scan_status=self.status,
                    measurement_seconds=round(time.monotonic()-self.started,3))

_scans={}
_lock=threading.Lock()
def step(path,seconds):
    with _lock:return _step(path,seconds)

def _step(path,seconds):
    key=str(path);now=time.monotonic();saved=_scans.get(key)
    if saved is None or now-saved.started>60 or saved.status=='COMPLETE':
        if saved:saved.close()
        saved=_scans[key]=Scan(path)
    while len(_scans)>64:
        first=next(iter(_scans));_scans.pop(first).close()
    return saved.step(now+max(.001,seconds))
