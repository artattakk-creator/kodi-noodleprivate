"""Start group, delayed catalogue, mini focus and profile integrity."""
import importlib,json,sys,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture,ADDON,QueuedPool
import test_xcmate_kodi21_overlay as _overlay_model


class GroupFocus35(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('guide_grid_window','guide_grid_data'):sys.modules.pop(name,None)
        self.grid=importlib.import_module('guide_grid_window');self.data=importlib.import_module('guide_grid_data')
        p=mock.patch.object(self.grid,'ThreadPoolExecutor',QueuedPool);p.start();self.addCleanup(p.stop)
    def window(self):
        w=self.grid.GuideGridWindow('XCMateGuideGrid.xml',str(ADDON),'Default','720p');w.configure(self.router,self.portal)
        self.addCleanup(w.close);w.show();self.settle(w);return w
    def test_valid_saved_group_wins_over_start_channel_in_other_group_without_reordering(self):
        entries=[dict(stream_id='a1',category_id='a',name='A'),dict(stream_id='b1',category_id='b',name='B')]
        self.index.replace_catalog('p','live',entries,self.catalogs['get_live_categories'])
        self.portal.update(start_group_id='b',start_stream_id='a1');before=json.dumps(self.portal,sort_keys=True)
        w=self.window();self.assertEqual(w.category,'b');self.assertEqual([r['channel']['sid'] for r in w.rows],['b1'])
        self.assertEqual(json.dumps(self.portal,sort_keys=True),before);self.assertFalse(self.options)
    def test_delayed_catalogue_retries_saved_start_group_instead_of_first_group(self):
        self.index.replace_catalog('p','live',[],[]);self.portal.update(start_group_id='b',start_stream_id='b1')
        w=self.window();self.assertEqual(w.mode,'groups');self.assertTrue(w._start_pending)
        self.index.replace_catalog('p','live',[dict(stream_id='a1',category_id='a',name='A'),dict(stream_id='b1',category_id='b',name='B')],self.catalogs['get_live_categories'])
        w._start_retry=0;w._owner_tick();self.settle(w)
        self.assertEqual(w.mode,'grid');self.assertEqual(w.category,'b');self.assertEqual(w.rows[w.row]['channel']['sid'],'b1')
        self.assertFalse(w._start_pending)
    def test_explicit_group_and_search_return_never_reapply_start_default(self):
        self.index.replace_catalog('p','live',[dict(stream_id='a1',category_id='a',name='A'),dict(stream_id='b1',category_id='b',name='B')],self.catalogs['get_live_categories'])
        w=self.window();w._show_groups(refresh=False);w.getControl(200).selectItem(1);w._choose_group();self.settle(w)
        self.assertEqual(w.category,'b');self.assertFalse(w._start_pending)
        w._start_retry=0;w._owner_tick();self.settle(w);self.assertEqual(w.category,'b')
    def test_ram_focus_respects_portal_current_group_disabled_group_and_empty_catalogue(self):
        from tv_focus import target
        from tv_data import CatalogIndex
        channels=[types.SimpleNamespace(extra={'stream_id':str(i),'category_id':'b' if i>100 else 'a'}) for i in range(240)]
        index=CatalogIndex(channels)
        self.assertEqual(target(self.portal,index,{'a','b'},'225')[:2],('b',124))
        self.assertEqual(target(self.portal,index,{'a'},'225')[0],'a')
        self.assertEqual(target(self.portal,index,set(),'225'),('',0,False))


class MiniNativeFocus35(unittest.TestCase):
    setUp=_overlay_model.OverlayLifecycleTests.setUp
    def test_reopening_mini_list_reselects_current_sid_even_in_same_native_page(self):
        # Actual native ControlList selection must follow current SID, not a
        # stale highlighted row with the same list/layout key.
        self.overlay._highlight['channels']=3;self.overlay._switch('channels');self.overlay.control.selectItem(3)
        self.overlay._switch('hidden')
        with mock.patch('playback_exit.identity',return_value=('live',dict(pid='p',sid='2'))):
            self.overlay.handle_command('left')
        self.assertEqual(self.overlay.mode,'channels');self.assertEqual(self.overlay.control.getSelectedPosition(),1)
        self.assertEqual(self.overlay._highlight['channels'],1);self.player.play.assert_not_called();self.player.stop.assert_not_called()
    def test_other_portal_tag_does_not_select_a_same_sid_from_wrong_portal(self):
        self.overlay._switch('hidden')
        with mock.patch('playback_exit.identity',return_value=('live',dict(pid='other',sid='3'))):
            self.overlay._focus_playing_channel()
        self.assertEqual(self.overlay._highlight['channels'],0)
