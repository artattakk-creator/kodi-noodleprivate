"""Minimal Kodi stub integration checks, without access to NoodleMagazine."""
import importlib.util
import os
import sys
import tempfile
import types
import urllib.parse
import unittest
from unittest import mock

ADDON_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'plugin.video.noodleprivate'))
sys.path.insert(0, ADDON_ROOT)


class DummyListItem:
    def __init__(self, label='', path='', **kw):
        self.label, self.path, self.properties, self.info, self.art = label, path, {}, {}, {}
    def setArt(self, art): self.art = art
    def setInfo(self, k, v): self.info = v
    def setProperty(self, k, v): self.properties[k] = v
    def addContextMenuItems(self, ctx): self.context = ctx
    def getPath(self): return self.path
    def setMimeType(self, typ): self.mime = typ
    def setContentLookup(self, v): pass


class KodiTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.log = []
        self.user_inputs = []
        self.selections = []
        def mkmod(name, **attrs):
            mod = types.ModuleType(name)
            mod.__dict__.update(attrs)
            sys.modules[name] = mod
            return mod
        this = self
        class DummyAddon:
            def getAddonInfo(self, key):
                return {'profile':this.tmp.name, 'path':ADDON_ROOT}.get(key,'')
        class DummyDialog:
            def yesno(self, *args): return True
            def notification(self, *args): pass
            def select(self, *args): return this.selections.pop(0) if this.selections else -1
            def input(self, *args, **kwargs): return this.user_inputs.pop(0) if this.user_inputs else ''
            def textviewer(self, *args): pass
        mkmod('xbmc', LOGWARNING=2, LOGERROR=3, log=lambda *x:None,
              getCondVisibility=lambda x:True,
              executebuiltin=lambda x:this.log.append(('builtin',x)))
        mkmod('xbmcaddon', Addon=DummyAddon)
        class DummyProgress:
            def create(self, *args): this.log.append(('progress_open',))
            def update(self, *args): this.log.append(('progress_update',))
            def iscanceled(self): return False
            def close(self): this.log.append(('progress_close',))
        mkmod('xbmcgui', ListItem=DummyListItem, Dialog=DummyDialog,
              DialogProgress=DummyProgress, INPUT_ALPHANUM=0)
        mkmod('xbmcvfs', translatePath=lambda x:x)
        mkmod('xbmcplugin', addDirectoryItem=lambda h,u,i,isFolder:this.log.append(('item',u,i,isFolder)),
              setContent=lambda *x:None, endOfDirectory=lambda *args, **kwargs:this.log.append(('eod',)),
              setResolvedUrl=lambda h,good,li:this.log.append(('resolved',good,li)))
        sys.argv=['plugin://plugin.video.noodleprivate/', '7','']
        spec=importlib.util.spec_from_file_location('np_default', os.path.join(ADDON_ROOT, 'default.py'))
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        self.mod.STORE.update_prefs(confirmed_adult=True)
    def tearDown(self):
        self.tmp.cleanup()
    def test_root_has_widgets(self):
        self.mod.root()
        urls=[x[1] for x in self.log if x[0]=='item']
        self.assertTrue(any('section=trending' in x for x in urls))
        self.assertTrue(any('action=favorites' in x for x in urls))
        self.assertEqual(self.log[-1][0],'eod')
    def test_listing_renders_playable_videos(self):
        from test_site import SAMPLE_LIST
        self.mod._read_page=lambda *a, **kw:SAMPLE_LIST
        self.mod.listing('popular')
        vids=[x for x in self.log if x[0]=='item' and not x[-1]]
        self.assertEqual(len(vids),2)
        self.assertEqual(vids[0][2].properties['IsPlayable'],'true')
        self.assertEqual(vids[0][2].info['duration'],1265)
    def test_search_works_without_container_navigation_race(self):
        from test_site import SAMPLE_LIST
        self.user_inputs = ['Video Alpha']
        self.mod._read_page = lambda *a, **kw: SAMPLE_LIST
        self.mod.ARGS = {'action': 'search_prompt'}
        self.mod.run()
        videos = [x for x in self.log if x[0] == 'item' and not x[-1]]
        self.assertEqual(len(videos), 2)
        self.assertEqual(sum(x[0]=='eod' for x in self.log), 1)
        self.assertFalse(any('Container.Update' in str(x) for x in self.log))
        self.assertIn('Video Alpha', self.mod.STORE.state()['searches'])

    def test_add_video_to_custom_list_and_remove(self):
        video = {'url': 'https://noodlemagazine.com/watch/-101_456',
                 'title': 'Sample', 'image': '', 'duration': 88}
        self.user_inputs = ['Privat 2026']
        self.selections = [0]  # Neue Liste
        self.mod.collection_add(video)
        collections = self.mod.STORE.collections()
        self.assertEqual(len(collections), 2)
        ident = next(k for k in collections if k != 'default')
        self.assertIn(video['url'], collections[ident]['items'])
        self.assertTrue(any(x[0] == 'builtin' and x[1] == 'Container.Refresh' for x in self.log))
        self.mod.collection_view(ident)
        cards = [x[2] for x in self.log if x[0]=='item' and not x[-1]]
        self.assertTrue(any('Aus dieser Liste entfernen' in [c[0] for c in v.context] for v in cards))
        self.mod.collection_remove({'url':video['url'], 'collection_id': ident})
        self.assertEqual(len(self.mod.STORE.get_collection(ident)['items']), 0)

    def test_existing_list_membership_does_not_toggle_off(self):
        video = {'url': 'https://noodlemagazine.com/watch/-101_456', 'title':'T'}
        self.mod.STORE.add_to_collection('default', video)
        self.selections = [1]
        self.mod.collection_add(video)
        self.assertIn(video['url'], self.mod.STORE.get_collection('default')['items'])

    def test_rename_and_delete_list(self):
        ident = self.mod.STORE.create_collection('Erste Liste')
        self.user_inputs = ['Umbenannt']
        self.mod.collection_rename({'collection_id':ident})
        self.assertEqual(self.mod.STORE.get_collection(ident)['name'], 'Umbenannt')
        self.mod.collection_delete({'collection_id':ident})
        self.assertNotIn(ident, self.mod.STORE.collections())

    def test_player_resolves(self):
        from test_site import SAMPLE_PLAY
        self.mod.fetch_html=lambda x:SAMPLE_PLAY
        self.mod.play({'url':'https://noodlemagazine.com/watch/-101_456','title':'Test'})
        resolved=[x for x in self.log if x[0]=='resolved']
        self.assertEqual(len(resolved),1)
        self.assertTrue(resolved[0][1])
        self.assertEqual(resolved[0][2].properties['inputstream'],'inputstream.adaptive')
    def test_merged_search_keeps_all_sources_and_closes_progress(self):
        from test_site import SAMPLE_LIST
        self.mod._read_page = lambda *args, **kw: SAMPLE_LIST
        def bridge(provider, uri):
            return [{'url': 'plugin://plugin.video.cumination/?mode={}.Playvid&url=https%3A%2F%2Fexample.net%2F123'.format(provider),
                     'title': 'Test', 'provider': provider, 'is_folder': False}]
        self.mod._bridge_items = bridge
        self.mod.global_search('query')
        cards = [x[2] for x in self.log if x[0] == 'item' and not x[-1]]
        self.assertEqual(len(cards), 8)
        self.assertTrue(any('[xHamster]' in card.label for card in cards))
        self.assertTrue(any('[NoodleMagazine]' in card.label for card in cards))
        self.assertEqual(sum(x[0]=='eod' for x in self.log), 1)
        self.assertEqual(sum(x[0]=='progress_close' for x in self.log), 1)

    def test_merged_search_survives_one_broken_provider(self):
        from test_site import SAMPLE_LIST
        from resources.lib.providers import BridgeError
        self.mod._read_page=lambda *a, **kw: SAMPLE_LIST
        def broken(provider, uri):
            raise BridgeError('HTTP 403')
        self.mod._bridge_items=broken
        self.mod.global_search('title')
        cards = [x[2] for x in self.log if x[0] == 'item' and not x[-1]]
        self.assertEqual(len(cards), 2)
        self.assertEqual(self.log[-1][0], 'eod')

    def test_save_cumination_video_in_named_favorites(self):
        from resources.lib.providers import cumination_uri
        entry = cumination_uri('eporner') + '&more=1'
        item = {'url': entry, 'title': 'Test EPorner', 'provider': 'eporner', 'image': '', 'duration': 180}
        ident = self.mod.STORE.create_collection('Meine Anbieter')
        self.selections = [2]  # [new, default, custom]
        self.mod.collection_add(item)
        self.assertIn(entry, self.mod.STORE.get_collection(ident)['items'])
        self.mod.collection_remove({'url': entry, 'collection_id': ident})
        self.assertNotIn(entry, self.mod.STORE.get_collection(ident)['items'])

    def test_disabled_provider_visible_in_catalogue_but_not_enabled(self):
        self.mod.STORE.update_prefs(provider_enabled={'xhamster': False})
        self.mod.provider_directory()
        urls=[x[1] for x in self.log if x[0]=='item']
        self.assertTrue(any('provider=xhamster' in u and 'provider_admin_detail' in u for u in urls))
        self.assertFalse(any('provider=xhamster' in u and 'provider_browse' in u for u in urls))
        self.assertTrue(any('provider=eporner' in u for u in urls))

    def test_cumination_items_forward_playback_to_original_plugin(self):
        from resources.lib.providers import cumination_uri
        uri=cumination_uri('eporner', 'Search', 'test')
        self.mod.video({'url':uri,'title':'Example','provider':'eporner'})
        li=[x[2] for x in self.log if x[0]=='item'][-1]
        self.assertEqual(li.getPath(),uri)
        self.assertTrue(any('Zu Favoritenliste' in entry[0] for entry in li.context))

    def test_bad_player_url(self):
        self.mod.play({'url':'https://other.example/watch/123'})
        self.assertFalse([x for x in self.log if x[0]=='resolved'][0][1])

if __name__ == '__main__':unittest.main()
