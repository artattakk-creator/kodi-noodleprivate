"""Explicitly tagged non-live playback; isolated polling and bounded writes."""
from localization import tr
import json
import math
import time
import uuid
import sqlite3

PROPERTY='XCMate.MediaSession'
UNIQUE_ID='xcmate_media'
_current=None
_last=None
_written=0
_seeked=False
_resume_deadline=0


def play(router,portal):
    import xbmcgui,xbmcplugin
    from player import build_playable_item
    from library_index import Reader
    kind=router._params.get('kind','vod');sid=str(router._params.get('sid') or '')
    if kind not in ('vod','episode','series_item') or not sid or portal.get('type') not in ('xtream','m3u','stb'):
        xbmcplugin.setResolvedUrl(router._handle,False,xbmcgui.ListItem());return
    from media_intent import allowed,complete
    request=str(router._params.get('intent') or '')
    if request and not allowed(request,portal['id'],kind,sid):
        xbmcplugin.setResolvedUrl(router._handle,False,xbmcgui.ListItem());return
    xc=router._xc(portal)
    if kind in ('vod','series_item'):
        record=Reader(portal['id']).get('series' if kind=='series_item' else 'vod',sid)
        if kind=='series_item' and not (portal.get('type')=='m3u' and record and record.get('series_flat')): record=None
        if not record:
            xbmcplugin.setResolvedUrl(router._handle,False,xbmcgui.ListItem());return
    else:
        from media_data import episode_records
        series_id=router._params.get('series_id','')
        if not Reader(portal['id']).get('series',series_id):
            xbmcplugin.setResolvedUrl(router._handle,False,xbmcgui.ListItem());return
        # Playback validation is cache-only, never trust an arbitrary episode URL/extension.
        data=xc._get_json('get_series_info',extra={'series_id':series_id},cached_only=True) or {}
        record=next((e for e in episode_records(data,series_id) if e['sid']==sid),None)
        if record is None:
            xbmcplugin.setResolvedUrl(router._handle,False,xbmcgui.ListItem());return
    extension=str(record.get('container_extension') or 'mkv')
    if not extension.isalnum() or len(extension)>8: extension='mkv'
    try:
        headers={}
        if portal.get('type')=='xtream':
            url=xc.vod_stream_url(sid,extension) if kind=='vod' else xc.series_episode_url(sid,extension)
        elif kind=='episode':
            url,headers=xc.episode_uri(series_id,sid,str(record.get('season','')))
        else: url,headers=xc.play_uri('series' if kind=='series_item' else 'vod',sid)
        item=build_playable_item(url,title=record.get('name',''),logo='',headers=headers)
    except (ValueError,OSError,RuntimeError):
        xbmcplugin.setResolvedUrl(router._handle,False,xbmcgui.ListItem());return
    if request and not allowed(request,portal['id'],kind,sid):
        xbmcplugin.setResolvedUrl(router._handle,False,xbmcgui.ListItem());return
    session={k:str(record[k]) for k in ('series_id','season','episode') if k in record}
    session.update(pid=str(portal['id']),kind=kind,sid=sid,nonce=request or uuid.uuid4().hex,at=time.time(),
                   resume=router._params.get('resume')=='1')
    try:
        item.getVideoInfoTag().setUniqueIDs({UNIQUE_ID:session['nonce']})
        xbmcgui.Window(10000).setProperty(PROPERTY,json.dumps(session))
    except (AttributeError,RuntimeError):
        # Playback still works, but no unverified resume tracking.
        xbmcgui.Window(10000).clearProperty(PROPERTY)
    if request: complete(request)
    if kind=='vod':
        from media_continue import reveal
        try:reveal(portal['id'],sid)
        except (OSError,sqlite3.Error):pass  # Playback remains available on read-only/full storage.
    xbmcplugin.setResolvedUrl(router._handle,True,item)


def poll(player=None,now=None):
    global _current,_last,_written,_seeked,_resume_deadline
    import xbmc,xbmcgui
    from media_state import progress,resume_position,save_progress
    now=time.monotonic() if now is None else now
    player=player or xbmc.Player()
    try:
        raw=xbmcgui.Window(10000).getProperty(PROPERTY)
        session=json.loads(raw) if raw and len(raw)<4096 else {}
        valid=(isinstance(session,dict) and session.get('kind') in ('vod','episode','series_item') and
               all(session.get(k) for k in ('nonce','pid','sid')) and
               0<=time.time()-float(session.get('at',0))<86400 and player.isPlayingVideo() and
               player.getVideoInfoTag().getUniqueID(UNIQUE_ID)==session['nonce'])
        if not valid:
            if _current and _last: save_progress(_current,*_last)
            _current=_last=None
            return
        if not _current or session['nonce']!=_current['nonce']:
            if _current and _last: save_progress(_current,*_last)
            _current,_last,_written,_seeked=session,None,now,False
            _resume_deadline=now+10
        duration=float(player.getTotalTime());position=float(player.getTime())
        if not math.isfinite(duration) or not math.isfinite(position) or duration<60: return
        if not _seeked:
            if session.get('resume'):
                target=resume_position(progress(session['pid'],session['kind'],session['sid'],session.get('series_id',''),session.get('season','')))
                if target:
                    if xbmc.getCondVisibility('Player.SeekEnabled'):
                        player.seekTime(min(target,duration-30))
                        position=min(target,duration-30)
                    elif now<_resume_deadline: return
                    else: xbmcgui.Dialog().notification('XCMate',tr(32538))
            _seeked=True
        _last=(position,duration)
        if now-_written>=15:
            save_progress(session,position,duration);_written=now
    except (ValueError,TypeError,AttributeError,RuntimeError,OSError,sqlite3.Error):
        # Never propagate into the frozen service's live-TV path.
        return


def shutdown():
    if _current and _last:
        from media_state import save_progress
        save_progress(_current,*_last)
