"""Security and build tests for review-only 0.5.28 cloud token importer."""
import base64
import importlib.util
import io
import json
import sys
import tempfile
import types
import unittest
import zipfile
from pathlib import Path
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'tools/gsmedia_setup0528/overlays/resources/lib/setup_tmdb_cloud528.py'
BUILD=ROOT/'tools/build_gsmedia_setup_0528.py'

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,str(path))
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

class CloudToken528(unittest.TestCase):
    def setUp(self):
        self.mod=module('cloud_528',SOURCE)

    def test_fixed_origins_and_no_traversal(self):
        cases=[
          ('drive','1EMzM8pU7JDpk1OkoRFNSCTiuS3MMZ-9w','www.googleapis.com'),
          ('github','artattakk-creator/kodi-noodleprivate/private/tmdb.txt','api.github.com'),
        ]
        for provider,name,host in cases:
            self.assertEqual(self.mod._locator(provider,name)[0],host)
        bad=[
          ('github','https://evil.local/secret.txt'),
          ('github','owner/repo/../token.txt'),
          ('github','owner/repo/test.py'),
          ('github','owner/repo/foo%2Fbar.txt'),
          ('drive','https://drive.google.com/file/d/foobar'),
          ('drive','..'),
          ('drive','something?alt=media'),
          ('http','owner/repo/token.txt'),
        ]
        for provider,name in bad:
            with self.assertRaises(self.mod.ImportError528):
                self.mod._locator(provider,name)

    def test_provider_downloads_are_bounded_and_use_no_secret_urls(self):
        sample=b'fake.private.tmdbtoken\n'
        github=json.dumps(dict(size=len(sample),encoding='base64',content=base64.b64encode(sample).decode())).encode()
        calls=[]
        def network(host,path,bearer,limit,cancel):
            calls.append((host,path,limit))
            self.assertNotIn(bearer,path)
            return github if host=='api.github.com' else sample
        with mock.patch.object(self.mod,'_https',side_effect=network):
            self.assertEqual(self.mod.download('github','owner/repo/token.txt','secret12345678'),sample)
            self.assertEqual(self.mod.download('drive','1EMzM8pU7JDpk1OkoRFNSCTiuS3MMZ-9w','secret12345678'),sample)
        self.assertEqual(calls[0][0],'api.github.com')
        self.assertEqual(calls[1][0],'www.googleapis.com')
        with mock.patch.object(self.mod,'_https',return_value=b'not-json'):
            with self.assertRaises(self.mod.ImportError528):
                self.mod.download('github','owner/repo/token.txt','secret12345678')

    def test_no_overwrite_or_commit_before_authentication(self):
        saved=[];activated=[]
        good='abc.def.'+'x'*56
        class TokenError(ValueError):pass
        tokenlib=types.SimpleNamespace(
            TokenError=TokenError,
            validate=lambda raw: good if raw==good.encode() else (_ for _ in ()).throw(TokenError()),
            import_bytes=lambda raw,expected,target=None:saved.append((raw,expected,target)) or 'IMPORTED',
            location=lambda:'/fake/private/tmdb_read_access_token.txt',
            read=lambda path,missing=False:None)
        addon=types.SimpleNamespace(getSetting=lambda key:'false' if key=='programme_tmdb_optout77' else '')
        modules={
          'xbmcaddon':types.SimpleNamespace(Addon=lambda *args:addon),
          'tmdb_token61':tokenlib,
          'media_sources43':types.SimpleNamespace(TMDB='https://api.themoviedb.org/3',SourceError=type('SourceError',(Exception,),{})),
          'tmdb_connection60':types.SimpleNamespace(request=lambda *a,**k:dict(images={'secure_base_url':'https://image.tmdb.org/t/p/','backdrop_sizes':['w780']}))
        }
        with mock.patch.dict(sys.modules,modules):
            with mock.patch.object(self.mod,'download',return_value=good.encode()):
                self.assertEqual(self.mod.perform('drive','1EMzM8pU7JDpk1OkoRFNSCTiuS3MMZ-9w','bearer123456789'),'PAIRED')
                self.assertEqual(len(saved),1)
                self.assertIsNone(saved[0][1])
                self.assertEqual(saved[0][2],tokenlib.location())
            with mock.patch.object(self.mod,'download',return_value=b'incorrect'):
                self.assertEqual(self.mod.perform('github','a/b/token.txt','bearer123456789'),'TOKEN_INVALID')
                self.assertEqual(len(saved),1)
            addon.getSetting=lambda key:'true' if key=='programme_tmdb_optout77' else ''
            with mock.patch.object(self.mod,'download',side_effect=AssertionError('MUST NOT DOWNLOAD')):
                self.assertEqual(self.mod.perform('github','a/b/token.txt','bearer123456789'),'SKIPPED')
        self.assertEqual(activated,[])

    def test_builder_reproducible_preserves_original_components(self):
        builder=module('builder_528',BUILD)
        with tempfile.TemporaryDirectory() as temp:
            a=builder.build(temp)
            one=(Path(temp)/builder.TARGET).read_bytes()
            b=builder.build(temp)
            two=(Path(temp)/builder.TARGET).read_bytes()
            self.assertEqual(one,two)
            self.assertEqual(a['sha256'],b['sha256'])
            self.assertEqual(a['android'],'ANDROID_NOT_TESTED')
            self.assertFalse(a['google_drive_oauth_login_integrated'])
            with zipfile.ZipFile(ROOT/'script.gsmedia.setup'/builder.SOURCE) as original, zipfile.ZipFile(io.BytesIO(one)) as new:
                self.assertIsNone(new.testzip())
                self.assertEqual(len(new.namelist()),len(original.namelist())+1)
                for path in original.namelist():
                    if path not in a['changed']:
                        self.assertEqual(original.read(path),new.read(path),path)
                self.assertIn(b'Importiere TMDB-Token',new.read(builder.PREFIX+builder.NEW))
                self.assertIn(b'TMDB_IMPORT528',new.read(builder.PREFIX+'resources/lib/setup_auto_ui50.py'))

if __name__=='__main__':unittest.main()
