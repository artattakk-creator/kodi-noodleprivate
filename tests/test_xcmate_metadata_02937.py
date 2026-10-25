"""Verified descriptive copies only; no DB payload reduction/space saving claimed."""
import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
import test_xcmate_artwork_02920 as model


class Metadata37(unittest.TestCase):
    def setUp(self):
        self.m=model.Artwork20Tests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.config=importlib.import_module('artwork_config');self.config.initialize()
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.target=Path(temp.name)
        migration=importlib.import_module('artwork_migration')
        migration.begin(str(self.target));migration.copy();migration.verify();migration.approve_render(True);migration.activate()
        self.export=importlib.import_module('metadata_export')

    def test_descriptive_payload_roundtrip_and_local_catalogue_bytes_unchanged(self):
        self.m.catalogs['get_vod_streams'][0]['plot']='A real description'
        self.m.index.replace_catalog('p','vod',self.m.catalogs['get_vod_streams'],self.m.catalogs['get_vod_categories'])
        index=self.m.folder/'library_v1.sqlite';before=index.read_bytes()
        result=self.export.export()
        self.assertGreater(result['files'],0);self.assertEqual(result['physical_offload'],'BLOCKED')
        row=self.m.index.Reader('p').page('vod',limit=1)[0][0]
        self.assertEqual(self.export.read_item('p','vod',row['sid'])['name'],row['name'])
        self.assertEqual(index.read_bytes(),before)
        self.assertTrue(list((self.target/'XCMate/Metadata').rglob('*.json')))

    def test_urls_credentials_and_stream_fields_never_enter_descriptive_export(self):
        value=self.export.portable(dict(name='Fixture',plot='See https://user:SECRET@private.invalid/SECRET',
            username='SECRET',password='SECRET',stream_url='https://private.invalid/SECRET',
            episodes={'1':[dict(title='Episode',direct_source='https://private.invalid/SECRET',container_extension='mkv')]}))
        raw=json.dumps(value);self.assertNotIn('SECRET',raw);self.assertNotIn('https://',raw);self.assertIn('Episode',raw)

    def test_corrupt_or_offline_copy_does_not_replace_original_index(self):
        self.export.export();row=self.m.index.Reader('p').page('vod',limit=1)[0][0]
        payload=self.target/'XCMate/Metadata'/self.config.read()['profile']/(self.export.key('p','vod',row['sid'])+'.json')
        payload.write_bytes(b'corrupt')
        self.assertEqual(self.export.read_item('p','vod',row['sid']),{})
        self.assertIsNotNone(self.m.index.Reader('p').get('vod',row['sid']))
