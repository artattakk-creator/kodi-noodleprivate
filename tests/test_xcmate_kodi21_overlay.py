import json
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
    def __init__(self, options=None):
        self.visible = True
        self.enabled = True
        self.options = options or {}
        self.items = []
        self.selected = 0
    def getId(self): return id(self)
    def setVisible(self, value): self.visible = value
    def setEnabled(self, enabled): self.enabled = enabled
    def setWidth(self, width): self.width = width
    def setPosition(self, x, y): self.position = (x,y)
    def setImage(self, imageFilename, useCache=True): self.image = imageFilename
    def setLabel(self, label='', font=None, textColor=None, disabledColor=None,
                 shadowColor=None, focusedColor=None, label2=''): self.label = label
    def setNavigation(self, up, down, left, right):
        assert all(isinstance(c, Control) for c in (up, down, left, right))
        self.navigation = (up, down, left, right)
    def controlLeft(self, control): self.left = control
    def controlRight(self, control): self.right = control
    def reset(self): self.items = []
    def addItems(self, items): self.items = list(items)
    def size(self): return len(self.items)
    def selectItem(self, index): self.selected = index
    def getSelectedPosition(self): return self.selected


class ControlList(Control):
    # Actual Omega legacy/Control.h binding parameter names, NOT the
    # unprefixed names shown in some generated documentation examples.
    def __init__(self, x, y, width, height, font=None, textColor=None,
                 buttonTexture=None, buttonFocusTexture=None, selectedColor=None,
                 _imageWidth=10, _imageHeight=10, _itemTextXOffset=10,
                 _itemTextYOffset=2, _itemHeight=27, _space=2, _alignmentY=4):
        super().__init__(locals().copy())


class ControlButton(Control):
    def __init__(self, x, y, width, height, label, focusTexture=None,
                 noFocusTexture=None, textOffsetX=10, textOffsetY=2,
                 alignment=4, font=None, textColor=None, disabledColor=None,
                 angle=0, shadowColor=None, focusedColor=None):
        super().__init__(locals().copy())


class ControlLabel(Control):
    def __init__(self, x, y, width, height, label, font=None, textColor=None,
                 disabledColor=None, alignment=0, hasPath=False, angle=0):
        super().__init__(locals().copy())


class ControlImage(Control):
    def __init__(self, x, y, width, height, filename, aspectRatio=0, colorDiffuse=None):
        super().__init__(locals().copy())


class OmegaDialog:
    def __init__(self):
        self.controls = []
        self.focus = None
        self.shown = False
        self.shows = self.closes = 0
    def getWidth(self): return 1280
    def getHeight(self): return 720
    def addControl(self, control):
        assert isinstance(control, Control)
        self.controls.append(control)
    def addControls(self, pControls):
        for control in pControls: self.addControl(control)
    def setFocus(self, control):
        assert control in self.controls and control.visible and control.enabled
        self.focus = control
    def getFocusId(self): return self.focus.getId() if self.focus else -1
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
        elif key in (1,2,3,4) and self.focus:
            if isinstance(self.focus,ControlList):
                target=getattr(self.focus,'left' if key==1 else 'right',self.focus)
            else:
                target=self.focus.navigation[{3:0,4:1,1:2,2:3}[key]]
            if target.enabled: self.setFocus(target)
        if key == 7 and hasattr(self, 'onControl') and self.focus.enabled:
            self.onControl(self.focus)
        self.onAction(types.SimpleNamespace(getId=lambda:key, getButtonCode=lambda:0))


