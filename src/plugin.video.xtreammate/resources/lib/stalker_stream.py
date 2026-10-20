"""Stream Stalker js.data arrays without buffering an entire provider page."""
import json
from streaming_json import iter_array


class ArrayReader:
    def __init__(self,stream,cancel=lambda:False):
        self.stream,self.cancel=stream,cancel;self.buffer=b'';self.pos=0
        self.prefix=bytearray();braces=0;quoted=escaped=False
        while True:
            c=self.byte()
            if c is None: raise ValueError('missing provider array')
            if not quoted and c==91: break
            self.prefix.append(c)
            if len(self.prefix)>65536: raise ValueError('provider header budget exceeded')
            if quoted:
                if escaped: escaped=False
                elif c==92: escaped=True
                elif c==34: quoted=False
            elif c==34: quoted=True
            elif c==123: braces+=1
            elif c==125: braces-=1
        shape=json.loads(bytes(self.prefix)+b'[]'+b'}'*braces)
        js=shape.get('js',shape) if isinstance(shape,dict) else shape
        if not (isinstance(js,list) or isinstance(js,dict) and isinstance(js.get('data'),list)):
            raise ValueError('unsupported provider envelope')
        self.started=False;self.depth=1;self.quoted=False;self.escaped=False;self.metadata=None

    def byte(self):
        if self.pos>=len(self.buffer):
            if self.cancel(): raise InterruptedError('provider cancelled')
            self.buffer=self.stream.read(32768);self.pos=0
            if not self.buffer: return None
        value=self.buffer[self.pos];self.pos+=1;return value

    def read(self,n):
        if n<0 or n>65536: raise ValueError('unbounded provider read')
        if not n or not self.depth: return b''
        out=bytearray()
        if not self.started: out.append(91);self.started=True
        while len(out)<n and self.depth:
            c=self.byte()
            if c is None: raise ValueError('truncated provider array')
            out.append(c)
            if self.quoted:
                if self.escaped: self.escaped=False
                elif c==92: self.escaped=True
                elif c==34: self.quoted=False
            elif c==34: self.quoted=True
            elif c==91: self.depth+=1
            elif c==93: self.depth-=1
        if not self.depth:
            tail=bytearray(self.buffer[self.pos:]);self.pos=len(self.buffer)
            while True:
                if self.cancel(): raise InterruptedError('provider cancelled')
                raw=self.stream.read(32768)
                if not raw: break
                tail.extend(raw)
                if len(tail)>65536: raise ValueError('provider trailer budget exceeded')
            if len(tail)>65536: raise ValueError('provider trailer budget exceeded')
            document=json.loads(bytes(self.prefix)+b'[]'+bytes(tail))
            self.metadata=document.get('js',document) if isinstance(document,dict) else {}
        return bytes(out)


def page(stream,cancel=lambda:False):
    reader=ArrayReader(stream,cancel)
    yield from iter_array(reader,cancel)
