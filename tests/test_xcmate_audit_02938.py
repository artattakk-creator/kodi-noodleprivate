"""Standalone audit changes nothing and never claims a live backup is safe."""
import importlib.util,tempfile,unittest
from pathlib import Path

class Audit38(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.root=Path(temp.name)
        spec=importlib.util.spec_from_file_location('audit38',Path(__file__).resolve().parents[1]/'tools/xcmate_readonly_audit_02938.py');self.audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.audit)
        self.source=self.root/'source';self.source.mkdir();(self.source/'media_art_v1').mkdir()
        (self.source/'portals.json').write_text('PRIVATE_PROVIDER_SECRET')
        (self.source/'media_art_v1'/('a'*64+'.img')).write_bytes(b'Existing image bytes')

    def test_inventory_preserves_all_bytes_and_prints_no_private_contents(self):
        before={str(f.relative_to(self.source)):f.read_bytes() for f in self.source.rglob('*') if f.is_file()}
        report=self.audit.audit(self.source)
        self.assertEqual(report['images']['media_art_v1']['files'],1);self.assertNotIn('PRIVATE_PROVIDER_SECRET',str(report));self.assertFalse(report['backup_verified'])
        self.assertEqual({str(f.relative_to(self.source)):f.read_bytes() for f in self.source.rglob('*') if f.is_file()},before)

    def test_backup_requires_matching_bytes_and_explicit_quiescent_confirmation(self):
        import shutil
        backup=self.root/'backup';shutil.copytree(self.source,backup)
        self.assertFalse(self.audit.audit(self.source,backup)['backup_verified']);self.assertTrue(self.audit.audit(self.source,backup,True)['backup_verified'])
        (backup/'portals.json').write_text('changed');self.assertFalse(self.audit.audit(self.source,backup,True)['backup_verified'])

    def test_symlinks_prevent_claiming_full_backup_verification(self):
        import shutil
        outside=self.root/'outside';outside.write_text('OTHER_PROFILE');(self.source/'media_art_v1'/('b'*64+'.img')).symlink_to(outside)
        backup=self.root/'backup';shutil.copytree(self.source,backup,symlinks=True)
        self.assertFalse(self.audit.audit(self.source,backup,True)['backup_verified']);self.assertEqual(outside.read_text(),'OTHER_PROFILE')
