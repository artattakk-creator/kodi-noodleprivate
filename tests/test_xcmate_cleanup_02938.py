"""Only temporary profiles: physical counts, explicit delete and DB integrity."""
import hashlib,importlib,json,os,sqlite3,unittest
from pathlib import Path
from unittest import mock
import test_xcmate_artwork_02920 as model

class Cleanup38(unittest.TestCase):
    def setUp(self):
        self.m=model.Artwork20Tests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.config=importlib.import_module('artwork_config');self.config.initialize();self.config.choose('dynamic')
        self.mod=importlib.import_module('artwork_inventory');self.root=self.m.folder/'media_art_v1';self.root.mkdir(exist_ok=True)
        self.other=self.m.folder/'portals.json';self.other.write_text('PRIVATE-PORTAL');self.snapshot=self.other.read_bytes()

    def seed(self,count=2):
        for i in range(count):
            ident=hashlib.sha256(str(i).encode()).hexdigest();(self.root/(ident+'.img')).write_bytes(self.m.png)

    def test_read_only_inventory_counts_physical_images_without_creating_db_or_journal(self):
        self.seed();before=set(self.m.folder.iterdir());value=self.mod.inventory()
        self.assertEqual(value['files'],2);self.assertEqual(value['bytes'],2*len(self.m.png));self.assertEqual(set(self.m.folder.iterdir()),before)
        self.assertFalse(Path(self.mod.filename()).exists())

    def test_empty_archive_is_not_inferred_from_ready_or_job_counts(self):
        value=self.mod.inventory();self.assertEqual(value['files'],0)
        with self.assertRaises(self.mod.InventoryFailure):self.mod.prepare(value,confirmed=True)
        self.assertFalse(Path(self.mod.filename()).exists())

    def test_prepare_and_execute_each_require_explicit_confirmation_and_dynamic_mode(self):
        self.seed();snapshot=self.mod.inventory()
        with self.assertRaises(self.mod.InventoryFailure):self.mod.prepare(snapshot)
        job=self.mod.prepare(snapshot,confirmed=True)
        with self.assertRaises(self.mod.InventoryFailure):self.mod.execute(job)
        self.config.choose('internal')
        with self.assertRaises(self.mod.InventoryFailure):self.mod.execute(job,confirmed=True)
        self.assertEqual(len(list(self.root.glob('*.img'))),2)

    def test_only_owned_hash_images_removed_and_ready_references_become_missing(self):
        self.seed();db=self.m.store.connect()
        with db:
            for file in self.root.glob('*.img'):db.execute("INSERT INTO jobs VALUES(?,'https://image.invalid/source','READY',0,0,0,0,?)",(file.stem,len(self.m.png)))
        db.close();(self.root/'private.sqlite').write_bytes(b'PRIVATE-DB');(self.root/'odd.img').write_bytes(self.m.png)
        job=self.mod.prepare(self.mod.inventory(),confirmed=True);value=self.mod.execute(job,confirmed=True)
        self.assertEqual(value['done'],2);self.assertEqual(value['removed_bytes_this_run'],2*len(self.m.png));self.assertFalse(value['pending'])
        self.assertEqual(self.other.read_bytes(),self.snapshot);self.assertEqual((self.root/'private.sqlite').read_bytes(),b'PRIVATE-DB');self.assertTrue((self.root/'odd.img').exists())
        db=self.m.store.connect();self.assertEqual({r[0] for r in db.execute('SELECT status FROM jobs')},{'MISSING'});db.close()
        self.assertFalse(self.m.store.run_one());self.m.http.assert_not_called()

    def test_symlink_root_files_and_hardlinks_never_delete_outside_profile(self):
        self.seed();external=self.m.folder/'private-image.img';external.write_bytes(self.m.png)
        (self.root/('f'*64+'.img')).symlink_to(external);os.link(external,self.root/('e'*64+'.img'))
        value=self.mod.inventory();self.assertEqual(value['files'],2)
        self.mod.execute(self.mod.prepare(value,confirmed=True),confirmed=True)
        self.assertEqual(external.read_bytes(),self.m.png);self.assertTrue((self.root/('f'*64+'.img')).is_symlink())

    def test_changed_source_and_replaced_root_fail_without_removing_new_file(self):
        self.seed();snapshot=self.mod.inventory();job=self.mod.prepare(snapshot,confirmed=True)
        first=next(self.root.glob('*.img'));first.write_bytes(self.m.png+b'changed')
        with self.assertRaises(self.mod.InventoryFailure):self.mod.execute(job,confirmed=True)
        self.assertTrue(first.exists());self.assertEqual(self.other.read_bytes(),self.snapshot)

    def test_cancel_and_manual_resume_remove_no_extra_files(self):
        self.seed(5);job=self.mod.prepare(self.mod.inventory(),confirmed=True);calls=[0]
        def cancel():calls[0]+=1;return calls[0]>2
        first=self.mod.execute(job,confirmed=True,cancel=cancel);self.assertEqual(first['done'],2);self.assertTrue(first['pending'])
        self.assertEqual(self.mod.pending()['files'],3)
        second=self.mod.execute(job,confirmed=True);self.assertEqual(second['done'],3);self.assertIsNone(self.mod.pending())
        self.assertEqual(self.other.read_bytes(),self.snapshot)

    def test_db_busy_after_unlink_preserves_journal_and_can_be_reconciled_once(self):
        self.seed(1);job=self.mod.prepare(self.mod.inventory(),confirmed=True)
        with mock.patch.object(self.mod,'_reconcile',side_effect=sqlite3.OperationalError('locked')):
            with self.assertRaises(sqlite3.OperationalError):self.mod.execute(job,confirmed=True)
        self.assertEqual(self.mod.pending()['files'],1)
        value=importlib.reload(self.mod).execute(job,confirmed=True);self.assertEqual(value['removed_bytes_this_run'],0);self.assertFalse(value['pending'])

    def test_new_images_after_inventory_are_preserved(self):
        self.seed(1);job=self.mod.prepare(self.mod.inventory(),confirmed=True)
        path=self.root/('a'*64+'.img');path.write_bytes(self.m.png)
        self.mod.execute(job,confirmed=True);self.assertTrue(path.exists())

    def test_status_has_localized_physical_values_and_separate_queue_counts(self):
        self.seed();module=importlib.import_module('artwork_status');data=module.collect();text=module.text(data)
        self.assertIn('2',text);self.assertIn('MiB',text);self.assertNotIn('PRIVATE-PORTAL',text);self.assertNotIn('"counts"',text)
        self.assertEqual(data['physical']['files'],2);self.assertEqual(self.other.read_bytes(),self.snapshot)
