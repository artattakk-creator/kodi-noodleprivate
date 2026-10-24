"""Original splash byte identity and stable Core presentation, no focus changes."""
import hashlib,importlib,unittest,xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,ADDON,ROOT


class Splash30Tests(Fixture,unittest.TestCase):
    def test_exact_original_splash_is_bundled_and_original_icon_unchanged(self):
        data=(ADDON/'resources/media/lightweight_splash.jpg').read_bytes()
        self.assertEqual(data,(ROOT/'themes/xcmate/space-premium/assets/branding/splash-1920.jpg').read_bytes())
        self.assertEqual(hashlib.sha256(data).hexdigest(),'2553464f81de674f3de8726ba1ec81dcf57d7c0232d39aa3322af10ee0435fcc')
        self.assertEqual(hashlib.sha256((ADDON/'icon.png').read_bytes()).hexdigest(),'81da1003a2753ec6afbdd50b2a320e738a2131ad9f0d76606da1babdd0d2f135')
        tree=ET.parse(ADDON/'resources/skins/Default/720p/XCMateMedia.xml')
        self.assertTrue(tree.findtext("./controls/control[@id='100']/texture").endswith('lightweight_splash.jpg'))
        self.assertTrue(tree.findtext("./controls/control[@id='104']/texture").endswith('media_shade.png'))

    def test_landing_and_search_keep_splash_during_cover_refresh_and_detail_can_show_fanart(self):
        render=importlib.import_module('theme_render');background=render.lightweight_background()
        for kind in ('vod','series'):
            w=self.media_window(kind);w._theme=None
            self.assertEqual(render.media_background(w,'/local/cover-fanart.jpg'),background)
            w._show('search');self.assertEqual(w.getControl(100).image,background)
            w.mode='search';w.selected=dict(sid='1',kind=kind,name='one')
            art=dict(poster='/local/poster.jpg',fanart='/local/fanart.jpg')
            with mock.patch('media_art.local_art',return_value=art):w._refresh_art()
            self.assertEqual(w.getControl(100).image,background)
            w.mode='detail';self.assertEqual(render.media_background(w,art['fanart']),art['fanart'])
            w._theme={'revision':'premium'};self.assertEqual(render.media_background(w,art['fanart']),art['fanart'])

    def test_home_and_settings_use_splash_without_activating_premium(self):
        import home_menu
        render=importlib.import_module('theme_render')
        with mock.patch.object(self.router,'_add_dir',wraps=self.router._add_dir) as directories,mock.patch.object(render,'snapshot',return_value=None):
            home_menu.show(self.router,self.portal)
            home_menu.settings(self.router,self.portal)
        self.assertTrue(self.added)
        self.assertTrue(all(item.art.get('fanart')==render.lightweight_background() for _,item,folder in self.added if not folder))
        self.assertTrue(directories.call_args_list)
        self.assertTrue(all(call.kwargs['fanart']==render.lightweight_background() for call in directories.call_args_list))
        self.assertFalse((self.folder/'appearance_v1.json').exists())


if __name__=='__main__':unittest.main()
