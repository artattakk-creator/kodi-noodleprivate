"""Explicit event bookmarks only; no mutation of guide/account databases."""
import hashlib,json,os,tempfile

def remember(pid,sid,event):
    from utils import addon_data_dir
    path=os.path.join(addon_data_dir(),'guide_bookmarks_v1.json')
    try:
        with open(path,encoding='utf-8') as stream:values=json.load(stream)
        if not isinstance(values,dict):raise ValueError('bookmark state')
    except FileNotFoundError:values={}
    ident=hashlib.sha256(json.dumps([str(pid),str(sid),int(event['start']),int(event['stop'])]).encode()).hexdigest()
    values[ident]=dict(pid=str(pid),sid=str(sid),start=int(event['start']),stop=int(event['stop']),title=str(event['title'])[:512])
    fd,tmp=tempfile.mkstemp(prefix='.guide-bookmarks-',dir=addon_data_dir())
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as stream:json.dump(values,stream);stream.flush();os.fsync(stream.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)


def entries(pid):
    from utils import addon_data_dir
    try:
        with open(os.path.join(addon_data_dir(),'guide_bookmarks_v1.json'),encoding='utf-8') as stream:values=json.load(stream)
        return sorted((v for v in values.values() if v.get('pid')==str(pid)),key=lambda v:v['start'])
    except FileNotFoundError:return []
