"""Real 2,905-channel index: names-first and one prepared local publication."""
import importlib,sys,time,unittest
from unittest import mock
import xcmate027_fixture as model


class SearchPerf39(model.Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.data=importlib.import_module('search_data');self.data._PREPARED.clear()
        rows=[dict(stream_id=str(i),category_id='a',epg_channel_id='special' if i==2905 else 'xml'+str(i%455),name='Rock channel' if i%600==0 or i==2904 else 'Channel '+str(i)) for i in range(1,2906)]
        self.index.replace_catalog('p','live',rows,self.catalogs['get_live_categories'])
        cache={'xml'+str(i):[dict(name='Current '+str(i),start_timestamp=self.now-60,stop_timestamp=self.now+300)] for i in range(455)}
        cache['special']=[dict(name='Rock programme',start_timestamp=self.now-60,stop_timestamp=self.now+300)]
        importlib.import_module('guide_store').import_cache('p',cache,revision='pub1')

    def test_names_publish_before_any_epg_or_media_work_even_from_movie_tab(self):
        with mock.patch.object(self.data.LiveSearch,'_prepare',side_effect=AssertionError('EPG before names')),mock.patch.object(self.index.Reader,'page',side_effect=AssertionError('media before names')):
            result=self.data.search(self.portal,'Rock','vod',incremental=True,now=self.now)
        self.assertEqual(len(result['live']['rows']),5);self.assertTrue(result['live']['partial'])
        self.assertEqual(result['vod']['code'],'INDEX_PENDING')

    def test_twenty_short_cache_revisions_do_not_restart_inflight_channel_cursor(self):
        result=self.data.search(self.portal,'Rock',incremental=True,now=self.now);cursor=result['_cursor']
        for n in range(20):
            self.properties['XCMate.ShortGuideRevision.p']=str(n)
            self.assertTrue(cursor.valid());self.assertEqual(cursor.phase,'prepare')
        while not cursor.done:cursor.step()
        self.assertEqual(cursor.counts['channels'],2905);self.assertEqual(cursor.slices,12)

    def test_second_query_reuses_aliases_current_epg_and_catalogue_publication(self):
        reader=self.index.Reader('p');first=self.data.LiveSearch(self.portal,'Rock',reader,self.now)
        first.step();first._prepare()
        second=self.data.LiveSearch(self.portal,'Channel',reader,self.now)
        with mock.patch.object(self.data,'_now_events',side_effect=AssertionError('repeated EPG scan')),mock.patch.object(reader,'_query',side_effect=AssertionError('repeated catalog scan')):
            # Name SQL is intentionally separate; prepare can reuse the snapshot.
            second._prepare()
        self.assertIs(second.channels,first.channels);self.assertIs(second.events,first.events)

    def test_real_publication_or_mapping_change_invalidates_cursor(self):
        result=self.data.search(self.portal,'Rock',incremental=True,now=self.now);cursor=result['_cursor'];cursor.step()
        store=importlib.import_module('guide_store')
        store.import_cache('p',{'xml':[dict(name='New',start_timestamp=self.now-60,stop_timestamp=self.now+300)]},revision='pub2')
        self.assertFalse(cursor.valid())

    def test_event_boundary_expires_cached_programme_matches(self):
        reader=self.index.Reader('p');cursor=self.data.LiveSearch(self.portal,'Rock',reader,self.now)
        while not cursor.done:cursor.step()
        with mock.patch.object(self.data.time,'time',return_value=self.now+301):self.assertFalse(cursor.valid())

    def test_real_cold_and_warm_scan_metrics_are_reported_without_android_claim(self):
        measurements=[]
        for index,query in enumerate(('Rock','Rock')):
            started=time.perf_counter();value=self.data.search(self.portal,query,'live',incremental=True,now=self.now)
            first=time.perf_counter()-started;cursor=value['_cursor']
            while not cursor.done:cursor.step()
            measurements.append(dict(query_kind='cold' if index==0 else 'warm',first_names_ms=round(first*1000,3),total_ms=round((time.perf_counter()-started)*1000,3),scanned=cursor.position,results=len(cursor.result)))
        print('SEARCH39_HOST',measurements)
        self.assertTrue(all(m['scanned']==2905 for m in measurements))
