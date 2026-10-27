"""Parent visibility, delayed native focus and a real local Actions entry."""
import sys,unittest
from unittest import mock
from xcmate027_fixture import Fixture


class Menu28Tests(Fixture,unittest.TestCase):
    def detail(self,kind='vod'):
        w=self.media_window(kind);w._details(w.rows[0]);self.settle(w);return w

    def test_parent_group_is_explicitly_visible_for_both_movie_and_series(self):
        for kind in ('vod','series'):
            w=self.detail(kind)
            self.assertIsNone(w.getControl(800).node.find('visible'))
            self.assertFalse(w.getControl(800).visible);self.assertFalse(w.getControl(810).visible)
            w.native(1)
            self.assertTrue(w.getControl(800).visible);self.assertTrue(w.getControl(810).visible)
            self.assertEqual(w.getFocusId(),810)
            w.native(92);self.assertFalse(w.getControl(800).visible);self.assertFalse(w.getControl(810).visible)

    def test_visible_actions_button_uses_same_panel_without_any_left_event(self):
        w=self.detail();self.assertTrue(w.getControl(820).visible);self.assertEqual(w.getControl(820).label,'Aktionen')
        w.setFocusId(820);w.native(7)
        self.assertTrue(w._detail_menu_open);self.assertTrue(w.getControl(800).visible)
        self.assertEqual(w.getFocusId(),810)
        w.native(2);self.assertEqual(w.getFocusId(),820);self.assertEqual(w.mode,'detail')
        w._show('landing');self.assertFalse(w.getControl(820).visible)

    def test_actions_button_is_reachable_with_right_from_detail_actions(self):
        w=self.detail();w.setFocusId(300);w.native(2)
        self.assertEqual(w.getFocusId(),820);w.native(7);self.assertEqual(w.getFocusId(),810)

    def test_delayed_parent_visibility_defers_focus_until_native_owner_tick(self):
        w=self.detail();w._playback_waiting=True
        with mock.patch.object(w.getControl(800),'isVisible',return_value=False):
            w.native(1);self.assertTrue(w._detail_menu_open)
            self.assertNotEqual(w.getFocusId(),810);self.assertEqual(w._focus_pending,('detail',810))
        w._resume_focus();self.assertEqual(w.getFocusId(),810);self.assertIsNone(w._focus_pending)

    def test_same_detail_refresh_keeps_open_menu_and_close_restores_action_row(self):
        w=self.detail();w.getControl(300).selectItem(1);w.native(1)
        w._show('detail');self.assertTrue(w._detail_menu_open);self.assertEqual(w.getFocusId(),810)
        w.native(92);self.assertEqual(w.getControl(300).getSelectedPosition(),1)
        self.assertEqual(w.getFocusId(),300)

    def test_missing_action_metadata_does_not_hide_menu_when_media_identity_is_known(self):
        w=self.detail();w.actions=[];w.setFocusId(820);w.native(7)
        self.assertTrue(w._detail_menu_open);self.assertEqual(w.getControl(810).size(),6)

    def test_anonymous_trace_carries_eligibility_without_title_or_provider(self):
        w=self.detail()
        with mock.patch.object(sys.modules['xbmc'],'log',create=True) as log,mock.patch.object(sys.modules['xbmc'],'LOGINFO',1,create=True):
            w.native(1);w.native(92)
        rendered=str(log.call_args_list)
        for value in ('DETAIL_LEFT_RECEIVED','DETAIL_MENU_ELIGIBILITY','MENU_VISIBLE','FOCUS_810','MENU_CLOSED'):self.assertIn(value,rendered)
        for value in ('SECRET','provider.invalid',w.selected['name']):self.assertNotIn(value,rendered)


if __name__=='__main__':unittest.main()
