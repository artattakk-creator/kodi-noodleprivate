"""Explicit selection after keyboard, resumable read-only guide, native re-init."""
import importlib,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture


class Search31Tests(Fixture,unittest.TestCase):
    def query(self,w,text='House'):
        self.dialog.input.return_value=text;w._search();self.settle(w)

    def test_root_search_keyboard_ok_does_not_select_first_result_or_stale_landing(self):
        w=self.media_window();w._search_root=True;self.query(w);w.onClick(700);self.settle(w)
        self.assertEqual(w.getFocusId(),700)
        w.onClick(710);w.onClick(120)
        self.assertIsNone(getattr(w,'_search_live',None));self.assertFalse(w._leaving);self.assertEqual(w.mode,'search')
        w.native(4);self.assertEqual(w.getFocusId(),710);w.native(7)
        self.assertTrue(w._leaving);self.assertIsNotNone(w._search_live)
        self.assertFalse(self.builtins)

    def test_native_reinit_while_keyboard_is_open_preserves_window_and_pending_request(self):
        w=self.media_window();original=w._generation
        def keyboard(*args,**kwargs):
            w.onInit();self.assertEqual(w._generation,original);return 'House'
        self.dialog.input.side_effect=keyboard;w._search();self.settle(w)
        self.assertFalse(w._closed);self.assertEqual(w.mode,'search');self.assertEqual(w.getFocusId(),701)
        before=w._generation;w.onInit();self.assertEqual(w._generation,before)
        self.assertEqual(w.mode,'search');self.assertFalse(w._closed);self.assertFalse(self.builtins)

    def test_reinit_during_slow_search_never_replaces_its_worker_with_landing(self):
        w=self.media_window();self.dialog.input.return_value='missing';w._search()
        future=w._pending_future;generation=w._generation;w.onInit()
        self.assertIs(w._pending_future,future);self.assertEqual(w._generation,generation)
        self.assertTrue(w._search_loading);self.settle(w)
        self.assertEqual(w.mode,'search');self.assertFalse(w._closed);self.assertFalse(w._leaving)
        self.assertEqual(w._search_data['live']['total'],0)

    def test_invisible_search_tab_defers_focus_and_ignores_native_result_click(self):
        w=self.media_window();self.query(w)
        original=w._valid_focus
        def lag(native=True):return [] if native else original(False)
        with mock.patch.object(w,'_valid_focus',side_effect=lag):
            w.setFocusId(700);self.assertEqual(w._focus_pending,('search',700));w.onClick(710)
        w._resume_focus();self.assertEqual(w.getFocusId(),700);self.assertFalse(w._leaving)

    def test_short_cache_after_old_two_second_cutoff_is_still_searched_for_all_channels(self):
        entries=[dict(stream_id=str(i),category_id='a',name='Channel '+str(i),epg_channel_id='missing') for i in range(135)]
        self.index.replace_catalog('p','live',entries,self.catalogs['get_live_categories'])
        module=importlib.import_module('search_data');clock=[0];seen=[]
        def cached(client,sid,now=None):
            seen.append(sid);clock[0]+=.3
            return dict(now='Exact programme' if sid in ('130','134') else '')
        cursor=None;partials=0
        with mock.patch('epg_views.cached_short_guide',side_effect=cached),mock.patch.object(module.time,'monotonic',side_effect=lambda:clock[0]):
            for _ in range(140):
                result=module.search(self.portal,'Exact programme',kind='live',now=self.now,incremental=True,continuation=cursor)
                cursor=result.get('_continuation')
                if cursor is None:break
                partials+=1;self.assertTrue(result['live']['partial'])
            else:self.fail('scan never finishes')
        self.assertGreater(partials,2);self.assertEqual(len(seen),135)
        self.assertEqual(result['live']['total'],2);self.assertEqual({r['sid'] for r in result['live']['rows']},{'130','134'})
        self.assertEqual(result['live']['code'],'READY');self.assertFalse(result['live']['partial'])
        self.client._get_json.assert_not_called()

    def test_progressive_completion_does_not_move_focus_to_results(self):
        entries=[dict(stream_id=str(i),category_id='a',name='House channel '+str(i)) for i in range(140)]
        self.index.replace_catalog('p','live',entries,self.catalogs['get_live_categories'])
        w=self.media_window();self.query(w);w.onClick(700);self.settle(w)
        self.assertEqual(w._search_data['live']['total'],140);self.assertEqual(w.getFocusId(),700)
        self.assertFalse(w._leaving);self.assertIsNone(getattr(w,'_search_live',None))


if __name__=='__main__':unittest.main()
