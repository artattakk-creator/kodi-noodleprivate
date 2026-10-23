"""Current .22 renderer contracts with the 98 original images, no provider I/O."""
import hashlib,importlib,json,sys,types,unittest
from pathlib import Path
from unittest import mock
import xml.etree.ElementTree as ET
from xcmate027_fixture import Fixture,ADDON,QueuedPool

THEME=ADDON.parents[1]/'themes/xcmate/space-premium/XCMate-Space-Premium-1.0.0.zip'


class PortTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('theme_store','theme_package','theme_render'):sys.modules.pop(name,None)
        self.store=importlib.import_module('theme_store')
        factory=sys.modules['xbmcaddon'].Addon
        def addon(*args):
            value=factory(*args);original=value.getAddonInfo
            value.getAddonInfo=lambda key:'0.1.29.24' if key=='version' else original(key)
            return value
        sys.modules['xbmcaddon'].Addon=addon
        sys.modules['xbmc'].Player=lambda:types.SimpleNamespace(isPlaying=lambda:False)
        self.revision=self.store.install(THEME);self.store.select(self.revision)

    def test_appearance_choice_persists_and_explicit_core_survives_reload(self):
        appearance=importlib.import_module('appearance')
        values=appearance.read();self.assertEqual(values['theme'],'space-premium')
        self.assertEqual(importlib.reload(self.store).current()['revision'],self.revision)
        self.store.select('');self.assertIsNone(importlib.reload(self.store).current());self.assertEqual(appearance.read()['theme'],'core')
        self.assertTrue((self.store.root()/'packages'/self.revision).is_dir())

    def test_old_theme_preference_migrates_without_changing_other_preferences(self):
        appearance=importlib.import_module('appearance');values=appearance.read();values['text']='AABBCC';appearance.save(values)
        (self.store.root()/'selection.json').unlink()
        self.assertEqual(importlib.reload(self.store).current()['revision'],self.revision)
        self.assertEqual(appearance.read()['text'],'AABBCC')

    def test_missing_package_falls_back_without_discarding_saved_preference(self):
        folder=self.store.root()/'packages'/self.revision;(folder/'theme.json').rename(folder/'not-active.json')
        self.assertIsNone(self.store.current());self.assertEqual(importlib.import_module('appearance').read()['theme'],'space-premium')
        sys.modules['utils'].http_get.assert_not_called()

    def test_current_guide_grid_texture_generation_keeps_white_focus_native_links_and_frame(self):
        appearance=importlib.import_module('appearance');original=ET.parse(ADDON/'resources/skins/Default/720p/XCMateGuideGrid.xml')
        generated=Path(appearance.window_source('XCMateGuideGrid.xml'))/'resources/skins/Default/720p/XCMateGuideGrid.xml';tree=ET.parse(generated)
        for cid in [str(n) for n in range(310,316)]+['200','730','750','1000']:
            before=original.find(".//control[@id='"+cid+"']");after=tree.find(".//control[@id='"+cid+"']")
            if before is None:continue
            for field in ('left','top','width','height','onleft','onright','onup','ondown','textcolor','focusedcolor','texturefocus'):
                self.assertEqual(before.findtext(field),after.findtext(field),cid+':'+field)
        text=generated.read_text();self.assertIn('assets/epg/bg-guide.jpg',text);self.assertIn('assets/epg/icon-today.png',text)
        self.assertIn('guide_focus_frame.png',text)

    def test_installed_manager_opens_offline_and_cancel_never_fetches_catalogue(self):
        ui=importlib.import_module('theme_ui');catalog=importlib.import_module('theme_catalog');self.dialog.select.return_value=-1
        with mock.patch.object(ui,'job',side_effect=lambda fn:fn(lambda:False)),mock.patch.object(catalog,'catalogue',side_effect=AssertionError('offline')):
            ui.manage()
        labels=self.dialog.select.call_args.args[1]
        self.assertTrue(labels);self.assertTrue((self.store.root()/'selection.json').exists())
        sys.modules['utils'].http_get.assert_not_called()

    def test_original_icon_is_immutable_across_premium_and_core(self):
        branding=importlib.import_module('branding');expected='81da1003a2753ec6afbdd50b2a320e738a2131ad9f0d76606da1babdd0d2f135'
        for selected in ('',self.revision,''):
            self.store.select(selected);self.assertEqual(hashlib.sha256(Path(branding.icon()).read_bytes()).hexdigest(),expected)

    def test_design_route_is_a_non_playable_action_and_needs_no_portal(self):
        self.portals=[];self.router._params.update(action='theme_manager')
        ui=importlib.import_module('theme_ui')
        with mock.patch.object(ui,'manage') as manage:self.routes.dispatch(self.router)
        manage.assert_called_once();self.assertTrue(self.ends)
        import window_navigation
        self.assertIn('theme_manager',window_navigation.DIALOG_ACTIONS)
