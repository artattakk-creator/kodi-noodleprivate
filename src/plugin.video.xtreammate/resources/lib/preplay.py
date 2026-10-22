"""Service-owned pre-play display; native Kodi playback stays on its caller.

The plugin requests/awaits a bounded UI acknowledgement; it never starts a
Player from a data worker. The existing LiveNavigator callbacks remain intact.
Only the connecting subclass gates controls while no verified video exists.
"""
import json
import os
import time
import xbmc
import xbmcgui
from localization import tr

REQUEST='XCMate.PrePlay.Request'
ACK='XCMate.PrePlay.Ack'
CANCEL='XCMate.PrePlay.Cancel'
_window=None


def marker(): return xbmcgui.Window(10000)




class PrePlayDialog(xbmcgui.WindowDialog):
    def __init__(self,session):
        super().__init__()
        self.session=session;self.closed=False;self.started=time.monotonic()
        import xbmcaddon
        from startup_preload import read
        from epg_views import guide_for_channel
        row=read(session['pid'],session['sid']);self.guide=row.get('guide') or guide_for_channel({})
        self.name=row.get('name') or session.get('name') or 'Live TV'
        media=os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources/media')
        width,height=max(960,self.getWidth()),max(640,self.getHeight())
        self.panel=xbmcgui.ControlImage(32,height-248,width-64,216,os.path.join(media,'tv_panel.png'))
        self.logo=xbmcgui.ControlImage(54,height-214,96,96,row.get('logo') or os.path.join(media,'tv.png'),aspectRatio=2)
        self.title=xbmcgui.ControlLabel(174,height-234,width-220,32,self.name,'font16','0xFFF0F2F5')
        self.now=xbmcgui.ControlLabel(174,height-193,width-220,29,self.guide.get('now') or tr(32646),'font13','0xFFF0F2F5')
        self.next=xbmcgui.ControlLabel(174,height-131,width-220,29,self.guide.get('next') or tr(32646),'font13','0xFFB6BCC6')
        self.track=xbmcgui.ControlImage(174,height-153,width-240,8,os.path.join(media,'tv_progress.png'))
        self.status=xbmcgui.ControlLabel(174,height-99,width-220,29,tr(32644),'font13','0xFFF0F2F5')
        self.capture=xbmcgui.ControlButton(174,height-61,width-220,28,tr(32647),
            focusTexture=os.path.join(media,'remote_clear.png'),noFocusTexture=os.path.join(media,'remote_clear.png'),font='font12')
        self.addControls([self.panel,self.logo,self.title,self.now,self.next,self.track,self.status,self.capture])
        self.capture.setNavigation(self.capture,self.capture,self.capture,self.capture)
        progress=self.guide.get('progress')
        import math
        valid=isinstance(progress,(int,float)) and math.isfinite(progress) and 0<progress<=1
        self.track.setVisible(valid)
        if valid: self.track.setWidth(max(1,int((width-240)*progress)))
    def show(self):
        super().show();self.setFocus(self.capture)
        marker().setProperty(ACK,self.session['nonce'])
        from live_overlay import trace
        trace('dialog','PREPLAY_SHOWN',marker=True)
    def onAction(self,action):
        if action.getId() in (9,10,13,92): self.cancel()
    def onControl(self,control):
        if control==self.capture: self.cancel()
    def cancel(self):
        # Invalidate this nonce before stopping. A new selection cannot be
        # cancelled by an old dialog callback.
        from live_overlay import SESSION_KEY,session_from_property
        current=session_from_property(marker().getProperty(SESSION_KEY))
        if current and current['nonce']==self.session['nonce']:
            marker().setProperty(CANCEL,self.session['nonce'])
            marker().clearProperty(SESSION_KEY)
            xbmc.Player().stop()
        self.close()
    def close(self):
        if self.closed: return
        self.closed=True;super().close()


