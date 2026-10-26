"""New explicit four-level Live FSM, ghost label reset and independent NOW/focus."""
import importlib,time,unittest
from unittest import mock
import test_xcmate_kodi21_overlay as model


class RailMini39(unittest.TestCase):
    def setUp(self):
        self.m=model.OverlayLifecycleTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.o=self.m.overlay;self.o._switch('hidden')

    def test_twenty_live_group_compact_full_cycles_preserve_stream_and_focus(self):
        o=self.o
        for _ in range(20):
            o.handle_command('left');self.assertEqual(o.mode,'channels');pos=o._highlight['channels']
            o.handle_command('left');self.assertEqual(o.mode,'groups');self.assertTrue(o._nav_rail.active);self.assertFalse(o._nav_rail.expanded)
            self.assertIs(o.focus,o.control)
            o.handle_command('left');self.assertEqual(o.mode,'nav_expanded');self.assertTrue(o._nav_rail.expanded)
            o.handle_command('back');self.assertEqual(o.mode,'groups')
            o.handle_command('right');self.assertEqual(o.mode,'channels');self.assertEqual(o._highlight['channels'],pos)
            o.handle_command('back');self.assertEqual(o.mode,'hidden')
        self.assertEqual(o.sid,'1');self.m.player.stop.assert_not_called()

    def test_hide_clears_all_native_labels_images_and_button_focusability(self):
        rail=self.o._nav_rail
        for _ in range(20):
            rail.show(True);self.assertTrue(any(b.label for b in rail.buttons))
            rail.hide()
            self.assertTrue(all(not b.label and not b.visible and not b.enabled for b in rail.buttons))
            self.assertTrue(all(not im.visible and not im.image for im in rail.icons));self.assertFalse(rail.panel.visible)

    def test_compact_group_rail_does_not_overlap_group_list(self):
        self.o._switch('groups');self.assertGreater(self.o.control.position[0],108)
        self.o._switch('channels');self.assertEqual(self.o.control.position[0],44)

    def test_now_mark_is_permanent_when_right_focus_moves_to_another_event(self):
        now=time.time();events=[dict(title='Before',start=now-600,stop=now-300),dict(title='Now',start=now-300,stop=now+300),dict(title='Next',start=now+300,stop=now+600)]
        self.o._guide.get=lambda sid:dict(now='Now',next='Next',now_time='',now_end_time='',next_time='',events=events)
        self.o.handle_command('left');mini=self.o._mini;self.o.handle_command('right');self.assertTrue(mini.focused)
        original=list(mini.list.items);self.o.handle_command('down');self.assertEqual(mini.selected,2)
        self.assertEqual(mini.list.items,original);self.assertIn('FF55DD99',original[1]);self.assertNotIn('FF55DD99',original[2])
        self.assertIn('▶',mini.hint.label);self.o.handle_command('left');self.assertFalse(mini.focused)
        self.assertEqual(mini.list.options['_itemHeight'],40);self.assertEqual(mini.list.options['font'],'font12')
        self.assertIn('xcmate_focus_neon.png',mini.list.options['buttonFocusTexture'])

    def test_compact_programme_column_fits_720_and_1080_safe_area(self):
        module=importlib.import_module('mini_epg')
        for width,height in ((1280,720),(1920,1080)):
            self.o._width=width;self.o._height=height;pane=module.MiniProgramme(self.o)
            self.assertLess(pane.list.options['x']+pane.list.options['width'],width*.78)
            self.assertLess(pane.list.options['y']+pane.list.options['height'],height-48)
