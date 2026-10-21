"""Owner-thread completion pump for Kodi WindowXML, without GUI Future callbacks.

    WindowXML.show + Monitor.waitForAbort dispatch Kodi's native callbacks on
    the owning PyThreadState (Kodi 21.3 proof: KODI_213_SETUP_THREAD_API_0294.json).
"""
import threading
import xbmc


class OwnerDispatch:
    def _configure_owner(self):
        self._owner=threading.get_ident()
        self._pending_future=None;self._pending_apply=None;self._pending_generation=0

    def _gui(self):
        if threading.get_ident()!=self._owner: raise RuntimeError('XM-WINDOW-GUI-THREAD')

    def _request(self,job,apply):
        self._gui()
        self._generation+=1
        if self._pending_future is not None: self._pending_future.cancel()
        self._pending_apply=apply;self._pending_generation=self._generation
        self._pending_future=self._pool.submit(job)

    def pump(self):
        self._gui()
        if self._closed: return
        future=self._pending_future
        if future is not None and future.done():
            apply=self._pending_apply;generation=self._pending_generation
            self._pending_future=None;self._pending_apply=None
            if generation==self._generation and not future.cancelled():
                try: value=future.result()
                except Exception as exc: self._query_failed(exc)
                else: apply(value)
        tick=getattr(self,'_owner_tick',None)
        if not self._closed and tick: tick()

    def run(self):
        self._gui();monitor=xbmc.Monitor()
        try:
            self.show()
            while not self._closed:
                self.pump()
                if monitor.waitForAbort(.05): break
        finally: self.close()
