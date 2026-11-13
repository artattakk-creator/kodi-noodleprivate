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
          ('drive','SYNTHETIC_DRIVE_FILE_ID_0123456789ABC','www.googleapis.com'),
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
            self.assertEqual(self.mod.download('drive','SYNTHETIC_DRIVE_FILE_ID_0123456789ABC','secret12345678'),sample)
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
                self.assertEqual(self.mod.perform('drive','SYNTHETIC_DRIVE_FILE_ID_0123456789ABC','bearer123456789'),'PAIRED')
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
                self.assertEqual(len(new.namelist()),len(original.namelist())+3)
                for path in original.namelist():
                    if path not in a['changed']:
                        self.assertEqual(original.read(path),new.read(path),path)
                self.assertIn(b'Importiere TMDB-Token',new.read(builder.PREFIX+builder.NEW))
                self.assertIn(b'TMDB_IMPORT528',new.read(builder.PREFIX+'resources/lib/setup_auto_ui50.py'))
                self.assertIn(b'EPG_ART_MODE528',new.read(builder.PREFIX+'resources/lib/setup_auto_ui50.py'))
                self.assertIn(b'epg_art_mode528',new.read(builder.PREFIX+builder.SETTINGS))
                self.assertIn(b'Joomla-API',new.read(builder.PREFIX+builder.NEW))
            self.assertEqual(a['epg_media_min_free_mb']['standard'],0)
            self.assertEqual(a['epg_media_min_free_mb']['extended'],0)
            self.assertTrue(a['epg_media_no_min_free_space_gate'])
            self.assertTrue(a['epg_media_dynamic_on_demand'])
            self.assertTrue(a['epg_media_storage_migration_optional'])
            self.assertFalse(a['epg_media_quotas_enforced_by_runtime'])



class ImageEPG528(unittest.TestCase):
    def setUp(self):
        self.mod=module('media528',ROOT/'tools/gsmedia_setup0528/overlays/resources/lib/setup_epg_art528.py')

    def test_image_epg_works_with_218_mb_free_or_unknown_volume(self):
        x=self.mod
        low=dict(code='READY',free_bytes=218*x.MIB,total_bytes=4*1024*x.MIB)
        for mode in ('text','standard','extended'):
            self.assertTrue(x.can_enable(mode,low))
            self.assertTrue(x.can_enable(mode,{'code':'STORAGE_UNKNOWN'}))
        self.assertFalse(x.can_enable('invalid',low))
        self.assertNotIn('media_art_budget_mb',str(x.MODES))
        self.assertNotIn('min_free',str(x.MODES))
        self.assertEqual(len(x.MODES),3)

    def test_measure_reports_capacity_advisory_only(self):
        with tempfile.TemporaryDirectory() as root:
            status=self.mod.measure(root)
            self.assertEqual(status['code'],'READY')
            self.assertGreaterEqual(status['total_bytes'],status['free_bytes'])
            self.assertIsInstance(status['device'],int)
        self.assertEqual(self.mod.measure('/definitely-missing-dir-epg-528')['code'],'STORAGE_UNKNOWN')

    def test_modes_do_not_force_disk_cache_even_at_low_space(self):
        m=self.mod
        class Addon:
            def __init__(self,vals,fail=False):
                self.values=dict(vals);self.fail=fail
            def getSetting(self,key):return self.values.get(key,'')
            def setSetting(self,key,value):
                if self.fail and key=='epg_show_thumbnails' and value=='true':
                    raise RuntimeError('simulated failure')
                self.values[key]=value
        report={'code':'READY','free_bytes':218*m.MIB,'total_bytes':4*1024*m.MIB}
        existing={'epg_show_thumbnails':'false','programme_art_local69':'false'}
        state={'epg_art_mode528':'text','epg_art_target_mb528':'0'}
        addon=Addon(existing);installer=Addon(state)
        self.assertEqual(m.configure('standard',report,addon,installer),'CONFIGURED')
        self.assertEqual(addon.getSetting('epg_show_thumbnails'),'true')
        self.assertEqual(addon.getSetting('programme_art_local69'),'false')
        self.assertEqual(installer.getSetting('epg_art_target_mb528'),'0')
        self.assertEqual(installer.getSetting('epg_art_mode528'),'standard')
        self.assertEqual(m.configure('extended',{'code':'STORAGE_UNKNOWN'},addon,installer),'CONFIGURED')
        self.assertEqual(installer.getSetting('epg_art_mode528'),'extended')
        self.assertEqual(installer.getSetting('epg_art_target_mb528'),'0')
        self.assertEqual(addon.getSetting('programme_art_local69'),'false')
        self.assertEqual(m.configure('text',report,addon,installer),'CONFIGURED')
        self.assertEqual(addon.getSetting('epg_show_thumbnails'),'false')

    def test_existing_local_cache_preference_preserved_and_rollback(self):
        m=self.mod
        class Addon:
            def __init__(self,vals,fail=False):
                self.values=dict(vals);self.fail=fail
            def getSetting(self,key):return self.values.get(key,'')
            def setSetting(self,key,value):
                if self.fail and key=='epg_show_thumbnails' and value=='true':
                    raise RuntimeError('simulated failure')
                self.values[key]=value
        addon=Addon({'epg_show_thumbnails':'false','programme_art_local69':'true'})
        installer=Addon({'epg_art_mode528':'text','epg_art_target_mb528':'0'})
        self.assertEqual(m.configure('standard',{'code':'STORAGE_UNKNOWN'},addon,installer),'CONFIGURED')
        self.assertEqual(addon.getSetting('programme_art_local69'),'true')
        broken=Addon({'epg_show_thumbnails':'false','programme_art_local69':'false'},fail=True)
        state=Addon({'epg_art_mode528':'text','epg_art_target_mb528':'0'})
        self.assertEqual(m.configure('extended',{'code':'STORAGE_UNKNOWN'},broken,state),'CONFIG_WRITE_FAILED')
        self.assertEqual(broken.values,{'epg_show_thumbnails':'false','programme_art_local69':'false'})
        self.assertEqual(state.values,{'epg_art_mode528':'text','epg_art_target_mb528':'0'})

if __name__=='__main__':unittest.main()
