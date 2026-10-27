"""Cross-surface event identity using real guide/shared SQLite snapshots."""
import importlib
import io
from pathlib import Path
import sqlite3
import sys
import time
import types
import unittest
from unittest import mock
from PIL import Image
from xcmate027_fixture import Fixture


class ProgrammeIntegration47(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.guide=importlib.import_module('guide_store')
        self.local=importlib.import_module('local_epg')
        self.events=importlib.import_module('programme_events46')
        self.shared=importlib.import_module('programme_index46')
        self.row=dict(sid='1',kind='live',name='Real station',epg_channel_id='xml',category_id='a')
        self.current=dict(channel='xml',name='Real programme',descr='Saved full description',
            start_timestamp=self.now-60,stop_timestamp=self.now+600,_source_index=0,
            screenshot_uri='https://images.example.test/exact-event.png',sub_title='Actual episode',season=2,episode_number=3)
        self.next=dict(channel='xml',name='Next programme',descr='Next description',
            start_timestamp=self.now+600,stop_timestamp=self.now+1200,_source_index=0)

    def save_guide(self):
        self.guide.import_cache('p',{'xml':[self.current,self.next]},'real-revision',now=self.now,trusted_feed=True)

    def channel(self):
        return types.SimpleNamespace(extra={'stream_id':'1','category_id':'a'},tvg_id='xml',logo='',name='Real station')

    def test_large_guide_mini_infobar_and_widget_use_the_same_actual_event_key(self):
        self.save_guide()
        info=self.local.now_next('p',[self.row],{},self.now)['1']
        detail=self.events.load(self.portal,self.row,now=self.now)
        widget=importlib.import_module('widget_items45').describe(self.portal,'live',self.row,{},info)
        tv=importlib.import_module('tv_data').GuideSnapshot(self.portal,self.client)
        tv.request([self.channel()]);tv.refresh();on_video=tv.get('1',now=self.now)
        grid=importlib.import_module('guide_grid_data').page(self.portal,0,self.now-120,'a')
        grid_event=grid['rows'][0]['events'][0]
        self.assertEqual({info['programme_key47'],detail['key'],widget['props']['XCMate.ProgrammeKey47'],on_video['programme_key47'],grid_event['programme_key47']},{detail['key']})
        self.assertEqual(on_video['canonical46'],'xml')
        self.assertEqual((detail['season'],detail['episode']),(2,3))

    def test_programme_picture_persisted_once_is_used_by_real_widget_and_detail(self):
        self.save_guide();detail=self.events.load(self.portal,self.row,now=self.now)
        out=io.BytesIO();Image.new('RGB',(320,180),(30,90,120)).save(out,'PNG');data=out.getvalue()
        art=importlib.import_module('programme_art46')
        Path(art.root()).mkdir()
        with mock.patch.object(art,'space'):
            prepared=art.prepare(detail,fetch=lambda *a,**kw:data,match=lambda *a,**kw:None)
        self.assertEqual(prepared['code'],'READY')
        art._memory.clear()
        info=self.local.now_next('p',[self.row],{},self.now)['1']
        widget=importlib.import_module('widget_items45').describe(self.portal,'live',self.row,{},info)
        loaded=art.cached(self.events.load(self.portal,self.row,now=self.now))
        self.assertEqual(widget['props']['XCMate.ProgrammeImage46'],loaded['image'])
        self.assertEqual(Path(loaded['image']).read_bytes(),data)

    def prepared_art(self):
        self.save_guide();event=self.events.load(self.portal,self.row,now=self.now)
        out=io.BytesIO();Image.new('RGB',(320,180),(30,90,120)).save(out,'PNG')
        art=importlib.import_module('programme_art46');Path(art.root()).mkdir(exist_ok=True)
        with mock.patch.object(art,'space'):value=art.prepare(event,fetch=lambda *a,**kw:out.getvalue(),match=lambda *a,**kw:None)
        return art,event,value

    def test_directory_header_hit_does_not_skip_first_worker_hash_verification(self):
        art,event,value=self.prepared_art();art._memory.clear();was_stopped=art._stop.is_set();art._stop.clear()
        def cleanup():
            with art._lock:art._queue.pop(event['key'],None);art._pending.discard(event['key'])
            if was_stopped:art._stop.set()
        self.addCleanup(cleanup)
        self.assertEqual(art.cached(event)['code'],'READY')
        with mock.patch.object(art,'ensure'):
            self.assertTrue(art.enqueue(event))
        self.assertNotIn('_verified47',art.peek(event))

    def test_missing_local_programme_image_is_not_presented_as_a_valid_texture(self):
        art,event,value=self.prepared_art()
        Path(value['image']).unlink()  # Synthetic host-owned file only.
        result=art.cached(event)
        self.assertEqual(result['code'],'LOCAL_IMAGE_MISSING')
        self.assertEqual(result['image'],event['placeholder'])

    def test_now_next_rollover_keeps_canonical_source_metadata_and_correct_key_in_ram(self):
        self.save_guide();tv=importlib.import_module('tv_data').GuideSnapshot(self.portal,self.client)
        tv.request([self.channel()]);tv.refresh();before=tv.get('1',now=self.now)
        with mock.patch('sqlite3.connect',side_effect=AssertionError('database on GUI rollover')),mock.patch('socket.getaddrinfo',side_effect=AssertionError('network on GUI rollover')):
            after=tv.get('1',now=self.now+601)
        expected=self.events.load(self.portal,self.row,now=self.now+601)
        self.assertNotEqual(before['programme_key47'],after['programme_key47'])
        self.assertEqual(after['programme_key47'],expected['key'])
        self.assertEqual(after['canonical46'],'xml')
        self.assertEqual(after['events'][0]['source'],0)

    def test_shared_lastgood_is_read_when_primary_guide_is_temporarily_absent(self):
        stage=self.shared.Stage('p','existing-feed')
        stage.add(self.current,dict(xmltv_image=self.current['screenshot_uri']),'provider')
        stage.flush();self.shared.finish('p',stage.generation,True)
        before=set(self.folder.iterdir())
        info=self.local.now_next('p',[self.row],{},self.now)['1']
        self.assertEqual(info['now'],'Real programme')
        self.assertFalse(Path(self.guide.path()).exists())
        self.assertLessEqual({p.name for p in set(self.folder.iterdir())-before},{'programme_artwork.sqlite-wal','programme_artwork.sqlite-shm'})

    def test_asset_only_database_does_not_hide_legacy_cache_only_short_epg(self):
        db=self.shared.connect(True);db.close()
        raw={'epg_listings':[dict(title='Cached short programme',start_timestamp=self.now-60,stop_timestamp=self.now+600)]}
        self.client._get_json=mock.Mock(return_value=raw)
        info=self.local.now_next('p',[self.row],{},self.now,client=self.client)['1']
        self.assertEqual(info['now'],'Cached short programme')
        self.assertFalse(Path(self.guide.path()).exists())
        self.assertTrue(all(call.kwargs['cached_only'] for call in self.client._get_json.call_args_list))

    def test_manual_mapping_wins_over_shared_provider_data_across_views(self):
        manual=dict(self.current,channel='manual',name='Manual mapped programme')
        stage=self.shared.Stage('p','existing-feed')
        stage.add(self.current,{},'provider');stage.add(manual,{},'provider')
        stage.flush();self.shared.finish('p',stage.generation,True)
        with mock.patch.object(sys.modules['epg_sources'],'configuration',return_value={'mappings':{'1':'manual'},'sources':[]}):
            info=self.local.now_next('p',[self.row],{'1':'manual'},self.now)['1']
            detail=self.events.load(self.portal,self.row,now=self.now)
        self.assertEqual(info['now'],'Manual mapped programme')
        self.assertEqual(info['programme_key47'],detail['key'])

    def test_negative_or_ambiguous_art_is_not_a_programme_picture(self):
        self.save_guide();info=self.local.now_next('p',[self.row],{},self.now)['1']
        placeholder=self.events.from_info(self.portal,self.row,info)['placeholder']
        value=dict(art={'thumb':'/own/station-logo.png'},props={},info={'plot':''})
        with mock.patch('programme_art46.cached',return_value=dict(image=placeholder,source='placeholder',code='NO_IMAGE')):
            decorated=importlib.import_module('programme_widgets46').decorate(value,self.portal,self.row,info)
        self.assertEqual(decorated['art']['thumb'],'/own/station-logo.png')
        self.assertEqual(decorated['props']['XCMate.ProgrammeImage46'],placeholder)
        self.assertEqual(decorated['props']['XCMate.ProgrammeDisplay47'],'STATION_LOGO')

    def test_no_logo_still_has_actual_station_name_without_claiming_image_success(self):
        value=importlib.import_module('widget_items45').describe(self.portal,'live',self.row,{},{})
        self.assertEqual(value['label'],'Real station')
        self.assertEqual(value['props']['XCMate.ProgrammeDisplay47'],'NEUTRAL_NO_LOGO')
        self.assertEqual(value['props']['XCMate.ProgrammeLogo46'],'')

    def test_native_sender_logo_fallback_and_programme_overlay_are_separate_references(self):
        value=dict(art={'thumb':'/own/logo.png'},props={},info={'plot':''})
        with mock.patch('programme_art46.cached',return_value=dict(image='/own/programme.jpg',source='xmltv_event',code='READY')):
            decorated=importlib.import_module('programme_widgets46').decorate(value,self.portal,self.row,{})
        self.assertEqual(decorated['art']['thumb'],'/own/programme.jpg')
        self.assertEqual(decorated['props']['channellogo'],'/own/logo.png')
        self.assertEqual(decorated['props']['XCMate.ProgrammeLogo46'],'/own/logo.png')

    def test_population_status_distinguishes_empty_database_from_text_without_pictures(self):
        snapshot=importlib.import_module('programme_snapshot47')
        db=self.shared.connect(True);db.close()
        self.assertEqual(snapshot.status('p')['code'],'DATA_EMPTY')
        self.save_guide()
        status=snapshot.status('p')
        self.assertGreater(status['facts'],0)
        self.assertEqual(status['code'],'LOCAL_TEXT_WITHOUT_MATCHED_ART')
        self.assertEqual(status['artwork_sample_ready'],0)

    def test_readonly_page_reuses_connections_and_closes_them_on_exception(self):
        self.save_guide();sessions=importlib.import_module('programme_read47')
        original=sqlite3.connect;opened=[]
        def connect(*a,**kw):db=original(*a,**kw);opened.append(db);return db
        with mock.patch.object(sqlite3,'connect',side_effect=connect):
            with self.assertRaisesRegex(RuntimeError,'interrupted'):
                with sessions.session():
                    for _ in range(12):self.events.load(self.portal,self.row,now=self.now)
                    raise RuntimeError('interrupted')
        # Guide view uses its own transaction; shared/rich handles are reused.
        for db in opened:
            with self.assertRaises(sqlite3.ProgrammingError):db.execute('SELECT 1')
        self.assertIsNone(getattr(sessions._local,'state',None))

    def test_thread_scoped_reads_do_not_share_sqlite_connection_between_workers(self):
        self.save_guide();sessions=importlib.import_module('programme_read47')
        import threading
        handles=[];errors=[]
        def read():
            try:
                with sessions.session():handles.append(self.shared.connect(False)._db)
            except Exception as error:errors.append(type(error).__name__)
        workers=[threading.Thread(target=read) for _ in range(2)]
        for worker in workers:worker.start()
        for worker in workers:worker.join(2)
        self.assertFalse(errors);self.assertEqual(len(handles),2);self.assertIsNot(handles[0],handles[1])

    def test_missing_reload_and_overlay_capability_are_not_reported_as_visible_pass(self):
        # Native ListItem properties cannot prove arbitrary BINGIE consumers.
        state=importlib.import_module('widget_diagnostics47').status('p')
        self.assertEqual(state['skin_render'],'ANDROID_NOT_TESTED')
        self.assertEqual(state['texture_decode'],'NOT_OBSERVABLE_VIA_LISTITEM')

    def test_actual_88_channel_publication_uses_bounded_page_connections(self):
        self.save_guide()
        records=[dict(stream_id=str(i),category_id='a',name='Station '+str(i),epg_channel_id='xml') for i in range(88)]
        self.index.import_group('p','live','a',records)
        rows,_=importlib.import_module('widget_data41').snapshot(self.portal,'live')
        refresh=importlib.import_module('widget_refresh45');original=sqlite3.connect;opened=[]
        def connect(*a,**kw):opened.append(a[0]);return original(*a,**kw)
        with mock.patch.object(sqlite3,'connect',side_effect=connect),mock.patch('programme_art46.enqueue'):
            self.assertTrue(refresh.publish(self.portal,'live',rows))
        self.assertLessEqual(len(opened),40)
        self.assertEqual(len(refresh.read('p','live')['items']),88)
