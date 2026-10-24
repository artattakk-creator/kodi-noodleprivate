"""Search stays inside the existing native window, never Container.Update."""
import time
import uuid
import xbmc
import xbmcgui
from localization import tr

KINDS=('live','vod','series')
LABELS=(33900,33901,33902)
FIELDS=('mode','kind','category','offset','rows','total','selected','groups','_previous',
        '_grid_return','_return_focus','episodes','next_episode','season','seasons')


def mark(event,correlation=''):
    allowed=('SEARCH_INPUT_ACCEPTED','SEARCH_GUI_READY','SEARCH_RETURN','SEARCH_RESULT_READY','SEARCH_WORKER_FAILED','SEARCH_WINDOW_CLOSED','SEARCH_WORKER_STOP_PENDING','SEARCH_RESUMED','SEARCH_CLICK_IGNORED')
    if event not in allowed:return
    try:
        xbmc.log('[XCMate][SEARCH] event={} ms={} dispatch={} window={} owner={}'.format(
            event,int(time.monotonic()*1000),correlation if len(correlation)==32 else '',
            xbmcgui.getCurrentWindowId(),__import__('threading').get_ident()),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass


def handoff(router,portal,window):
    intent=getattr(window,'_search_live',None)
    if intent:
        # Native input/pump and navigation lease must have finished first.
        if not window._closed or getattr(window,'_running',False):return False
        from search_live import handoff as play
        play(router,portal,intent)


class SearchMixin:
    def _search_closed(self):
        if not hasattr(self,'_search_correlation'):return
        from search_navigation import mark as nav_mark
        nav_mark('SEARCH_CLOSED',self.router,'media',self._search_correlation,owner=True)
        mark('SEARCH_WINDOW_CLOSED',self._search_correlation)
        future=getattr(self,'_pending_future',None)
        if future is not None and not future.done():mark('SEARCH_WORKER_STOP_PENDING',self._search_correlation)

    def _search_tick(self):
        startup=getattr(self,'_search_startup',None)
        if startup is not None:
            self._search_startup=None;self._open_search(startup[0])
        if self.mode!='search' or self._closed or self._leaving:return
        now=time.monotonic()
        if now<getattr(self,'_search_art_poll',0):return
        self._search_art_poll=now+.5
        from media_art import revision,local_art
        current=revision()
        if current==getattr(self,'_search_art_revision',None):return
        self._search_art_revision=current
        # Update existing ListItems; never reset selection/focus for an image.
        control=self.getControl(710)
        for pos,row in enumerate(getattr(self,'_search_rows',[])):
            if pos<control.size():control.getListItem(pos).setArt(local_art(dict(row,kind=self._search_kind),self._theme))

    def _open_search(self,query=None):
        if self._closed or self._leaving or getattr(self,'_search_prompt',False):return
        self._search_prompt=True
        try:
            if query is None:query=xbmcgui.Dialog().input(tr(32534),defaultt=getattr(self,'_search_query',''))
        finally:self._search_prompt=False
        query=str(query or '').strip()[:200]
        if not query:
            if getattr(self,'_search_root',False) and not hasattr(self,'_search_origin'):self.close()
            return
        session=getattr(self,'_search_next_session','');self._search_next_session=''
        self._search_correlation=session if len(session)==32 and all(c in '0123456789abcdef' for c in session) else uuid.uuid4().hex
        mark('SEARCH_INPUT_ACCEPTED',self._search_correlation)
        if not hasattr(self,'_search_origin'):
            self._search_origin={name:getattr(self,name) for name in FIELDS if hasattr(self,name)}
            self._search_origin_focus=self.getFocusId()
        self._search_query=query;self._search_kind=getattr(self,'_search_kind',self.kind)
        if self._search_kind not in KINDS:self._search_kind='vod'
        self._search_offset=0;self._search_selected=0;self._search_rows=[];self._search_data={};self._search_loading=True
        self._search_continuation=None;self._search_rendered=None
        self.mode='search';self._show('search')
        for pos,label in enumerate(LABELS):self.getControl(700+pos).setLabel(tr(label)+' (…)')
        self.getControl(720).setLabel(tr(32475));self.getControl(721).setLabel(tr(32476))
        self.getControl(103).setLabel(tr(33903))
        self.getControl(102).setLabel(tr(33904));self._fill(710,[])
        self.setFocusId(700+KINDS.index(self._search_kind))
        self._search_load()
        mark('SEARCH_GUI_READY',self._search_correlation)
        from search_navigation import mark as nav_mark
        nav_mark('SEARCH_OPEN',self.router,'media',self._search_correlation,self.getFocusId(),True)

    def _search_load(self):
        from search_data import search
        portal=dict(self.portal);query=self._search_query;kind=self._search_kind;offset=self._search_offset
        cursor=getattr(self,'_search_continuation',None);self._search_continuation=None
        session=self._search_correlation
        if cursor is None:self._search_loading=True
        def apply(value):
            if (not self._closed and not self._leaving and self.mode=='search' and
                session==self._search_correlation and kind==self._search_kind and offset==self._search_offset):
                self._search_ready(value)
        self._request(lambda:search(portal,query,kind,offset,incremental=True,continuation=cursor,correlation=session),apply)

    def _search_ready(self,value,resume=False):
        if self.mode!='search' or self._closed or self._leaving:return
        cursor=value.get('_continuation') if not resume else None
        value={k:v for k,v in value.items() if k!='_continuation'}
        if not resume:self._search_loading=False
        self._search_data=value
        old_focus=self._mode_focus.get('search',self.getFocusId()) if resume else self.getFocusId()
        old_position=self.getControl(710).getSelectedPosition()
        self.getControl(103).setLabel(tr(33903)+' · '+self._search_query)
        for pos,kind in enumerate(KINDS):
            count=value[kind]['total']
            self.getControl(700+pos).setLabel(tr(LABELS[pos])+' ('+(str(count)+('+' if value[kind].get('partial') else '') if count is not None else '…')+')')
        section=value[self._search_kind];self._search_rows=section['rows']
        rows=[dict(row,kind=self._search_kind) for row in self._search_rows]
        signature=tuple((str(row.get('sid','')),row.get('name',''),row.get('_now_title','')) for row in rows)
        if resume or signature!=getattr(self,'_search_rendered',None):
            self._fill(710,rows);self._search_rendered=signature
        self.getControl(710).selectItem(old_position if old_focus==710 else getattr(self,'_search_selected',0))
        self.getControl(102).setLabel(tr(33906) if section['code']=='INDEX_ERROR' else tr(33904) if section['total'] is None else
            tr(33907) if not rows else '{}–{} / {}'.format(self._search_offset+1,self._search_offset+len(rows),section['total']))
        self.getControl(501).setLabel(tr(33908) if section['code'] in ('NO_EPG','NO_CURRENT_EPG','EPG_UNAVAILABLE','EPG_PARTIAL') else '')
        self.getControl(720).setVisible(self._search_offset>0)
        self.getControl(721).setVisible(bool(section['total'] and self._search_offset+len(rows)<section['total']))
        # Never turn the keyboard's finishing OK into a first-result click.
        # Keep the tab until the user explicitly moves down to the results.
        target=old_focus if old_focus in self._valid_focus() else 700+KINDS.index(self._search_kind)
        self.setFocusId(target)
        mark('SEARCH_RESULT_READY',self._search_correlation)
        if cursor is not None:
            self._search_continuation=cursor;self._search_load()

    def _search_click(self,cid):
        if self.mode!='search':return False
        if getattr(self,'_search_prompt',False) or self._focus_pending is not None:return True
        if cid not in (400,700,701,702,710,720,721):
            mark('SEARCH_CLICK_IGNORED',self._search_correlation);return True
        if cid==710 and self.getFocusId()!=710:
            mark('SEARCH_CLICK_IGNORED',self._search_correlation);return True
        if cid in (700,701,702):
            self._search_kind=KINDS[cid-700];self._search_offset=0;self._search_selected=0
            self.setFocusId(cid);self._search_load();return True
        if cid in (720,721):
            self._search_offset=max(0,self._search_offset+(-48 if cid==720 else 48));self._search_selected=0;self._search_load();return True
        if cid!=710:return False
        if self._search_loading:return True
        pos=self.getControl(710).getSelectedPosition()
        if not 0<=pos<len(self._search_rows):return True
        item=self._search_rows[pos]
        self._search_selected=pos
        if self._search_kind=='live':
            from guide_playback import request,player_state
            self._search_live=request(self.portal,item,player_state())
            try:self._search_live['window']=int(xbmcgui.getCurrentWindowId())
            except (AttributeError,RuntimeError):self._search_live['window']=None
            self._leaving=True;self._leave_after=time.monotonic()+.15
        else:
            self.kind=self._search_kind;self._grid_return=None;self._search_detail=True
            self._details(item)
        return True

    def _search_action(self,key):
        if getattr(self,'_search_prompt',False):return True
        if key in (9,10,92) and self.mode=='detail' and getattr(self,'_search_detail',False):
            self._search_detail=False;self._generation+=1;self.mode='search';self._show('search')
            self._search_ready(self._search_data);return True
        if self.mode!='search':return False
        if key in (9,10,92):
            self._generation+=1
            if self._pending_future is not None:self._pending_future.cancel()
            mark('SEARCH_RETURN',self._search_correlation)
            if getattr(self,'_search_root',False):
                if getattr(self,'_running',False):self._leaving=True;self._leave_after=time.monotonic()+.15
                else:self.close()
                return True
            origin=self._search_origin;del self._search_origin
            for name,value in origin.items():setattr(self,name,value)
            self._show(self.mode)
            if self.mode=='detail':self._detail_ready((self.selected,{'episodes':self._episode_raw()}))
            elif self.mode=='episodes':self._show_episodes()
            elif self.mode=='seasons':self._fill(330,self._season_rows())
            else:self._page_ready((self.rows,self.total))
            self.setFocusId(self._search_origin_focus);return True
        focus=self.getFocusId()
        if key in (1,2) and focus in (700,701,702):
            self.setFocusId(700+(focus-700+(-1 if key==1 else 1))%3);return True
        if key==4 and focus in (400,700,701,702):
            self.setFocusId(710 if self._search_rows else 700+KINDS.index(self._search_kind));return True
        if key==3 and focus==710 and self.getControl(710).getSelectedPosition()==0:
            self.setFocusId(700+KINDS.index(self._search_kind));return True
        if key==117:self._open_search();return True
        return key in (1,2,3,4,5,6,7)
