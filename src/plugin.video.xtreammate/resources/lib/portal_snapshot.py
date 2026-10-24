"""One versioned profile snapshot per interpreter, detached mutable API copies."""
import copy,os,stat,threading,time


class PortalReadError(RuntimeError):pass


class Snapshot:
    def __init__(self):
        self.lock=threading.RLock();self.key=None;self.value=None;self.retry=0;self.failures=0

    def invalidate(self):
        with self.lock:self.key=None;self.value=None;self.retry=0;self.failures=0

    @staticmethod
    def version(path):
        try:s=os.stat(path)
        except FileNotFoundError:
            if os.path.lexists(path):raise ValueError('Invalid profile file')
            return (path,None)
        return (path,s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)

    def read(self,path,types,select=lambda rows:rows):
        from boot_diagnostics import phase
        from profile_transaction import reading
        from service_runtime import portal_call,portal_read,portal_failure,note_pressure
        portal_call()
        with self.lock,reading():
            key=self.version(path)
            if key!=self.key:self.value=None;self.retry=0;self.failures=0;self.key=key
            if time.monotonic()<self.retry:raise PortalReadError('Portale: Speicherpause aktiv. Bitte kurz warten und erneut öffnen.')
            try:
                if self.value is None:
                    with phase('PORTALS_LOAD'):
                        for attempt in range(2):
                            key=self.version(path)
                            if key[1] is None:self.value=[];self.key=key;break
                            fd=os.open(path,os.O_RDONLY|getattr(os,'O_NONBLOCK',0))
                            with os.fdopen(fd,'rb') as stream:
                                actual=os.fstat(stream.fileno())
                                if not stat.S_ISREG(actual.st_mode):raise ValueError('Not a regular profile')
                                if actual.st_size>4*1024*1024:raise ValueError('Profile budget')
                                raw=stream.read(4*1024*1024+1)
                            if len(raw)>4*1024*1024:raise ValueError('Profile budget')
                            import json
                            value=json.loads(raw)
                            if not isinstance(value,list) or any(not isinstance(p,dict) or not isinstance(p.get('id'),str) or not p['id'] or p.get('type') not in types for p in value):raise ValueError('Invalid profile')
                            if self.version(path)!=key:continue
                            self.key=key;self.value=value;portal_read(len(raw));break
                        else:raise PortalReadError('Portale wurden gleichzeitig geändert. Bitte erneut öffnen.')
                # Never expose cached credentials/groups to mutable callers.
                result=copy.deepcopy(select(self.value));self.failures=0;self.retry=0
                return result
            except MemoryError:
                self.value=None;self.failures=min(5,self.failures+1);self.retry=time.monotonic()+min(30,2**self.failures)
                portal_failure('OOM');note_pressure()
                raise PortalReadError('Portale konnten wegen Speicherknappheit nicht gelesen werden. Daten unverändert; kurz warten und erneut öffnen.') from None
            except Exception:
                self.value=None;portal_failure('READ_ERROR')
                raise
