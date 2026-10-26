"""Virtual 8-row native guide, shared UTC time axis and owner-only UI updates."""
import datetime
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import xbmc,xbmcgui
from localization import tr
from owner_dispatch import OwnerDispatch,native_init,open_owned_window
from guide_grid_data import ROWS,SPAN,CELLS,rectangle


class GuideGridWindow(OwnerDispatch,xbmcgui.WindowXMLDialog):
    _native_surface='dialog'
    def configure(self,router,portal,return_view=None):
        self._configure_owner();self.router,self.portal=router,portal
        self._theme=__import__('theme_render').snapshot()
        self._pool=ThreadPoolExecutor(max_workers=1);self._generation=0;self._closed=False;self._ready=False
        self._loading=False;self._leaving=False;self._cells={};self.rows=[];self.groups=[];self.category=''
        self.mode='grid';self._focus_zone='grid';self._header=312;self._views={};self._group_back_after=0;self._input_after=0;self._group_return=None
        self.offset=0;self.total=0;self.row=0;self.cursor=int(time.time());self.origin=self.cursor//1800*1800
        self._last_refresh=0;self._art_revision=0;self._short_revision='';self._return_home=False;self._play_request=None;self._diagnosing=False
        from guide_playback import player_state
        self._entry_player=player_state()
        self._search_request=None;self._search_prompt=False;self._search_return=return_view;self._start_pending=return_view is None;self._start_retry=0
        self._focus_pending=None;self._focus_deadline=0

    @native_init
    def onInit(self):
        if self._ready:return
        self._ready=True
        for cid in range(1000,1000+ROWS*CELLS):self.getControl(cid).setVisible(False)
        for cid,ident in ((310,33101),(311,33102),(312,33103),(313,33104),(314,33105),(315,33106),(501,33602)):
            self.getControl(cid).setLabel(tr(ident))
        self.getControl(200).setVisible(False);self.getControl(201).setVisible(False);self.getControl(202).setVisible(False)
        for r in range(ROWS):self.getControl(730+r).setVisible(False);self.getControl(750+r).setVisible(False)
        self.getControl(101).setLabel(tr(33100))
        if self._search_return is not None:
            for name,value in self._search_return.items():setattr(self,name,value)
            self._search_return=None
            if self.mode=='groups':self._show_groups()
            else:
                if self._focus_zone=='header':self.setFocusId(self._header)
                self._load()
        else:self._initial_load()

    def setFocusId(self,cid):
        if getattr(getattr(self,'_navigation_rail',None),'active',False):return
        if self._closed:return
        control=self.getControl(cid)
        if not control.isVisible() or not xbmc.getCondVisibility('Control.IsEnabled({})'.format(cid)):
            if self._focus_pending!=cid:
                self._focus_pending=cid;self._focus_deadline=time.monotonic()+2
                from window_navigation import trace
                trace('FOCUS_DEFER','guide',cid,getattr(self.router,'_navigation_dispatch',''))
            return
        pending=self._focus_pending;self._focus_pending=None
        super().setFocusId(cid)
        if pending is not None:
            from window_navigation import trace
            trace('FOCUS_READY','guide',cid,getattr(self.router,'_navigation_dispatch',''))

    def _resume_focus(self):
        cid=self._focus_pending
        if cid is None:return
        if time.monotonic()>=self._focus_deadline:
            self._focus_pending=None
            from search_navigation import mark
            mark('FOCUS_TIMEOUT',self.router,'grid',focus=cid,owner=True);return
        self.setFocusId(cid)

    def _initial_load(self):
        self._loading=True;self._background=False;self._last_data_refresh=time.monotonic()
        self.getControl(102).setLabel(tr(33108))
        def load():
            from guide_grid_data import initial
            try:client=self.router._xc(self.portal)
            except (ValueError,AttributeError):client=None
            return initial(self.portal,self.origin,client)
        self._request(load,self._initial_ready)

    def _initial_ready(self,value):
        self._start_pending=not bool(value['groups'])
        self._start_retry=time.monotonic()+2
        self.category=value['category'];self.offset=value['offset'];self.row=value['row']
        self._loaded(value)
        if not self.groups:self._show_groups(refresh=False)

    def _load(self,background=False):
        self._diagnosing=False
        self._background=background;self._last_data_refresh=time.monotonic()
        if not background:
            self._loading=True
            if self._focus_zone=='grid':self.setFocusId(312)
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
        __import__('theme_render').guide_status(self,'ready' if value['rows'] else 'empty')
        self._loading=False;self.rows=value['rows'];self.total=value['total'];self.groups=value['groups']
        if self.groups and self.category not in {g['cid'] for g in self.groups}:
            self.category=self.groups[0]['cid'];self.offset=self.row=0;self._load();return
        self.row=min(self.row,max(0,len(self.rows)-1));self._render()
        from epg_views import prefetch_short_guides
        if self.rows:prefetch_short_guides(self.portal,[row['channel'] for row in self.rows],limit=ROWS)

    def _query_failed(self,exc):
        __import__('theme_render').guide_status(self,'error')
        self._loading=False
        if self.mode=='groups':self.getControl(102).setLabel(tr(33109));return
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
        if self._closed or self._leaving or self.mode=='groups':return
        self._cells={};target=None
        for r in range(ROWS):
            row=self.rows[r] if r<len(self.rows) else None
            self.getControl(730+r).setVisible(row is not None)
            self.getControl(750+r).setVisible(row is not None and r==self.row)
            self.getControl(700+r).setText(row['channel']['name'] if row else '')
            from media_art import local_art
            self.getControl(720+r).setImage(local_art(row['channel'],self._theme)['thumb'] if row else '')
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
        group=next((g['title'] for g in self.groups if g['cid']==self.category),'')
        self.getControl(101).setLabel(tr(33100)+' · '+group+' · '+time.strftime('%a %d.%m.%Y',time.localtime(self.origin)))
        available=sum(bool(r['events']) for r in self.rows)
        self.getControl(102).setLabel(tr(33111,self.offset+1 if self.rows else 0,min(self.total,self.offset+len(self.rows)),self.total,available,len(self.rows))+(' · '+tr(33120) if any(len(r['events'])>CELLS for r in self.rows) else ''))
        self._focus_cell(target)

    def _refresh_logos(self):
        from media_art import local_art
        for r,row in enumerate(self.rows):self.getControl(720+r).setImage(local_art(row['channel'],self._theme)['thumb'])

    def _focus_cell(self,cid=None):
        if cid is None:
            event=self._selected();cid=next((key for key,(r,e) in self._cells.items() if r==self.row and e is event),None)
            if cid is None:cid=next((key for key,(r,e) in self._cells.items() if r==self.row),312)
        if self._focus_zone=='grid':self.setFocusId(cid)
        elif self._focus_zone=='sender' and self.rows:self.setFocusId(730+self.row)
        for r in range(ROWS):self.getControl(750+r).setVisible(r==self.row and r<len(self.rows) and self.mode=='grid')
        event=self._selected()
        self.getControl(103).setLabel((self.rows[self.row]['channel']['name']+' · ' if self.rows else '')+(time.strftime('%H:%M',time.localtime(event['start']))+' – '+time.strftime('%H:%M',time.localtime(event['stop']))+' · '+event['title']) if event else tr(33110))

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
        if candidates:self.cursor=min(candidates) if step>0 else max(self.origin,max(candidates))
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
        choice=xbmcgui.Dialog().select(channel['name'] if channel_only or not event else event['title'],__import__('theme_render').epg_choices(choices,self._theme),useDetails=bool(self._theme))
        if choice==0:
            text=channel['name']+'\n'+tr(33114,row['mapping'])
            if event:text+='\n'+event['title']+'\n'+str(event.get('description') or tr(32553))
            xbmcgui.Dialog().textviewer(tr(33112),text)
        elif choice==1:
            # Only record the selected channel. No close/PlayMedia in a native
            # callback: the owner pump closes after this callback has returned.
            from guide_playback import request
            from window_lifecycle import capture
            self._play_request=request(self.portal,channel,self._entry_player,capture(self))
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
        snapshot=dict(loading=self._loading,cells=len(self._cells))
        def load():
            from guide_grid_diagnostics import inspect
            try:client=router._xc(portal)
            except (AttributeError,ValueError):client=None
            return inspect(portal,row,origin,cursor,focus,client,snapshot)
        self._request(load,self._diagnosed)

    def _diagnosed(self,text):
        self._diagnosing=False
        if not self._leaving:xbmcgui.Dialog().textviewer(tr(33121),text)

    def _grid_visibility(self,visible):
        for cid in list(range(310,316))+list(range(600,606))+list(range(700,708))+list(range(720,728))+list(range(730,738))+list(range(750,758))+list(self._cells):
            self.getControl(cid).setVisible(visible or cid==314)
        self.getControl(500).setVisible(False)
        self.getControl(200).setVisible(not visible and bool(self.groups))
        self.getControl(201).setVisible(not visible and not self.groups)

    def _show_groups(self,refresh=True):
        if self.mode=='grid':
            self._views[self.category]=(self.offset,self.row,self.cursor,self.origin,self._focus_zone)
            self._group_return=(self.category,self.offset,self.row,self.cursor,self.origin,self._focus_zone,self._header,self.rows,self.total)
        self.mode='groups';self._loading=False;self._diagnosing=False
        self._generation+=1
        if self._pending_future is not None:self._pending_future.cancel()
        self._pending_future=None;self._pending_apply=None
        self._group_back_after=time.monotonic()+.15
        self._grid_visibility(False);self._fill_groups()
        if refresh:
            def load():
                from library_index import Reader
                return Reader(self.portal['id']).groups('live')
            self._request(load,self._groups_loaded)

    def _fill_groups(self,selected=None):
        if self.mode!='groups':return
        panel=self.getControl(200);panel.reset()
        panel.addItems([xbmcgui.ListItem(g['title']) for g in self.groups])
        selected=self.category if selected is None else selected
        panel.selectItem(next((i for i,g in enumerate(self.groups) if g['cid']==selected),0))
        self.getControl(200).setVisible(bool(self.groups));self.getControl(201).setVisible(not self.groups)
        self.getControl(201).setLabel(tr(33604))
        self.getControl(101).setLabel(tr(33601));self.getControl(103).setLabel(tr(33603));self.getControl(102).setLabel('')
        self.getControl(501).setLabel(tr(33603))
        # Empty groups retain a focusable explicit Home button.
        self.getControl(202).setVisible(not self.groups)
        self.getControl(202).setLabel(tr(33605))
        self.setFocusId(200 if self.groups else 202)

    def _groups_loaded(self,groups):
        if self.mode!='groups':return
        if self._start_pending and groups:
            self.mode='grid';self._grid_visibility(True);self._initial_load();return
        index=self.getControl(200).getSelectedPosition()
        selected=self.groups[index]['cid'] if self.groups and index<len(self.groups) else self.category
        self.groups=groups;self._fill_groups(selected)

    def _choose_group(self):
        if not self.groups:return
        index=self.getControl(200).getSelectedPosition()
        if not 0<=index<len(self.groups):return
        self._start_pending=False
        self.category=self.groups[index]['cid'];self.mode='grid'
        self.offset,self.row,self.cursor,self.origin,_=self._views.get(self.category,(0,0,self.cursor,self.origin,'grid'))
        self._focus_zone='grid';self._grid_visibility(True);self.getControl(202).setVisible(False)
        # Never display the previous group's channels while the new local page
        # is pending; keep the saved row/offset, but clear only the UI snapshot.
        self.rows=[];self.total=0;self._render()
        self.getControl(501).setLabel(tr(33602));self._load()

    def _return_to_grid(self):
        """Cancel group browsing; restore the exact view without changing settings."""
        snapshot=self._group_return
        if not snapshot or not self.groups:self._leave_home();return
        self._generation+=1
        if self._pending_future is not None:self._pending_future.cancel()
        self._pending_future=None;self._pending_apply=None
        self._diagnosing=False;self._loading=False
        (self.category,self.offset,self.row,self.cursor,self.origin,self._focus_zone,
         self._header,self.rows,self.total)=snapshot
        self._group_return=None;self.mode='grid';self._input_after=time.monotonic()+.15
        self._grid_visibility(True);self.getControl(202).setVisible(False)
        self.getControl(501).setLabel(tr(33602))
        missing=self.category not in {g['cid'] for g in self.groups}
        if missing:
            self.category=self.groups[0]['cid'];self.offset=self.row=0
            self.rows=[];self.total=0;self._focus_zone='grid'
        if self._focus_zone=='header':self.setFocusId(self._header)
        self._render()
        if missing:self._load()

    def _header_focus(self):
        self._focus_zone='header';self.setFocusId(self._header)

    def _leave_home(self):
        self._return_home=True
        if getattr(self,'_running',False):
            self._leaving=True;self._leave_after=time.monotonic()+.15;self._generation+=1
            if self._pending_future is not None:self._pending_future.cancel()
            self._pending_future=None;self._pending_apply=None
        else:self.close()

    def onAction(self,action):
        if self._closed or self._leaving or self._search_prompt or self._focus_pending is not None:return
        key=action.getId();focus=self.getFocusId()
        from nav_rail import view_action,open_in_view
        if view_action(self,key):return
        if self.mode=='groups' and key==1:open_in_view(self,'guide');return
        if key in (9,10,92):
            if time.monotonic()<self._input_after:return
            if self.mode=='grid':self._leave_home()
            elif time.monotonic()>=self._group_back_after:self._return_to_grid()
            return
        if self.mode=='groups':return
        if 310<=focus<=315:self._focus_zone='header';self._header=focus
        elif 730<=focus<730+ROWS:self._focus_zone='sender';self.row=focus-730
        elif focus in self._cells:self._focus_zone='grid'
        if key==117:self._actions(channel_only=True);return
        if key==218:self._header_focus();return  # Kodi ACTION_BLUE, XCMate-local only
        if self._loading:return
        if focus in self._cells and key in (1,2,3,4):
            if key==3 and self.row==0:self._header_focus();return
            if key==1:
                event=self._selected()
                if focus==min((cid for cid,(r,e) in self._cells.items() if r==self.row),default=focus):
                    self._focus_zone='sender';self.setFocusId(730+self.row);self._focus_cell();return
            self._step(key)
        elif 730<=focus<730+ROWS:
            if key==1:self._show_groups()
            elif key==2:self._focus_zone='grid';self._focus_cell()
            elif key in (3,4):
                if key==3 and self.row==0 and self.offset==0:self._header_focus()
                else:self._step(key)
        elif 310<=focus<=315:
            if key==4:self._focus_zone='grid';self._focus_cell()
            elif key==3 and self.offset>=ROWS:
                self.offset-=ROWS;self.row=ROWS-1;self._focus_zone='grid';self._load()

    def onClick(self,cid):
        rail=getattr(self,'_navigation_rail',None)
        if rail and rail.click(cid):return
        if self._closed or self._leaving or self._search_prompt or self._focus_pending is not None:return
        if cid==314:
            from search_navigation import queue
            queue(self,'grid');return
        if self.mode=='groups':
            if cid==200:self._choose_group()
            elif cid==202:self._leave_home()
            return
        if 730<=cid<730+ROWS:
            self.row=cid-730;self._actions(channel_only=True);return
        if cid in self._cells:
            previous=self._selected();self.row,event=self._cells[cid]
            if event is not None and event is not previous:self.cursor=max(self.origin,event['start'])
            self._actions();return
        if cid in (310,311):self._day(-1 if cid==310 else 1)
        elif cid==312:self.cursor=int(time.time());self.origin=self.cursor//1800*1800;self._load()
        elif cid==315:
            local=datetime.datetime.fromtimestamp(self.cursor).replace(hour=20,minute=15,second=0,microsecond=0)
            self.cursor=int(time.mktime(local.timetuple()));self.origin=self.cursor//1800*1800;self._load()
        elif cid==313:self._show_groups()

    def _owner_tick(self):
        if not self._leaving:self._resume_focus()
        if self._leaving:
            if time.monotonic()>=self._leave_after:self.close()
            return
        if self.mode=='groups' and self._start_pending and self._pending_future is None and time.monotonic()>=self._start_retry:
            self._start_retry=time.monotonic()+2
            def groups():
                from library_index import Reader
                return Reader(self.portal['id'],timeout=.15,query_seconds=1).groups('live')
            self._request(groups,self._groups_loaded)
        if self._diagnosing or self.mode=='groups':return
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
    from search_navigation import guide_flow
    return guide_flow(router,portal,open_owned_window,GuideGridWindow,'XCMateGuideGrid.xml','grid')
