"""P0 #67: real routes/windows with a delayed native-callback MODEL.

These are AUTOMATED tests, not a running Kodi or Android GUI. The successful
directory prerequisite is from pinned Kodi 21.3 PluginDirectory/GUIMediaWindow.
"""
import importlib
import threading
import types
import unittest
from concurrent.futures import ThreadPoolExecutor, wait
from unittest import mock

from xcmate027_fixture import Fixture, WindowXML, Control


class WindowStartTests(Fixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.trace=[];self.native=[];self.windows=[];self.logs=[]
        xbmc=importlib.import_module('xbmc')
        self.patch(mock.patch.object(xbmc,'LOGINFO',1,create=True))
        self.patch(mock.patch.object(xbmc,'log',side_effect=lambda text,level:self.logs.append(text),create=True))
        self.owner=threading.get_ident()
        self.gui_threads=[]
        def guard(fn):
            def invoke(*args,**kwargs):
                self.gui_threads.append(threading.get_ident())
                self.assertEqual(threading.get_ident(),self.owner)
                return fn(*args,**kwargs)
            return invoke
        for cls,names in ((WindowXML,('getControl','setFocusId','close')),
                          (Control,('setLabel','setText','reset','addItems','setVisible','setImage'))):
            for name in names:self.patch(mock.patch.object(cls,name,guard(getattr(cls,name))))
        def finish(handle,succeeded=True,**kwargs):
            self.trace.append(('directory',succeeded));self.ends.append(((handle,succeeded),kwargs))
        self.patch(mock.patch.object(importlib.import_module('xbmcplugin'),'endOfDirectory',side_effect=finish))
        def show(window):
            self.assertEqual(self.trace[0],('directory',True))
            self.trace.append(('show',None));self.windows.append(window)
            window.shown=True
            importlib.import_module('xbmc')._focus_window=window
            self.native.append(window.onInit)  # delivered by the wait, not show()
        self.patch(mock.patch.object(WindowXML,'show',show))
        for module in (self.guide,self.media):
            self.patch(mock.patch.object(module,'ThreadPoolExecutor',ThreadPoolExecutor))
        self.patch(mock.patch.object(self.media.MediaWindow,'_start_watch'))
        self.patch(mock.patch.object(importlib.import_module('owner_dispatch').xbmc,'Monitor',
                                    return_value=types.SimpleNamespace(waitForAbort=self.tick),create=True))
        self.ticks=0

    def patch(self,patch):
        result=patch.start();self.addCleanup(patch.stop);return result

    def tick(self,seconds):
        self.ticks+=1
        self.assertLess(self.ticks,30,'unbounded owner loop')
        if self.native:
            self.trace.append(('native_init',None));self.native.pop(0)()
        window=self.windows[-1]
        if getattr(window,'_leaving',False):window._leave_after=0
        future=window._pending_future
        if future:self.assertTrue(wait([future],timeout=3).done)
        if (getattr(window,'channels',None) or getattr(window,'rows',None)) and future is None:
            # Native Back follows existing hierarchy; it is not synthetic data.
            if hasattr(window,'channels'):window.setFocusId(210)
            window.native(92)
        return False

    def route(self,action):
        self.router._params.update(action=action)
        self.router._directory_done=False
        self.routes.dispatch(self.router)

    def test_all_three_menu_routes_complete_successfully_then_receive_delayed_native_init(self):
        # Actual Router.dispatch -> _app_route -> app_routes -> real windows.
        from importlib.util import spec_from_file_location,module_from_spec
        from xcmate027_fixture import LIB
        spec=spec_from_file_location('main0296_actual',LIB/'main.py')
        main=module_from_spec(spec);spec.loader.exec_module(main)
        for action in ('guide_browser','movies_home','series_home'):
            with self.subTest(action=action):
                self.trace.clear();self.ticks=0;before=len(self.builtins)
                self.router=main.Router(['plugin://plugin.video.xtreammate','7','?action='+action+'&pid=p'])
                self.router._xc=lambda portal:self.client
                self.router.dispatch()
                window=self.windows[-1]
                self.assertTrue(window._closed);self.assertFalse(window.shown)
                self.assertTrue(window.channels if action=='guide_browser' else window.rows)
                self.assertEqual([p[0] for p in self.trace[:3]],['directory','show','native_init'])
                self.assertEqual(len(self.builtins)-before,1)
                self.assertTrue(self.builtins[-1].endswith(',replace)'))
                self.assertIn('action=xcmate_home',self.builtins[-1])
        self.assertTrue(self.gui_threads);self.assertEqual(set(self.gui_threads),{self.owner})

    def test_native_init_exception_is_logged_and_raised_on_owner_without_credentials(self):
        with mock.patch.object(self.guide.GuideWindow,'_group_view',side_effect=ValueError('SECRET https://provider.invalid')):
            with self.assertRaises(ValueError):self.route('guide_browser')
        self.assertTrue(self.windows[-1]._closed)
        self.assertTrue(any('INIT_FAILED' in row for row in self.logs))
        self.assertTrue(any('error=ValueError' in row for row in self.logs))
        self.assertNotIn('SECRET','\n'.join(self.logs));self.assertNotIn('provider.invalid','\n'.join(self.logs))

    def test_missing_native_init_has_a_bounded_diagnostic_failure(self):
        owner=importlib.import_module('owner_dispatch')
        with mock.patch.object(owner.xbmc,'Monitor',return_value=types.SimpleNamespace(waitForAbort=lambda n:False)),\
             mock.patch.object(owner,'_clock',side_effect=[0,0,20,20,20]):
            with mock.patch.object(importlib.import_module('window_navigation'),'open_route',side_effect=lambda r,p,fn:(self.routes._end(r),fn())[-1]):
                with self.assertRaises(owner.WindowStartError):self.route('guide_browser')
        self.assertTrue(self.windows[-1]._closed)
        self.assertTrue(any('INIT_TIMEOUT' in row for row in self.logs))

    def test_modal_busy_handoff_waits_before_show_then_opens_normally(self):
        owner=importlib.import_module('owner_dispatch');modal=[True,True,False]
        def visibility(condition):
            if condition=='System.HasActiveModalDialog':return modal.pop(0)
            return False
        def tick(seconds):
            if not self.windows:
                self.trace.append(('modal_wait',None));return False
            return self.tick(seconds)
        with mock.patch.object(owner.xbmc,'getCondVisibility',side_effect=visibility),\
             mock.patch.object(owner.xbmc,'Monitor',return_value=types.SimpleNamespace(waitForAbort=tick)):
            self.route('movies_home')
        self.assertEqual([item[0] for item in self.trace[:4]],['directory','modal_wait','modal_wait','show'])
        self.assertTrue(self.windows[-1]._closed)
        self.assertTrue(any('WAIT_MODAL' in row for row in self.logs))

    def test_modal_timeout_never_closes_or_forces_another_kodi_window(self):
        owner=importlib.import_module('owner_dispatch')
        with mock.patch.object(owner.xbmc,'getCondVisibility',return_value=True),\
             mock.patch.object(owner,'_clock',side_effect=[0,20]),\
             mock.patch.object(WindowXML,'close') as close:
            with mock.patch.object(importlib.import_module('window_navigation'),'open_route',side_effect=lambda r,p,fn:(self.routes._end(r),fn())[-1]):
                with self.assertRaises(owner.WindowStartError):self.route('guide_browser')
        self.assertFalse(self.windows);close.assert_not_called()
        self.assertTrue(any('MODAL_TIMEOUT' in row for row in self.logs))

    def test_abort_while_waiting_for_modal_disposes_without_native_window_navigation(self):
        owner=importlib.import_module('owner_dispatch')
        with mock.patch.object(owner.xbmc,'getCondVisibility',return_value=True),\
             mock.patch.object(owner.xbmc,'Monitor',return_value=types.SimpleNamespace(waitForAbort=lambda n:True)),\
             mock.patch.object(WindowXML,'close') as close:
            self.route('guide_browser')
        self.assertFalse(self.windows);close.assert_not_called()
        self.assertTrue(any('DISPOSE_UNSHOWN' in row for row in self.logs))

    def test_abort_before_native_init_does_not_touch_uninitialized_controls(self):
        owner=importlib.import_module('owner_dispatch')
        with mock.patch.object(owner.xbmc,'Monitor',return_value=types.SimpleNamespace(waitForAbort=lambda n:True)):
            self.route('guide_browser')
        self.assertTrue(self.windows[-1]._closed)
        self.assertFalse(self.windows[-1]._ready)
        self.assertTrue(any('ABORT' in row for row in self.logs))
        # A queued late native callback must not populate a closed window.
        self.native.pop(0)()
        self.assertFalse(self.windows[-1]._ready)

    def test_show_error_is_not_replaced_by_close_error(self):
        original=ValueError('PRIVATE show failure')
        with mock.patch.object(WindowXML,'show',side_effect=original),\
             mock.patch.object(WindowXML,'close',side_effect=RuntimeError('PRIVATE close failure')) as close:
            with self.assertRaises(ValueError) as captured:self.route('movies_home')
        self.assertIs(captured.exception,original)
        self.assertTrue(any('DISPOSE_UNSHOWN' in row for row in self.logs));close.assert_not_called()
        self.assertNotIn('PRIVATE','\n'.join(self.logs))

    def test_constructor_and_configure_failures_are_logged(self):
        with mock.patch.object(self.guide,'GuideWindow',side_effect=TypeError('SECRET')):
            with self.assertRaises(TypeError):self.route('guide_browser')
        self.assertTrue(any('CONSTRUCT_FAILED' in row for row in self.logs))
        self.logs.clear();self.trace.clear();self.router._directory_done=False
        with mock.patch.object(self.guide.GuideWindow,'configure',side_effect=ValueError('SECRET')):
            with self.assertRaises(ValueError):self.route('guide_browser')
        self.assertTrue(any('CONFIGURE_FAILED' in row for row in self.logs))
        self.assertNotIn('SECRET','\n'.join(self.logs))

    def test_thread_guard_is_kept_and_logged_without_native_close_from_worker(self):
        from xcmate027_fixture import ADDON
        window=self.guide.GuideWindow('XCMateGuide.xml',str(ADDON),'Default','720p')
        window.configure(self.router,self.portal);self.addCleanup(window.close)
        with ThreadPoolExecutor(max_workers=1) as worker:
            with self.assertRaises(RuntimeError):worker.submit(window.close).result(timeout=3)
        self.assertFalse(window._closed)
        self.assertTrue(any('THREAD_MISMATCH' in row for row in self.logs))


if __name__=='__main__':unittest.main()
