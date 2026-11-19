"""The same exact XMLTV event supplies the artwork preferred by each view."""
from io import BytesIO
import unittest
from unittest import mock

from PIL import Image

from xcmate027_fixture import Fixture


class ArtworkRoles499(Fixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.options.update(epg_agent_enabled=True, programme_tmdb46=True, tmdb_research43=True)

    def event(self, roles):
        from programme_events46 import describe

        event = describe(self.portal, {'sid': '1', 'name': 'Test channel'}, {
            'title': 'Programme 499', 'start': self.now - 3, 'stop': self.now + 3600})
        event['agent_art'] = {
            role: {'url': 'https://image.tmdb.org/t/p/w1280/test_' + role + '.png',
                   'source': 'agent_tmdb', 'provider': 'tmdb', 'match': 'EXACT_EVENT',
                   'attribution': 'XCMate EPG Agent · TMDB'}
            for role in roles
        }
        return event

    def preflight(self, url, **kwargs):
        role = url.partition('/test_')[2].removesuffix('.png')
        size = (750, 1100) if role == 'poster' else (1280, 720)
        output = BytesIO()
        Image.new('RGB', size, {'poster': 'red', 'episode_still': 'green'}.get(role,'blue')).save(output, 'PNG')
        return {'url':url,'width':size[0],'height':size[1],'decoded77':True,'_body81':output.getvalue()}

    def test_hero_details_and_card_keep_their_own_verified_image_for_one_event(self):
        from programme_requests68 import result
        from programme_urls55 import resolve

        hero = self.event(('backdrop','poster','episode_still','legacy_icon'))
        detail = dict(hero, _detail93=True)
        card = dict(hero, _art_view499='card')
        with mock.patch('home_schedule75.applicable', return_value=True), \
             mock.patch('programme_match46.candidate', side_effect=AssertionError('extra title search')), \
             mock.patch('programme_urls55.probe', side_effect=self.preflight) as check:
            self.assertEqual(resolve(hero, allow_lookup=True,url_mode69=True)['role81'], 'backdrop')
            self.assertEqual(resolve(detail,allow_lookup=True,url_mode69=True)['role81'], 'episode_still')
            self.assertEqual(resolve(card,allow_lookup=True,url_mode69=True)['role81'], 'poster')
            self.assertEqual(result(hero)['role81'], 'backdrop')
            self.assertEqual(result(detail)['role81'], 'episode_still')
            self.assertEqual(result(card)['role81'], 'poster')
        self.assertEqual(check.call_count, 3)

    def test_missing_backdrop_uses_verified_legacy_icon_instead_of_portrait(self):
        from programme_urls55 import resolve
        event = self.event(('poster','legacy_icon'))
        with mock.patch('home_schedule75.applicable', return_value=True), \
             mock.patch('programme_match46.candidate', side_effect=AssertionError('extra title search')), \
             mock.patch('programme_urls55.probe', side_effect=self.preflight) as check:
            value = resolve(event,allow_lookup=True,url_mode69=True)
        self.assertEqual(value['role81'], 'legacy_icon')
        self.assertTrue(value['source_url'].endswith('/test_legacy_icon.png'))
        self.assertEqual(check.call_count, 1)

    def test_mislabeled_landscape_poster_falls_back_to_legacy_for_card(self):
        from programme_urls55 import resolve

        event = dict(self.event(('poster','legacy_icon')), _art_view499='card')
        def landscape(url, **kwargs):
            return dict(self.preflight(url, **kwargs), width=1280, height=720)
        with mock.patch('programme_urls55.probe', side_effect=landscape):
            value = resolve(event,allow_lookup=False,url_mode69=True)
        self.assertEqual(value['role81'], 'legacy_icon')

    def test_confirmed_manual_image_is_not_replaced_by_typed_role(self):
        from programme_urls55 import resolve
        event = dict(self.event(('poster','episode_still')), _detail93=True)
        manual = dict(code='READY', source='user_local86', match='MANUAL_CONFIRMED',
                      image='/confirmed-local.png', manual85=True)
        with mock.patch('programme_lock89.current', return_value=manual), \
             mock.patch('programme_urls55.probe', side_effect=AssertionError('extra image fetch')):
            self.assertEqual(resolve(event,allow_lookup=True,url_mode69=True), manual)

    def test_widget_programme_card_binds_portrait_without_reusing_as_landscape(self):
        from programme_urls55 import resolve
        from programme_widgets46 import decorate

        event = self.event(('backdrop', 'poster'))
        info = {'now_time':'20:15','now_end_time':'21:15','progress':.25}
        item = {'art':{},'props':{},'info':{'plot':''}}
        with mock.patch('home_schedule75.applicable', return_value=True), \
             mock.patch('programme_urls55.probe', side_effect=self.preflight), \
             mock.patch('programme_events46.from_info',return_value=event):
             backdrop = resolve(event,url_mode69=True)['image']
             poster = resolve(dict(event,_art_view499='card'),url_mode69=True)['image']
             rendered = decorate(item,self.portal,{'sid':'1'},info)
        self.assertEqual(rendered['art']['poster'],poster)
        self.assertEqual(rendered['art']['fanart'],backdrop)
        self.assertNotEqual(poster,backdrop)

    def test_generic_negative_for_missing_role_does_not_block_valid_other_role(self):
        from programme_urls55 import resolve

        event = self.event(('poster',))
        self.assertEqual(resolve(event,url_mode69=True)['source'],'placeholder')
        card = dict(event,_art_view499='card')
        with mock.patch('programme_urls55.probe', side_effect=self.preflight):
            self.assertEqual(resolve(card,url_mode69=True)['role81'],'poster')

    def test_generic_lastgood_rejects_still_in_hero_view(self):
        from programme_lastgood80 import choose
        from programme_urls55 import resolve

        hero = self.event(('episode_still',))
        with mock.patch('programme_urls55.probe', side_effect=self.preflight):
            previous = resolve(dict(hero,_detail93=True),url_mode69=True)
        result = choose(hero, {'code':'PENDING','source':'placeholder'}, previous)
        self.assertEqual(result['source'],'placeholder')

    def test_broker_sees_existing_detail_receipt_as_terminal_for_detail_intent(self):
        from programme_requests68 import completed, drain, request
        from programme_urls55 import resolve

        detail = dict(self.event(('episode_still',)), _detail93=True)
        with mock.patch('programme_urls55.probe', side_effect=self.preflight):
            completed(detail,resolve(detail,url_mode69=True))
        self.assertTrue(request(detail,priority=True))
        self.index.import_group('p','live','a',[{'stream_id':'1','category_id':'a','name':'Test channel'}])
        with mock.patch('programme_events46.load',return_value=dict(detail,code='LOCAL_EVENT')), \
             mock.patch('programme_urls55.enqueue') as enqueue:
            drain()
        enqueue.assert_not_called()

    def test_cold_kodi_texture_recovery_selects_view_role_without_http(self):
        import hashlib
        import json
        from decoded_assets88 import shutdown
        from event_cache88 import recover
        from programme_urls55 import resolve

        event = self.event(('backdrop','episode_still'))
        detail = dict(event,_detail93=True)
        with mock.patch('programme_urls55.probe',side_effect=self.preflight):
            still=resolve(detail,url_mode69=True)
            backdrop=resolve(event,url_mode69=True)
        textures=[{'url':still['image'],'cachedurl':'still'},{'url':backdrop['image'],'cachedurl':'backdrop'}]
        payload=json.dumps({'result':{'textures':textures}})
        file=self.folder/'texture.png'
        file.write_bytes(self.preflight(still['source_url'])['_body81'])
        stamp=file.stat()
        body={'file':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'width':1280,'height':720,
              'stamp':[stamp.st_mtime_ns,stamp.st_size]}
        shutdown()
        self.properties.clear()
        with mock.patch('xbmc.executeJSONRPC',create=True,return_value=payload), \
             mock.patch('widget_cache82.decoded',return_value=body), \
             mock.patch('programme_transport77.verified',side_effect=AssertionError('network on recovery')):
            recovered=recover(detail)
        self.assertEqual(recovered['role81'],'episode_still')
        self.assertEqual(recovered['image'],str(file))

    def test_details_keep_prepared_logo_fallback_when_requested_still_is_missing(self):
        from programme_window46 import ProgrammeWindow46
        from xcmate027_fixture import ADDON

        channel={'sid':'1','name':'Test channel'}
        event=dict(self.event(('poster',)),_detail93=True,_fallback499='/locally-verified-logo.png')
        window=ProgrammeWindow46('XCMateProgramme46.xml',str(ADDON),'Default','720p')
        window.configure(self.portal,channel)
        window._ready=True
        window.event=event
        self.addCleanup(window.close)
        with mock.patch('programme_requests68.result',return_value={'code':'NO_IMAGE','source':'placeholder'}):
            window.pump()
        self.assertTrue(window.getControl(110).visible)
        self.assertEqual(window.getControl(110).image,event['_fallback499'])
        self.assertFalse(window.getControl(130).visible)