class OverlayLifecycleTests(unittest.TestCase):
    def setUp(self):
        path_patch = mock.patch.object(sys, 'path', [str(LIB)] + sys.path)
        path_patch.start()
        self.addCleanup(path_patch.stop)
        self.props = {}
        self.paused=False
        def pause(): self.paused=not self.paused
        self.player = types.SimpleNamespace(
            isPlayingVideo=lambda:True, getPlayingFile=lambda:'https://example.invalid/live/u/p/1.ts',
            getTotalTime=lambda:3600, getTime=lambda:0,
            pause=mock.Mock(side_effect=pause), stop=mock.Mock(), play=mock.Mock(),seekTime=mock.Mock())
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
        gui.ControlButton = ControlButton
        gui.ControlImage = ControlImage
        gui.ControlLabel = ControlLabel
        window = types.SimpleNamespace(setProperty=self.props.__setitem__,
            getProperty=lambda k:self.props.get(k,''),clearProperty=lambda k:self.props.pop(k,None))
        gui.Window = lambda *_:window
        gui.Dialog = lambda:types.SimpleNamespace(notification=mock.Mock(),textviewer=mock.Mock())
        xbmc = types.ModuleType('xbmc')
        xbmc.Monitor = lambda:types.SimpleNamespace(abortRequested=lambda:False)
        xbmc.Player = lambda:self.player
        xbmc.executebuiltin = mock.Mock()
        xbmc.getCondVisibility = lambda condition:self.paused if condition=='Player.Paused' else True
        xbmc.getInfoLabel = lambda *_:''
        addon = types.ModuleType('xbmcaddon')
        addon.Addon = lambda:types.SimpleNamespace(getAddonInfo=lambda *_:str(LIB.parents[1]))
        utils = types.ModuleType('utils')
        utils.info = utils.warn = lambda *a:None
        utils.setting=lambda key,default='':default
        xtream = types.ModuleType('xtream')
        xtream.XtreamClient = lambda *a:self.client
        iptv = types.ModuleType('iptv')
        iptv.Channel = lambda **kwargs:types.SimpleNamespace(tvg_id='', **{k:v for k,v in kwargs.items() if k!='tvg_id'})
        groups = types.ModuleType('group_selection')
        groups.load = lambda *_:None
        groups.enabled_ids = lambda pid,kind,categories:{str(c['category_id']) for c in categories}
        groups.save = mock.Mock()
        epg = types.ModuleType('epg')
        epg.load_cache = lambda *_:{}
        views_spec = importlib.util.spec_from_file_location('epg_views',LIB/'epg_views.py')
        views = importlib.util.module_from_spec(views_spec)
        views_spec.loader.exec_module(views)
        utils.addon_data_dir = lambda:'/unused'
        profiles_spec = importlib.util.spec_from_file_location('remote_profiles',LIB/'remote_profiles.py')
        profiles = importlib.util.module_from_spec(profiles_spec)
        with mock.patch.dict(sys.modules,utils=utils): profiles_spec.loader.exec_module(profiles)
        self.bindings = dict(profiles.DEFAULT, ok=42)
        profiles.load = mock.Mock(side_effect=lambda:dict(self.bindings))
        portals = types.ModuleType('portals')
        portals.get_by_id = lambda *_:self.portal
        spec = importlib.util.spec_from_file_location('live_recovery',LIB/'live_recovery.py')
        recovery = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(recovery)
        patch = mock.patch.dict(sys.modules,dict(xbmc=xbmc,xbmcgui=gui,xbmcaddon=addon,utils=utils,
            xtream=xtream,iptv=iptv,group_selection=groups,epg=epg,epg_views=views,
            remote_profiles=profiles,portals=portals,live_recovery=recovery,
            app_services=types.SimpleNamespace(poll=lambda:None)))
        patch.start()
        self.addCleanup(patch.stop)
        data_spec = importlib.util.spec_from_file_location('tv_data',LIB/'tv_data.py')
        data = importlib.util.module_from_spec(data_spec)
        data_spec.loader.exec_module(data)
        data_patch = mock.patch.dict(sys.modules, {'tv_data':data})
        data_patch.start()
        self.addCleanup(data_patch.stop)
        start_patch = mock.patch.object(data.GuideSnapshot,'start',lambda _:None)
        start_patch.start()
        self.addCleanup(start_patch.stop)
        spec = importlib.util.spec_from_file_location('omega_overlay_test',LIB/'live_overlay.py')
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.overlay = self.module.LiveNavigator(self.portal,'1')
        self.overlay.show()
        self.addCleanup(self.overlay.close)
        self.overlay.handle_command('left')

    def finish_owned_exit(self):
        import live_exit
        value=live_exit.state();self.assertIsNotNone(value)
        value['not_before']=0;live_exit._save(value)
        self.player.stop.assert_not_called()
        self.player.stop.side_effect=lambda:setattr(self.player,'isPlayingVideo',lambda:False)
        live_exit.poll(self.overlay)
        from exit37_fixture import drain_stop
        drain_stop()
        live_exit.poll(self.overlay)
        live_exit.poll(self.overlay)

    def tag_current_live(self):
        session=self.module.announce('p','1')
        self.player.getVideoInfoTag=lambda:types.SimpleNamespace(getUniqueID=lambda key:json.dumps(session) if key=='xcmate_live' else '')

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
        self.assertEqual(o.control.options['_itemHeight'],46)
        self.assertEqual(o.control.options['_space'],3)

    def test_native_left_survives_stale_profile_on_capture_and_list_ten_times(self):
        self.bindings['left']=88
        self.bindings['more']=1  # historical collision with native LEFT
        o=self.module.LiveNavigator(self.portal,'1')
        self.addCleanup(o.close)
        o.show()
        for _ in range(10):
            self.assertIs(o.focus,o.capture)
            o.native(1)
            self.assertEqual(o.mode,'channels')
            self.assertIs(o.focus,o.control)
            o.native(1)
            self.assertEqual(o.mode,'groups')
            o.native(2)
            self.assertEqual(o.mode,'channels')
            o.native(92)
            self.assertEqual(o.mode,'hidden')
        self.player.pause.assert_not_called()
        self.player.stop.assert_not_called()
        self.assertEqual(o._left_counts,dict(left_received=20,left_channels=10,left_groups=10))

    def test_profile_is_not_read_in_native_callbacks(self):
        o=self.overlay
        profiles=sys.modules['remote_profiles']
        profiles.load.side_effect=AssertionError('profile disk read in callback')
        o._switch('hidden')
        for key in (1,1,2,92,42,4,4,3,3,92): o.native(key)

    def test_corrupt_remote_profile_falls_back_without_blocking_dialog_start(self):
        profiles=sys.modules['remote_profiles']
        profiles.load.side_effect=ValueError('invalid profile')
        o=self.module.LiveNavigator(self.portal,'1')
        self.addCleanup(o.close)
        o.show()
        o.native(1)
        self.assertEqual(o.mode,'channels')
        o.native(1)
        self.assertEqual(o.mode,'groups')

    def test_native_left_trace_contains_mapping_mode_transition_and_focus(self):
        o=self.overlay
        o._switch('hidden')
        with mock.patch.object(self.module,'trace') as trace:
            o.native(1)
        handled=next(c for c in trace.call_args_list if c.args==('input','COMMAND_HANDLED'))
        self.assertEqual(handled.kwargs['input_source'],'native')
        self.assertEqual(handled.kwargs['action_id'],1)
        self.assertEqual(handled.kwargs['command'],'left')
        self.assertEqual(handled.kwargs['mode_before'],'hidden')
        self.assertEqual(handled.kwargs['mode_after'],'channels')
        self.assertEqual(handled.kwargs['focus_before'],o.capture.getId())
        self.assertEqual(handled.kwargs['focus_id'],o.control.getId())

    def test_play_pause_updates_label_and_icon_and_only_stop_stops(self):
        o=self.overlay
        o._switch('controls')
        self.assertEqual(o.main_buttons[0].label,'Pause')
        o.native(7)
        self.player.pause.assert_called_once()
        self.assertEqual(o.mode,'controls')
        self.assertEqual(o.main_buttons[0].label,'Weiter')
        self.assertTrue(o._button_icons[0][1].image.endswith('player-play-normal.png'))
        o.native(7)
        self.assertEqual(self.player.pause.call_count,2)
        self.assertEqual(o.main_buttons[0].label,'Pause')
        self.player.stop.assert_not_called()
        self.tag_current_live()
        o._focus_main=3
        o._render()
        o.native(7)
        self.finish_owned_exit()
        self.player.stop.assert_called_once()
        self.assertTrue(o._closed)

    def test_seek_and_live_edge_are_clamped_and_capability_rechecked(self):
        o=self.overlay
        self.player.getTime=lambda:5
        o._switch('controls')
        o._execute('controls',1)
        self.player.seekTime.assert_called_with(0)
        self.player.getTime=lambda:3595
        o._execute('controls',2)
        self.player.seekTime.assert_called_with(3600)
        o._execute('controls',5)
        self.player.seekTime.assert_called_with(3600)
        self.player.seekTime.reset_mock()
        for duration in (0,5,float('nan'),float('inf')):
            self.player.getTotalTime=lambda:duration
            o._render()
            self.assertTrue(all(o.main_buttons[i].visible for i in (1,2,5)))
            self.assertFalse(any(o.main_buttons[i].enabled for i in (1,2,5)))
            for i in (1,2,5): o._execute('controls',i)
            o.handle_command('long_play_pause')
        self.player.seekTime.assert_not_called()
        self.player.getTotalTime=lambda:3600
        sys.modules['xbmc'].getCondVisibility=lambda _:False
        o._execute('controls',5)
        self.player.seekTime.assert_not_called()

    def test_tick_reflects_external_pause_without_moving_focus(self):
        o=self.overlay
        o._switch('controls')
        o.native(2)
        focused=o.focus
        self.paused=True
        o._last_tick=0
        o.tick()
        self.assertEqual(o.main_buttons[0].label,'Weiter')
        self.assertIs(o.focus,focused)

    def test_lost_seek_capability_repairs_focus_only_in_own_top_dialog(self):
        o=self.overlay
        gui=sys.modules['xbmcgui']
        for own in (True,False):
            self.player.getTotalTime=lambda:3600
            o._switch('controls')
            o._focus_main=1
            o._render()
            self.player.getTotalTime=lambda:0
            saved_window=gui.Window
            top=types.SimpleNamespace(getProperty=lambda _:o._window_nonce if own else 'other')
            with mock.patch.object(gui,'getCurrentWindowDialogId',return_value=12345,create=True), \
                 mock.patch.object(gui,'Window',side_effect=lambda ident:saved_window(ident) if ident==10000 else top):
                o._last_tick=0
                o.tick()
            self.assertIs(o.focus,o.main_buttons[0 if own else 1])
        self.player.pause.assert_not_called()
        self.player.stop.assert_not_called()

    def test_frozen_025_infobar_geometry_assets_and_text(self):
        o=self.overlay
        expected=[(32,472,1216,216),(54,506,96,96),(174,486,1060,32),
                  (174,527,815,29),(1000,527,230,29),(174,567,820,8),
                  (174,567,820,8),(174,589,1060,27),(174,621,1060,29),
                  (174,659,1060,24)]
        self.assertEqual([tuple(c.options[k] for k in ('x','y','width','height'))
                          for c in o._info_controls],expected)
        self.assertEqual(o.info_hint.options['label'],
                         'OK / Runter: Bedienung    Links: Sender    Zurück: TV')
        self.assertEqual(o.info_now.options['textColor'],'0xFFF0F2F5')
        self.assertTrue(o.info_bg.options['filename'].endswith('tv_panel.png'))
        self.assertTrue(o.info_progress.options['filename'].endswith('tv_progress.png'))

    def test_down_and_up_change_levels_without_executing_transport(self):
        o=self.overlay
        o._switch('hidden')
        for key,mode in ((7,'info'),(7,'controls'),(4,'extras'),(3,'controls'),
                         (3,'info'),(3,'hidden')):
            o.native(key)
            self.assertEqual(o.mode,mode)
        self.player.pause.assert_not_called()
        self.player.stop.assert_not_called()

    def test_native_binding_rejects_both_old_keyword_names(self):
        for keyword in ('itemHeight', 'space'):
            with self.subTest(keyword=keyword), self.assertRaises(TypeError):
                ControlList(0, 0, 400, 500, **{keyword: 46})

    def test_first_second_ok_down_and_back_follow_two_stage_ui_without_player_action(self):
        o=self.overlay
        o._switch('hidden')
        o.native(7)
        self.assertEqual(o.mode,'info')
        self.assertIs(o.focus,o.capture)
        self.assertTrue(o.info_bg.visible)
        self.assertFalse(any(c.visible for c in o.main_buttons+o.extra_buttons))
        self.assertIn('Sender 1',o.info_name.label)
        self.assertIn('keine EPG-Daten',o.info_now.label)
        self.assertFalse(o.info_progress.visible)
        self.assertFalse(o.info_duration.visible)
        o.native(7)
        self.assertEqual(o.mode,'controls')
        self.assertIs(o.focus,o.main_buttons[0])
        self.player.pause.assert_not_called()
        self.player.stop.assert_not_called()
        o.native(92)
        self.assertEqual(o.mode,'info')
        o.native(4)
        self.assertEqual(o.mode,'controls')
        self.player.pause.assert_not_called()
        o.native(92)
        o.native(92)
        self.assertEqual(o.mode,'hidden')

    def test_infobar_uses_actual_cached_timestamps_and_expires_without_stopping(self):
        o=self.overlay
        now=self.module.time.time()
        views=sys.modules['epg_views']
        o._guide._values['1']=views.guide_for_channel({'x':[
            {'name':'Actual News','start_timestamp':now-1800,'stop_timestamp':now+1800},
            {'name':'Actual Next','start_timestamp':now+1800,'stop_timestamp':now+3600}]},'x',now=now)
        o._switch('info')
        self.assertIn('Actual News',o.info_now.label)
        self.assertIn('Actual Next',o.info_next.label)
        self.assertTrue(o.info_progress.visible)
        self.assertAlmostEqual(o.info_progress.width/o._progress_width,.5,places=2)
        o._info_deadline=0
        o.tick()
        self.assertEqual(o.mode,'hidden')
        self.player.stop.assert_not_called()

    def test_navigation_and_identity_checks_never_read_disk_or_call_client(self):
        o=self.overlay
        self.client.get_cached_catalog=mock.Mock(side_effect=AssertionError('catalog read in callback'))
        self.client._get_json.side_effect=AssertionError('HTTP/cache access in callback')
        self.client.get_short_epg.side_effect=AssertionError('HTTP in callback')
        with mock.patch.object(sys.modules['epg'],'load_cache',side_effect=AssertionError('disk read')):
            o._switch('hidden')
            for key in (7,7,2,1,117,92,92,1,4,3,92): o.native(key)
        self.client.get_cached_catalog.assert_not_called()
        self.client._get_json.assert_not_called()
        self.client.get_short_epg.assert_not_called()

    def test_background_program_update_preserves_focus_and_shows_real_programmes(self):
        o=self.overlay
        o.handle_command('epg')
        self.assertEqual(o.mode,'guide')
        self.assertIn('Keine EPG-Daten',o.control.items[0])
        now=self.module.time.time()
        o._guide._values['1']=sys.modules['epg_views'].guide_for_channel({'x':[
            {'name':'Programme One','start_timestamp':now-60,'stop_timestamp':now+600}]},'x')
        o._guide.generation+=1
        o._last_tick=0
        o.setFocus(o.capture)  # simulate a native dialog temporarily above us
        o.tick()
        self.assertIn('Programme One',o.control.items[0])
        self.assertIs(o.focus,o.capture)
        self.player.play.assert_not_called()

    def test_native_audio_video_subtitles_windows_and_unseekable_controls(self):
        o=self.overlay
        self.player.getTotalTime=lambda:0
        o._switch('controls')
        self.assertFalse(o.main_buttons[1].enabled or o.main_buttons[2].enabled or o.main_buttons[5].enabled)
        o.native(2)
        self.assertIs(o.focus,o.main_buttons[3])
        for index,window in enumerate(('osdaudiosettings','osdvideosettings','osdsubtitlesettings')):
            o._switch('extras')
            o._execute('extras',index)
            sys.modules['xbmc'].executebuiltin.assert_called_with('ActivateWindow('+window+')')

    def test_viewport_has_at_most_eight_visible_rows_and_separate_live_focus(self):
        o=self.overlay
        o.native(4)
        titles=[row[2].label for row in o._row_controls if row[2].visible]
        self.assertTrue(titles[0].startswith('LIVE  '))
        self.assertFalse(titles[1].startswith('LIVE  '))
        self.assertTrue(o._row_controls[1][0].visible)
        self.assertLessEqual(len(titles),8)
        self.assertLessEqual(len(o._guide._wanted),9)

    def test_53664_channels_render_bounded_pages_and_tune_absolute_selection(self):
        o = self.overlay
        o.channels = [types.SimpleNamespace(name='Sender '+str(i), tvg_id='',
            extra={'stream_id':str(i), 'category_id':'a'}) for i in range(1,53665)]
        o.index = sys.modules['tv_data'].CatalogIndex(o.channels)
        o.sid = '53664'
        self.player.getPlayingFile = lambda:'https://example.invalid/live/u/p/53664.ts'
        self.client.get_cached_catalog = lambda action: ([{'stream_id':'53664'}]
            if action == 'get_live_streams' else [])
        o._scroll_to_current = True
        with mock.patch.object(o._guide,'get',wraps=o._guide.get) as lookup:
            o._render()
            self.assertLessEqual(lookup.call_count,9)
            self.assertLessEqual(o.control.size(),102)
            self.assertEqual(o.control.items[o.control.selected],'Sender 53664')
            o._tune = mock.Mock()
            o.native(7)
            self.assertEqual(o._tune.call_args.args[0].extra['stream_id'],'53664')
            o._tune.reset_mock()
            # Every row is now a real station, no visible page actions.
            o.control.selectItem(0)
            o.native(7)
            self.assertEqual(o._tune.call_args.args[0].extra['stream_id'],'53601')
            o._tune.reset_mock()
            o._highlight['channels']=53599;o._scroll_to_current=False;o._render()
            o.native(4)
            self.assertEqual(o._highlight['channels'],53600)
            self.assertEqual(o.control.items[o.control.selected],'Sender 53601')
            o.native(3)
            self.assertEqual(o._highlight['channels'],53599)
            self.assertEqual(o.control.items[o.control.selected],'Sender 53600')
            o._tune.assert_not_called()
            self.assertLessEqual(o.control.size(),100)

    def test_constructor_failure_preserves_stage_and_safe_exception_class(self):
        o = self.module.LiveNavigator(self.portal, '1')
        with mock.patch.object(sys.modules['xbmcgui'], 'ControlList',
                               side_effect=TypeError('private://do-not-record')), \
             mock.patch.object(self.module, 'trace') as trace:
            with self.assertRaises(TypeError): o.show()
        trace.assert_any_call('dialog', 'SHOW_FAILED', failure_stage='CONTROL_LIST',
                              exception_class='TypeError')
        self.assertFalse(any(call.args[:2] == ('dialog','SHOW_REQUESTED')
                             for call in trace.call_args_list))
        self.assertTrue(o._closed)

    def test_remote_learning_builds_before_modal_without_oninit_or_onclick(self):
        spec = importlib.util.spec_from_file_location('omega_learning_test', LIB/'remote_profiles.py')
        learning = importlib.util.module_from_spec(spec)
        with mock.patch.object(sys.modules['utils'], 'addon_data_dir', return_value='/unused', create=True):
            spec.loader.exec_module(learning)
        case = self
        def native_modal(dialog):
            case.assertEqual(len(dialog.controls), 2)
            case.assertIs(dialog.focus, dialog.focus_button)
            case.assertFalse(hasattr(dialog, 'onInit'))
            case.assertFalse(hasattr(dialog, 'onClick'))
            dialog.onAction(types.SimpleNamespace(getId=lambda:7, getButtonCode=lambda:615))
        with mock.patch.object(OmegaDialog, 'doModal', native_modal, create=True):
            self.assertEqual(learning._capture(), (7,615))

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

    def test_native_page_action_in_short_list_remembers_kodis_position(self):
        o = self.overlay
        o.native(6)
        self.assertEqual(o._highlight['channels'],o.control.getSelectedPosition())
        self.assertEqual(o._highlight['channels'],3)

    def test_select_callback_and_action_together_tune_only_once(self):
        o = self.overlay
        o._tune = mock.Mock(side_effect=lambda channel:o._switch('hidden'))
        o.native(7)
        o._tune.assert_called_once()
        self.assertEqual(o.mode,'hidden')
        o.native(7)
        self.assertEqual(o.mode,'info')
        o.native(7)
        self.assertEqual(o.mode,'controls')
        self.player.pause.assert_not_called()
        # Rapid separate keypresses must not be lost to a time-based debounce.
        o.native(7)
        self.player.pause.assert_called_once()
        self.assertEqual(o.mode,'controls')

    def test_dpad_menu_back_and_visible_focus_textures(self):
        o = self.overlay
        o.native(1)
        self.assertEqual(o.mode,'groups')
        o.native(2)
        self.assertEqual(o.mode,'channels')
        o.native(2)
        self.assertEqual(o.mode,'channels')
        o.native(92)
        self.assertEqual(o.mode,'hidden')
        o.native(1)
        self.assertEqual(o.mode,'channels')
        o.native(117)
        self.assertEqual(o.mode,'extras')
        self.assertIn(o.focus,o.extra_buttons)
        o.native(92)
        self.assertEqual(o.mode,'controls')
        o.native(2)
        self.assertIs(o.focus,o.main_buttons[2])
        o.native(1)
        self.assertIs(o.focus,o.main_buttons[0])
        o.native(4)
        self.assertEqual(o.mode,'extras')
        self.assertIs(o.focus,o.extra_buttons[0])
        o.native(3)
        self.assertEqual(o.mode,'controls')
        self.assertIs(o.focus,o.main_buttons[0])
        for c in [o.control,*o.main_buttons,*o.extra_buttons]:
            focus = c.options.get('focusTexture',c.options.get('buttonFocusTexture'))
            self.assertTrue(Path(focus).is_file())
        o._switch('channels')
        self.assertEqual(sum(row[0].visible for row in o._row_controls),1)
        self.assertNotEqual(o.main_buttons[0].options['focusTexture'],
                            o.main_buttons[0].options['noFocusTexture'])

    def test_learned_ok_has_no_native_click_but_still_executes(self):
        self.overlay._switch('hidden')
        self.overlay.native(42)
        self.assertEqual(self.overlay.mode,'info')
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
        self.player.stop.assert_not_called()  # A newer foreign session rejects stale Exit.
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
        self.tag_current_live()
        self.overlay.native(13)
        self.finish_owned_exit()
        self.assertNotIn(self.module.SESSION_KEY,self.props)
        self.overlay.show()
        self.assertFalse(self.overlay.shown)

    def test_group_settings_from_controls_use_only_cached_categories(self):
        self.overlay._switch('extras')
        self.overlay._execute('extras',5)
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
            self.overlay.handle_command('epg')
            self.assertEqual(self.overlay.mode,'guide')
            thread.assert_not_called()
            self.client.get_short_epg.assert_not_called()
            self.client._get_json.assert_not_called()

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

    def test_optional_new_app_worker_failure_does_not_block_frozen_live_dialog(self):
        sys.modules['app_services'].poll=mock.Mock(side_effect=ValueError('optional index unavailable'))
        self.module.announce('p','1')
        candidate=self.module.LiveNavigator(self.portal,'1')
        with mock.patch.object(self.module,'LiveNavigator',return_value=candidate):
            self.run_service_once()
        self.assertEqual(candidate.shows,1)
        self.assertEqual(candidate.closes,1)

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

    def test_rejected_native_event_is_distinct_from_no_callback(self):
        self.player.getPlayingFile=lambda:'plugin://another.addon/movie'
        self.overlay.onAction(types.SimpleNamespace(getId=lambda:7,getButtonCode=lambda:23))
        self.assertTrue(self.overlay._closed)
        self.assertIn('ACTION_REJECTED',self.props['XtreamMate.Diagnostic.input'])
        self.assertIn('"action_id": 7',self.props['XtreamMate.Diagnostic.input'])

    def test_malformed_and_expired_markers_have_distinct_diagnostic_codes(self):
        import json
        self.assertIsNone(self.module.session_from_property('not-json'))
        self.assertIn('MARKER_INVALID',self.props['XtreamMate.Diagnostic.session'])
        self.assertIsNone(self.module.session_from_property(json.dumps(
            dict(pid='p',sid='1',nonce='n',at=1)),now=100000))
        self.assertIn('MARKER_EXPIRED',self.props['XtreamMate.Diagnostic.session'])


if __name__ == '__main__': unittest.main()
