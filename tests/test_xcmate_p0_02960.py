"""#284: optional private TMDB and real existing Home source contracts."""
import importlib
import io
import json
import time
import unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture
from xcmate050_fixture import Fixture50


class TMDB60(Fixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.client = importlib.import_module('tmdb_connection60')
        self.client._cooldowns.clear()
        self.options.update(tmdb_read_token43='synthetic-not-a-real-token', tmdb_research43=True, programme_tmdb46=True)

    def response(self, status=200, data=None):
        response = mock.Mock(status=status, headers={'Content-Type': 'application/json'})
        stream = io.BytesIO(json.dumps(data if data is not None else {'images': {'secure_base_url': 'https://image.tmdb.org/t/p/', 'backdrop_sizes': ['w780']}}).encode())
        response.read.side_effect = stream.read
        return response

    def run_connection(self, status=200, data=None):
        with mock.patch('download_redirect.addresses', return_value=['93.184.216.34']), mock.patch('download_redirect._connect', return_value=self.response(status, data)) as connect:
            code = self.client.test_connection()
        return code, connect

    def test_configuration_uses_one_verified_https_bearer_request(self):
        code, connect = self.run_connection()
        self.assertEqual(code, 'TMDB_OK')
        self.assertEqual(connect.call_count, 1)
        self.assertEqual(connect.call_args.args[0], 'https://api.themoviedb.org/3/configuration')
        self.assertEqual(connect.call_args.args[2]['Authorization'], 'Bearer ' + self.options['tmdb_read_token43'])
        self.assertNotIn(self.options['tmdb_read_token43'], code)

    def test_missing_token_performs_no_network(self):
        self.options['tmdb_read_token43'] = ''
        with mock.patch('media_sources43.get', side_effect=AssertionError('no token')):
            self.assertEqual(self.client.test_connection(), 'TOKEN_MISSING')

    def test_401_403_and_429_have_specific_safe_codes(self):
        for status, expected in ((401, 'HTTP_AUTH'), (403, 'HTTP_AUTH'), (429, 'HTTP_RATE_LIMIT')):
            self.client._cooldowns.clear()
            self.assertEqual(self.run_connection(status)[0], expected)

    def test_rate_limit_is_shared_between_events_without_retry_storm(self):
        self.assertEqual(self.run_connection(429)[0], 'HTTP_RATE_LIMIT')
        with mock.patch('media_sources43.get', side_effect=AssertionError('cooldown bypassed')):
            self.assertEqual(self.client.test_connection(), 'HTTP_RATE_LIMIT')
        self.assertLessEqual(len(self.client._cooldowns), 8)

    def test_timeout_dns_tls_and_invalid_json_do_not_disclose_error_text(self):
        from media_sources43 import SourceError
        for code, expected in [('TIMEOUT', 'TIMEOUT'), ('DNS_ERROR', 'NETWORK_ERROR'), ('TLS_ERROR', 'NETWORK_ERROR'), ('INVALID_JSON', 'INVALID_RESPONSE')]:
            with mock.patch('media_sources43.get', side_effect=SourceError(code)):
                self.assertEqual(self.client.test_connection(), expected)
        self.assertEqual(self.run_connection(data={'success': True})[0], 'INVALID_RESPONSE')

    def test_untrusted_origin_and_api_key_url_are_refused(self):
        from media_sources43 import SourceError
        for url in ('http://api.themoviedb.org/3/configuration', 'https://foreign.example.test/3/configuration', 'https://api.themoviedb.org/3/configuration?api_key=synthetic'):
            with self.assertRaises(SourceError), mock.patch('media_sources43.get', side_effect=AssertionError('unsafe origin')):
                self.client.request(url, token='synthetic')

    def test_retry_after_longer_than_five_minutes_is_respected(self):
        response = self.response(429)
        response.headers['Retry-After'] = '1800'
        with mock.patch('download_redirect.addresses', return_value=['93.184.216.34']), mock.patch('download_redirect._connect', return_value=response):
            self.assertEqual(self.client.test_connection(), 'HTTP_RATE_LIMIT')
        deadline = next(iter(self.client._cooldowns.values()))[0]
        self.assertGreater(deadline - time.monotonic(), 1790)

    def test_connection_ui_keeps_http_off_the_dialog_owner_thread(self):
        import threading
        import sys
        owner = threading.get_ident()
        seen = []
        gui = sys.modules['xbmcgui']
        xbmc = sys.modules['xbmc']
        progress = mock.Mock()
        progress.iscanceled.return_value = False
        monitor = mock.Mock()
        monitor.waitForAbort.side_effect = lambda seconds: time.sleep(.001)
        def perform(cancel):
            seen.append(threading.get_ident())
            return 'TMDB_OK'
        with mock.patch.object(gui, 'DialogProgress', return_value=progress, create=True), mock.patch.object(xbmc, 'Monitor', return_value=monitor), mock.patch.object(self.client, 'test_connection', side_effect=perform):
            self.client.launch()
        self.assertEqual(len(seen), 1)
        self.assertNotEqual(seen[0], owner)
        progress.close.assert_called_once()

    def test_enabling_local_token_invalidates_old_negative_url_record(self):
        events = importlib.import_module('programme_events46')
        urls = importlib.import_module('programme_urls55')
        channel = dict(sid='1', name='Station', kind='live')
        event = events.describe(self.portal, channel, dict(self.movie(), start=self.now - 10, stop=self.now + 600))
        self.options['programme_tmdb46'] = False
        old = urls.resolve(event, allow_lookup=True)
        self.assertEqual(old['source'], 'placeholder')
        self.options['programme_tmdb46'] = True
        self.assertIsNone(urls.display(event, old))

    def movie(self):
        return dict(title='Unique synthetic film', genre='Spielfilm', year=2024)

    def search(self, rows):
        return dict(total_pages=1, total_results=len(rows), results=rows)

    def row(self, ident=42, year='2024'):
        return dict(id=ident, title='Unique synthetic film', release_date=year + '-01-01', adult=False)

    def test_movie_requires_unique_complete_search_and_independent_title_year_details(self):
        match = importlib.import_module('programme_match46')
        details = dict(self.row(), backdrop_path='/exact.jpg')
        with mock.patch('media_sources43.get', side_effect=[self.search([self.row()]), details]) as get:
            value = match.candidate(self.movie())
        self.assertEqual(value['match'], 'EXACT_TITLE_YEAR')
        self.assertEqual(value['url'], 'https://image.tmdb.org/t/p/w500/exact.jpg')
        self.assertEqual(get.call_count, 2)
        for payload in (self.search([self.row(), self.row(43)]), dict(self.search([self.row()]), total_pages=2), self.search([self.row(year='2023')])):
            with mock.patch('media_sources43.get', return_value=payload):
                self.assertIsNone(match.candidate(self.movie()))
        with mock.patch('media_sources43.get', side_effect=[self.search([self.row()]), dict(details, title='Wrong film')]):
            self.assertIsNone(match.candidate(self.movie()))

    def test_episode_requires_exact_parent_and_season_episode_subtitle(self):
        match = importlib.import_module('programme_match46')
        event = dict(title='Exact synthetic series', season=2, episode=3, subtitle='Exact episode')
        search = self.search([dict(id=12, name=event['title'], first_air_date='2020-01-01')])
        episode = dict(id=15, season_number=2, episode_number=3, name='Exact episode', still_path='/episode.png')
        with mock.patch('media_sources43.get', side_effect=[search, episode]):
            self.assertEqual(match.candidate(event)['match'], 'EXACT_SEASON_EPISODE')
        for changed in (dict(episode, episode_number=4), dict(episode, name='Wrong episode'), dict(episode, still_path='/../wrong.jpg')):
            with mock.patch('media_sources43.get', side_effect=[search, changed]):
                self.assertIsNone(match.candidate(event))

    def test_unclassified_news_empty_title_or_disabled_feature_never_searches(self):
        match = importlib.import_module('programme_match46')
        with mock.patch('media_sources43.get', side_effect=AssertionError('unverified match')):
            self.assertIsNone(match.candidate(dict(title='News', genre='Nachrichten')))
            self.assertIsNone(match.candidate(dict(title='', genre='Film', year=2024)))
            self.options['programme_tmdb46'] = False
            self.assertIsNone(match.candidate(self.movie()))

    def test_tmdb_image_is_local_persistent_and_shared_by_details_and_widget(self):
        events = importlib.import_module('programme_events46')
        urls = importlib.import_module('programme_urls55')
        art = importlib.import_module('programme_art46')
        channel = dict(sid='1', name='Synthetic station', epg_channel_id='xml', kind='live')
        event = events.describe(self.portal, channel, dict(self.movie(), start=self.now - 60, stop=self.now + 600), canonical='xml')
        event.update(self.movie())
        from PIL import Image
        png = io.BytesIO()
        Image.new('RGB', (160, 90), (20, 80, 130)).save(png, 'PNG')
        Path(art.root()).mkdir(exist_ok=True)
        responses = [self.search([self.row()]), dict(self.row(), backdrop_path='/exact.jpg'), png.getvalue()]
        with mock.patch('media_sources43.get', side_effect=responses) as get, mock.patch.object(art, 'space'):
            result = urls.resolve(event, allow_lookup=True)
        self.assertEqual(result['code'], 'READY')
        self.assertEqual(result['source'], 'tmdb_movie')
        self.assertEqual(get.call_count, 3)
        self.assertTrue(Path(result['image']).is_file())
        art._memory.clear()
        with mock.patch('media_sources43.get', side_effect=AssertionError('focus/restart network')):
            self.assertEqual(art.cached(event)['image'], result['image'])
            self.assertEqual(urls.resolve(event, allow_lookup=True)['image'], result['image'])
        self.assertIn('not endorsed', result['attribution'])
        self.assertFalse(Path(importlib.import_module('guide_store').path()).exists())


class Home60(Fixture50, unittest.TestCase):
    def test_nested_xtream_url_does_not_select_live_layout_for_foreign_plugin(self):
        import xml.etree.ElementTree as E
        compiler = self.native_reference().Template()
        data = self.skinmod.patch('shortcuts/template.xml', (self.skin / 'shortcuts/template.xml').read_bytes())
        tree = E.fromstring(data)
        live = next(n for n in tree.iter('include') if n.get('content') == 'XCMate50.LiveRow')
        props = dict(widgetPath1='plugin://foreign.addon/?url=plugin://plugin.video.xtreammate/?action=widget_live_start_group&pid=p')
        # Evaluate the exact selection expression with the same native
        # Skinshortcuts compiler. No binding or source URL is edited.
        target = E.Element('controls')
        condition = E.SubElement(target, 'include', content='XCMate50.LiveRow', condition=live.get('condition'))
        compiler.replaceElements(target, None, None, [], props)
        self.assertIn('[false]', condition.get('condition'))

    def test_complete_start_group_preserves_order_without_pinning_or_foreign_group(self):
        home = importlib.import_module('widget_home50')
        self.portal['start_stream_id'] = '50'
        self.index.import_group('p', 'live', 'a', [dict(stream_id=str(i), category_id='a', name='Station ' + str(i), epg_channel_id='xml' + str(i)) for i in range(188)])
        rows, code = home.rows(self.portal)
        self.assertEqual(code, 'READY')
        self.assertEqual([r['sid'] for r in rows], [str(i) for i in range(188)])

    def test_old_saved_live_url_without_home_flag_reaches_complete_directory(self):
        self.router._params.update(action='widget_live_start_group')
        self.router._params.pop('home50', None)
        dispatch = importlib.import_module('widget_entry46').dispatch
        with mock.patch('widget_home50.render') as render, mock.patch('app_routes.widget', side_effect=AssertionError('legacy branch')):
            self.assertTrue(dispatch(self.router))
        render.assert_called_once()

    def test_opt_in_adapter_accepts_existing_url_without_home_flag_and_has_real_diff(self):
        before = self.skin_bytes()
        plan = self.skinmod.prepare(self.skin)
        self.assertEqual(self.skin_bytes(), before)
        template = (self.tx.folder() / plan['id'] / 'candidate.3').read_text()
        self.assertNotIn('home50=1', template)
        self.assertIn('XCMate50.LiveRow', template)
        preview = importlib.import_module('widget_skin60').preview(plan)
        self.assertIn('--- xml/IncludesHomeWidgets.xml', preview)
        self.assertIn('+', preview)
        with self.assertRaises(PermissionError):
            self.skinmod.apply(plan['id'], self.skin)

    def test_live_consumer_is_verified_from_generated_own_include_and_sampled(self):
        self.skinmod.apply(self.skinmod.prepare(self.skin)['id'], self.skin, confirmed=True)
        rows = list(self.saved) + [['mainmenu', '10000', key + '.2', value] for key, value in dict(widget='Addon', widgetName='Live', widgetType='videos', widgetTarget='videos', widgetPath=self.binding.source('live', 'p')).items()]
        self.prop.write_text(repr(rows))
        generated = self.skin / 'xml/script-skinshortcuts-includes.xml'
        generated.write_text('<includes><include content="XCMate50.LiveRow"><param name="widgetid" value="2530"/><param name="widgetPath" value="plugin://plugin.video.xtreammate/?action=widget_live_start_group&amp;pid=p"/><param name="widgetTarget" value="videos"/><param name="contentStyle" value="normal"/></include></includes>')
        value = importlib.import_module('widget_consumer58').inspect(self.profile, self.skin, generated, 'p', lambda cid: dict(visible=True, items=88))
        self.assertEqual(value['kinds']['live']['binding'], 'BINDING_PRESENT')
        self.assertEqual(value['kinds']['live']['consumer'], 'GENERATED_CONSUMER_PRESENT')
        self.assertEqual(value['kinds']['live']['control_ids59'], [2530])
        self.assertEqual(value['kinds']['live']['home'], 'HOME_ITEMS_PRESENT')
        self.assertEqual(value['kinds']['live']['pixels'], 'NOT_TESTED')
