"""Atomic full-group publication using bounded pages, never one giant EPG DTO.

Two private metadata slots are reused without deleting images/databases. A
reader verifies each page's generation/hash; overwritten old pages fail closed.
The old manifest remains active until every new page is completely written.
"""
import hashlib,json,os,tempfile,time
from collections.abc import Sequence
MAX_PAGE=512*1024


def atomic(filename,data):
    fd,temp=tempfile.mkstemp(prefix='.widget-page46-',dir=os.path.dirname(filename))
    try:
        with os.fdopen(fd,'wb') as f:f.write(data)
        os.replace(temp,filename)
    finally:
        if os.path.exists(temp):os.unlink(temp)


class Items(Sequence):
    def __init__(self,filename,manifest):self.filename=filename;self.manifest=manifest
    def __len__(self):return self.manifest['count46']
    def __iter__(self):
        root=os.path.dirname(self.filename)
        for page in self.manifest['pages46']:
            name=page['name']
            if os.path.basename(name)!=name or not name.startswith(os.path.basename(self.filename)+'.page46-'):raise ValueError('PAGE_PATH')
            path=os.path.join(root,name)
            if os.path.islink(path):raise ValueError('PAGE_PATH')
            with open(path,'rb') as f:data=f.read(MAX_PAGE+1)
            if len(data)>MAX_PAGE or hashlib.sha256(data).hexdigest()!=page['sha256']:raise ValueError('PAGE_CHANGED')
            value=json.loads(data)
            if value.get('generation46')!=self.manifest['generation46'] or len(value.get('items',[]))!=page['count']:raise ValueError('PAGE_CHANGED')
            yield from value['items']
    def __getitem__(self,index):
        if isinstance(index,slice):return list(self)[index]
        if index<0:index+=len(self)
        for pos,value in enumerate(self):
            if pos==index:return value
        raise IndexError(index)


def publish(portal,rows,approved):
    import uuid
    from widget_refresh45 import path,trace,_art_cursor46
    from widget_items45 import describe
    from widget_group46 import infos
    from widget_data41 import policy
    from programme_art46 import enqueue
    filename=path(portal['id'],'live');old={}
    try:
        with open(filename,encoding='utf-8') as f:old=json.loads(f.read(256*1024))
    except (OSError,ValueError):pass
    slot=1-int(old.get('slot46',0));generation=uuid.uuid4().hex
    frame=dict(pid=str(portal['id']),kind='live',policy=policy(portal,'live'),at=time.time(),generation46=generation,slot46=slot,pages46=[],count46=len(rows))
    digest=hashlib.sha256();cursor=_art_cursor46.get(str(portal['id']),0)%len(rows)
    wanted={(cursor+i)%len(rows) for i in range(min(16,len(rows)))}
    from import_budget import check_space
    try:
        check_space(filename,MAX_PAGE*2)
        for offset in range(0,len(rows),16):
            batch=rows[offset:offset+16];epg=infos(portal,batch);items=[]
            for index,row in enumerate(batch):
                value=describe(portal,'live',row,approved,epg.get(row['sid']));event=value.pop('_programme46',None)
                if event and offset+index in wanted:enqueue(event)
                items.append(value)
            digest.update(json.dumps(items,sort_keys=True).encode())
            data=json.dumps(dict(generation46=generation,items=items)).encode()
            if len(data)>MAX_PAGE:trace('BAD_FRAME','live');return False
            name=os.path.basename(filename)+'.page46-'+str(slot)+'-'+str(offset//16)+'.json'
            atomic(os.path.join(os.path.dirname(filename),name),data)
            frame['pages46'].append(dict(name=name,count=len(items),sha256=hashlib.sha256(data).hexdigest()))
        frame['signature']=digest.hexdigest();data=json.dumps(frame).encode()
        if len(data)>256*1024:trace('BAD_FRAME','live');return False
        atomic(filename,data);_art_cursor46[str(portal['id'])]=(cursor+16)%len(rows)
        from widget_notice46 import prepare
        prepare(portal,'live',frame['signature'],len(rows));trace('PUBLISHED','live',len(rows));return True
    except (OSError,ValueError,TypeError):trace('READ_ERROR','live');return False
