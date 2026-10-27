"""Owned, optional artwork/metadata dialog. Network/validation/Save use one worker.

Parent requests this from a callback; open_pending is called later by its owner
pump. No Container.Update, player operation, foreign dialog close or skin patch.
"""
from concurrent.futures import Future
import os,tempfile,threading,time
import xbmc,xbmcgui,xbmcaddon
from localization import tr
_research_slots=threading.BoundedSemaphore(2)


def request(parent):
    if parent.mode=='detail' and parent.selected and parent.kind in ('vod','series'):
        parent._picker_requested43=(str(parent.portal['id']),parent.kind,str(parent.selected['sid']))


def open_pending(parent):
    wanted=getattr(parent,'_picker_requested43',None)
    if not wanted:return
    parent._picker_requested43=None
    if parent._closed or parent._leaving or parent._playback_waiting or parent.mode!='detail':return
    if wanted!=(str(parent.portal['id']),parent.kind,str(parent.selected['sid'])):return
    dialog=int(xbmcgui.getCurrentWindowDialogId())
    if dialog not in (0,9999,getattr(parent,'_native_dialog_id',None)):return
    picker=ArtworkPicker('XCMateArtwork43.xml',xbmcaddon.Addon().getAddonInfo('path'),'Default','720p')
    picker.configure(parent)
    changed=picker.run()
    if not changed or parent._closed or parent.mode!='detail' or wanted!=(str(parent.portal['id']),parent.kind,str(parent.selected['sid'])):return
    item=dict(parent.selected)
    def load():
        from media_overrides43 import apply_many
        return apply_many(wanted[0],[item])[0]
    def ready(item):
        parent._detail_ready((item,{'episodes':parent._episode_raw()}));parent._refresh_art()
    parent._request(load,ready)


