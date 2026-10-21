"""0.1.28 callback models, persisted language/appearance, and cold/warm UI."""
import importlib
import json
from pathlib import Path
import sys
import time
import types
import unittest
from unittest import mock
import xml.etree.ElementTree as ET
from xcmate027_fixture import Fixture,ADDON


class NewUITests(Fixture,unittest.TestCase):
    def test_independent_language_de_en_kodi_upgrade_and_content_filter(self):
        l10n=importlib.import_module('localization');home=importlib.import_module('home_menu')
        self.ui_locale='en_gb';self.options['lang_priority']='de'
        self.options['xcmate_ui_language']='de_de';home.show(self.router,self.portal)
        self.assertEqual(self.added[3][1].label,'Filme')
        self.options['xcmate_ui_language']='en_gb';self.added.clear();self.ui_locale='de_de';home.show(self.router,self.portal)
        self.assertEqual(self.added[3][1].label,'Movies')
        self.options['xcmate_ui_language']='kodi';self.added.clear();home.show(self.router,self.portal)
        self.assertEqual(self.added[3][1].label,'Filme');self.assertEqual(self.options['lang_priority'],'de')
        self.assertFalse(self.builtins)

    def test_language_selection_save_cancel_and_no_global_language_write(self):
        l10n=importlib.import_module('localization')
        self.dialog.select.return_value=0;self.assertTrue(l10n.choose_language())
        self.assertEqual(self.options,{'xcmate_ui_language':'de_de'})
        self.dialog.select.return_value=-1;self.assertFalse(l10n.choose_language())
        self.assertEqual(self.options,{'xcmate_ui_language':'de_de'})

    def test_appearance_save_reload_invalid_values_and_atomic_write_failure(self):
        appearance=importlib.import_module('appearance')
        values=dict(appearance.DEFAULT,background='123456',accent='ABCDEF',font='large',panel_opacity=0)
        appearance.save(values)
        self.assertEqual(appearance.read()['background'],'123456');self.assertEqual(appearance.read()['panel_opacity'],25)
        before=Path(appearance.path()).read_bytes()
        with mock.patch.object(appearance.os,'replace',side_effect=OSError('full')):
            with self.assertRaises(OSError): appearance.save(dict(values,background='FFFFFF'))
        self.assertEqual(Path(appearance.path()).read_bytes(),before)
        Path(appearance.path()).write_text('corrupt');self.assertEqual(appearance.read(),appearance.DEFAULT)
        self.assertEqual(appearance.validate(dict(background='../../bad',font='missing'))['background'],appearance.DEFAULT['background'])

    def test_generated_windowxml_stable_ids_navigation_fonts_colour_alpha_and_original_unchanged(self):
        appearance=importlib.import_module('appearance');original=(ADDON/'resources/skins/Default/720p/XCMateMedia.xml').read_bytes()
        appearance.save(dict(appearance.DEFAULT,icon_opacity=50,background_opacity=40,font='large',accent='112233'))
        script=appearance.window_source('XCMateMedia.xml')
        generated=ET.parse(Path(script)/'resources/skins/Default/720p/XCMateMedia.xml')
        source=ET.fromstring(original)
        for a,b in zip(source.iter('control'),generated.getroot().iter('control')):
            self.assertEqual(a.get('id'),b.get('id'))
            for key in ('onleft','onright','onup','ondown'): self.assertEqual(a.findtext(key),b.findtext(key))
        self.assertEqual(generated.findtext("./controls/control[@id='101']/textcolor"),'FF112233')
        posters=[n for n in generated.iter('texture') if (n.text or '').startswith('$INFO[ListItem.Art')]
        self.assertTrue(posters);self.assertTrue(all(n.get('colordiffuse')=='80FFFFFF' for n in posters))
        self.assertEqual((ADDON/'resources/skins/Default/720p/XCMateMedia.xml').read_bytes(),original)
        self.assertNotIn('skin.',script)

    def test_cold_window_is_visible_focusable_without_refresh_and_back_cancels_late_results(self):
        db=self.index.connect(write=True)
        with db: db.execute("DELETE FROM titles WHERE kind='vod'");db.execute("DELETE FROM catalog WHERE kind='vod'")
        db.close()
        with mock.patch.object(self.index,'refresh',side_effect=AssertionError('full refresh on open')):
            start=time.monotonic();w=self.media_window()
            visible=time.monotonic()-start
            self.assertTrue(w.shown);self.assertEqual(w.getFocusId(),120)
            self.assertTrue(w._catalog_missing)
            w.native(7);w.native(92)
            self.settle(w);self.assertFalse(w.shown);self.assertTrue(w._closed)
        print('\nMODEL_COLD_WINDOW_MS {:.3f}'.format(visible*1000))
        sys.modules['utils'].http_get.assert_not_called()

    def test_progressive_import_is_visible_without_reopening_and_closed_view_untouched(self):
        w=self.media_window();self.assertEqual(w.total,100)
        self.index.import_group('p','vod','a',[dict(stream_id='new',category_id='a',name='Fresh')])
        w._poll_catalog();self.settle(w);self.assertEqual(w.total,1);self.assertEqual(w.rows[0]['sid'],'new')
        w.close();label=w.getControl(102).label
        w._poll_catalog();self.settle(w);self.assertEqual(w.getControl(102).label,label)

    def test_search_cold_index_queues_all_active_kinds_and_distinguishes_missing(self):
        db=self.index.connect(write=True)
        with db: db.execute('DELETE FROM titles');db.execute('DELETE FROM catalog')
        db.close()
        self.router._params.update(action='global_search',q='known')
        self.routes.dispatch(self.router)
        self.assertEqual(len(self.added),4)
        self.assertTrue(all('Index' in li.label or 'Katalog' in li.label for _,li,_ in self.added[:3]))
        db=self.index.connect()
        try: self.assertEqual({r['kind'] for r in db.execute('SELECT * FROM sync_requests')},{'live','vod','series'})
        finally: db.close()
        sys.modules['utils'].http_get.assert_not_called()

    def test_movies_directory_succeeds_before_owned_window(self):
        self.router._params['action']='movies_home'
        with mock.patch.object(self.media,'open_media') as open_media:
            def open_(*args,**kw):
                self.assertEqual(self.ends[-1][0],(7,))
                self.assertNotEqual(self.ends[-1][1].get('succeeded'),False)
            open_media.side_effect=open_
            self.routes.dispatch(self.router);open_media.assert_called_once()

    def test_manual_catalog_refresh_ends_directory_and_only_queues_groups(self):
        import ast
        from xcmate027_fixture import LIB
        tree=ast.parse((LIB/'main.py').read_text())
        method=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='_refresh_portal')
        namespace=dict(xbmcplugin=sys.modules['xbmcplugin'],xbmc=sys.modules['xbmc'],notify=mock.Mock())
        exec(compile(ast.Module(body=[method],type_ignores=[]),'manual-refresh','exec'),namespace)
        jobs=importlib.import_module('catalog_sync')
        self.router._load_channels=mock.Mock(side_effect=AssertionError('blocking catalogue load'))
        with mock.patch.object(jobs,'request') as request:
            namespace['_refresh_portal'](self.router)
            self.assertEqual([c.args[1] for c in request.call_args_list],['live','vod','series'])
            self.assertTrue(all(c.kwargs['force'] for c in request.call_args_list))
        self.router._load_channels.assert_not_called();self.assertEqual(self.ends[-1][0],(7,True))

    def test_optional_preload_failure_does_not_starve_catalogue_or_timers(self):
        service=importlib.import_module('app_services')
        jobs=importlib.import_module('catalog_sync');preload=importlib.import_module('startup_preload')
        timers=importlib.import_module('guide_timers')
        class Monitor:
            def abortRequested(self): return False
            def waitForAbort(self,seconds): return True
        sys.modules['xbmc'].Monitor=Monitor
        with mock.patch.object(service,'refresh_local'),mock.patch.object(preload,'prepare',side_effect=ValueError('bad guide')),mock.patch.object(jobs,'run_next',return_value=True) as run,mock.patch.object(timers,'poll') as remind:
            service._run();run.assert_called_once();remind.assert_called_once()


