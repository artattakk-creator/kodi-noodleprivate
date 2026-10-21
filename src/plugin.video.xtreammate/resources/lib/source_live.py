"""Shared live navigator for M3U/Stalker, with explicit InfoTag ownership.

Provider link creation happens on one worker. Only the service thread applies
completed tune requests; stale requests and foreign playback never receive play.
"""
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import xbmc
import xbmcgui
import xbmcplugin
from live_overlay import LiveNavigator,SESSION_KEY,session_from_property,announce,trace


def browse(router,portal):
    from library_index import Reader
    from app_routes import add_index_item,_end
    from epg import load_cache
    from epg_sources import configuration
    from epg_views import resolve_guide
    from source_adapters import for_portal
    from catalog_sync import request
    reader=Reader(portal['id']);cid=router._params.get('cid')
    request(portal,'live',priority=1)
    xbmcplugin.setContent(router._handle,'videos')
    if cid is None:
        for g in reader.groups('live'): router._add_dir(g['title'],router.url(action='source_live',pid=portal['id'],cid=g['cid']))
        router._add_dir('XCMate · '+__import__('localization').tr(32430),router.url(action='groups_manager',pid=portal['id']))
    else:
        try: offset=max(0,int(router._params.get('offset',0)))
        except ValueError: offset=0
        rows,total=reader.page('live',category=cid,offset=offset,limit=48)
        cache=load_cache(portal['id']);mappings=configuration(portal['id'])['mappings'];adapter=for_portal(portal)
        for row in rows:
            info=resolve_guide(cache,row.get('epg_channel_id',''),row['sid'],client=adapter,mappings=mappings)
            from app_routes import guide_plot
            add_index_item(router,portal,'live',row,dict(Now=info['now'],Next=info['next'],plot=guide_plot(info)))
        from app_routes import paging
        paging(router,total,offset,action='source_live',cid=cid)
    _end(router)


def play(router,portal,direct=False):
    from library_index import Reader
    from source_adapters import for_portal
    from player import build_playable_item
    from live_recovery import tag_live_item
    sid=str(router._params.get('sid') or portal.get('start_stream_id') or '')
    reader=Reader(portal['id']);record=reader.get('live',sid) if sid else None
    if direct and record is None:
        rows,_=reader.page('live',limit=1);record=rows[0] if rows else None
    if not record or portal.get('type') not in ('m3u','stb'):
        if not direct: xbmcplugin.setResolvedUrl(router._handle,False,xbmcgui.ListItem())
        return
    # This is a plugin interpreter, never the overlay's input callback.
    try:
        url,headers=for_portal(portal).play_uri('live',record['sid'])
        session=announce(portal['id'],record['sid'],record['name'])
        item=build_playable_item(url,title=record['name'],logo='',headers=headers)
        if not tag_live_item(item,session): raise RuntimeError('Kodi live identity unavailable')
        if direct:
            from app_routes import _end
            _end(router);xbmc.Player().play(item.getPath(),item)
        else: xbmcplugin.setResolvedUrl(router._handle,True,item)
    except Exception as exc:
        trace('dialog','SOURCE_PLAY_FAILED',exception_class=type(exc).__name__)
        if not direct: xbmcplugin.setResolvedUrl(router._handle,False,xbmcgui.ListItem())
        xbmcgui.Dialog().notification('XCMate',type(exc).__name__)


