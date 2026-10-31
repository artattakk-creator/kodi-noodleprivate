"""Explicit picker VFS imports. All credentials are synthetic syntax fixtures."""
import importlib,threading,time,unittest
from unittest import mock
from xcmate027_fixture import Fixture
from test_xcmate_tmdb_token_02961 import FIXTURE

class TokenVfs63(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.reader=importlib.import_module('tmdb_import63');self.tokens=importlib.import_module('tmdb_token61')
 def handle(self,raw=FIXTURE):
  h=mock.Mock();h.size.return_value=len(raw);h.readBytes.side_effect=[raw,b''];return h
 def test_selected_smb_and_android_usb_use_bounded_vfs_and_preserve_source(self):
  for path in ('smb://fixture/private/token.txt','/storage/fixture-usb/token.txt','/sdcard/Download/other-name.txt','/mnt/media_rw/fixture/token.txt'):
   h=self.handle()
   with mock.patch('xbmcvfs.File',return_value=h,create=True) as opened:
    self.assertEqual(self.reader.selected(path),FIXTURE);opened.assert_called_once_with(path,'rb')
   self.assertEqual(h.readBytes.call_args_list,[mock.call(self.tokens.MAX_BYTES+1),mock.call(1)]);h.close.assert_called_once()
 def test_arbitrary_http_plugin_traversal_controls_and_remote_file_urls_are_forbidden(self):
  for path in ('https://fixture/a.txt','http://127.0.0.1/x','ftp://fixture/x','plugin://x','content://x','file://remote/x','smb://fixture/a/../b','smb://fixture/a%2f..%2fb','smb://fixture/x?query','smb://fixture/x#fragment','smb://fixture/%00x','relative.txt','special://unknown/x'):
   with self.subTest(path=path),self.assertRaises(self.tokens.TokenError) as exc:self.reader.selected(path)
   self.assertEqual(exc.exception.code,'TOKEN_PATH')
 def test_special_and_file_uris_resolve_only_to_supported_local_sources(self):
  source=self.folder/'other name.txt';source.write_bytes(FIXTURE)
  self.assertEqual(self.reader.selected(source.as_uri()),FIXTURE)
  with mock.patch('xbmcvfs.translatePath',return_value=str(source)):
   self.assertEqual(self.reader.selected('special://profile/other.txt'),FIXTURE)
  alias=self.folder/'alias.txt';alias.symlink_to(source)
  with self.assertRaises(self.tokens.TokenError):self.reader.selected(str(alias))
 def test_vfs_size_short_reads_growth_and_unreadable_are_distinct(self):
  h=self.handle();h.size.return_value=5000
  with mock.patch('xbmcvfs.File',return_value=h,create=True),self.assertRaises(self.tokens.TokenError) as exc:self.reader.selected('smb://fixture/a')
  self.assertEqual(exc.exception.code,'TOKEN_SIZE');h.readBytes.assert_not_called();h.close.assert_called_once()
  for raw,eof in ((b'A'*4098,b''),(FIXTURE,b'x')):
   h=self.handle();h.size.return_value=0;h.readBytes.side_effect=[raw,eof]
   with mock.patch('xbmcvfs.File',return_value=h,create=True),self.assertRaises(self.tokens.TokenError) as exc:self.reader.selected('smb://fixture/a')
   self.assertEqual(exc.exception.code,'TOKEN_SIZE')
  with mock.patch('xbmcvfs.File',side_effect=OSError('private fake source'),create=True),self.assertRaises(self.tokens.TokenError) as exc:self.reader.selected('smb://fixture/a')
  self.assertEqual(str(exc.exception),'TOKEN_UNREADABLE')
 def test_formats_are_validated_after_source_classification_without_content_in_errors(self):
  for raw in (FIXTURE,FIXTURE+b'\n',FIXTURE+b'\r\n'):
   with mock.patch('xbmcvfs.File',return_value=self.handle(raw),create=True):
    self.assertEqual(self.tokens.validate(self.reader.selected('smb://fixture/a')),FIXTURE.decode())
  for raw in (FIXTURE+b'\nsecond',b'\xef\xbb\xbf'+FIXTURE,b'Bearer '+FIXTURE,b'"'+FIXTURE+b'"',b' '+FIXTURE,FIXTURE+b' '):
   with mock.patch('xbmcvfs.File',return_value=self.handle(raw),create=True),self.assertRaises(self.tokens.TokenError) as exc:self.tokens.validate(self.reader.selected('smb://fixture/a'))
   self.assertEqual(str(exc.exception),'TOKEN_FORMAT')
 def test_stalled_vfs_has_one_outstanding_job_and_returns_without_publishing(self):
  gate=threading.Event();started=threading.Event()
  def read(path):started.set();gate.wait(2);return FIXTURE
  try:
   with mock.patch.object(self.reader,'_vfs',side_effect=read):
    before=time.monotonic()
    with self.assertRaises(self.tokens.TokenError):self.reader.selected('smb://fixture/a',budget=.05)
    self.assertLess(time.monotonic()-before,.5);self.assertTrue(started.is_set())
    with self.assertRaises(self.tokens.TokenError):self.reader.selected('smb://fixture/a',budget=.05)
  finally:
   gate.set()
   for _ in range(100):
    if not self.reader._busy.locked():break
    time.sleep(.01)

 def test_short_vfs_packets_unknown_stat_and_cancel_are_bounded_without_writes(self):
  h=self.handle();h.size.side_effect=RuntimeError('fixture stat unavailable');h.readBytes.side_effect=[FIXTURE[:9],FIXTURE[9:31],FIXTURE[31:],b'']
  with mock.patch('xbmcvfs.File',return_value=h,create=True):self.assertEqual(self.reader.selected('smb://fixture/a'),FIXTURE)
  self.assertEqual(h.readBytes.call_count,4);h.close.assert_called_once()
  with mock.patch('xbmcvfs.File',create=True) as opened,self.assertRaises(self.tokens.TokenError):self.reader.selected('smb://fixture/a',cancel=lambda:True)
  opened.assert_not_called()
