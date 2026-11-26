import unittest
from unittest import mock

import test_xcmate_artwork_roles_499 as roles_fixture
from xcmate027_fixture import Fixture


class PublicArt103(Fixture, unittest.TestCase):
    event = roles_fixture.ArtworkRoles499.event
    preflight = roles_fixture.ArtworkRoles499.preflight

    def setUp(self):
        super().setUp()
        self.options.update(epg_agent_enabled=True, programme_tmdb46=True, tmdb_research43=True)

    def test_public_tmdb_and_tvmaze_references_do_not_enable_direct_research(self):
        from artwork_sources96 import enabled
        from programme_image69 import eligible
        from programme_urls55 import resolve
        from storage_policy92 import images_enabled

        self.options.update(programme_tmdb46=False, tmdb_research43=False,
                            programme_tvmaze67=False, programme_xmltv96=False)
        event = self.event(('backdrop', 'poster'))
        event['agent_art']['poster'].update(source='agent_tvmaze', provider='tvmaze',
            url='https://static.tvmaze.com/uploads/images/original_untouched/test_poster.png')
        self.assertFalse(enabled('tmdb'))
        self.assertFalse(enabled('tvmaze'))
        with mock.patch('artwork_sources96.token_valid', side_effect=AssertionError('API token')):
            self.assertTrue(images_enabled())
        with mock.patch('programme_urls55.probe', side_effect=self.preflight):
            self.assertEqual(resolve(event, url_mode69=True)['source'], 'agent_tmdb')
            card = dict(event, _art_view499='card')
            poster = resolve(card, url_mode69=True)
        self.assertEqual(poster['source'], 'agent_tvmaze')
        self.assertTrue(eligible(poster, card))

    def test_switching_to_standard_hides_previously_verified_agent_images(self):
        from epg_handoff63 import profile_scope
        from programme_image69 import eligible
        from programme_urls55 import resolve

        event = self.event(('backdrop',))
        with mock.patch('programme_urls55.probe', side_effect=self.preflight):
            picture = resolve(event, url_mode69=True)
        self.assertTrue(eligible(picture, event))
        self.properties['XCMate.Agent103.Variant.' + profile_scope()] = 'standard'
        self.assertFalse(eligible(picture, event))

    def test_missing_still_uses_real_backdrop_then_real_poster_in_detail_view(self):
        from programme_urls55 import resolve
        from media_sources43 import SourceError

        event = dict(self.event(('backdrop', 'poster', 'legacy_icon')), _detail93=True)
        with mock.patch('programme_urls55.probe', side_effect=self.preflight):
            self.assertEqual(resolve(event, url_mode69=True)['role81'], 'backdrop')
        self.properties.clear()

        def unavailable_landscape(url, **kwargs):
            if 'test_backdrop' in url:
                raise SourceError('HTTP_NOT_FOUND')
            return self.preflight(url, **kwargs)

        with mock.patch('programme_urls55.probe', side_effect=unavailable_landscape):
            self.assertEqual(resolve(event, url_mode69=True)['role81'], 'poster')

    def test_legacy_portrait_is_not_allowed_in_the_landscape_hero(self):
        from programme_urls55 import resolve

        event = self.event(('legacy_icon',))
        with mock.patch('home_schedule75.applicable', return_value=False), \
             mock.patch('programme_urls55.probe', side_effect=lambda url, **kwargs:
                        dict(self.preflight(url, **kwargs), width=700, height=1050)):
            self.assertEqual(resolve(event, url_mode69=True)['source'], 'placeholder')

    def test_explicit_agent_candidates_reject_nonapproved_cdn(self):
        from agent_programme100 import candidates

        event = self.event(('backdrop',))
        event['agent_art']['backdrop']['url'] = 'https://unapproved.example.com/image.jpg'
        self.assertEqual(candidates(event), [])


    def test_manual_agent_alternative_survives_reload_without_replacing_backdrop(self):
        from programme_mapping85 import reload
        from programme_urls55 import resolve
        from work_requests86 import request, drain, result

        self.options.update(programme_tmdb46=False, tmdb_research43=False,
                            programme_tvmaze67=False, programme_xmltv96=False)
        event = self.event(('backdrop', 'poster'))
        poster = event['agent_art']['poster']
        preferred = poster['url'].replace('test_poster', 'alternate_poster')
        poster['alternatives'] = [dict(poster, url=preferred)]
        self.index.import_group('p', 'live', 'a', [
            {'stream_id': '1', 'category_id': 'a', 'name': 'Test channel'}])
        def preflight(url, **kwargs):
            return dict(self.preflight(poster['url'] if url == preferred else url), url=url)
        with mock.patch('programme_events46.load', return_value=event), \
             mock.patch('programme_urls55.probe', side_effect=preflight):
            nonce = request(event, 'search', source='agent_event103')
            drain()
            self.assertEqual(result(nonce)['code'], 'READY')
            candidates = result(nonce)['rows']
            self.assertEqual([row['role'] for row in candidates], ['backdrop','poster','poster'])
            self.assertTrue(all('url' not in row for row in candidates))
            nonce = request(event, 'save', candidate=candidates[-1])
            drain()
            self.assertEqual(result(nonce)['code'], 'SAVED')
            self.properties.clear()
            self.assertTrue(reload())
            manual = resolve(dict(event, _art_view499='card'), url_mode69=True)
            home = resolve(event, url_mode69=True)
        self.assertEqual(manual['source_url'], preferred)
        self.assertTrue(manual['manual85'])
        self.assertEqual(home['role81'], 'backdrop')

    def test_poster_confirmation_publishes_visible_loading_without_reopening(self):
        from programme_window46 import ProgrammeWindow46
        from xcmate027_fixture import ADDON

        window = ProgrammeWindow46('XCMateProgramme46.xml', str(ADDON), 'Default', '720p')
        window.configure(self.portal, {'sid':'1', 'name':'Test channel'})
        window.event = dict(self.event(('backdrop','poster')), _detail93=True)
        window._series_menu85 = True
        window._ready = True
        self.addCleanup(window.close)
        with mock.patch('work_manager86.open', return_value=True):
            window.pump()
        self.assertTrue(window.getControl(147).visible)
        self.assertIn('wird geladen', window.getControl(147).label)

    def test_diagnostic_retains_tvmaze_api_result_if_kodi_texture_probe_fails(self):
        from programme_diagnostic74 import check

        self.options['programme_tvmaze67'] = True
        with mock.patch('tmdb_connection60.test_connection', return_value='TMDB_TOKEN_MISSING'), \
             mock.patch('media_sources43.get', return_value={'id': 1}), \
             mock.patch('programme_diagnostic74.active_image', side_effect=RuntimeError('unavailable Kodi texture probe')):
            diagnostic = check()
        self.assertEqual(diagnostic['tvmaze'], 'TVMAZE_OK')
        self.assertEqual(diagnostic['image'], 'IMAGE_PROBE_FAILED')

    def test_xmltv_cast_role_is_shown_with_the_named_actor(self):
        from io import BytesIO
        from programme_flow48 import source_metadata
        from programme_window46 import ProgrammeWindow46
        from xcmate027_fixture import ADDON
        from xmltv_stream import parse

        payload = b"""<tv><programme channel="fixture" start="20261125181500 +0000" stop="20261125184000 +0000">
          <title>Example</title><credits><actor role="Sam">Rose McIver</actor><actor>Brandon Scott Jones</actor></credits>
          </programme></tv>"""
        programmes = []
        parse(BytesIO(payload), lambda *row: None, programmes.append)
        data = source_metadata(programmes[0])
        self.assertEqual(data.get('cast_roles'), {'Rose McIver': 'Sam'})
        window = ProgrammeWindow46('XCMateProgramme46.xml', str(ADDON), 'Default', '720p')
        window.configure(self.portal, {'sid': '1', 'name': 'Test channel'})
        self.addCleanup(window.close)
        window._paint_facts(dict(self.event(()), **data))
        self.assertEqual(window.getControl(720).label, 'Rose McIver · Sam')
        self.assertEqual(window.getControl(721).label, 'Brandon Scott Jones')

    def test_details_prefers_a_verified_still_over_same_event_lastgood_backdrop(self):
        from programme_lastgood80 import choose
        from programme_urls55 import resolve

        event = dict(self.event(('episode_still','backdrop')), _detail93=True)
        event['agent_art']['episode_still'].update(
            source='agent_tvmaze', provider='tvmaze',
            url='https://static.tvmaze.com/uploads/images/original_untouched/test_episode_still.png')
        with mock.patch('programme_urls55.probe', side_effect=self.preflight), \
             mock.patch('home_schedule75.applicable', return_value=False), \
             mock.patch('artwork_display84.observe', return_value=False):
            previous = resolve(dict(event, _art_view499='hero'), url_mode69=True)
            current = resolve(event, url_mode69=True)
            self.assertEqual(previous['role81'], 'backdrop')
            self.assertEqual(current['role81'], 'episode_still')
            self.assertEqual(choose(event, current, previous)['role81'], 'episode_still')

    def test_public_artwork_worker_never_reads_disabled_tmdb_token(self):
        from programme_requests68 import drain, request

        self.options.update(programme_tmdb46=False, tmdb_research43=False,
                            programme_tvmaze67=False, programme_xmltv96=False)
        event = self.event(('backdrop',))
        self.index.import_group('p', 'live', 'a', [
            {'stream_id': '1', 'category_id': 'a', 'name': 'Test channel'}])
        with mock.patch('programme_events46.load', return_value=event), \
             mock.patch('tmdb_token61.effective_tmdb_read_token', side_effect=AssertionError('disabled API token read')), \
             mock.patch('programme_urls55.enqueue', return_value=True):
            self.assertTrue(request(event, priority=True))
            self.assertEqual(drain(), 1)

    def test_detail_can_recover_verified_backdrop_from_kodi_cache_without_network(self):
        import hashlib
        import json

        from decoded_assets88 import shutdown
        from event_cache88 import recover
        from programme_urls55 import resolve

        event = self.event(('backdrop',))
        detail = dict(event, _detail93=True)
        with mock.patch('home_schedule75.applicable', return_value=False), \
             mock.patch('artwork_display84.observe', return_value=False), \
             mock.patch('programme_urls55.probe', side_effect=self.preflight):
            backdrop = resolve(event, url_mode69=True)
        body = self.preflight(backdrop['source_url'])['_body81']
        file = self.folder / 'kodi-image.png'
        file.write_bytes(body)
        texture = dict(file=str(file), sha256=hashlib.sha256(body).hexdigest(), width=1280, height=720)
        rpc = json.dumps({'result': {'textures': [{'url': backdrop['image']}]}})
        shutdown()
        self.properties.clear()
        with mock.patch('xbmc.executeJSONRPC', return_value=rpc, create=True), \
             mock.patch('widget_cache82.decoded', return_value=texture), \
             mock.patch('programme_urls55.probe', side_effect=AssertionError('Kodi cache hit')):
            recovered = recover(detail)
        self.assertIsNotNone(recovered)
        self.assertEqual(recovered['role81'], 'backdrop')
        self.assertEqual(recovered['image'], str(file))

    def test_detail_keeps_backdrop_and_manual_poster_provenance_separate(self):
        from programme_window46 import ProgrammeWindow46
        from xcmate027_fixture import ADDON

        window = ProgrammeWindow46('XCMateProgramme46.xml', str(ADDON), 'Default', '720p')
        window.configure(self.portal, {'sid': '1', 'name': 'Test channel'})
        window.event = dict(self.event(('backdrop',)), _detail93=True)
        self.addCleanup(window.close)
        backdrop = dict(source='agent_tmdb', role81='backdrop', image='/verified-wide.png')
        poster = dict(source='tvmaze_series', role81='poster', image='/manual-portrait.png', manual85=True)
        with mock.patch('programme_image69.eligible', side_effect=lambda value, event: bool(value)):
            window._paint_art(poster, backdrop, {})
        self.assertEqual(window.getControl(105).label, 'Hintergrundbild · Agent/TMDB')
        self.assertEqual(window.getControl(146).label, 'Poster · TVMaze')

    def test_switching_direct_api_off_keeps_already_verified_agent_artwork(self):
        from artwork_sources96 import choose, enabled
        from programme_image69 import eligible
        from programme_requests68 import result
        from programme_urls55 import resolve
        import xml.etree.ElementTree as xml

        settings = self.folder / 'settings.xml'
        settings.write_text('<settings/>')
        event = self.event(('backdrop',))

        def set_kodi_setting(key, value):
            self.options[key] = value == 'true'
            root = xml.parse(settings).getroot()
            xml.SubElement(root, 'setting', id=key).text = value
            xml.ElementTree(root).write(settings)

        with mock.patch('programme_urls55.probe', side_effect=self.preflight):
            picture = resolve(event, url_mode69=True)
        self.assertTrue(eligible(picture, event))
        with mock.patch('xbmcaddon.Addon', return_value=mock.Mock(setSetting=set_kodi_setting)):
            choose('tmdb', False)
        self.assertFalse(enabled('tmdb'))
        self.assertTrue(eligible(picture, event))
        self.assertEqual(result(event)['image'], picture['image'])

    def test_native_locked_agent_backdrop_remains_eligible_after_direct_optout(self):
        import hashlib
        import time

        from decoded_assets88 import shutdown
        from programme_image69 import eligible
        from programme_lock89 import acknowledge, propose, window
        from programme_requests68 import result
        from programme_urls55 import resolve

        event = self.event(('backdrop',))
        with mock.patch('programme_urls55.probe', side_effect=self.preflight):
            artwork = resolve(event, url_mode69=True)
        body = self.preflight(artwork['source_url'])['_body81']
        image = self.folder / 'native-kodi-texture.png'
        image.write_bytes(body)
        propose(event, artwork, dict(file=str(image), sha256=hashlib.sha256(body).hexdigest()))
        native = window()
        native.setProperty('XCMate.Hero63.Active', 'A')
        native.setProperty('XCMate.Hero63.A.Image', artwork['image'])
        with mock.patch('xbmcgui.getCurrentWindowId', return_value=10000), \
             mock.patch('xbmc.getInfoLabel', side_effect=lambda name: 'live' if 'WidgetKind41' in name else '1'), \
             mock.patch('xbmc.getCondVisibility', return_value=True), \
             mock.patch('time.monotonic', return_value=time.monotonic() + 1):
            self.assertTrue(acknowledge(event, native)['lock89'])
        shutdown()
        locked = result(event)
        self.assertTrue(locked['lock89'])
        self.assertTrue(eligible(locked, event))
        self.options.update(programme_tmdb46=False, tmdb_research43=False, programme_tmdb_optout77=True)
        locked = result(event)
        self.assertTrue(locked['lock89'])
        self.assertEqual(locked['image'], str(image))
        self.assertTrue(eligible(locked, event))

    def test_home_can_admit_a_recovered_agent_backdrop_under_its_own_image_policy(self):
        import json

        from agent_programme100 import candidates
        from hero_render86 import recovered_candidate
        from programme_image69 import eligible

        event = self.event(('backdrop',))
        candidate = candidates(event)[0]
        texture = dict(file='/verified/agent.png', sha256='a'*64, width=1280, height=720)
        rpc = json.dumps({'result': {'textures': [{'url': candidate['url']}]}})
        with mock.patch('xbmc.executeJSONRPC', return_value=rpc, create=True), \
             mock.patch('widget_cache82.decoded', return_value=texture):
            artwork = recovered_candidate(event, candidate, candidate['url'])
        self.assertIsNotNone(artwork)
        self.assertTrue(eligible(artwork, event))
