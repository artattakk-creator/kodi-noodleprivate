"""Atomic full-group publication using bounded pages, never one giant EPG DTO.

Immutable content-addressed pages keep concurrent old readers consistent.
Each page verifies generation/hash. The old manifest stays active until every
new page is written. Only obsolete private publication metadata is reaped.
"""
import hashlib,json,os,sqlite3,tempfile,time
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


from home_publication74 import serialized

@serialized
def publish(portal,rows,approved):
    from widget_refresh45 import path,trace,_art_cursor46,MAX_BYTES
    from widget_data41 import policy
    from programme_urls55 import enqueue
    from home_publication74 import old_frame,merge,signature,note,source_refs,art_status
    from epg_status import revision as epg_revision
    filename=path(portal['id'],'live')
    from import_budget import check_space
    try:
        old=old_frame(portal,'live');all_items=[];records=[]
        cursor=_art_cursor46.get(str(portal['id']),0)%max(1,len(rows))
        wanted={(cursor+i)%len(rows) for i in range(min(16,len(rows)))} if rows else set()
        from widget_render47 import values as render
        for offset in range(0,len(rows),16):
            for index,value in enumerate(render(portal,'live',rows[offset:offset+16],approved)):
                event=value.pop('_programme46',None)
                if event and offset+index in wanted:enqueue(event)
                if event:records.append(event)
                all_items.append(value)
        all_items,revision=merge(portal,'live',all_items,rows,old)
        digest=signature(all_items,'live')
        if old and old.get('signature')==digest and old.get('source_revision74')==revision and time.time()-old.get('at',0)<300:
            trace('UNCHANGED','live',len(all_items));return True
        if len(json.dumps(all_items).encode())>MAX_BYTES:trace('BAD_FRAME','live');return False
        check_space(filename,MAX_PAGE*2)
        frame=dict(pid=str(portal['id']),kind='live',policy=policy(portal,'live'),at=time.time(),
            generation46=digest,pages46=[],count46=len(all_items),signature=digest,
            source_revision74=revision,epg_revision74=epg_revision(portal['id']),immutable74=True,source_refs74=source_refs(rows),art_status74=art_status(all_items))
        for offset in range(0,len(all_items),16):
            items=all_items[offset:offset+16]
            data=json.dumps(dict(generation46=digest,items=items)).encode()
            if len(data)>MAX_PAGE:trace('BAD_FRAME','live');return False
            page_hash=hashlib.sha256(data).hexdigest()
            name=os.path.basename(filename)+'.page46-74-'+page_hash+'.json'
            target=os.path.join(os.path.dirname(filename),name)
            if not os.path.isfile(target):atomic(target,data)
            frame['pages46'].append(dict(name=name,count=len(items),sha256=page_hash))
        data=json.dumps(frame).encode()
        if len(data)>256*1024:trace('BAD_FRAME','live');return False
        atomic(filename,data);_art_cursor46[str(portal['id'])]=(cursor+16)%max(1,len(rows))
        # Optional metadata mirrors follow publication; their lock failure must
        # not turn a valid immutable display frame into a failed publication.
        try:
            from programme_index46 import publish as publish_records
            from programme_assets47 import channels
            for offset in range(0,len(records),64):
                publish_records(records[offset:offset+64],include_art=False)
                channels(portal,records[offset:offset+64])
        except (OSError,ValueError,RuntimeError,sqlite3.Error):pass
        from widget_notice46 import prepare
        prepare(portal,'live',digest,len(all_items));note(portal,'live','COMMIT',old,len(all_items),revision,digest,frame['art_status74'])
        trace('PUBLISHED','live',len(all_items))
        # Reap only our immutable publication metadata beyond two hours. A
        # readable manifest expires after ten minutes; current pages are pinned.
        # Images, old .46 slots, databases and every user file are untouched.
        keep={p['name'] for p in frame['pages46']}
        from pathlib import Path
        for page in Path(filename).parent.glob(Path(filename).name+'.page46-74-*.json'):
            if page.name not in keep and not page.is_symlink() and time.time()-page.stat().st_mtime>7200:page.unlink()
        return True
    except (OSError,ValueError,TypeError):trace('READ_ERROR','live');return False
