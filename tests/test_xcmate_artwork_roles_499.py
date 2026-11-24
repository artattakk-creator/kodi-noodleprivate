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

    def test_details_keep_prepared_station_logo_under_neutral_hero_when_artwork_is_missing(self):
        from programme_window46 import ProgrammeWindow46
        from xcmate027_fixture import ADDON

        channel={'sid':'1','name':'Test channel'}
        event=dict(self.event(('poster',)),_detail93=True,logo='/locally-verified-logo.png')
        window=ProgrammeWindow46('XCMateProgramme46.xml',str(ADDON),'Default','720p')
        window.configure(self.portal,channel)
        window._ready=True
        window.event=event
        window._paint_facts(event)
        self.addCleanup(window.close)
        with mock.patch('programme_requests68.result',return_value={'code':'NO_IMAGE','source':'placeholder'}):
            window.pump()
        self.assertFalse(window.getControl(110).visible)
        self.assertTrue(window.getControl(111).visible)
        self.assertEqual(window.getControl(111).image,event['logo'])
        self.assertFalse(window.getControl(130).visible)
    def test_gui_intent_and_worker_preserve_concurrent_roles_and_coalesce_same_role(self):
        import importlib.util
        import sys
        import threading
        from programme_requests68 import drain, request, result
        import programme_urls55
        spec=importlib.util.spec_from_file_location('programme_urls55',programme_urls55.__file__)
        worker=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(worker)

        hero = self.event(('backdrop','poster','episode_still'))
        details = dict(hero,_detail93=True)
        card = dict(hero,_art_view499='card')
        self.index.import_group('p','live','a',[{'stream_id':'1','category_id':'a','name':'Test channel'}])
        entered = threading.Event()
        release = threading.Event()
        fetched = []
        def check(url, **kwargs):
            fetched.append(url)
            if len(fetched) == 1:
                entered.set()
                self.assertTrue(release.wait(3))
            return self.preflight(url, **kwargs)
        with mock.patch.dict(sys.modules,programme_urls55=worker), \
             mock.patch('programme_events46.load',side_effect=lambda *args:dict(hero,code='LOCAL_EVENT')), \
             mock.patch.object(worker,'probe',side_effect=check), \
             mock.patch('programme_reference84.tick'):
            try:
                self.assertTrue(request(hero,priority=True))
                self.assertTrue(request(card))
                self.assertTrue(request(details,priority=True))
                self.assertEqual(drain(),3)
                self.assertTrue(entered.wait(3), (result(hero).get('code'), result(card).get('code'), result(details).get('code'), list(worker._pending)))
                self.assertTrue(request(card))
                self.assertEqual(drain(),0)
                release.set()
                import time
                deadline=time.monotonic()+3
                while worker._pending and time.monotonic()<deadline:
                    time.sleep(.01)
                self.assertFalse(worker._pending)
                self.assertEqual(result(hero)['role81'],'backdrop')
                self.assertEqual(result(card)['role81'],'poster')
                self.assertEqual(result(details)['role81'],'episode_still')
                self.assertCountEqual(fetched,[role['url'] for role in hero['agent_art'].values()])
            finally:
                release.set()
                worker.shutdown()
                if worker._thread:
                    worker._thread.join(3)
                if 'decoded_assets88' in sys.modules:
                    sys.modules['decoded_assets88'].shutdown()

    def test_worker_keeps_same_event_roles_queued_but_only_one_job_per_role(self):
        import importlib.util
        import programme_urls55
        spec=importlib.util.spec_from_file_location('role_queue499_fixture',programme_urls55.__file__)
        worker=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(worker)

        event = self.event(('backdrop','poster'))
        card = dict(event,_art_view499='card')
        with mock.patch.object(worker,'_thread',mock.Mock(is_alive=lambda:True)):
            self.assertTrue(worker.enqueue(event,priority68=True))
            self.assertTrue(worker.enqueue(card,priority68=True))
            self.assertFalse(worker.enqueue(dict(card),priority68=True))
            self.assertEqual(len(worker._pending),2)


    def test_same_verified_body_deduplicates_bytes_but_recovers_both_role_proofs(self):
        import hashlib
        import json
        import decoded_assets88 as assets
        from event_cache88 import recover
        from programme_urls55 import resolve

        hero=self.event(('backdrop','episode_still'))
        details=dict(hero,_detail93=True)
        hero['agent_art']['episode_still']['url']=hero['agent_art']['backdrop']['url']
        body=self.preflight(hero['agent_art']['backdrop']['url'])['_body81']
        with mock.patch('programme_transport77.verified',side_effect=lambda url,cancel,**kw:self.preflight(url,**kw)) as fetch, \
             mock.patch.object(assets,'MAX_BYTES',len(body)):
            wide=resolve(hero,url_mode69=True)
            still=resolve(details,url_mode69=True)
        self.assertEqual(fetch.call_count,1)
        self.assertEqual(wide['sha256'],still['sha256'])
        self.assertNotEqual(wide['image'],still['image'])
        self.assertEqual(len([item for item in assets._items.values() if item['body']==body]),2)
        self.assertEqual(len({id(item['body']) for item in assets._items.values() if item['body']==body}),1)
        file=self.folder/'texture.png'
        file.write_bytes(body)
        record=dict(file=str(file),sha256=hashlib.sha256(body).hexdigest(),width=1280,height=720)
        textures=[{'url':wide['image']},{'url':still['image']}]
        assets.shutdown()
        self.properties.clear()
        with mock.patch('xbmc.executeJSONRPC',create=True,return_value=json.dumps(dict(result=dict(textures=textures)))), \
             mock.patch('widget_cache82.decoded',return_value=record):
             self.assertEqual(recover(hero)['role81'],'backdrop')
             self.assertEqual(recover(details)['role81'],'episode_still')

    def test_bad_primary_tries_same_role_alternative_before_legacy_icon(self):
        from programme_urls55 import resolve

        event=self.event(('poster','legacy_icon'))
        poster=event['agent_art']['poster']
        alternate=dict(poster,url='https://image.tmdb.org/t/p/w1280/test_alternate.png')
        poster['alternatives']=[alternate]
        def check(url, **kwargs):
            result=self.preflight(url,**kwargs)
            if url==poster['url']:
                return dict(result,width=1280,height=720)
            if url==alternate['url']:
                return dict(self.preflight(poster['url'],**kwargs),url=url)
            raise AssertionError('legacy before valid alternate')
        with mock.patch('programme_urls55.probe',side_effect=check) as fetch:
            art=resolve(dict(event,_art_view499='card'),url_mode69=True)
        self.assertEqual(art['source_url'],alternate['url'])
        self.assertEqual(art['role81'],'poster')
        self.assertEqual(fetch.call_count,2)

    def test_same_qualified_xmltv_origin_asset_only_downloads_once_across_roles(self):
        from programme_urls55 import resolve

        hero=dict(self.event(('backdrop','episode_still')),canonical='fixture.channel')
        uri='https://cdn.example.org/test_backdrop.png'
        for candidate in hero['agent_art'].values():
            candidate.update(url=uri,source='agent_xmltv',provider='xmltv')
        details=dict(hero,_detail93=True)
        with mock.patch('programme_transport77.verified',side_effect=lambda url,cancel,**kw:self.preflight(url,**kw)) as fetch:
            self.assertEqual(resolve(hero,url_mode69=True)['role81'],'backdrop')
            self.assertEqual(resolve(details,url_mode69=True)['role81'],'episode_still')
        self.assertEqual(fetch.call_count,1)

    def test_previous_hero_legacy_icon_does_not_mask_valid_card_poster(self):
        from programme_requests68 import result
        from programme_urls55 import resolve

        hero=self.event(('poster','legacy_icon'))
        card=dict(hero,_art_view499='card')
        with mock.patch('home_schedule75.applicable',return_value=True), \
             mock.patch('programme_urls55.probe',side_effect=self.preflight) as fetch:
            self.assertEqual(resolve(hero,url_mode69=True)['role81'],'legacy_icon')
            self.assertNotEqual(result(card).get('role81'),'legacy_icon')
            self.assertEqual(resolve(card,url_mode69=True)['role81'],'poster')
        self.assertEqual(fetch.call_count,2)
