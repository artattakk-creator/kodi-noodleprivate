"""Theme format/installation/rollback tests. Tiny synthetic images are fixtures,
never evidence that any approved Space Premium originals have been recovered.
"""
import hashlib
import importlib
import io
import json
from pathlib import Path
import shutil
import struct
import sys
import tempfile
import threading
import types
import unittest
from unittest import mock
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT/'src/plugin.video.xtreammate'
LIB = ADDON/'resources/lib'


def png(width=2, height=2):
    def chunk(kind, data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,6,0,0,0))
            +chunk(b'IDAT',zlib.compress((b'\0'+b'\0\x20\x40\xff'*2)*2))+chunk(b'IEND',b''))


class ThemeTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.temp=Path(temp.name)
        self.profile=self.temp/'profile';self.profile.mkdir();self.busy=False
        utils=types.ModuleType('utils');utils.addon_data_dir=lambda:str(self.profile);utils.setting=lambda key,default='':default
        self.player=mock.Mock();self.player.isPlaying.side_effect=lambda:self.busy
        xbmc=types.ModuleType('xbmc');xbmc.Player=lambda:self.player
        addon=types.ModuleType('xbmcaddon');addon.Addon=lambda:types.SimpleNamespace(
            getAddonInfo=lambda k:{'version':'0.1.30','path':str(ADDON)}.get(k,''))
        patch=mock.patch.dict(sys.modules,utils=utils,xbmc=xbmc,xbmcaddon=addon)
        patch.start();self.addCleanup(patch.stop)
        patch=mock.patch.object(sys,'path',[str(LIB)]+sys.path);patch.start();self.addCleanup(patch.stop)
        for name in ('theme_package','theme_store','theme_catalog','theme_ui','profile_transaction'):
            sys.modules.pop(name,None)
        self.package=importlib.import_module('theme_package');self.store=importlib.import_module('theme_store')
        self.catalog=importlib.import_module('theme_catalog')
        self.asset=png()

    def files(self, version='1.0.0', theme_id='test-theme', asset=None, count=1):
        payload=self.asset if asset is None else asset
        images={'assets/shared/image-'+str(i)+'.png':payload for i in range(count)}
        names=list(images)
        assets={'sample.'+str(i):name for i,name in enumerate(names)}
        for key in ('background.home','background.movies','background.series','background.epg',
                    'icon.settings','icon.epg','panel.sidebar','focus.default'): assets[key]=names[0]
        spec=dict(schema_version=1,id=theme_id,name='Space Premium' if theme_id=='space-premium' else 'Test Theme',
            author='GS Media',version=version,supported_xcmate={'min':'0.1.30','max_exclusive':'0.2.0'},
            palette=dict(background='061322',accent='159FEA',focus='42D9FF',text='E6F5FF',secondary='88A6BE'),
            assets=assets,required_files=names,sha256={p:hashlib.sha256(b).hexdigest() for p,b in images.items()})
        return dict(images,**{'theme.json':json.dumps(spec).encode(),
            'SHA256SUMS.txt':''.join(spec['sha256'][p]+'  '+p+'\n' for p in sorted(names)).encode(),
            'README.md':b'TEST FIXTURE, not approved artwork.','LICENSE.txt':b'Test fixture.'})

    def archive(self, files=None, extra=(), name='theme.zip'):
        target=self.temp/name
        with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as archive:
            for path,data in (self.files() if files is None else files).items(): archive.writestr(path,data)
            for path,data in extra: archive.writestr(path,data)
        return target

    def install(self, **kwargs): return self.store.install(self.archive(self.files(**kwargs)))

    def test_install_activate_and_restore_default_without_profile_changes(self):
        private={name:b'keep-'+name.encode() for name in ('portals.json','settings.xml','groups.json','epg.sqlite-wal','resume.json')}
        for name,data in private.items(): (self.profile/name).write_bytes(data)
        revision=self.install();self.assertIsNone(self.store.current())
        self.assertFalse(self.store.select(revision))
        self.assertEqual(Path(self.store.asset('background.home')).read_bytes(),self.asset)
        self.store.select('');self.assertEqual(self.store.asset('missing','core.png'),'core.png')
        for name,data in private.items(): self.assertEqual((self.profile/name).read_bytes(),data)
        self.player.stop.assert_not_called();self.player.play.assert_not_called()

    def test_default_theme_read_is_read_only_and_does_not_create_profile_directories(self):
        for _ in range(5):
            self.assertIsNone(self.store.current())
            self.assertEqual(self.store.asset('background.home','core'),'core')
        self.assertEqual(list(self.profile.iterdir()),[])

    def test_fresh_interpreter_restart_preserves_selection_and_rechecks_assets(self):
        revision=self.install();self.store.select(revision)
        self.store=importlib.reload(self.store)
        self.assertEqual(self.store.current()['revision'],revision)

    def test_corrupted_asset_and_missing_asset_fall_back_after_warm_cache(self):
        revision=self.install();self.store.select(revision);snapshot=self.store.current()
        path=snapshot['folder']/snapshot['spec']['required_files'][0]
        path.write_bytes(b'broken')
        self.assertEqual(self.store.asset('background.home','core.png'),'core.png')
        path.unlink();self.assertIsNone(self.store.current())

    def test_corrupt_manifest_or_selection_falls_back_without_resetting_other_settings(self):
        revision=self.install();self.store.select(revision)
        folder=self.store.current()['folder'];(folder/'theme.json').write_text('{bad')
        self.assertIsNone(self.store.current())
        (self.store.root()/'selection.json').write_text('{"active":"../../accounts"}')
        self.assertIsNone(self.store.current())

    def test_switch_is_deferred_during_playback_without_play_stop_or_global_calls(self):
        first=self.install();self.store.select(first)
        self.busy=True;second=self.install(version='1.1.0')
        self.assertEqual(self.store.current()['revision'],first)
        self.assertTrue(self.store.select(''));self.assertEqual(self.store.current()['revision'],first)
        self.busy=False;self.assertIsNone(self.store.current())
        self.assertTrue((self.store.root()/'packages'/first).is_dir())
        self.assertTrue((self.store.root()/'packages'/second).is_dir())
        self.player.stop.assert_not_called();self.player.play.assert_not_called()

    def test_successful_update_keeps_old_revision_and_advances_active_atomically(self):
        first=self.install();self.store.select(first);second=self.install(version='1.1.0')
        self.assertEqual(self.store.current()['revision'],second)
        self.assertTrue((self.store.root()/'packages'/first).exists())

    def test_bad_update_keeps_active_revision_and_selection_bytes(self):
        first=self.install();self.store.select(first);before=(self.store.root()/'selection.json').read_bytes()
        files=self.files(version='1.1.0');files['assets/shared/image-0.png']=b'wrong'
        with self.assertRaisesRegex(self.package.ThemeError,'CHECKSUM'): self.store.install(self.archive(files))
        self.assertEqual(self.store.current()['revision'],first)
        self.assertEqual((self.store.root()/'selection.json').read_bytes(),before)
        self.assertEqual(list(self.store.root().glob('.install-*')),[])

    def test_disk_full_and_cancellation_do_not_publish_staging_content(self):
        path=self.archive()
        with mock.patch.object(self.store.shutil,'disk_usage',return_value=types.SimpleNamespace(free=0)):
            with self.assertRaisesRegex(self.package.ThemeError,'SPACE'): self.store.install(path)
        with self.assertRaisesRegex(self.package.ThemeError,'CANCELLED'): self.store.install(path,cancel=lambda:True)
        self.assertEqual(self.store.installed(),[]);self.assertEqual(list(self.store.root().glob('.install-*')),[])

    def test_failed_commit_cannot_replace_previous_theme(self):
        first=self.install();self.store.select(first)
        path=self.archive(self.files(version='1.1.0'))
        with mock.patch.object(self.store.os,'replace',side_effect=OSError('disk fault')):
            with self.assertRaises(OSError): self.store.install(path)
        self.assertEqual(self.store.current()['revision'],first)

    def test_idempotence_same_version_conflict_and_downgrade_policy(self):
        first=self.install();self.assertEqual(self.install(),first)
        files=self.files();files['README.md']=b'changed'
        with self.assertRaisesRegex(self.package.ThemeError,'SAME_VERSION'): self.store.install(self.archive(files))
        self.install(version='1.1.0')
        with self.assertRaisesRegex(self.package.ThemeError,'DOWNGRADE'): self.install()

    def test_remove_is_explicit_scoped_and_blocked_while_playing(self):
        revision=self.install();self.store.select(revision);self.busy=True
        with self.assertRaisesRegex(self.package.ThemeError,'BUSY'): self.store.remove('test-theme')
        self.busy=False;self.store.remove('test-theme')
        self.assertIsNone(self.store.current());self.assertEqual(self.store.installed(),[])
        with self.assertRaises(self.package.ThemeError): self.store.remove('../')
        self.player.stop.assert_not_called()

    def test_archive_paths_duplicates_case_aliases_symlinks_and_executables_are_rejected(self):
        for name in ('../escape.png','/tmp/escape.png','assets/../escape.png','assets\\escape.png','C:/escape.png','./theme.json'):
            with self.subTest(name=name),self.assertRaises(self.package.ThemeError):
                self.store.install(self.archive(extra=[(name,b'x')]))
        for name in ('THEME.JSON','theme.json','plugin.py','layout.xml'):
            with self.subTest(name=name),self.assertRaises(self.package.ThemeError):
                with __import__('warnings').catch_warnings():
                    __import__('warnings').simplefilter('ignore',UserWarning)
                    self.store.install(self.archive(extra=[(name,b'x')]))
        link=zipfile.ZipInfo('assets/link.png');link.create_system=3;link.external_attr=0o120777 << 16
        with self.assertRaisesRegex(self.package.ThemeError,'PATH'): self.store.install(self.archive(extra=[(link,b'../../private')]))
        self.assertFalse((self.temp/'escape.png').exists())

    def test_truncated_zip_wrong_zip_hash_and_bad_image_are_rejected(self):
        path=self.archive();path.write_bytes(path.read_bytes()[:-12])
        with self.assertRaisesRegex(self.package.ThemeError,'ARCHIVE'): self.store.install(path)
        with self.assertRaisesRegex(self.package.ThemeError,'CHECKSUM'): self.store.install(self.archive(), '0'*64)
        with self.assertRaisesRegex(self.package.ThemeError,'IMAGE'): self.install(asset=b'not a png')

    def test_zip_expansion_limits_and_file_count_are_checked_before_extracting(self):
        with self.assertRaisesRegex(self.package.ThemeError,'LIMIT'):
            self.store.install(self.archive(extra=[('assets/bomb.png',b'0'*2_000_000)]))
        with self.assertRaisesRegex(self.package.ThemeError,'LIMIT'):
            self.store.install(self.archive(extra=[('extra'+str(i),b'x') for i in range(130)]))
        self.assertEqual(self.store.installed(),[])

    def test_huge_image_dimensions_and_crc_or_deflate_corruption_are_rejected(self):
        with self.assertRaisesRegex(self.package.ThemeError,'LIMIT'): self.install(asset=png(9999,9999))
        corrupted=bytearray(png());corrupted[-1]^=1
        with self.assertRaisesRegex(self.package.ThemeError,'IMAGE'): self.install(asset=bytes(corrupted))
        self.assertEqual(self.package.image(png(),'.png')['width'],2)

    def test_manifest_duplicate_json_keys_versions_and_incompatible_core_are_rejected(self):
        files=self.files();files['theme.json']=b'{"schema_version":1,"schema_version":1}'
        with self.assertRaisesRegex(self.package.ThemeError,'MANIFEST'): self.store.install(self.archive(files))
        files=self.files();spec=json.loads(files['theme.json']);spec['supported_xcmate']['min']='0.2.0';files['theme.json']=json.dumps(spec).encode()
        with self.assertRaisesRegex(self.package.ThemeError,'INCOMPATIBLE'): self.store.install(self.archive(files))
        for value in ('1.0','1.0.0;exec','999999.0.0',None):
            with self.assertRaises(self.package.ThemeError): self.package.version(value)

    def test_space_premium_requires_98_real_files_not_98_alias_keys(self):
        with self.assertRaisesRegex(self.package.ThemeError,'INCOMPLETE'): self.install(theme_id='space-premium',count=97)
        revision=self.install(theme_id='space-premium',count=98)
        self.assertEqual(len(self.store._revision(revision)['spec']['required_files']),98)
        # This is only a format fixture, never an approved production theme.

    def test_symlink_replacement_inside_installed_theme_falls_back(self):
        revision=self.install();self.store.select(revision);folder=self.store.current()['folder']
        shutil.rmtree(folder/'assets/shared');(folder/'assets/shared').symlink_to(self.temp,target_is_directory=True)
        self.assertIsNone(self.store.current())

    def test_catalogue_only_accepts_explicit_approved_compatible_repository_themes(self):
        row=dict(id='test-theme',name='Test Theme',version='1.0.0',approved=True,
            url=self.catalog.ORIGIN+'themes/xcmate/test/theme.zip',sha256='a'*64,bytes=200,
            supported_xcmate={'min':'0.1.30','max_exclusive':'0.2.0'})
        data=dict(schema_version=1,themes=[dict(row,approved=False),row])
        def stream(url,sink,limit,cancel): sink.write(json.dumps(data).encode());return '',0
        with mock.patch.object(self.catalog,'stream',side_effect=stream):
            self.assertEqual(len(self.catalog.catalogue('0.1.30')),1)
            self.assertEqual(self.catalog.catalogue('0.2.0'),[])
            data['themes']=[dict(row,url='https://evil.invalid/payload')]
            with self.assertRaisesRegex(self.package.ThemeError,'CATALOG'): self.catalog.catalogue('0.1.30')

    def test_network_stream_caps_length_encoding_redirects_and_cancellation(self):
        response=mock.MagicMock();response.__enter__.return_value=response;response.status=200
        response.headers={'Content-Length':'3'};response.read1.side_effect=[b'abc',b'']
        with mock.patch.object(self.catalog,'build_opener',return_value=types.SimpleNamespace(open=lambda *a,**kw:response)):
            self.assertEqual(self.catalog.stream(self.catalog.CATALOG,io.BytesIO(),3)[1],3)
            response.headers={'Content-Length':'999'}
            with self.assertRaisesRegex(self.package.ThemeError,'LIMIT'): self.catalog.stream(self.catalog.CATALOG,io.BytesIO(),3)
            response.headers={'Content-Encoding':'gzip'}
            with self.assertRaisesRegex(self.package.ThemeError,'DOWNLOAD'): self.catalog.stream(self.catalog.CATALOG,io.BytesIO(),3)
            response.headers={}
            response.read1.side_effect=[b'abcd']
            with self.assertRaisesRegex(self.package.ThemeError,'LIMIT'): self.catalog.stream(self.catalog.CATALOG,io.BytesIO(),3)
            with mock.patch.object(self.catalog.time,'monotonic',side_effect=[0,121]):
                with self.assertRaisesRegex(self.package.ThemeError,'DOWNLOAD'): self.catalog.stream(self.catalog.CATALOG,io.BytesIO(),3)
            with self.assertRaisesRegex(self.package.ThemeError,'CANCELLED'): self.catalog.stream(self.catalog.CATALOG,io.BytesIO(),3,lambda:True)
        with self.assertRaisesRegex(self.package.ThemeError,'CATALOG'):
            self.catalog.NoRedirect().redirect_request(None,None,302,'',{},'https://evil.invalid')

    def test_catalogue_digest_mismatch_never_installs_or_keeps_download_file(self):
        row=dict(url=self.catalog.CATALOG,bytes=3,sha256='a'*64)
        def stream(url,sink,limit,cancel): sink.write(b'bad');return 'b'*64,3
        with mock.patch.object(self.catalog,'stream',side_effect=stream):
            with self.assertRaisesRegex(self.package.ThemeError,'CHECKSUM'): self.catalog.download(row)
        self.assertEqual(self.store.installed(),[]);self.assertEqual(list(self.store.root().glob('.download-*')),[])

    def test_verified_catalogue_download_installs_matching_identity_only(self):
        raw=self.archive().read_bytes();digest=hashlib.sha256(raw).hexdigest()
        row=dict(id='test-theme',version='1.0.0',url=self.catalog.CATALOG,bytes=len(raw),sha256=digest)
        def stream(url,sink,limit,cancel): sink.write(raw);return digest,len(raw)
        with mock.patch.object(self.catalog,'stream',side_effect=stream):
            revision=self.catalog.download(row)
            self.assertEqual(self.store._revision(revision)['spec']['id'],'test-theme')
            with self.assertRaisesRegex(self.package.ThemeError,'CATALOG'): self.catalog.download(dict(row,id='wrong'))
        self.assertEqual(list(self.store.root().glob('.download-*')),[])

    def test_kodi_vfs_zip_import_closes_source_and_cleans_copy_on_cancel(self):
        raw=self.archive().read_bytes();readers=[]
        class VFS:
            def __init__(self,uri): self.stream=io.BytesIO(raw);self.closed=False;readers.append(self)
            def readBytes(self,size): return self.stream.read(size)
            def close(self): self.closed=True;self.stream.close()
        with mock.patch.dict(sys.modules,xbmcvfs=types.SimpleNamespace(File=VFS)):
            ui=importlib.import_module('theme_ui')
            revision=ui.local_import('smb://test-only/theme.zip')
            self.assertEqual(self.store._revision(revision)['spec']['version'],'1.0.0')
            with self.assertRaisesRegex(self.package.ThemeError,'CANCELLED'):
                ui.local_import('smb://test-only/theme.zip',cancel=lambda:True)
            with mock.patch.object(self.store.shutil,'disk_usage',return_value=types.SimpleNamespace(free=0)):
                with self.assertRaisesRegex(self.package.ThemeError,'SPACE'):
                    ui.local_import('smb://test-only/theme.zip')
        self.assertTrue(all(reader.closed for reader in readers));self.assertEqual(list(self.store.root().glob('.import-*')),[])

    def test_explicit_job_runs_off_gui_thread_and_cancellation_does_not_join_worker(self):
        progress=mock.Mock();progress.iscanceled.return_value=False
        gui=types.ModuleType('xbmcgui');gui.DialogProgress=lambda:progress
        sys.modules['xbmc'].Monitor=lambda:types.SimpleNamespace(waitForAbort=lambda seconds:False)
        with mock.patch.dict(sys.modules,xbmcgui=gui):
            ui=importlib.import_module('theme_ui')
            main=threading.get_ident();self.assertNotEqual(ui.job(lambda cancel:threading.get_ident()),main)
            started=threading.Event();finished=threading.Event();exited=threading.Event();observed=[]
            def operation(cancel):
                started.set()
                try:
                    if finished.wait(2): observed.append(cancel())
                finally: exited.set()
            progress.iscanceled.return_value=True
            with self.assertRaisesRegex(self.package.ThemeError,'CANCELLED'): ui.job(operation)
            finished.set()
            self.assertTrue(exited.wait(2));self.assertEqual(observed,[True])
        progress.close.assert_called()

    def test_native_zip_browser_cancel_and_remove_confirmation_have_no_side_effects(self):
        dialog=mock.Mock();gui=types.ModuleType('xbmcgui');gui.Dialog=lambda:dialog
        with mock.patch.dict(sys.modules,xbmcgui=gui):
            ui=importlib.import_module('theme_ui')
            dialog.select.side_effect=[2,-1];dialog.browseSingle.return_value=''
            ui.manage();self.assertEqual(self.store.installed(),[])
            self.install();dialog.select.side_effect=[4,0,-1];dialog.yesno.return_value=False
            with mock.patch.object(ui,'job',side_effect=lambda fn:fn(lambda:False)): ui.manage()
            self.assertEqual(len(self.store.installed()),1)

    def test_published_core_remains_verified_and_catalogue_does_not_offer_missing_art(self):
        # CI's official builder replaces its disposable index with 0.1.30.
        # Verify the immutable published package against a matching frozen
        # index fixture; the real main index is separately checked by the tool.
        published=self.temp/'published';(published/'plugin.video.xtreammate').mkdir(parents=True)
        for version in ('0.1.28','0.1.29.2'):
            filename='plugin.video.xtreammate-'+version+'.zip'
            shutil.copyfile(ROOT/'plugin.video.xtreammate'/filename,published/'plugin.video.xtreammate'/filename)
        checksum=ROOT/'plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.2.zip.sha256'
        shutil.copyfile(checksum,published/'plugin.video.xtreammate'/checksum.name)
        with zipfile.ZipFile(published/'plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.2.zip') as archive:
            index=b'<addons>'+archive.read('plugin.video.xtreammate/addon.xml').split(b'?>',1)[-1]+b'</addons>'
        (published/'addons.xml').write_bytes(index);(published/'addons.xml.md5').write_text(hashlib.md5(index).hexdigest())
        path=ROOT/'tools/verify_xcmate_installation.py'
        spec=importlib.util.spec_from_file_location('verify_installation',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        report=module.verify(published)
        self.assertEqual(report['version'],'0.1.29.2');self.assertTrue(report['upgrade_same_id'])
        self.assertEqual(json.loads((ROOT/'themes/xcmate/catalog-v1.json').read_text())['themes'],[])

    def test_theme_xml_preserves_geometry_control_ids_remote_links_and_dynamic_provider_art(self):
        import xml.etree.ElementTree as ET
        revision=self.install();self.store.select(revision)
        appearance=importlib.import_module('appearance')
        for filename in ('XCMateMedia.xml','XCMateGuide.xml'):
            original=(ADDON/'resources/skins/Default/720p'/filename).read_bytes()
            source=ET.fromstring(original)
            script=appearance.window_source(filename)
            rendered=ET.parse(Path(script)/'resources/skins/Default/720p'/filename).getroot()
            self.assertEqual(len(list(source.iter('control'))),len(list(rendered.iter('control'))))
            for a,b in zip(source.iter('control'),rendered.iter('control')):
                self.assertEqual(a.attrib,b.attrib)
                for tag in ('left','top','width','height','onleft','onright','onup','ondown','label'):
                    self.assertEqual(a.findtext(tag),b.findtext(tag))
            self.assertEqual([n.text for n in source.iter('texture') if (n.text or '').startswith('$')],
                [n.text for n in rendered.iter('texture') if (n.text or '').startswith('$')])
            self.assertIn(str(self.store.root()),ET.tostring(rendered).decode())
            self.assertEqual((ADDON/'resources/skins/Default/720p'/filename).read_bytes(),original)

    def test_snapshot_asset_rechecks_changed_bytes_and_never_reads_remote_sources(self):
        revision=self.install();self.store.select(revision);snapshot=self.store.current()
        with mock.patch.object(self.store,'current',side_effect=AssertionError('snapshot should avoid global scans')):
            path=self.store.asset('background.home','core',snapshot=snapshot)
            self.assertTrue(Path(path).is_file())
            Path(path).write_bytes(b'wrong')
            self.assertEqual(self.store.asset('background.home','core',snapshot=snapshot),'core')

    def test_build_tool_fully_decodes_98_fixture_images_preserves_bytes_and_reproduces_zip(self):
        files=self.files(theme_id='space-premium',count=98)
        source=self.temp/'source';source.mkdir()
        for name,data in files.items():
            path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        module_spec=importlib.util.spec_from_file_location('build_theme',ROOT/'tools/build_xcmate_theme.py')
        module=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(module)
        first=self.temp/'first.zip';second=self.temp/'second.zip'
        report=module.build(source,first);module.build(source,second)
        self.assertTrue(report['full_decode']);self.assertEqual(report['assets'],98)
        self.assertEqual(first.read_bytes(),second.read_bytes())
        for name,data in files.items(): self.assertEqual((source/name).read_bytes(),data)
        with self.assertRaises(FileExistsError): module.build(source,first)
        # Files exist only in this disposable test directory, not in the catalogue.

    def test_jpeg_runtime_dimensions_and_build_decoder_reject_corruption(self):
        actual=(ADDON/'fanart.jpg').read_bytes()
        self.assertEqual(self.package.image(actual,'.jpg')['format'],'JPEG')
        with self.assertRaisesRegex(self.package.ThemeError,'IMAGE'): self.package.image(actual[:-5],'.jpg')
        files=self.files(theme_id='space-premium',count=98)
        files['assets/shared/image-0.png']=b'bad bytes'
        # Even a matching declared checksum cannot make invalid pixels valid.
        spec=json.loads(files['theme.json']);spec['sha256']['assets/shared/image-0.png']=hashlib.sha256(b'bad bytes').hexdigest()
        files['theme.json']=json.dumps(spec).encode()
        files['SHA256SUMS.txt']=''.join(spec['sha256'][p]+'  '+p+'\n' for p in sorted(spec['required_files'])).encode()
        with self.assertRaisesRegex(self.package.ThemeError,'IMAGE'): self.store.install(self.archive(files))

    def test_central_directory_limit_is_checked_before_zipfile_allocates_entries(self):
        target=self.archive()
        data=bytearray(target.read_bytes())
        end=data.rfind(b'PK\x05\x06')
        data[end+10:end+12]=struct.pack('<H',65535)
        target.write_bytes(data)
        with mock.patch.object(self.store.zipfile,'ZipFile',side_effect=AssertionError('unsafe ZipFile allocation')):
            with self.assertRaisesRegex(self.package.ThemeError,'LIMIT'): self.store.install(target)

    def test_png_internal_inflate_bomb_is_bounded_independently_of_zip_expansion(self):
        raw=png();offset=raw.index(b'IDAT')-4;size=int.from_bytes(raw[offset:offset+4],'big')
        payload=zlib.compress(b'\0'*200000)
        replacement=struct.pack('>I',len(payload))+b'IDAT'+payload+struct.pack('>I',zlib.crc32(b'IDAT'+payload)&0xffffffff)
        corrupt=raw[:offset]+replacement+raw[offset+size+12:]
        with self.assertRaisesRegex(self.package.ThemeError,'IMAGE'): self.install(asset=corrupt)


if __name__=='__main__': unittest.main()
