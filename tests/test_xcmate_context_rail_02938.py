"""Shared rail attaches to real media views; unchanged search remains excluded."""
import importlib,sys,types,unittest
from unittest import mock
import xcmate027_fixture as model
import test_xcmate_kodi21_overlay as native

class ContextRail38(model.Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();gui=sys.modules['xbmcgui']
        gui.ControlButton=native.ControlButton;gui.ControlImage=native.ControlImage;gui.ControlLabel=native.ControlLabel
        original=model.WindowXML.getControl
        def add(window,control):
            if not hasattr(window,'extra_controls'):window.extra_controls={}
            window.extra_controls[control.getId()]=control
        def get(window,cid):
            if cid in getattr(window,'extra_controls',{}):return window.extra_controls[cid]
            return original(window,cid)
        methods=dict(addControl=add,addControls=lambda w,values:[add(w,v) for v in values],getControl=get,
                     getWidth=lambda w:1280,getHeight=lambda w:720,setFocus=lambda w,c:setattr(w,'focus',c.getId()))
        for name,fn in methods.items():
            patch=mock.patch.object(model.WindowXML,name,fn,create=True);patch.start();self.addCleanup(patch.stop)

    def test_media_edge_opens_and_back_restores_original_context_without_playback(self):
        window=self.media_window();window.setFocusId(120);before=(window.mode,window.category,window.offset,list(window.rows))
        window.onAction(types.SimpleNamespace(getId=lambda:1));self.assertTrue(window._navigation_rail.active)
        for _ in range(20):
            window.onAction(types.SimpleNamespace(getId=lambda:4));window.onAction(types.SimpleNamespace(getId=lambda:3))
        window.onAction(types.SimpleNamespace(getId=lambda:92));self.assertFalse(window._navigation_rail.active)
        self.assertEqual((window.mode,window.category,window.offset,window.rows),before);self.assertEqual(window.getFocusId(),120)
        self.assertFalse(self.builtins);self.client._get_json.assert_not_called()

    def test_search_cannot_open_rail_and_controls_stay_unchanged(self):
        window=self.media_window();window.mode='search';window._show('search')
        from nav_rail import open_in_view
        self.assertFalse(open_in_view(window,'media'));self.assertFalse(getattr(window,'extra_controls',{}))
        self.assertTrue(all(window.getControl(cid).isVisible() for cid in (700,701,702)))

    def test_native_click_queues_exact_destination_only_after_parent_release(self):
        window=self.media_window();window.setFocusId(120);window.onAction(types.SimpleNamespace(getId=lambda:1))
        rail=window._navigation_rail;rail.position=3;window.onClick(rail.buttons[3].getId())
        self.assertEqual(window._nav_destination,'movies_home');self.assertTrue(window._closed);self.assertFalse(self.builtins)

    def test_foreign_modal_defers_queued_navigation_and_token_takeover_cancels_it(self):
        nav=importlib.import_module('navigation_dispatch');life=importlib.import_module('window_lifecycle')
        self.assertTrue(nav.dispatch('movies_home','p'));self.assertFalse(nav.dispatch('series_home','p'))
        with mock.patch.object(life,'state',return_value=dict(window=10025,dialog=999,modal=True,updating=False)),mock.patch.object(life,'lease',return_value=''):
            nav.poll();self.assertFalse(self.builtins)
        with mock.patch.object(life,'state',return_value=dict(window=10025,dialog=0,modal=False,updating=False)),mock.patch.object(life,'lease',return_value=''):
            nav.poll();nav.poll()
        self.assertEqual(len(self.builtins),1);self.assertIn('action=movies_home',self.builtins[0])

    def test_invalid_navigation_destination_is_rejected(self):
        nav=importlib.import_module('navigation_dispatch')
        self.assertFalse(nav.dispatch('System.Exec(unsafe)','p'));self.assertFalse(self.builtins)

    def test_hidden_detail_control_300_is_never_focused_from_search(self):
        window=self.media_window();window.mode='search';window._show('search');window._mode_focus['search']=300
        self.assertFalse(window.getControl(300).isVisible());window.setFocusId(300)
        self.assertNotEqual(window.getFocusId(),300);self.assertIn(window.getFocusId(),window._valid_focus())

    def test_native_detail_menu_edges_have_visibility_and_enabled_conditions(self):
        import xml.etree.ElementTree as ET
        node=ET.parse(model.ADDON/'resources/skins/Default/720p/XCMateMedia.xml').find(".//control[@id='820']")
        for name in ('onleft','ondown'):
            routes=node.findall(name);self.assertEqual([r.text for r in routes],['300','400'])
            self.assertTrue(all(r.get('condition') for r in routes))

    def test_large_guide_group_edge_rail_restores_context_twenty_times(self):
        import test_xcmate_guide_navigation_02922 as guide_model
        case=guide_model.GuideNavigationTests(methodName='runTest');case.setUp();self.addCleanup(case.doCleanups)
        gui=sys.modules['xbmcgui'];gui.ControlButton=native.ControlButton;gui.ControlImage=native.ControlImage;gui.ControlLabel=native.ControlLabel
        window=case.window();window._show_groups();before=(window.category,window.offset,window.origin,window.cursor,window.row)
        for _ in range(20):
            window.onAction(types.SimpleNamespace(getId=lambda:1));self.assertTrue(window._navigation_rail.active)
            window.onAction(types.SimpleNamespace(getId=lambda:92));self.assertFalse(window._navigation_rail.active)
            self.assertEqual((window.category,window.offset,window.origin,window.cursor,window.row),before)
            self.assertEqual(window.mode,'groups')
