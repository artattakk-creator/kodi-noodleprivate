"""Observe unchanged refreshes and the user's exact two-Right category contract."""
import importlib,time,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture
import test_xcmate_kodi21_overlay as gui

class MediaNavigation44(Fixture,unittest.TestCase):
    def category(self):
        w=self.media_window();w.onClick(120);self.settle(w);self.assertEqual(w.getFocusId(),200);return w
    def test_up_down_only_moves_category_focus_until_ok_confirms_it(self):
        w=self.category();category=w.category;rows=list(w.rows)
        with mock.patch.object(w,'_request') as query:
            w.native(4);self.assertEqual(w.category,category);self.assertEqual(w.rows,rows);query.assert_not_called()
        w.native(7);self.settle(w);self.assertEqual(w.category,w.groups[1]['cid']);self.assertEqual(w.getFocusId(),200)
    def test_first_right_poster_one_with_sidebar_second_right_poster_two_full_width(self):
        w=self.category();w.native(2)
        self.assertEqual(w.getFocusId(),210);self.assertEqual(w.getControl(210).getSelectedPosition(),0);self.assertTrue(w.getControl(200).visible);self.assertEqual(w._cols,4)
        w.native(2);self.assertEqual(w.getControl(210).getSelectedPosition(),1);self.assertFalse(w.getControl(200).visible);self.assertEqual(w._cols,6)
    def test_additional_left_at_gallery_edge_restores_category_without_reloading(self):
        w=self.category();w.native(2);w.native(2);w.native(1)
        self.assertEqual(w.getControl(210).getSelectedPosition(),0);self.assertFalse(w.getControl(200).visible)
        with mock.patch.object(w,'_request') as query:w.native(1);query.assert_not_called()
        self.assertEqual(w.getFocusId(),200);self.assertTrue(w.getControl(200).visible)
    def test_identical_background_page_keeps_native_items_and_focus(self):
        w=self.category();w.native(2);w.native(2);w.getControl(210).selectItem(7);w._focus_item(7)
        items=list(w.getControl(210).items)
        with mock.patch.object(w.getControl(210),'reset',side_effect=AssertionError('unchanged native page reset')):
            w._page(w.mode,w.offset);self.settle(w)
        self.assertEqual(w.getControl(210).items,items);self.assertEqual(w.getControl(210).getSelectedPosition(),7);self.assertEqual(w.getFocusId(),210)
    def test_detail_back_preserves_confirmed_category_and_sidebar_layout(self):
        w=self.category();w.native(2);w.native(7);self.settle(w);self.assertEqual(w.mode,'detail');w.native(92);self.settle(w)
        self.assertEqual(w.mode,'grid');self.assertEqual(w.getFocusId(),210);self.assertTrue(w.getControl(200).visible);self.assertEqual(w.getControl(210).getSelectedPosition(),0)
    def test_unchanged_guide_worker_ticks_do_not_increment_visible_generation(self):
        data=importlib.import_module('tv_data');store=importlib.import_module('guide_store')
        store.import_cache('p',{'xml':[dict(name='Real programme',start_timestamp=self.now-10,stop_timestamp=self.now+3600)]})
        snap=data.GuideSnapshot(self.portal,self.client);channel=types.SimpleNamespace(tvg_id='xml',extra=dict(stream_id='1'))
        snap.request([channel]);snap.refresh();generation=snap.generation
        for _ in range(20):snap.refresh()
        self.assertEqual(snap.generation,generation)
        self.assertTrue(snap.get('1')['snapshot_revision'])

class LiveRendering44(unittest.TestCase):
    def setUp(self):
        self.m=gui.OverlayLifecycleTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups);self.o=self.m.overlay
    def test_200_identical_left_row_renders_have_no_hide_show_label_or_image_writes(self):
        self.o._switch('channels');self.o._render();calls=[]
        for row in self.o._row_controls:
            for control in row:
                for method in ('setVisible','setLabel','setImage','setWidth','setPosition'):
                    if not hasattr(control,method):continue
                    fn=getattr(control,method)
                    def observe(*a,_fn=fn,_method=method,**kw):calls.append(_method);return _fn(*a,**kw)
                    setattr(control,method,observe)
        for _ in range(200):self.o._render(focus=False)
        self.assertEqual(calls,[]);self.m.player.stop.assert_not_called()
    def test_expanded_to_groups_collapses_separate_text_controls_before_width_change(self):
        o=self.o
        for _ in range(20):
            o._switch('nav_expanded');rail=o._nav_rail;self.assertTrue(any(c.visible and c.label for c in rail.captions))
            original=rail.panel.setWidth
            def change(width):
                if width==84:self.assertTrue(all(not c.visible and not c.label for c in rail.captions))
                return original(width)
            with mock.patch.object(rail.panel,'setWidth',side_effect=change):o._switch('groups')
            self.assertTrue(all(not b.label for b in rail.buttons));self.assertTrue(all(not c.visible and not c.label for c in rail.captions));self.assertTrue(all(i.visible for i in rail.icons))
        self.m.player.stop.assert_not_called()
    def test_hide_then_show_restores_cached_rows_without_ghosting(self):
        o=self.o;o._switch('channels');labels=[title.label for _,_,title,_ in o._row_controls];o._switch('hidden');o._switch('channels')
        self.assertEqual([title.label for _,_,title,_ in o._row_controls],labels);self.assertTrue(o._row_controls[0][2].visible)
