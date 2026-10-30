"""Offline contract for opt-in read-only XCMate Live-TV view60."""
import importlib.util
import os
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1] / 'src/plugin.video.xtreammate/resources'
LIB = ROOT / 'lib'
XML = ROOT / 'skins/Default/720p/XCMateLiveView60.xml'


class FakeControl:
    def __init__(self):
        self.value = ''
    def setLabel(self, value):
        self.value = value


class SafeLiveViewTests(unittest.TestCase):
    def setUp(self):
        self.xbmc = types.ModuleType('xbmc')
        self.xbmc.Monitor = object
        self.xbmcaddon = types.ModuleType('xbmcaddon')
        self.xbmcaddon.Addon = lambda: types.SimpleNamespace(getAddonInfo=lambda key: '/installed/xcmate')
        self.xbmcgui = types.ModuleType('xbmcgui')
        self.xbmcgui.WindowXMLDialog = type('WindowXMLDialog', (), {})
        self.xbmcgui.ListItem = type('ListItem', (), {})
        self.patch = patch.dict(sys.modules, {
            'xbmc': self.xbmc, 'xbmcaddon': self.xbmcaddon, 'xbmcgui': self.xbmcgui
        })
        self.patch.start()
        spec = importlib.util.spec_from_file_location('live_view60_tested', LIB / 'live_view60.py')
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        self.addCleanup(self.patch.stop)

    def test_small_logo_uses_provider_image(self):
        self.assertEqual(self.mod.logo_for({'stream_icon':'https://cdn.example/logo.png'}),
                         'https://cdn.example/logo.png')

    def test_missing_logo_is_neutral(self):
        self.assertEqual(self.mod.logo_for({'name':'Channel'}),
                         os.path.join('/installed/xcmate', 'resources','media','tv.png'))

    def test_start_group_allows_88_local_channels(self):
        rows = [{'sid':str(i),'name':'Channel '+str(i)} for i in range(88)]
        with patch.dict(sys.modules, {'widget_home50':types.SimpleNamespace(rows=lambda portal:(rows,'READY'))}):
            items,code=self.mod.load_rows({'id':'p'})
        self.assertEqual(len(items),88)
        self.assertEqual(code,'READY')

    def test_oversize_group_returns_safe_status(self):
        rows = [{'sid':str(i)} for i in range(self.mod.ROW_LIMIT+1)]
        with patch.dict(sys.modules, {'widget_home50':types.SimpleNamespace(rows=lambda portal:(rows,'READY'))}):
            items,code=self.mod.load_rows({'id':'p'})
        self.assertEqual(items,[])
        self.assertEqual(code,'TOO_MANY_CHANNELS')

    def test_just_one_epg_row_hydrated(self):
        captured=[]
        def render(portal,kind,rows,approved):
            captured.append((kind,len(rows)))
            return [{'props':{'XCMate.ProgrammeChannel46':'Das Erste'},'art':{}}]
        mods={'widget_render47':types.SimpleNamespace(values=render),
              'widget_art44':types.SimpleNamespace(read=lambda pid:{})}
        with patch.dict(sys.modules,mods):
            props,_=self.mod.preview({'id':'p'},{'sid':'101'})
        self.assertEqual(captured,[('live',1)])
        self.assertEqual(props['XCMate.ProgrammeChannel46'],'Das Erste')

    def test_ok_does_not_start_a_player(self):
        view=self.mod.SafeLiveView60()
        c=FakeControl()
        view.getControl=lambda cid:c
        view.onClick(200)
        self.assertIn('deaktiviert',c.value)

    def test_focus_future_tuple_completed_without_attributeerror(self):
        import concurrent.futures
        view=self.mod.SafeLiveView60()
        view.rows=[{'sid':'101','name':'Das Erste'}]
        view._focus_index=0
        view._focus_key=(0,'101')
        view._focus_requested=0.0
        view._shown=None
        view._focus_refresh=0.0
        view._rows_future=None
        done=concurrent.futures.Future()
        done.set_result(({'XCMate.ProgrammeTitle46':'Test'},{}))
        view._focus_future=(done,(0,'101'))
        view.getControl=lambda cid:types.SimpleNamespace(getSelectedPosition=lambda:0,
                                    setLabel=lambda v:None,setText=lambda v:None,
                                    setImage=lambda v:None,setPercent=lambda v:None)
        view._render_preview=lambda data:setattr(view,'_shown',(0,'101'))
        view.pump()
        self.assertIsNone(view._focus_future)
        self.assertEqual(view._shown,(0,'101'))

    def test_all_required_kodi_controls_exist(self):
        root=ET.parse(XML).getroot()
        found={n.get('id') for n in root.iter('control') if n.get('id')}
        self.assertTrue({str(n) for n in (101,110,111,112,113,114,115,116,117,118,119,200)}<=found)
        content=XML.read_text(encoding='utf-8')
        for forbidden in ('PlayerControl','RunPlugin(','PlayMedia(','<onfocus>','<onclick>'):
            self.assertNotIn(forbidden,content)

    def test_pin_only_entry_and_no_bingie_skin_change(self):
        app=(LIB/'app_routes.py').read_text(encoding='utf-8')
        lock=(LIB/'experimental45.py').read_text(encoding='utf-8')
        menu=(LIB/'settings_sections45.py').read_text(encoding='utf-8')
        self.assertIn("if action=='live_view60':",app)
        self.assertIn("'live_view60'",lock)
        self.assertIn("(36720,'live_view60',{})",menu)
        source=(LIB/'live_view60.py').read_text(encoding='utf-8')
        self.assertNotIn('PlayerControl(',source)
        self.assertNotIn('guide_playback',source)
        self.assertNotIn('script.skinshortcuts',source)


if __name__ == '__main__':
    unittest.main()
