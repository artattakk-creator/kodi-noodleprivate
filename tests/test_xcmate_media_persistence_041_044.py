"""Durable art jobs and three landing rails against actual SQLite/UI code."""
import importlib
import json
from pathlib import Path
import struct
import sys
import time
import unittest
import zlib
from unittest import mock
from xcmate027_fixture import Fixture


class PersistenceTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        sys.modules.pop('art_store',None);self.store=importlib.import_module('art_store')
        self.art=importlib.import_module('media_art')
        def chunk(kind,data):
            return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
        self.png=(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',100,150,8,2,0,0,0))+
            chunk(b'IDAT',zlib.compress((b'\0'+b'\x10\x20\x30'*100)*150))+chunk(b'IEND',b''))
        self.http=sys.modules['utils'].http_get;self.http.side_effect=None;self.http.return_value=(self.png,{})

    def test_over_hundred_covers_survive_return_restart_and_never_refetch(self):
        urls=['https://image.invalid/'+str(i) for i in range(130)]
        for url in urls: self.assertTrue(self.art.fetch(url))
        self.assertEqual(self.http.call_count,130)
        self.assertEqual(len(list((self.folder/'media_art_v1').glob('*.img'))),130)
        restarted=importlib.reload(self.art)
        for url in urls: self.assertTrue(restarted.cached(url));restarted.fetch(url)
        self.assertEqual(self.http.call_count,130)
        self.assertEqual(self.store.status()['counts']['READY'],130)

    def test_budget_or_disk_full_keeps_existing_images_and_does_not_evict(self):
        first=self.art.fetch('https://image.invalid/first');before=Path(first).read_bytes()
        with mock.patch.object(self.store,'budget',return_value=len(self.png)):
            with self.assertRaises(OSError): self.art.fetch('https://image.invalid/second')
        import import_budget
        with mock.patch.object(import_budget,'check_space',side_effect=OSError(28,'full')):
            with self.assertRaises(OSError): self.art.fetch('https://image.invalid/third')
        self.assertEqual(Path(first).read_bytes(),before)
        self.assertEqual(self.http.call_count,1)

    def test_durable_queue_prioritizes_visible_and_limits_retries_after_restart(self):
        self.store.enqueue(['https://image.invalid/background'],20)
        self.store.enqueue(['https://image.invalid/visible'],0)
        self.store=importlib.reload(self.store)
        self.assertTrue(self.store.run_one(now=time.time()+1))
        self.assertEqual(self.http.call_args.args[0],'https://image.invalid/visible')
        self.http.side_effect=TimeoutError('SECRET')
        stamp=time.time()+60
        for n in range(5): self.store.run_one(now=stamp+n*1801)
        db=self.store.connect()
        try: row=dict(db.execute("SELECT * FROM jobs WHERE status='FAILED'").fetchone())
        finally: db.close()
        self.assertEqual(row['attempts'],3)
        calls=self.http.call_count;self.store.run_one(now=stamp+100000);self.assertEqual(self.http.call_count,calls)
        self.store.retry();self.assertTrue(self.store.run_one(now=stamp+100001))

    def test_worker_lease_blocks_parallel_download_and_recovers_after_expiry(self):
        self.store.enqueue(['https://image.invalid/one'])
        db=self.store.connect()
        with db: db.execute('UPDATE worker SET until=? WHERE id=1',(time.time()+30,))
        db.close()
        self.assertFalse(self.store.run_one());self.http.assert_not_called()
        self.assertTrue(self.store.run_one(now=time.time()+31))

    def test_expired_worker_cannot_release_new_owner_lease(self):
        self.store.enqueue(['https://image.invalid/one'])
        def takeover(url):
            db=self.store.connect()
            with db: db.execute("UPDATE worker SET owner='replacement',until=9999999999 WHERE id=1")
            db.close()
        with mock.patch.object(self.art,'fetch',side_effect=takeover): self.store.run_one()
        db=self.store.connect()
        try: self.assertEqual(db.execute('SELECT owner FROM worker').fetchone()[0],'replacement')
        finally: db.close()

    def test_corrupt_file_is_not_used_and_legacy_valid_files_are_preserved(self):
        filename=self.art.fetch('https://image.invalid/old');Path(filename).write_bytes(b'bad')
        self.assertFalse(self.art.cached('https://image.invalid/old'))
        self.assertEqual(self.art.fetch('https://image.invalid/old'),filename)
        self.assertEqual(Path(filename).read_bytes(),self.png)
        self.assertEqual(self.http.call_count,2)

    def test_landing_favourites_continue_and_immediate_remove(self):
        self.state.toggle('p','vod','2')
        self.state.save_progress(dict(pid='p',kind='vod',sid='3'),600,2700)
        w=self.media_window();self.assertEqual([r['sid'] for r in w.rails[111]],['2'])
        self.assertEqual([r['sid'] for r in w.rails[112]],['3'])
        self.assertEqual(w.getFocusId(),112)
        w.native(4);self.assertEqual(w.getFocusId(),111)
        w.native(4);self.assertEqual(w.getFocusId(),110)
        w.native(3);self.assertEqual(w.getFocusId(),111)
        w.native(117);self.assertFalse(w.rails[111]);self.assertEqual(w.getFocusId(),120)
        self.assertFalse(self.state.favourite('p','vod','2'))
        self.assertEqual(self.state.progress('p','vod','3')['position'],600)

    def test_favourite_detail_back_restores_rail_and_selection(self):
        self.state.toggle('p','vod','2')
        w=self.media_window();w.setFocusId(111);w.native(7);self.settle(w)
        self.assertEqual(w.mode,'detail');w.native(92);self.settle(w)
        self.assertEqual(w.getFocusId(),111)

    def test_favourite_snapshot_survives_missing_provider_rows_and_completion(self):
        item=self.index.Reader('p').get('vod','2')
        self.state.toggle('p','vod','2',item)
        self.state.save_progress(dict(pid='p',kind='vod',sid='2'),2690,2700)
        self.index.replace_catalog('p','vod',[],[])
        rows=self.state.rail_items('p','vod',self.index.Reader('p'))
        self.assertEqual(rows[0]['name'],item['name']);self.assertTrue(rows[0]['_unavailable'])
        self.assertTrue(self.state.favourite('p','vod','2'))
        self.assertFalse(self.state.rail_items('other','vod',self.index.Reader('other')))

    def test_visible_art_refresh_updates_nonfocused_tiles_without_reload(self):
        w=self.media_window();row=w.rows[1]
        before=w.getControl(110).getListItem(1).art['poster']
        self.art.fetch(row['stream_icon']);w._refresh_art()
        after=w.getControl(110).getListItem(1).art['poster']
        self.assertNotEqual(before,after);self.assertTrue(Path(after).is_file())
        self.assertEqual(w.selected['sid'],w.rows[0]['sid'])

    def test_series_continue_status_and_favourites_are_independent(self):
        self.state.toggle('p','series','1')
        self.state.save_progress(dict(pid='p',kind='episode',sid='12',series_id='1',season='1',episode='2'),300,1200)
        w=self.media_window('series');self.assertEqual(w.rails[112][0]['sid'],'1')
        w.native(7);self.settle(w)
        choice=next(i for i,(_,action) in enumerate(w.actions) if action=='seasons')
        w.getControl(300).selectItem(choice);w.onClick(300);w.onClick(330)
        self.assertTrue(any('25 %' in li.label for li in w.getControl(330).items))
        self.state.mark_episode('p',dict(sid='12',series_id='1',season=1),True)
        w._refresh_rails();self.assertFalse(w.rails[112]);self.assertTrue(w.rails[111])
