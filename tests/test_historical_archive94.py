"""Archive cleanup must not erase test coverage or republish old packages."""
import hashlib,importlib.util,tempfile,unittest,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('archive94_contract',ROOT/'tools/run_host94_contract.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class HistoricalInputs94(unittest.TestCase):
 def test_manifest_is_exact_approved_cleanup_and_excludes_all_active_versions(self):
  rows=module.manifest(ROOT);self.assertEqual(len(rows),227)
  self.assertNotIn('plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.90.zip',rows)
  self.assertNotIn('src/plugin.video.xtreammate/addon.xml',rows)
 def test_historical_blob_and_sha256_sidecar_still_match(self):
  name='docs/XCMate/test-builds/02984/plugin.video.xtreammate-0.1.29.84.zip'
  raw=module.read_archived(ROOT,name);side=module.read_archived(ROOT,name+'.sha256')
  self.assertEqual(hashlib.sha256(raw).hexdigest(),side.decode().split()[0])
  self.assertFalse((Path(os.environ.get('XCMATE94_REVIEW_ROOT',str(ROOT)))/name).exists(),'Cleanup must remain in the actual checkout')
 def test_unknown_and_missing_active_inputs_are_never_synthesized(self):
  for name in ('../secret','src/plugin.video.xtreammate/addon.xml','plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.94.zip'):
   with self.assertRaises(FileNotFoundError):module.read_archived(ROOT,name)
 def test_archival_materialization_cannot_write_to_the_reviewed_checkout(self):
  with self.assertRaises(ValueError):module.materialize(ROOT,ROOT)
  with tempfile.TemporaryDirectory() as folder:
   with self.assertRaises(ValueError):module.materialize(ROOT,folder)
