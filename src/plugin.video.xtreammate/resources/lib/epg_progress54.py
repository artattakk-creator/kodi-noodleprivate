"""Bounded real I/O/parser/write observations; never a synthetic heartbeat."""
import time

class Progress:
    def __init__(self,callback):self.callback=callback;self.last=0;self.phase='';self.values=dict(bytes=0,programmes=0,channels=0,stored=0)
    def emit(self,phase,force=False,**counts):
        self.values.update(counts)
        if self.callback is None:return
        now=time.monotonic()
        if force or not self.phase or now-self.last>=.25:
            self.phase=phase;self.last=now;self.callback(dict(self.values,phase=phase))
    def parsed(self,counts):self.emit('PARSE',programmes=counts['programmes'],channels=counts['channels'])
    def wrap(self,stream):
        progress=self
        class Reader:
            def read(self,size=-1):
                value=stream.read(size)
                if value:progress.emit('DOWNLOAD',bytes=progress.values['bytes']+len(value))
                return value
        return Reader()
