"""Native modeless VOD dialog; Kodi remains the video engine.

Built/shown/polled on the existing service owner thread, like the proven live
navigator. No modal loop, global keymap, HTTP, catalog query or live mutation.
"""
import math
import os
import time
import xbmc
import xbmcgui
import xbmcaddon
from localization import tr
from media_actions import available,extension
from playback_exit import identity,_same,stop_owned

_window=None


def _dialog_id():
    try:return int(xbmcgui.getCurrentWindowDialogId())
    except (AttributeError,RuntimeError,TypeError):return 9999


def _fullscreen():return xbmc.getCondVisibility('Window.IsVisible(fullscreenvideo)')

def _number(value):
    number=float(value)
    return number if math.isfinite(number) and number>=0 else 0


def clock(seconds):
    value=int(max(0,seconds));return '{:02d}:{:02d}:{:02d}'.format(value//3600,value//60%60,value%60)


class MediaOSD(xbmcgui.WindowDialog):
    def __init__(self,token,player):
        super().__init__();self.token=token;self.player=player;self.visible=False;self.closed=False;self.suspended=False
        self.native_id=9999;self.buttons={};self.icons={};self.decor=[];self._last=0;self._signature=();self.actions=[]
        self.media=os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources','media')
        self.width,self.height=max(960,self.getWidth()),max(640,self.getHeight())
        clear=os.path.join(self.media,'remote_clear.png')
        self.capture=xbmcgui.ControlButton(8,8,8,8,'',focusTexture=clear,noFocusTexture=clear)
        self.addControl(self.capture);self.capture.setNavigation(self.capture,self.capture,self.capture,self.capture)
        y=self.height-264
        self.panel=xbmcgui.ControlImage(32,y,self.width-64,232,os.path.join(self.media,'tv_panel.png'))
        self.poster=xbmcgui.ControlImage(48,y+14,88,132,token[1].get('poster') or os.path.join(self.media,'vod.png'),aspectRatio=2)
        self.title=xbmcgui.ControlLabel(156,y+10,self.width-208,34,'','font16','0xFFF4F7F9')
        self.position=xbmcgui.ControlLabel(156,y+48,self.width-208,26,'','font13','0xFFDCE2EA')
        self.track=xbmcgui.ControlImage(156,y+82,self.width-212,8,os.path.join(self.media,'tv_normal.png'))
        self.progress=xbmcgui.ControlImage(156,y+82,1,8,os.path.join(self.media,'tv_progress.png'))
        self.hint=xbmcgui.ControlLabel(48,self.height-54,self.width-96,24,tr(33011),'font12','0xFFDCE2EA')
        self.decor=[self.panel,self.poster,self.title,self.position,self.track,self.progress,self.hint]
        self.addControls(self.decor)
        self._build();self.hide_bar()

    def owned(self):return _same(self.token,identity(self.player)) and self.token[0]=='media'

    def capabilities(self):
        audio=[];subtitles=[]
        try:audio=self.player.getAvailableAudioStreams()
        except (AttributeError,RuntimeError):pass
        try:subtitles=self.player.getAvailableSubtitleStreams()
        except (AttributeError,RuntimeError):pass
        try:duration=_number(self.player.getTotalTime())
        except (AttributeError,RuntimeError,ValueError):duration=0
        seek=bool(xbmc.getCondVisibility('Player.SeekEnabled') and duration>0)
        return dict(pause=True,stop=True,back=seek,forward=seek,audio=bool(audio),subtitles=bool(subtitles),
                    subtitle_toggle=bool(subtitles),video=True,audio_settings=True,info=True)

    def _build(self):
        entries=available(self.token[1],self.capabilities())
        signature=tuple(e[0] for e in entries)
        if signature==self._signature:return
        old=self.focus_action();self._signature=signature;self.actions=entries
        for control in [*self.buttons.values(),*self.icons.values()]:self.removeControl(control)
        self.buttons={};self.icons={}
        for group,y in (('transport',self.height-162),('settings',self.height-108)):
            row=[entry for entry in entries if entry[2]==group];step=(self.width-208)//max(1,len(row))
            for i,(name,label,_) in enumerate(row):
                control=xbmcgui.ControlButton(156+i*step,y,step-8,46,tr(label),
                    focusTexture=os.path.join(self.media,'xcmate_focus_neon.png'),
                    noFocusTexture=os.path.join(self.media,'tv_normal.png'),textOffsetX=36,font='font13',textColor='0xFFF4F7F9',focusedColor='0xFFFFFFFF')
                self.buttons[name]=control;self.addControl(control)
                icon={'subtitle_toggle':'subtitle','subtitles':'subtitle','audio_settings':'audio','info':'more','video':'video'}.get(name,'pause' if name=='pause' else name)
                self.icons[name]=xbmcgui.ControlImage(164+i*step,y+12,22,22,os.path.join(self.media,'tv_'+icon+'.png'))
                self.addControl(self.icons[name])
        rows=[[e[0] for e in entries if e[2]==group] for group in ('transport','settings')]
        for r,names in enumerate(rows):
            for i,name in enumerate(names):
                other=rows[1-r];target=other[min(i,len(other)-1)] if other else name
                self.buttons[name].setNavigation(self.buttons[target],self.buttons[target],
                                                self.buttons[names[(i-1)%len(names)]],self.buttons[names[(i+1)%len(names)]])
        for button in [*self.buttons.values(),*self.icons.values()]:button.setVisible(self.visible)
        if self.visible:self.setFocus(self.buttons.get(old,self.buttons['pause']))

    def focus_action(self):
        try:ident=self.getFocusId()
        except RuntimeError:return ''
        return next((name for name,button in self.buttons.items() if button.getId()==ident),'')

    def show_capture(self):
        if not self.closed:
            self.show();self.native_id=_dialog_id();self.setFocus(self.capture)

    def show_bar(self):
        if not self.owned():self.dispose();return
        self.visible=True;self._build()
        for control in self.decor+list(self.buttons.values())+list(self.icons.values()):control.setVisible(True)
        self.setFocus(self.buttons['pause']);self.update()

    def hide_bar(self):
        self.visible=False
        for control in self.decor+list(self.buttons.values())+list(self.icons.values()):control.setVisible(False)
        if not self.closed:self.setFocus(self.capture)

    def update(self):
        if not self.owned():self.dispose();return
        if not self.visible:return
        self._build()
        session=self.token[1];title=session.get('title') or tr(33012)
        self.title.setLabel(title[:512])
        try:
            position=_number(self.player.getTime());duration=_number(self.player.getTotalTime())
            self.position.setLabel(clock(position)+' / '+clock(duration))
            self.progress.setWidth(max(1,int((self.width-212)*min(1,position/duration))) if duration else 1)
            self.progress.setVisible(duration>0)
        except (RuntimeError,ValueError,TypeError):self.position.setLabel(tr(33013));self.progress.setVisible(False)
        paused=xbmc.getCondVisibility('Player.Paused')
        self.buttons['pause'].setLabel(tr(33014) if paused else tr(33001))
        self.icons['pause'].setImage(os.path.join(self.media,'tv_play.png' if paused else 'tv_pause.png'))

    def invoke(self,name):
        if not self.owned():self.dispose();return False
        if name not in {e[0] for e in available(self.token[1],self.capabilities())}:return False
        try:
            if name=='pause':self.player.pause()
            elif name in ('back','forward'):
                position=_number(self.player.getTime());duration=_number(self.player.getTotalTime())
                if self.owned():self.player.seekTime(max(0,min(duration-.1,position+(-10 if name=='back' else 30))))
            elif name=='stop':
                result=stop_owned(self.player,expected=self.token);self.dispose();return result
            elif name in ('audio','subtitles'):
                streams=self.player.getAvailableAudioStreams() if name=='audio' else self.player.getAvailableSubtitleStreams()
                choice=xbmcgui.Dialog().select(tr(33005 if name=='audio' else 33006),list(streams))
                if 0<=choice<len(streams) and self.owned():
                    if name=='audio':self.player.setAudioStream(choice)
                    else:self.player.setSubtitleStream(choice);self.player.showSubtitles(True)
            elif name=='subtitle_toggle':
                if self.owned():self.player.showSubtitles(not xbmc.getCondVisibility('VideoPlayer.SubtitlesEnabled'))
            elif name in ('video','audio_settings'):
                self.hide_bar();self.suspended=True;self._suspend_until=time.monotonic()+.5;self.close()
                xbmc.executebuiltin('ActivateWindow('+('osdvideosettings' if name=='video' else 'osdaudiosettings')+')')
            elif name=='info':xbmcgui.Dialog().textviewer(tr(33010),self.token[1].get('title') or tr(33012))
            else:
                if self.owned():return extension(name,self.token[1])
            self.update();return True
        except (AttributeError,RuntimeError,ValueError,TypeError):
            xbmcgui.Dialog().notification('XCMate',tr(33015));return False

    def onAction(self,action):
        if self.closed:return
        if not self.owned():self.dispose();return
        key=action.getId()
        if key in (9,10,92):
            if self.visible:self.hide_bar()
            else:self.invoke('stop')
        # Native buttons call onControl BEFORE onAction(7), exactly once.
        elif key==7:return
        elif key in (12,79,229):self.invoke('pause')
        elif key==13:self.invoke('stop')

    def onControl(self,control):
        if self.closed:return
        if control.getId()==self.capture.getId():self.show_bar();return
        name=next((n for n,b in self.buttons.items() if b.getId()==control.getId()),'')
        if name:self.invoke(name)

    def dispose(self):
        if self.closed:return
        self.closed=True;self.close()


def poll(player=None):
    global _window
    player=player or xbmc.Player()
    token=identity(player)
    if not token or token[0]!='media' or not _fullscreen():
        if _window:_window.dispose();_window=None
        return
    current=_dialog_id()
    if _window and not _same(_window.token,token):_window.dispose();_window=None
    if _window is None:
        if current not in (0,9999):return # never steal a foreign dialog
        _window=MediaOSD(token,player);_window.show_capture()
    elif _window.suspended:
        if current in (0,9999) and time.monotonic()>=_window._suspend_until:_window.suspended=False;_window.show_capture()
    elif current in (0,9999,_window.native_id):_window.update()
