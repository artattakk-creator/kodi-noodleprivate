"""Manual-only Next against real media state, native callbacks and local records."""
import importlib
import sys
import types
import unittest
from unittest import mock
from xcmate027_fixture import Fixture


class ManualNextTests(Fixture,unittest.TestCase):
    def series(self,episodes=None):
        if episodes is not None:self.details['get_series_info']['episodes']=episodes
        w=self.media_window('series');w.native(7);self.settle(w)
        return w

    def episodes(self,w,season=1):
        w.getControl(300).selectItem(next(i for i,a in enumerate(w.actions) if a[1]=='seasons'));w.onClick(300)
        w.getControl(330).selectItem(w.seasons.index(season));w.onClick(330)
        self.assertEqual(w.mode,'episodes')

    def return_from_video(self,w,native=False):
        playing=[True]
        player=types.SimpleNamespace(isPlayingVideo=lambda:playing[0],getVideoInfoTag=lambda:types.SimpleNamespace(getUniqueID=lambda key:w._play_intent))
        with mock.patch.object(sys.modules['xbmc'],'Player',return_value=player):
            w.pump();self.assertTrue(w._playback_seen)
            playing[0]=False;w.focus=400
            if native:w.onInit()
            else:w.pump()

    def test_zero_watched_has_manual_next_and_read_only_navigation_never_starts(self):
        w=self.series();before=self.state.read()
        self.assertIn('next_episode',[a[1] for a in w.actions]);self.assertEqual(w.next_episode['sid'],'12')
        self.episodes(w);self.assertTrue(w.getControl(340).visible)
        w.native(3);self.assertEqual(w.getFocusId(),340)
        w.native(3);self.assertEqual(w.getFocusId(),400)
        w.native(4);self.assertEqual(w.getFocusId(),340)
        w.native(4);self.assertEqual(w.getFocusId(),330)
        self.assertEqual(before,self.state.read());self.assertFalse(self.builtins)

    def test_next_ignores_all_seen_all_unseen_and_mixed_seen(self):
        w=self.series()
        for values in ((False,False,False),(True,True,True),(False,True,False),(True,False,True)):
            for e,seen in zip(w.episodes,values):self.state.mark_episode('p',e,seen)
            w._detail_ready((w.selected,{'episodes':w._episode_raw()}))
            self.assertEqual(w.next_episode['sid'],'12')
        self.assertFalse(self.builtins)

    def test_numeric_sort_gaps_season_transition_and_real_end(self):
        w=self.series({'10':[dict(id='101',episode_num='1')],'2':[dict(id='21',episode_num='1')],
                       '1':[dict(id='110',episode_num='10'),dict(id='12',episode_num='2'),dict(id='11',episode_num='1')]})
        sequence=importlib.import_module('media_sequence')
        rows=sequence.ordered(w.episodes,'p','1');self.assertEqual([e['sid'] for e in rows],['11','12','110','21','101'])
        for current,target in zip(rows,rows[1:]):self.assertEqual(sequence.successor(w.episodes,'p','1',current)['sid'],target['sid'])
        self.assertIsNone(sequence.successor(w.episodes,'p','1',rows[-1]))

    def test_selected_middle_episode_controls_button_without_provider_requests(self):
        w=self.series();self.episodes(w)
        self.assertEqual(w.next_episode['sid'],'12')
        w.native(4);self.assertEqual(w.getControl(330).getSelectedPosition(),1)
        self.assertEqual(w.next_episode['sid'],'21');self.assertIn('Staffel 2',w.getControl(340).label)
        w.native(2);self.assertEqual(w.getFocusId(),340);self.assertEqual(w.next_episode['sid'],'21')
        w.native(4);self.assertEqual(w.getControl(330).getSelectedPosition(),1)
        with mock.patch.object(w.router,'_xc',side_effect=AssertionError('provider on D-pad')):
            w.native(3);self.assertEqual(w.next_episode['sid'],'12')
            w.getControl(330).selectItem(1);w.pump();self.assertEqual(w.next_episode['sid'],'21')
        self.assertFalse(self.builtins);sys.modules['utils'].http_get.assert_not_called()

    def test_explicit_next_click_starts_exactly_one_target_and_not_on_owner_ticks(self):
        w=self.series();self.episodes(w);w.native(3);self.assertEqual(w.getFocusId(),340)
        w.native(7);self.assertEqual(len(self.builtins),1);self.assertIn('sid=12',self.builtins[0])
        w.native(7);w.pump();w.pump();self.assertEqual(len(self.builtins),1)
        self.return_from_video(w);self.assertEqual(w.getFocusId(),330)
        self.assertEqual(w.visible_episodes[w.getControl(330).getSelectedPosition()]['sid'],'12')
        self.assertEqual(w.next_episode['sid'],'21');self.assertEqual(len(self.builtins),1)

    def test_next_crosses_season_and_returns_to_correct_episode_without_autoplay(self):
        for native in (False,True):
            w=self.series();self.episodes(w);w.native(4)
            w.native(2);self.assertEqual(w.getFocusId(),340);w.native(7);self.assertIn('sid=21',self.builtins[-1]);calls=len(self.builtins)
            self.return_from_video(w,native)
            self.assertEqual((w.mode,w.season,w.getFocusId()),('episodes',2,330))
            self.assertEqual(w.visible_episodes[w.getControl(330).getSelectedPosition()]['sid'],'21')
            self.assertIsNone(w.next_episode);self.assertFalse(w.getControl(340).visible)
            w.pump();self.assertEqual(len(self.builtins),calls)
            w.native(92);self.assertEqual(w.seasons[w.getControl(330).getSelectedPosition()],2);w.close()

    def test_natural_end_in_detail_preserves_anchor_then_manual_next(self):
        w=self.series();w._play(w.episodes[1],'episode');self.return_from_video(w)
        self.assertEqual(w.getFocusId(),300);self.assertEqual(w.next_episode['sid'],'21')
        calls=len(self.builtins);w.pump();self.assertEqual(len(self.builtins),calls)
        w.getControl(300).selectItem(next(i for i,a in enumerate(w.actions) if a[1]=='next_episode'));w.native(7)
        self.assertIn('sid=21',self.builtins[-1]);self.assertEqual(len(self.builtins),calls+1)

    def test_after_episode_list_back_detail_next_uses_last_selected_not_first_unseen(self):
        w=self.series();self.episodes(w);w.native(4);w.native(92)
        self.assertEqual(w.mode,'seasons');self.assertFalse(w.getControl(340).visible)
        w.native(92);self.assertEqual(w.mode,'detail');self.assertEqual(w.next_episode['sid'],'21')

    def test_latest_real_progress_selects_anchor_after_new_window_not_manual_seen_time(self):
        e=dict(pid='p',kind='episode',sid='12',series_id='1',season='1',episode='2')
        self.state.save_progress(e,300,1200)
        self.state.mark_episode('p',dict(sid='21',series_id='1',season=2),True)
        w=self.series();self.assertEqual(w.next_episode['sid'],'21')
        self.assertIn('continue_episode',[a[1] for a in w.actions])

    def test_series_end_no_button_no_detail_action_and_no_replay(self):
        w=self.series();self.episodes(w,2)
        self.assertIsNone(w.next_episode);self.assertNotIn(340,w._valid_focus())
        w.onClick(340);self.assertFalse(self.builtins)
        w.native(92);w.native(92);self.assertNotIn('next_episode',[a[1] for a in w.actions])

    def test_empty_single_and_missing_successor_never_invent_episode(self):
        for raw in ({},{'1':[dict(id='11',episode_num=1)]},{'0':[dict(id='1',episode_num=1)]}):
            w=self.series(raw);self.assertNotIn('next_episode',[a[1] for a in w.actions])
            w._play_next();self.assertFalse(self.builtins);w.close()

    def test_explicit_foreign_provider_identities_rejected_before_binding(self):
        sequence=importlib.import_module('media_sequence')
        rows=[dict(id='11',episode_num=1),dict(id='12',episode_num=2,series_id='other'),
              dict(id='13',episode_num=3,pid='other'),dict(id='14',episode_num=4,info=dict(portal_id='other')),
              dict(id='15',episode_num=5,info=dict(series_id='other')),dict(id='16',episode_num=6)]
        actual=sequence.records({'episodes':{'1':rows}},'p','1')
        self.assertEqual([e['sid'] for e in actual],['11','16'])
        self.assertEqual(sequence.successor(actual,'p','1',actual[0])['sid'],'16')
        self.assertEqual(sequence.records({'pid':'other','episodes':{'1':rows}},'p','1'),[])
        self.assertEqual(sequence.records({'info':{'series_id':'other'},'episodes':{'1':rows}},'p','1'),[])

    def test_ambiguous_ids_or_positions_invalid_numbers_and_specials_are_not_next(self):
        sequence=importlib.import_module('media_sequence')
        raw={'0':[dict(id='special',episode_num=1)],'1':[dict(id='11',episode_num=1),
             dict(id='same',episode_num=2),dict(id='same',episode_num=3),
             dict(id='a',episode_num=4),dict(id='b',episode_num=4),dict(id='bad',episode_num=1.2),
             dict(id='zero',episode_num=0),dict(id='negative',episode_num=-2),dict(id='16',episode_num=6)]}
        rows=sequence.records({'episodes':raw},'p','1');ordered=sequence.ordered(rows,'p','1')
        self.assertEqual([e['sid'] for e in ordered],['11','16'])
        self.assertIsNone(sequence.successor(rows,'p','1',dict(sid='same',series_id='1',season=1,episode=2)))

    def test_cross_portal_series_and_stale_episode_reference_fail_closed(self):
        w=self.series();sequence=importlib.import_module('media_sequence');anchor=w.episodes[0]
        for reference in (dict(anchor,pid='other'),dict(anchor,series_id='other'),dict(anchor,episode=9)):
            self.assertIsNone(sequence.successor(w.episodes,'p','1',reference))
            w._episode_refs['p','1']=reference;w._play_next()
        self.assertFalse(self.builtins)
        self.assertIsNone(sequence.successor(w.episodes,'other','1',anchor))
        self.assertIsNone(sequence.successor(w.episodes,'p','other',anchor))

    def test_stale_button_cannot_play_removed_or_foreign_target(self):
        w=self.series();self.episodes(w);self.assertEqual(w.next_episode['sid'],'12')
        w.episodes=[dict(e,pid='other') for e in w.episodes];w.onClick(340)
        self.assertFalse(self.builtins);self.assertFalse(w.getControl(340).visible)

    def test_resume_favourites_and_eyes_unchanged_by_manual_selection_and_back(self):
        self.state.toggle('p','series','1')
        self.state.save_progress(dict(pid='p',kind='episode',sid='11',series_id='1',season=1,episode=1),300,1200)
        self.state.mark_episode('p',dict(sid='12',series_id='1',season=1),True)
        before=self.state.read();w=self.series();self.episodes(w)
        self.assertTrue(w.getControl(330).items[0].getProperty('XCMate.Eye').endswith('eye_unseen.png'))
        self.assertTrue(w.getControl(330).items[1].getProperty('XCMate.Eye').endswith('eye_watched.png'))
        w.native(4);w.native(3);w.native(3);w.native(4);w.native(92);w.native(92)
        self.assertEqual(before,self.state.read());self.assertFalse(self.builtins)

    def test_invalid_provider_numbers_remain_excluded_after_window_reinit(self):
        w=self.series({'1':[dict(id='11',episode_num=1),dict(id='bad',episode_num=1.2),dict(id='12',episode_num=2)]})
        self.assertEqual(w.next_episode['sid'],'12');w.onInit()
        self.assertEqual(w.next_episode['sid'],'12');self.assertFalse(self.builtins)

    def test_stationary_owner_polls_do_not_resort_or_query_episodes_repeatedly(self):
        w=self.series();self.episodes(w)
        sequence=importlib.import_module('media_sequence')
        with mock.patch.object(sequence,'successor',wraps=sequence.successor) as lookup:
            for _ in range(50):w.pump()
            lookup.assert_not_called()
            w.native(4);self.assertEqual(lookup.call_count,1)
        self.assertFalse(self.builtins)

    def test_movies_and_flat_series_have_no_episode_next_or_button(self):
        w=self.media_window();w.native(7);self.settle(w)
        self.assertNotIn('next_episode',[a[1] for a in w.actions]);self.assertFalse(w.getControl(340).visible)
        w=self.series();w._detail_ready((dict(w.selected,series_flat=True),{}))
        self.assertNotIn('next_episode',[a[1] for a in w.actions]);self.assertFalse(self.builtins)


if __name__=='__main__':unittest.main()
