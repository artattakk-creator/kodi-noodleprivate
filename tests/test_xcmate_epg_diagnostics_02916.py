"""Real read-only SQLite evidence, separate short cache, and timeline regressions."""
import importlib,os,sqlite3,sys,time,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,QueuedPool,ADDON

class DiagnosticsTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for n in ('guide_grid_window','guide_grid_data','guide_grid_diagnostics'):sys.modules.pop(n,None)
        self.grid=importlib.import_module('guide_grid_window');self.data=importlib.import_module('guide_grid_data');self.diag=importlib.import_module('guide_grid_diagnostics')
        p=mock.patch.object(self.grid,'ThreadPoolExecutor',QueuedPool);p.start();self.addCleanup(p.stop)
        self.store=importlib.import_module('guide_store');self.origin=int(time.time())//86400*86400+12*3600
        db=self.store.connect()
        with db:
            db.execute('INSERT INTO guide_alias VALUES(?,?,?)',('p','xml','long'))
            for day in range(8):
                for hour in (0,1,2,5,6,12,13,14,15,20,23):
                    start=self.origin+day*86400+(hour-12)*3600
                    db.execute('INSERT INTO programmes VALUES(?,?,?,?,?,?,?)',('p','long',start,start+1800,'Real '+str(day)+'/'+str(hour),'',1))
        db.close()
        self.source=dict(name='EPGShare01',url='https://SECRET.invalid/feed',enabled=True)
        sys.modules['epg_sources'].configuration=lambda pid:dict(mappings={},sources=[self.source])
        sys.modules['epg_status'].source_key=lambda source:'source1'
        sys.modules['epg_status'].read=lambda pid:dict(source1=dict(code='READY',last_success=self.origin))
    def window(self):
        with mock.patch.object(self.grid.time,'time',return_value=self.origin):
            w=self.grid.GuideGridWindow('XCMateGuideGrid.xml',str(ADDON),'Default','720p');w.configure(self.router,self.portal);w.doModal();self.settle(w)
        self.addCleanup(w.close);return w
    def test_diagnostic_reads_whole_selected_channel_horizon_without_mutation_or_network(self):
        w=self.window();before=Path(self.store.path()).read_bytes()
        with mock.patch.object(self.store,'connect',side_effect=AssertionError('DDL forbidden')):
            text=self.diag.inspect(self.portal,w.rows[0],w.origin,w.cursor,w.getFocusId(),self.client)
        self.assertIn('Alias: xml → CID: long',text);self.assertIn('Programme: 88',text)
        self.assertIn('EPGShare01 | READY',text);self.assertIn('Real 7/23',text);self.assertIn('After',text)
        self.assertIn('SHORT_EPG (separater Cache',text);self.assertNotIn('SECRET',text)
        self.assertEqual(Path(self.store.path()).read_bytes(),before);sys.modules['utils'].http_get.assert_not_called()
    def test_authoritative_missing_manual_mapping_is_distinguished_from_provider_coverage(self):
        w=self.window();sys.modules['epg_sources'].configuration=lambda pid:dict(mappings={'1':'missing'},sources=[])
        text=self.diag.inspect(self.portal,w.rows[0],w.origin,w.cursor,w.getFocusId())
        self.assertIn('MANUAL',text);self.assertIn('Alias: missing → CID: missing',text);self.assertIn('Programme: 0',text);self.assertNotIn('Real 7/23',text)
    def test_menu_queries_on_worker_and_shows_on_owner_without_player_or_db_writes(self):
        w=self.window();before=Path(self.store.path()).read_bytes();self.dialog.select.return_value=3
        w.native(7);self.assertTrue(w._diagnosing);self.dialog.textviewer.assert_not_called()
        self.settle(w);self.assertFalse(w._diagnosing);self.dialog.textviewer.assert_called_once()
        self.assertFalse(self.builtins);self.assertFalse(w._closed);self.assertEqual(Path(self.store.path()).read_bytes(),before)
    def test_missing_database_is_not_created_and_short_cache_is_not_long_coverage(self):
        w=self.window();Path(self.store.path()).unlink()
        text=self.diag.inspect(self.portal,w.rows[0],w.origin,w.cursor,w.getFocusId(),self.client)
        self.assertIn('NOT_CREATED',text);self.assertIn('SHORT_EPG',text);self.assertFalse(Path(self.store.path()).exists())
    def test_locked_database_reports_unknown_coverage_without_repair(self):
        w=self.window();db=sqlite3.connect(self.store.path(),timeout=.01)
        db.execute('PRAGMA journal_mode=DELETE');db.execute('BEGIN EXCLUSIVE')
        try:
            started=time.monotonic();text=self.diag.inspect(self.portal,w.rows[0],w.origin,w.cursor,w.getFocusId())
            self.assertLess(time.monotonic()-started,.6);self.assertIn('DB: BUSY',text);self.assertNotIn('Programme: 0',text)
        finally:db.rollback();db.close()
    def test_right_and_left_cross_three_hour_windows_gaps_and_midnight_to_real_last_day(self):
        w=self.window();start=w.cursor;limit=self.origin+7*86400
        for _ in range(500):
            if w.cursor>=limit:break
            previous=w.cursor;w._step(2);self.settle(w)
            self.assertGreater(w.cursor,previous);self.assertGreaterEqual(w.getFocusId(),1000);self.assertFalse(w._loading)
        self.assertGreaterEqual(w.cursor,limit)
        for _ in range(500):
            if w.cursor<=start:break
            previous=w.cursor;w._step(1);self.settle(w);self.assertLess(w.cursor,previous)
        self.assertLessEqual(w.cursor,start);self.assertFalse(self.builtins)
    def test_fully_empty_and_short_only_sender_can_cross_empty_future_windows(self):
        w=self.window();w.row=1
        for r in w.rows:r['events']=[]
        w._render();start=w.cursor
        with mock.patch.object(self.data,'page',side_effect=lambda portal,offset,origin,*a:dict(rows=[dict(r,events=[]) for r in w.rows],total=3,groups=[],origin=origin,offset=offset)):
            for _ in range(55):w._step(2);self.settle(w);self.assertGreaterEqual(w.getFocusId(),1000)
        self.assertEqual(w.cursor,start+55*1800);self.assertIsNone(w._selected())
