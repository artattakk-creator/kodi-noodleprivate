"""Real source catalogues and asynchronous owner-loop mapping regressions."""
import importlib
import io
import sqlite3
import threading
import time
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest import mock
import xml.etree.ElementTree as ET

import test_xcmate_mini_mapping_02996 as base
from xcmate027_fixture import ADDON


class Mapping482(unittest.TestCase):
    def setUp(self):
        self.owner=base.MiniMapping96(methodName='runTest');self.owner.setUp()
        self.addCleanup(self.owner.doCleanups)
        self.d=self.owner.dialog;self.f=self.owner.fixture
        # The old fixture installs a synchronous _submit: use the real worker.
        self.d._submit=importlib.import_module('guide_mapping48').MappingWindow48._submit.__get__(self.d)
        self.d.source={'id':self.f.bid,'name':'Second XMLTV'}
        self.d.candidate={'id':'xml','name':'Station'}

    def pump(self):
        until=time.monotonic()+3
        while self.d.future is not None:
            self.d.pump()
            if time.monotonic()>until:self.fail('SYNTHETIC_WORKER_NOT_FINISHED')
            time.sleep(.002)

    def names(self):
        names=[('eins.de','Kabel Eins'),('one.de','Kabel 1 HD'),('onehd.de','Kabel1HD'),('plus.de','Kabel 1 +1')]
        self.f.binding.stage_channels('p','names482',self.f.bid,names)
        self.f.binding.finish_channels('p','names482',True)
        return [dict(id=cid,name=name) for cid,name in names]

    def test_normalized_local_suggestions_preserve_ids_and_exclude_unrequested_timeshift(self):
        self.names()
        for query in ('Kabel Eins','Kabel 1 HD','Kabel1HD','DE | Kabel 1 HD'):
            with self.subTest(query=query):
                rows=self.f.binding.channels('p',self.f.bid,query)
                self.assertEqual({r['id'] for r in rows},{'eins.de','one.de','onehd.de'})

    def test_cold_ram_catalogue_uses_same_conservative_name_suggestions(self):
        self.d.cold53.catalogue=(self.f.bid,self.names())
        self.assertEqual({r['id'] for r in self.d.cold53.channels(self.f.portal,self.f.bid,'Kabel1HD',0,lambda:False)},
                         {'eins.de','one.de','onehd.de'})
        self.assertEqual([r['id'] for r in self.d.cold53.channels(self.f.portal,self.f.bid,'Kabel 1 +1',0,lambda:False)],['plus.de'])

    def test_local_and_ram_search_agree_on_punctuation_accents_and_pagination(self):
        names=[('punct','Kabel_1_HD'),('accent','Däs Erste'),('dash','Das-Erste')]
        names += [('bulk%03d'%n,'Kabel_1_HD') for n in range(151)]
        self.f.binding.stage_channels('p','spell482',self.f.bid,names)
        self.f.binding.finish_channels('p','spell482',True)
        self.d.cold53.catalogue=(self.f.bid,[dict(id=i,name=n) for i,n in sorted(names)])  # scan() publishes ID order
        for query,offset in (('Kabel1HD',0),('Kabel1HD',100),('Das Erste',0)):
            with self.subTest(query=query,offset=offset):
                local=self.f.binding.channels('p',self.f.bid,query,offset)
                cold=self.d.cold53.channels(self.f.portal,self.f.bid,query,offset,lambda:False)
                self.assertEqual({r['id'] for r in local},{r['id'] for r in cold})
                self.assertTrue(local)

    def test_source_catalogues_rank_core_station_before_other_families_and_regions(self):
        names=[('a-zdfneo.de','ZDFneo'),('b-zdfinfo.de','ZDFinfo'),
               ('c-zdf.at','AT | ZDF HD'),('d-zdf.de','ZDF SD'),
               ('y-zdf.de','ZDF HD'),('z-zdf.de','ZDF HD (Joyn)')]
        self.f.binding.stage_channels('p','variant100',self.f.bid,names)
        self.f.binding.finish_channels('p','variant100',True)
        self.d.cold53.catalogue=(self.f.bid,[dict(id=cid,name=name) for cid,name in sorted(names)])
        for query in ('DE | Joyn ZDF HD','DE | ZDF HEVC'):
            local=self.f.binding.channels('p',self.f.bid,query,strict482=True)
            ram=self.d.cold53.channels(self.f.portal,self.f.bid,query,0,lambda:False)
            self.assertEqual([r['id'] for r in local],[r['id'] for r in ram])
            self.assertEqual({r['id'] for r in local[:3]},{'d-zdf.de','y-zdf.de','z-zdf.de'})
            if query.endswith('HD'):
                self.assertEqual({r['id'] for r in local[:2]},{'y-zdf.de','z-zdf.de'})
            self.assertEqual({r['id'] for r in local[-2:]},{'a-zdfneo.de','b-zdfinfo.de'})

    def test_existing_guide_archive_without_named_catalogue_can_find_exact_region_channel(self):
        db=self.f.store.connect(write=True)
        try:
            with db:
                for cid in ('ATV2.at','ATV.at'):
                    db.execute('INSERT INTO guide44_inputs VALUES(?,?,?,?,?,?,?,?)',
                               ('p',self.f.bid,cid,self.f.now-60,self.f.now+600,'Show','',2))
        finally:db.close()
        rows=self.f.binding.channels('p',self.f.bid,'AUS | ATV 2 HD',strict482=True)
        self.assertEqual([row['id'] for row in rows],['ATV2.at'])

    def test_candidate_rows_display_only_real_quality_and_region_evidence(self):
        self.f.binding.stage_channels('p','labels100',self.f.bid,[('british.de','Kabel Eins HD')])
        self.f.binding.finish_channels('p','labels100',True)
        self.d.query='Kabel Eins';self.d._channels();self.pump()
        label=getattr(self.d.getControl(200).getListItem(0),'label2','')
        self.assertIn('british.de',label)
        self.assertIn('HD',label)
        self.assertIn('DE',label)

    def test_explicit_cold_load_can_be_retried_after_source_timeout(self):
        self.d.candidate=None;self.d.query='unindexed482';self.d._channels();self.pump()
        self.assertIn('NO_LOCAL_INDEX',self.d.getControl(103).text)
        calls=[]
        @contextmanager
        def transport(*args,**kwargs):
            calls.append(True)
            if len(calls)==1:raise TimeoutError('SYNTHETIC_PRIVATE_URL')
            yield io.BytesIO(b'<tv><channel id="retry482"><display-name>unindexed482</display-name></channel></tv>')
        with mock.patch('stream_epg.source_stream',side_effect=transport):
            self.d.onClick(404);self.pump()
            self.assertIn('SOURCE_TIMEOUT',self.d.getControl(103).text)
            self.assertTrue(self.d.getControl(404).enabled)
            self.assertFalse(self.d.getControl(104).visible)
            self.d.onClick(404);self.pump()
        self.assertEqual(len(calls),2)
        self.assertEqual([r['id'] for r in self.d.rows],['retry482'])

    def test_failed_source_reload_cannot_select_an_old_sources_list_item(self):
        self.d.rows=[dict(id='old-cid',name='Old source result')]
        self.d.getControl(200).addItems([importlib.import_module('xbmcgui').ListItem('Old source result')])
        self.d.source={'id':self.f.aid,'name':'New source'}
        from mapping_search482 import MappingReadError
        with mock.patch('epg_binding48.channels',side_effect=MappingReadError('DB_BUSY')):
            self.d._channels();self.pump()
        self.assertEqual(self.d.rows,[])
        with mock.patch.object(self.d.adapter96,'load_preview',side_effect=AssertionError('STALE_SOURCE')) as load:
            self.d.onClick(200)
        load.assert_not_called();self.assertFalse(self.d.previewed)
        self.assertIsNone(self.d._proof482)

    def test_twenty_thousand_local_channels_reach_late_match_and_confirm_no_match(self):
        rows=[('id%05d'%n,'Unrelated station %05d'%n) for n in range(19999)]+[('zz-valid','Kabel_1_HD')]
        self.f.binding.stage_channels('p','large482',self.f.bid,rows)
        self.f.binding.finish_channels('p','large482',True)
        self.assertEqual([r['id'] for r in self.f.binding.channels('p',self.f.bid,'Kabel1HD',strict482=True)],['zz-valid'])
        self.assertEqual(self.f.binding.channels('p',self.f.bid,'Nonexistent station',strict482=True),[])

    def test_excluded_timeshifts_do_not_hide_the_first_valid_local_match(self):
        rows=[('aa%04d'%n,'Kabel1+1') for n in range(400)]+[('zz-valid','Kabel Eins')]
        self.f.binding.stage_channels('p','shift482',self.f.bid,rows)
        self.f.binding.finish_channels('p','shift482',True)
        self.assertEqual([r['id'] for r in self.f.binding.channels('p',self.f.bid,'Kabel Eins')],['zz-valid'])

    def test_native_grid_can_pump_before_asynchronous_oninit_without_io(self):
        from guide_grid_window import GuideGridWindow
        from xcmate027_fixture import QueuedPool
        with mock.patch('guide_grid_window.ThreadPoolExecutor',QueuedPool):
            window=GuideGridWindow('XCMateGuideGrid.xml',str(ADDON),'Default','720p')
            window.configure(self.f.router,self.f.portal)
        self.addCleanup(window.close)
        with mock.patch.object(window,'_load') as load,mock.patch('media_art.revision',side_effect=AssertionError('PRE_INIT_IO')):
            window.pump()
        load.assert_not_called();self.assertFalse(window._ready)

    def test_local_no_match_never_opens_cold_transport(self):
        self.names();self.d.query='Not a station'
        calls=[]
        @contextmanager
        def transport(*args,**kwargs):
            calls.append(True);yield io.BytesIO(b'<tv/>')
        with mock.patch('stream_epg.source_stream',side_effect=transport):
            self.d._channels();self.pump()
        self.assertEqual(calls,[])
        self.assertIn('NO_MATCH',self.d.getControl(103).text)
        self.assertFalse(self.d.previewed)

    def test_entry_prefills_focused_station_and_opens_actual_source_choices(self):
        self.owner.channel.name='Kabel Eins'
        from guide_mapping48 import MappingWindow48
        from mapping_context96 import MiniAdapter
        d=MappingWindow48('XCMateMapping48.xml',str(ADDON),'Default','720p')
        d.configure(self.owner.parent,MiniAdapter(self.owner.parent,self.owner.channel));self.addCleanup(d.close)
        self.assertEqual(d.query,'Kabel Eins')
        self.d=d;d.onInit();d.source=None
        with mock.patch('menu_icons45.select',return_value=-1) as choose:
            d.pump();self.pump()
        self.assertEqual(choose.call_count,1)
        labels=choose.call_args.args[2]
        self.assertTrue(any('Xtream' in label or 'Anbieter' in label for label in labels))
        self.assertTrue(any('Second XMLTV' in label for label in labels))
        self.assertTrue(all('lokal' in label.lower() or 'Index' in label for label in labels))

    def test_rejected_preview_has_busy_reason_and_recovers_after_slot_release(self):
        module=importlib.import_module('guide_mapping48');module._slots.acquire()
        try:
            self.d._preview()
            self.assertIsNone(self.d.future)
            self.assertIn('MAPPING_BUSY',self.d.getControl(103).text)
            self.assertFalse(self.d.getControl(405).enabled)
            self.assertNotIn('wird gelesen',self.d.getControl(103).text)
        finally:module._slots.release()
        self.d._preview();self.pump()
        self.assertTrue(self.d.previewed)

    def test_timeout_is_classified_and_has_no_private_exception_text(self):
        with mock.patch.object(self.d.adapter96,'load_preview',side_effect=TimeoutError('SYNTHETIC_PRIVATE_URL')):
            self.d._preview();self.pump()
        self.assertIn('SOURCE_TIMEOUT',self.d.getControl(103).text)
        self.assertNotIn('SYNTHETIC_PRIVATE_URL',self.d.getControl(103).text)
        self.assertFalse(self.d.getControl(405).enabled)
        self.d.onClick(406);self.assertTrue(self.d._closed)

    def test_zero_programmes_do_not_authorize_save_or_mutate_mapping(self):
        before=Path(self.f.sources._file_path()).read_bytes()
        self.d.candidate={'id':'missing','name':'Empty'}
        with mock.patch.object(self.d.cold53,'programmes',return_value=[]):
            self.d._preview();self.pump()
        self.assertFalse(self.d.previewed)
        self.assertFalse(self.d.getControl(405).enabled)
        self.assertIn('NO_PROGRAMMES',self.d.getControl(103).text)
        self.d.onClick(405)
        self.assertEqual(Path(self.f.sources._file_path()).read_bytes(),before)

    def test_source_change_during_preview_cancels_old_apply_then_opens_picker(self):
        started=threading.Event();release=threading.Event()
        original=self.d.adapter96.load_preview
        def slow(*args):
            started.set();release.wait(2);return original(*args)
        before=Path(self.f.sources._file_path()).read_bytes()
        with mock.patch.object(self.d.adapter96,'load_preview',side_effect=slow),mock.patch('menu_icons45.select',return_value=-1) as choose:
            self.d._preview();self.assertTrue(started.wait(1))
            self.d.onClick(401);release.set();self.pump()
            self.d.pump();self.pump()
        self.assertEqual(choose.call_count,1)
        self.assertFalse(self.d.previewed)
        self.assertEqual(Path(self.f.sources._file_path()).read_bytes(),before)

    def test_cancel_while_worker_runs_is_immediate_and_late_result_not_applied(self):
        started=threading.Event();release=threading.Event();original=self.d.adapter96.load_preview
        def slow(*args):started.set();release.wait(2);return original(*args)
        with mock.patch.object(self.d.adapter96,'load_preview',side_effect=slow):
            self.d._preview();self.assertTrue(started.wait(1));future=self.d.future
            at=time.monotonic();self.d.onClick(406)
            self.assertLess(time.monotonic()-at,.2);release.set();future.result(timeout=2);self.d.pump()
        self.assertTrue(self.d._closed);self.assertFalse(self.d.previewed)

    def test_status_and_spinner_fit_without_overlap_at_native_coordinates(self):
        root=ET.parse(ADDON/'resources/skins/Default/720p/XCMateMapping48.xml').getroot()
        controls={n.get('id'):n for n in root.iter('control') if n.get('id')}
        status=controls['103'];listing=controls['200']
        # Native720p font13 wraps message+code to three28px lines.
        self.assertGreaterEqual(int(status.findtext('height')),3*28)
        source=controls['105']
        self.assertLessEqual(int(status.findtext('top'))+int(status.findtext('height')),int(source.findtext('top')))
        self.assertLessEqual(int(source.findtext('top'))+int(source.findtext('height')),int(listing.findtext('top')))
        self.assertEqual(int(listing.findtext('height'))%int(listing.find('itemlayout').get('height')),0)
        self.assertLessEqual(int(status.findtext('top'))+int(status.findtext('height')),int(listing.findtext('top')))
        spinner=controls['104']
        self.assertEqual(spinner.get('type'),'image')
        self.assertTrue(spinner.findall('animation'))
        for scale in (1,1.5):
            group=controls['900']
            self.assertLessEqual((int(group.findtext('top'))+int(group.findtext('height')))*scale,720*scale)

    def test_sqlite_busy_is_distinct_from_no_match_and_never_loads_feed(self):
        before=Path(self.f.sources._file_path()).read_bytes()
        with mock.patch('programme_index46.connect',side_effect=sqlite3.OperationalError('database is locked')),mock.patch('stream_epg.source_stream',side_effect=AssertionError('NO_NETWORK')):
            self.d._channels();self.pump()
        self.assertIn('DB_BUSY',self.d.getControl(103).text)
        self.assertFalse(self.d.getControl(405).enabled)
        self.assertEqual(Path(self.f.sources._file_path()).read_bytes(),before)

    def test_configured_source_choices_include_provider_and_only_enabled_optional_sources(self):
        from mapping_search482 import source_rows
        for count in (0,1,5):
            entries=[dict(id='source'+str(i),name='Source '+str(i),enabled=i!=1) for i in range(count)]
            self.f.sources._write_all({'p':dict(sources=entries,mappings={})})
            choices=source_rows(self.f.portal)
            self.assertEqual(choices[0]['id'],'provider')
            self.assertEqual(len(choices),2+sum(s['enabled'] for s in entries))
            self.assertIn('agent', {row['id'] for row in choices})
            self.assertTrue(all('local_count' in row and 'local_code' in row for row in choices))

    def test_source_counts_use_existing_guide_ids_when_name_catalogue_is_missing(self):
        from mapping_search482 import source_rows
        counts={row['id']:row['local_count'] for row in source_rows(self.f.portal)}
        self.assertEqual(counts,{'provider':1,self.f.aid:1,self.f.bid:1,'agent':None})

    def test_cancelled_source_picker_never_leaves_a_false_loading_message(self):
        self.d.source=None
        with mock.patch('menu_icons45.select',return_value=-1):
            self.d._choose_source();self.pump()
        self.assertNotIn('werden lokal gelesen',self.d.getControl(103).text)
        self.assertFalse(self.d.getControl(104).visible)

    def test_source_picker_distinguishes_busy_database_from_missing_index(self):
        self.d.source=None
        with mock.patch('programme_index46.connect',side_effect=sqlite3.OperationalError('database is locked')),mock.patch('menu_icons45.select',return_value=-1) as choose:
            self.d._choose_source();self.pump()
        labels = choose.call_args.args[2]
        self.assertTrue(all('Datenbank belegt' in label for label in labels if 'Agent' not in label))
        self.assertTrue(any('Agent' in label and 'Index nicht verfügbar' in label for label in labels))

    def test_missing_names_require_explicit_cold_load_and_keep_preview_in_ram(self):
        self.d.query='Kabel1HD';calls=[]
        @contextmanager
        def transport(*args,**kwargs):
            calls.append(True)
            yield io.BytesIO(b'<tv><channel id="cold482"><display-name>Kabel 1 HD</display-name></channel></tv>')
        before=Path(self.f.sources._file_path()).read_bytes()
        with mock.patch('stream_epg.source_stream',side_effect=transport):
            self.d._channels();self.pump()
            self.assertEqual(calls,[])
            self.assertIn('NO_LOCAL_INDEX',self.d.getControl(103).text)
            self.assertTrue(self.d.getControl(404).enabled)
            self.d.onClick(404);self.pump()
        self.assertEqual(calls,[True]);self.assertEqual([r['id'] for r in self.d.rows],['cold482'])
        self.assertEqual(Path(self.f.sources._file_path()).read_bytes(),before)


if __name__=='__main__':unittest.main()
