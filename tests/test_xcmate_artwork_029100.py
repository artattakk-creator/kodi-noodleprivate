"""Artwork transport and derived UI regressions for Issue #498."""
from concurrent.futures import ThreadPoolExecutor
import importlib
import threading
import unittest
from unittest import mock
import xml.etree.ElementTree as ET
from pathlib import Path

from xcmate027_fixture import Fixture


class Artwork100(Fixture, unittest.TestCase):
    def test_agent_tmdb_has_the_same_brand_and_verified_rating_rules(self):
        from programme_actions88 import tmdb_source, rating
        self.assertTrue(tmdb_source('agent_tmdb'))
        self.assertFalse(tmdb_source('agent_tvmaze'))
        self.assertTrue(rating(dict(source='agent_tmdb', vote_average88=8.0, vote_count88=10)))
        self.assertEqual(rating(dict(source='agent_tmdb', vote_average88=8.0)), '')

    def test_repeated_tmdb_request_shares_pending_http_and_returns_owned_json(self):
        connection = importlib.import_module('tmdb_connection60')
        entered = threading.Event()
        release = threading.Event()
        second_started = threading.Event()
        url = 'https://api.themoviedb.org/3/search/tv?query=Example'
        def transport(*args, **kwargs):
            entered.set()
            if not release.wait(2):
                raise AssertionError('test did not release transport')
            return {'results': [{'id': 23}]}
        def second():
            second_started.set()
            return connection.request(url, token='synthetic')
        with mock.patch('media_sources43.get', side_effect=transport) as fetch:
            with ThreadPoolExecutor(max_workers=2) as pool:
                first = pool.submit(connection.request, url, token='synthetic')
                self.assertTrue(entered.wait(2))
                another = pool.submit(second)
                self.assertTrue(second_started.wait(2))
                release.set()
                first.result()['results'][0]['id'] = 42
                self.assertEqual(another.result(), {'results': [{'id': 23}]})
            self.assertEqual(fetch.call_count, 1)

    def test_tmdb_cancellation_and_configuration_test_bypass_cached_success(self):
        connection = importlib.import_module('tmdb_connection60')
        from media_sources43 import SourceError
        base = 'https://api.themoviedb.org/3'
        def transport(*args, **kwargs):
            if kwargs['cancel']():
                raise SourceError('CANCELLED')
            return {'results': []}
        with mock.patch('media_sources43.get', side_effect=transport) as fetch:
            url = base + '/search/movie?query=Artwork'
            connection.request(url, token='synthetic')
            with self.assertRaisesRegex(SourceError, 'CANCELLED'):
                connection.request(url, token='synthetic', cancel=lambda: True)
            connection.request(url, token='synthetic')
            connection.request(base + '/configuration', token='synthetic')
            connection.request(base + '/configuration', token='synthetic')
            self.assertEqual(fetch.call_count, 3)

    def test_tmdb_missing_image_metadata_uses_short_negative_cache_per_token(self):
        connection = importlib.import_module('tmdb_connection60')
        from media_sources43 import SourceError
        url = 'https://api.themoviedb.org/3/tv/100/season/2/episode/3'
        with mock.patch('media_sources43.get', side_effect=SourceError('HTTP_NOT_FOUND')) as fetch:
            for token in ('synthetic', 'synthetic', 'other-synthetic'):
                with self.assertRaisesRegex(SourceError, 'HTTP_NOT_FOUND'):
                    connection.request(url, token=token)
            self.assertEqual(fetch.call_count, 2)

    def test_premium_retains_explicit_profile_colours_and_changes_xml_revision(self):
        appearance = importlib.import_module('appearance')
        theme = {'revision': 'space-premium/1.0.0-synthetic', 'spec': {
            'palette': {'background': '061322', 'text': 'E6F5FF', 'accent': '159FEA',
                        'focus': '42D9FF', 'secondary': '88A6BE'}, 'assets': {}}}
        def xml():
            from theme_store import asset
            with mock.patch('theme_render.snapshot', return_value=theme), mock.patch('theme_store.asset', wraps=asset):
                path = appearance.window_source('XCMateMedia.xml')
            target = Path(path) / 'resources/skins/Default/720p/XCMateMedia.xml'
            return path, ET.parse(target)
        previous, before = xml()
        self.assertEqual(before.findtext("./controls/control[@id='101']/textcolor"), 'FF159FEA')
        appearance.save(dict(appearance.read(), accent='FF8F00', font='very_large'))
        current, updated = xml()
        self.assertEqual(updated.findtext("./controls/control[@id='101']/textcolor"), 'FFFF8F00')
        self.assertNotEqual(current, previous)
        self.assertEqual(appearance.read()['font'], 'very_large')

    def test_logo_editor_previews_provider_original_even_with_active_override(self):
        editor = importlib.import_module('logo_editor96')
        row = {'sid': '1', 'name': 'Sender'}
        with mock.patch('menu_icons45.select', side_effect=[0,-1]), \
             mock.patch('artwork_ui.job', side_effect=lambda fn: fn(lambda: False, lambda *a: None)), \
             mock.patch('logo_manifest86.read', side_effect=lambda portal, rows, **kw:
                        {'1': '/provider.png' if kw.get('with_overrides') is False else '/override.png'}), \
             mock.patch('artwork_ui._render') as render:
            editor.edit(self.portal, row)
        render.assert_called_once_with('/provider.png')

    def test_storage_capacity_keeps_exact_bytes_and_redacted_volume(self):
        import storage_artwork96
        facts = dict(free=67_108_865, total=1_073_741_824, volume82='abc123abc123',
                     mount82='ext4', capacity82='SAME_VOLUME_VERIFIED')
        with mock.patch('art_storage82.capacity', return_value=facts):
            cache = storage_artwork96.status()['classes'][0]
        self.assertEqual(cache.get('free_bytes'), 67_108_865)
        self.assertEqual(cache.get('volume'), 'abc123abc123')
        self.assertEqual(cache.get('mount'), 'ext4')

    def test_feed_art_is_selected_without_private_tmdb_lookup(self):
        self.options.update(epg_agent_enabled=True, programme_tmdb46=True, tmdb_research43=True)
        from programme_events46 import describe
        from programme_urls55 import resolve
        event = describe(self.portal, {'sid': '1', 'name': 'Sender'}, {
            'title': 'Serie', 'start': self.now - 3, 'stop': self.now + 3600})
        image = 'https://image.tmdb.org/t/p/w1280/agent100.jpg'
        event['agent_art'] = {'backdrop': {'url': image, 'source': 'agent_tmdb',
                                          'provider': 'tmdb', 'match': 'EXACT_EVENT',
                                          'attribution': 'XCMate EPG Agent · TMDB'}}
        from io import BytesIO
        from PIL import Image
        buffer = BytesIO()
        Image.new('RGB', (1280, 720), '#101520').save(buffer, 'PNG')
        with mock.patch('home_schedule75.applicable', return_value=True), \
             mock.patch('programme_match46.candidate', side_effect=AssertionError('unneeded lookup')):
            result = resolve(event, allow_lookup=True, url_mode69=True, check=lambda url, **kw:
                             dict(url=url, width=1280, height=720, decoded77=True, _body81=buffer.getvalue()))
        self.assertEqual(result['source'], 'agent_tmdb')
        self.assertEqual(result['role81'], 'backdrop')
        self.assertEqual(result['source_url'], image)

    def test_feed_poster_is_not_misclassified_as_a_hero_backdrop(self):
        from hero_art86 import classify
        result = classify({'source': 'agent_tmdb', 'role81': 'poster',
                           'image_width77': 1000, 'image_height77': 1500})
        self.assertEqual(result[0] if result else None, 'official_poster')
        self.assertIsNone(classify({'source': 'agent_tmdb', 'role81': 'thumb',
                                    'image_width77': 1280, 'image_height77': 720}))

    def test_agent_source_opt_out_invalidates_previously_eligible_local_reference(self):
        from programme_image69 import eligible
        self.options.update(epg_agent_enabled=True, programme_tvmaze67=True)
        art = {'code': 'READY', 'source': 'agent_tvmaze', 'image': '/verified.jpg'}
        self.assertTrue(eligible(art))
        self.options['programme_tvmaze_optout77'] = True
        self.assertFalse(eligible(art))
        self.options.update(programme_tvmaze_optout77=False, epg_agent_enabled=False)
        self.assertFalse(eligible(art))

    def test_feed_logo_is_decoded_on_worker_then_available_after_receipt_loss(self):
        from io import BytesIO
        from PIL import Image
        import sys
        from types import SimpleNamespace
        import logo_manifest86
        import station_logos88

        raw = BytesIO()
        Image.new('RGBA', (72, 32), (54, 90, 110, 150)).save(raw, 'PNG')
        row = {'sid': '1', 'name': 'Sender'}
        agent = SimpleNamespace(logos=lambda pid, sids: {'1': 'https://static.example.org/icon.png'})
        with mock.patch.dict(sys.modules, epg_agent100_art=agent), \
             mock.patch('programme_transport77.verified', return_value={'_body81': raw.getvalue()}) as fetch:
            self.options['epg_agent_enabled'] = True
            self.assertNotIn('1', logo_manifest86.read(self.portal, [row]))
            station_logos88.prepare(self.portal, [row])
            saved = logo_manifest86.read(self.portal, [row])['1']
            self.assertEqual(Path(saved).read_bytes(), raw.getvalue())
            self.properties.clear()  # Simulate lost volatile handoffs across restart.
            station_logos88.prepare(self.portal, [row])
            self.assertEqual(logo_manifest86.read(self.portal, [row])['1'], saved)
            self.assertNotIn('1', logo_manifest86.read(self.portal, [row], with_agent=False))
            self.options['epg_agent_enabled'] = False
            self.assertNotIn('1', logo_manifest86.read(self.portal, [row]))
        self.assertEqual(fetch.call_count, 1)

    def test_artwork_source_switch_preserves_explicit_global_image_choice(self):
        import artwork_sources96
        import storage_policy92
        from types import SimpleNamespace

        with mock.patch('settings_guard96.write', return_value=SimpleNamespace(code='READY')), \
             mock.patch('programme_refresh63.request'):
            storage_policy92.choose('no')
            artwork_sources96.choose('xmltv', True)
        self.assertEqual(storage_policy92.read()['image_epg'], 'no')

    def test_installed_extra_theme_can_be_activated_offline(self):
        import theme_ui
        package = {'spec': {'id': 'other-theme', 'name': 'Other theme', 'version': '1.0.0'},
                   'revision': 'other-theme/1.0.0-synthetic'}
        with mock.patch('theme_ui.job', side_effect=lambda fn: fn(lambda: False)), \
             mock.patch('theme_store.installed', return_value=[package]), \
             mock.patch('theme_render.snapshot', return_value=None), \
             mock.patch('menu_icons45.select', side_effect=[5, 0, 0, -1]), \
             mock.patch('theme_store.select') as activate:
            theme_ui.manage()
        activate.assert_called_once_with(package['revision'])

    def test_tvmaze_metadata_from_two_consumers_reuses_same_search_reply(self):
        from programme_tvmaze67 import candidate84
        from programme_tvmaze85 import search
        from media_sources43 import SourceError
        self.options['programme_tvmaze67'] = True
        event = {'title': 'Synthetic Shared Maze', 'genre': 'series', 'year': 2020,
                 'season': 2, 'episode': 3}
        with mock.patch('media_sources43.get', return_value=[]) as fetch:
            with self.assertRaisesRegex(SourceError, 'NO_MATCH'):
                candidate84(event)
            self.assertEqual(search(event), ([], True))
        self.assertEqual(fetch.call_count, 1)

    def test_validated_public_programme_image_body_is_reused_across_events(self):
        from programme_urls55 import probe
        url = 'https://image.tmdb.org/t/p/w1280/two-events100.jpg'
        image = dict(url=url, width=1280, height=720, decoded77=True, _body81=b'synthetic-decoded-body')
        with mock.patch('programme_transport77.verified', return_value=image) as fetch:
            first = probe(url)
            again = probe(url)
            self.assertEqual(again, first)
            self.assertIsNot(again, first)
        self.assertEqual(fetch.call_count, 1)

    def test_appearance_layer_options_are_independent_on_guide_grid(self):
        from appearance import save, window_source

        save({'background': '002244', 'background_opacity': 60, 'dimmer': 40})
        path = Path(window_source('XCMateGuideGrid.xml')) / 'resources/skins/Default/720p/XCMateGuideGrid.xml'
        tree = ET.parse(path)
        controls = tree.find('./controls')
        first, backdrop, dimmer = list(controls)[:3]
        self.assertEqual(first.findtext('colordiffuse'), 'FF002244')
        self.assertEqual(backdrop.findtext('colordiffuse'), '99FFFFFF')
        self.assertEqual(dimmer.findtext('colordiffuse'), '66000000')
        self.assertIsNone(first.get('id'))
        self.assertIsNone(dimmer.get('id'))
        self.assertEqual(tree.findtext('defaultcontrol'), '314')

    def test_preview_explicitly_uses_transparent_button_textures_over_colour_sample(self):
        import appearance
        import sys
        from PIL import Image

        class NativeWindow:
            def addControls(self, controls): pass
            def setFocus(self, control): pass
            def doModal(self): pass
            def close(self): pass

        gui = sys.modules['xbmcgui']
        with mock.patch.object(gui, 'WindowDialog', NativeWindow, create=True), \
             mock.patch.object(gui, 'ControlImage', create=True), \
             mock.patch.object(gui, 'ControlLabel', create=True), \
             mock.patch.object(gui, 'ControlButton', create=True) as button:
            appearance.preview(appearance.read())
        for field in ('focusTexture', 'noFocusTexture'):
            self.assertIn(field, button.call_args.kwargs)
            with Image.open(button.call_args.kwargs[field]) as image:
                self.assertEqual(image.convert('RGBA').getpixel((0, 0))[3], 0)

    def test_new_manual_logo_is_compact_without_distorting_aspect_or_alpha(self):
        from io import BytesIO
        from PIL import Image
        from logo_overrides96 import save, read

        stream = BytesIO()
        Image.new('RGBA', (1000, 500), (80, 130, 180, 110)).save(stream, format='PNG')
        row = {'sid':'1'}
        saved = save(self.portal, row, stream.getvalue(), confirmed=True)
        self.assertEqual(read(self.portal, [row])['1'], saved)
        with Image.open(saved) as stored:
            self.assertEqual(stored.size, (512,256))
            self.assertEqual(stored.convert('RGBA').getpixel((45,20))[3], 110)
