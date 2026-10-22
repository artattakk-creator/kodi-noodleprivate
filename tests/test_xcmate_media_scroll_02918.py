"""Real SQLite, native panel movement, async append and non-destructive state."""
import importlib,json,sys,time,types,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,ADDON

class ProgressiveMediaTests(Fixture,unittest.TestCase):
    def category(self,kind='vod',count=100):
        records=[dict(stream_id=str(i),series_id=str(i),category_id='a',name='Synthetic '+str(i),added=self.now-i) for i in range(count)]
        if count:self.index.import_group('p',kind,'a',records)
        w=self.media_window(kind);w.category='a' if count else 'b';w._page('grid',0);self.settle(w);return w
    def test_counts_small_and_large_for_movies_and_series_are_real_filtered_totals(self):
        for kind in ('vod','series'):
            for count in (0,1,24,25,48,49,103):
                with self.subTest(kind=kind,count=count):
                    w=self.category(kind,count);seen={r['sid'] for r in w.rows}
                    while w.offset+len(w.rows)<w.total:
                        w._prefetch(force=True);self.settle(w);seen.update(r['sid'] for r in w.rows)
                    self.assertEqual(w.total,count);self.assertEqual(len(seen),count)
                    if count:self.assertIn(str(count),w._page_status)
                    w.close()
    def test_native_down_appends_without_right_and_keeps_focused_cover(self):
        w=self.category(count=79);w.getControl(210).selectItem(18);w._focus_item(18)
        w.native(4);self.assertEqual(len(w.rows),24);self.assertIsNotNone(w._append_future)
        sid=w.rows[w.getControl(210).getSelectedPosition()]['sid'];self.settle(w)
        self.assertEqual(len(w.rows),48);self.assertEqual(w.rows[w.getControl(210).getSelectedPosition()]['sid'],sid)
        self.assertEqual(len(w.getControl(210).items),48);self.assertIn('48',w.getControl(102).label)
        self.assertFalse(self.builtins);sys.modules['utils'].http_get.assert_not_called()
    def test_native_down_at_consumed_boundary_advances_when_batch_finishes(self):
        w=self.category(count=53);w.getControl(210).selectItem(23);w._focus_item(23)
        w.native(4);self.assertEqual(w.getControl(210).getSelectedPosition(),23);self.settle(w)
        self.assertGreater(w.getControl(210).getSelectedPosition(),23);self.assertEqual(len(w.rows),48)
    def test_owner_poll_prefetches_when_native_control_swallows_down_callback(self):
        w=self.category(count=71);w.getControl(210).selectItem(22)
        w.pump();self.assertIsNotNone(w._append_future);self.settle(w);self.assertEqual(len(w.rows),48)
        self.assertEqual(w.getControl(210).getSelectedPosition(),22)
    def test_large_catalogue_is_ordered_bounded_and_reachable_in_both_directions(self):
        w=self.category(count=1703);seen=set();previous_end=0
        while True:
            seen.update(r['sid'] for r in w.rows)
            self.assertLessEqual(len(w.rows),240);self.assertEqual(len(w.rows),len(w.getControl(210).items))
            self.assertEqual([r['sid'] for r in w.rows],[str(i) for i in range(w.offset,w.offset+len(w.rows))])
            end=w.offset+len(w.rows);self.assertGreater(end,previous_end);previous_end=end
            if end==w.total:break
            pos=len(w.rows)-1;w.getControl(210).selectItem(pos);w._focus_item(pos)
            w._prefetch(force=True);self.settle(w)
        self.assertEqual(len(seen),1703)
        while w.offset:
            w.getControl(210).selectItem(0);w._focus_item(0);old=w.offset
            w.native(3);self.settle(w);self.assertLess(w.offset,old);self.assertLessEqual(len(w.rows),240)
        self.assertEqual(w.rows[0]['sid'],'0')
    def test_detail_back_restores_loaded_window_category_and_exact_title(self):
        w=self.category(count=341)
        for _ in range(3):w._prefetch(force=True);self.settle(w)
        w.getControl(210).selectItem(53);w._focus_item(53);before=[r['sid'] for r in w.rows]
        w.native(7);self.settle(w);w.native(92);self.settle(w)
        self.assertEqual(w.mode,'grid');self.assertEqual(w.category,'a');self.assertEqual([r['sid'] for r in w.rows],before)
        self.assertEqual(w.rows[w.getControl(210).getSelectedPosition()]['sid'],'53')
    def test_category_change_ignores_running_stale_append(self):
        w=self.category(count=100);w._prefetch(force=True);future=w._append_future;future.set_running_or_notify_cancel()
        w.category='b';w._page('grid',0);self.settle(w)
        self.assertEqual(w.category,'b');self.assertFalse(w.rows);self.assertEqual(w.total,0)
    def test_failed_append_preserves_page_and_explicit_retry_recovers(self):
        w=self.category(count=70);before=[r['sid'] for r in w.rows]
        with mock.patch.object(w.reader,'page',side_effect=RuntimeError('BUSY')):
            w._prefetch(force=True);self.settle(w)
        self.assertTrue(w._append_failed);self.assertEqual([r['sid'] for r in w.rows],before)
        w._prefetch(force=True);self.settle(w);self.assertEqual(len(w.rows),48)
    def test_repeated_down_does_not_queue_duplicate_batches(self):
        w=self.category(count=100);w.getControl(210).selectItem(23);w._focus_item(23)
        for _ in range(12):w.native(4)
        self.assertEqual(len(w._pool.jobs),1);self.settle(w)
        self.assertEqual(len(w.rows),48);self.assertEqual(len(set(r['sid'] for r in w.rows)),48)
    def test_append_worker_is_cancelled_on_close(self):
        w=self.category(count=100);w._prefetch(force=True);future=w._append_future;w.close()
        self.assertTrue(future.cancelled());self.assertTrue(w._closed)
    def test_hidden_movie_preserves_resume_watched_favourite_and_catalogue_across_reload(self):
        hidden=importlib.import_module('media_continue');self.state.save_progress(dict(pid='p',kind='vod',sid='2'),601,2700)
        self.state.toggle('p','vod','2');before=self.state.read();catalog=self.index.Reader('p').page('vod')
        hidden.hide('p','2');hidden=importlib.reload(hidden)
        self.assertEqual(self.state.read(),before);self.assertEqual(self.index.Reader('p').page('vod'),catalog)
        self.assertFalse(self.state.rail_items('p','vod',self.index.Reader('p'),'continue'))
        self.assertEqual(len(self.state.rail_items('p','vod',self.index.Reader('p'),'favourites')),1)
        self.assertEqual(self.state.resume_position(self.state.progress('p','vod','2')),601)
        hidden.hide('other','2');hidden.reveal('p','2');self.assertEqual(hidden.hidden('p'),set());self.assertEqual(hidden.hidden('other'),{'2'})
    def test_continue_context_hides_only_after_explicit_choice_and_keeps_safe_focus(self):
        self.state.save_progress(dict(pid='p',kind='vod',sid='2'),601,2700);w=self.media_window();w.setFocusId(112)
        self.dialog.select.return_value=-1;w.native(117);self.settle(w);self.assertEqual(len(w.rails[112]),1)
        self.dialog.select.return_value=0;w.native(117);self.assertEqual(len(w.rails[112]),1);self.settle(w)
        self.assertFalse(w.rails[112]);self.assertIn(w.getFocusId(),w._valid_focus());self.assertFalse(self.builtins)
        self.assertEqual(self.state.resume_position(self.state.progress('p','vod','2')),601)
    def test_missing_hidden_store_is_not_created_by_read_or_normal_catalogue(self):
        hidden=importlib.import_module('media_continue');self.assertFalse(Path(hidden.path()).exists())
        self.assertEqual(hidden.hidden('p'),set());hidden.reveal('p','1');self.assertFalse(Path(hidden.path()).exists())
    def test_episode_icons_legend_and_progress_keep_existing_state_semantics(self):
        w=self.media_window('series');w.native(7);self.settle(w);w.getControl(300).selectItem(next(i for i,a in enumerate(w.actions) if a[1]=='seasons'));w.onClick(300)
        w.onClick(330);self.assertEqual(w.mode,'episodes')
        e=w.visible_episodes[0];self.state.mark_episode('p',e,True);w._show_episodes()
        self.assertTrue(w.getControl(330).items[0].getProperty('XCMate.Eye').endswith('eye_watched.png'))
        self.assertTrue(w.getControl(330).items[1].getProperty('XCMate.Eye').endswith('eye_unseen.png'))
        self.assertTrue(w.getControl(630).visible);self.assertIn('Ungesehen',w.getControl(631).label);self.assertIn('Gesehen',w.getControl(633).label)
        self.state.mark_episode('p',e,False);w._show_episodes();self.assertTrue(w.getControl(330).items[0].getProperty('XCMate.Eye').endswith('eye_unseen.png'))
    def test_natural_end_without_oninit_restores_detail_focus_on_owner_and_no_autoplay(self):
        w=self.media_window('series');w.native(7);self.settle(w);w._play(w.episodes[0],'episode')
        playing=[True];player=types.SimpleNamespace(isPlayingVideo=lambda:playing[0],getVideoInfoTag=lambda:types.SimpleNamespace(getUniqueID=lambda key:w._play_intent))
        with mock.patch.object(sys.modules['xbmc'],'Player',return_value=player):
            w.pump();self.assertTrue(w._playback_seen)
            # Model Kodi returning with a cleared focus and no Python onInit.
            w.focus=400;playing[0]=False;w.pump()
        self.assertEqual(w.getFocusId(),300);self.assertFalse(w._playback_waiting)
        calls=len(self.builtins);w.native(4);w.native(3);self.assertEqual(len(self.builtins),calls)
        self.assertFalse(w._closed);self.assertFalse(w._leaving)
    def test_pending_start_is_not_mistaken_for_episode_end(self):
        w=self.media_window('series');w.native(7);self.settle(w);w._play(w.episodes[0],'episode')
        w.pump();self.assertTrue(w._playback_waiting);self.assertFalse(w._playback_seen)
    def test_native_reinit_after_playback_keeps_actions_and_navigation(self):
        w=self.media_window('series');w.native(7);self.settle(w);self.assertTrue(w.episodes)
        self.state.mark_episode('p',w.episodes[0],True)
        w._playback_waiting=True;w._playback_seen=True;w.onInit()
        self.assertEqual(w.getFocusId(),300);self.assertIn('next_episode',[a[1] for a in w.actions])
        self.assertFalse(w._playback_waiting);w.native(92);self.settle(w);self.assertEqual(w.mode,'landing')
    def test_catalogue_refresh_restores_absolute_selected_title_after_multiple_batches(self):
        w=self.category(count=220);w._prefetch(force=True);self.settle(w);w._prefetch(force=True);self.settle(w)
        w.getControl(210).selectItem(51);w._focus_item(51)
        w._catalog_update=(w.reader,w.reader.state(w.kind),'new-revision',None,w.groups)
        w.pump();self.settle(w)
        self.assertEqual(w.rows[w.getControl(210).getSelectedPosition()]['sid'],'51')
    def test_live_exit_and_movie_progress_modules_are_not_called_by_episode_focus_restore(self):
        w=self.media_window('series');w.native(7);self.settle(w);w._playback_waiting=w._playback_seen=True
        with mock.patch.object(self.media,'xbmc') as kodi:
            kodi.Player.return_value.isPlayingVideo.return_value=True
            kodi.Player.return_value.getVideoInfoTag.return_value.getUniqueID.return_value=w._play_intent
            w._catalog_update=(w.reader,w.reader.state(w.kind),'new',None,w.groups)
            with mock.patch.object(w,'_refresh_art') as art:w._owner_tick();art.assert_not_called()
        self.assertFalse(w._closed)
