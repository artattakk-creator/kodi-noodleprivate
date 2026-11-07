"""The explicit #385 pre-Android exception applies only to exact .78 bytes."""
import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Release78(unittest.TestCase):
 def setUp(self):
  spec=importlib.util.spec_from_file_location('release78_test',ROOT/'tools/release_channel75.py');self.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.m)
  temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.root=Path(temp.name);self.m.ROOT=self.root
  self.manifest=self.root/'src/plugin.video.xtreammate/addon.xml';self.manifest.parent.mkdir(parents=True)
  self.manifest.write_text('<addon id="plugin.video.xtreammate" version="0.1.29.78"/>')
  package=self.root/'docs/XCMate/test-builds/02978/plugin.video.xtreammate-0.1.29.78.zip';package.parent.mkdir(parents=True);package.write_bytes(b'synthetic exact package')
  self.approval=self.root/'docs/XCMate/releases/user-approved-untested-0.1.29.78.json';self.approval.parent.mkdir()
  self.data=dict(addon_id='plugin.video.xtreammate',version='0.1.29.78',exception_applies_only_to_version='0.1.29.78',user_approved_regular_release=True,user_approved_all_channels=True,android_status='NOT_TESTED',android_pass_claimed=False,authorization_issue=385,sha256=hashlib.sha256(package.read_bytes()).hexdigest())
 def save(self):self.approval.write_text(json.dumps(self.data))
 def test_absent_approval_is_blocked(self):self.assertFalse(self.m.regular_allowed())
 def test_exact_78_explicit_consent_is_allowed_without_faking_android_pass(self):self.save();self.assertTrue(self.m.regular_allowed())
 def test_wrong_hash_or_faked_device_pass_is_rejected(self):
  self.data['sha256']='0'*64;self.save();self.assertFalse(self.m.regular_allowed())
  self.data['android_status']='PASS';self.save();self.assertFalse(self.m.regular_allowed())
 def test_future_version_cannot_inherit_the_78_exception(self):
  self.save();self.manifest.write_text('<addon id="plugin.video.xtreammate" version="0.1.29.79"/>');self.assertFalse(self.m.regular_allowed())
