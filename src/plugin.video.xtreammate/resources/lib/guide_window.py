"""Full-screen accessible multi-channel day guide; queries off the GUI thread."""
from localization import tr
import datetime
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import xbmc
import xbmcgui
import xbmcaddon


class GuideWindow(xbmcgui.WindowXML):
    def configure(self,router,portal):
        self.router,self.portal=router,portal
        self._pool=ThreadPoolExecutor(max_workers=1)
        self._lock=threading.RLock();self._generation=0;self._closed=False;self._ready=False
        self.groups=[];self.channels=[];self.programmes=[];self.category='';self.sid=''
        self.day=0;self.channel_offset=0;self.event_offset=0;self.event_total=0;self.channel_total=0
        self.mappings={};self._last_channel_pos=-1
        from utils import setting_int
        self.days=10 if setting_int('epg_days',7)==10 else 7

    def _request(self,job,apply):
        self._generation+=1;generation=self._generation
        future=self._pool.submit(job)
        def done(result):
            try: value=result.result()
            except Exception as exc:
                with self._lock:
                    if not self._closed and generation==self._generation:
                        self.getControl(102).setLabel(tr(32539)+type(exc).__name__+tr(32540))
                return
            with self._lock:
                if not self._closed and generation==self._generation: apply(value)
        future.add_done_callback(done)

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
            if self.portal.get('type')=='xtream':
                from catalog_sync import request
                request(self.portal,'live',self.portal.get('start_group_id',''),priority=0)
            self.reader=Reader(self.portal['id'])
            self.mappings=configuration(self.portal['id'])['mappings']
            try: refresh_guide(self.portal)
            except Exception: pass  # A failed import does not erase the previous DB.
            groups=self.reader.groups('live')
            start=self.reader.get('live',str(self.portal.get('start_stream_id') or ''))
            return groups,initial_group(self.portal,groups,start)
        self._request(load,self._initial_ready)

    def _fill(self,cid,labels):
        control=self.getControl(cid);control.reset();control.addItems([xbmcgui.ListItem(label) for label in labels])

    def _initial_ready(self,value):
        self.groups,self.category=value
        self._fill(200,[g['title'] for g in self.groups])
        if not self.category:
            self.getControl(102).setLabel(tr(32542))
            self.setFocusId(310);return
        self._load_channels(0)

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
            self._load_events(0)
            request(self.channels)

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
            client=self.router._xc(self.portal) if self.portal.get('type')=='xtream' else None
            info=resolve_guide(load_cache(self.portal['id']),channel.get('epg_channel_id',''),channel['sid'],
                               client=client,mappings=self.mappings)
            eid=self.mappings.get(channel['sid']) or channel['sid']
            start,stop=day_window(day)
            rows,total=events(self.portal['id'],eid,start,stop,page)
            if not rows and not self.mappings.get(channel['sid']):
                rows,total=events(self.portal['id'],channel.get('epg_channel_id',''),start,stop,page)
                eid=channel.get('epg_channel_id','')
            if day==0 and page==0 and info.get('mapping')=='SHORT_EPG':
                rows=[dict(e,title=e['title'],description=e.get('description',''),source=-1) for e in info['events']]+[
                    e for e in rows if not info.get('stop') or e['start']>=info['stop']]
                unique={ (e['start'],e['stop']):e for e in rows }
                rows=sorted(unique.values(),key=lambda e:e['start'])[:100];total=max(total,len(rows))
            return rows,total,horizon(self.portal['id'],eid),info
        self._request(load,self._events_ready)

    def _events_ready(self,value):
        self.programmes,self.event_total,horizon,info=value
        now=time.time()
        self._fill(220,[('{} - {} · {}'.format(time.strftime('%H:%M',time.localtime(e['start'])),
            time.strftime('%H:%M',time.localtime(e['stop'])),e['title']))+
            (tr(32544) if e['start']<=now<e['stop'] else '') for e in self.programmes])
        last=horizon['last_event']
        limit=tr(32545)+time.strftime(tr(32584),time.localtime(last)) if last else tr(32546)
        self.getControl(102).setLabel(tr(32547).format(
            limit,self.day+1,self.days,self.event_total))
        if not self.programmes:
            self._fill(220,[tr(32548)])

    def _group_view(self,expanded):
        self.getControl(200).setVisible(expanded)
        self.getControl(210).setVisible(not expanded)

    def _day(self,step):
        target=self.day+step
        if 0<=target<self.days:
            self.day=target
            if self.channels: self._load_events(max(0,self.getControl(210).getSelectedPosition()))

    def onAction(self,action):
        key=action.getId();focus=self.getFocusId()
        with self._lock:
            if key==117:
                query=xbmcgui.Dialog().input(tr(32534))
                if query.strip():
                    self.close()
                    xbmc.executebuiltin('Container.Update('+self.router.url(action='global_search',pid=self.portal['id'],q=query[:200])+')')
                return
            if key in (9,10,92):
                if focus==200: self._group_view(False);self.setFocusId(210 if self.channels else 310)
                else: self.close()
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
            selected=xbmcgui.Dialog().select(event['title'],choices)
            if selected==0:
                text=tr(32552).format(
                    self.channel['name'],time.strftime(tr(32584),time.localtime(event['start'])),
                    time.strftime(tr(32584),time.localtime(event['stop'])),event.get('description') or tr(32553),
                    tr(32554) if event.get('source')==-1 else tr(32555) if not event.get('source') else tr(32556)+str(event['source']))
                xbmcgui.Dialog().textviewer(event['title'],text)
            elif selected==1:
                self.close()
                xbmc.executebuiltin('PlayMedia('+self.router.url(action='play_live',pid=self.portal['id'],sid=self.sid,name=self.channel['name'])+')')
            elif selected==2:
                from guide_timers import add
                if add(self.portal['id'],self.sid,self.channel['name'],event):
                    xbmcgui.Dialog().notification('XCMate',tr(32557))

    def close(self):
        if self._closed: return
        self._closed=True;self._generation+=1
        self._pool.shutdown(wait=False,cancel_futures=True);super().close()


def open_guide(router,portal):
    from appearance import window_source
    window=GuideWindow('XCMateGuide.xml',window_source('XCMateGuide.xml'),'Default','720p')
    window.configure(router,portal)
    try: window.doModal()
    finally: window.close()
