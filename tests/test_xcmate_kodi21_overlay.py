"""Omega WindowDialog integration model, not an Android device acceptance test.

WindowDialog.show does NOT call onInit. Native controls move/click before
Window.onAction queues its Python callback (Kodi Omega legacy/Window*.cpp).
"""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest import mock

LIB = Path(__file__).resolve().parents[1] / 'src/plugin.video.xtreammate/resources/lib'


class Control:
    def __init__(self, *args, **kwargs):
        self.visible = True
        self.options = kwargs
        self.items = []
        self.selected = 0
    def getId(self): return id(self)
    def setVisible(self, value): self.visible = value
    def setLabel(self, value): self.label = value
    def setItemHeight(self, value): pass
    def setSpace(self, value): pass
    def setNavigation(self, *controls): self.navigation = controls
    def controlLeft(self, control): pass
    def controlRight(self, control): pass
    def reset(self): self.items = []
    def addItems(self, items): self.items = list(items)
    def size(self): return len(self.items)
    def selectItem(self, index): self.selected = index
    def getSelectedPosition(self): return self.selected


class ControlList(Control):
    pass


class OmegaDialog:
    def __init__(self):
        self.controls = []
        self.focus = None
        self.shown = False
        self.shows = self.closes = 0
    def getWidth(self): return 1280
    def getHeight(self): return 720
    def addControl(self, control): self.controls.append(control)
    def setFocus(self, control):
        assert control in self.controls and control.visible
        self.focus = control
    def show(self):
        # Deliberately no onInit callback for a programmatic WindowDialog.
        self.shown = True
        self.shows += 1
    def close(self):
        self.shown = False
        self.closes += 1
    def native(self, key):
        """Run the native control action, then the Python action callback."""
        if isinstance(self.focus, ControlList) and key in (3, 4, 5, 6):
            step = {3:-1, 4:1, 5:-10, 6:10}[key]
            self.focus.selected = min(max(self.focus.selected + step, 0), self.focus.size()-1)
        if key == 7:
            self.onControl(self.focus)
        self.onAction(types.SimpleNamespace(getId=lambda:key, getButtonCode=lambda:0))


class OverlayLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.props = {}
        self.player = types.SimpleNamespace(
            isPlayingVideo=lambda:True, getPlayingFile=lambda:'https://example.invalid/live/u/p/1.ts',
            pause=mock.Mock(), stop=mock.Mock(), play=mock.Mock())
        self.portal = dict(id='p', name='Demo', type='xtream', xc_host='https://example.invalid',
                           xc_user='u', xc_pass='p', start_stream_id='1')
        categories = [dict(category_id='a', category_name='A'),dict(category_id='b', category_name='B')]
        streams = [dict(stream_id=str(i), category_id='a', name=f'Sender {i}') for i in range(1,5)]
        self.client = types.SimpleNamespace(
            get_cached_catalog=lambda action: categories if action=='get_live_categories' else streams,
            live_stream_url=lambda sid, ext:f'https://example.invalid/live/u/p/{sid}.{ext}',
            _get_json=mock.Mock(return_value={}), get_short_epg=mock.Mock())
        gui = types.ModuleType('xbmcgui')
        gui.WindowDialog = OmegaDialog
        gui.ControlList = ControlList
        gui.ControlButton = gui.ControlImage = gui.ControlLabel = Control
        window = types.SimpleNamespace(setProperty=self.props.__setitem__,
            getProperty=lambda k:self.props.get(k,''),clearProperty=lambda k:self.props.pop(k,None))
        gui.Window = lambda *_:window
        gui.Dialog = lambda:types.SimpleNamespace(notification=mock.Mock(),textviewer=mock.Mock())
        xbmc = types.ModuleType('xbmc')
        xbmc.Player = lambda:self.player
        xbmc.executebuiltin = mock.Mock()
        xbmc.getCondVisibility = lambda *_:True
        xbmc.getInfoLabel = lambda *_:''
        addon = types.ModuleType('xbmcaddon')
        addon.Addon = lambda:types.SimpleNamespace(getAddonInfo=lambda *_:str(LIB.parents[1]))
        utils = types.ModuleType('utils')
        utils.info = utils.warn = lambda *a:None
        xtream = types.ModuleType('xtream')
        xtream.XtreamClient = lambda *a:self.client
        iptv = types.ModuleType('iptv')
        iptv.Channel = lambda **kwargs:types.SimpleNamespace(tvg_id='', **{k:v for k,v in kwargs.items() if k!='tvg_id'})
        groups = types.ModuleType('group_selection')
        groups.load = lambda *_:None
        groups.save = mock.Mock()
        epg = types.ModuleType('epg')
        epg.load_cache = lambda *_:{}
        views = types.ModuleType('epg_views')
        views.guide_for_channel = lambda *a:{}
        views.row_title = lambda name, guide:name
        profiles = types.ModuleType('remote_profiles')
        profiles.mapped_action = lambda key:{1:'left',3:'up',4:'down',117:'menu',42:'ok',122:'more'}.get(key)
        portals = types.ModuleType('portals')
        portals.get_by_id = lambda *_:self.portal
        spec = importlib.util.spec_from_file_location('live_recovery',LIB/'live_recovery.py')
        recovery = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(recovery)
        patch = mock.patch.dict(sys.modules,dict(xbmc=xbmc,xbmcgui=gui,xbmcaddon=addon,utils=utils,
            xtream=xtream,iptv=iptv,group_selection=groups,epg=epg,epg_views=views,
            remote_profiles=profiles,portals=portals,live_recovery=recovery))
        patch.start()
        self.addCleanup(patch.stop)
        spec = importlib.util.spec_from_file_location('omega_overlay_test',LIB/'live_overlay.py')
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.overlay = self.module.LiveNavigator(self.portal,'1')
        self.overlay.show()

    def test_show_builds_once_without_an_oninit_callback(self):
        o = self.overlay
        self.assertTrue(o._drawn and o.shown)
        self.assertIs(o.focus,o.control)
        count = len(o.controls)
        o.show()
        self.assertEqual(len(o.controls),count)
        self.assertEqual(o.shows,2)
        self.assertFalse(hasattr(o,'onInit'))
        self.assertFalse(hasattr(o,'onClick'))
        self.assertEqual(self.props['XtreamMate.OverlayStatus'],'bereit')

    def test_native_list_moves_exactly_once_and_bridge_moves_explicitly(self):
        o = self.overlay
        o.native(4)
        self.assertEqual(o.control.selected,1)
        o.native(4)
        self.assertEqual(o.control.selected,2)
        o.native(3)
        self.assertEqual(o.control.selected,1)
        o.handle_command('down')
        self.assertEqual(o.control.selected,2)

    def test_select_callback_and_action_together_tune_only_once(self):
        o = self.overlay
        o._tune = mock.Mock(side_effect=lambda channel:o._switch('hidden'))
        o.native(7)
        o._tune.assert_called_once()
        self.assertEqual(o.mode,'hidden')
        o.native(7)
        self.assertEqual(o.mode,'controls')
        self.player.pause.assert_not_called()
        # Rapid separate keypresses must not be lost to a time-based debounce.
        o.native(7)
        self.player.pause.assert_called_once()
        self.assertEqual(o.mode,'hidden')

    def test_dpad_menu_back_and_visible_focus_textures(self):
        o = self.overlay
        o.native(1)
        self.assertEqual(o.mode,'groups')
        o.native(2)
        self.assertEqual(o.mode,'channels')
        o.native(2)
        self.assertEqual(o.mode,'hidden')
        o.native(1)
        self.assertEqual(o.mode,'channels')
        o.native(117)
        self.assertEqual(o.mode,'extras')
        self.assertIn(o.focus,o.extra_buttons)
        o.native(92)
        self.assertEqual(o.mode,'controls')
        o.native(2)
        self.assertIs(o.focus,o.main_buttons[1])
        o.native(1)
        self.assertIs(o.focus,o.main_buttons[0])
        o.native(4)
        self.assertIs(o.focus,o.main_buttons[1])
        o.native(3)
        self.assertIs(o.focus,o.main_buttons[0])
        for c in [o.control,*o.main_buttons,*o.extra_buttons]:
            focus = c.options.get('focusTexture',c.options.get('buttonFocusTexture'))
            self.assertTrue(Path(focus).is_file())
        self.assertNotEqual(o.control.options['buttonTexture'],o.control.options['buttonFocusTexture'])

    def test_learned_ok_has_no_native_click_but_still_executes(self):
        self.overlay._switch('hidden')
        self.overlay.native(42)
        self.assertEqual(self.overlay.mode,'controls')
        self.overlay.native(42)
        self.player.pause.assert_called_once()

    def test_foreign_playback_releases_dialog_and_session_immediately(self):
        o = self.overlay
        self.module.announce('p','1')
        self.props['XtreamMate.RemoteCommand'] = 'queued'
        self.player.getPlayingFile = lambda:'plugin://another.addon/movie'
        o.native(117)
        self.assertTrue(o._closed)
        self.assertFalse(o.shown)
        self.assertNotIn(self.module.SESSION_KEY,self.props)
        self.assertNotIn('XtreamMate.RemoteCommand',self.props)
        self.assertIsNone(self.module.start_if_eligible(''))

    def test_stop_closes_once_and_does_not_clear_a_new_portal_session(self):
        o = self.overlay
        self.module.announce('other','2')
        o.native(13)
        self.player.stop.assert_called_once()
        o.close()
        self.assertEqual(o.closes,1)
        self.assertEqual(self.module.session_from_property(self.props[self.module.SESSION_KEY])['pid'],'other')

    def test_async_tune_retains_old_verified_stream_for_bounded_transition(self):
        player=types.ModuleType('player')
        player.build_playable_item=lambda *a,**kw:types.SimpleNamespace(getPath=lambda:a[0])
        with mock.patch.dict(sys.modules,{'player':player}):
            self.overlay.native(4)
            self.overlay.native(7)
        self.assertEqual(self.overlay.sid,'2')
        self.assertFalse(self.overlay._closed)
        self.assertTrue(self.overlay.owns_playback())
        self.overlay._tune_deadline=0
        self.assertFalse(self.overlay.owns_playback())
        self.player.getPlayingFile=lambda:'https://example.invalid/live/u/p/2.ts'
        self.assertTrue(self.overlay.owns_playback())

    def test_stop_clears_owned_session_and_prevents_reopening(self):
        self.module.announce('p','1')
        self.overlay.native(13)
        self.assertNotIn(self.module.SESSION_KEY,self.props)
        self.overlay.show()
        self.assertFalse(self.overlay.shown)

    def test_group_settings_from_controls_use_only_cached_categories(self):
        self.overlay._switch('extras')
        self.overlay._execute('extras',4)
        self.assertEqual(self.overlay.mode,'groups')

    def test_failed_show_releases_partial_window(self):
        o = self.module.LiveNavigator(self.portal,'1')
        with mock.patch.object(OmegaDialog,'show',side_effect=RuntimeError('GUI failure')):
            with self.assertRaises(RuntimeError): o.show()
        self.assertTrue(o._closed)
        self.assertEqual(o.closes,1)

    def test_epg_input_schedules_network_in_worker_only(self):
        self.overlay._switch('hidden')
        with mock.patch('threading.Thread') as thread:
            self.overlay.handle_command('info')
            thread.return_value.start.assert_called_once()
            self.client.get_short_epg.assert_not_called()
            thread.call_args.kwargs['target']()
            self.client.get_short_epg.assert_called_once()

    def run_service_once(self, existing=None):
        class Monitor:
            def __init__(self): self.finished=False
            def abortRequested(self): return self.finished
            def waitForAbort(self, timeout): self.finished=True; return True
        sys.modules['xbmc'].Monitor=Monitor
        sys.modules['utils'].setting_bool=lambda key,default=False:False
        sys.modules['utils'].setting_int=lambda key,default=0:default
        sys.modules['utils'].error=lambda *a:None
        sys.modules['portals'].get_active=lambda:[self.portal]
        remote=types.ModuleType('remote_control')
        remote.COMMAND_KEY='XtreamMate.RemoteCommand'
        remote.parse_command=lambda _:None
        remote.ensure_for_live_tv=mock.Mock(return_value='native')
        remote.release_unrequested_keymap=mock.Mock(return_value=False)
        healthspec=importlib.util.spec_from_file_location('omega_health',LIB/'service_health.py')
        health=importlib.util.module_from_spec(healthspec)
        healthspec.loader.exec_module(health)
        with mock.patch.dict(sys.modules,dict(live_overlay=self.module,remote_control=remote,service_health=health)):
            spec=importlib.util.spec_from_file_location('omega_service',LIB.parents[1]/'service.py')
            module=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            with mock.patch.object(module.IPTVMasterService,'_start_reminders'):
                service=module.IPTVMasterService()
            if existing:
                service._overlay=existing
                service._last_session_nonce=self.module.session_from_property(self.props[self.module.SESSION_KEY])['nonce']
            service.run()
        self.assertNotIn('Fehler',self.props.get(health.LAST_ERROR,''))
        return remote

    def test_service_starts_real_dialog_and_cleans_it_on_shutdown(self):
        self.module.announce('p','1')
        candidate=self.module.LiveNavigator(self.portal,'1')
        with mock.patch.object(self.module,'LiveNavigator',return_value=candidate):
            self.run_service_once()
        self.assertTrue(candidate._drawn)
        self.assertEqual(candidate.shows,1)
        self.assertEqual(candidate.closes,1)
        self.assertNotIn(self.module.SESSION_KEY,self.props)

    def test_service_releases_foreign_playback_without_new_key_events(self):
        self.module.announce('p','1')
        self.player.getPlayingFile=lambda:'plugin://another.addon/movie'
        self.run_service_once(existing=self.overlay)
        self.assertTrue(self.overlay._closed)
        self.assertEqual(self.overlay.closes,1)

    def test_service_waits_until_kodi_has_activated_fullscreen(self):
        self.module.announce('p','1')
        sys.modules['xbmc'].getCondVisibility=lambda _:False
        candidate=self.module.LiveNavigator(self.portal,'1')
        with mock.patch.object(self.module,'LiveNavigator',return_value=candidate):
            self.run_service_once()
        self.assertEqual(candidate.shows,0)
        self.assertIn(self.module.SESSION_KEY,self.props)
        self.assertIn('WAIT_FULLSCREEN',self.props.get('XtreamMate.Diagnostic.dialog',''))

    def test_redirected_tune_retains_previous_tag_only_during_transition(self):
        session=self.module.announce('p','1')
        self.player.getPlayingFile=lambda:'https://redirect.invalid/opaque'
        self.player.getVideoInfoTag=lambda:types.SimpleNamespace(getUniqueID=lambda _:__import__('json').dumps(session))
        self.assertTrue(self.overlay.owns_playback())
        player=types.ModuleType('player')
        player.build_playable_item=lambda *a,**kw:types.SimpleNamespace(getPath=lambda:a[0])
        with mock.patch.dict(sys.modules,{'player':player}):
            self.overlay._tune(self.overlay.channels[1])
        self.assertTrue(self.overlay.owns_playback())
        self.overlay._tune_deadline=0
        self.assertFalse(self.overlay.owns_playback())


if __name__ == '__main__': unittest.main()
