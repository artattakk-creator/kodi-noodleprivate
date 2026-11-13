"""Current .93 scope and exact candidate: old .91 tests remain historical."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from stabilization_contract93 import delta93,without93
class Release93(unittest.TestCase):
 def test_entire_runtime_matches_reviewed_delta_and_no_unknown_module_is_admitted(self):
  delta=delta93();base=delta['base'];prefix='src/plugin.video.xtreammate/'
  paths=subprocess.check_output(['git','ls-tree','-r','--name-only',base,prefix],cwd=ROOT).decode().splitlines()
  source={p.relative_to(ROOT).as_posix():p.read_bytes() for p in (ROOT/'src/plugin.video.xtreammate').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
  self.assertEqual(set(source),set(paths)|set(delta['added']))
  for name,change in delta['modules'].items():
   self.assertEqual(hashlib.sha256(source[name]).hexdigest(),change['new_sha256']);self.assertEqual(without93(source[name],name),change['old'].encode())
   self.assertEqual(without93(source[name]+b'\nUNREVIEWED\n',name),source[name]+b'\nUNREVIEWED\n')
  for name,digest in delta['added'].items():self.assertEqual(hashlib.sha256(source[name]).hexdigest(),digest)
  for name in set(paths)-set(delta['modules']):self.assertEqual(source[name],subprocess.check_output(['git','show',base+':'+name],cwd=ROOT))
 def test_fallback90_bytes_are_preserved_in_both_existing_channels(self):
  for relative in ('plugin.video.xtreammate/','online-test/plugin.video.xtreammate/'):
   file=ROOT/relative/'plugin.video.xtreammate-0.1.29.90.zip';digest=hashlib.sha256(file.read_bytes()).hexdigest()
   self.assertEqual(digest,'e95b0a0cc46e745a3318a609e6e57a005ee3a88965f6e7de0c4b21c68f30f17f');self.assertIn(digest,Path(str(file)+'.sha256').read_text())
 def test_current_zip_is_reproducible_crc_clean_and_matches_all_source_bytes(self):
  import release_candidate93 as candidate
  from package_xcmate71 import build
  original=ROOT/'docs/XCMate/test-builds/02993'/candidate.NAME
  with tempfile.TemporaryDirectory() as folder:
   proof=build(folder);self.assertEqual(proof,candidate.inspect_package(original));self.assertEqual((Path(folder)/candidate.NAME).read_bytes(),original.read_bytes())
 def test_offline_proposal_does_not_publish_or_authorize_merge(self):
  import release_candidate93 as candidate
  result=candidate.verify(ROOT/'docs/XCMate/test-builds/02993')
  self.assertFalse(result['repository_released']);self.assertEqual(result['android'],'ANDROID_NOT_TESTED')
  plan=json.loads((ROOT/'docs/XCMate/test-builds/02993/pilot-plan.json').read_text());self.assertFalse(plan['source_merged']);self.assertFalse(plan['merge_or_publish_authorized'])
