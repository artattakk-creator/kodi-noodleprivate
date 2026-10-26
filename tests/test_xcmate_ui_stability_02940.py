"""Targeted Kodi21 native UI contracts; real Android rendering stays NOT_TESTED."""
import importlib,sys,threading,time,types,unittest
from pathlib import Path
from unittest import mock
import test_xcmate_kodi21_overlay as live
import test_xcmate_media_osd_02921 as media

class UIStability40(unittest.TestCase):
    def setUp(self):
        self.m=live.OverlayLifecycleTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.o=self.m.overlay

    def test_two_line_mini_title_is_bounded_and_narrower_at_both_resolutions(self):
        mini=importlib.import_module('mini_epg')
        for w,h in ((1280,720),(1920,1080)):
            self.o._width=w;self.o._height=h;pane=mini.MiniProgramme(self.o)
            text=mini.wrap_title('A very long programme title with many words '*30,pane.column_width)
            self.assertEqual(len(text.splitlines()),2);self.assertTrue(text.endswith('…'))
            self.assertLessEqual(pane.column_width,w*.32)
            self.assertEqual(len(pane.rows),5)
            for _,_,title in pane.rows:self.assertEqual(title.options['height'],40)

    def test_now_mark_and_focus_are_independent_in_two_line_programme_painter(self):
        mini=self.o._mini;now=time.time()
        mini.events=[dict(title='Now programme',start=now-30,stop=now+30),dict(title='Next programme',start=now+30,stop=now+60)]
        mini.focused=True;mini.selected=1;mini._paint()
        self.assertIn('FF55DD99',mini.rows[0][1].label)
        self.assertFalse(mini.rows[0][0].visible);self.assertTrue(mini.rows[1][0].visible)
        self.assertEqual(mini.rows[0][2].text,'Now programme')

    def test_twenty_navigation_hides_clear_owned_labels_and_closed_surface(self):
        for _ in range(20):
            self.o._switch('groups');self.o._switch('nav_expanded');self.o._switch('hidden')
            self.assertFalse(self.o.heading.label);self.assertFalse(self.o.sub.label);self.assertFalse(self.o.footer.label)
            self.assertTrue(all(not title.label and not detail.label for _,_,title,detail in self.o._row_controls))
            self.assertTrue(all(not b.enabled and not b.label for b in self.o._nav_rail.buttons))
        self.o._switch('info');self.o.close()
        self.assertTrue(all(not c.visible for c in self.o._info_controls))
        self.assertFalse(self.o.info_name.label)

    def test_standard_osd_first_ok_recovery_opens_infobar_then_controls(self):
        own=('live',dict(pid='p',sid='1',nonce='n',at=time.time()))
        self.o._switch('hidden')
        with mock.patch('playback_exit.identity',return_value=own),mock.patch('osd_ownership.recover',side_effect=[True,False]),mock.patch.object(sys.modules['xbmcgui'],'getCurrentWindowDialogId',return_value=9999,create=True):
            self.o.tick();self.o.tick()
        self.assertEqual(self.o.mode,'info');self.assertTrue(self.o.info_name.visible)
        self.o.handle_command('ok');self.assertEqual(self.o.mode,'controls')
        self.m.player.stop.assert_not_called()

    def test_slow_local_epg_refresh_does_not_hold_ir_navigation_or_ram_snapshot(self):
        entered=threading.Event();release=threading.Event();errors=[]
        def cache(*a,**kw):entered.set();release.wait(3);return None
        def refresh():
            try:self.o._guide.refresh()
            except BaseException as exc:errors.append(type(exc).__name__)
        with mock.patch('guide_viewport.cache',side_effect=cache),mock.patch('epg_status.revision',return_value='published'),mock.patch.dict(sys.modules,epg_sources=types.SimpleNamespace(configuration=lambda pid:dict(mappings={}))),mock.patch.object(sys.modules['epg'],'_mem_clear',create=True),mock.patch('logo_cache.request'):
            worker=threading.Thread(target=refresh);worker.start()
            try:
                self.assertTrue(entered.wait(1))
                for _ in range(20):self.o.handle_command('left');self.o.handle_command('back');self.o._guide.get('1')
                self.assertTrue(worker.is_alive());self.m.player.stop.assert_not_called()
            finally:release.set();worker.join(2)
        self.assertFalse(errors)

class StreamGroups40(unittest.TestCase):
    def setUp(self):
        self.m=media.MediaOSDTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.details=importlib.import_module('stream_details')

    def test_video_audio_subtitle_snapshot_uses_local_icons_and_honest_unknown_values(self):
        values=dict(width='1920',height='1080',video='h264',audio='aac',subtitle_enabled=False)
        groups=self.details.groups(values)
        self.assertEqual(len(groups),7);self.assertEqual(len(set(row[0] for row in groups)),3)
        self.assertEqual(groups[0][3],'1920×1080');self.assertNotIn('SDR',str(groups));self.assertNotIn(' fps',groups[2][3])
        dialog=mock.Mock();dialog.select.return_value=-1
        with mock.patch.object(sys.modules['xbmcgui'],'Dialog',return_value=dialog):self.details.present(values)
        self.assertTrue(dialog.select.call_args.kwargs['useDetails'])
        items=dialog.select.call_args.args[1];self.assertEqual(len(items),7)
        from player_controls import texture
        for _,_,icon,_ in groups:self.assertTrue(Path(texture(icon)).is_file())
        self.m.player.stop.assert_not_called()

    def test_video_osd_is_recovered_even_during_transient_fullscreen_flag_loss(self):
        sys.modules['xbmcgui'].getCurrentWindowDialogId=lambda:12901
        with mock.patch.object(self.m.osd,'_fullscreen',return_value=False):self.m.osd.poll(self.m.player)
        self.assertIn('Dialog.Close(videoosd)',self.m.builtins);self.m.player.stop.assert_not_called()
