"""Real atomic catalog heads: 45/883 groups, interruption and exact resume."""
import importlib,sqlite3,time,unittest
from pathlib import Path
from unittest import mock
import test_xcmate_setup_0294 as old

class Catalog54(unittest.TestCase):
    def setUp(self):
        self.m=old.StorageTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.d=self.m.draft;self.d.phased54=True
        self.d.categories={'live':[dict(category_id=str(n),category_name='Group '+str(n)) for n in range(1,884)],'vod':[],'series':[]}
        self.d.selected={'live':set(map(str,range(1,46))),'vod':set(),'series':set()};self.calls=[];self.fail=None
        def entries(kind,cid,cancel,allowed):
            self.calls.append((kind,cid))
            for n in range(2):
                yield dict(stream_id=cid+'-'+str(n),category_id=cid,name='Station '+cid+' '+str(n),epg_channel_id='xml')
                if cid==self.fail:raise InterruptedError('synthetic interruption')
        self.d.adapter.entries=entries
    def test_45_of_883_groups_checkpoint_38_before_interrupt_and_retry_only_missing(self):
        self.fail='39'
        with self.assertRaises(InterruptedError):self.d.scan()
        self.assertEqual(len(self.calls),39);self.assertFalse(self.d.scanned)
        self.assertEqual(self.m.index.Reader(self.d.pid,self.d.index).page('live',limit=1)[1],76)
        before=Path(self.d.index).stat().st_ino;self.calls.clear();self.fail=None;messages=[];self.d.scan(status=lambda *v:messages.append(v))
        self.assertEqual([cid for k,cid in self.calls],list(map(str,range(39,46))))
        self.assertEqual(Path(self.d.index).stat().st_ino,before);self.assertEqual(self.d.report['live'],90)
        self.assertTrue(any('Gruppe 39 von 45' in t for p,t in messages));self.assertEqual(self.m.portals.load_all(),[self.m.portal])
    def test_portal_published_before_any_epg_and_stays_usable_after_epg_failure(self):
        self.d.epg_sources=[dict(id='feed',name='Public',uri='https://public.invalid/feed.xml',enabled=True)]
        self.d.scan();self.d._scan_epg=mock.Mock(side_effect=AssertionError('must not scan EPG before save'))
        portal=self.d.save();self.assertEqual(self.m.index.Reader(portal['id']).page('live',limit=1)[1],90)
        self.assertTrue(importlib.import_module('wizard_epg54').pending(portal));self.assertEqual(self.m.portals.get_by_id('p'),self.m.portal)
        self.assertEqual(self.d.save()['id'],portal['id']);self.assertEqual(len(self.m.portals.load_all()),2)
    def test_changed_selection_imports_only_new_group_and_hides_deselected_head(self):
        self.d.scan();self.calls.clear();self.d.selected['live'].remove('5');self.d.selected['live'].add('46');self.d.scan()
        self.assertEqual(self.calls,[('live','46')]);self.assertEqual(self.d.report['live'],90)
        db=sqlite3.connect(self.d.index)
        self.assertIsNone(db.execute('SELECT 1 FROM heads WHERE pid=? AND cid=?',(self.d.pid,'5')).fetchone());db.close()
        self.calls.clear();self.d.selected['live'].add('5');self.d.scan();self.assertEqual(self.calls,[]);self.assertEqual(self.d.report['live'],92)
    def test_modified_completed_group_is_revalidated_and_only_it_is_reimported(self):
        self.d.scan();db=sqlite3.connect(self.d.index)
        with db:db.execute("UPDATE items_v2 SET payload='{}' WHERE pid=? AND cid='2'",(self.d.pid,))
        db.close();self.calls.clear();self.d.scan();self.assertEqual(self.calls,[('live','2')])
    def test_changed_group_identity_or_expired_receipt_invalidates_only_that_unit(self):
        self.d.scan();self.calls.clear();self.d.categories['live'][2]['category_name']='Changed group'
        self.d.scan();self.assertEqual(self.calls,[('live','3')]);self.calls.clear()
        db=sqlite3.connect(self.d.index)
        with db:db.execute("UPDATE wizard_units54 SET completed=? WHERE pid=? AND cid='8'",(time.time()-90000,self.d.pid))
        db.close();self.d.scan();self.assertEqual(self.calls,[('live','8')])
    def test_partial_checkpoint_survives_new_session_and_does_not_serialize_password(self):
        resume=importlib.import_module('wizard_resume53');s=resume.Session();self.d.resume53=s;s.live=self.d
        s.checkpoint(self.d,'groups',categories=True);self.fail='3'
        with self.assertRaises(InterruptedError):self.d.scan()
        saved=Path(resume.root(),'current.json').read_text();self.assertNotIn('SECRET',saved)
        restored=resume.Session.load();d=restored.restore(dict(restored.data,xc_pass='new synthetic'));d.resume53=restored;d.phased54=True
        d.adapter=self.d.adapter;self.calls.clear();self.fail=None;d.scan()
        self.assertEqual([c for k,c in self.calls],list(map(str,range(3,46))));self.assertEqual(d.report['live'],90)
    def test_sqlite_error_is_not_a_complete_checkpoint_or_portal(self):
        with mock.patch('wizard_catalog54.digest_rows',side_effect=sqlite3.OperationalError('synthetic busy')):
            with self.assertRaises(sqlite3.Error):self.d.scan()
        self.assertFalse(self.d.scanned);self.assertEqual(self.m.portals.load_all(),[self.m.portal])
    def test_empty_completed_group_does_not_restart_on_every_retry(self):
        original=self.d.adapter.entries
        def rows(kind,cid,cancel,allowed):
            if cid=='1':self.calls.append((kind,cid));return
            yield from original(kind,cid,cancel,allowed)
        self.d.adapter.entries=rows;self.d.scan();self.calls.clear();self.d.scan()
        self.assertEqual(self.calls,[]);self.assertEqual(self.d.report['live'],88)
    def test_old_53_epg_staging_never_blocks_new_catalog_portal_publication(self):
        Path(self.d.guide).write_bytes(b'preserved incomplete old guide')
        before=Path(self.d.guide).read_bytes();self.d.scan();portal=self.d.save()
        self.assertEqual(self.m.index.Reader(portal['id']).page('live',limit=1)[1],90)
        self.assertEqual(Path(self.d.guide).read_bytes(),before)
    def test_unfinished_group_has_explicit_partial_attempt_not_complete_receipt(self):
        self.fail='4'
        with self.assertRaises(InterruptedError):self.d.scan()
        db=sqlite3.connect(self.d.index)
        try:
            self.assertEqual(db.execute("SELECT state FROM wizard_attempts54 WHERE pid=? AND cid='4'",(self.d.pid,)).fetchone()[0],'PARTIAL')
            self.assertIsNone(db.execute("SELECT 1 FROM wizard_units54 WHERE pid=? AND cid='4'",(self.d.pid,)).fetchone())
        finally:db.close()
    def test_nonempty_but_invalid_provider_rows_are_not_checkpointed_as_empty_success(self):
        self.d.adapter.entries=lambda *a,**k:iter([{}])
        with self.assertRaises(ValueError):self.d.scan()
        self.assertFalse(self.d.scanned);self.assertEqual(self.m.portals.load_all(),[self.m.portal])
    def test_owned_partial_53_draft_adopts_valid_atomic_heads_without_reimport(self):
        resume=importlib.import_module('wizard_resume53');s=resume.Session();s.live=self.d;self.d.resume53=s
        self.d.scan();db=sqlite3.connect(self.d.index)
        with db:db.execute('DROP TABLE wizard_units54');db.execute('DROP TABLE wizard_attempts54')
        db.close();self.d.scanned=False;self.d._scan_signature=None;s.checkpoint(self.d,'groups',categories=True)
        restarted=resume.Session.load();d=restarted.restore(dict(restarted.data,xc_pass='synthetic reentry'));d.resume53=restarted;d.phased54=True;d.adapter=self.d.adapter
        self.calls.clear();d.scan();self.assertEqual(self.calls,[]);self.assertEqual(d.report['live'],90)
    def test_unproven_legacy_head_is_not_trusted_without_owned_resume(self):
        self.d.scan();db=sqlite3.connect(self.d.index)
        with db:db.execute('DROP TABLE wizard_units54');db.execute('DROP TABLE wizard_attempts54')
        db.close();self.calls.clear();self.d.scan();self.assertEqual(len(self.calls),45)
    def test_old_unpublished_53_epg_is_retained_even_after_catalog_setup_completion(self):
        resume=importlib.import_module('wizard_resume53');s=resume.Session();s.live=self.d;self.d.resume53=s
        Path(self.d.guide).write_bytes(b'preserved old EPG work');self.d.scan();self.d.save();s.checkpoint(self.d,'epg_ready');self.d.dispose()
        self.assertTrue(Path(self.d.guide).is_file());self.assertEqual(Path(self.d.guide).read_bytes(),b'preserved old EPG work')
