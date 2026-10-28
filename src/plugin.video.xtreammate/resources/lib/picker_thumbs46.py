"""One cancellable thumbnail lane per picker; two lanes globally, 24 results.

Only validated reduced local PNGs reach Kodi. No provider URI in XML; full
originals are downloaded/validated separately for explicit Preview and Save.
"""
import hashlib,io,os,queue,threading
_slots=threading.BoundedSemaphore(2)


def key(row):return hashlib.sha256((str(row.get('source',''))+'|'+str(row.get('url',''))+'|'+str(row.get('role',''))).encode()).hexdigest()


class Thumbnails:
    def __init__(self,picker):
        self.picker=picker;self.thread=None;self.cancel=threading.Event();self.results=queue.Queue(24)
        self.pending=None;self.generation=0;self.paths={};self.codes={}

    def reset(self,rows):
        self.cancel.set();self.generation+=1;self.paths={};self.codes={}
        self.pending=(self.generation,[dict(r) for r in rows[:24] if (r.get('url') or r.get('local_path48'))])

    def close(self):self.cancel.set();self.pending=None

    def resume(self):
        remaining=[dict(r) for r in self.picker._all_rows46 if (r.get('url') or r.get('local_path48')) and key(r) not in self.paths and key(r) not in self.codes]
        if remaining:self.pending=(self.generation,remaining)

    def pump(self):
        p=self.picker;p._gui()
        while True:
            try:generation,ident,path,code=self.results.get_nowait()
            except queue.Empty:break
            if generation!=self.generation or p._closed:continue
            self.codes[ident]=code
            if path:self.paths[ident]=path
            for pos,row in enumerate(p.rows):
                if key(row)==ident:
                    li=p.getControl(200).getListItem(pos)
                    if path:li.setArt({'thumb':path})
                    li.setProperty('XCMate.Preview46',code)
                    from localization import tr
                    li.setProperty('XCMate.PreviewLabel46',tr(36123) if path else code)
        if self.pending and p.mode=='list' and not p._closed and (self.thread is None or not self.thread.is_alive()):
            if not _slots.acquire(blocking=False):return
            generation,rows=self.pending;self.pending=None;self.cancel=threading.Event()
            self.thread=threading.Thread(target=self._work,args=(generation,rows,self.cancel),name='XCMate-thumbnails46',daemon=True)
            try:self.thread.start()
            except (RuntimeError,MemoryError):_slots.release();self.pending=(generation,rows)

    def _work(self,generation,rows,cancel):
        try:
            for row in rows:
                if cancel.is_set() or self.picker._cancel.is_set():break
                ident=key(row);path='';code='READY'
                try:
                    from media_sources43 import get,validate_image,SourceError
                    from PIL import Image
                    if row.get('local_path48'):
                        from media_preview48 import local_bytes
                        data=local_bytes(self.picker.pid,row['local_path48'])
                    else:data=get(row['url'],cancel=cancel.is_set)
                    validate_image(data)
                    with Image.open(io.BytesIO(data)) as image:
                        image.thumbnail((320,480));buffer=io.BytesIO();image.convert('RGBA').save(buffer,'PNG');thumb=buffer.getvalue()
                    with self.picker._io_lock:
                        if cancel.is_set() or self.picker._cancel.is_set():break
                        from import_budget import check_space
                        path=os.path.join(self.picker._temp.name,'thumb46-'+ident+'.png');check_space(path,len(thumb))
                        with open(path,'wb') as f:f.write(thumb)
                except Exception as exc:
                    code=getattr(exc,'code','THUMBNAIL_FAILED');path=''
                    if code not in ('CANCELLED','RESEARCH_BUSY'):
                        from picker_status44 import mark
                        mark('ERROR',row.get('source',''),code)
                try:self.results.put_nowait((generation,ident,path,code))
                except queue.Full:break
        finally:_slots.release()