def poll(current_overlay=None):
    """Only called by the service's normal UI loop, not the import worker."""
    global _window
    from live_overlay import SESSION_KEY,session_from_property,trace
    session=session_from_property(marker().getProperty(SESSION_KEY))
    request=session_from_property(marker().getProperty(REQUEST))
    if _window is not None:
        if not session or _window.session['nonce']!=session['nonce']:
            _window.close();_window=None
        elif _window.closed:
            _window=None
    if not session or not request or request['nonce']!=session['nonce']: return
    if marker().getProperty(CANCEL)==session['nonce']: return
    player=xbmc.Player()
    from portals import get_by_id
    portal=get_by_id(session['pid'])
    if not portal or portal.get('type')!='xtream' or not portal.get('enabled',True): return
    from live_recovery import playback_match
    from xtream import XtreamClient
    match,_=playback_match(player,[portal],XtreamClient,session)
    ready=False
    if match==(session['pid'],session['sid']):
        try: player.getTime();ready=True
        except Exception: pass
    if ready:
        marker().setProperty(ACK,session['nonce'])
        if _window is not None: _window.close();_window=None
        marker().clearProperty(REQUEST)
        marker().setProperty('XCMate.PrePlay.Ready',session['nonce'])
        trace('dialog','PREPLAY_VIDEO_READY',video=True,marker=True)
        return
    if _window is None and marker().getProperty(ACK)!=session['nonce']:
        if current_overlay is not None and not current_overlay._closed:
            current_overlay.close()
            if not marker().getProperty(SESSION_KEY): marker().setProperty(SESSION_KEY,json.dumps(session))
        _window=PrePlayDialog(session);_window.show()
    if _window is not None:
        if time.monotonic()-_window.started>60:
            _window.status.setLabel(tr(32648));_window.cancel();trace('dialog','PREPLAY_TIMEOUT')
        elif time.monotonic()-_window.started>1: _window.status.setLabel(tr(32645))


def start_navigator(last_nonce):
    from live_overlay import SESSION_KEY,session_from_property
    session=session_from_property(marker().getProperty(SESSION_KEY))
    if not xbmc.Player().isPlayingVideo() or not session or session['nonce']==last_nonce: return None
    if marker().getProperty(REQUEST) and marker().getProperty('XCMate.PrePlay.Ready')!=session['nonce']: return None
    from portals import get_by_id
    portal=get_by_id(session['pid'])
    if not portal or portal.get('type')!='xtream' or not portal.get('enabled',True): return None
    candidate=ConnectingNavigator(portal,session['sid'])
    if not candidate.owns_playback(): candidate.close();return None
    if marker().getProperty('XCMate.PrePlay.Ready')==session['nonce']:
        candidate.mode='info';candidate._info_deadline=time.monotonic()+candidate._info_timeout
    return candidate


from live_overlay import LiveNavigator


class ConnectingNavigator(LiveNavigator):
    """Warm tune reuses controls/index. Established callback implementation is inherited."""
    _connecting=False
    def _tune(self,channel):
        self._connecting=True;self._connecting_started=time.monotonic()
        super()._tune(channel)
    def _switch(self,mode):
        super()._switch('info' if self._connecting and mode=='hidden' else mode)
        if self._connecting: self._info_deadline=None
    def _render_info(self):
        super()._render_info()
        if self._connecting: self.info_hint.setLabel(tr(32645)+' · '+tr(32647))
    def owns_playback(self):
        if super().owns_playback(): return True
        if self._connecting and xbmc.Player().isPlayingVideo():
            from live_recovery import playback_match
            match,_=playback_match(xbmc.Player(),[self.portal],lambda *a:self._identity_client,self._previous_session)
            if match and match[0]==str(self.portal['id']) and match[1]==self._recent_sid and time.monotonic()-self._connecting_started<60:
                return True
        if self._connecting and not xbmc.Player().isPlayingVideo():
            from live_overlay import SESSION_KEY,session_from_property
            current=session_from_property(marker().getProperty(SESSION_KEY))
            return bool(current and current['pid']==str(self.portal['id']) and current['sid']==self.sid
                        and time.monotonic()-self._connecting_started<60)
        return False
    def _accept_input(self):
        if getattr(self,'_exiting',False):return False
        if self._connecting and not self._closed:
            from live_overlay import session_from_property,SESSION_KEY
            session=session_from_property(marker().getProperty(SESSION_KEY))
            return bool(session and session['pid']==str(self.portal['id']) and session['sid']==self.sid and self.owns_playback())
        return super()._accept_input()
    def handle_command(self,command,source='bridge',**fields):
        if self._connecting:
            if command=='back':
                self._request_exit();return
            if command not in ('up','down','left','right'): return
            # Only safe sender/list navigation; never pause/seek a pending player.
            if self.mode=='info' and command in ('up','down'):
                self._zap(-1 if command=='up' else 1);return
        return super().handle_command(command,source,**fields)
    def tick(self):
        if self._connecting:
            from live_recovery import playback_match
            from live_overlay import SESSION_KEY,session_from_property
            session=session_from_property(marker().getProperty(SESSION_KEY))
            match,_=playback_match(xbmc.Player(),[self.portal],lambda *a:self._identity_client,session)
            if match==(str(self.portal['id']),self.sid):
                try: xbmc.Player().getTime()
                except RuntimeError: return
                self._connecting=False;self._switch('info')
            elif time.monotonic()-self._connecting_started>60:
                self._request_exit();return
        super().tick()
