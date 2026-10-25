"""Optional verified descriptive metadata COPY. Local index remains authoritative.

No physical payload offload is claimed: safely reducing SQLite payloads and
its measured space gain are BLOCKED pending a dedicated recovery migration.
"""
import hashlib
import json
import os
import re
import tempfile
from artwork_vfs import StorageFailure

MAX_METADATA=2*1024*1024
FIELDS=frozenset(('name','title','plot','description','year','genre','rating','cast','director','duration','duration_secs',
                 'season','season_number','episode','episode_num','episode_number','releaseDate','release_date','air_date',
                 'episodes','seasons','info','series_info'))


def portable(value,depth=0):
    if depth>8:raise StorageFailure('METADATA_LIMIT')
    if isinstance(value,dict):return {key:portable(item,depth+1) for key,item in value.items() if key in FIELDS or key.isdigit() and len(key)<=6}
    if isinstance(value,list):
        if len(value)>20000:raise StorageFailure('METADATA_LIMIT')
        return [portable(item,depth+1) for item in value]
    if isinstance(value,str):
        # Descriptive text is retained; embedded private network/file URLs are
        # never exported as an accidental credential or provider URL manifest.
        value=re.sub(r'(?i)(?:https?://|smb://|file://|special://)\S+','[URL REDACTED]',value)
        return value
    return value if value is None or isinstance(value,(int,float,bool)) else None


def _paths():
    from artwork_config import read
    from artwork_vfs import backend_for
    value=read()
    if value['mode']!='external':raise StorageFailure('METADATA_TARGET_REQUIRED')
    image=backend_for(value['target'],value['profile'])
    if image.availability()!='AVAILABLE':raise StorageFailure('STORAGE_OFFLINE')
    return value,value['target']+'/XCMate/Metadata/'+value['profile'],image


def _write(filename,data,image):
    digest=hashlib.sha256(data).hexdigest()
    if image.kind=='KODI_VFS':
        import xbmcvfs
        folder=filename.rsplit('/',1)[0]+'/'
        if not xbmcvfs.mkdirs(folder) and not xbmcvfs.exists(folder):raise StorageFailure('TARGET_WRITE_FAILED')
        image._write(filename,data)
        if image._read(filename,MAX_METADATA+1)!=data:raise StorageFailure('METADATA_VERIFY_FAILED')
        image._write(filename+'.ok',digest.encode())
    else:
        folder=os.path.dirname(filename)
        if os.path.realpath(folder)!=folder:raise StorageFailure('TARGET_SYMLINK')
        os.makedirs(folder,exist_ok=True)
        if os.path.islink(filename) or os.path.islink(filename+'.ok'):raise StorageFailure('TARGET_SYMLINK')
        fd,temp=tempfile.mkstemp(prefix='.metadata-',dir=folder)
        try:
            with os.fdopen(fd,'wb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
            with open(temp,'rb') as stream:readback=stream.read(MAX_METADATA+1)
            if readback!=data:raise StorageFailure('METADATA_VERIFY_FAILED')
            os.replace(temp,filename);temp=''
            with open(filename+'.ok','wb') as stream:stream.write(digest.encode());stream.flush();os.fsync(stream.fileno())
        finally:
            if temp:
                try:os.unlink(temp)
                except OSError:pass


def key(pid,kind,sid):return hashlib.sha256(json.dumps([str(pid),kind,str(sid)]).encode()).hexdigest()


def read_item(pid,kind,sid):
    """Worker-only optional read. Offline/corrupt copies never replace local data."""
    try:
        config,root,image=_paths();filename=root+'/'+key(pid,kind,sid)+'.json'
        if image.kind=='KODI_VFS':data=image._read(filename,MAX_METADATA+1);digest=image._read(filename+'.ok',128).decode()
        else:
            with open(filename,'rb') as stream:data=stream.read(MAX_METADATA+1)
            with open(filename+'.ok',encoding='ascii') as stream:digest=stream.read(128)
        if len(data)>MAX_METADATA or hashlib.sha256(data).hexdigest()!=digest:return {}
        value=json.loads(data)
        return value['payload'] if value.get('version')==1 else {}
    except (OSError,ValueError,UnicodeError,KeyError,TypeError):return {}


def export(cancel=lambda:False,progress=lambda **kw:None):
    from artwork_gate import writer
    from library_index import Reader
    from portals import get_active
    with writer():
        config,root,image=_paths();count=0;size=0
        for portal in get_active():
            reader=Reader(portal['id'])
            for kind in ('vod','series'):
                offset=0
                while not cancel():
                    rows,total=reader.page(kind,offset=offset,limit=128)
                    if not rows:break
                    for row in rows:
                        if cancel():return dict(files=count,bytes=size,physical_offload='BLOCKED')
                        payload=portable(row)
                        # Include only already cached series info; never warm
                        # all provider detail endpoints from the export UI.
                        if kind=='series' and portal.get('type')=='xtream':
                            from xtream import XtreamClient
                            client=XtreamClient(portal['xc_host'],portal['xc_user'],portal['xc_pass'])
                            info=client._get_json('get_series_info',extra={'series_id':row['sid']},cached_only=True) or {}
                            payload.update(portable(info))
                        data=json.dumps(dict(version=1,kind=kind,payload=payload),ensure_ascii=False).encode()
                        if len(data)>MAX_METADATA:raise StorageFailure('METADATA_LIMIT')
                        _write(root+'/'+key(portal['id'],kind,row['sid'])+'.json',data,image)
                        count+=1;size+=len(data)
                        if count%16==0:progress(stage='METADATA_COPY',done=count,done_bytes=size)
                    offset+=len(rows)
                    if offset>=total:break
        return dict(files=count,bytes=size,physical_offload='BLOCKED',local_index='UNCHANGED')
