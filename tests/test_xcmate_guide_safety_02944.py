"""Isolated SQLite/WAL fixtures only; no device or private guide is accessed."""
import contextlib,hashlib,importlib,io,os,sqlite3,sys,time,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture

class GuideSafety44(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();sys.modules['epg_sources']._channel_name_key=lambda name:str(name).casefold()
        self.g=importlib.import_module('guide_store');self.pub=importlib.import_module('guide_publish44')
        self.backup=importlib.import_module('guide_backup44');self.stream=importlib.import_module('stream_epg')
        self.now=int(time.time());db=self.g.connect();db.close()
    def event(self,start,stop,title='Real',source=0):
        return dict(channel='x',name=title,start_timestamp=start,stop_timestamp=stop,_source_index=source)
    def put_cache(self,events):return self.g.import_cache('p',{'x':events},now=self.now)
    def rows(self):
        db=sqlite3.connect(self.g.path())
        try:return db.execute('SELECT pid,cid,start,stop,title,source FROM programmes ORDER BY pid,cid,start,stop').fetchall()
        finally:db.close()
    def xml(self,events,index=0,source='source-a',cancel=lambda:False):
        def stamp(ts):return time.strftime('%Y%m%d%H%M%S +0000',time.gmtime(ts))
        raw='<tv><channel id="x"><display-name>Channel</display-name></channel>'+''.join('<programme channel="x" start="'+stamp(a)+'" stop="'+stamp(b)+'"><title>'+t+'</title></programme>' for a,b,t in events)+'</tv>'
        @contextlib.contextmanager
        def stream(*a,**kw):yield io.BytesIO(raw.encode())
        with mock.patch.object(self.stream,'source_stream',stream):
            return self.stream.import_source('p',dict(id=source,uri='https://redacted.invalid'),index,[dict(sid='1',name='Channel',epg_channel_id='x')],{},cancel=cancel)
    def legacy(self):
        self.put_cache([self.event(self.now-30,self.now+300)])
        db=sqlite3.connect(self.g.path())
        with db:
            for table in ('guide44_inputs','guide44_outcomes','guide44_authorization','guide44_ranges'):db.execute('DROP TABLE '+table)
        db.close()
    def test_sparse_new_feed_keeps_every_valid_gap_and_future_interval(self):
        events=[self.event(self.now+i*1800,self.now+(i+1)*1800,'Old'+str(i)) for i in range(8)]
        self.put_cache(events);before=self.rows();self.xml([(self.now,self.now+1800,'Correction'),(self.now+7*1800,self.now+8*1800,'Last')])
        rows=self.rows();self.assertEqual(len(rows),8);self.assertEqual(rows[1:-1],before[1:-1]);self.assertEqual(rows[0][4],'Correction')
    def test_short_compatibility_snapshot_cannot_replace_published_long_guide(self):
        self.xml([(self.now+i*1800,self.now+(i+1)*1800,'Long'+str(i)) for i in range(48)])
        before=self.rows();self.put_cache([self.event(self.now,self.now+1800,'Short replacement')]);self.assertEqual(self.rows(),before)
    def test_zero_source_keeps_rows_and_revision(self):
        self.xml([(self.now,self.now+1800,'Good')]);before=self.rows()
        with self.assertRaises(Exception):self.xml([])
        self.assertEqual(self.rows(),before)
    def test_three_sources_fill_real_gaps_without_whole_channel_priority_suppression(self):
        self.xml([(self.now,self.now+1800,'Provider')],0)
        self.xml([(self.now,self.now+1800,'Lower'),(self.now+1800,self.now+3600,'Second')],1,'second')
        self.xml([(self.now+3600,self.now+5400,'Third')],2,'third')
        self.assertEqual([r[4] for r in self.rows()],['Provider','Second','Third'])
    def test_source_ids_survive_equal_channel_and_rank_changes_without_raw_collision(self):
        span=[(self.now,self.now+1800,'A')];self.xml(span,1,'one');self.xml([(self.now,self.now+1800,'B')],2,'two');self.xml(span,3,'one')
        db=sqlite3.connect(self.g.path());rows=db.execute('SELECT source_id,cid,title,rank FROM guide44_inputs').fetchall();db.close()
        self.assertEqual(len(rows),2);self.assertEqual(len({r[0] for r in rows}),2)
        self.assertEqual(next(r[3] for r in rows if r[2]=='A'),3)
    def test_shifted_conflict_preserves_old_full_coverage_instead_of_trimming(self):
        self.put_cache([self.event(self.now,self.now+3600,'Keep')]);before=self.rows()
        result=self.xml([(self.now+10,self.now+1800,'Partial')])
        self.assertEqual(self.rows(),before);self.assertEqual(result['publish_code'],'PARTIAL_PRESERVED')
    def test_identical_source_refresh_does_not_change_published_revision(self):
        span=[(self.now,self.now+1800,'Same')];self.xml(span)
        def revision():
            db=sqlite3.connect(self.g.path());r=db.execute('SELECT * FROM guide_meta').fetchall();db.close();return r
        before=revision();self.xml(span);self.assertEqual(revision(),before)
    def test_seven_calendar_days_are_imported_and_oldest_day_is_not_pruned(self):
        oldest=self.g.day_window(-7,self.now)[0]
        self.xml([(oldest+100,oldest+1800,'History'),(self.now,self.now+1800,'Now')]);before=self.rows()
        self.put_cache([self.event(self.now+1800,self.now+3600,'Next')]);self.assertTrue(set(before)<=set(self.rows()))
        self.assertTrue(any(r[4]=='History' for r in self.rows()))
    def test_legacy_store_requires_explicit_backup_before_any_write_or_network(self):
        self.legacy();before=self.rows()
        with mock.patch.object(self.stream,'source_stream') as remote:
            with self.assertRaises(self.pub.BackupRequired):self.xml([(self.now,self.now+1800,'Wrong')])
            remote.assert_not_called()
        self.assertEqual(self.rows(),before)
        db=sqlite3.connect(self.g.path());self.assertFalse(self.pub.ready(db));db.close()
    def test_opening_legacy_guide_never_reimports_four_event_cache(self):
        self.legacy();before=self.rows();epg=importlib.import_module('epg')
        with mock.patch.object(epg,'load_cache',return_value={'x':[self.event(self.now,self.now+60,'Short')]}) as cache:
            self.assertFalse(self.g.refresh(self.portal));cache.assert_not_called()
        self.assertEqual(self.rows(),before)
    def test_verified_backup_contains_uncheckpointed_wal_and_preserves_original(self):
        self.legacy();db=sqlite3.connect(self.g.path());db.execute('PRAGMA wal_autocheckpoint=0')
        with db:db.execute('INSERT INTO programmes VALUES(?,?,?,?,?,?,?)',('p','x',self.now+300,self.now+600,'In WAL','',1))
        before=self.rows();result=self.backup.authorize(self.g.path());self.assertEqual(self.rows(),before)
        saved=Path(self.g.path()).parent/'guide_backups44'/result['backup'];self.assertEqual(hashlib.sha256(saved.read_bytes()).hexdigest(),result['sha256'])
        copy=sqlite3.connect(saved);self.assertEqual(copy.execute('SELECT count(*) FROM programmes').fetchone()[0],2);copy.close();db.close()
        self.xml([(self.now+600,self.now+900,'After backup')]);self.assertTrue(set(before)<=set(self.rows()))
    def test_cancelled_or_disk_full_backup_never_authorizes_or_changes_legacy_rows(self):
        self.legacy();before=self.rows()
        with self.assertRaises(InterruptedError):self.backup.authorize(self.g.path(),lambda:True)
        with mock.patch('import_budget.check_space',side_effect=OSError(28,'synthetic full')):
            with self.assertRaises(OSError):self.backup.authorize(self.g.path())
        self.assertEqual(self.rows(),before);db=sqlite3.connect(self.g.path());self.assertFalse(self.pub.ready(db));db.close()
    def test_interrupted_publication_rolls_back_all_rows_and_revision(self):
        self.put_cache([self.event(self.now,self.now+1800,'Keep')]);before=self.rows();calls=[0]
        def cancel():calls[0]+=1;return calls[0]>3
        with self.assertRaises(InterruptedError):self.xml([(self.now+1800,self.now+3600,'New')],cancel=cancel)
        self.assertEqual(self.rows(),before)
    def test_busy_store_reports_failure_without_publishing_partial_rows(self):
        self.put_cache([self.event(self.now,self.now+1800,'Keep')]);before=self.rows();db=sqlite3.connect(self.g.path());db.execute('BEGIN IMMEDIATE')
        try:
            with self.assertRaises(sqlite3.OperationalError):self.xml([(self.now+1800,self.now+3600,'Blocked')])
        finally:db.rollback();db.close()
        self.assertEqual(self.rows(),before)
    def test_readonly_diagnostic_does_not_mutate_data_or_include_titles_urls_ids(self):
        self.put_cache([self.event(self.now,self.now+1800,'Private title')]);before=self.rows();result=self.pub.diagnose(self.g.path(),'p')
        self.assertEqual(result['events'],1);self.assertNotIn('Private title',str(result));self.assertNotIn('redacted.invalid',str(result));self.assertEqual(self.rows(),before)
    def test_calendar_window_handles_23_and_25_hour_days(self):
        with mock.patch.dict(os.environ,TZ='Europe/Berlin'):
            time.tzset()
            try:
                for date,hours in (((2026,3,29),23),((2026,10,25),25)):
                    now=time.mktime((*date,12,0,0,0,0,-1));start,stop=self.g.day_window(0,now);self.assertEqual(stop-start,hours*3600)
            finally:
                # tearDown restores TZ; force libc to reread after patch exits.
                pass
        time.tzset()
    def test_day_minus_seven_is_allowed_but_minus_eight_is_not(self):
        w=self.guide_window();w.channels=[]
        for _ in range(9):w._day(-1)
        self.assertEqual(w.day,-7);w._day(1);self.assertEqual(w.day,-6)
    def test_private_source_configuration_is_backed_up_but_never_logged(self):
        self.legacy();config=self.folder/'xtreammate_epg_sources.json';data=b'{"p":{"uri":"https://private.invalid/SECRET"}}';config.write_bytes(data)
        result=self.backup.authorize(self.g.path())
        saved=self.folder/'guide_backups44'/(result['backup']+'.sources.json')
        self.assertEqual(saved.read_bytes(),data);self.assertEqual(config.read_bytes(),data)
        self.assertNotIn('SECRET',str(result));self.assertEqual(saved.stat().st_mode&0o777,0o600)