class PrePlayTests(unittest.TestCase):
    def setUp(self):
        import test_xcmate_kodi21_overlay as omega
        omega.OverlayLifecycleTests.setUp(self)
        self.addCleanup(self.overlay.close)
        self.patch=mock.patch.dict(sys.modules,live_overlay=self.module)
        self.patch.start();self.addCleanup(self.patch.stop)
        sys.modules['utils'].setting=lambda k,d='':d
        sys.modules.pop('preplay',None);sys.modules.pop('play_intent',None)
        self.preplay=importlib.import_module('preplay');self.intent=importlib.import_module('play_intent')
        self.addCleanup(lambda:self.preplay._window.close() if self.preplay._window else None)
        self.player.isPlayingVideo=lambda:False
        self.session=self.module.announce('p','1','Sender 1')
        self.props[self.intent.REQUEST]=json.dumps(self.session)

    def test_service_shows_controls_before_play_and_native_back_invalidates_nonce(self):
        self.preplay.poll()
        window=self.preplay._window
        self.assertTrue(window.shown);self.assertEqual(self.props[self.intent.ACK],self.session['nonce'])
        self.assertEqual(window.getFocusId(),window.capture.getId());self.player.play.assert_not_called()
        self.assertFalse(window.track.visible)  # no fake guide progress
        window.native(92)
        self.assertTrue(window.closed);self.assertEqual(self.props[self.intent.CANCEL],self.session['nonce'])
        self.assertNotIn(self.module.SESSION_KEY,self.props);self.player.stop.assert_called_once()

    def test_handshake_waits_for_real_service_ack_without_starting_player_thread(self):
        calls=[]
        parent=self
        class Monitor:
            def abortRequested(self): return False
            def waitForAbort(self,seconds): calls.append(seconds);parent.preplay.poll();return False
        sys.modules['xbmc'].Monitor=Monitor
        self.assertTrue(self.intent.before_play(self.session))
        self.assertTrue(calls);self.assertTrue(self.preplay._window.shown)
        self.player.play.assert_not_called()
        self.preplay._window.cancel()
        self.assertFalse(self.intent.before_play(self.session))

    def test_foreign_video_does_not_complete_handoff_and_wrong_portal_not_displayed(self):
        self.preplay.poll();window=self.preplay._window
        self.player.isPlayingVideo=lambda:True
        self.player.getPlayingFile=lambda:'plugin://other.addon/movie'
        self.preplay.poll();self.assertFalse(window.closed)
        self.props[self.module.SESSION_KEY]=json.dumps(dict(self.session,pid='wrong',nonce='other'))
        self.props[self.intent.REQUEST]=self.props[self.module.SESSION_KEY]
        sys.modules['portals'].get_by_id=lambda pid:None if pid=='wrong' else self.portal
        self.preplay.poll();self.assertTrue(window.closed)

    def test_verified_video_closes_preplay_before_navigator_and_keeps_session(self):
        self.preplay.poll();window=self.preplay._window
        self.player.isPlayingVideo=lambda:True
        self.preplay.poll()
        self.assertTrue(window.closed);self.assertNotIn(self.intent.REQUEST,self.props)
        self.assertEqual(self.props['XCMate.PrePlay.Ready'],self.session['nonce'])
        navigator=self.preplay.start_navigator('');self.addCleanup(navigator.close)
        navigator.show();self.assertEqual(navigator.mode,'info')
        navigator.handle_command('ok');self.assertEqual(navigator.mode,'controls')
        navigator.handle_command('down');self.assertEqual(navigator.mode,'extras')
        navigator.handle_command('back');self.assertEqual(navigator.mode,'controls')
        navigator.handle_command('back');self.assertEqual(navigator.mode,'info')
        navigator.handle_command('left');self.assertEqual(navigator.mode,'channels')
        navigator.handle_command('left');self.assertEqual(navigator.mode,'groups')

    def test_matching_url_without_player_readiness_does_not_handoff_or_expose_player_controls(self):
        self.preplay.poll();window=self.preplay._window
        self.player.isPlayingVideo=lambda:True
        self.player.getTime=mock.Mock(side_effect=RuntimeError('AV not ready'))
        self.preplay.poll();self.assertFalse(window.closed)
        self.assertIsNone(self.preplay.start_navigator(''))
        self.player.getTime.return_value=0;self.player.getTime.side_effect=None
        self.preplay.poll();self.assertTrue(window.closed)
        nav=self.preplay.start_navigator('');self.addCleanup(nav.close);nav.show()
        nav._connecting=True;nav._connecting_started=time.monotonic()
        self.player.getTime.side_effect=RuntimeError('AV pending')
        nav.tick();self.assertTrue(nav._connecting)
        nav.handle_command('play_pause');self.player.pause.assert_not_called()

    def test_old_cancel_callback_cannot_stop_new_session(self):
        self.preplay.poll();old=self.preplay._window
        fresh=self.module.announce('p','2','Sender 2')
        old.cancel();self.player.stop.assert_not_called()
        self.assertEqual(json.loads(self.props[self.module.SESSION_KEY])['nonce'],fresh['nonce'])

    def test_timeout_stops_pending_own_session_once(self):
        with mock.patch.object(self.preplay.time,'monotonic',return_value=100) as clock:
            self.preplay.poll();window=self.preplay._window
            clock.return_value=161;self.preplay.poll()
        self.assertTrue(window.closed);self.player.stop.assert_called_once()
        self.assertNotIn(self.module.SESSION_KEY,self.props)

    def test_warm_tune_reuses_controls_shows_info_before_player_and_back_cancels(self):
        self.player.isPlayingVideo=lambda:True
        nav=self.preplay.ConnectingNavigator(self.portal,'1');self.addCleanup(nav.close);nav.show()
        count=len(nav.controls)
        def play(*args):
            self.assertEqual(nav.mode,'info');self.assertIn(self.preplay.tr(32645),nav.info_hint.label)
            self.player.isPlayingVideo=lambda:False
        self.player.play.side_effect=play
        from contextlib import ExitStack
        with ExitStack() as stack:
            fake=types.SimpleNamespace(build_playable_item=lambda *a,**kw:types.SimpleNamespace(getPath=lambda:a[0]))
            stack.enter_context(mock.patch.dict(sys.modules,player=fake))
            nav._tune(nav.index.by_sid['2'])
        self.assertEqual(len(nav.controls),count);self.assertTrue(nav._connecting)
        nav.handle_command('back');self.assertTrue(nav._closed);self.player.stop.assert_called_once()
