"""Native XML focus and provider fanart routing, no live profile changes."""
import importlib,json,unittest
from pathlib import Path
from unittest import mock
import xml.etree.ElementTree as ET
from xcmate027_fixture import Fixture,ADDON

class MediaFocusTests(Fixture,unittest.TestCase):
    def test_neon_frame_is_used_for_every_interactive_layout_and_nine_slice_border(self):
        root=ET.parse(ADDON/'resources/skins/Default/720p/XCMateMedia.xml')
        for cid in (120,400,200,210,300,330,110,111,112):
            control=root.find(".//control[@id='"+str(cid)+"']")
            textures=control.findall('texturefocus')+control.findall('./focusedlayout/control/texture')
            frames=[n for n in textures if 'focus' in (n.text or '')]
            self.assertTrue(frames,cid)
            for frame in frames:self.assertTrue(frame.text.endswith('xcmate_focus_neon.png'));self.assertEqual(frame.get('border'),'6' if cid in (110,111,112,210) else '4')

    def test_existing_appearance_preferences_do_not_tint_or_dim_new_focus_frame(self):
        appearance=importlib.import_module('appearance');appearance.save(dict(appearance.DEFAULT,focus='2276A8',icon_opacity=25))
        before=Path(appearance.path()).read_bytes();generated=ET.parse(Path(appearance.window_source('XCMateMedia.xml'))/'resources/skins/Default/720p/XCMateMedia.xml')
        for texture in generated.iter():
            if (texture.text or '').endswith('xcmate_focus_neon.png'):self.assertIn(texture.get('colordiffuse'),(None,'FFFFFFFF','FF000000'))
        self.assertEqual(Path(appearance.path()).read_bytes(),before)

    def test_poster_is_not_used_as_fake_fanart(self):
        art=importlib.import_module('media_art');item=dict(cover='https://image.invalid/poster')
        with mock.patch.object(art,'cached',side_effect=lambda url:'/local/poster.img' if url==item['cover'] else ''):
            value=art.local_art(item)
        self.assertEqual(value['poster'],'/local/poster.img');self.assertEqual(value['fanart'],'')

    def test_nested_detail_fields_preserve_real_fanart_and_ignore_malformed_addresses(self):
        metadata=importlib.import_module('metadata_views');art=importlib.import_module('media_art')
        item=metadata.enrich(dict(sid='1',cover='https://image.invalid/poster'),dict(info=dict(plot='A'),movie_data=dict(backdrop_path=['bad','https://image.invalid/fanart'])))
        self.assertEqual(art.sources(item),('https://image.invalid/poster','https://image.invalid/fanart'))
        self.assertEqual(art.sources(dict(cover='bad',fanart='not a URL')),('',''))

    def test_asynchronous_fanart_refresh_updates_current_detail_without_reopening(self):
        self.details['get_vod_info']['info']['backdrop_path']=['https://image.invalid/fanart-one']
        art=importlib.import_module('media_art');downloaded=[False]
        def cached(url):return '/local/fanart-one.img' if downloaded[0] and url=='https://image.invalid/fanart-one' else ''
        with mock.patch.object(art,'cached',side_effect=cached):
            w=self.media_window();w.native(7);self.settle(w)
            self.assertTrue(w.getControl(100).image.endswith('lightweight_splash.jpg'))
            self.assertTrue(w.getControl(105).visible);self.assertFalse(w.getControl(104).visible)
            downloaded[0]=True;w._refresh_art();self.assertEqual(w.getControl(100).image,'/local/fanart-one.img')
            self.assertEqual(w.mode,'detail');w.native(92);self.settle(w);self.assertFalse(w.getControl(105).visible)

    def test_missing_fanart_for_new_title_clears_previous_title_background(self):
        art=importlib.import_module('media_art');w=self.media_window();w.mode='detail'
        with mock.patch.object(art,'cached',side_effect=lambda url:'/local/first.img' if url=='https://image.invalid/first-art' else ''):
            w._queue_art(dict(cover='https://image.invalid/one',backdrop_path='https://image.invalid/first-art'))
            self.assertEqual(w.getControl(100).image,'/local/first.img')
            w._queue_art(dict(cover='https://image.invalid/two'))
            self.assertTrue(w.getControl(100).image.endswith('lightweight_splash.jpg'))
