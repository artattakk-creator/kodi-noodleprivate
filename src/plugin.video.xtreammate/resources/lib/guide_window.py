"""Full-screen accessible multi-channel day guide; queries off the GUI thread."""
from localization import tr
from owner_dispatch import OwnerDispatch,native_init,open_owned_window
import datetime
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import xbmc
import xbmcgui
import xbmcaddon


class GuideWindow(OwnerDispatch,xbmcgui.WindowXMLDialog):
    _native_surface='dialog'
    def configure(self,router,portal,return_view=None):
        self._configure_owner()
        self._theme=__import__('theme_render').snapshot()
        self._return_home=False
        self._leaving=False;self._search_prompt=False;self._search_request=None;self._search_return=return_view
        self.router,self.portal=router,portal
        self._pool=ThreadPoolExecutor(max_workers=1)
        self._lock=threading.RLock();self._generation=0;self._closed=False;self._ready=False
        self.groups=[];self.channels=[];self.programmes=[];self.category='';self.sid=''
        self.day=0;self.channel_offset=0;self.event_offset=0;self.event_total=0;self.channel_total=0
        self.mappings={};self._last_channel_pos=-1
        self._short_revision='';self._short_poll=0
        from utils import setting_int
        self.days=10 if setting_int('epg_days',7)==10 else 7
        from programme_index46 import available_days
        self.days=max(self.days,available_days(portal['id']))

    def _query_failed(self,exc):
        __import__('theme_render').guide_status(self,'error')
        self._gui()
        self.getControl(102).setLabel(tr(32610))

    @native_init
    def onInit(self):
        for control_id,string_id in ((310,32588),(311,32589),(312,32590),(501,32591)):
            self.getControl(control_id).setLabel(tr(string_id))
        if self._ready: return
        self.getControl(101).setLabel(tr(32604))
        self._ready=True;self._group_view(False)
        self.getControl(102).setLabel(tr(32541))
        def load():
            from library_index import Reader,initial_group
            from guide_store import refresh as refresh_guide
            from epg_sources import configuration
            if not Reader(self.portal['id']).state('live') and self.portal.get('type') in ('xtream','m3u','stb'):
                from catalog_sync import request
                request(self.portal,'live',self.portal.get('start_group_id',''),priority=0)
            reader=Reader(self.portal['id'])
            mappings=configuration(self.portal['id'])['mappings']
            try: refresh_guide(self.portal)
            except Exception: pass  # A failed import does not erase the previous DB.
            groups=reader.groups('live')
            start=reader.get('live',str(self.portal.get('start_stream_id') or ''))
            return reader,mappings,groups,initial_group(self.portal,groups,start)
        self._request(load,self._initial_ready)

    def _fill(self,cid,labels):
        control=self.getControl(cid);control.reset()
        from menu_icons45 import decorate
        control.addItems([decorate(xbmcgui.ListItem(label),'calendar' if cid==220 else 'list',full=True) for label in labels])

    def _initial_ready(self,value):
        self.reader,self.mappings,self.groups,self.category=value
        self._fill(200,[g['title'] for g in self.groups])
        if not self.category:
            self.getControl(102).setLabel(tr(32542))
            self.setFocusId(310);return
        if self._search_return is not None:
            view=self._search_return;self._search_return=None
            self.category=view['category'];self.day=view['day']
            self._search_restore=view
            self._load_channels(view['channel_offset'])
        else:self._load_channels(0)

    def _load_channels(self,offset):
        self.channel_offset=max(0,offset);self._last_channel_pos=-1
        self.channels=[];self.programmes=[];self.event_total=0
        self.getControl(210).reset();self.getControl(220).reset()
        category=self.category
        self._request(lambda:self.reader.page('live',category=category,offset=self.channel_offset,limit=48),self._channels_ready)

    def _channels_ready(self,value):
        self.channels,self.channel_total=value
        from media_art import local_art,request
        self.getControl(210).reset()
        items=[]
        for row in self.channels:
            item=xbmcgui.ListItem(row['name']);item.setArt(local_art(row));items.append(item)
        self.getControl(210).addItems(items)
        self.getControl(210).selectItem(0)
        self.setFocusId(210 if self.channels else 310)
        if self.channels:
            view=getattr(self,'_search_restore',None)
            pos=min(view['channel_pos'],len(self.channels)-1) if view else 0
            self.getControl(210).selectItem(pos)
            if view:self._restore_event=view['event_pos']
            self._load_events(pos,view['event_offset'] if view else 0)
            request(self.channels)
            from epg_views import prefetch_short_guides
            prefetch_short_guides(self.portal,self.channels)

    def _owner_tick(self):
        if getattr(self,'_programme_request46',None):
            from programme_window46 import open_pending
            open_pending(self)
        if self._leaving:
            if time.monotonic()>=self._leave_after:self.close()
            return
        if time.monotonic()-self._short_poll<.5: return
        self._short_poll=time.monotonic()
        revision=xbmcgui.Window(10000).getProperty('XCMate.ShortGuideRevision.'+str(self.portal['id']))
        if revision!=self._short_revision and self._pending_future is None:
            self._short_revision=revision
            if revision and self.channels:
                self._restore_event=self.getControl(220).getSelectedPosition()
                self._load_events(max(0,self._last_channel_pos),self.event_offset)

    def _load_events(self,pos,offset=0):
        if not 0<=pos<len(self.channels): return
        self._last_channel_pos=pos;self.channel=self.channels[pos];self.sid=self.channel['sid']
        self.event_offset=max(0,offset)
        channel=dict(self.channel);day=self.day;page=self.event_offset
        # A quick OK during the next query must not assign a previous
        # channel/day's programme to the newly selected stream/reminder.
        self.programmes=[];self.event_total=0;self.getControl(220).reset()
        date=datetime.date.today()+datetime.timedelta(days=day)
        self.getControl(101).setLabel(tr(32543)+date.strftime(tr(32583))+' · '+channel['name'])
        def load():
            from guide_store import day_window,events,horizon
            from epg import load_cache
            from epg_views import resolve_guide
            # Use precisely the shared mapping/short-EPG resolver for the
            # current programme; the day DB supplies the uncapped remainder.
            client=self.router._xc(self.portal)
            from local_epg import now_next
            info=now_next(self.portal['id'],[channel],self.mappings,client=client).get(channel['sid'],{})
            eid=self.mappings.get(channel['sid']) or channel['sid']
            start,stop=day_window(day)
            rows,total=events(self.portal['id'],eid,start,stop,page)
            if not rows and not self.mappings.get(channel['sid']):
                rows,total=events(self.portal['id'],channel.get('epg_channel_id',''),start,stop,page)
                eid=channel.get('epg_channel_id','')
            if day>=-7:
                from local_epg import window,channel_keys
                from epg_events import deduplicate
                prepared46=window(self.portal['id'],[channel],self.mappings,start,stop,limit=256)
                if prepared46 is not None:
                    for ident46 in channel_keys(channel,self.mappings)[1]:
                        values46=deduplicate(prepared46.get(ident46,[]),channel=ident46)
                        if values46 and (len(values46)>=total or __import__('epg_binding48').binding(self.mappings,channel['sid'])):
                            total=len(values46);rows=values46[page:page+100];break
            if day==0 and page==0 and info.get('mapping')=='SHORT_EPG':
                rows=[dict(e,title=e['title'],description=e.get('description',''),source=-1) for e in info['events']]+[
                    e for e in rows if not info.get('stop') or e['start']>=info['stop']]
                from epg_events import deduplicate
                rows=deduplicate(rows,channel=channel['sid'])[:100];total=max(total,len(rows))
            coverage46=horizon(self.portal['id'],eid)
            from programme_index46 import last_event as last_prepared46
            last46=last_prepared46(self.portal['id'],eid)
            if last46:coverage46['last_event']=max(coverage46.get('last_event') or 0,last46)
            return rows,total,coverage46,info
        self._request(load,self._events_ready)

    def _events_ready(self,value):
        __import__('theme_render').guide_status(self,'ready' if value[0] else 'empty',True)
        self.programmes,self.event_total,horizon,info=value
        now=time.time()
        self._fill(220,[('{} - {} · {}'.format(time.strftime('%H:%M',time.localtime(e['start'])),
            time.strftime('%H:%M',time.localtime(e['stop'])),e['title']))+
            (tr(32544) if e['start']<=now<e['stop'] else '') for e in self.programmes])
        if hasattr(self,'_restore_event'):
            self.getControl(220).selectItem(self._restore_event);del self._restore_event
        last=horizon['last_event']
        limit=tr(32545)+time.strftime(tr(32584),time.localtime(last)) if last else tr(32546)
        self.getControl(102).setLabel(tr(32547).format(
            limit,self.day+1,self.days,self.event_total))
        if not self.programmes:
            self._fill(220,[tr(32548)])
        view=getattr(self,'_search_restore',None)
        if view:
            del self._search_restore
            if view['focus']==200:self._group_view(True)
            self.setFocusId(view['focus'])

    def _group_view(self,expanded):
        __import__('theme_render').guide_status(self,'loading')
        self.getControl(200).setVisible(expanded)
        self.getControl(210).setVisible(not expanded)

    def _day(self,step):
        target=self.day+step
        if -7<=target<self.days:
            self.day=target
            if self.channels: self._load_events(max(0,self.getControl(210).getSelectedPosition()))

    def onAction(self,action):
        if self._closed or self._leaving or self._search_prompt:return
        key=action.getId();focus=self.getFocusId()
        with self._lock:
            if key==117:
                from search_navigation import queue
                queue(self,'guide')
                return
            if key in (9,10,92):
                if focus==200: self._group_view(False);self.setFocusId(210 if self.channels else 310)
                elif focus==220: self.setFocusId(210 if self.channels else 310)
                else: self._return_home=True;self.close()
                return
            if key==1:
                if focus==220: self.setFocusId(210 if self.channels else 310)
                elif focus==210: self._group_view(True);self.setFocusId(200)
                return
            if key==2 and focus==200:
                self._group_view(False);self.setFocusId(210 if self.channels else 310);return
            if focus==210:
                pos=self.getControl(210).getSelectedPosition()
                if key in (5,6):
                    offset=self.channel_offset+(-48 if key==5 else 48)
                    if 0<=offset<self.channel_total: self._load_channels(offset)
                elif pos!=self._last_channel_pos: self._load_events(pos)
            elif focus==220 and key in (5,6):
                offset=self.event_offset+(-100 if key==5 else 100)
                if 0<=offset<self.event_total: self._load_events(self._last_channel_pos,offset)

    def onClick(self,controlId):
        if self._closed or self._leaving or self._search_prompt:return
        if controlId in (310,311): self._day(-1 if controlId==310 else 1);return
        if controlId==312:
            xbmc.executebuiltin('RunPlugin('+self.router.url(action='epg_status',pid=self.portal['id'])+')');return
        if controlId==200:
            pos=self.getControl(200).getSelectedPosition()
            if 0<=pos<len(self.groups):
                self.category=self.groups[pos]['cid'];self._group_view(False);self._load_channels(0)
        elif controlId==210 and self.channels: self.setFocusId(220)
        elif controlId==220:
            pos=self.getControl(220).getSelectedPosition()
            if not 0<=pos<len(self.programmes): return
            event=self.programmes[pos]
            choices=[tr(32549),tr(32550)]
            if event['start']>time.time(): choices.append(tr(32551))
            selected=__import__('menu_icons45').select(xbmcgui.Dialog(),event['title'],__import__('theme_render').epg_choices(choices,self._theme),useDetails=bool(self._theme),default='calendar')
            if selected==0:
                from programme_window46 import request
                request(self,self.channel,event)
            elif selected==1:
                self.close()
                xbmc.executebuiltin('PlayMedia('+self.router.url(action='play_live',pid=self.portal['id'],sid=self.sid,name=self.channel['name'])+')')
            elif selected==2:
                from guide_timers import request_add45 as add
                if add(self.portal['id'],self.sid,self.channel['name'],event):
                    xbmcgui.Dialog().notification('XCMate',tr(32557))

    def close(self):
        self._gui()
        if self._closed: return
        self._closed=True;self._generation+=1
        self._pool.shutdown(wait=False,cancel_futures=True);super().close()


def open_guide(router,portal):
    from search_navigation import guide_flow
    return guide_flow(router,portal,open_owned_window,GuideWindow,'XCMateGuide.xml','guide')
