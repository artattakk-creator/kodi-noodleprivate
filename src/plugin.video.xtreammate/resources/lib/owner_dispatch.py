"""Owner-thread completion pump for Kodi WindowXML, without GUI Future callbacks.

    WindowXML.show + Monitor.waitForAbort dispatch Kodi's native callbacks on
    the owning PyThreadState (Kodi 21.3 proof: KODI_213_SETUP_THREAD_API_0294.json).
"""
import threading
import time
from functools import wraps
import xbmc
_clock=time.monotonic


class WindowStartError(RuntimeError):
    """Native WindowXML initialization was not delivered; no user data changed."""


def window_mark(view,stage,error=None):
    """Fixed lifecycle labels only; never exception text, URLs or account data."""
    views=('GUIDE','MOVIES','SERIES')
    stages=('CONSTRUCT','CONFIGURE','WAIT_MODAL','MODAL_TIMEOUT','DISPOSE_UNSHOWN',
            'SHOW_BEGIN','SHOW_DONE','INIT_BEGIN','INIT_DONE',
            'INIT_FAILED','INIT_TIMEOUT','ABORT','RUN_FAILED','CLOSE_BEGIN','CLOSE_DONE',
            'CLOSE_FAILED','CONSTRUCT_FAILED','CONFIGURE_FAILED','THREAD_MISMATCH')
    errors=('RuntimeError','WindowStartError','ValueError','TypeError','OSError',
            'ImportError','ModuleNotFoundError','MemoryError','TimeoutError')
    message='[XCMate][WINDOW] view={} stage={}'.format(
        view if view in views else 'OTHER',stage if stage in stages else 'OTHER')
    if error is not None:
        name=type(error).__name__;message+=' error='+(name if name in errors else 'OTHER')
    try: xbmc.log(message,xbmc.LOGINFO)
    except Exception: pass
    try:
        import xbmcgui
        xbmc.log('[XCMate][WINDOW_STATE] thread={} window={} dialog={}'.format(
            threading.get_ident(),int(xbmcgui.getCurrentWindowId()),
            int(xbmcgui.getCurrentWindowDialogId())),xbmc.LOGINFO)
    except Exception: pass


def native_init(callback):
    """Capture failures Kodi otherwise reports only inside its callback bridge."""
    @wraps(callback)
    def initialize(self):
        if self._closed:return
        self._native_active=True
        self._window_mark('INIT_BEGIN')
        try:
            self._gui()
            callback(self)
        except Exception as exc:
            self._init_error=exc
            self._window_mark('INIT_FAILED',exc)
        else:
            self._native_initialized=True
            self._window_mark('INIT_DONE')
    return initialize


def dispose_unshown(window):
    """Release workers without Window.close(), which navigates PreviousWindow."""
    if window is None:return
    window._closed=True
    pool=getattr(window,'_pool',None)
    stop=getattr(window,'_watch_stop',None)
    if stop is not None:stop.set()
    if pool is not None:pool.shutdown(wait=False,cancel_futures=True)


def open_owned_window(window_class,xml,router,portal,*args,**kwargs):
    """Log constructor/configuration failures as well as the running lifecycle."""
    from appearance import window_source
    view='GUIDE' if xml=='XCMateGuide.xml' else 'SERIES' if args and args[0]=='series' else 'MOVIES'
    stage='CONSTRUCT'
    window=None
    try:
        window_mark(view,stage)
        window=window_class(xml,window_source(xml),'Default','720p')
        window._window_view=view
        stage='CONFIGURE';window_mark(view,stage)
        window.configure(router,portal,*args,**kwargs)
    except Exception as exc:
        window_mark(view,stage+'_FAILED',exc)
        # No native close before show: that would navigate a different window.
        try:dispose_unshown(window)
        except Exception as cleanup:window_mark(view,'CLOSE_FAILED',cleanup)
        raise
    window.run()  # run owns exactly one idempotent close, even on failure.
    return window


class OwnerDispatch:
    def _configure_owner(self):
        self._owner=threading.get_ident()
        self._pending_future=None;self._pending_apply=None;self._pending_generation=0
        self._native_initialized=False;self._init_error=None
        self._native_active=False

    def _window_mark(self,stage,error=None):
        view=getattr(self,'_window_view','GUIDE' if type(self).__name__=='GuideWindow' else
                     'SERIES' if getattr(self,'kind','')=='series' else 'MOVIES')
        window_mark(view,stage,error)

    def _gui(self):
        if threading.get_ident()!=self._owner:
            self._window_mark('THREAD_MISMATCH')
            raise RuntimeError('XM-WINDOW-GUI-THREAD')

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
        self._running=True
        started=_clock();failed=False;show_requested=False
        try:
            # Kodi 21.3 GUIWindowManager rejects activation AND plays the
            # error sound while a modal dialog is active. Never force it shut.
            waiting=False
            while xbmc.getCondVisibility('System.HasActiveModalDialog'):
                if not waiting:self._window_mark('WAIT_MODAL');waiting=True
                if _clock()-started>=15:
                    self._window_mark('MODAL_TIMEOUT')
                    raise WindowStartError('XM-WINDOW-MODAL-TIMEOUT')
                if monitor.waitForAbort(.05):
                    self._window_mark('ABORT');return
            started=_clock()
            self._window_mark('SHOW_BEGIN')
            show_requested=True
            try:
                import xbmcgui
                previous=int(xbmcgui.getCurrentWindowId())
            except Exception:previous=None
            self.show()
            try:
                current=int(xbmcgui.getCurrentWindowId())
                if previous is not None and current>=13000 and current!=previous:
                    self._native_active=True
            except Exception:pass
            self._window_mark('SHOW_DONE')
            while not self._closed:
                if self._init_error is not None:raise self._init_error
                if self._native_initialized:self.pump()
                elif _clock()-started>=15:
                    self._window_mark('INIT_TIMEOUT')
                    raise WindowStartError('XM-WINDOW-INIT-TIMEOUT')
                if monitor.waitForAbort(.05):
                    self._window_mark('ABORT');break
        except BaseException as exc:
            failed=True;self._window_mark('RUN_FAILED',exc)
            raise
        finally:
            self._running=False
            self._window_mark('CLOSE_BEGIN')
            try:
                if show_requested and self._native_active:self.close()
                else:
                    self._window_mark('DISPOSE_UNSHOWN');dispose_unshown(self)
            except Exception as exc:
                self._window_mark('CLOSE_FAILED',exc)
                if not failed:raise
            else:self._window_mark('CLOSE_DONE')
