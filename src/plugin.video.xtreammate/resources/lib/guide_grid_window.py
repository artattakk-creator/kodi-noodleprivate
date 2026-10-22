"""Virtual 8-row native guide, shared UTC time axis and owner-only UI updates."""
import datetime
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import xbmc,xbmcgui
from localization import tr
from owner_dispatch import OwnerDispatch,native_init,open_owned_window
from guide_grid_data import ROWS,SPAN,CELLS,rectangle


class GuideGridWindow(OwnerDispatch,xbmcgui.WindowXML):
    def configure(self,router,portal):
        self._configure_owner();self.router,self.portal=router,portal
        self._pool=ThreadPoolExecutor(max_workers=1);self._generation=0;self._closed=False;self._ready=False
        self._loading=False;self._leaving=False;self._cells={};self.rows=[];self.groups=[];self.category=None
        self.offset=0;self.total=0;self.row=0;self.cursor=int(time.time());self.origin=self.cursor//1800*1800
        self._last_refresh=0;self._art_revision=0;self._short_revision='';self._return_home=False;self._play_request=None;self._diagnosing=False
        from guide_playback import player_state
        self._entry_player=player_state()

    @native_init
    def onInit(self):
        if self._ready:return
        self._ready=True
        for cid in range(1000,1000+ROWS*CELLS):self.getControl(cid).setVisible(False)
        for cid,ident in ((310,33101),(311,33102),(312,33103),(313,33104),(314,33105),(315,33106),(501,33107)):
            self.getControl(cid).setLabel(tr(ident))
        self.getControl(101).setLabel(tr(33100));self._load()

    def _load(self,background=False):
        self._diagnosing=False
        self._background=background;self._last_data_refresh=time.monotonic()
        if not background:self._loading=True;self.setFocusId(312)
        self.getControl(102).setLabel(tr(33108))
        origin,offset,category=self.origin,self.offset,self.category
        router,portal=self.router,self.portal
        def load():
            from guide_grid_data import page
            try:client=router._xc(portal)
            except (ValueError,AttributeError):client=None
            return page(portal,offset,origin,category,client)
        self._request(load,self._loaded)

    def _loaded(self,value):
        self._loading=False;self.rows=value['rows'];self.total=value['total'];self.groups=value['groups']
        self.row=min(self.row,max(0,len(self.rows)-1));self._render()
        from epg_views import prefetch_short_guides
        if self.rows:prefetch_short_guides(self.portal,[row['channel'] for row in self.rows],limit=ROWS)

    def _query_failed(self,exc):
        self._loading=False
        if self._diagnosing:
            self._diagnosing=False;self.getControl(102).setLabel(tr(33109));return
        if not self._background:self.rows=[];self._render();self.setFocusId(312)
        self.getControl(102).setLabel(tr(33109))

    def _selected(self):
        if not self.rows:return None
        events=self.rows[self.row]['events']
        containing=[e for e in events if e['start']<=self.cursor<e['stop']]
        if containing:return max(containing,key=lambda e:e['start'])
        return min(events,key=lambda e:min(abs(e['start']-self.cursor),abs(e['stop']-self.cursor))) if events else None

    def _render(self):
        if self._closed or self._leaving:return
        self._cells={};target=None
        for r in range(ROWS):
            row=self.rows[r] if r<len(self.rows) else None
            self.getControl(700+r).setText(row['channel']['name'] if row else '')
            from media_art import local_art
            self.getControl(720+r).setImage(local_art(row['channel'])['thumb'] if row else '')
            candidates=[e for e in row['events'] if rectangle(e['start'],e['stop'],self.origin)] if row else []
            selected=self._selected() if r==self.row else None
            # If an unusually dense schedule exceeds the native pool, pan to
            # the selected event rather than silently making it unreachable.
            if selected and selected in candidates and candidates.index(selected)>=CELLS:
                self.origin=selected['start'];self._load();return
            for c in range(CELLS):
                cid=1000+r*CELLS+c;control=self.getControl(cid);event=candidates[c] if c<len(candidates) else None
                empty=bool(row and not candidates and c==0)
                control.setVisible(event is not None or empty)
                if event is None and not empty:continue
                geometry=rectangle(event['start'],event['stop'],self.origin) if event else (0,896)
                x,width=geometry;control.setPosition(340+x,168+r*56);control.setWidth(max(1,width-2))
                control.setLabel(event['title'] if event else tr(33110))
                self._cells[cid]=(r,event)
                if r==self.row and (event is selected or (selected is None and (empty or target is None))):target=cid
        for tick in range(6):
            self.getControl(600+tick).setLabel(time.strftime('%H:%M',time.localtime(self.origin+tick*1800)))
        now=time.time();delta=(now-self.origin)*896/SPAN;marker=self.getControl(500)
        marker.setVisible(0<=delta<896)
        if 0<=delta<896:marker.setPosition(340+int(delta),166)
        self.getControl(101).setLabel(tr(33100)+' · '+time.strftime('%a %d.%m.%Y',time.localtime(self.origin)))
        available=sum(bool(r['events']) for r in self.rows)
        self.getControl(102).setLabel(tr(33111,self.offset+1 if self.rows else 0,min(self.total,self.offset+len(self.rows)),self.total,available,len(self.rows))+(' · '+tr(33120) if any(len(r['events'])>CELLS for r in self.rows) else ''))
        self._focus_cell(target)

    def _refresh_logos(self):
        from media_art import local_art
        for r,row in enumerate(self.rows):self.getControl(720+r).setImage(local_art(row['channel'])['thumb'])

    def _focus_cell(self,cid=None):
        if cid is None:
            event=self._selected();cid=next((key for key,(r,e) in self._cells.items() if r==self.row and e is event),None)
            if cid is None:cid=next((key for key,(r,e) in self._cells.items() if r==self.row),312)
        self.setFocusId(cid)
        event=self._selected()
        self.getControl(103).setLabel((time.strftime('%H:%M',time.localtime(event['start']))+' – '+time.strftime('%H:%M',time.localtime(event['stop']))+' · '+event['title']) if event else tr(33110))

    def _step(self,direction):
        if self._loading:return
        if direction in (3,4):
            target=self.row+(-1 if direction==3 else 1)
            if 0<=target<len(self.rows):self.row=target;self._focus_cell();return
            offset=self.offset+(-ROWS if direction==3 else ROWS)
            if 0<=offset<self.total:
                self.offset=offset;self.row=ROWS-1 if direction==3 else 0;self._load()
            return
        if not self.rows:return
        events=self.rows[self.row]['events'];selected=self._selected();step=-1 if direction==1 else 1
        # Adjacent array entries can overlap or be nearest to a gap. Their
        # start may be behind the cursor: never let Right repeat/jump backwards.
        boundary=selected['start'] if step<0 and selected and selected['start']<=self.cursor else self.cursor
        candidates=[e['start'] for e in events if (e['start']>boundary if step>0 else e['start']<boundary)]
        if candidates:self.cursor=min(candidates) if step>0 else max(candidates)
        else:self.cursor+=step*1800
        if not self.origin<=self.cursor<self.origin+SPAN:
            self.origin=self.cursor//1800*1800;self._load()
        else:self._render()

    def _day(self,step):
        date=datetime.datetime.fromtimestamp(self.cursor)+datetime.timedelta(days=step)
        # The local calendar decides the UTC delta across 23/25-hour DST days.
        target=int(time.mktime(date.timetuple()))
        if not 0<=(date.date()-datetime.date.today()).days<=9:return
        self.cursor=target;self.origin=target//1800*1800;self._load()

    def _actions(self,channel_only=False):
        if self._closed or self._leaving or self._loading or not self.rows:return
        row=self.rows[self.row];channel=row['channel'];event=self._selected()
        choices=[tr(33112),tr(32550),tr(33118),tr(33121)]
        if event and not channel_only:
            if event['start']>time.time():choices.append(tr(32551))
            choices.append(tr(33113))
        choice=xbmcgui.Dialog().select(channel['name'] if channel_only or not event else event['title'],choices)
        if choice==0:
            text=channel['name']+'\n'+tr(33114,row['mapping'])
            if event:text+='\n'+event['title']+'\n'+str(event.get('description') or tr(32553))
            xbmcgui.Dialog().textviewer(tr(33112),text)
        elif choice==1:
            # Only record the selected channel. No close/PlayMedia in a native
            # callback: the owner pump closes after this callback has returned.
            from guide_playback import request
            self._play_request=request(self.portal,channel,self._entry_player)
            try:self._play_request['window']=int(xbmcgui.getCurrentWindowId())
            except (AttributeError,RuntimeError):self._play_request['window']=None
            self._leaving=True;self._leave_after=time.monotonic()+.15
            self._generation+=1
            if self._pending_future is not None:self._pending_future.cancel()
            self._pending_future=None;self._pending_apply=None
        elif 0<=choice<len(choices) and choices[choice]==tr(33121):
            self._diagnose()
        elif 0<=choice<len(choices) and choices[choice]==tr(33118):
            from guide_bookmarks import entries
            entries=entries(self.portal['id'])
            text='\n'.join(time.strftime('%d.%m. %H:%M',time.localtime(e['start']))+' · '+e['title'] for e in entries)
            xbmcgui.Dialog().textviewer(tr(33118),text or tr(33119))
        elif 0<=choice<len(choices) and choices[choice]==tr(32551):
            from guide_timers import add
            if add(self.portal['id'],channel['sid'],channel['name'],event):xbmcgui.Dialog().notification('XCMate',tr(32557))
        elif 0<=choice<len(choices) and choices[choice]==tr(33113):
            if xbmcgui.Dialog().yesno('XCMate',tr(33115)):
                from guide_bookmarks import remember
                remember(self.portal['id'],channel['sid'],event)
                xbmcgui.Dialog().notification('XCMate',tr(33116))
        # Recording/Catch-up/TMDB are not advertised as working capabilities.

    def _diagnose(self):
        if self._diagnosing:return
        self._diagnosing=True
        portal,router=self.portal,self.router
        row=self.rows[self.row];origin,cursor,focus=self.origin,self.cursor,self.getFocusId()
        def load():
            from guide_grid_diagnostics import inspect
            try:client=router._xc(portal)
            except (AttributeError,ValueError):client=None
            return inspect(portal,row,origin,cursor,focus,client)
        self._request(load,self._diagnosed)

    def _diagnosed(self,text):
        self._diagnosing=False
        if not self._leaving:xbmcgui.Dialog().textviewer(tr(33121),text)

    def onAction(self,action):
        if self._closed or self._leaving:return
        key=action.getId();focus=self.getFocusId()
        if key in (9,10,92):
            self._return_home=True
            if getattr(self,'_running',False):
                self._leaving=True;self._leave_after=time.monotonic()+.15;self._generation+=1
                if self._pending_future is not None:self._pending_future.cancel()
                self._pending_future=None
            else:self.close()
            return
        if key==117:self._actions(channel_only=True);return
        if focus in self._cells and key in (1,2,3,4):self._step(key)
        elif focus<1000 and key==4 and not self._loading:self._focus_cell()

    def onClick(self,cid):
        if self._closed or self._leaving:return
        if cid in self._cells:
            previous=self._selected();self.row,event=self._cells[cid]
            if event is not None and event is not previous:self.cursor=max(self.origin,event['start'])
            self._actions();return
        if cid in (310,311):self._day(-1 if cid==310 else 1)
        elif cid==312:self.cursor=int(time.time());self.origin=self.cursor//1800*1800;self._load()
        elif cid==315:
            local=datetime.datetime.fromtimestamp(self.cursor).replace(hour=20,minute=15,second=0,microsecond=0)
            self.cursor=int(time.mktime(local.timetuple()));self.origin=self.cursor//1800*1800;self._load()
        elif cid==313:
            selected=xbmcgui.Dialog().select(tr(33104),[tr(33117)]+[g['title'] for g in self.groups])
            if 0<=selected<=len(self.groups):self.category=None if selected==0 else self.groups[selected-1]['cid'];self.offset=self.row=0;self._load()
        elif cid==314:
            query=xbmcgui.Dialog().input(tr(32534))
            if query.strip():
                self._next_route=self.router.url(action='global_search',pid=self.portal['id'],q=query[:200]);self.close()

    def _owner_tick(self):
        if self._leaving:
            if time.monotonic()>=self._leave_after:self.close()
            return
        if self._diagnosing:return
        # Poll only revision hints/time. Direction keys do not query the DB.
        now=time.monotonic()
        if now-self._last_refresh<2:return
        self._last_refresh=now
        from media_art import revision as art_revision
        value=art_revision()
        if value!=self._art_revision:self._art_revision=value;self._refresh_logos()
        revision=xbmcgui.Window(10000).getProperty('XCMate.ShortGuideRevision.'+str(self.portal['id']))
        if revision!=self._short_revision and self._pending_future is None:
            self._short_revision=revision
            if revision:self._load(background=True)
        if self._pending_future is None and now-self._last_data_refresh>=30:self._load(background=True)
        if not self._loading:
            delta=(time.time()-self.origin)*896/SPAN;self.getControl(500).setVisible(0<=delta<896)
            if 0<=delta<896:self.getControl(500).setPosition(340+int(delta),166)

    def close(self):
        self._gui()
        if self._closed:return
        self._closed=True;self._generation+=1
        if self._pending_future is not None:self._pending_future.cancel()
        self._pending_future=None;self._pending_apply=None
        self._pool.shutdown(wait=False,cancel_futures=True);super().close()


def open_grid(router,portal):
    window=open_owned_window(GuideGridWindow,'XCMateGuideGrid.xml',router,portal)
    if getattr(window,'_next_route',''):xbmc.executebuiltin('Container.Update('+window._next_route+')')
    intent=window._play_request
    # Do not return or retain the WindowXML through the playback transition.
    del window
    return intent
