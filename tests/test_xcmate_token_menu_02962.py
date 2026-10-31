import importlib,unittest
from unittest import mock
from xcmate027_fixture import Fixture
class TokenMenu62(Fixture,unittest.TestCase):
 def test_visible_back_index_four_and_remote_back_never_change_options_or_confirm(self):
  ui=importlib.import_module('tmdb_access61')
  for choice in (4,-1):
   self.dialog.select.return_value=choice;self.dialog.yesno.reset_mock();before=dict(self.options);ui.show()
   self.assertEqual(self.options,before);self.dialog.yesno.assert_not_called()
 def test_disable_is_separate_from_back_and_requires_explicit_confirmation(self):
  ui=importlib.import_module('tmdb_access61');self.options.update(programme_tmdb46=True,tmdb_research43=True)
  self.dialog.select.side_effect=[5,-1];self.dialog.yesno.return_value=False;ui.show();self.assertTrue(self.options['programme_tmdb46'])
  self.dialog.select.side_effect=[5,-1];self.dialog.yesno.return_value=True;ui.show();self.assertEqual(self.options['programme_tmdb46'],'false')
 def test_local_file_and_kodi_paths_are_translated_without_following_selected_symlinks(self):
  token=importlib.import_module('tmdb_token61');p=self.folder/'read token.txt';p.write_text('local fixture')
  self.assertEqual(token.import_source_path(p.as_uri()),str(p))
  with mock.patch('xbmcvfs.translatePath',return_value=str(p)):self.assertEqual(token.import_source_path('special://profile/read.txt'),str(p))
  for path in ('smb://server/private.txt','content://provider/document/1','file://remote/path.txt','file:///tmp/../private.txt','special://unknown/x'):
   with self.assertRaises(token.TokenError):token.import_source_path(path)