class SourceNavigator(LiveNavigator):
    def __init__(self,portal,initial_sid=''):
        from source_adapters import for_portal
        self._source_pool=ThreadPoolExecutor(max_workers=1)
        self._source_lock=threading.Lock();self._source_result=None;self._source_serial=0;self._target_sid=initial_sid
        self._catalog_next=time.monotonic()+5;self._catalog_future=None;self._catalog_result=None;self._catalog_revision=None
        super().__init__(portal,initial_sid,client=for_portal(portal))
    def owns_playback(self):
        try:
            player=xbmc.Player()
            if self._closed or not player.isPlayingVideo(): return False
            from live_recovery import ITEM_ID
            raw=player.getVideoInfoTag().getUniqueID(ITEM_ID)
            tag=session_from_property(raw) if len(raw)<4096 else None
            current=session_from_property(xbmcgui.Window(10000).getProperty(SESSION_KEY))
            possible=[current]
            if time.monotonic()<self._tune_deadline: possible.append(self._previous_session)
            return bool(tag and tag['pid']==str(self.portal['id']) and
                any(value and all(tag.get(k)==value.get(k) for k in ('pid','sid','nonce','at')) for value in possible) and
                (tag['sid']==self.sid or tag['sid']==self._recent_sid and time.monotonic()<self._tune_deadline))
        except (AttributeError,ValueError,TypeError,RuntimeError): return False
    def _tune(self,channel):
        if not self.owns_playback(): return
        self._source_serial+=1;serial=self._source_serial
        self._target_sid=str(channel.extra['stream_id'])
        expected=session_from_property(xbmcgui.Window(10000).getProperty(SESSION_KEY))
        def resolve():
            if serial!=self._source_serial or self._closed: return
            try: result=(channel,self.xc.play_uri('live',str(channel.extra['stream_id'])),None)
            except Exception as exc: result=(channel,None,type(exc).__name__)
            with self._source_lock:
                if serial==self._source_serial and not self._closed: self._source_result=(serial,expected,result)
        self._source_pool.submit(resolve)
    def tick(self):
        if not self._closed and time.monotonic()>=self._catalog_next and (self._catalog_future is None or self._catalog_future.done()):
            self._catalog_next=time.monotonic()+5
            def read_catalog():
                try:
                    from library_index import Reader
                    state=Reader(self.portal['id']).state('live')
                    revision=(state or {}).get('revision')
                    if revision==self._catalog_revision: return
                    from source_adapters import for_portal
                    client=for_portal(self.portal)
                    groups=client.get_cached_catalog('get_live_categories');streams=client.get_cached_catalog('get_live_streams')
                    with self._source_lock:
                        if not self._closed: self._catalog_result=(revision,groups,streams,client._local_urls)
                except Exception as exc:
                    trace('catalog_performance','SOURCE_CACHE_READ_FAILED',exception_class=type(exc).__name__)
            self._catalog_future=self._source_pool.submit(read_catalog)
        with self._source_lock:
            catalog=self._catalog_result;self._catalog_result=None
        if catalog and not self._closed:
            self._catalog_revision,groups,streams,urls=catalog
            self.xc._local_urls=urls
            self.xc._catalog_snapshot={'get_live_categories':groups,'get_live_streams':streams}
            self._load_catalog_from_disk();self._list_key=None
            if self._drawn: self._render(focus=False)
        with self._source_lock: ready=self._source_result;self._source_result=None
        if ready and not self._closed:
            serial,expected,(channel,link,failure)=ready
            current=session_from_property(xbmcgui.Window(10000).getProperty(SESSION_KEY))
            if serial==self._source_serial and expected==current and self.owns_playback():
                if failure: trace('dialog','SOURCE_LINK_FAILED');xbmcgui.Dialog().notification('XCMate',failure)
                else:
                    from player import build_playable_item
                    uri,headers=link;sid=str(channel.extra['stream_id'])
                    # Base _tune retains established switching, tagging and input
                    # behavior. Pass the prepared URL including Kodi headers.
                    prepared=build_playable_item(uri,title=channel.name,logo='',headers=headers)
                    channel.url=prepared.getPath()
                    super()._tune(channel)
        super().tick()
    def _zap(self,step):
        rows,positions=self.index.selection(self.category_id,self.enabled)
        if not rows: return super()._zap(step)
        sid=str(self._target_sid or self.sid)
        pos=(positions.get(sid,0)+step)%len(rows)
        self._tune(rows[pos])
    def close(self):
        self._source_serial+=1
        super().close()
        self._source_pool.shutdown(wait=False,cancel_futures=True)


def start_if_eligible(last_nonce):
    session=session_from_property(xbmcgui.Window(10000).getProperty(SESSION_KEY))
    if not session or session['nonce']==last_nonce or not xbmc.Player().isPlayingVideo(): return None
    from portals import get_by_id
    portal=get_by_id(session['pid'])
    if not portal or not portal.get('enabled',True) or portal.get('type') not in ('m3u','stb'): return None
    try:
        candidate=SourceNavigator(portal,session['sid'])
        if candidate.owns_playback(): return candidate
        candidate.close()
    except Exception as exc: trace('dialog','SOURCE_CONSTRUCTION_FAILED',exception_class=type(exc).__name__)
    return None
