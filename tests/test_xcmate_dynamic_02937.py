"""Dynamic provider-URL admission/render values, never actual Kodi texture PASS."""
import importlib
import json
from pathlib import Path
import socket
import sys
import threading
import unittest
from unittest import mock
import test_xcmate_artwork_02920 as model
from xcmate027_fixture import ADDON


class Dynamic37(unittest.TestCase):
    def setUp(self):
        self.m=model.Artwork20Tests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.config=importlib.import_module('artwork_config');self.config.initialize();self.config.choose('dynamic')
        self.visible=importlib.import_module('artwork_visible')
        with self.visible._lock:self.visible._values.clear();self.visible._dns_cache.clear()
        self.addCleanup(self.drain)

    def drain(self):
        for work in self.visible._queues.values():work.join()
        for worker in tuple(self.visible._threads.values()):worker.join(3)

    def test_visible_dynamic_posters_and_logos_use_urls_without_archive_or_queue(self):
        rows=[dict(cover='https://artwork.example.com/'+str(i),kind='vod' if i<3 else 'series') for i in range(5)]
        before=set(self.m.folder.iterdir())
        with mock.patch.object(self.visible.socket,'getaddrinfo',return_value=[(socket.AF_INET,socket.SOCK_STREAM,6,'',('8.8.8.8',443))]):
            for row in rows:self.m.art.local_art(row)
            logos=importlib.import_module('logo_cache')
            for i in range(2):logos.local_logo('https://artwork.example.com/logo'+str(i))
            self.drain()
            for row in rows:self.assertEqual(self.m.art.local_art(row)['poster'],row['cover']+self.visible.KODI_OPTIONS)
            for i in range(2):self.assertEqual(logos.local_logo('https://artwork.example.com/logo'+str(i)),'https://artwork.example.com/logo'+str(i)+self.visible.KODI_OPTIONS)
        self.m.request(rows);self.assertFalse(self.m.store.run_one());self.m.store.prefetch_selected()
        self.assertEqual(set(self.m.folder.iterdir()),before);self.m.http.assert_not_called()

    def test_dynamic_does_not_check_archive_reserve_or_reset_old_ready_and_failed_jobs(self):
        self.config.choose('internal');self.m.art.fetch('https://image.invalid/old37')
        self.m.seed(['https://image.invalid/blocked37'],'DISK_FULL',attempts=3)
        db=self.m.store.connect();before=[tuple(r) for r in db.execute('SELECT * FROM jobs ORDER BY ident')];db.close()
        self.config.choose('dynamic')
        with mock.patch.object(self.m.policy,'check',side_effect=AssertionError('dynamic archive reserve')):
            self.m.request([dict(cover='https://artwork.example.com/dynamic37')]);self.assertFalse(self.m.store.run_one())
            self.m.store.prefetch_selected();self.assertFalse(self.m.art.ensure_worker())
            self.assertEqual(self.m.art.retry_poster(dict(cover='https://artwork.example.com/dynamic37')),'NOT_REQUESTED')
        db=self.m.store.connect();self.assertEqual([tuple(r) for r in db.execute('SELECT * FROM jobs ORDER BY ident')],before);db.close()
        self.assertTrue((self.m.folder/'media_art_v1').is_dir())

    def test_dynamic_rejects_non_http_credentials_private_hosts_and_mixed_dns(self):
        bad=['file:///etc/passwd','smb://host/share','http://127.0.0.1/image','http://169.254.169.254/image','http://[::1]/image',
             'https://user:SECRET@example.com/image','https://localhost/image','https://artwork.example.com/a|Authorization=SECRET']
        for url in bad:self.assertEqual(self.visible.dynamic(url),'')
        rows=[(socket.AF_INET,socket.SOCK_STREAM,6,'',('8.8.8.8',443)),(socket.AF_INET,socket.SOCK_STREAM,6,'',('10.1.2.3',443))]
        with mock.patch.object(self.visible.socket,'getaddrinfo',return_value=rows):
            url='https://artwork.example.com/mixed37';self.visible.dynamic(url);self.drain();self.assertEqual(self.visible.dynamic(url),'')

    def test_dns_failure_and_missing_provider_fields_keep_neutral_placeholder(self):
        row=dict(kind='series',cover='https://artwork.example.com/dns37')
        with mock.patch.object(self.visible.socket,'getaddrinfo',side_effect=socket.gaierror('PRIVATE')):
            first=self.m.art.local_art(row)['poster'];self.drain();self.assertEqual(self.m.art.local_art(row)['poster'],first)
        self.assertTrue(first.endswith('series.png'))
        self.assertTrue(self.m.art.local_art(dict(kind='vod'))['poster'].endswith('vod.png'))
        self.m.http.assert_not_called()

    def test_waiting_dns_does_not_block_native_search_or_ui_owner(self):
        entered=threading.Event();release=threading.Event()
        def resolve(*args,**kw):entered.set();release.wait(3);return []
        with mock.patch.object(self.visible.socket,'getaddrinfo',side_effect=resolve):
            try:
                self.m.art.local_art(dict(cover='https://artwork.example.com/held37'))
                self.assertTrue(entered.wait(1))
                window=self.m.media_window();window._search_prompt=False
                self.assertFalse(release.is_set());self.assertTrue(self.visible._threads['dynamic'].is_alive())
                window.close()
            finally:release.set();self.drain()

    def test_texture_error_fallback_changes_no_geometry_or_focus_controls(self):
        import xml.etree.ElementTree as ET
        for name in ('XCMateMedia.xml','XCMateGuide.xml'):
            tree=ET.parse(ADDON/'resources/skins/Default/720p'/name)
            textures=[n for n in tree.iter('texture') if n.text in ('$INFO[ListItem.Art(poster)]','$INFO[ListItem.Art(thumb)]')]
            self.assertTrue(textures);self.assertTrue(all(n.get('fallback','').startswith('special://home/addons/plugin.video.xtreammate/') for n in textures))
