"""Actual native controls with modeled Kodi owner/IR and local guide data."""
import importlib,json,time,unittest
from pathlib import Path
from unittest import mock
import test_xcmate_kodi21_overlay as model

class Navigation38(unittest.TestCase):
    def setUp(self):
        self.m=model.OverlayLifecycleTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.o=self.m.overlay;self.o._switch('hidden');self.sid=self.o.sid

    def test_five_left_levels_twenty_cycles_never_stop_or_retune(self):
        for _ in range(20):
            for wanted in ('channels','groups','nav_icons','nav_expanded','hidden'):
                self.o.handle_command('left');self.assertEqual(self.o.mode,wanted)
            self.assertEqual(self.o.sid,self.sid)
        self.m.player.stop.assert_not_called()

    def test_reverse_rail_levels_restore_groups_then_same_mini_focus(self):
        for _ in range(3):self.o.handle_command('left')
        self.o.handle_command('left');self.o.handle_command('back');self.assertEqual(self.o.mode,'nav_icons')
        self.o.handle_command('right');self.assertEqual(self.o.mode,'groups')
        self.o.handle_command('right');self.assertEqual(self.o.mode,'channels');self.assertEqual(self.o.sid,self.sid)

    def test_compact_expanded_full_height_buttons_and_local_icons(self):
        for _ in range(3):self.o.handle_command('left')
        rail=self.o._nav_rail;self.assertEqual(rail.panel.options['height'],self.o._height-48)
        before=rail.panel.options['height'];self.o.handle_command('left');self.assertEqual(rail.panel.options['height'],before)
        actions=[e[3] for e in rail.items]
        self.assertTrue({'global_search','favourites','home_live','movies_home','series_home','guide_grid','settings_home','xcmate_home','startup_current'}<=set(actions))
        for _ in range(len(rail.items)*2):self.o.handle_command('down');self.assertIs(self.o.focus,rail.buttons[rail.position])
        for image in rail.icons:self.assertIn('/navigation/',image.image)

    def test_mini_highlight_changes_programmes_without_tune(self):
        self.o.handle_command('left');self.o._guide.get=mock.Mock(side_effect=lambda sid:dict(now='',next='',now_time='',now_end_time='',events=[dict(title='Station '+sid,start=time.time()-60,stop=time.time()+300,description='Actual local programme')]))
        self.o._render();before=self.o._mini.sid
        with mock.patch.object(self.o,'_tune') as tune:
            self.o.handle_command('down');self.assertNotEqual(self.o._mini.sid,before)
            self.o.handle_command('right');self.assertEqual(self.o.mode,'channels');self.assertTrue(self.o._mini.focused)
            self.o.handle_command('back');self.assertFalse(self.o._mini.focused);self.assertEqual(self.o.mode,'channels')
            tune.assert_not_called()
        self.assertEqual(self.o.sid,self.sid)

    def test_programme_focus_does_not_skip_groups_on_left(self):
        self.o.handle_command('left');self.o._guide.get=lambda sid:dict(now='',next='',now_time='',now_end_time='',events=[dict(title='Now',start=time.time()-1,stop=time.time()+60)])
        self.o.handle_command('right');self.assertTrue(self.o._mini.focused)
        self.o.handle_command('left');self.assertEqual(self.o.mode,'channels');self.assertFalse(self.o._mini.focused)
        self.o.handle_command('left');self.assertEqual(self.o.mode,'groups')

    def test_empty_epg_has_no_fictitious_programme_or_tune(self):
        self.o.handle_command('left');self.o._guide.get=lambda sid:dict(now='',next='',now_time='',now_end_time='',events=[])
        self.o._render();self.o.handle_command('right');self.assertFalse(self.o._mini.focused);self.assertFalse(self.o._mini.events)

    def test_real_previous_now_next_order_and_no_invalid_times(self):
        module=importlib.import_module('mini_epg')
        events=[dict(title='After',start=110,stop=130),dict(title='Before',start=70,stop=90),dict(title='Now',start=90,stop=110),dict(title='Invalid',start=110,stop=100)]
        rows,pos=module.programme_rows(events,100);self.assertEqual([e['title'] for e in rows],['Before','Now','After']);self.assertEqual(pos,1)