class ArtworkPicker(xbmcgui.WindowXMLDialog):
    def configure(self,parent):
        self.parent=parent;self.pid=str(parent.portal['id']);self.kind=parent.kind
        self.record=dict(parent.selected);self.sid=str(self.record['sid'])
        self._owner=threading.get_ident();self._closed=False;self._ready=False
        self._cancel=threading.Event();self._io_lock=threading.Lock()
        self._temp=tempfile.TemporaryDirectory(prefix='xcmate-choice43-')
        self._future=None;self._apply=None;self._generation=0
        self._stage_paths=[]
        self.rows=[];self.selected=None;self.preview=None;self.image=None
        self.mode='list';self.role='poster';self.armed=False;self.changed=False
        self.query=str(self.record.get('name',''))[:200]

    def _gui(self):
        if threading.get_ident()!=self._owner:raise RuntimeError('CHOICE_OWNER_THREAD')

    def _status(self,text):self.getControl(103).setLabel(str(text)[:512])

    def _stage(self,data):
        from hashlib import sha256
        with self._io_lock:
            if self._cancel.is_set():return None
            path=os.path.join(self._temp.name,sha256(data).hexdigest()+'.img')
            if path not in self._stage_paths:
                from import_budget import check_space
                check_space(path,len(data))
                with open(path,'wb') as f:f.write(data)
                self._stage_paths.append(path)
                while len(self._stage_paths)>8:
                    old=self._stage_paths.pop(0)
                    if os.path.isfile(old):os.unlink(old)  # Own temporary preview, never archive/source.
            return path

    def _submit(self,fn,apply):
        self._gui()
        if self._future is not None:
            self._status(tr(35905));return
        if not _research_slots.acquire(blocking=False):self._status(tr(35906,'RESEARCH_BUSY'));return
        future=Future();self._future=future;self._apply=apply
        def work():
            try:
                if not future.set_running_or_notify_cancel():return
                try:value=fn()
                except Exception as exc:future.set_exception(exc)
                else:future.set_result(value)
            finally:_research_slots.release()
        # No unbounded queue; a cancelled DNS call cannot create more workers.
        try:threading.Thread(target=work,name='XCMate-choice43',daemon=True).start()
        except (RuntimeError,MemoryError):
            _research_slots.release();future.cancel();self._future=self._apply=None;self._status(tr(35906,'WORKER_UNAVAILABLE'));return
        self._status(tr(35905))

    def pump(self):
        self._gui()
        if self._closed:return
        future=self._future
        if future is not None and future.done():
            apply=self._apply;self._future=self._apply=None
            if future.cancelled():return
            try:value=future.result()
            except Exception as exc:
                from media_sources43 import SourceError
                from art_storage import ArtworkFailure
                code=exc.code if isinstance(exc,SourceError) else (exc.code+(':'+exc.reason if exc.reason else '')) if isinstance(exc,ArtworkFailure) else 'SAVE_FAILED' if isinstance(exc,OSError) else 'UNAVAILABLE'
                self._status(tr(35935) if code=='IMAGE_DECODER_MISSING' else tr(35906,code))
            else:apply(value)

    def run(self):
        self._gui();monitor=xbmc.Monitor();started=time.monotonic()
        try:
            self.show()
            while not self._closed and not self.parent._closed:
                if self._ready:self.pump()
                elif time.monotonic()-started>10:break
                if monitor.waitForAbort(.05):break
        finally:self.close()
        return self.changed

    def onInit(self):
        self._gui();self._ready=True
        for cid,label in ((401,35900),(402,35901),(403,35902),(404,35903),(405,35904),
                          (501,35910),(502,35911),(503,35912),(504,35913),(505,35914),(506,35915),(507,35916),(508,35917)):
            self.getControl(cid).setLabel(tr(label))
        self.getControl(101).setLabel(tr(35918));self.getControl(102).setLabel(self.query)
        self._show_list();self.setFocusId(401);self._source('provider')

    def _show_list(self):
        self.mode='list';self.armed=False
        self.getControl(200).setVisible(True);self.getControl(600).setVisible(False)
        for cid in range(501,509):self.getControl(cid).setVisible(False)
        self.getControl(300).setVisible(False);self.getControl(301).setVisible(False)
        self._navigation()

    def _navigation(self):
        # Wire only visible buttons; Kodi XML neighbors can otherwise strand
        # an IR remote on the hidden Save/reset buttons.
        buttons=[cid for cid in range(501,509) if self.getControl(cid).isVisible()]
        target=buttons[0] if buttons else 200
        for cid in range(401,406):
            self.getControl(cid).setNavigation(self.getControl(cid),self.getControl(target),
                self.getControl(405 if cid==401 else cid-1),self.getControl(401 if cid==405 else cid+1))
        for i,cid in enumerate(buttons):
            previous=buttons[i-1] if i else 401
            following=buttons[i+1] if i+1<len(buttons) else buttons[0]
            self.getControl(cid).setNavigation(self.getControl(previous),self.getControl(following),
                self.getControl(previous),self.getControl(following))

    def _source(self,source):
        if self._future is not None:return
        self._show_list()
        from media_sources43 import provider,tmdb,commons
        if source!='provider':
            query=xbmcgui.Dialog().input(tr(35919),defaultt=self.query)
            if not query.strip():return
            self.query=query.strip()[:200];self.getControl(102).setLabel(self.query)
        person=False
        if source=='tmdb':
            choice=xbmcgui.Dialog().select(tr(35920),[tr(35921),tr(35922)])
            if choice not in (0,1):return
            person=choice==1
        item=dict(self.record.get('_provider43',self.record))
        def query():
            if source=='provider':
                from media_data import details
                from metadata_views import enrich
                try:
                    data=details(self.parent.router._xc(self.parent.portal),self.kind,self.sid,refresh=True)
                    combined=enrich(item,data)
                    for key in ('sid','kind','category_id'):
                        if key in item:combined[key]=item[key]
                    return provider(combined)
                except Exception:
                    return dict(rows=provider(item),code='PROVIDER_REFRESH_UNAVAILABLE')
            if source=='tmdb':return tmdb(self.query,self.kind,person,self._cancel.is_set)
            return commons(self.query,self._cancel.is_set)
        self._submit(query,self._results)

    def _results(self,rows):
        code=rows.get('code','') if isinstance(rows,dict) else ''
        rows=rows.get('rows',[]) if isinstance(rows,dict) else rows
        self.rows=rows[:24];control=self.getControl(200);control.reset()
        values=[]
        for row in self.rows:
            li=xbmcgui.ListItem(str(row['name']),label2=str(row['attribution'])[:200])
            # Only already validated local previews become thumbnails. No
            # uncontrolled provider URL is passed into Kodi's texture loader.
            values.append(li)
        control.addItems(values);self._status(tr(35906,code)+' · '+tr(35923,len(values)) if code else tr(35923,len(values)) if values else tr(35924))
        if values:self.setFocusId(200)

    def _preview(self,fetch=True):
        pos=self.getControl(200).getSelectedPosition()
        if not 0<=pos<len(self.rows):return
        candidate=dict(self.rows[pos]);self.selected=candidate;self.role=candidate['role'];self.armed=False
        self.mode='preview';self.getControl(200).setVisible(False)
        for cid in range(501,509):self.getControl(cid).setVisible(True)
        self.getControl(503).setVisible(False);self.getControl(508).setVisible(bool(self.record.get('_metadata_override43')))
        self.getControl(300).setVisible(True);self.getControl(301).setVisible(True)
        self.getControl(301).setText(candidate['name']+'\n'+candidate['attribution']+'\n'+tr(35925))
        self.image=None;self.getControl(300).setImage('');self._navigation();self.setFocusId(501)
        def load():
            from media_sources43 import get,validate_image
            data=get(candidate['url'],cancel=self._cancel.is_set) if candidate.get('url') else None
            if data is None:return None,None
            validate_image(data)
            path=self._stage(data)
            return data,path
        def ready(value):
            if self.mode!='preview' or self.selected!=candidate:return
            self.image,path=value
            if path:
                self.getControl(300).setImage(path,useCache=False)
                self.getControl(200).getListItem(pos).setArt({'thumb':path})
            self._status(tr(35926,self.role))
        if fetch:self._submit(load,ready)

    def _metadata(self):
        if not self.selected or self.selected.get('media_type')=='person':return
        candidate=dict(self.selected)
        def load():
            if candidate['source']=='tmdb':
                from media_sources43 import tmdb_details
                return tmdb_details(candidate,self._cancel.is_set)
            return candidate.get('metadata',{})
        def ready(fields):
            if not fields:self._status(tr(35924));return
            keys=list(fields)
            labels=[key+': '+str(self.record.get(key,'—'))[:80]+' → '+str(fields[key])[:300] for key in keys]
            selected=xbmcgui.Dialog().multiselect(tr(35916),labels,preselect=[])
            if not selected:return
            selected={keys[i]:fields[keys[i]] for i in selected if 0<=i<len(keys)}
            if not selected or not xbmcgui.Dialog().yesno('XCMate',tr(35927)+'\n'+', '.join(selected)):return
            from media_overrides43 import save
            self._submit(lambda:save(self.pid,self.kind,self.sid,metadata=selected,source=candidate['source'],attribution=candidate['attribution'],provenance=self._provenance(candidate)),self._saved)
        self._submit(load,ready)

    def _saved(self,result):
        if result:self.changed=True;self._status(tr(35928));self.close()

    def _provenance(self,candidate):
        from hashlib import sha256
        return dict(media_type=candidate.get('media_type','image'),remote_id=candidate.get('remote_id'),
                    source_fingerprint=sha256(candidate.get('url','').encode()).hexdigest())

    def onClick(self,cid):
        self._gui()
        if cid in (401,402,403):self._source({401:'provider',402:'tmdb',403:'commons'}[cid]);return
        if cid==404:
            if self._future is not None:return
            path=xbmcgui.Dialog().browseSingle(1,tr(35903),'files','.jpg|.jpeg|.png')
            if not path:return
            import xbmcvfs
            path=xbmcvfs.translatePath(path)
            if '://' in path:self._status(tr(35906,'LOCAL_FILE_REQUIRED'));return
            # No source-file deletion, URI workarounds or shared-storage writes.
            self._show_list()
            self.rows=[dict(source='local',url='',name=tr(35903),role='poster',attribution=tr(35929),metadata={})]
            self._results(self.rows);self._preview(fetch=False)
            def local():
                from media_sources43 import MAX_IMAGE,validate_image
                if not os.path.isfile(path) or os.path.islink(path):
                    from media_sources43 import SourceError
                    raise SourceError('LOCAL_FILE_REQUIRED')
                with open(path,'rb') as f:data=f.read(MAX_IMAGE+1)
                validate_image(data)
                dest=self._stage(data)
                return data,dest
            def ready(value):
                self.image,image=value
                if image:self.getControl(300).setImage(image,useCache=False)
                self._status(tr(35926,self.role))
            if self._future is None or self._future.done():self._submit(local,ready)
            return
        if cid==405:self.close();return
        if self._future is not None:return
        if cid==200:self._preview()
        elif cid==501:
            if self.image:self.armed=True;self.getControl(503).setVisible(True);self._navigation();self.setFocusId(503)
        elif cid==502:
            choice=xbmcgui.Dialog().select(tr(35930),[tr(35931),tr(35932),tr(35933)])
            if choice in (0,1,2):self.role=('poster','fanart','replacement')[choice];self.armed=False;self.getControl(503).setVisible(False);self._navigation();self._status(tr(35926,self.role))
        elif cid==503 and self.armed and self.image:
            from media_overrides43 import save
            data=self.image;role=self.role;candidate=dict(self.selected)
            self._submit(lambda:save(self.pid,self.kind,self.sid,image=data,role=role,source=candidate['source'],attribution=candidate['attribution'],provenance=self._provenance(candidate)),self._saved)
        elif cid==504:self._show_list();self.setFocusId(200 if self.rows else 401)
        elif cid in (505,508):
            if xbmcgui.Dialog().yesno('XCMate',tr(35934)):
                from media_overrides43 import reset
                self._submit(lambda:reset(self.pid,self.kind,self.sid,metadata=cid==508),self._saved)
        elif cid==506:self.close()
        elif cid==507:self._metadata()

    def onAction(self,action):
        if action.getId() in (9,10,92):
            if self.mode=='preview' and (self._future is None or self._future.done()):self._show_list();self.setFocusId(200 if self.rows else 401)
            else:self.close()

    def close(self):
        if self._closed:return
        self._closed=True;self._cancel.set()
        if self._future:self._future.cancel()
        def cleanup():
            with self._io_lock:self._temp.cleanup()
        try:threading.Thread(target=cleanup,name='XCMate-choice43-cleanup',daemon=True).start()
        except (RuntimeError,MemoryError):pass  # OS temp cleanup later; never block owner on a worker lock.
        super().close()
