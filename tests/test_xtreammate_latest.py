"""Regression suite: provider added dates, first seen, category permissions and paths."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1] / 'src/plugin.video.xtreammate'
LIB=ROOT / 'resources/lib'
spec=importlib.util.spec_from_file_location('xm_latest', LIB / 'latest_media.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

NOW=1792000000

class LatestTests(unittest.TestCase):
    def setUp(self):
        d=tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        self.folder=d.name
    def test_dates_unix_ms_iso_and_invalid(self):
        self.assertEqual(mod.added_timestamp('1712345678', now=NOW),1712345678)
        self.assertEqual(mod.added_timestamp('1712345678000',now=NOW),1712345678)
        self.assertEqual(mod.added_timestamp('2025-05-13T12:30:00Z',now=NOW),1747139400)
        for bad in ('', 'nonsense', '0', '2030-01-01', True, None):
            self.assertIsNone(mod.added_timestamp(bad,now=NOW))
    def test_first_scan_is_baseline_not_fake_new(self):
        items=[{'stream_id':11,'name':'Old'},{'stream_id':12,'name':'Old2'}]
        self.assertEqual(mod.observe('srv1','get_vod_streams',items,self.folder,now=1700000000),{})
        self.assertEqual(mod.first_seen('srv1','get_vod_streams',items,self.folder),{})
        self.assertEqual(mod.recent_entries(items,'get_vod_streams',now=NOW),[])
        later=items+[{'stream_id':13,'name':'New'}]
        dates=mod.observe('srv1','get_vod_streams',later,self.folder,now=1711111111)
        self.assertEqual(dates,{'13':1711111111})
        self.assertEqual([x['name'] for x in mod.recent_entries(later,'get_vod_streams',dates,now=NOW)], ['New'])
        self.assertEqual(mod.first_seen('srv1','get_vod_streams',later,self.folder),dates)
    def test_sort_by_provider_date_not_year(self):
        items=[
            {'stream_id':1,'name':'Old-release-new-upload','year':'1980','added':'1750000000'},
            {'stream_id':2,'name':'New-release-old-upload','year':'2026','added':'1710000000'},
            {'stream_id':3,'name':'Invalid-no-sort','year':'2030'},
        ]
        self.assertEqual([x['stream_id'] for x in mod.recent_entries(items,'get_vod_streams',now=NOW)],[1,2])
    def test_separate_movie_and_series_provider_states(self):
        old=[{'stream_id':1}]; mod.observe('A','get_vod_streams',old,self.folder,now=1700000000)
        mod.observe('B','get_vod_streams',old,self.folder,now=1700000000)
        mod.observe('A','get_series',[{'series_id':10}],self.folder,now=1700000000)
        self.assertEqual(mod.observe('A','get_vod_streams',old+[{'stream_id':2}],self.folder,now=1710000000),{'2':1710000000})
        self.assertEqual(mod.first_seen('B','get_vod_streams',old,self.folder),{})
        self.assertEqual(mod.observe('A','get_series',[{'series_id':10},{'series_id':11}],self.folder,now=1710000000),{'11':1710000000})
    def test_bad_server_empty_index_does_not_reset_baseline(self):
        orig=[{'series_id':1}]; mod.observe('C','get_series',orig,self.folder,now=1700000000)
        self.assertEqual(mod.observe('C','get_series',[],self.folder,now=1710000000),{})
        self.assertEqual(mod.observe('C','get_series',orig+[{'series_id':2}],self.folder,now=1710000000),{'2':1710000000})
    def test_cached_items_backfill_baseline(self):
        old=[{'series_id':1,'name':'Old'}]
        self.assertEqual(mod.first_seen('D','get_series',old,self.folder),{})
        self.assertEqual(mod.first_seen('D','get_series',old,self.folder),{})
    def test_limit(self):
        arr=[{'stream_id':i,'added':str(1700000000+i)} for i in range(10)]
        self.assertEqual([a['stream_id'] for a in mod.recent_entries(arr,'get_vod_streams',limit=3,now=NOW)],[9,8,7])
    def test_directory_links_are_visible_on_xtream_home(self):
        src=(LIB/'main.py').read_text(encoding='utf-8')
        self.assertIn("'recent_vod'         : self._recent_vod",src)
        self.assertIn("'recent_series'      : self._recent_series",src)
        self.assertIn("icon=_ICON_VOD",src)
        self.assertIn("icon=_ICON_SERIES",src)
        self.assertIn('filter_entries(all_items, p[\'id\'], kind)',src)
        self.assertIn('xc.get_cached_catalog(action)',src)

if __name__=='__main__':
    unittest.main()
