"""Native in-window search, private tracing and local EPG-now matching."""
import importlib
import sys
import unittest
from unittest import mock
from xcmate027_fixture import Fixture


class SearchTests(Fixture,unittest.TestCase):
    def query(self,w,text='Upload'):
        self.dialog.input.return_value=text;w._search();self.settle(w)

    def test_upload_never_closes_window_or_navigates_home_container(self):
        w=self.media_window();self.query(w)
        self.assertFalse(w._closed);self.assertEqual(w.mode,'search');self.assertFalse(self.builtins)
        self.assertEqual(w._search_data['vod']['total'],0)
        w.native(92);self.settle(w)
        self.assertEqual(w.mode,'landing');self.assertIn(w.getFocusId(),w._valid_focus())

    def test_cancel_and_repeated_search_keep_owner_and_do_not_apply_stale_results(self):
        w=self.media_window();before=w.getFocusId()
        self.dialog.input.return_value='';w._search()
        self.assertEqual(w.mode,'landing');self.assertEqual(w.getFocusId(),before)
        self.dialog.input.return_value='Upload';w._search()
        w.onClick(710);self.assertEqual(w.mode,'search')
        self.dialog.input.return_value='House';w._search();self.settle(w)
        self.assertEqual(w._search_query,'House');self.assertEqual(w._search_data['vod']['total'],100)
        self.assertFalse(w._closed);self.assertFalse(self.builtins)

    def test_tabs_real_counts_series_detail_and_back_restore_query(self):
        w=self.media_window();self.query(w,'House')
        self.assertEqual([w._search_data[k]['total'] for k in ('live','vod','series')],[1,100,3])
        w.onClick(702);self.settle(w)
        self.assertEqual(w._search_kind,'series');w.setFocusId(710);w.native(7);self.settle(w)
        self.assertEqual((w.mode,w.kind),('detail','series'))
        w.native(92);self.settle(w)
        self.assertEqual(w.mode,'search');self.assertEqual(w._search_query,'House')
        w.native(92);self.settle(w);self.assertEqual(w.kind,'vod')
        self.assertFalse(self.builtins)

    def test_metadata_and_playback_contracts_are_used_for_film_results(self):
        w=self.media_window();self.query(w,'House')
        w.setFocusId(710);w.native(7);self.settle(w)
        self.assertEqual(w.mode,'detail');self.assertEqual(w.getFocusId(),300)
        with mock.patch.object(w,'_play') as play:w.native(7)
        play.assert_called_once();self.assertFalse(self.builtins)

    def test_paging_has_exact_total_and_reaches_more_than_fifty(self):
        w=self.media_window();self.query(w,'House')
        self.assertEqual(len(w._search_rows),48)
        w.onClick(721);self.settle(w);self.assertEqual(w._search_offset,48)
        self.assertEqual(len(w._search_rows),48)
        w.onClick(721);self.settle(w);self.assertEqual(len(w._search_rows),4)
        w.onClick(720);self.settle(w);self.assertEqual(w._search_offset,48)

    def test_live_epg_now_match_uses_real_programme_and_manual_alias(self):
        guide=importlib.import_module('guide_store')
        guide.import_cache('p',{'canonical':[dict(channel='canonical',name='Upload episode',start_timestamp=self.now-60,stop_timestamp=self.now+3600)]})
        cfg=importlib.import_module('epg_sources')
        search=importlib.import_module('search_data')
        with mock.patch.object(cfg,'configuration',return_value={'mappings':{'2':'canonical'}}):
            result=search.search(self.portal,'Upload',kind='live',now=self.now)
        self.assertEqual(result['live']['total'],1)
        self.assertEqual(result['live']['rows'][0]['sid'],'2')
        self.assertTrue(result['live']['rows'][0]['_now_match'])
        self.assertEqual(result['live']['rows'][0]['_now_title'],'Upload episode')

    def test_missing_epg_does_not_invent_live_programmes(self):
        result=importlib.import_module('search_data').search(self.portal,'Upload',kind='live')
        self.assertEqual(result['live']['total'],0)
        self.assertEqual(result['live']['code'],'NO_EPG')

    def test_index_error_is_not_zero_results_and_never_runs_provider_http(self):
        from library_index import Reader,IndexReadError
        with mock.patch.object(Reader,'page',side_effect=IndexReadError('private')):
            result=importlib.import_module('search_data').search(self.portal,'Upload')
        self.assertIsNone(result['vod']['total']);self.assertEqual(result['vod']['code'],'INDEX_ERROR')
        sys.modules['utils'].http_get.assert_not_called()

    def test_special_characters_and_long_query_do_not_escape_local_index(self):
        w=self.media_window();self.query(w,'_%\\'+'x'*300)
        self.assertEqual(len(w._search_query),200)
        self.assertFalse(w._closed);self.assertFalse(self.builtins)

    def test_search_worker_failure_is_retryable_without_closing_window(self):
        w=self.media_window();self.dialog.input.return_value='Upload';w._search()
        w._query_failed(ValueError('PRIVATE'))
        self.assertFalse(w._search_loading);self.assertFalse(w._closed)

    def test_more_than_five_thousand_results_have_exact_count_and_last_page(self):
        entries=[dict(stream_id=str(i),category_id='a',name='Upload '+str(i)) for i in range(5105)]
        self.index.replace_catalog('p','vod',entries,self.catalogs['get_vod_categories'])
        result=importlib.import_module('search_data').search(self.portal,'Upload',kind='vod',offset=5088)
        self.assertEqual(result['vod']['total'],5105);self.assertEqual(len(result['vod']['rows']),17)

    def test_explicit_manual_mapping_does_not_fall_back_to_wrong_provider_epg(self):
        guide=importlib.import_module('guide_store')
        guide.import_cache('p',{'xml':[dict(channel='xml',name='Upload',start_timestamp=self.now-60,stop_timestamp=self.now+3600)]})
        cfg=importlib.import_module('epg_sources')
        with mock.patch.object(cfg,'configuration',return_value={'mappings':{'1':'missing','2':'missing','3':'missing'}}):
            result=importlib.import_module('search_data').search(self.portal,'Upload',kind='live',now=self.now)
        self.assertEqual(result['live']['total'],0)

    def test_action_route_opens_one_owner_without_search_container_update(self):
        self.router._handle=-1;self.router._params.update(action='global_search',q='Upload')
        import types
        with mock.patch.object(self.media,'open_search',return_value=types.SimpleNamespace(_search_live=None)) as open_search:
            self.routes.dispatch(self.router)
        open_search.assert_called_once();self.assertFalse(self.builtins)

    def test_root_search_back_defers_native_close_until_owner_tick(self):
        w=self.media_window();self.query(w);w._search_root=True;w._running=True
        w.native(92);self.assertFalse(w._closed);self.assertTrue(w._leaving)
        w._leave_after=0;w._owner_tick();self.assertTrue(w._closed)


if __name__=='__main__':unittest.main()
