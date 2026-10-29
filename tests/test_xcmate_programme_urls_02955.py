"""Persistent exact event URLs; synthetic network boundaries only."""
import importlib,json,sys,time,unittest
from unittest import mock
from pathlib import Path
from xcmate027_fixture import Fixture,ADDON


class URLs55(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.urls=importlib.import_module('programme_urls55');self.art=importlib.import_module('programme_art46')
        self.events=importlib.import_module('programme_events46');self.db=importlib.import_module('programme_index46')
        self.options['programme_image_hosts55']='images.example.test'
        self.row=dict(sid='1',kind='live',name='Station',epg_channel_id='xml')
        self.event=self.events.describe(self.portal,self.row,dict(start=self.now-60,stop=self.now+600,title='Exact event'),canonical='xml')
        self.event.update(xmltv_image='https://images.example.test/exact.jpg',epg_source46='external:one',source_key46='external:one')

    def resolve(self,**kw):return self.urls.resolve(self.event,check=kw.pop('check',mock.Mock()),**kw)

    def test_saved_url_survives_restart_and_does_not_create_an_image_archive(self):
        first=self.resolve();self.assertEqual(first['code'],'READY')
        self.art._memory.clear();check=mock.Mock(side_effect=AssertionError('no repeat lookup'))
        again=self.resolve(check=check);check.assert_not_called()
        self.assertEqual(first['image'],again['image']);self.assertFalse(Path(self.art.root()).exists())
        self.assertTrue(Path(self.db.path()).exists());self.assertFalse(Path(importlib.import_module('guide_store').path()).exists())

    def test_reader_performs_no_dns_http_job_or_sql_write(self):
        self.resolve();self.art._memory.clear()
        with mock.patch.object(self.urls,'probe',side_effect=AssertionError('reader network')),mock.patch.object(self.urls,'enqueue',side_effect=AssertionError('reader job')),mock.patch('socket.getaddrinfo',side_effect=AssertionError('reader DNS')):
            for _ in range(25):self.assertEqual(self.art.cached(self.event)['image'],self.event['xmltv_image']+self.urls.OPTIONS)

    def test_same_persisted_url_is_used_for_widget_and_details(self):
        self.resolve()
        # Exercise the same public cache entry point used by both consumers.
        details=self.art.cached(self.event);widget=self.art.cached(dict(self.event))
        self.assertEqual(details['image'],widget['image']);self.assertEqual(details['binding55'],widget['binding55'])
        self.assertIn('programme_art46 import cached',(ADDON/'resources/lib/programme_window46.py').read_text())

    def test_source_or_mapping_collision_never_reuses_other_picture(self):
        saved=self.resolve()
        for fields in (dict(canonical='other'),dict(source_key46='external:two'),dict(pid='other'),dict(start=1),dict(title='Other title')):
            self.assertIsNone(self.urls.display(dict(self.event,**fields),saved))

    def test_expired_or_deleted_url_does_not_remain_a_valid_texture(self):
        self.resolve()
        with mock.patch.object(self.urls.time,'time',return_value=time.time()+90000):
            self.assertEqual(self.art.cached(self.event)['source'],'placeholder')

    def test_policy_blocks_downgrade_credentials_signed_query_private_hosts_and_headers(self):
        for url in ('http://images.example.test/x.jpg','https://u:p@images.example.test/x.jpg','https://images.example.test/x.jpg?token=secret','https://127.0.0.1/x.jpg','https://10.0.0.1/x.jpg','https://images.example.test/x.jpg|Authorization=secret','https://images.example.test/%0aCookie','https://images.example.test/../x.jpg','https://images.example.test:8443/x.jpg','https://unapproved.example.test/x.jpg','https://images.example.test/x.jpg#fragment'):
            self.assertFalse(self.urls.safe(url),url)
        self.assertTrue(self.urls.safe(self.event['xmltv_image']))

    def test_official_tmdb_image_path_is_accepted_without_api_key_or_lookup(self):
        self.assertTrue(self.urls.safe('https://image.tmdb.org/t/p/w780/Exact_1.jpg'))
        self.assertFalse(self.urls.safe('https://image.tmdb.org/3/search/movie'))

    def test_404_or_network_error_has_negative_ttl_and_neutral_picture(self):
        from media_sources43 import SourceError
        check=mock.Mock(side_effect=SourceError('HTTP_NOT_FOUND'))
        value=self.resolve(check=check);self.assertEqual(value['code'],'HTTP_NOT_FOUND')
        self.assertEqual(value['source'],'placeholder');self.resolve(check=check);self.assertEqual(check.call_count,1)

    def test_unapproved_host_is_honestly_blocked_before_network(self):
        self.event['xmltv_image']='https://not-approved.example.test/x.jpg';check=mock.Mock()
        value=self.resolve(check=check);check.assert_not_called();self.assertEqual(value['code'],'BLOCKED_IMAGE_HOST_OR_URL')

    def test_cancel_does_not_publish_partial_or_ready_url(self):
        self.assertIsNone(self.resolve(cancel=lambda:True));self.assertIsNone(self.db.art(self.event))

    def test_no_tmdb_lookup_on_boot_baseline_or_focus(self):
        self.urls._revisions.clear()
        self.assertFalse(self.urls.refreshed('p','r1'));self.assertFalse(self.urls.refreshed('p','r1'))
        self.assertTrue(self.urls.refreshed('p','r2'));self.assertTrue(self.urls.refreshed('p','r2'))
        self.event.pop('xmltv_image')
        with mock.patch('programme_match46.candidate',side_effect=AssertionError('boot metadata lookup')):
            self.assertEqual(self.resolve()['code'],'AWAITING_BACKGROUND_REFRESH')

    def test_opt_in_exact_lookup_can_follow_a_new_published_revision(self):
        self.event.pop('xmltv_image');self.resolve()
        candidate=dict(url='https://image.tmdb.org/t/p/w780/exact.jpg',source='tmdb_episode',match='EXACT_SEASON_EPISODE',attribution='TMDb · synthetic exact-episode proof')
        self.event.update(season=2,episode=3,subtitle='Exact episode')
        match=mock.Mock(return_value=candidate)
        value=self.resolve(allow_lookup=True,match=match)
        match.assert_called_once();self.assertEqual(value['match'],'EXACT_SEASON_EPISODE')
        self.assertEqual(value['tvspielfilm55'],'BLOCKED_NO_AUTHORIZED_API')

    def test_storage_busy_never_becomes_false_ready(self):
        with mock.patch.object(self.db,'art',return_value=None),mock.patch.object(self.db,'event'):
            value=self.resolve();self.assertEqual(value['code'],'PROGRAMME_DB_UNAVAILABLE');self.assertEqual(value['source'],'placeholder')

    def test_persisted_record_contains_matching_proof_ttl_attribution_and_identity(self):
        self.resolve();value=self.db.art(self.event)
        for key in ('binding55','key','source_url','source','match','attribution','resolved_at55','until','tvspielfilm55'):
            self.assertIn(key,value)
        self.assertEqual(value['source_url'],self.event['xmltv_image']);self.assertGreater(value['until'],value['resolved_at55'])

    def test_details_and_focus_paths_cannot_request_event_research(self):
        source=(ADDON/'resources/lib/programme_window46.py').read_text()
        self.assertNotIn('enqueue(',source);self.assertNotIn('write=True',source)
        source=(ADDON/'resources/lib/widget_notice46.py').read_text()
        self.assertNotIn('enqueue(',source)

    def test_host_approval_change_releases_only_the_targeted_negative_job(self):
        self.options['programme_image_hosts55']='';self.assertEqual(self.resolve()['code'],'BLOCKED_IMAGE_HOST_OR_URL')
        self.options['programme_image_hosts55']='images.example.test'
        self.assertEqual(self.resolve()['code'],'READY')

    def test_caller_credentials_in_image_path_are_rejected_before_preflight(self):
        self.event['xmltv_image']='https://images.example.test/SECRET/image.jpg'
        check=mock.Mock();self.assertEqual(self.resolve(check=check)['code'],'BLOCKED_CREDENTIAL_URL');check.assert_not_called()

    def test_corrupt_ttl_is_a_safe_cache_miss_and_not_a_home_exception(self):
        value=self.resolve()
        for until in ('later',None,[],float('inf')):
            self.assertIsNone(self.urls.display(self.event,dict(value,until=until)))

    def test_private_dns_answer_is_blocked_before_any_image_connection(self):
        from media_sources43 import SourceError
        with mock.patch('socket.getaddrinfo',return_value=[(2,1,6,'',('10.0.0.2',443))]),mock.patch('download_redirect._connect') as connect:
            with self.assertRaises(SourceError):self.urls.probe(self.event['xmltv_image'])
        connect.assert_not_called()

    def test_404_preflight_closes_response_and_never_reads_image_body(self):
        from media_sources43 import SourceError
        response=mock.Mock(status=404)
        with mock.patch('download_redirect.addresses',return_value=['93.184.216.34']),mock.patch('download_redirect._connect',return_value=response):
            with self.assertRaises(SourceError) as error:self.urls.probe(self.event['xmltv_image'])
        self.assertEqual(error.exception.code,'HTTP_NOT_FOUND');response.read.assert_not_called();response.close.assert_called_once()

    def test_positive_png_and_jpeg_headers_are_validated_without_archiving(self):
        import io
        from PIL import Image
        for kind,mime in [('PNG','image/png'),('JPEG','image/jpeg')]:
            output=io.BytesIO();Image.new('RGB',(160,90)).save(output,kind);stream=io.BytesIO(output.getvalue())
            response=mock.Mock(status=200,headers={'Content-Type':mime});response.read.side_effect=stream.read
            with mock.patch('download_redirect.addresses',return_value=['93.184.216.34']),mock.patch('download_redirect._connect',return_value=response):
                self.urls.probe(self.event['xmltv_image'])
            response.close.assert_called_once();self.assertFalse(Path(self.art.root()).exists())

    def test_real_queue_deduplicates_and_bounds_pending_events_without_native_threads(self):
        import importlib.util,types
        spec=importlib.util.spec_from_file_location('isolated_url_queue55',self.urls.__file__)
        queue=importlib.util.module_from_spec(spec);spec.loader.exec_module(queue)
        queue._thread=types.SimpleNamespace(is_alive=lambda:True)
        for i in range(50):queue.enqueue(dict(self.event,key=str(i)))
        self.assertEqual(len(queue._pending),24);self.assertEqual(len(queue._queue),24)
        self.assertFalse(queue.enqueue(dict(self.event,key='0')))

    def test_stale_producer_ram_cannot_replace_a_newer_committed_online_reference(self):
        saved=self.resolve()
        stale=dict(saved,source='placeholder',code='NO_IMAGE',image=self.event['placeholder'])
        self.art.remember(self.event['key'],stale)
        self.assertTrue(self.db.publish([self.event],include_art=False))
        current=self.db.art(self.event)
        self.assertEqual(current['code'],'READY');self.assertEqual(current['source_url'],saved['source_url'])
