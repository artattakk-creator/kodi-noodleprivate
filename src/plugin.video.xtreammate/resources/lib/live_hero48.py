"""Live-only native design preview; never installs/rebinds a BINGIE skin.

Small station buttons select a local programme hero; only OK queues the proven
guide player handoff. Movie/series rows and their reload hooks are untouched.
The matching optional BINGIE include is a review artifact, not auto-installed.
"""
from concurrent.futures import Future
import threading
import time
import xbmc
import xbmcaddon
import xbmcgui
_slots=threading.BoundedSemaphore(1)


def values(portal):
    from widget_data41 import snapshot
    from widget_render47 import values as render
    from widget_art44 import read
    rows,code=snapshot(portal,'live')
    result=[]
    for offset in range(0,len(rows),16):
        for value in render(portal,'live',rows[offset:offset+16],read(portal['id'])):
            value.pop('_programme46',None);result.append(value)
    return rows,result,code


class LiveHeroWindow48(xbmcgui.WindowXMLDialog):
    def configure(self,router,portal):
        self.router,self.portal=router,portal;self.owner=threading.get_ident()
        self._closed=False;self._ready=False;self.rows=[];self.items=[];self.future=None;self.intent=None;self.next=0
        from guide_playback import player_state
        self.entry=player_state()
    def _gui(self):
        if threading.get_ident()!=self.owner:raise RuntimeError('HERO_OWNER_THREAD')
    def onInit(self):
        self._gui();self._ready=True;self.setFocusId(200)
        self.getControl(101).setLabel('Live-TV · Vorschau ohne Skinänderung')
    def pump(self):
        self._gui()
        if self.future and self.future.done():
            future=self.future;self.future=None
            if not future.cancelled():
                try:rows,items,code=future.result()
                except Exception:self.getControl(101).setLabel('Lokale Live-Vorschau nicht verfügbar.')
                else:
                    control=self.getControl(200);position=control.getSelectedPosition() if self.rows else 0
                    previous=str(self.rows[position]['sid']) if 0<=position<len(self.rows) else ''
                    self.rows,self.items=rows,items
                    boundaries=[float(v['props'].get('XtreamMate.Stop',0)) for v in items]
                    delay=min([30]+[stop-time.time() for stop in boundaries if stop>time.time()])
                    self.next=min(self.next,time.monotonic()+max(.2,delay))
                    from widget_items45 import item
                    control.reset();control.addItems([item(v) for v in items])
                    control.selectItem(next((i for i,r in enumerate(rows) if str(r['sid'])==previous),0))
                    self.getControl(101).setLabel('Live-TV · '+str(len(items))+' Sender · Fokus = Vorschau / OK = Wiedergabe · Zurück = Schließen')
        if not self.future and time.monotonic()>=self.next and _slots.acquire(blocking=False):
            self.next=time.monotonic()+30;future=Future();self.future=future
            def work():
                try:
                    if not future.set_running_or_notify_cancel():return
                    try:future.set_result(values(self.portal))
                    except Exception:future.set_exception(RuntimeError('HERO_UNAVAILABLE'))
                finally:_slots.release()
            try:threading.Thread(target=work,name='XCMate-hero48',daemon=True).start()
            except (RuntimeError,MemoryError):_slots.release();self.future=None
    def onClick(self,cid):
        if cid!=200 or self.intent:return
        position=self.getControl(200).getSelectedPosition()
        if 0<=position<len(self.rows):
            from guide_playback import request
            self.intent=request(self.portal,self.rows[position],self.entry)
            self.close()
    def onAction(self,action):
        if action.getId() in (9,10,92):self.close()
    def run(self):
        monitor=xbmc.Monitor();started=time.monotonic()
        try:
            self.show()
            while not self._closed:
                if self._ready:self.pump()
                elif time.monotonic()-started>10:break
                if monitor.waitForAbort(.05):break
        finally:self.close()
        return self.intent
    def close(self):
        self._gui()
        if self._closed:return
        self._closed=True
        if self.future:self.future.cancel()
        super().close()


def launch(router,portal):
    if not portal:return
    from programme_window46 import permitted
    from window_navigation import ownership
    with ownership() as acquired:
        if not acquired or not permitted():return
        dialog=LiveHeroWindow48('XCMateLiveHero48.xml',xbmcaddon.Addon().getAddonInfo('path'),'Default','720p')
        dialog.configure(router,portal);intent=dialog.run()
    if intent:
        from guide_playback import handoff
        handoff(router,portal,intent)
