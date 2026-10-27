"""Own Kodi WindowXML: real horizontal rail, groups/grid and detail view.

Native XML controls dispatch onClick, unlike programmatic WindowDialog. Data,
metadata and images are prepared by bounded workers; callbacks only use views.
"""
from localization import tr
from owner_dispatch import OwnerDispatch,native_init,open_owned_window
from media_search import SearchMixin
from detail_menu import DetailMenuMixin
import json
import os
import queue
import threading
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor

import xbmc
import xbmcgui
import xbmcaddon

PAGE=24
WINDOW_ITEMS=240


class MediaView(DetailMenuMixin,SearchMixin,OwnerDispatch):
    def configure(self,router,portal,kind,sid='',favourites=False):
        self._configure_owner()
        from theme_render import snapshot
        self._theme=snapshot()
        self._dispatch=getattr(router,'_navigation_dispatch','')
        self._return_home=False
        self.router,self.portal,self.kind=router,portal,kind
        self.initial_sid=sid
        self.favourites_only=favourites
        self.mode='landing';self.category='';self.offset=0;self.total=0
        self.rails={111:[],112:[]};self._art_revision=0
        self.rows=[];self.groups=[];self.selected=None;self.episodes=[];self.actions=[]
        self._positions={};self._previous=None;self._last_position=0;self._cols=4
        self._ready=False;self._closed=False;self._generation=0;self._play_intent=''
        self._watch_stop=threading.Event();self._watch_thread=None;self._pending_future=None
        self._opened_at=time.monotonic();self._seen_revision=''
        self._catalog_missing=True
        self._catalog_update=None
        self._mode_focus={};self._next_route=None
        self._focus_pending=None
        self._restore_focus=None;self._season_cursor=0
        self._episode_cursor={};self._leaving=False
        self._landing_loaded=False
        self._rail_focus={}
        self._art_selected=None;self._art_diagnostic=None
        self._append_future=None;self._append_context=None;self._append_failed=False
        self._append_advance=None;self._grid_return=None
        self._playback_waiting=False;self._playback_seen=False;self._autoplay_root=''
        self._episode_refs={};self.next_episode=None;self._episode_last_pos=0;self._episode_next_key=None
        self._lock=threading.RLock();self._pool=ThreadPoolExecutor(max_workers=2)
        self._art=queue.Queue(maxsize=3)
        self._art_thread=threading.Thread(target=self._art_loop,daemon=True,name='XCMate-art')
        self._art_thread.start()

    def _stop_media_only(self):
        from playback_exit import identity
        token=identity(xbmc.Player())
        if token and token[0]=='media':
            from exit_jobs import request
            return request(pid=self.portal['id'],expected=token,reason='USER_BACK')
        return False

    def setFocusId(self,control_id):
        if self._closed:return
        rail=getattr(self,'_navigation_rail',None)
        if rail and rail.active:return
        requested=control_id
        # Native setVisible/enabled flags may lag one GUI frame. Keep the
        # intended target instead of committing a temporary fallback to Search.
        eligible=self._valid_focus(native=False)
        if control_id not in eligible:
            primary=300 if self.mode=='detail' else 330 if self.mode in ('episodes','seasons') else None
            control_id=primary if primary is not None else next(iter(eligible),None)
        if control_id is None:return
        valid=self._valid_focus()
        if self.mode=='search':
            from search_navigation import focus_details
            focus_details(self,requested,eligible,valid)
            # Native XML can process another key before visibility catches up.
            # Never leave old 400 -> 120 landing edges live during that frame.
            for cid in (400,700,701,702,710,720,721):
                control=self.getControl(cid);control.setNavigation(control,control,control,control)
        if control_id not in valid:
            if (self.mode in ('detail','seasons','episodes') and control_id in (300,330,340,810,820)
                    or self.mode=='search' and control_id in eligible):
                self._mode_focus[self.mode]=control_id
                pending=(self.mode,control_id)
                if self._focus_pending!=pending:
                    from window_navigation import trace
                    trace('FOCUS_DEFER',self.mode,control_id,self._dispatch)
                if self._focus_pending!=pending:self._focus_deadline=time.monotonic()+2
                self._focus_pending=pending
                return
            # Preserve established catalogue/landing navigation when a target
            # is genuinely disabled or its row has disappeared.
            if not valid:return
            control_id=self._mode_focus.get(self.mode,valid[0])
            if control_id not in valid:control_id=valid[0]
        deferred=self._focus_pending is not None
        self._focus_pending=None
        for pos,cid in enumerate(valid):
            control=self.getControl(cid)
            control.setNavigation(self.getControl(valid[max(0,pos-1)]),
                                  self.getControl(valid[min(len(valid)-1,pos+1)]),control,control)
        if 210 in valid:
            panel=self.getControl(210)
            panel.setNavigation(self.getControl(400),panel,panel,panel)
        super().setFocusId(control_id)
        if deferred:
            from window_navigation import trace
            trace('FOCUS_READY',self.mode,control_id,self._dispatch)
        if self.mode=='landing':
            first=next((cid for cid in (112,111,110) if cid in valid),120)
            cat=self.getControl(120);search=self.getControl(400);row=self.getControl(first)
            cat.setNavigation(cat,row,cat,search)
            search.setNavigation(search,row,cat,search)
            self._track_art_focus()
        if self.mode=='episodes':
            rows=self.getControl(330);search=self.getControl(400)
            target=self.getControl(340) if 340 in valid else rows
            rows.setNavigation(target,rows,rows,target)
            search.setNavigation(search,target,search,search)
            if 340 in valid:target.setNavigation(search,rows,rows,rows)
        self._nav_focus=control_id
        self._mode_focus[self.mode]=control_id

    def _resume_focus(self):
        # One nonblocking check per existing owner-pump tick. No GUI work on
        # workers, no additional loop, and no search click while focus is stale.
        if self._closed or self._leaving or self._playback_waiting and not getattr(self,'_detail_menu_open',False):return
        pending=self._focus_pending
        if pending is None:return
        if pending[0]!=self.mode:
            self._focus_pending=None;return
        if self.mode=='search' and time.monotonic()>=getattr(self,'_focus_deadline',float('inf')):
            self._focus_pending=None
            from search_navigation import mark
            mark('FOCUS_TIMEOUT',self.router,'media',getattr(self,'_search_correlation',''),pending[1],True)
            return
        if pending[1] in self._valid_focus():self.setFocusId(pending[1])

    def _valid_focus(self,native=True):
        if getattr(self,'_detail_menu_open',False):
            return [810] if not native or self.getControl(800).isVisible() and self.getControl(810).isVisible() else []
        candidates=([120,400,112,111,110] if self.mode=='landing' else
                    [200,210,400] if self.mode in ('grid','groups') else
                    [300,820,400] if self.mode=='detail' else [700,701,702,710,720,721,400] if self.mode=='search' else [330,340,400] if self.mode=='episodes' else [330,400])
        result=[]
        for cid in candidates:
            if cid==110 and not self.rows:continue
            if cid in (111,112) and not self.rails[cid]:continue
            if cid==200 and (not self.groups or self.mode=='grid' and self._cols==6):continue
            if cid==210 and not self.rows:continue
            if cid==300 and not self.actions:continue
            if cid==330 and not self.getControl(330).size():continue
            if cid==340 and self.next_episode is None:continue
            if cid==710 and (not getattr(self,'_search_rows',[]) or getattr(self,'_search_loading',False)):continue
            if cid==720 and not getattr(self,'_search_offset',0):continue
            if cid==721:
                section=getattr(self,'_search_data',{}).get(getattr(self,'_search_kind','vod'),{})
                if not section.get('total') or self._search_offset+len(self._search_rows)>=section['total']:continue
            control=self.getControl(cid)
            if not native or control.isVisible() and xbmc.getCondVisibility('Control.IsEnabled({})'.format(cid)) and xbmc.getCondVisibility('Control.IsVisible({})'.format(cid)):result.append(cid)
        return result

    @native_init
    def onInit(self):
        if getattr(self,'_returning39',False):return
        self.getControl(400).setLabel(tr(32586))
        self.getControl(501).setLabel(tr(32587))
        if self._ready and getattr(self,'_playback_origin39',None):
            # Fullscreen/Stop races must not reset the still-owned native view.
            self._poll_playback_return();return
        if self._ready and getattr(self,'_search_prompt',False):return
        if self._ready and self.mode=='search':
            from media_search import mark
            mark('SEARCH_RESUMED',getattr(self,'_search_correlation',''))
            self._show('search')
            if getattr(self,'_search_data',None):self._search_ready(self._search_data,resume=True)
            return
        if self._ready:
            if self._chain_active():return
            # onInit can be delivered during Kodi decoder/fullscreen startup.
            # Reinitialization is not an explicit Back/Stop or cancellation.
            self._playback_waiting=False;self._playback_seen=False
            self._generation+=1
            if self._pending_future is not None:self._pending_future.cancel()
            self._pending_future=None;self._pending_apply=None
            self._show(self.mode)
            if self.mode=='detail': self._detail_ready((self.selected,{'episodes':self._episode_raw()}))
            elif self.mode=='episodes': self._show_episodes()
            elif self.mode=='seasons':
                self._fill(330,self._season_rows());self.setFocusId(330)
            else:
                self._fill(200,[dict(name=g['title'],sid=g['cid']) for g in self.groups])
                self._page_ready((self.rows,self.total))
            return
        self._ready=True
        if getattr(self,'_search_root',False):
            # A root search has no landing/catalogue frame to initialize.
            from window_lifecycle import capture
            self._search_native_window=capture(self)
            self.mode='search';self._show('search')
            self.getControl(101).setLabel(tr(32586));return
        self._show('landing')
        self.getControl(101).setLabel('XCMate · '+(tr(32461) if self.kind=='vod' else tr(32462)))
        self.getControl(120).setLabel((tr(32403) if self.kind=='vod' else tr(32404))+tr(32492))
        self.getControl(102).setLabel(tr(32491))
        self._request(self._initial,self._initial_ready)
        self._start_watch()

    def _query_failed(self,exc):
        self._gui()
        if self.mode=='search':
            self._search_loading=False
            from media_search import mark
            mark('SEARCH_WORKER_FAILED',self._search_correlation)
        self.getControl(102).setLabel(tr(32610))

    def _initial(self):
        from media_catalog43 import Reader
        from catalog_sync import request
        reader=Reader(self.portal['id'])
        groups=reader.groups(self.kind)
        preferred=self.category or (groups[0]['cid'] if groups else '')
        if not reader.state(self.kind): request(self.portal,self.kind,preferred,priority=2)
        return reader,groups,reader.state(self.kind)

    def _initial_ready(self,value):
        self.reader,self.groups,state=value
        self._catalog_missing=not bool(state)
        self._seen_revision=(state or {}).get('revision','')
        self._fill(200,[dict(name=g['title'],sid=g['cid']) for g in self.groups])
        self.category=self.category if any(g['cid']==self.category for g in self.groups) else (self.groups[0]['cid'] if self.groups else '')
        if not state:
            self.getControl(102).setLabel(tr(32494))
            self.getControl(120).setLabel(tr(32495))
            self.setFocusId(120)
            return
        self.getControl(120).setLabel((tr(32403) if self.kind=='vod' else tr(32404))+tr(32492))
        if self.initial_sid:
            # The completion callback owns GUI, not SQL/profile IO. Widgets
            # resolve their one verified media ID on the existing data worker.
            reader,kind,sid=self.reader,self.kind,self.initial_sid
            self.initial_sid=''
            self._request(lambda:reader.get(kind,sid),lambda item:self._details(item) if item else self._page('landing',0))
            return
        self._page('landing',0)

    def _start_watch(self):
        if self._watch_thread is not None: return
        def watch():
            while not self._watch_stop.wait(2):
                if self._closed: return
                try: self._poll_catalog()
                except Exception: pass
        self._watch_thread=threading.Thread(target=watch,name='XCMate-index-view',daemon=True)
        self._watch_thread.start()

    def _poll_catalog(self):
        from media_art import revision
        if revision()!=self._art_revision:
            self._art_revision=revision()
        from library_index import sync_state
        from media_catalog43 import Reader
        reader=Reader(self.portal['id'])
        state=reader.state(self.kind)
        revision=(state or {}).get('revision','')
        from catalog_delta import states as delta_states
        status=delta_states(self.portal['id'],self.kind)+sync_state(self.portal['id'],self.kind)
        groups=reader.groups(self.kind) if state else []
        with self._lock:item=dict(self._art_selected) if self._art_selected else None
        if item:
            from media_art import diagnose,request
            diagnosis=diagnose(item)
            if diagnosis['poster'] in ('NOT_REQUESTED','DB_BUSY'):request([item])
        with self._lock:
            if self._closed: return
            if item:self._art_diagnostic=(item,diagnosis)
            self._catalog_update=(reader,state,revision,status,groups)
        if threading.get_ident()==self._owner: self._owner_tick()

    def _owner_tick(self):
        self._gui()
        if getattr(self,'_picker_requested43',None):
            from media_picker43 import open_pending
            open_pending(self)
            if self._closed:return
        self._search_tick()
        self._resume_focus()
        self._poll_playback_return()
        if self._playback_waiting and self._playback_seen:return
        if self.mode=='episodes':self._sync_episode_next()
        self._poll_append()
        if self._leaving:
            if time.monotonic()>=self._leave_after:self.close()
            return
        with self._lock:
            update=self._catalog_update;self._catalog_update=None
        if update is None or self._closed: return
        reader,state,revision,status,groups=update
        self._refresh_art()
        with self._lock:
            if self._closed: return
            if state and revision!=self._seen_revision:
                self._seen_revision=revision
                if self.mode in ('landing','grid','groups'):
                    self.reader=reader;self.groups=groups;self._catalog_missing=False
                    self._fill(200,[dict(name=g['title'],sid=g['cid']) for g in self.groups])
                    if not self.category and self.groups: self.category=self.groups[0]['cid']
                    start=self.offset
                    if self.mode=='grid' and self.rows:
                        absolute=self.offset+self.getControl(210).getSelectedPosition()
                        start=absolute//PAGE*PAGE
                        self._positions[(self.mode,self.category,start)]=absolute-start
                        pos=self.getControl(210).getSelectedPosition()
                        if 0<=pos<len(self.rows):self._catalog_restore43=self.rows[pos]['sid']
                    self._page(self.mode,start)
            if status and status[0]['code'] in ('FAILED','CANCELLED'):
                self.getControl(102).setLabel(tr(32610))
                if self._catalog_missing: self.getControl(120).setLabel(tr(32611))
            elif status and status[0]['code'] in ('PENDING','RUNNING'):
                self.getControl(102).setLabel(tr(35400))
            elif status and status[0]['code']=='EMPTY_SOURCE':
                self.getControl(102).setLabel(tr(35401))
            elif status and status[0]['code']=='INDEXING':
                self.getControl(102).setLabel(tr(32612,status[0]['stored'],status[0]['received']))

    def _display_art39(self,row):
        from collections import OrderedDict
        from media_art import local_art,sources
        from artwork_visible import retain_displayed
        if not hasattr(self,'_art_history39'):self._art_history39=OrderedDict()
        key=(str(row.get('kind',self.kind)),str(row.get('sid','')),sources(row))
        history=self._art_history39
        current=retain_displayed(row,history.get(key,{}),local_art(row,self._theme))
        history[key]=current;history.move_to_end(key)
        while len(history)>256:history.popitem(last=False)
        return current

    def _fill(self,control_id,rows):
        from media_art import local_art
        control=self.getControl(control_id);control.reset()
        items=[]
        for row in rows:
            art=self._display_art39(row)
            if control_id==710:
                from search_results import item
                li=item(row,self._theme,art=art)
            else:
                li=xbmcgui.ListItem(str(row.get('name','')))
                li.setArt(art)
            if not hasattr(self,'_shown_art'):self._shown_art={}
            self._shown_art[(control_id,len(items))]=art
            if control_id in (300,330):
                from theme_render import action_art
                li.setArt(action_art(row.get('sid','') if control_id==300 else 'next_episode' if self.mode=='episodes' else 'seasons',self._theme,row.get('favourite',getattr(self,'_theme_favourite',False))))
            li.setInfo('video',{'title':str(row.get('name',''))})
            if '_watched' in row:
                icon='eye_watched.png' if row['_watched'] else 'eye_unseen.png'
                li.setProperty('XCMate.Eye',os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources','media',icon))
            items.append(li)
        control.addItems(items)
        from media_art import request
        request(rows,priority=0)

    def _refresh_art(self):
        from media_art import local_art
        with self._lock:
            if self._closed: return
            controls={110:self.rows} if self.mode=='landing' else {210:self.rows} if self.mode in ('grid','groups') else {}
            if self.mode=='landing': controls.update(self.rails)
            for cid,rows in controls.items():
                from artwork_visible import retain_displayed
                if not hasattr(self,'_shown_art'):self._shown_art={}
                for pos,row in enumerate(rows):
                    key=(cid,pos);prior=self._shown_art.get(key,{})
                    art=self._display_art39(row)
                    if art!=prior:
                        self.getControl(cid).getListItem(pos).setArt(art)
                        self._shown_art[key]=art
            if self.selected:
                from artwork_visible import retain_displayed
                prior=getattr(self,'_selected_art',{})
                art=self._display_art39(self.selected)
                from theme_render import media_background
                if art.get('fanart')!=prior.get('fanart'):self.getControl(100).setImage(media_background(self,art['fanart']))
                if self.mode=='detail' and art.get('poster')!=prior.get('poster'):self.getControl(310).setImage(art['poster'])
                self._selected_art=art
            if self.mode in ('landing','grid','groups','detail') and self._art_diagnostic:
                item,value=self._art_diagnostic
                if item==self._art_selected:
                    from media_art import diagnostic_label
                    self.getControl(501).setLabel(tr(33400,diagnostic_label(value['poster']))+' · '+tr(32587))

    def _refresh_rails(self):
        from media_state import rail_items
        for cid,rail in ((111,'favourites'),(112,'continue')):
            try: rows=rail_items(self.portal['id'],self.kind,self.reader,rail)
            except (ValueError,OSError,sqlite3.Error):
                rows=[]
                self.getControl(102).setLabel(tr(32520))
            self.rails[cid]=rows
            self._fill(cid,rows)
            selected=self._rail_focus.get(cid,'')
            self.getControl(cid).selectItem(next((i for i,r in enumerate(rows) if r['sid']==selected),0))
        self.getControl(113).setLabel(tr(32663))
        self.getControl(114).setLabel(tr(32664) if self.rails[111] else tr(32665))
        self.getControl(115).setLabel(tr(32668) if self.rails[112] else tr(32669))
        for cid,gid,rows in ((112,610,self.rails[112]),(111,611,self.rails[111]),(110,612,self.rows)):
            self.getControl(gid).setHeight(288 if rows else 48)
            self.getControl(cid).setVisible(bool(rows))

    def _page(self,mode,offset=0):
        if self._append_future is not None:self._append_future.cancel()
        self._append_future=None;self._append_context=None;self._append_failed=False;self._append_advance=None
        self.mode=mode;self.offset=max(0,offset)
        self._show(mode)
        self.rows=[];self.getControl(110 if mode=='landing' else 210).reset()
        self.getControl(102).setLabel(tr(32496))
        kind,category,page=self.kind,self.category,self.offset
        reader=self.reader;restore=getattr(self,'_catalog_restore43',None);self._catalog_restore43=None
        def load():
            if self.favourites_only:
                from media_state import read
                ids=[json.loads(k)[2] for k in read()['favourites'] if json.loads(k)[:2]==[str(self.portal['id']),kind]]
                rows=[r for sid in ids if (r:=self.reader.get(kind,sid))]
                return rows[page:page+PAGE],len(rows)
            if mode=='landing':
                from utils import setting_int
                return self.reader.rail(kind,offset=page,limit=PAGE,keep=setting_int('recent_keep',100))
            from media_page43 import read
            return read(reader,kind,category,page,PAGE,restore=restore)
        self._request(load,self._page_ready)

    def _page_ready(self,value):
        old_focus=self.getFocusId()
        if hasattr(value,'offset'):self.offset=value.offset
        if hasattr(value,'revision'):self._catalog_token43=value.revision
        self.rows,self.total=value
        cid=110 if self.mode=='landing' else 210
        self._fill(cid,self.rows)
        if self.mode=='landing': self._refresh_rails()
        pos=min(self._positions.get((self.mode,self.category,self.offset),0),max(0,len(self.rows)-1))
        if getattr(value,'selected',None):pos=next((i for i,r in enumerate(self.rows) if r['sid']==value.selected),pos)
        self.getControl(cid).selectItem(pos);self._last_position=pos
        self.getControl(102).setLabel(tr(32497).format(
            tr(32498) if self.mode=='landing' else tr(32499),self.offset+1 if self.rows else 0,
            self.offset+len(self.rows),self.total) if self.rows else
            (tr(32500) if self.mode=='landing' else tr(32501)))
        self._page_status='{}–{} / {}'.format(self.offset+1 if self.rows else 0,self.offset+len(self.rows),self.total)
        if self.mode in ('grid','groups'):self._grid_status()
        if not self.rows and self.mode=='grid':
            self.mode='groups' if self.groups else 'landing';self._show(self.mode)
        target=200 if self.mode=='groups' else cid if self.rows else 120
        if self.mode=='landing':
            valid=self._valid_focus()
            target=old_focus if self._landing_loaded and old_focus in valid else next((c for c in (112,111,110) if c in valid),120)
            self._landing_loaded=True
        self.setFocusId(target)
        if self.rows: self._focus_item(pos)
        target=getattr(self,'_restore_rail',None)
        if self.mode=='landing' and target in (111,112):
            self._restore_rail=None
            self.setFocusId(target if self.rails[target] else 120)
        if self._restore_focus is not None:
            target=self._restore_focus;self._restore_focus=None;self.setFocusId(target)
        self._track_art_focus()

    def _track_art_focus(self):
        focus=self.getFocusId()
        if self.mode=='landing' and focus in (111,112):
            rows=self.rails[focus];pos=self.getControl(focus).getSelectedPosition()
            if 0<=pos<len(rows) and rows[pos]!=self._art_selected:self._queue_art(rows[pos])

    def _show(self,mode):
        self._detail_menu_prepare(mode)
        if mode in ('landing','search') and not self._theme:
            from theme_render import lightweight_background
            self.getControl(100).setImage(lightweight_background())
        self.getControl(501).setLabel(tr(32587))
        self.getControl(340).setVisible(mode=='episodes' and self.next_episode is not None)
        self.getControl(330).setPosition(44,190 if mode=='episodes' else 174)
        for cid in (630,631,632,633):self.getControl(cid).setVisible(mode=='episodes')
        self.getControl(631).setLabel(tr(32527));self.getControl(633).setLabel(tr(32525))
        self.getControl(104).setVisible(mode!='detail')
        self.getControl(105).setVisible(mode=='detail')
        self.getControl(620).setVisible(mode=='landing')
        self.getControl(103).setVisible(mode!='landing')
        self.getControl(400).setPosition(1050,80 if mode=='landing' else 32)
        for cid in (110,111,112,113,114,115,120,200,210,300,310,320,330):
            visible=(cid in (110,111,112,113,114,115,120) if mode=='landing' else cid in (200,210) if mode in ('grid','groups')
                     else cid in (300,310,320) if mode=='detail' else cid==330)
            self.getControl(cid).setVisible(visible)
        if mode in ('grid','groups'):
            expanded=mode=='groups' or self._cols==4
            self.getControl(200).setVisible(expanded)
            self.getControl(210).setPosition(320 if expanded else 44,174)
            self.getControl(210).setWidth(916 if expanded else 1192)
            self._cols=4 if expanded else 6
        for cid in (700,701,702,710,720,721):self.getControl(cid).setVisible(mode=='search')
        if mode=='search':self.getControl(330).setVisible(False)
        # Kodi's default focus must never remain on the now hidden landing button.
        primary=300 if mode=='detail' else 330 if mode in ('seasons','episodes') else self.getFocusId()
        self.setFocusId(self._mode_focus.get(mode,primary))

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
        self._art_selected=dict(item)
        self.getControl(501).setLabel(tr(32587))
        from media_art import local_art
        art=self._display_art39(item)
        from theme_render import media_background
        self.getControl(100).setImage(media_background(self,art['fanart']))
        try: self._art.put_nowait(dict(item))
        except queue.Full:
            try: self._art.get_nowait()
            except queue.Empty: pass
            try: self._art.put_nowait(dict(item))
            except queue.Full: pass

    def _art_loop(self):
        from media_art import request
        while not self._closed:
            try: item=self._art.get(timeout=.5)
            except queue.Empty: continue
            request([item],priority=0)

    def _details(self,item):
        if self.mode in ('grid','groups'):
            self._grid_return=(self.mode,self.category,self.offset,list(self.rows),self.total,self._last_position,self._cols)
        self._previous=(self.mode,self.category,self.offset,self._last_position)
        self._return_focus=self.getFocusId()
        self.actions=[]
        self._mode_focus['detail']=300
        self.mode='detail';self.selected=dict(item);self._show('detail')
        self._detail_ready((dict(item),{}))
        self.setFocusId(300)
        if item.get('_unavailable'):
            self.getControl(102).setLabel(tr(32667));return
        self.getControl(102).setLabel(tr(32505))
        def load():
            from media_data import details
            from metadata_views import enrich
            data=details(self.router._xc(self.portal),self.kind,item['sid'])
            merged=enrich(item.get('_provider43',item),data)
            from media_metadata43 import fallback
            merged=fallback(merged,self.kind)
            for k in ('sid','kind','category_id'):
                if k in item: merged[k]=item[k]
            from media_overrides43 import apply_many
            return apply_many(self.portal['id'],[merged])[0],data
        self._request(load,self._detail_ready)

    def _detail_ready(self,value):
        if self.mode!='detail': return
        old_focus=self._mode_focus.get('detail',300)
        old_position=self.getControl(300).getSelectedPosition()
        old_action=self.actions[old_position][1] if 0<=old_position<len(self.actions) else ''
        from media_art import local_art
        from media_data import video_info
        from media_sequence import records
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
        self.getControl(310).setImage(self._display_art39(item)['poster'])
        self.getControl(320).setText(info['plot'] or tr(32511))
        self._queue_art(item)
        self.actions=[]
        flat=self.kind=='series' and bool(item.get('series_flat'))
        if flat: self.getControl(320).setText(tr(32744))
        if self.kind=='vod' or flat:
            saved=progress('series_item' if flat else 'vod',item['sid'])
            self.actions=[(tr(32512),'play'),(tr(32513),'restart')]
            position=resume_position(saved)
            if position:
                self.actions.insert(0,(tr(32514).format(int(position)//3600,int(position)//60%60,int(position)%60),'resume'))
        else:
            self.episodes=records(data,self.portal['id'],item['sid'])
            self.actions=[(tr(32515),'seasons')] if self.episodes else []
            if not self.episodes and self.portal.get('type')=='stb': self.getControl(320).setText(tr(32775))
            saved_episodes=[(e,progress('episode',e['sid'],e['series_id'],e['season'])) for e in self.episodes]
            started=[pair for pair in saved_episodes if resume_position(pair[1])]
            if started:
                self.continue_episode=max(started,key=lambda pair:pair[1].get('updated',0))[0]
                e=self.continue_episode
                self.actions.append((tr(32516).format(e['season'],e['episode']),'continue_episode'))
            self.next_episode=self._next_for_series(state['progress'])
            if self.next_episode:
                e=self.next_episode
                self.actions.append((tr(32517).format(e['season'],e['episode']),'next_episode'))
        if item.get('_unavailable'): self.actions=[]
        fav=state_key(self.portal['id'],self.kind,item['sid']) in state['favourites']
        self._theme_favourite=fav
        if self._state_ready:
            self.actions.append((tr(32518) if fav else tr(32519),'favourite'))
        else: self.getControl(102).setLabel(tr(32520))
        self.trailer=trailer_id(item)
        if self.trailer and xbmc.getCondVisibility('System.HasAddon(plugin.video.youtube)'):
            self.actions.append((tr(32521),'trailer'))
        if not item.get('_unavailable'):self.actions.append((tr(33703),'poster_status'))
        self._fill(300,[dict(name=label,sid=action) for label,action in self.actions])
        self.getControl(300).selectItem(next((i for i,a in enumerate(self.actions) if a[1]==old_action),0))
        self.setFocusId(old_focus if old_focus in (300,400) else 300)

    def _play(self,item,kind,resume=False):
        from exit_jobs import blocked
        if blocked():
            xbmcgui.Dialog().notification('XCMate',tr(35845));return
        if self._playback_waiting:return  # IR repeats cannot queue competing resolvers.
        self._cancel_chain()
        if kind=='episode':
            from media_sequence import match
            episode=match(self.episodes,self.portal['id'],self.selected['sid'],item)
            if episode:
                self._episode_refs[(str(self.portal['id']),str(self.selected['sid']))]=episode
                if self.mode=='episodes':
                    self.season=episode['season']
                    if self.season in self.seasons:self._season_cursor=self.seasons.index(self.season)
                    rows=[e for e in self.episodes if e['season']==self.season]
                    self._episode_cursor[self.season]=next(i for i,e in enumerate(rows) if e['sid']==episode['sid'])
        self._playback_waiting=True;self._playback_seen=False;self._playback_started40=time.monotonic()
        self._generation+=1
        if self._pending_future is not None:self._pending_future.cancel()
        self._pending_future=None;self._pending_apply=None
        from media_intent import begin
        self._play_intent=begin(self.portal['id'],kind,item['sid'])
        from media_return import capture as capture_origin
        capture_origin(self,self._play_intent)
        if getattr(self,'_native_surface','window')=='dialog':
            # Keep the owner/memento alive, release only this native modal.
            self._origin_suspended40=True
            super().close()
        self._autoplay_root=self._play_intent if kind=='episode' else ''
        url=self.router.url(action='media_play',pid=self.portal['id'],kind=kind,sid=item['sid'],
            series_id=item.get('series_id'),season=item.get('season'),episode=item.get('episode'),intent=self._play_intent,resume='1' if resume else '0',
            autoplay='1' if kind=='episode' else '0',autoplay_chain=self._autoplay_root)
        xbmc.executebuiltin('PlayMedia('+url+')')

    def onClick(self,controlId):
        rail=getattr(self,'_navigation_rail',None)
        if rail and rail.click(controlId):return
        if self._closed or self._leaving:return
        if self._detail_menu_click(controlId):return
        with self._lock:
            self._resume_focus()
            if self._focus_pending is not None:return
            if self._search_click(controlId):return
            if controlId==400:
                if self.getFocusId()==400 and self._mode_focus.get(self.mode)==400:self._search()
                return
            if controlId==120 and hasattr(self,'reader'):
                if getattr(self,'_catalog_missing',False):
                    self.getControl(102).setLabel(tr(32522))
                    from catalog_sync import request
                    request(self.portal,self.kind,self.category,priority=1,force=True)
                    self._request(self._initial,self._initial_ready)
                    return
                self._cols=4;self._page('grid',0)
            elif controlId in (110,210):
                pos=self.getControl(controlId).getSelectedPosition()
                if 0<=pos<len(self.rows): self._focus_item(pos);self._details(self.rows[pos])
            elif controlId in (111,112):
                pos=self.getControl(controlId).getSelectedPosition()
                rows=self.rails[controlId]
                if 0<=pos<len(rows):
                    self._rail_focus[controlId]=rows[pos]['sid'];self._details(rows[pos])
            elif controlId==200:
                pos=self.getControl(200).getSelectedPosition()
                if 0<=pos<len(self.groups):
                    self.category=self.groups[pos]['cid']
                    from catalog_sync import request
                    request(self.portal,self.kind,self.category,priority=1)
                    self._page('grid',0)
            elif controlId==300 and self.mode=='detail':
                pos=self.getControl(300).getSelectedPosition()
                if not 0<=pos<len(self.actions): return
                action=self.actions[pos][1]
                if action in ('play','restart','resume'): self._play(self.selected,'series_item' if self.kind=='series' and self.selected.get('series_flat') else 'vod',action=='resume')
                elif action=='favourite':
                    from media_state import toggle
                    toggle(self.portal['id'],self.kind,self.selected['sid'],self.selected)
                    self._detail_ready((self.selected,{'episodes':self._episode_raw()}))
                elif action=='trailer': self.router._play_youtube_id(self.trailer)
                elif action in ('continue_episode','next_episode'):
                    if action=='next_episode':self._play_next()
                    else:self._play(self.continue_episode,'episode',True)
                elif action=='poster_status':self._poster_status()
                elif action=='seasons':
                    self.mode='seasons';self._show('seasons')
                    self.seasons=sorted({e['season'] for e in self.episodes})
                    self._fill(330,self._season_rows());self.setFocusId(330)
            elif controlId==340 and self.mode=='episodes':
                self._sync_episode_next();self._play_next()
            elif controlId==330:
                pos=self.getControl(330).getSelectedPosition()
                if self.mode=='seasons' and 0<=pos<len(self.seasons):
                    self._season_cursor=pos;self.season=self.seasons[pos];self.mode='episodes'
                    self._show_episodes()
                elif self.mode=='episodes' and 0<=pos<len(self.visible_episodes):
                    self._episode_cursor[self.season]=pos
                    e=self.visible_episodes[pos]
                    from media_state import progress,resume_position
                    saved=progress(self.portal['id'],'episode',e['sid'],e['series_id'],e['season'])
                    resume=bool(resume_position(saved)) and xbmcgui.Dialog().yesno('XCMate',tr(32524))
                    self._play(e,'episode',resume)

    def _poster_status(self):
        item=dict(self.selected)
        def inspect():
            from media_art import poster_report
            return poster_report(item)
        def show(report):
            from media_art import diagnostic_label
            text=diagnostic_label(report['status'])+'\n'+', '.join(k+': '+str(v) for k,v in report.items() if k!='status')
            choice=xbmcgui.Dialog().select(tr(33703),[text,tr(33704)])
            if choice==1:
                def retry():
                    from media_art import retry_poster
                    return retry_poster(item)
                self._request(retry,lambda code:xbmcgui.Dialog().notification('XCMate',diagnostic_label(code)))
        self._request(inspect,show)

    def _episode_raw(self):
        raw={}
        for e in self.episodes:
            raw.setdefault(str(e['season']),[]).append(dict(e,id=e['sid'],title=e['name'],episode_num=e['episode'],info=e))
        return raw

    def _season_rows(self):
        from media_state import read,progress_key
        try: snapshot=read()['progress']
        except (ValueError,OSError,sqlite3.Error): snapshot=None
        rows=[]
        for season in self.seasons:
            episodes=[e for e in self.episodes if e['season']==season]
            values=[snapshot.get(progress_key(self.portal['id'],'episode',e['sid'],e['series_id'],season),{}) for e in episodes] if snapshot is not None else []
            watched=sum(bool(v.get('watched')) for v in values)
            status=tr(32520) if snapshot is None else tr(32525) if episodes and watched==len(episodes) else tr(32526) if any(v.get('position') or v.get('watched') for v in values) else tr(32527)
            rows.append(dict(name=tr(32523)+str(season)+' · '+str(watched)+'/'+str(len(episodes))+' · '+status,sid=str(season)))
        return rows

    def _show_episodes(self):
        self._show('episodes')
        from media_state import read,progress_key
        snapshot=read()['progress']
        self.visible_episodes=[e for e in self.episodes if e['season']==self.season]
        rows=[]
        for e in self.visible_episodes:
            saved=snapshot.get(progress_key(self.portal['id'],'episode',e['sid'],e['series_id'],e['season']),{})
            status=tr(32526) if saved.get('position') and not saved.get('watched') else ''
            duration=saved.get('duration',0);position=saved.get('position',0)
            if isinstance(duration,(int,float)) and isinstance(position,(int,float)) and duration>0:
                status+=' · {} %'.format(max(0,min(100,int(position/duration*100))))
            rows.append(dict(e,name='{} · {}{}'.format(e['episode'],e['name'],' · '+status if status else ''),_watched=bool(saved.get('watched'))))
        self._fill(330,rows);self.getControl(330).selectItem(self._episode_cursor.get(self.season,0))
        self._sync_episode_next();self.setFocusId(330)

    def _next_for_series(self,snapshot=None):
        from media_sequence import ordered,successor
        from media_state import progress_key
        pid,series=str(self.portal['id']),str(self.selected['sid'])
        rows=ordered(self.episodes,pid,series)
        reference=self._episode_refs.get((pid,series))
        if reference is None and rows:
            # Real playback payloads carry position/duration; manual Seen marks
            # alone are never mistaken for a last-played episode.
            saved=[(e,(snapshot or {}).get(progress_key(pid,'episode',e['sid'],series,e['season']),{})) for e in rows]
            played=[(e,p) for e,p in saved if isinstance(p.get('position'),(int,float)) and p['position']>=60
                    and str(p.get('pid',''))==pid and str(p.get('series_id',''))==series]
            reference=max(played,key=lambda pair:pair[1].get('updated',0))[0] if played else rows[0]
        return successor(self.episodes,pid,series,reference)

    def _sync_episode_next(self):
        if self.mode!='episodes' or self._playback_waiting:return
        pos=self.getControl(330).getSelectedPosition()
        key=(str(self.portal['id']),str(self.selected['sid']),id(self.episodes),self.season,pos)
        if key==self._episode_next_key:return
        self._episode_next_key=key
        if 0<=pos<len(self.visible_episodes):
            self._episode_last_pos=pos
            self._episode_cursor[self.season]=pos
            self._episode_refs[(str(self.portal['id']),str(self.selected['sid']))]=self.visible_episodes[pos]
        self.next_episode=self._next_for_series()
        button=self.getControl(340);button.setVisible(self.next_episode is not None)
        if self.next_episode:
            e=self.next_episode;button.setLabel(tr(32517).format(e['season'],e['episode']))
        if self.getFocusId()==340 and self.next_episode is None:self.setFocusId(330)

    def _play_next(self):
        if self._playback_waiting or self.selected.get('_unavailable'):return
        # Revalidate against the current local series, never trust a stale button.
        from media_state import read
        try:snapshot=read()['progress']
        except (ValueError,OSError,sqlite3.Error):snapshot={}
        target=self._next_for_series(snapshot)
        if target is not None:self._play(target,'episode')

    def onAction(self,action):
        if self._leaving:
            from window_navigation import trace
            trace('TRANSITION',self.mode,action.getId(),self._dispatch);return
        if self._closed:
            from window_navigation import trace
            trace('CLOSED_INPUT',self.mode,action.getId());return
        self._action_focus=getattr(self,'_nav_focus',self.getFocusId())
        try: self._handle_action(action)
        finally:
            if not self._closed:self._nav_focus=self.getFocusId()

    def _handle_action(self,action):
        key=action.getId()
        from nav_rail import view_action,open_in_view
        if view_action(self,key):return
        if key==1 and (self.mode=='landing' and self.getFocusId()==120 or self.mode=='groups' and self.getFocusId()==200):
            open_in_view(self,'media');return
        if self._closed:return
        with self._lock:
            if self._detail_menu_action(key):return
            if self._search_action(key):return
            if key in (9,10,92):
                from window_navigation import trace
                trace('BACK',self.mode,key,self._dispatch)
                from media_intent import cancel
                self._cancel_chain()
                cancel(self.portal['id'],self._play_intent)
                from exit_jobs import request as stop_owned
                if self._stop_media_only(): return
                if self._playback_waiting:
                    self._playback_waiting=False;self._playback_seen=False
                    from media_return import discard
                    discard(self)  # Explicit Back also cancels an unresolved start.
                self._generation+=1
                if self.mode=='episodes':
                    self.mode='seasons';self._show('seasons');self._fill(330,self._season_rows())
                    self.getControl(330).selectItem(self._season_cursor);self.setFocusId(330);return
                if self.mode=='seasons':
                    self.mode='detail';self._show('detail')
                    self._detail_ready((self.selected,{'episodes':self._episode_raw()}));self.setFocusId(300);return
                if self.mode=='detail' and self._grid_return:
                    mode,self.category,self.offset,self.rows,self.total,pos,self._cols=self._grid_return
                    self._grid_return=None;self.mode=mode
                    self._positions[(mode,self.category,self.offset)]=pos
                    self._show(mode);self._page_ready((self.rows,self.total));self.setFocusId(210);return
                if self.mode=='detail' and self._previous:
                    mode,self.category,offset,pos=self._previous
                    self._positions[(mode,self.category,offset)]=pos
                    self._restore_rail=getattr(self,'_return_focus',None)
                    self._page(mode,offset);return
                if self.mode=='grid' and self._cols==6:
                    self.mode='groups';self._show('groups');self.setFocusId(200);return
                if self.mode in ('grid','groups'):
                    self._restore_focus=self._mode_focus.get('landing',120)
                    self._cols=4;self._page('landing',0);return
                self._return_home=True
                if getattr(self,'_running',False):
                    # Keep the old native window owning queued input for three
                    # pump ticks. A second intentional Back cannot hit Kodi's
                    # directory before Home has been revealed.
                    self._leaving=True;self._leave_after=time.monotonic()+.15
                else:self.close()
                return
            self._resume_focus()
            if self._focus_pending is not None:return
            if key in (1,2,3,4) and self.getFocusId() in self._valid_focus():
                self._mode_focus[self.mode]=self.getFocusId()
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
                focus=self.getFocusId()
                if self.mode=='landing' and focus==112 and self.kind=='vod':
                    pos=self.getControl(112).getSelectedPosition();rows=self.rails[112]
                    if 0<=pos<len(rows) and xbmcgui.Dialog().select('XCMate',[tr(33202)])==0:
                        from media_continue import hide
                        pid,sid=self.portal['id'],rows[pos]['sid']
                        def saved(_):
                            self._refresh_rails();self.getControl(112).selectItem(min(pos,max(0,len(self.rails[112])-1)))
                            self.setFocusId(112 if self.rails[112] else next((c for c in (111,110) if c in self._valid_focus()),120))
                        self._request(lambda:hide(pid,sid),saved)
                    return
                if self.mode=='landing' and focus==111:
                    rows=self.rails[111];pos=self.getControl(111).getSelectedPosition()
                    if 0<=pos<len(rows):
                        from media_state import toggle
                        toggle(self.portal['id'],self.kind,rows[pos]['sid'])
                        self._refresh_rails()
                        self.setFocusId(111 if self.rails[111] else 120)
                    return
                self._search()
                return
            focus=self.getFocusId()
            previous_focus=getattr(self,'_action_focus',focus)
            if self.mode=='episodes':
                previous_pos=self._episode_last_pos
                self._sync_episode_next()
                if key==2 and previous_focus==330 and self.next_episode:
                    self.setFocusId(340);return
                if key==3 and previous_focus==330 and previous_pos==0 and self.getControl(330).getSelectedPosition()==0:
                    self.setFocusId(340 if self.next_episode else 400);return
                if key==4 and focus==400:self.setFocusId(340 if self.next_episode else 330);return
            if self.mode in ('grid','groups') and previous_focus==210:
                panel=self.getControl(210);pos=panel.getSelectedPosition()
                if key==4:
                    if pos==self._last_position and pos>=len(self.rows)-self._cols:
                        self._prefetch(1,force=True,advance=self.rows[pos]['sid'] if self.rows else None)
                    else:self._prefetch(1)
                    self.setFocusId(210)
                    if 0<=pos<len(self.rows):self._focus_item(pos)
                    return
                if key==3 and pos==self._last_position and pos<self._cols and self.offset:
                    self._prefetch(-1,force=True,advance=self.rows[pos]['sid']);self.setFocusId(210);return
                if key==6:
                    if pos+PAGE<len(self.rows):
                        panel.selectItem(pos+PAGE);self._focus_item(pos+PAGE);self._prefetch()
                    else:self._prefetch(1,force=True,advance=self.rows[pos]['sid'] if self.rows else None)
                    self.setFocusId(210);return
                if key==5 and self.offset:self._prefetch(-1,force=True);self.setFocusId(210);return
            if self.mode=='landing' and focus in (111,112) and key in (1,2):
                pos=self.getControl(focus).getSelectedPosition();rows=self.rails[focus]
                if 0<=pos<len(rows):
                    self._rail_focus[focus]=rows[pos]['sid'];self._queue_art(rows[pos])
                return
            if self.mode=='landing' and key in (3,4) and previous_focus in (110,111,112,120):
                order=[120]+([112] if self.rails[112] else [])+([111] if self.rails[111] else [])+([110] if self.rows else [])
                index=order.index(previous_focus) if previous_focus in order else 0
                self.setFocusId(order[max(0,min(len(order)-1,index+(-1 if key==3 else 1)))])
                return
            if focus==400 and key==4:
                target=next((c for c in (112,111,110) if c in self._valid_focus()),120) if self.mode=='landing' else 120
                if self.mode in ('grid','groups'): target=210 if self.rows else 200
                elif self.mode=='detail':target=300
                elif self.mode=='seasons':target=330
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
            if focus==110 and key==2 and self._last_position==len(self.rows)-1 and self.offset+len(self.rows)<self.total:
                self._page(self.mode,self.offset+PAGE);return
            if key==1 and self._last_position==0 and self.offset and focus==110:
                self._page(self.mode,self.offset-PAGE);return
            if 0<=pos<len(self.rows): self._focus_item(pos)

    def _grid_status(self):
        name=next((g['title'] for g in self.groups if g['cid']==self.category),tr(32499))
        self._page_status=tr(33200,name,self.offset+len(self.rows),self.total)
        if self.offset:self._page_status=tr(33203,name,self.offset+1,self.offset+len(self.rows),self.total)
        if self.total and self.offset+len(self.rows)>=self.total:self._page_status+=' · '+tr(35950)
        self.getControl(102).setLabel(self._page_status)

    def _prefetch(self,direction=1,force=False,advance=None):
        if self.mode not in ('grid','groups') or self._append_failed and not force:return
        pos=self.getControl(210).getSelectedPosition()
        if direction>0:
            if self.offset+len(self.rows)>=self.total:return
            if not force and pos<len(self.rows)-6:return
            start=self.offset+len(self.rows)
        else:
            if not self.offset:return
            start=max(0,self.offset-PAGE)
        if advance:self._append_advance=(advance,direction)
        if self._append_future is not None:return
        context=(self._generation,self.portal['id'],self.kind,self.category,self.mode,self.offset)
        reader,kind,category=self.reader,self.kind,self.category
        limit=PAGE if direction>0 else self.offset-start
        self._append_failed=False;self._append_context=(context,start,direction)
        favourites=self.favourites_only;pid=self.portal['id']
        expected=getattr(self,'_catalog_token43',None)
        def load():
            if favourites:
                from media_state import read
                ids=[json.loads(k)[2] for k in read()['favourites'] if json.loads(k)[:2]==[str(pid),kind]]
                available=[r for sid in ids if (r:=reader.get(kind,sid))]
                rows,total=available[start:start+limit],len(available)
            else:
                from media_page43 import read
                result=read(reader,kind,category,start,limit,expected=expected)
                rows,total=result
            from media_art import request
            request(rows,priority=0)
            return rows,total
        self._append_future=self._pool.submit(load)
        self.getControl(102).setLabel(self._page_status+' · '+tr(33201))

    def _poll_append(self):
        future=self._append_future
        if future is not None and future.done():
            context,start,direction=self._append_context
            self._append_future=None;self._append_context=None
            current=(self._generation,self.portal['id'],self.kind,self.category,self.mode,self.offset)
            if future.cancelled() or context!=current:return
            try:
                rows,total=future.result()
                if not rows and start<total:raise ValueError('Empty catalogue batch')
                if set(r['sid'] for r in self.rows)&set(r['sid'] for r in rows):raise ValueError('Catalogue changed')
                self._append_rows(rows,total,start,direction)
            except Exception as error:
                self._append_failed=True;self._append_advance=None
                from media_page43 import CatalogueChanged
                if isinstance(error,CatalogueChanged):
                    pos=self.getControl(210).getSelectedPosition()
                    self._catalog_restore43=self.rows[pos]['sid'] if 0<=pos<len(self.rows) else None
                    self._page(self.mode,self.offset);return
                self.getControl(102).setLabel(tr(32610))
        if self.mode=='grid' and self.getFocusId()==210 and self.rows:
            self._prefetch()

    def _append_rows(self,rows,total,start,direction):
        panel=self.getControl(210);pos=panel.getSelectedPosition()
        sid=self.rows[pos]['sid'] if 0<=pos<len(self.rows) else ''
        from media_art import local_art
        if direction>0:
            items=[]
            for row in rows:
                li=xbmcgui.ListItem(row['name']);li.setArt(self._display_art39(row));li.setInfo('video',{'title':row['name']});items.append(li)
            panel.addItems(items);self.rows+=rows
            if len(self.rows)>WINDOW_ITEMS:
                trim=((len(self.rows)-WINDOW_ITEMS+PAGE-1)//PAGE)*PAGE
                for _ in range(trim):panel.removeItem(0)
                self.rows=self.rows[trim:];self.offset+=trim
        else:
            self.rows=rows+self.rows;self.offset=start
            self.rows=self.rows[:WINDOW_ITEMS];self._fill(210,self.rows)
        self.total=total
        selected=next((i for i,r in enumerate(self.rows) if r['sid']==sid),0)
        advance=self._append_advance;self._append_advance=None
        if advance and advance[0]==sid and self.getFocusId()==210:
            selected=max(0,min(len(self.rows)-1,selected+advance[1]*self._cols))
        panel.selectItem(selected);self._last_position=selected
        self._positions[(self.mode,self.category,self.offset)]=selected
        self._grid_status()
        if self.getFocusId()==210 and self.rows:self._focus_item(selected)

    def _cancel_chain(self):
        from media_autoplay import request_cancel
        request_cancel(getattr(self,'_autoplay_root',''),self.portal['id'])

    def _chain_active(self):
        root=getattr(self,'_autoplay_root','')
        if not root:return False
        from media_autoplay import view
        state=view(root,self.portal['id'])
        if not state:return False
        self._play_intent=state['nonce'];self._playback_waiting=True
        if state['phase']=='PLAYING':self._playback_seen=True
        if self.selected and str(self.selected['sid'])==state.get('series_id'):
            from media_sequence import match
            episode=match(self.episodes,self.portal['id'],self.selected['sid'],state)
            if episode:
                self._episode_refs[(str(self.portal['id']),str(self.selected['sid']))]=episode
                self.season=episode['season']
                if self.season in getattr(self,'seasons',[]):self._season_cursor=self.seasons.index(self.season)
                rows=[e for e in self.episodes if e['season']==self.season]
                self._episode_cursor[self.season]=next(i for i,e in enumerate(rows) if e['sid']==episode['sid'])
        return True

    def _poll_playback_return(self):
        if not self._playback_waiting or self._leaving or self._closed:return
        if self._chain_active():return
        if getattr(self,'_playback_origin39',None):
            from media_return import restore
            if restore(self):return
        from exit_jobs import blocked
        if blocked():return
        player=xbmc.Player()
        try:
            if player.isPlayingVideo():
                from media_progress import UNIQUE_ID
                if player.getVideoInfoTag().getUniqueID(UNIQUE_ID)==self._play_intent:self._playback_seen=True
                # A transient non-fullscreen frame is not a user exit.
                # Owned Back/Stop handlers publish the explicit stop/return.
                return
            if not self._playback_seen:
                from media_intent import failure,cancel
                failed=failure(self._play_intent,self.portal['id'])
                expired=time.monotonic()-getattr(self,'_playback_started40',time.monotonic())>=20
                if not failed and not expired:return
                if getattr(player,'isPlaying',player.isPlayingVideo)():return
                # A failed/never-started own resolver can be cancelled, but a
                # deadline does NOT authorize Stop on an initializing player.
                cancel(self.portal['id'],self._play_intent);self._cancel_chain()
            if xbmc.getCondVisibility('Window.IsVisible(fullscreenvideo)') or xbmc.getCondVisibility('System.HasActiveModalDialog'):return
        except (AttributeError,RuntimeError):return
        if getattr(self,'_playback_origin39',None):
            from media_return import restore
            if restore(self,natural=True):return
        # Some Kodi skins reveal WindowXML without delivering another onInit.
        # Restore through the owner pump, never a player/worker callback.
        self._playback_waiting=False;self._playback_seen=False
        self._generation+=1
        if self._pending_future is not None:self._pending_future.cancel()
        self._pending_future=None;self._pending_apply=None
        self._show(self.mode)
        if self.mode=='detail':self._detail_ready((self.selected,{'episodes':self._episode_raw()}));self.setFocusId(300)
        elif self.mode=='episodes':self._show_episodes();self.setFocusId(330)
        elif self.mode=='seasons':self._fill(330,self._season_rows());self.setFocusId(330)

    def _search(self):
        self._open_search()

    def close(self):
        self._gui()
        if self._closed: return
        from media_return import discard
        discard(self)
        self._cancel_chain()
        from media_intent import cancel
        cancel(self.portal['id'],self._play_intent)
        if self._append_future is not None:self._append_future.cancel()
        self._append_future=None
        if getattr(self,'_search_root',False):
            from window_lifecycle import capture
            self._search_native_window=capture(self)
        self._closed=True;self._generation+=1;self._watch_stop.set()
        self._pool.shutdown(wait=False,cancel_futures=True)
        super().close()
        self._search_closed()


class MediaWindow(MediaView,xbmcgui.WindowXML):
    pass


def open_media(router,portal,kind,sid='',favourites=False):
    return open_owned_window(MediaWindow,'XCMateMedia.xml',router,portal,kind,sid,favourites)


def open_search(router,portal,query=None,session=''):
    class SearchWindow(MediaView,xbmcgui.WindowXMLDialog):
        _native_surface='dialog'
        def configure(self,*args,**kwargs):
            super().configure(*args,**kwargs)
            self._search_startup=(query,);self._search_root=True;self._search_kind='live'
            self._search_next_session=session
    return open_owned_window(SearchWindow,'XCMateMedia.xml',router,portal,'vod')
