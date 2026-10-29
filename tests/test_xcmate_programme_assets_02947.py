"""Real SQLite/PNG/Kodi-path tests over the existing .46 shared database."""
import hashlib
import importlib
import io
import json
from pathlib import Path
import sqlite3
import sys
import threading
import time
import unittest
from unittest import mock
from urllib.parse import urlsplit
from PIL import Image
from xcmate027_fixture import Fixture,ADDON


class ProgrammeAssets47(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.assets=importlib.import_module('programme_assets47')
        self.db=importlib.import_module('programme_index46')
        self.assets._cursor.clear()

    def png(self):
        out=io.BytesIO();Image.new('RGB',(64,48),(30,80,120)).save(out,'PNG');return out.getvalue()

    def row(self,sid='1'):
        return dict(sid=sid,kind='live',name='Station '+sid,stream_icon='https://images.example.test/'+sid+'.png')

    def dns(self,url):
        module=importlib.import_module('artwork_visible');parts=urlsplit(url)
        module._dns_cache[(parts.hostname,443)]=(time.monotonic()+30,True)
        return True

    def test_additive_tables_keep_existing_application_schema_and_committed_events(self):
        db=self.db.connect(True)
        with db:db.execute("INSERT INTO events VALUES('old','p','1','canonical',1,2,'base','{}',1,0)")
        db.close()
        db=self.assets.writer()
        self.assertEqual(db.execute('PRAGMA application_id').fetchone()[0],self.db.APPLICATION_ID)
        self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0],1)
        self.assertEqual(db.execute("SELECT event_key FROM events").fetchall(),[('old',)])
        db.close()

    def test_unknown_future_schema_is_not_modified(self):
        filename=Path(self.db.path());db=sqlite3.connect(filename)
        db.execute('PRAGMA application_id='+str(self.db.APPLICATION_ID));db.execute('PRAGMA user_version=99')
        db.execute('CREATE TABLE future(secret TEXT)');db.execute("INSERT INTO future VALUES('retained')");db.commit();db.close()
        before=filename.read_bytes()
        with self.assertRaises(ValueError):self.assets.writer()
        self.assertEqual(filename.read_bytes(),before)

    def test_wrong_optional_table_schema_rolls_back_without_erasing_existing_data(self):
        db=self.db.connect(True);db.execute('CREATE TABLE asset_refs47(unknown TEXT)');db.commit();db.close()
        with self.assertRaises(ValueError):self.assets.writer()
        db=self.db.connect(False)
        self.assertEqual(db.execute('PRAGMA table_info(asset_refs47)').fetchall()[0][1],'unknown')
        self.assertIsNone(db.execute("SELECT name FROM sqlite_master WHERE name='channels47'").fetchone());db.close()

    def test_read_only_asset_query_never_initializes_or_fetches(self):
        with mock.patch('socket.getaddrinfo',side_effect=AssertionError('DNS from reader')):
            self.assertEqual(self.assets.read_many('p','live',[self.row()]),{})
        self.assertFalse(Path(self.db.path()).exists())

    def test_real_special_and_file_android_paths_preserve_spaces_and_unicode(self):
        path=self.folder/'Android Bilder ä.png';path.write_bytes(self.png())
        with mock.patch.object(sys.modules['xbmcvfs'],'translatePath',return_value=str(path),create=True):
            self.assertEqual(self.assets.local_uri('special://profile/Android Bilder ä.png'),str(path))
        self.assertEqual(self.assets.local_uri(path.as_uri()),str(path))
        self.assertEqual(self.assets.local_uri('file://remote/private.png'),'')
        self.assertEqual(self.assets.local_uri('smb://user:pass@private/logo.png'),'')
        self.assertEqual(self.assets.local_uri(str(path)+'\x00'),'')

    def test_symlink_and_missing_cached_image_are_not_rendered(self):
        path=self.folder/'logo.png';path.write_bytes(self.png());link=self.folder/'linked.png';link.symlink_to(path)
        self.assertEqual(self.assets.local_uri(str(link)),'')
        self.assertEqual(self.assets.local_uri(str(self.folder/'absent.png')),'')

    def test_real_station_tv_png_is_not_confused_with_our_bundled_placeholder(self):
        self.assertTrue(self.assets.station_image('/storage/channel logos/tv.png'))
        self.assertTrue(self.assets.station_image('https://images.example.test/icon.png|redirect-limit=0'))
        self.assertFalse(self.assets.station_image(str(ADDON/'resources/media/tv.png')))
        self.assertFalse(self.assets.station_image(str(ADDON/'icon.png')))

    def test_dynamic_start_group_approves_sender_137_without_image_archive(self):
        rows=[self.row(str(i)) for i in range(137)]
        with mock.patch('artwork_config.persistent',return_value=False),mock.patch('media_art.cached',return_value=''),mock.patch('artwork_visible.public_dns',side_effect=self.dns):
            self.assets.prepare(self.portal,'live',rows)
            assets=self.assets.read_many('p','live',rows)
        self.assertEqual(len(assets),137)
        self.assertTrue(assets['136']['poster'].startswith(rows[-1]['stream_icon']))
        self.assertFalse((self.folder/'programme_images46').exists())
        self.assertEqual(self.options,{})

    def test_dynamic_references_retain_expiry_and_safe_kodi_options(self):
        row=self.row()
        with mock.patch('artwork_config.persistent',return_value=False),mock.patch('media_art.cached',return_value=''),mock.patch('artwork_visible.public_dns',side_effect=self.dns):
            self.assets.prepare(self.portal,'live',[row])
        values=self.assets.read_many('p','live',[row])
        self.assertIn('redirect-limit=0',values['1']['poster'])
        db=self.db.connect(True)
        with db:db.execute('UPDATE asset_refs47 SET expires=?',(time.time()-1,))
        db.close()
        self.assertEqual(self.assets.read_many('p','live',[row]),{})

    def test_portal_and_changed_provider_image_cannot_reuse_foreign_asset(self):
        row=self.row()
        with mock.patch('artwork_config.persistent',return_value=False),mock.patch('media_art.cached',return_value=''),mock.patch('artwork_visible.public_dns',side_effect=self.dns):self.assets.prepare(self.portal,'live',[row])
        self.assertEqual(self.assets.read_many('other','live',[row]),{})
        self.assertEqual(self.assets.read_many('p','live',[dict(row,stream_icon='https://images.example.test/new.png')]),{})

    def test_unsafe_or_failed_dns_never_reaches_native_texture(self):
        row=dict(self.row(),stream_icon='http://127.0.0.1/private.png')
        with mock.patch('artwork_config.persistent',return_value=False),mock.patch('media_art.cached',return_value=''),mock.patch('artwork_visible.public_dns',side_effect=AssertionError('unsafe DNS')):
            self.assets.prepare(self.portal,'live',[row])
        self.assertFalse(self.assets.read_many('p','live',[row]).get('1',{}).get('poster'))

    def test_internal_image_uses_real_validated_local_path(self):
        path=self.folder/'local logo.png';path.write_bytes(self.png());row=self.row()
        with mock.patch('artwork_config.persistent',return_value=True),mock.patch('media_art.cached',return_value=str(path)):
            self.assets.prepare(self.portal,'live',[row])
        self.assertEqual(self.assets.read_many('p','live',[row])['1']['poster'],str(path))
        path.unlink();self.assertFalse(self.assets.read_many('p','live',[row]).get('1'))

    def test_background_asset_approval_does_not_alter_successful_series_pipeline(self):
        # .56 shares optional series references too; existing local covers
        # remain authoritative and neither require DNS nor get replaced.
        path=self.folder/'existing series.png';path.write_bytes(self.png())
        row=dict(self.row(),kind='series')
        with mock.patch('artwork_config.persistent',return_value=True),mock.patch('media_art.cached',return_value=str(path)),mock.patch('artwork_visible.public_dns',side_effect=AssertionError('local series DNS')):
            self.assets.prepare(self.portal,'series',[row])
        self.assertEqual(self.assets.read_many('p','series',[row])['1']['poster'],str(path))
        self.assertEqual(path.read_bytes(),self.png())

    def test_manual_save_keeps_original_and_registers_verified_extension_copy(self):
        choices=importlib.import_module('media_overrides43');data=self.png()
        self.assertTrue(choices.save('p','vod','1',image=data))
        digest=hashlib.sha256(data).hexdigest()
        original=self.folder/'media_choices43/images'/(digest+'.img')
        self.assertEqual(original.read_bytes(),data)
        display=self.assets.choice('p','vod','1','poster',digest)
        self.assertTrue(display.endswith('.png'))
        self.assertEqual(Path(display).read_bytes(),data)
        row=choices.apply_many('p',[dict(sid='1',kind='vod',name='Film')])[0]
        self.assertEqual(choices.cached_art(row)['poster'],display)

    def test_manual_selection_is_shared_after_module_restart_and_cannot_cross_portal(self):
        choices=importlib.import_module('media_overrides43');data=self.png()
        choices.save('p','series','2',image=data,role='fanart')
        digest=hashlib.sha256(data).hexdigest();self.assets=importlib.reload(self.assets)
        self.assertTrue(self.assets.choice('p','series','2','fanart',digest))
        self.assertFalse(self.assets.choice('other','series','2','fanart',digest))
        self.assertFalse(self.assets.choice('p','series','2','fanart','0'*64))

    def test_optional_shared_copy_failure_does_not_destroy_explicit_original_choice(self):
        choices=importlib.import_module('media_overrides43');data=self.png()
        with mock.patch.object(self.assets,'remember_choice',side_effect=OSError('budget')):
            self.assertTrue(choices.save('p','vod','1',image=data))
        row=choices.apply_many('p',[dict(sid='1',kind='vod',name='Film')])[0]
        self.assertEqual(Path(choices.cached_art(row)['poster']).read_bytes(),data)

    def test_corrupt_display_copy_falls_back_to_verified_original_without_deletion(self):
        choices=importlib.import_module('media_overrides43');data=self.png()
        choices.save('p','vod','1',image=data)
        digest=hashlib.sha256(data).hexdigest();copy=Path(self.assets.choice('p','vod','1','poster',digest));copy.write_bytes(b'broken')
        choices._cache.clear();choices._versions.clear()
        row=choices.apply_many('p',[dict(sid='1',kind='vod',name='Film')])[0]
        original=Path(choices.cached_art(row)['poster'])
        self.assertEqual(original.suffix,'.img');self.assertEqual(original.read_bytes(),data)
        self.assertTrue(copy.exists())

    def test_asset_transaction_rolls_back_new_reference_and_preserves_previous(self):
        db=self.assets.writer()
        with db:db.execute("INSERT INTO channels47 VALUES('p','old','canonical','{}',0)")
        db.execute('BEGIN IMMEDIATE');db.execute("INSERT INTO channels47 VALUES('p','new','new','{}',0)");db.rollback();db.close()
        db=self.db.connect(False)
        self.assertEqual(db.execute('SELECT sid FROM channels47').fetchall(),[('old',)]);db.close()

    def test_concurrent_connections_read_committed_old_snapshot_during_writer(self):
        db=self.assets.writer()
        with db:db.execute("INSERT INTO channels47 VALUES('p','1','old','{}',0)")
        db.execute('BEGIN IMMEDIATE');db.execute("UPDATE channels47 SET canonical='new'")
        result=[]
        def read():
            other=self.db.connect(False)
            try:result.append(other.execute('SELECT canonical FROM channels47').fetchone()[0])
            finally:other.close()
        thread=threading.Thread(target=read);thread.start();thread.join(2)
        self.assertFalse(thread.is_alive());self.assertEqual(result,['old']);db.rollback();db.close()

    def test_additive_asset_preparation_never_modifies_existing_guide_payload(self):
        guide=importlib.import_module('guide_store')
        guide.import_cache('p',{'xml':[dict(channel='xml',name='Retained',start_timestamp=self.now-60,stop_timestamp=self.now+600)]})
        filename=Path(guide.path());before=filename.read_bytes()
        self.assets.channels(self.portal,[dict(sid='1',canonical='xml',channel='Station',key='key',start=1,stop=2)])
        self.assertEqual(filename.read_bytes(),before)
