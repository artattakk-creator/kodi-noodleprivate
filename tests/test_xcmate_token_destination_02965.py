"""Real private anchors, root-denied Android-like access, no secret credentials."""
import errno,hashlib,importlib,os,stat,sys,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture
from test_xcmate_tmdb_token_02961 import FIXTURE
class Destination65(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp()
  self.profile=self.folder/'kodi-profile65';self.profile.mkdir()
  def translate(value):
   prefix='special://profile/'
   return str(self.profile/value[len(prefix):]) if value.startswith(prefix) else value
  patch=mock.patch.object(sys.modules['xbmcvfs'],'translatePath',side_effect=translate);patch.start();self.addCleanup(patch.stop)
  self.tokens=importlib.import_module('tmdb_token61');self.dest=importlib.import_module('token_destination65');self.writer=importlib.import_module('token_write64')
  self.path=Path(self.tokens.location());self.tokens._cache=None
 def prepare(self):return self.writer.read_destination(self.tokens,str(self.path),initialize=True)
 def test_missing_private_parent_is_missing_without_status_write_then_explicitly_initialized(self):
  self.assertIsNone(self.tokens.read(str(self.path),missing=True));self.assertFalse(self.path.parent.exists())
  self.assertIsNone(self.prepare());self.assertTrue(self.path.parent.is_dir());self.assertFalse(self.path.exists())
  self.assertEqual(self.path.parent.stat().st_mode&0o777,0o700)
 def test_root_listing_denied_does_not_block_authoritative_profile_pre_read_or_import(self):
  original=os.open
  def opened(path,*args,**kwargs):
   if path=='/':raise PermissionError(errno.EACCES,'private root denied')
   return original(path,*args,**kwargs)
  with mock.patch.object(self.dest.os,'open',side_effect=opened):
   self.assertIsNone(self.prepare());self.assertEqual(self.tokens.import_bytes(FIXTURE,None),'IMPORTED')
   self.assertEqual(self.tokens.read(str(self.path)),FIXTURE+b'\n')
 def test_unsupported_directory_flag_uses_checked_descriptor_without_following_symlinks(self):
  original=os.open
  def opened(path,flags,*args,**kwargs):
   if flags&getattr(os,'O_DIRECTORY',0):raise OSError(errno.EINVAL,'FUSE flag unsupported')
   return original(path,flags,*args,**kwargs)
  with mock.patch.object(self.dest.os,'open',side_effect=opened):self.assertIsNone(self.prepare())
  self.assertTrue(self.path.parent.is_dir())
 def test_search_only_profile_can_use_opath_while_private_descendants_are_checked(self):
  if not hasattr(os,'O_PATH'):self.skipTest('POSIX O_PATH unavailable')
  original=os.open
  def opened(path,flags,*args,**kwargs):
   if path==str(self.profile) and not flags&os.O_PATH:raise PermissionError(errno.EACCES,'directory listing unavailable')
   return original(path,flags,*args,**kwargs)
  with mock.patch.object(self.dest.os,'open',side_effect=opened):self.assertIsNone(self.prepare())
 def test_private_ancestor_symlink_is_not_a_mount_alias_exception(self):
  outside=self.folder/'outside';outside.mkdir();(self.profile/'addon_data').symlink_to(outside,target_is_directory=True)
  with self.assertRaises(self.tokens.TokenError):self.prepare()
  self.assertEqual(list(outside.iterdir()),[])
 def test_regular_existing_token_and_invalid_readable_file_keep_explicit_overwrite_guard(self):
  self.prepare();self.path.write_bytes(b'invalid existing bytes')
  before=self.prepare();self.assertEqual(before,b'invalid existing bytes')
  with self.assertRaises(self.tokens.TokenError):self.tokens.import_bytes(FIXTURE,None)
  self.assertEqual(self.path.read_bytes(),before)
  self.tokens.import_bytes(FIXTURE,hashlib.sha256(before).hexdigest());self.tokens._cache=None
  self.assertEqual(self.tokens.effective_tmdb_read_token(True),FIXTURE.decode())
 def test_source_and_destination_symlinks_are_rejected_without_explicit_recovery(self):
  self.prepare();outside=self.folder/'source';outside.write_bytes(FIXTURE);self.path.symlink_to(outside)
  with self.assertRaises(self.tokens.TokenError) as raised:self.prepare()
  self.assertEqual(raised.exception.subcode,'SYMLINK_OR_NOT_DIRECTORY');self.assertEqual(outside.read_bytes(),FIXTURE)
  with self.assertRaises(self.tokens.TokenError):self.tokens.read(str(self.path))
 def test_recovery_decline_preserves_entry_and_source(self):
  self.prepare();outside=self.folder/'original';outside.write_bytes(FIXTURE);self.path.symlink_to(outside);self.dialog.yesno.return_value=False
  with self.assertRaises(self.dest.Cancelled65):self.dest.pre_read(self.tokens,str(self.path),self.dialog,sys.modules['xbmcgui'])
  self.assertTrue(self.path.is_symlink());self.assertFalse(list(self.path.parent.glob('.tmdb-preserved65-*')))
 def test_explicit_recovery_quarantines_only_leaf_without_following_or_deleting_target(self):
  self.prepare();outside=self.folder/'original';outside.write_bytes(FIXTURE);self.path.symlink_to(outside);self.dialog.yesno.return_value=True
  self.assertIsNone(self.dest.pre_read(self.tokens,str(self.path),self.dialog,sys.modules['xbmcgui']))
  saved=list(self.path.parent.glob('.tmdb-preserved65-*'));self.assertEqual(len(saved),1);self.assertTrue(saved[0].is_symlink())
  self.assertEqual(outside.read_bytes(),FIXTURE);self.tokens.import_bytes(FIXTURE,None)
  self.assertFalse(self.path.is_symlink());self.assertEqual(outside.read_bytes(),FIXTURE)
 def test_recovery_inode_race_is_rejected_and_new_bytes_preserved(self):
  self.prepare();self.path.write_bytes(b'old');expected=self.dest.recovery_state(str(self.path))
  self.path.unlink();self.path.write_bytes(b'new protected data')
  with self.assertRaises(self.tokens.TokenError):self.dest.quarantine(str(self.path),expected)
  self.assertEqual(self.path.read_bytes(),b'new protected data')
 def test_nonregular_leaf_directory_is_not_automatically_recovered(self):
  self.prepare();self.path.mkdir()
  self.assertIsNone(self.dest.recovery_state(str(self.path)))
  with self.assertRaises(self.tokens.TokenError) as raised:self.prepare()
  self.assertEqual(raised.exception.subcode,'NOT_REGULAR')
 def test_permission_io_and_unsafe_path_subcodes_retain_errno_without_raw_data(self):
  expected={errno.EACCES:'ACCESS_DENIED',errno.EPERM:'ACCESS_DENIED',errno.ELOOP:'SYMLINK_OR_NOT_DIRECTORY',errno.ENOTDIR:'SYMLINK_OR_NOT_DIRECTORY',errno.EIO:'IO_ERROR',errno.EROFS:'READ_ONLY',errno.ENOTSUP:'DIRECTORY_UNSUPPORTED'}
  for number,code in expected.items():
   with self.subTest(errno=number):
    value=self.dest.failure('TOKEN_UNREADABLE',OSError(number,'private path '+str(self.path)))
    self.assertEqual(value.errno,number);self.assertEqual(value.subcode,code);self.assertNotIn(str(self.path),str(value))
 def test_log_contains_normalized_subcode_and_no_secret_or_path(self):
  logged=[]
  with mock.patch('xbmc.LOGINFO',1,create=True),mock.patch('xbmc.log',side_effect=lambda v,*a:logged.append(v),create=True):
   self.writer.note('PRIVATE_DESTINATION_READ','FAILED',errno.EACCES,subcode='ACCESS_DENIED')
  self.assertIn('subcode=ACCESS_DENIED',''.join(logged));self.assertNotIn(FIXTURE.decode(),''.join(logged));self.assertNotIn(str(self.path),''.join(logged))
 def test_manual_input_uses_same_safe_pre_read_and_masked_setting_path(self):
  self.dialog.input.return_value=FIXTURE.decode()
  ui=importlib.import_module('tmdb_access61')
  ui.imported(7,self.dialog,sys.modules['xbmcaddon'].Addon(),sys.modules['xbmcgui'],self.tokens)
  self.assertEqual(self.options.get('tmdb_read_token43'),FIXTURE.decode());self.assertFalse(self.path.exists())
