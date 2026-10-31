"""Private source copy, explicit two opt-ins and safe visible Back."""
import hashlib,importlib,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture
from test_xcmate_tmdb_token_02961 import FIXTURE

class TokenUi63(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.t=importlib.import_module('tmdb_token61');self.ui=importlib.import_module('tmdb_access61');self.path=Path(self.t.location())
  self.source=self.folder/'arbitrary-name.txt';self.source.write_bytes(FIXTURE)
  self.dialog.browseSingle=mock.Mock(return_value=str(self.source))
 def test_smb_bytes_are_copied_once_to_private_target_without_enabling_on_plain_import(self):
  self.dialog.browseSingle.return_value='smb://fixture/share/another-name.txt';self.dialog.select.side_effect=[0,-1]
  with mock.patch('tmdb_import63.selected',return_value=FIXTURE) as read:self.ui.show()
  read.assert_called_once();self.assertEqual(self.path.read_bytes(),FIXTURE+b'\n');self.assertEqual(self.path.stat().st_mode&0o777,0o600)
  self.assertNotIn('programme_tmdb46',self.options);self.assertNotIn('tmdb_research43',self.options)
  self.assertNotIn(FIXTURE.decode(),str(self.dialog.ok.call_args_list))
 def test_import_and_activation_requires_explicit_separate_choice_and_confirmation(self):
  self.dialog.select.side_effect=[6,-1];self.dialog.yesno.return_value=False;self.ui.show()
  self.assertFalse(self.path.exists());self.assertNotIn('programme_tmdb46',self.options)
  self.dialog.select.side_effect=[6,-1];self.dialog.yesno.return_value=True;self.ui.show()
  self.assertEqual(self.options['programme_tmdb46'],'true');self.assertEqual(self.options['tmdb_research43'],'true')
  self.assertEqual(self.source.read_bytes(),FIXTURE);self.assertTrue(self.path.exists())
 def test_masked_direct_entry_uses_existing_setting_if_no_file_and_guides_invalid_file_replacement(self):
  self.dialog.select.side_effect=[7,-1];self.dialog.input.return_value=FIXTURE.decode();self.ui.show()
  self.assertEqual(self.options['tmdb_read_token43'],FIXTURE.decode());self.assertFalse(self.path.exists())
  self.assertTrue(self.dialog.input.call_args.kwargs.get('option'))
  self.path.write_bytes(b'invalid');self.dialog.select.side_effect=[7,-1];self.dialog.yesno.return_value=False
  self.ui.show();self.assertEqual(self.path.read_bytes(),b'invalid')
  self.dialog.select.side_effect=[7,-1];self.dialog.yesno.return_value=True;self.ui.show()
  self.assertEqual(self.path.read_bytes(),FIXTURE+b'\n')
 def test_destination_change_or_write_failure_never_overwrites_without_matching_confirmation(self):
  self.path.write_bytes(b'previous');before=hashlib.sha256(b'previous').hexdigest()
  self.path.write_bytes(b'changed')
  with self.assertRaises(self.t.TokenError):self.t.import_bytes(FIXTURE,before)
  self.assertEqual(self.path.read_bytes(),b'changed')
  with mock.patch.object(self.t.os,'replace',side_effect=OSError('fixture private path')),self.assertRaises(self.t.TokenError) as exc:self.t.import_bytes(FIXTURE,hashlib.sha256(b'changed').hexdigest())
  self.assertEqual(exc.exception.code,'TOKEN_WRITE');self.assertEqual(self.path.read_bytes(),b'changed')
 def test_android_private_profile_anchor_resolves_only_trusted_root_and_creates_private_children(self):
  profile=self.folder/'physical-profile';profile.mkdir()
  suffix='/addon_data/plugin.video.xtreammate/'+self.t.NAME
  with mock.patch('xbmcvfs.translatePath',return_value='/storage/fixture-profile'+suffix),mock.patch.object(self.t.os.path,'realpath',return_value=str(profile)) as resolve:
   self.assertEqual(self.t.location(),str(profile)+suffix)
   self.assertEqual(self.t.status(),'FILE_MISSING')
   self.t.import_bytes(FIXTURE,None)
   target=profile/'addon_data/plugin.video.xtreammate'/self.t.NAME
   self.assertEqual(target.read_bytes(),FIXTURE+b'\n');self.assertEqual(target.stat().st_mode&0o777,0o600)
   self.assertTrue(all(call.args[0]=='/storage/fixture-profile' for call in resolve.call_args_list))
 def test_profile_change_before_confirmation_is_not_written_to_another_profile(self):
  with self.assertRaises(self.t.TokenError) as exc:self.t.import_bytes(FIXTURE,None,target=str(self.folder/'other-profile'/self.t.NAME))
  self.assertEqual(exc.exception.code,'TOKEN_CHANGED');self.assertFalse(self.path.exists())
