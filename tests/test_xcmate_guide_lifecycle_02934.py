"""Kodi 21.2 Window.close parent activation versus XMLDialog close model."""
import importlib,sys,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture,WindowXML,WindowXMLDialog,QueuedPool,ADDON


class Counter:
    def __init__(self):self.value=0
    def __call__(self):self.value+=1;return self.value


class GuideLifecycle34(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();sys.modules.pop('guide_grid_window',None);sys.modules.pop('guide_playback',None)
        self.grid=importlib.import_module('guide_grid_window');self.play=importlib.import_module('guide_playback')
        patch=mock.patch.object(self.grid,'ThreadPoolExecutor',QueuedPool);patch.start();self.addCleanup(patch.stop)
        self.root_dispatches=[];self.busy=False;self.foreign=0
        self.xbmc=sys.modules['xbmc'];self.gui=sys.modules['xbmcgui']
        def current_window():
            view=getattr(self.xbmc,'_focus_window',None)
            return 13006 if view and view.shown and not isinstance(view,WindowXMLDialog) else 10025
        def current_dialog():
            view=getattr(self.xbmc,'_focus_window',None)
            return self.foreign or (13006 if view and view.shown and isinstance(view,WindowXMLDialog) else 10138 if self.busy else 9999)
        original=self.xbmc.getCondVisibility
        def cond(value):
            if value=='System.HasActiveModalDialog':return current_dialog()!=9999
            if value=='Container.IsUpdating':return self.busy
            return original(value)
        def close_window(view):
            view.shown=False;self.root_dispatches.append('root');self.busy=True
        for patch in (mock.patch.object(self.gui,'getCurrentWindowId',side_effect=current_window,create=True),mock.patch.object(self.gui,'getCurrentWindowDialogId',side_effect=current_dialog,create=True),mock.patch.object(self.xbmc,'getCondVisibility',side_effect=cond),mock.patch.object(WindowXML,'close',close_window)):
            patch.start();self.addCleanup(patch.stop)
        self.router._handle=-1

    def window(self):
        w=self.grid.GuideGridWindow('XCMateGuideGrid.xml',str(ADDON),'Default','720p');w.configure(self.router,self.portal)
        self.addCleanup(w.close);w.show();self.settle(w);return w

    def test_four_reported_guide_starts_dispatch_once_without_root_reentry(self):
        outcomes=[]
        for _ in range(4):
            self.busy=False;w=self.window();self.dialog.select.return_value=1;w.native(7)
            self.assertFalse(w._closed);w._leave_after=0;w._owner_tick()
            with mock.patch.object(self.play,'time',types.SimpleNamespace(monotonic=Counter())):
                outcomes.append(self.play.handoff(self.router,self.portal,w._play_request))
        self.assertEqual(outcomes,[True]*4);self.assertEqual(self.root_dispatches,[])
        self.assertEqual(sum(c.startswith('PlayMedia(') for c in self.builtins),4)

    def test_both_guide_types_use_native_xml_dialog_without_parent_reactivation(self):
        self.assertTrue(issubclass(self.grid.GuideGridWindow,WindowXMLDialog))
        self.assertTrue(issubclass(self.guide.GuideWindow,WindowXMLDialog))

    def test_search_standalone_is_dialog_but_existing_media_is_window(self):
        seen=[]
        core=getattr(self.media,'MediaView',self.media.MediaWindow)
        def run(w):
            w.show();w._owner_tick();self.settle(w);seen.append(isinstance(w,WindowXMLDialog));w.close()
        with mock.patch.object(core,'run',run):self.media.open_search(self.router,self.portal,'House')
        self.assertEqual(seen,[True]);self.assertFalse(issubclass(self.media.MediaWindow,WindowXMLDialog))
        self.assertEqual(self.root_dispatches,[])


    def test_two_complete_search_excursions_restore_the_exact_grid_snapshot(self):
        for name in ('search_navigation','search_handoff'):sys.modules.pop(name,None)
        navigation=importlib.import_module('search_navigation')
        for _ in range(2):
            w=self.window();w.cursor+=3600;w.origin+=10800;w.row=1
            w.category='a';w._focus_zone='grid'
            self.dialog.input.return_value='House';navigation.queue(w,'grid')
            expected=dict(w._search_request['view']);w._leave_after=0;w._owner_tick()
            self.assertTrue(w._closed)
            opened=[]
            def open_view(cls,xml,router,portal,**kw):
                if not opened:opened.append('initial');return w
                restored=cls(xml,str(ADDON),'Default','720p');restored.configure(router,portal,**kw)
                restored.show();self.settle(restored)
                for key in ('category','origin','cursor','row','_focus_zone'):
                    self.assertEqual(getattr(restored,key),expected[key],key)
                opened.append('restored');restored.close();return restored
            def search(view):
                view.show();view._owner_tick();self.settle(view)
                self.assertEqual(view.mode,'search');self.assertTrue(view._search_rows)
                self.assertIn(view.getFocusId(),view._valid_focus());view.close()
            with mock.patch.object(self.media.MediaView,'run',search):
                self.assertIsNone(navigation.guide_flow(self.router,self.portal,open_view,self.grid.GuideGridWindow,'XCMateGuideGrid.xml','grid'))
            self.assertEqual(opened,['initial','restored'])
        self.assertEqual(self.root_dispatches,[]);self.assertFalse(self.builtins)

    def test_normal_window_close_reproduces_parallel_root_busy_but_dialog_close_does_not(self):
        # Counterfactual .33 native mechanism; no assumption about root suppression.
        old=WindowXML('XCMateGuideGrid.xml',str(ADDON),'Default','720p');old.close()
        self.assertEqual(self.root_dispatches,['root']);self.assertTrue(self.busy)
        self.root_dispatches.clear();self.busy=False
        w=self.window();w.close()
        self.assertEqual(self.root_dispatches,[]);self.assertFalse(self.busy)

class GuidePlaybackReasons34(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('guide_playback','window_lifecycle','search_navigation','search_handoff'):
            sys.modules.pop(name,None)
        self.play=importlib.import_module('guide_playback');self.life=importlib.import_module('window_lifecycle')
        self.xbmc=sys.modules['xbmc'];self.gui=sys.modules['xbmcgui'];self.logs=[]
        self.xbmc.log=lambda message,*args:self.logs.append(message);self.xbmc.LOGINFO=1
        self.addCleanup(mock.patch.stopall)
        mock.patch.object(self.play,'time',types.SimpleNamespace(monotonic=Counter())).start()

    def intent(self):return self.play.request(self.portal,dict(sid='1'),(False,''))

    def rejected(self,intent,reason,portal=None):
        self.assertFalse(self.play.handoff(self.router,portal or self.portal,intent))
        self.assertIn('stage=SKIPPED reason='+reason,self.logs[-1])
        self.assertFalse(self.builtins)

    def test_four_distinct_native_skip_conditions_are_identified(self):
        for snapshot,reason in (
            (dict(window=10025,dialog=13001,modal=True,updating=False),'WINDOW_STILL_ACTIVE'),
            (dict(window=10025,dialog=10138,modal=True,updating=True),'BUSY_TIMEOUT'),
            (dict(window=10025,dialog=10103,modal=True,updating=False),'FOREIGN_MODAL'),
            (dict(window=10025,dialog=9999,modal=False,updating=True),'CONTAINER_UPDATING')):
            with self.subTest(reason=reason),mock.patch.object(self.life,'state',return_value=snapshot):
                intent=self.intent();intent.update(window=13001,surface='dialog',owner='a'*32)
                self.rejected(intent,reason)
        self.assertFalse(any('Dialog.Close' in c for c in self.builtins))

    def test_unknown_dialog_identity_never_becomes_released_by_assumption(self):
        intent=self.intent();intent.update(surface='dialog',window=None)
        self.rejected(intent,'OWNER_UNAVAILABLE')
        self.assertTrue(self.life.active(dict(surface='dialog',window=None)))

    def test_abort_is_separate_from_busy_and_foreign_modal(self):
        with mock.patch.object(self.xbmc,'Monitor',return_value=types.SimpleNamespace(abortRequested=lambda:True)):
            self.rejected(self.intent(),'OWNER_ABORT')

    def test_player_unavailable_changed_and_new_session_are_distinct(self):
        intent=self.intent()
        with mock.patch.object(self.play,'player_state',return_value=None):self.rejected(intent,'PLAYER_UNAVAILABLE')
        intent=self.intent();intent['player']=(True,'private-playing-file')
        self.rejected(intent,'PLAYER_STATE_CHANGED')
        intent=self.intent();self.properties['XtreamMate.LiveSession']='changed'
        self.rejected(intent,'LIVE_SESSION_CHANGED')

    def test_unchanged_foreign_player_is_preserved_and_same_portal_owned_live_can_switch(self):
        exit=importlib.import_module('playback_exit')
        for identity in (None,('media',{'pid':'p'}),('live',{'pid':'other'})):
            with mock.patch.object(self.play,'player_state',return_value=(True,'private-file')),mock.patch.object(exit,'identity',return_value=identity):
                intent=self.play.request(self.portal,dict(sid='1'),(True,'private-file'))
                self.rejected(intent,'FOREIGN_PLAYER')
        with mock.patch.object(self.play,'player_state',return_value=(True,'private-file')),mock.patch.object(exit,'identity',return_value=('live',{'pid':'p'})):
            intent=self.play.request(self.portal,dict(sid='1'),(True,'private-file'))
            self.assertTrue(self.play.handoff(self.router,self.portal,intent))
        self.assertEqual(len(self.builtins),1)

    def test_invalid_changed_disabled_and_missing_entities_have_separate_reasons(self):
        intent=self.intent();intent['pid']='other';self.rejected(intent,'INVALID_INTENT')
        intent=self.intent();intent['sid']='absent';self.rejected(intent,'CHANNEL_UNAVAILABLE')
        intent=self.intent()
        with mock.patch.object(sys.modules['portals'],'get_by_id',return_value=None):self.rejected(intent,'PORTAL_UNAVAILABLE')
        intent=self.intent()
        with mock.patch.object(sys.modules['portals'],'get_by_id',return_value=dict(self.portal,type='m3u')):self.rejected(intent,'PORTAL_CHANGED')
        self.portal['type']='unsupported';self.rejected(self.intent(),'UNSUPPORTED_PORTAL')

    def test_consumed_intent_never_restarts_after_any_number_of_replays(self):
        intent=self.intent();self.assertTrue(self.play.handoff(self.router,self.portal,intent))
        for _ in range(4):
            self.assertFalse(self.play.handoff(self.router,self.portal,intent))
            self.assertIn('reason=REPLAY',self.logs[-1])
        self.assertEqual(len(self.builtins),1)
        self.assertTrue(intent['consumed'])

    def test_failure_logs_only_allowlisted_codes_and_random_correlations(self):
        intent=self.intent();intent.update(owner='URL-SECRET',lease='private-portal',request='bad-token')
        with mock.patch.object(self.index,'Reader',side_effect=RuntimeError('https://user:SECRET@provider.invalid/path')):
            self.rejected(intent,'EXCEPTION_CLASS')
        rendered=' '.join(self.logs)
        for private in ('SECRET','provider.invalid','private-portal','URL-SECRET','bad-token'):
            self.assertNotIn(private,rendered)
        self.assertIn('error=RuntimeError',rendered)

    def test_player_change_during_read_is_checked_again_before_resolver(self):
        with mock.patch.object(self.play,'player_state',side_effect=[(False,''),(True,'private-new')]):
            self.rejected(self.intent(),'PLAYER_STATE_CHANGED')

    def test_native_marker_belongs_to_this_instance_before_dialog_id_is_accepted(self):
        w=self.guide_window();self.addCleanup(w.close)
        self.assertEqual(self.life.capture(w)['surface'],'dialog')
        self.assertEqual(self.life.capture(w)['window'],13001)
        w.setProperty(self.life.OWNER_PROPERTY,'foreign');w._native_dialog_id=None
        self.assertIsNone(self.life.capture(w)['window'])

    def test_navigation_lease_is_unique_cleared_after_release_and_root_trace_has_no_arguments(self):
        nav=importlib.import_module('window_navigation');self.router._params['q']='PRIVATE QUERY'
        self.router._params['pid']='PRIVATE ACCOUNT'
        with nav.ownership() as acquired:
            self.assertTrue(acquired);first=self.life.lease();self.assertEqual(len(first),32)
            self.life.route_phase(self.router,'ENTRY','root')
            with nav.ownership() as nested:self.assertFalse(nested)
            self.assertEqual(self.life.lease(),first)
        self.assertEqual(self.life.lease(),'')
        with nav.ownership() as acquired:self.assertNotEqual(self.life.lease(),first)
        self.assertNotIn('PRIVATE',' '.join(self.logs))
        self.assertIn('phase=ENTRY action=root',' '.join(self.logs))

    def test_async_busy_foreign_and_abort_never_open_search_or_force_dialog_closed(self):
        nav=importlib.import_module('search_navigation');router=self.router;router._search_async_owner=True
        for dialog,reason in ((10138,'BUSY_REENTRANT'),(10103,'FOREIGN_MODAL')):
            snapshot=dict(window=10025,dialog=dialog,modal=True,updating=False)
            with mock.patch.object(self.life,'state',return_value=snapshot),mock.patch.object(nav,'time',types.SimpleNamespace(monotonic=Counter())):
                self.assertFalse(nav.released(router,'grid','a'*32,dict(surface='dialog',window=13001)))
                self.assertEqual(router._search_block_reason,reason)
        with mock.patch.object(self.xbmc,'Monitor',return_value=types.SimpleNamespace(waitForAbort=lambda _:True)):
            self.assertFalse(nav.released(router,'grid','a'*32,None));self.assertEqual(router._search_block_reason,'ABORT')
        self.assertFalse(self.builtins)


if __name__=='__main__':unittest.main()
