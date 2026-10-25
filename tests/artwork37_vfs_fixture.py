"""Kodi VFS adapter model backed by real independent fixture files, not SMB hardware."""
from pathlib import Path
import shutil
import types
from urllib.parse import urlsplit


class VFS:
    def __init__(self,root):self.root=Path(root);self.online=True;self.short_copy=False;self.calls=[]
    def path(self,uri):
        if not self.online:raise OSError('fixture offline')
        p=urlsplit(str(uri))
        if p.scheme!='smb':raise AssertionError('unexpected VFS target')
        path=self.root/p.netloc/p.path.lstrip('/');self.calls.append(p.scheme)
        return path
    def exists(self,uri):return self.path(uri).exists()
    def mkdirs(self,uri):self.path(uri).mkdir(parents=True,exist_ok=True);return True
    def listdir(self,uri):
        entries=list(self.path(uri).iterdir());return [p.name for p in entries if p.is_dir()],[p.name for p in entries if p.is_file()]
    def delete(self,uri):self.path(uri).unlink();return True
    def copy(self,a,b):
        source=self.path(a);target=self.path(b)
        if self.short_copy:target.write_bytes(source.read_bytes()[:10])
        else:shutil.copyfile(source,target)
        return True
    def File(self,uri,mode='r'):
        stream=self.path(uri).open('wb' if mode=='w' else 'rb')
        class Handle:
            def readBytes(self,n):return stream.read(n)
            def write(self,data):return stream.write(data)
            def close(self):stream.close()
        return Handle()
