"""Real private-file transactions, bounded errors and synthetic credentials only."""
import errno,hashlib,importlib,os,stat,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture
from test_xcmate_tmdb_token_02961 import FIXTURE

class Write64(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.t=importlib.import_module('tmdb_token61');self.w=importlib.import_module('token_write64');self.path=Path(self.t.location())
 def test_normal_atomic_copy_is_private_and_survives_interpreter_cache_reset(self):
  self.assertEqual(self.t.import_bytes(FIXTURE,None),'IMPORTED')
  self.assertEqual(self.path.read_bytes(),FIXTURE+b'\n');self.assertEqual(self.path.stat().st_mode&0o777,0o600)
  self.t._cache=None;self.assertEqual(self.t.effective_tmdb_read_token(force=True),FIXTURE.decode())
 def test_directory_sync_errors_after_commit_are_verified_warning_not_false_failed_import(self):
  original=os.fsync
  for number in (errno.EINVAL,errno.ENOTSUP,errno.EACCES,errno.EROFS,errno.EIO):
   with self.subTest(errno=number):
    before=self.path.read_bytes() if self.path.exists() else None
    expected=hashlib.sha256(before).hexdigest() if before is not None else None
    def sync(fd):
     if stat.S_ISDIR(os.fstat(fd).st_mode):raise OSError(number,'secret-bearing raw text must not escape')
     return original(fd)
    with mock.patch.object(self.w.os,'fsync',side_effect=sync):
     self.assertEqual(self.t.import_bytes(FIXTURE,expected),'IMPORTED_SYNC_WARNING')
    self.assertEqual(self.path.read_bytes(),FIXTURE+b'\n');self.assertEqual(self.t.status(),'FILE_VALID')
 def test_file_sync_failure_keeps_existing_file_unchanged(self):
  self.path.write_bytes(b'existing protected bytes')
  expected=hashlib.sha256(self.path.read_bytes()).hexdigest();original=os.fsync
  def sync(fd):
   if not stat.S_ISDIR(os.fstat(fd).st_mode):raise OSError(errno.EIO,'private failure')
   return original(fd)
  with mock.patch.object(self.w.os,'fsync',side_effect=sync),self.assertRaises(self.t.TokenError) as result:self.t.import_bytes(FIXTURE,expected)
  self.assertEqual(result.exception.stage,'FILE_FSYNC');self.assertFalse(result.exception.committed)
  self.assertEqual(self.path.read_bytes(),b'existing protected bytes')
 def test_rename_failure_preserves_old_destination_and_reports_precise_stage(self):
  self.path.write_bytes(b'original');expected=hashlib.sha256(b'original').hexdigest()
  with mock.patch.object(self.w.os,'replace',side_effect=OSError(errno.EROFS,'private path')),self.assertRaises(self.t.TokenError) as result:self.t.import_bytes(FIXTURE,expected)
  self.assertEqual(result.exception.stage,'ATOMIC_RENAME');self.assertEqual(result.exception.code,'TOKEN_WRITE');self.assertFalse(result.exception.committed)
  self.assertEqual(self.path.read_bytes(),b'original');self.assertFalse(list(self.path.parent.glob('.tmdb64-*')))
 def test_unreadable_destination_retains_actual_code_and_does_not_become_generic_write_failure(self):
  with mock.patch.object(self.t,'read',side_effect=self.t.TokenError('TOKEN_UNREADABLE')),self.assertRaises(self.t.TokenError) as result:self.w.read_destination(self.t,str(self.path))
  self.assertEqual(result.exception.code,'TOKEN_UNREADABLE');self.assertEqual(result.exception.stage,'PRIVATE_DESTINATION_READ')
 def test_unwritable_private_directory_is_a_precommit_failure(self):
  for number in (errno.EROFS,errno.EACCES):
   with self.subTest(errno=number),mock.patch.object(self.t,'private_parent',side_effect=OSError(number,'raw private path')),self.assertRaises(self.t.TokenError) as result:self.t.import_bytes(FIXTURE,None)
   self.assertEqual(result.exception.stage,'PRIVATE_DIRECTORY');self.assertFalse(result.exception.committed);self.assertFalse(self.path.exists())
 def test_failed_postwrite_verification_is_explicitly_committed_and_unconfirmed(self):
  with mock.patch.object(self.t,'read',side_effect=[None,None,b'invalid changed bytes']),self.assertRaises(self.t.TokenError) as result:self.t.import_bytes(FIXTURE,None)
  self.assertEqual(result.exception.code,'TOKEN_COMMIT_UNVERIFIED');self.assertTrue(result.exception.committed);self.assertEqual(result.exception.stage,'POSTWRITE_VERIFY')
 def test_symlink_target_and_profile_change_stay_rejected(self):
  outside=self.folder/'outside-secret';outside.write_bytes(b'protected');self.path.symlink_to(outside)
  with self.assertRaises(self.t.TokenError):self.t.import_bytes(FIXTURE,None)
  self.assertEqual(outside.read_bytes(),b'protected');self.path.unlink()
  with self.assertRaises(self.t.TokenError) as result:self.t.import_bytes(FIXTURE,None,target=str(outside))
  self.assertEqual(result.exception.code,'TOKEN_CHANGED');self.assertFalse(self.path.exists())
 def test_private_target_read_error_is_not_hidden_by_ui(self):
  ui=importlib.import_module('tmdb_access61');self.dialog.select.side_effect=[0,-1];self.dialog.browseSingle=mock.Mock(return_value='smb://fixture/share/source.txt')
  with mock.patch('tmdb_import63.selected',return_value=FIXTURE),mock.patch.object(self.w,'read_destination',side_effect=self.t.TokenError('TOKEN_UNREADABLE')):ui.show()
  text=str(self.dialog.ok.call_args_list);self.assertIn('TOKEN_UNREADABLE',text);self.assertNotIn('TOKEN_WRITE',text);self.assertNotIn(FIXTURE.decode(),text)
 def test_diagnostics_never_log_token_fragment_hash_path_or_raw_exception(self):
  logs=[]
  with mock.patch('xbmc.log',side_effect=lambda text,*a:logs.append(text),create=True),mock.patch('xbmc.LOGINFO',1,create=True):
   self.w.note('ATOMIC_RENAME','OK',committed=True);self.w.note('not-a-valid-stage',FIXTURE.decode(),13)
  text=' '.join(logs);self.assertNotIn(FIXTURE.decode(),text);self.assertNotIn(hashlib.sha256(FIXTURE).hexdigest(),text);self.assertNotIn(str(self.path),text)
  self.assertIn('ATOMIC_RENAME',text);self.assertEqual(len(logs),1)
