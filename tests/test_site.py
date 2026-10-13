import os
import json
import sys
import tempfile
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'plugin.video.noodleprivate')))
from resources.lib.site import parse_listing, parse_detail, listing_path, watch_url, SiteError
from resources.lib.storage import Storage

SAMPLE_LIST = '''<html><body>
<div class="item"><a href="/watch/-101_456"><img src="https://img.example.com/a.jpg"></a>
<span class="title">Video Alpha &amp; Beta</span><svg></svg> 21:05 <span class="hd_mark">HD</span></div>
<div class="item"><a href="/watch/-102_456"><img data-src="https://img.example.com/b.jpg"></a>
<span class="title">Video Gamma</span><span class="duration">1:01:05</span></div>
<div class="item"><a href="/watch/-101_456"><span class="title">Dupe</span></a></div>
<a class="more" data-page="1" data-i18n="show_more">Show more</a></body></html>'''
SAMPLE_PLAY = '''<html><meta property="og:title" content="Video Alpha">
<meta property="og:description" content="Plot sample"><meta property="og:image" content="https://example.com/poster.jpg">
<script>window.playlist = {"sources": [{"label":"480","file":"https://cdn.example.com/v480.mp4","type":"mp4"},
{"label":"1080","file":"//media.example.com/stream.m3u8","type":"hls"}]};</script></html>'''

class SiteTests(unittest.TestCase):
    def test_listing(self):
        videos, page = parse_listing(SAMPLE_LIST)
        self.assertEqual(page, 1)
        self.assertEqual(len(videos), 2)
        self.assertEqual(videos[0]['title'], 'Video Alpha & Beta')
        self.assertEqual(videos[0]['duration'], 1265)
        self.assertEqual(videos[1]['duration'], 3665)
        self.assertEqual(videos[1]['image'], 'https://img.example.com/b.jpg')
    def test_detail(self):
        d = parse_detail(SAMPLE_PLAY)
        self.assertEqual(d['title'], 'Video Alpha')
        self.assertEqual(len(d['sources']), 2)
        self.assertTrue(d['sources'][0]['hls'])
        self.assertEqual(d['sources'][0]['label'], '1080')
    def test_bad_url(self):
        with self.assertRaises(SiteError):
            watch_url('https://example.com/watch/-12_45')
    def test_search_path(self):
        url=listing_path('search','Such Begriff',1)
        self.assertIn('/video/Such%20Begriff?',url)
        self.assertIn('p=1',url)
    def test_collection_migration_preserves_old_favourites(self):
        with tempfile.TemporaryDirectory() as tmp:
            video = {'url':'https://noodlemagazine.com/watch/-1_2', 'title':'Old'}
            with open(os.path.join(tmp, 'state.json'), 'w', encoding='utf-8') as f:
                json.dump({'favorites': {video['url']: video}, 'recent': [], 'searches': []}, f)
            s = Storage(tmp)
            self.assertIn(video['url'], s.get_collection('default')['items'])
            new_id = s.create_collection('Abends')
            s.add_to_collection(new_id, video)
            s.remove_from_collection('default', video['url'])
            self.assertIn(video['url'], s.get_collection(new_id)['items'])
            s2 = Storage(tmp)
            self.assertNotIn(video['url'], s2.get_collection('default')['items'])
            self.assertEqual(s2.get_collection(new_id)['name'], 'Abends')

    def test_collection_names_unique_and_rename(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = Storage(tmp)
            ident = s.create_collection('Themen')
            with self.assertRaises(ValueError):
                s.create_collection('themen')
            self.assertEqual(s.rename_collection(ident, 'Was anderes'), 'Was anderes')
            with self.assertRaises(ValueError):
                s.rename_collection(ident, 'Meine Favoriten')

    def test_storage(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=Storage(tmp)
            self.assertFalse(s.prefs()['confirmed_adult'])
            v={'url':'https://noodlemagazine.com/watch/-101_456','title':'Test'}
            self.assertTrue(s.toggle_favorite(v))
            self.assertIn(v['url'], s.state()['favorites'])
            self.assertFalse(s.toggle_favorite(v))
            s.remember_play(v)
            self.assertEqual(len(s.state()['recent']),1)
            s.put_page('https://noodlemagazine.com/home','<html>hi</html>')
            self.assertEqual(s.get_page('https://noodlemagazine.com/home', 60),'<html>hi</html>')

if __name__ == '__main__':
    unittest.main()
