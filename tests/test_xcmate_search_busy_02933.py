"""Kodi .32 busy regressions; host models are not an Android PASS."""
import importlib,sys,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture,ADDON


class SearchBusy33(Fixture,unittest.TestCase):
    def busy(self,dialog=10138):
        self.gui=sys.modules['xbmcgui'];self.xbmc=sys.modules['xbmc'];self.dialog_id=dialog
        self.addCleanup(mock.patch.stopall)
        mock.patch.object(self.gui,'getCurrentWindowId',return_value=10025,create=True).start()
        mock.patch.object(self.gui,'getCurrentWindowDialogId',side_effect=lambda:self.dialog_id,create=True).start()
        original=self.xbmc.getCondVisibility
        mock.patch.object(self.xbmc,'getCondVisibility',side_effect=lambda c:bool(self.dialog_id) if c=='System.HasActiveModalDialog' else original(c)).start()

    def test_three_reported_busy_timeouts_yield_an_owned_search_continuation(self):
        nav=importlib.import_module('search_navigation');self.busy()
        for _ in range(3):
            request=dict(query='House',session='a'*32,view={},window=13004)
            guide=types.SimpleNamespace(_closed=True,_running=False,_search_request=request)
            with mock.patch.object(nav,'released',return_value=False),mock.patch.object(self.media,'open_search') as opened:
                result=nav.guide_flow(self.router,self.portal,lambda *a:guide,None,'unused','grid')
            self.assertIsNotNone(result);self.assertTrue(getattr(result,'deferred',False));opened.assert_not_called()

    def test_native_media_default_is_visible_in_search_after_keyboard(self):
        w=self.media_window();self.dialog.input.return_value='House';w._search();self.settle(w)
        default=int(w.tree.findtext('defaultcontrol'))
        self.assertIn(default,w._valid_focus());self.assertTrue(w.getControl(default).isVisible())

    def test_focus_lag_cannot_retain_xml_edge_to_hidden_landing_button(self):
        w=self.media_window();self.dialog.input.return_value='House'
        original=w._valid_focus
        with mock.patch.object(w,'_valid_focus',side_effect=lambda native=True:[] if native else original(False)):
            w._search()
            self.assertEqual(w._focus_pending,('search',701))
            self.assertNotEqual(w.getControl(400).node.findtext('onleft'),'120')


    def transfer(self,source='route',query='House'):
        broker=importlib.import_module('search_handoff')
        return broker,broker.SearchTransfer(self.router,self.portal,dict(query=query,session='a'*32,view={},window=None),source)

    def token(self,broker):return self.properties[broker.LATEST]

    def test_busy_is_not_ignored_and_continuation_runs_only_after_original_return(self):
        self.busy();nav=importlib.import_module('window_navigation');self.router._handle=-1
        self.router._params.update(action='global_search',q='House');self.router._navigation_dispatch='a'*32
        with mock.patch.object(self.media,'open_search') as opened:self.routes.dispatch(self.router)
        opened.assert_not_called();self.assertEqual(len(self.builtins),1);self.assertTrue(self.builtins[0].startswith('RunScript('))
        broker=importlib.import_module('search_handoff');token=self.token(broker)
        # Kodi ExecuteAsync has queued the script; return of the first plugin
        # clears its native Busy. Only now does the new script own a window.
        self.dialog_id=0;calls=[]
        def execute(w):
            w.show();w._owner_tick();self.settle(w)
            self.assertEqual(w.mode,'search');self.assertTrue(w._search_rows);self.assertIn(w.getFocusId(),w._valid_focus());calls.append('ready')
            w.close()
        with mock.patch.object(self.media.MediaWindow,'run',execute):self.assertIsNone(broker.run(token))
        self.assertEqual(calls,['ready']);self.assertNotIn(broker.PREFIX+token,self.properties)
        self.assertFalse(broker.run(token));self.assertEqual(len(self.builtins),1)
        with nav.ownership() as acquired:self.assertTrue(acquired)

    def test_guide_busy_defers_after_unlock_then_restores_from_same_snapshot(self):
        self.busy();broker,transfer=self.transfer('grid');view=dict(category='a',row=3,offset=16,origin=123,cursor=456)
        transfer.payload['request']['view']=view;seen=[];nav=importlib.import_module('window_navigation');self.router._handle=-1
        nav.open_route(self.router,self.portal,lambda:transfer,after_close=broker.handoff)
        token=self.token(broker);self.dialog_id=0
        def continuation(*args,**kwargs):
            with nav.ownership() as owned:self.assertFalse(owned)
            self.assertEqual(kwargs['initial']['view'],view);seen.append('guide-flow');return None
        with mock.patch('search_navigation.guide_flow',side_effect=continuation):self.assertTrue(broker.run(token))
        self.assertEqual(seen,['guide-flow']);self.assertEqual(len(self.builtins),1)

    def test_real_foreign_dialog_never_gets_forced_closed_or_bypassed(self):
        self.busy(10103);broker,transfer=self.transfer();broker.schedule(transfer);token=self.token(broker)
        with mock.patch('search_navigation.released',return_value=False),mock.patch.object(self.media,'open_search') as opened:
            self.assertFalse(broker.run(token))
        opened.assert_not_called();self.assertEqual(self.dialog_id,10103)
        self.assertFalse(any('Dialog.Close' in cmd or 'ActivateWindow' in cmd for cmd in self.builtins))

    def test_late_foreign_window_owner_rejects_transfer_and_clears_memory_token(self):
        broker,transfer=self.transfer();broker.schedule(transfer);token=self.token(broker)
        nav=importlib.import_module('window_navigation')
        with nav.ownership() as owned,mock.patch.object(self.media,'open_search') as opened:
            self.assertTrue(owned);self.assertFalse(broker.run(token))
        opened.assert_not_called();self.assertNotIn(broker.PREFIX+token,self.properties)

    def test_ttl_latest_wins_and_replay_do_not_reopen_a_search(self):
        broker,first=self.transfer();broker.schedule(first);old=self.token(broker)
        broker.schedule(first);latest=self.token(broker);self.assertNotEqual(old,latest);self.assertIsNone(broker._consume(old))
        import json
        value=json.loads(self.properties[broker.PREFIX+latest]);value['created']-=30
        self.properties[broker.PREFIX+latest]=json.dumps(value)
        self.assertFalse(broker.run(latest));self.assertFalse(broker.run(latest));self.assertNotIn(broker.LATEST,self.properties)

    def test_context_portal_player_or_session_change_cancels_delayed_search(self):
        for change in ('folder','portal','player','session'):
            with self.subTest(change=change):
                broker,transfer=self.transfer();broker.schedule(transfer);token=self.token(broker)
                folder=self.current_folder
                if change=='folder':self.current_folder='plugin://other.addon/'
                if change=='portal':self.portal['enabled']=False
                if change=='session':self.properties['XtreamMate.LiveSession']='new-session'
                with mock.patch('search_navigation.released',return_value=True),mock.patch.object(self.media,'open_search') as opened:
                    if change=='player':
                        with mock.patch('guide_playback.player_state',return_value=(True,'foreign-playback')):self.assertFalse(broker.run(token))
                    else:self.assertFalse(broker.run(token))
                opened.assert_not_called();self.current_folder=folder;self.portal['enabled']=True;self.properties.pop('XtreamMate.LiveSession',None)

    def test_positive_directory_handle_yields_then_uses_completed_container(self):
        self.busy();self.router._params.update(action='global_search',q='House')
        with mock.patch.object(self.media,'open_search') as opened:self.routes.dispatch(self.router)
        opened.assert_not_called();self.assertEqual(len(self.ends),1)
        broker=importlib.import_module('search_handoff');token=self.token(broker);self.dialog_id=0
        self.current_folder=self.router.url(**self.router._params)
        with mock.patch.object(self.media,'open_search',return_value=types.SimpleNamespace(_closed=True,_search_live=None)) as opened:
            broker.run(token)
        opened.assert_called_once();self.assertFalse(any('Container.Update' in c for c in self.builtins))

    def test_run_script_parameters_and_traces_never_contain_search_or_credentials(self):
        broker,transfer=self.transfer(query='PRIVATE House SECRET');broker.schedule(transfer)
        self.assertNotIn('PRIVATE',self.builtins[-1]);self.assertNotIn('SECRET',self.builtins[-1])
        self.assertNotIn('pid=',self.builtins[-1]);self.assertNotIn('q=',self.builtins[-1])
        token=self.token(broker);self.assertTrue(broker.valid_token(token));self.assertIsNone(broker._consume('bad-token'))
        self.assertIn(broker.PREFIX+token,self.properties)

    def test_foreign_dialog_keeps_owner_start_guard_and_slow_busy_release_is_bounded(self):
        self.busy();nav=importlib.import_module('search_navigation');self.router._search_async_owner=True;ticks=[]
        def tick(seconds):
            ticks.append(seconds)
            if len(ticks)==4:self.dialog_id=0
            return False
        with mock.patch.object(self.xbmc,'Monitor',return_value=types.SimpleNamespace(waitForAbort=tick)):
            self.assertTrue(nav.released(self.router,'grid','a'*32,13004))
        self.assertEqual(len(ticks),4);self.assertFalse(self.builtins)

    def test_keyboard_native_reinit_retains_search_target_and_xml_default_is_safe(self):
        w=self.media_window();self.dialog.input.return_value='House';w._search();self.settle(w)
        w.setFocusId(710);w._search_root=True
        # Native init chooses the always-visible XML default before Python.
        from xcmate027_fixture import WindowXML
        WindowXML.setFocusId(w,int(w.tree.findtext('defaultcontrol')));w.onInit()
        self.assertEqual(w.mode,'search');self.assertEqual(w.getFocusId(),710)
        self.assertFalse(w._leaving);self.assertFalse(self.builtins)

    def test_partial_counts_do_not_reset_an_unchanged_focused_result_container(self):
        w=self.media_window();self.dialog.input.return_value='House';w._search();self.settle(w);w.setFocusId(710)
        with mock.patch.object(w,'_fill',wraps=w._fill) as fill:w._search_ready(w._search_data)
        fill.assert_not_called();self.assertEqual(w.getFocusId(),710)

    def test_grid_safe_native_default_stays_visible_in_group_mode(self):
        from xcmate027_fixture import QueuedPool
        sys.modules.pop('guide_grid_window',None);grid=importlib.import_module('guide_grid_window')
        with mock.patch.object(grid,'ThreadPoolExecutor',QueuedPool):
            w=grid.GuideGridWindow('XCMateGuideGrid.xml',str(ADDON),'Default','720p');w.configure(self.router,self.portal)
        self.addCleanup(w.close);w.show();self.settle(w);w._show_groups(refresh=False)
        default=int(w.tree.findtext('defaultcontrol'));self.assertEqual(default,314)
        self.assertTrue(w.getControl(default).isVisible());self.assertFalse(w.getControl(312).isVisible())
        self.dialog.input.return_value='';w.onClick(314);self.assertEqual(w.mode,'groups');self.assertFalse(w._leaving)


    def test_busy_continuation_uses_real_search_then_restores_real_guide_view(self):
        self.busy();nav=importlib.import_module('window_navigation');navigation=importlib.import_module('search_navigation')
        broker=importlib.import_module('search_handoff');self.router._handle=-1
        # Native IDs depend on whether the previous XML window is still shown.
        def native_id():
            active=getattr(self.xbmc,'_focus_window',None)
            return 13004 if active is not None and active.shown else 10025
        mock.patch.object(self.gui,'getCurrentWindowId',side_effect=native_id).start()
        w=self.guide_window();w.day=2;w.getControl(210).selectItem(1);w.setFocusId(210)
        self.dialog.input.return_value='House';navigation.queue(w,'guide');w._leave_after=0;w._owner_tick()
        nav.open_route(self.router,self.portal,lambda:navigation.guide_flow(self.router,self.portal,lambda *a:w,None,'unused','guide'),after_close=broker.handoff)
        token=self.token(broker);self.assertTrue(w._closed);self.dialog_id=0;events=[]
        def search(window):
            window.show();window._owner_tick();self.settle(window)
            self.assertEqual(window.mode,'search');self.assertTrue(window._search_rows)
            events.append('search');window.close()
        def guide(window):
            window.show();self.settle(window)
            self.assertEqual(window.day,2);self.assertEqual(window.getControl(210).getSelectedPosition(),1)
            self.assertEqual(window.getFocusId(),210);events.append('guide');window.close()
        with mock.patch.object(self.media.MediaWindow,'run',search),mock.patch.object(self.guide.GuideWindow,'run',guide):
            self.assertTrue(broker.run(token))
        self.assertEqual(events,['search','guide']);self.assertEqual(len(self.builtins),1)

    def test_real_foreign_modal_does_not_create_any_search_continuation(self):
        self.busy(10103);module=importlib.import_module('search_navigation')
        window=types.SimpleNamespace(_closed=True,_running=False,_search_request=dict(query='House',session='a'*32,view={},window=13004))
        with mock.patch.object(module,'released',return_value=False):
            self.assertIsNone(module.guide_flow(self.router,self.portal,lambda *a:window,None,'unused','guide'))
        self.assertFalse(self.builtins)


if __name__=='__main__':unittest.main()
