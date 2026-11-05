"""Native search route/owner contract. Host evidence is not Android acceptance."""
import importlib,sys,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture,ADDON,QueuedPool


class SearchNavigation32(Fixture,unittest.TestCase):
    def test_positive_directory_global_search_also_opens_native_search(self):
        self.router._params.update(action='global_search',q='House')
        self.current_folder=self.router.url(**self.router._params)
        with mock.patch.object(self.media,'open_search',return_value=types.SimpleNamespace(_search_live=None)) as opened:
            self.routes.dispatch(self.router)
        opened.assert_called_once()
        self.assertFalse(any('action=global_search' in c for c in self.builtins))

    def test_legacy_guide_search_only_queues_until_its_owner_tick(self):
        w=self.guide_window();w._running=True
        self.dialog.input.return_value='House'
        w.onAction(types.SimpleNamespace(getId=lambda:117))
        self.assertFalse(w._closed)
        self.assertTrue(w._leaving)
        self.assertFalse(self.builtins)
        self.assertEqual(w._search_request['query'],'House')
        w._leave_after=0;w._owner_tick();self.assertTrue(w._closed)

    def test_grid_search_closes_on_pump_without_directory_handoff(self):
        sys.modules.pop('guide_grid_window',None);grid=importlib.import_module('guide_grid_window')
        with mock.patch.object(grid,'ThreadPoolExecutor',QueuedPool):
            w=grid.GuideGridWindow('XCMateGuideGrid.xml',str(ADDON),'Default','720p');w.configure(self.router,self.portal)
        self.addCleanup(w.close);w.show();self.settle(w);w._running=True
        self.dialog.input.return_value='House';w.onClick(314)
        self.assertFalse(w._closed);self.assertTrue(w._leaving);self.assertFalse(self.builtins)
        w._leave_after=0;w._owner_tick();self.assertTrue(w._closed)
        self.assertEqual(w._search_request['query'],'House')

    def test_native_search_initialization_has_no_landing_query_or_focus(self):
        def run(w):
            w.show();self.assertEqual(w.mode,'search')
            self.assertFalse(w._pool.jobs)
            w._owner_tick();self.settle(w)
            self.assertEqual(w.mode,'search');self.assertIn(w.getFocusId(),(700,701,702))
            w.close()
        with mock.patch.object(self.media.MediaView,'run',run):
            self.media.open_search(self.router,self.portal,'House')


    def test_directory_completion_precedes_window_without_a_second_home_update(self):
        self.router._params.update(action='global_search',q='House');events=[]
        xbmc=sys.modules['xbmc'];plugin=sys.modules['xbmcplugin'];old_end=plugin.endOfDirectory
        def done(*a,**kw):events.append('directory');old_end(*a,**kw)
        def tick(seconds):
            self.assertEqual(events,['directory'])
            self.current_folder=self.router.url(**self.router._params);return False
        def opened(*a):events.append('search');return types.SimpleNamespace(_search_live=None)
        with mock.patch.object(plugin,'endOfDirectory',side_effect=done),mock.patch.object(xbmc,'Monitor',return_value=types.SimpleNamespace(waitForAbort=tick)),mock.patch.object(self.media,'open_search',side_effect=opened):
            self.routes.dispatch(self.router)
        self.assertEqual(events,['directory','search']);self.assertEqual(len(self.ends),1);self.assertFalse(self.builtins)
        self.assertEqual(len(self.added),7);self.assertTrue(self.added[0][1].art['icon'])
        self.assertTrue(all(item.art['fanart'] for _,item,folder in self.added if not folder))

    def test_directory_timeout_and_busy_owner_never_open_or_recurse(self):
        nav=importlib.import_module('window_navigation');search_nav=importlib.import_module('search_navigation')
        self.router._params.update(action='global_search',q='House')
        with mock.patch.object(search_nav,'mark'),mock.patch.object(search_nav,'time',types.SimpleNamespace(monotonic=mock.Mock(side_effect=[0,6]))),mock.patch.object(self.media,'open_search') as opened:
            self.routes.dispatch(self.router)
        opened.assert_not_called();self.assertFalse(self.builtins)
        self.router._directory_done=False
        with nav.ownership() as acquired,mock.patch.object(self.media,'open_search') as opened:
            self.assertTrue(acquired);self.routes.dispatch(self.router)
        opened.assert_not_called();self.assertFalse(self.builtins)

    def test_action_handle_home_and_foreign_context_have_one_explicit_owner(self):
        for folder,count in ((self.current_folder,0),('plugin://foreign.addon/?action=movies',1)):
            self.builtins.clear();self.current_folder=folder;self.router._handle=-1
            self.router._params.update(action='global_search',q='House')
            with mock.patch.object(self.media,'open_search',return_value=types.SimpleNamespace(_search_live=None)) as opened:
                self.routes.dispatch(self.router)
            opened.assert_called_once();self.assertEqual(len(self.builtins),count)
            self.assertFalse(any('action=global_search' in c for c in self.builtins));self.assertFalse(self.ends)

    def test_existing_search_section_widget_remains_directory_only(self):
        self.router._params.update(action='search_section',q='House',kind='live')
        with mock.patch.object(self.media,'open_search') as opened:self.routes.dispatch(self.router)
        opened.assert_not_called();self.assertEqual(len(self.ends),1);self.assertTrue(self.added)

    def test_guide_keyboard_cancel_and_fast_repeated_input_keep_one_intent(self):
        w=self.guide_window();self.dialog.input.return_value='';generation=w._generation
        w.onAction(types.SimpleNamespace(getId=lambda:117))
        self.assertFalse(w._closed);self.assertFalse(w._leaving);self.assertIsNone(w._search_request)
        self.assertEqual(w._generation,generation)
        self.dialog.input.return_value='House';w.onAction(types.SimpleNamespace(getId=lambda:117));request=w._search_request
        w.onAction(types.SimpleNamespace(getId=lambda:117));w.onAction(types.SimpleNamespace(getId=lambda:92))
        self.assertIs(w._search_request,request);self.assertEqual(self.dialog.input.call_count,2);self.assertFalse(w._closed)

    def test_real_guide_search_back_owner_sequence_restores_selected_view(self):
        self.router._handle=-1;windows=[];events=[];callback=[False];nav=importlib.import_module('window_navigation')
        original_guide=self.guide.GuideWindow.configure;original_media=self.media.MediaView.configure
        def configure_guide(w,*args,**kw):original_guide(w,*args,**kw);windows.append(w);events.append('guide')
        def configure_search(w,*args,**kw):original_media(w,*args,**kw);windows.append(w);events.append('search')
        done=set()
        def tick(seconds):
            if not windows:return False
            w=windows[-1]
            if w._closed:return False
            w._pool.drain()
            if w._pending_future is not None:return False
            if id(w) in done:return False
            done.add(id(w));callback[0]=True
            if events==['guide']:
                w.day=2;w.getControl(210).selectItem(1);w.setFocusId(210)
                w.onAction(types.SimpleNamespace(getId=lambda:117));self.assertFalse(w._closed);w._leave_after=0
            elif events==['guide','search']:
                self.assertEqual(w.mode,'search');self.assertEqual(w._search_kind,'live');self.assertTrue(w._search_rows)
                w.native(92);self.assertFalse(w._closed);w._leave_after=0
            else:
                self.assertEqual(w.day,2);self.assertEqual(w.getControl(210).getSelectedPosition(),1);self.assertEqual(w.getFocusId(),210)
                w.close()
            callback[0]=False
            if len(events)>3:self.fail('unexpected extra window')
            return False
        self.dialog.input.return_value='House'
        with mock.patch.object(self.guide.GuideWindow,'configure',configure_guide),mock.patch.object(self.media.MediaView,'configure',configure_search),mock.patch.object(sys.modules['xbmc'],'Monitor',return_value=types.SimpleNamespace(waitForAbort=tick)):
            nav.open_route(self.router,self.portal,lambda:self.guide.open_guide(self.router,self.portal))
        self.assertEqual(events,['guide','search','guide']);self.assertFalse(self.builtins)
        self.assertTrue(all(w._closed and not w._running for w in windows))

    def test_grid_search_back_preserves_time_group_row_and_focus(self):
        sys.modules.pop('guide_grid_window',None);grid=importlib.import_module('guide_grid_window')
        with mock.patch.object(grid,'ThreadPoolExecutor',QueuedPool):
            w=grid.GuideGridWindow('XCMateGuideGrid.xml',str(ADDON),'Default','720p');w.configure(self.router,self.portal)
        self.addCleanup(w.close);w.show();self.settle(w)
        w.cursor+=3600;w.origin+=1800;w.row=1;w._focus_zone='header';w._header=315;w.setFocusId(315)
        self.dialog.input.return_value='House';w.onClick(314);view=w._search_request['view'];w.close()
        with mock.patch.object(grid,'ThreadPoolExecutor',QueuedPool):
            restored=grid.GuideGridWindow('XCMateGuideGrid.xml',str(ADDON),'Default','720p');restored.configure(self.router,self.portal,return_view=view)
        self.addCleanup(restored.close);restored.show();self.settle(restored)
        for name in ('category','cursor','origin','row','offset','_focus_zone','_header'):self.assertEqual(getattr(restored,name),view[name])
        self.assertEqual(restored.getFocusId(),315);self.assertFalse(self.builtins)

    def test_search_live_intent_is_dispatched_only_after_navigation_lease_ends(self):
        module=importlib.import_module('search_navigation');nav=importlib.import_module('window_navigation');events=[]
        self.router._handle=-1
        window=types.SimpleNamespace(_closed=True,_running=False,_search_request=dict(query='House',session='a'*32,view={}))
        intent={'test':'intent'};search=types.SimpleNamespace(_closed=True,_running=False,_search_live=intent)
        def opened(*a):
            with nav.ownership() as acquired:self.assertFalse(acquired)
            events.append('search');return search
        def after(r,p,value):
            with nav.ownership() as acquired:self.assertTrue(acquired)
            self.assertIs(value,intent);events.append('after')
        with mock.patch.object(self.media,'open_search',side_effect=opened):
            nav.open_route(self.router,self.portal,lambda:module.guide_flow(self.router,self.portal,lambda *a:window,None,'unused','grid'),after_close=after)
        self.assertEqual(events,['search','after']);self.assertFalse(self.builtins)

    def test_stale_callback_after_new_query_tab_change_and_close_is_ignored(self):
        w=self.media_window();self.dialog.input.return_value='House';w._search();apply=w._pending_apply
        w._pool.drain();value=w._pending_future.result()
        self.dialog.input.return_value='missing';w._search();self.settle(w);fresh=w._search_data
        apply(value);self.assertIs(w._search_data,fresh)
        w.onClick(700);self.settle(w);apply(value);self.assertIsNot(w._search_data,value)
        w.close();apply(value);self.assertIsNone(getattr(w,'_search_live',None));self.assertFalse(self.builtins)

    def test_twenty_ir_cycles_retain_native_search_and_require_explicit_selection(self):
        w=self.media_window()
        for _ in range(20):
            self.dialog.input.return_value='House';w._search();self.settle(w)
            for key in (1,2,4,3):w.native(key)
            self.assertEqual(w.mode,'search');self.assertIn(w.getFocusId(),w._valid_focus())
            self.assertIsNone(getattr(w,'_search_live',None));w.native(92);self.settle(w)
            self.assertEqual(w.mode,'landing')
        self.assertFalse(w._closed);self.assertFalse(self.builtins)

    def test_media_detail_search_back_restores_detail_and_valid_focus(self):
        w=self.media_window();w.native(7);self.settle(w);sid=w.selected['sid']
        self.dialog.input.return_value='House';w._search();self.settle(w);w.native(92);self.settle(w)
        self.assertEqual(w.mode,'detail');self.assertEqual(w.selected['sid'],sid);self.assertIn(w.getFocusId(),w._valid_focus());self.assertFalse(self.builtins)

    def test_search_focus_lag_is_bounded_and_never_focuses_hidden_120(self):
        w=self.media_window();self.dialog.input.return_value='House';w._search();self.settle(w)
        with mock.patch.object(w,'_valid_focus',side_effect=lambda native=True:[] if native else [700,701,702,400]):
            w.setFocusId(700);self.assertEqual(w._focus_pending,('search',700))
            w._focus_deadline=0;w._resume_focus();self.assertIsNone(w._focus_pending)
        self.assertNotEqual(w.getFocusId(),120);w.setFocusId(700);self.assertIn(w.getFocusId(),w._valid_focus())

    def test_trace_contains_only_allowlisted_metadata_and_no_query_or_accounts(self):
        module=importlib.import_module('search_navigation');logger=mock.Mock()
        with mock.patch.object(sys.modules['xbmc'],'log',logger,create=True),mock.patch.object(sys.modules['xbmc'],'LOGINFO',1,create=True):
            module.mark('SEARCH_OPEN',self.router,'PRIVATE_SOURCE','PRIVATE_QUERY_12345678901234567890',700,True)
        text=logger.call_args[0][0]
        for private in ('PRIVATE','SECRET','provider.invalid','House','pid=','q='):self.assertNotIn(private,text)
        self.assertIn('handle=directory',text);self.assertIn('focus=700',text);self.assertIn('owner=1',text)

    def test_native_close_must_finish_before_another_window_can_open(self):
        module=importlib.import_module('search_navigation');xbmc=sys.modules['xbmc'];gui=sys.modules['xbmcgui']
        current=[13001];ticks=[]
        def tick(seconds):
            ticks.append(seconds)
            if len(ticks)==3:current[0]=10025
            return False
        with mock.patch.object(gui,'getCurrentWindowId',side_effect=lambda:current[0],create=True),mock.patch.object(xbmc,'Monitor',return_value=types.SimpleNamespace(waitForAbort=tick)):
            self.assertTrue(module.released(self.router,'grid','a'*32,13001))
        self.assertEqual(len(ticks),3);self.assertFalse(self.builtins)

    def test_release_timeout_keeps_closed_guide_from_opening_search(self):
        module=importlib.import_module('search_navigation');gui=sys.modules['xbmcgui']
        window=types.SimpleNamespace(_closed=True,_running=False,_search_request=dict(query='House',session='a'*32,view={},window=13001))
        with mock.patch.object(module,'mark'),mock.patch.object(module,'time',types.SimpleNamespace(monotonic=mock.Mock(side_effect=[0,3]))),mock.patch.object(gui,'getCurrentWindowId',return_value=13001,create=True),mock.patch.object(self.media,'open_search') as opened:
            self.assertIsNone(module.guide_flow(self.router,self.portal,lambda *a:window,None,'unused','grid'))
        opened.assert_not_called();self.assertFalse(self.builtins)

    def test_grid_header_312_focus_waits_for_native_visibility_and_can_expire(self):
        sys.modules.pop('guide_grid_window',None);grid=importlib.import_module('guide_grid_window')
        with mock.patch.object(grid,'ThreadPoolExecutor',QueuedPool):
            w=grid.GuideGridWindow('XCMateGuideGrid.xml',str(ADDON),'Default','720p');w.configure(self.router,self.portal)
        self.addCleanup(w.close);w.show();self.settle(w);before=w.getFocusId()
        w.getControl(312).setVisible(False);w.setFocusId(312)
        self.assertEqual(w.getFocusId(),before);self.assertEqual(w._focus_pending,312)
        w.getControl(312).setVisible(True);w._resume_focus();self.assertEqual(w.getFocusId(),312);self.assertIsNone(w._focus_pending)
        w.getControl(312).setVisible(False);w.setFocusId(312);w._focus_deadline=0;w._resume_focus();self.assertIsNone(w._focus_pending)

    def test_search_initial_keyboard_cancel_has_no_landing_or_result_job(self):
        self.dialog.input.return_value=''
        def run(w):
            w.show();w._owner_tick();self.assertTrue(w._closed);self.assertFalse(w._pool.jobs)
        with mock.patch.object(self.media.MediaView,'run',run):self.media.open_search(self.router,self.portal)
        self.assertFalse(self.builtins)


if __name__=='__main__':unittest.main()
