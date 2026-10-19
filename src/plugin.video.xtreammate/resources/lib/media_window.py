"""Own Kodi WindowXML: real horizontal rail, groups/grid and detail view.

Native XML controls dispatch onClick, unlike programmatic WindowDialog. Data,
metadata and images are prepared by bounded workers; callbacks only use views.
"""
from localization import tr
import json
import os
import queue
import threading
import sqlite3
from concurrent.futures import ThreadPoolExecutor

import xbmc
import xbmcgui
import xbmcaddon

PAGE=24


class MediaWindow(xbmcgui.WindowXML):
    def configure(self,router,portal,kind,sid='',favourites=False):
        self.router,self.portal,self.kind=router,portal,kind
        self.initial_sid=sid
        self.favourites_only=favourites
        self.mode='landing';self.category='';self.offset=0;self.total=0
        self.rows=[];self.groups=[];self.selected=None;self.episodes=[];self.actions=[]
        self._positions={};self._previous=None;self._last_position=0;self._cols=4
        self._ready=False;self._closed=False;self._generation=0
        self._lock=threading.RLock();self._pool=ThreadPoolExecutor(max_workers=2)
        self._art=queue.Queue(maxsize=3)
        self._art_thread=threading.Thread(target=self._art_loop,daemon=True,name='XCMate-art')
        self._art_thread.start()

    def onInit(self):
        self.getControl(400).setLabel(tr(32586))
        self.getControl(501).setLabel(tr(32587))
        if self._ready:
            self._show(self.mode)
            if self.mode=='detail': self._detail_ready((self.selected,{'episodes':self._episode_raw()}))
            elif self.mode=='episodes': self._show_episodes()
            elif self.mode=='seasons':
                self._fill(330,[dict(name=tr(32523)+str(s),sid=str(s)) for s in self.seasons]);self.setFocusId(330)
            else:
                self._fill(200,[dict(name=g['title'],sid=g['cid']) for g in self.groups])
                self._page_ready((self.rows,self.total))
            return
        self._ready=True
        self._show('landing')
        self.getControl(101).setLabel('XCMate · '+(tr(32461) if self.kind=='vod' else tr(32462)))
        self.getControl(120).setLabel((tr(32403) if self.kind=='vod' else tr(32404))+tr(32492))
        self.getControl(102).setLabel(tr(32491))
        self._request(self._initial,self._initial_ready)

    def _request(self,job,apply):
        self._generation+=1;generation=self._generation
        future=self._pool.submit(job)
        def done(result):
            try: value=result.result()
            except Exception as exc:
                with self._lock:
                    if not self._closed and generation==self._generation:
                        self.getControl(102).setLabel(tr(32493)+type(exc).__name__)
                return
            with self._lock:
                if not self._closed and generation==self._generation: apply(value)
        future.add_done_callback(done)

    def _initial(self):
        from library_index import refresh,Reader
        client=self.router._xc(self.portal)
        refresh(self.portal,client)
        reader=Reader(self.portal['id'])
        return reader,reader.groups(self.kind),reader.state(self.kind)

    def _initial_ready(self,value):
        self.reader,self.groups,state=value
        self._catalog_missing=not bool(state)
        self._fill(200,[dict(name=g['title'],sid=g['cid']) for g in self.groups])
        self.category=self.groups[0]['cid'] if self.groups else ''
        if not state:
            self.getControl(102).setLabel(tr(32494))
            self.getControl(120).setLabel(tr(32495))
            self.setFocusId(120)
            return
        self.getControl(120).setLabel((tr(32403) if self.kind=='vod' else tr(32404))+tr(32492))
        if self.initial_sid:
            # Fetching the one ID is local, still on the data worker callback.
            item=self.reader.get(self.kind,self.initial_sid)
            self.initial_sid=''
            if item: self._details(item);return
        self._page('landing',0)

    def _fill(self,control_id,rows):
        from media_art import local_art
        control=self.getControl(control_id);control.reset()
        items=[]
        for row in rows:
            li=xbmcgui.ListItem(str(row.get('name','')))
            li.setArt(local_art(row))
            li.setInfo('video',{'title':str(row.get('name',''))})
            items.append(li)
        control.addItems(items)

    def _page(self,mode,offset=0):
        self.mode=mode;self.offset=max(0,offset)
        self._show(mode)
        self.rows=[];self.getControl(110 if mode=='landing' else 210).reset()
        self.getControl(102).setLabel(tr(32496))
        kind,category,page=self.kind,self.category,self.offset
        def load():
            if self.favourites_only:
                from media_state import read
                ids=[json.loads(k)[2] for k in read()['favourites'] if json.loads(k)[:2]==[str(self.portal['id']),kind]]
                rows=[r for sid in ids if (r:=self.reader.get(kind,sid))]
                return rows[page:page+PAGE],len(rows)
            if mode=='landing':
                from utils import setting_int
                return self.reader.rail(kind,offset=page,limit=PAGE,keep=setting_int('recent_keep',100))
            return self.reader.page(kind,category=category,offset=page,limit=PAGE)
        self._request(load,self._page_ready)

    def _page_ready(self,value):
        self.rows,self.total=value
        cid=110 if self.mode=='landing' else 210
        self._fill(cid,self.rows)
        pos=min(self._positions.get((self.mode,self.category,self.offset),0),max(0,len(self.rows)-1))
        self.getControl(cid).selectItem(pos);self._last_position=pos
        self.getControl(102).setLabel(tr(32497).format(
            tr(32498) if self.mode=='landing' else tr(32499),self.offset+1 if self.rows else 0,
            self.offset+len(self.rows),self.total) if self.rows else
            (tr(32500) if self.mode=='landing' else tr(32501)))
        self._page_status='{}–{} / {}'.format(self.offset+1 if self.rows else 0,self.offset+len(self.rows),self.total)
        if not self.rows and self.mode=='grid':
            self.mode='groups' if self.groups else 'landing';self._show(self.mode)
        self.setFocusId(200 if self.mode=='groups' else cid if self.rows else 120)
        if self.rows: self._focus_item(pos)

    def _show(self,mode):
        for cid in (110,120,200,210,300,310,320,330):
            visible=(cid in (110,120) if mode=='landing' else cid in (200,210) if mode in ('grid','groups')
                     else cid in (300,310,320) if mode=='detail' else cid==330)
            self.getControl(cid).setVisible(visible)
        if mode in ('grid','groups'):
            expanded=mode=='groups' or self._cols==4
            self.getControl(200).setVisible(expanded)
            self.getControl(210).setPosition(320 if expanded else 44,174)
            self.getControl(210).setWidth(916 if expanded else 1192)
            self._cols=4 if expanded else 6

    def _focus_item(self,index):
        if not 0<=index<len(self.rows): return
        self._last_position=index
        self._positions[(self.mode,self.category,self.offset)]=index
        self.selected=self.rows[index]
        self.getControl(103).setLabel(self.selected.get('name',''))
        from media_data import video_info,recent_label
        from utils import setting_int
        info=video_info(self.selected)
        fields=[getattr(self,'_page_status','')]
        if self.mode=='landing': fields.append(recent_label(self.selected,setting_int('recent_days',10)))
        if info.get('duration'): fields.append(str(info['duration']//60)+tr(32502))
        if 'rating' in info: fields.append(tr(32503)+str(info['rating'])+tr(32504))
        self.getControl(102).setLabel(' · '.join(fields))
        self._queue_art(self.selected)

    def _queue_art(self,item):
        from media_art import local_art
        art=local_art(item)
        self.getControl(100).setImage(art['fanart'] or os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources','media','media_neutral.png'))
        try: self._art.put_nowait(dict(item))
        except queue.Full:
            try: self._art.get_nowait()
            except queue.Empty: pass
            try: self._art.put_nowait(dict(item))
            except queue.Full: pass

    def _art_loop(self):
        from media_art import sources,fetch,local_art
        while not self._closed:
            try: item=self._art.get(timeout=.5)
            except queue.Empty: continue
            for url in dict.fromkeys(sources(item)):
                if self._closed: break
                try: fetch(url)
                except Exception: pass
                with self._lock:
                    if self._closed: break
                    art=local_art(item)
                    if self.selected and self.selected.get('sid')==item.get('sid'):
                        if art['fanart']: self.getControl(100).setImage(art['fanart'])
                        if self.mode=='detail': self.getControl(310).setImage(art['poster'])
                    if self.mode in ('landing','grid'):
                        cid=110 if self.mode=='landing' else 210
                        for pos,row in enumerate(self.rows):
                            if row.get('sid')==item.get('sid'):
                                self.getControl(cid).getListItem(pos).setArt(art)

    def _details(self,item):
        self._previous=(self.mode,self.category,self.offset,self._last_position)
        self.mode='detail';self.selected=dict(item);self._show('detail')
        self.actions=[]
        self._detail_ready((dict(item),{}))
        self.getControl(102).setLabel(tr(32505))
        def load():
            from media_data import details
            from metadata_views import enrich
            data=details(self.router._xc(self.portal),self.kind,item['sid'])
            merged=enrich(item,data)
            for k in ('sid','kind','category_id'):
                if k in item: merged[k]=item[k]
            return merged,data
        self._request(load,self._detail_ready)

    def _detail_ready(self,value):
        if self.mode!='detail': return
        old_focus=self.getFocusId()
        old_position=self.getControl(300).getSelectedPosition()
        old_action=self.actions[old_position][1] if 0<=old_position<len(self.actions) else ''
        from media_art import local_art
        from media_data import video_info,episode_records
        from metadata_views import trailer_id
        from media_state import read,key as state_key,progress_key,resume_position
        item,data=value;self.selected=item
        try:
            state=read();self._state_ready=True
        except (ValueError,OSError,sqlite3.Error):
            state={'progress':{},'favourites':[]};self._state_ready=False
        def progress(kind,sid,series='',season=''):
            return state['progress'].get(progress_key(self.portal['id'],kind,sid,series,season),{})
        info=video_info(item)
        self.getControl(103).setLabel(info['title'])
        meta=[tr(32506)]
        for name,key in ((tr(32507),'year'),(tr(32508),'genre'),(tr(32509),'rating')):
            if key in info: meta.append('{}: {}'.format(name,info[key]))
        if 'duration' in info: meta.append(tr(32510).format(info['duration']//60))
        self.getControl(102).setLabel(' · '.join(meta))
        self.getControl(310).setImage(local_art(item)['poster'])
        self.getControl(320).setText(info['plot'] or tr(32511))
        self._queue_art(item)
        self.actions=[]
        if self.kind=='vod':
            saved=progress('vod',item['sid'])
            self.actions=[(tr(32512),'play'),(tr(32513),'restart')]
            position=resume_position(saved)
            if position:
                self.actions.insert(0,(tr(32514).format(int(position)//3600,int(position)//60%60,int(position)%60),'resume'))
        else:
            self.episodes=episode_records(data,item['sid'])
            self.actions=[(tr(32515),'seasons')] if self.episodes else []
            saved_episodes=[(e,progress('episode',e['sid'],e['series_id'],e['season'])) for e in self.episodes]
            started=[pair for pair in saved_episodes if resume_position(pair[1])]
            if started:
                self.continue_episode=max(started,key=lambda pair:pair[1].get('updated',0))[0]
                e=self.continue_episode
                self.actions.append((tr(32516).format(e['season'],e['episode']),'continue_episode'))
            watched=[i for i,(e,s) in enumerate(saved_episodes) if s.get('watched') and e['season']>0 and e['episode']>0]
            if watched and max(watched)+1<len(self.episodes):
                self.next_episode=self.episodes[max(watched)+1]
                if self.next_episode['season']>0 and self.next_episode['episode']>0:
                    self.actions.append((tr(32517).format(self.next_episode['season'],self.next_episode['episode']),'next_episode'))
        fav=state_key(self.portal['id'],self.kind,item['sid']) in state['favourites']
        if self._state_ready:
            self.actions.append((tr(32518) if fav else tr(32519),'favourite'))
        else: self.getControl(102).setLabel(tr(32520))
        self.trailer=trailer_id(item)
        if self.trailer and xbmc.getCondVisibility('System.HasAddon(plugin.video.youtube)'):
            self.actions.append((tr(32521),'trailer'))
        self._fill(300,[dict(name=label,sid=action) for label,action in self.actions])
        self.getControl(300).selectItem(next((i for i,a in enumerate(self.actions) if a[1]==old_action),0))
        self.setFocusId(old_focus if old_focus in (300,400) else 300)

    def _play(self,item,kind,resume=False):
        url=self.router.url(action='media_play',pid=self.portal['id'],kind=kind,sid=item['sid'],
            series_id=item.get('series_id'),season=item.get('season'),episode=item.get('episode'),resume='1' if resume else '0')
        xbmc.executebuiltin('PlayMedia('+url+')')

    def onClick(self,controlId):
        with self._lock:
            if controlId==400:
                self._search();return
            if controlId==120 and hasattr(self,'reader'):
                if getattr(self,'_catalog_missing',False):
                    self.getControl(102).setLabel(tr(32522))
                    def load():
                        self.router._xc(self.portal).warm_catalogs(include_live=False,include_vod=self.kind=='vod',include_series=self.kind=='series')
                        return self._initial()
                    self._request(load,self._initial_ready)
                    return
                self._cols=4;self._page('grid',0)
            elif controlId in (110,210):
                pos=self.getControl(controlId).getSelectedPosition()
                if 0<=pos<len(self.rows): self._focus_item(pos);self._details(self.rows[pos])
            elif controlId==200:
                pos=self.getControl(200).getSelectedPosition()
                if 0<=pos<len(self.groups):
                    self.category=self.groups[pos]['cid'];self._page('grid',0)
            elif controlId==300 and self.mode=='detail':
                pos=self.getControl(300).getSelectedPosition()
                if not 0<=pos<len(self.actions): return
                action=self.actions[pos][1]
                if action in ('play','restart','resume'): self._play(self.selected,'vod',action=='resume')
                elif action=='favourite':
                    from media_state import toggle
                    toggle(self.portal['id'],self.kind,self.selected['sid'])
                    self._detail_ready((self.selected,{'episodes':self._episode_raw()}))
                elif action=='trailer': self.router._play_youtube_id(self.trailer)
                elif action in ('continue_episode','next_episode'):
                    self._play(self.continue_episode if action=='continue_episode' else self.next_episode,'episode',action=='continue_episode')
                elif action=='seasons':
                    self.mode='seasons';self._show('seasons')
                    self.seasons=sorted({e['season'] for e in self.episodes})
                    self._fill(330,[dict(name=tr(32523)+str(s),sid=str(s)) for s in self.seasons]);self.setFocusId(330)
            elif controlId==330:
                pos=self.getControl(330).getSelectedPosition()
                if self.mode=='seasons' and 0<=pos<len(self.seasons):
                    self.season=self.seasons[pos];self.mode='episodes'
                    self._show_episodes()
                elif self.mode=='episodes' and 0<=pos<len(self.visible_episodes):
                    e=self.visible_episodes[pos]
                    from media_state import progress,resume_position
                    saved=progress(self.portal['id'],'episode',e['sid'],e['series_id'],e['season'])
                    resume=bool(resume_position(saved)) and xbmcgui.Dialog().yesno('XCMate',tr(32524))
                    self._play(e,'episode',resume)

    def _episode_raw(self):
        raw={}
        for e in self.episodes:
            raw.setdefault(str(e['season']),[]).append(dict(e,id=e['sid'],title=e['name'],episode_num=e['episode'],info=e))
        return raw

    def _show_episodes(self):
        from media_state import read,progress_key
        snapshot=read()['progress']
        self.visible_episodes=[e for e in self.episodes if e['season']==self.season]
        rows=[]
        for e in self.visible_episodes:
            saved=snapshot.get(progress_key(self.portal['id'],'episode',e['sid'],e['series_id'],e['season']),{})
            status=tr(32525) if saved.get('watched') else tr(32526) if saved.get('position') else tr(32527)
            rows.append(dict(e,name='{} · {} · {}'.format(e['episode'],e['name'],status)))
        self._fill(330,rows);self.getControl(330).selectItem(0);self.setFocusId(330)

    def onAction(self,action):
        key=action.getId()
        with self._lock:
            if key in (9,10,92):
                self._generation+=1
                if self.mode=='episodes':
                    self.mode='seasons';self._fill(330,[dict(name=tr(32523)+str(s),sid=str(s)) for s in self.seasons]);return
                if self.mode=='seasons': self.mode='detail';self._show('detail');self.setFocusId(300);return
                if self.mode=='detail' and self._previous:
                    mode,self.category,offset,pos=self._previous
                    self._positions[(mode,self.category,offset)]=pos
                    self._page(mode,offset);return
                if self.mode in ('grid','groups'):
                    self._cols=4;self._page('landing',0);return
                self.close();return
            if key==117:
                if self.mode=='episodes':
                    pos=self.getControl(330).getSelectedPosition()
                    if 0<=pos<len(self.visible_episodes):
                        choice=xbmcgui.Dialog().select(tr(32528),[tr(32529),tr(32530),tr(32531)])
                        if choice in (0,1,2) and (choice!=2 or xbmcgui.Dialog().yesno('XCMate',tr(32532))):
                            from media_state import mark_episode
                            mark_episode(self.portal['id'],self.visible_episodes[pos],True if choice==0 else False if choice==1 else None)
                            self._show_episodes();self.getControl(330).selectItem(pos)
                    return
                self._search()
                return
            focus=self.getFocusId()
            if focus==400 and key==4:
                target=110 if self.mode=='landing' and self.rows else 120
                if self.mode in ('grid','groups'): target=210 if self.rows else 200
                self.setFocusId(target)
                return
            if focus==200 and key==2:
                if not self.rows:
                    self.getControl(102).setLabel(tr(32533))
                    return
                self.mode='grid';self._cols=6;self._show('grid');self.setFocusId(210);return
            if focus not in (110,210): return
            pos=self.getControl(focus).getSelectedPosition()
            if key==3 and focus==210 and self._last_position<self._cols:
                self.setFocusId(400);return
            if key in (5,6):
                target=self.offset+(-PAGE if key==5 else PAGE)
                if 0<=target<self.total: self._page(self.mode,target)
                return
            if key==1 and focus==210 and self._last_position%self._cols==0:
                self.getControl(210).selectItem(self._last_position)
                self.mode='groups';self._show('groups');self.setFocusId(200);return
            if key==2 and self._last_position==len(self.rows)-1 and self.offset+len(self.rows)<self.total:
                self._page(self.mode,self.offset+PAGE);return
            if key==1 and self._last_position==0 and self.offset and focus==110:
                self._page(self.mode,self.offset-PAGE);return
            if 0<=pos<len(self.rows): self._focus_item(pos)

    def _search(self):
        query=xbmcgui.Dialog().input(tr(32534))
        if query.strip():
            self.close()
            xbmc.executebuiltin('Container.Update('+self.router.url(action='global_search',pid=self.portal['id'],q=query[:200])+')')

    def close(self):
        if self._closed: return
        self._closed=True;self._generation+=1
        self._pool.shutdown(wait=False,cancel_futures=True)
        super().close()


def open_media(router,portal,kind,sid='',favourites=False):
    window=MediaWindow('XCMateMedia.xml',xbmcaddon.Addon().getAddonInfo('path'),'Default','720p')
    window.configure(router,portal,kind,sid,favourites)
    try: window.doModal()
    finally: window.close()
