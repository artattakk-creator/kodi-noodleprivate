"""Private token file integrity, priority, GUI privacy and worker boundaries."""
import hashlib,importlib,os,sys,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture

# Generated syntax-only fixture. Never an actual TMDB credential.
FIXTURE=b'e30.'+b'c2FmZV9maXh0dXJlX25vdF9hX2NyZWRlbnRpYWw.'+b'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
class Token61(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.t=importlib.import_module('tmdb_token61');self.path=Path(self.t.location());self.source=self.folder/'import.txt';self.source.write_bytes(FIXTURE)
 def test_file_precedence_and_absent_file_legacy_compatibility(self):
  self.options['tmdb_read_token43']='legacy-syntax-fixture'
  self.assertEqual(self.t.effective_tmdb_read_token(True),'legacy-syntax-fixture')
  self.path.write_bytes(FIXTURE+b'\n');self.assertEqual(self.t.effective_tmdb_read_token(True),FIXTURE.decode())
 def test_bad_existing_file_never_uses_legacy_or_network(self):
  self.options['tmdb_read_token43']='legacy-syntax-fixture';self.path.write_bytes(b'invalid')
  with self.assertRaises(self.t.TokenError):self.t.effective_tmdb_read_token(True)
  self.assertEqual(self.t.status(),'FILE_INVALID')
  with mock.patch('media_sources43.get',side_effect=AssertionError('network')):
   self.assertEqual(importlib.import_module('tmdb_connection60').test_connection(),'TOKEN_FILE_INVALID')
 def test_utf8_single_line_bounds_bearer_json_quotes_comments_and_placeholders(self):
  invalid=[b'',b'\xff',b'Bearer '+FIXTURE,b'"'+FIXTURE+b'"',b'{"token":"'+FIXTURE+b'"}',FIXTURE+b'\n\n',FIXTURE+b'\n#comment',b' '+FIXTURE,FIXTURE+b' ',b'A'*5000,b'placeholder.'+b'A'*40+b'.'+b'A'*40]
  for raw in invalid:
   with self.subTest(size=len(raw)),self.assertRaises(self.t.TokenError):self.t.validate(raw)
  for raw in (FIXTURE,FIXTURE+b'\n',FIXTURE+b'\r\n'):self.assertEqual(self.t.validate(raw),FIXTURE.decode())
 def test_symlink_sources_parent_targets_and_nonregular_files_are_rejected(self):
  link=self.folder/'link.txt';link.symlink_to(self.source)
  with self.assertRaises(self.t.TokenError):self.t.read(str(link))
  sub=self.folder/'real';sub.mkdir();(sub/'a.txt').write_bytes(FIXTURE);alias=self.folder/'alias';alias.symlink_to(sub,target_is_directory=True)
  with self.assertRaises(self.t.TokenError):self.t.read(str(alias/'a.txt'))
  with self.assertRaises(self.t.TokenError):self.t.read(str(sub))
  fifo=self.folder/'fifo';os.mkfifo(fifo)
  with self.assertRaises(self.t.TokenError):self.t.read(str(fifo))
  self.path.symlink_to(self.source)
  with self.assertRaises(self.t.TokenError):self.t.import_file(str(self.source),None)
  self.assertTrue(self.path.is_symlink())
 def test_unsafe_relative_network_vfs_and_traversal_paths_are_rejected(self):
  for path in ('relative.txt','smb://server/token.txt','https://host/token.txt','special://x','/tmp/../token','/tmp/\x00token'):
   with self.subTest(kind=path.split(':')[0]),self.assertRaises(self.t.TokenError):self.t.read(path)
 def test_atomic_private_import_preserves_source_options_and_other_files(self):
  self.options.update(tmdb_research43=False,programme_tmdb46=False)
  before=dict(self.options);protected=self.folder/'portals.json';protected.write_bytes(b'keep')
  self.assertEqual(self.t.import_file(str(self.source),None),'IMPORTED')
  self.assertEqual(self.path.read_bytes(),FIXTURE+b'\n');self.assertEqual(self.path.stat().st_mode&0o777,0o600)
  self.assertEqual(self.source.read_bytes(),FIXTURE);self.assertEqual(protected.read_bytes(),b'keep');self.assertEqual(self.options,before)
  self.assertFalse(list(self.folder.glob('.tmdb61-*')))
 def test_existing_file_requires_exact_reviewed_digest_and_changed_file_is_protected(self):
  self.path.write_bytes(b'old')
  with self.assertRaises(self.t.TokenError):self.t.import_file(str(self.source),None)
  self.assertEqual(self.path.read_bytes(),b'old')
  digest=hashlib.sha256(b'old').hexdigest();self.t.import_file(str(self.source),digest);self.assertEqual(self.path.read_bytes(),FIXTURE+b'\n')
 def test_atomic_replace_failure_retains_old_token_and_cleans_temp(self):
  self.path.write_bytes(b'old');digest=hashlib.sha256(b'old').hexdigest()
  with mock.patch.object(self.t.os,'replace',side_effect=OSError('private text')):
   with self.assertRaises(self.t.TokenError) as exc:self.t.import_file(str(self.source),digest)
  self.assertEqual(str(exc.exception),'TOKEN_WRITE');self.assertEqual(self.path.read_bytes(),b'old');self.assertFalse(list(self.folder.glob('.tmdb61-*')))
 def test_status_and_diagnostics_do_not_display_token(self):
  self.path.write_bytes(FIXTURE);self.assertEqual(self.t.status(),'FILE_VALID')
  self.options.update(tmdb_research43=True,programme_tmdb46=True)
  code=importlib.import_module('programme_match46').diagnose(dict(genre='film',year=2026));self.assertNotIn(FIXTURE.decode(),code)
 def test_fingerprint_uses_ram_and_changes_after_worker_or_import_refresh(self):
  before=self.t.token_fingerprint();self.path.write_bytes(FIXTURE);self.t.effective_tmdb_read_token(True)
  with mock.patch.object(self.t,'read',side_effect=AssertionError('focus disk IO')):
   self.assertNotEqual(before,self.t.token_fingerprint())
   art=importlib.import_module('programme_art46');self.options['programme_tmdb46']=True
   for _ in range(100):art.fingerprint(dict(title='Movie',year=2026))
 def test_real_connection_and_artwork_token_clients_use_private_file(self):
  self.path.write_bytes(FIXTURE);self.options['tmdb_research43']=True
  sources=importlib.import_module('media_sources43');self.assertEqual(sources.tmdb_token(),FIXTURE.decode())
  client=importlib.import_module('tmdb_connection60')
  with mock.patch.object(client,'request',return_value={'images':{'secure_base_url':'https://image.tmdb.org/t/p/','backdrop_sizes':['w780']}}) as request:
   self.assertEqual(client.test_connection(),'TMDB_OK');self.assertEqual(request.call_args.kwargs['token'],FIXTURE.decode())
 def test_import_ui_cancel_and_overwrite_decline_preserve_bytes(self):
  ui=importlib.import_module('tmdb_access61');self.path.write_bytes(FIXTURE+b'\n');before=self.path.read_bytes()
  self.dialog.browseSingle=mock.Mock(return_value=str(self.source));self.dialog.select.side_effect=[0,-1];self.dialog.yesno.return_value=False
  ui.show();self.assertEqual(self.path.read_bytes(),before);self.assertFalse(self.options)
 def test_exact_epg_submenu_and_import_does_not_enable_artwork(self):
  sections=importlib.import_module('settings_sections45');self.assertIn((36620,'native_options45',{'group':'tmdb_access61'}),sections.ROWS['epg'])
  ui=importlib.import_module('tmdb_access61');self.dialog.browseSingle=mock.Mock(return_value=str(self.source));self.dialog.select.side_effect=[0,-1]
  ui.show();self.assertEqual(self.path.read_bytes(),FIXTURE+b'\n');self.assertFalse(self.options)
  self.assertNotIn(FIXTURE.decode(),str(self.dialog.ok.call_args_list))
 def test_restart_reloads_valid_file_and_invalid_replacement_blocks_fallback(self):
  self.t.import_file(str(self.source),None);self.t._cache=None;self.assertEqual(self.t.effective_tmdb_read_token(),FIXTURE.decode())
  self.path.write_bytes(b'broken');self.options['tmdb_read_token43']='legacy'
  with self.assertRaises(self.t.TokenError):self.t.effective_tmdb_read_token(True)
