"""Kodi control compatibility smoke tests for XtreamMate on-video UI."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

LIB=Path(__file__).resolve().parents[1]/'src/plugin.video.xtreammate/resources/lib'
class UIControl:
    def __init__(self,*args,**kw):
        if isinstance(self,ControlList):
            unexpected=set(kw)-{'font','textColor','selectedColor','itemHeight','space','imageWidth','imageHeight','alignment','buttonTexture','buttonFocusTexture','itemTextXOffset','itemTextYOffset','scrollTime'}
            if unexpected:raise TypeError('invalid Kodi ControlList kwargs '+str(unexpected))
        self.labels=[];self.selected=0;self.id=id(self)
    def setVisible(self,v):pass
    def setLabel(self,label):pass
    def reset(self):self.labels=[]
    def addItems(self,values):self.labels=list(values)
    def selectItem(self,i):self.selected=i
    def getSelectedPosition(self):return self.selected
    def size(self):return len(self.labels)
    def getId(self):return self.id
class ControlList(UIControl):pass
class FakeWindow:
    def __init__(self):self.controls=[]
    def getWidth(self):return 1280
    def getHeight(self):return 720
    def addControl(self,x):self.controls.append(x)
    def setFocus(self,x):self.focus=x
class KodiOverlayTests(unittest.TestCase):
    def test_native_control_arguments_allow_oninit(self):
        fakegui=types.ModuleType('xbmcgui')
        fakegui.WindowDialog=FakeWindow
        fakegui.ControlList=ControlList
        fakegui.ControlButton=UIControl
        fakegui.ControlImage=UIControl
        fakegui.ControlLabel=UIControl
        props={}
        class Property:
            def setProperty(self,k,v):props[k]=v
        fakegui.Window=lambda id: Property()
        addon=types.ModuleType('xbmcaddon')
        addon.Addon=lambda: types.SimpleNamespace(getAddonInfo=lambda name:'/tmp/xtreammate')
        fakeutils=types.ModuleType('utils')
        fakeutils.info=fakeutils.warn=lambda *args:None
        fakeutils.error=lambda *args:None
        fakeutils.addon_data_dir=lambda:'/tmp'
        fakeepg=types.ModuleType('epg')
        fakeepg.load_cache=lambda *args:{}
        fakeviews=types.ModuleType('epg_views')
        fakeviews.guide_for_channel=lambda *args:{'now':'','next':''}
        fakeviews.row_title=lambda name, guide:name
        with mock.patch.dict(sys.modules,{'xbmc':types.ModuleType('xbmc'),'xbmcgui':fakegui,'xbmcaddon':addon,'utils':fakeutils,'epg':fakeepg,'epg_views':fakeviews}):
            spec=importlib.util.spec_from_file_location('xtream_overlay_test',LIB/'live_overlay.py')
            mod=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            overlay=mod.LiveNavigator.__new__(mod.LiveNavigator)
            FakeWindow.__init__(overlay)
            overlay.portal={'name':'Demo','id':'p'}
            overlay.mode='hidden'
            overlay._focus_main=0
            overlay._focus_extra=0
            overlay._drawn=False
            overlay._highlight={'groups':0,'channels':0}
            overlay.groups=[]
            overlay.channels=[]
            overlay.enabled=set()
            overlay.rows=[]
            overlay._catalog_ready=True
            overlay.sid='1'
            overlay.category_id='*'
            overlay._scroll_to_current=True
            overlay.onInit()
            self.assertTrue(overlay._drawn)
            self.assertEqual(props.get('XtreamMate.OverlayStatus'),'bereit')
            overlay.handle_command('left')
            self.assertEqual(overlay.mode,'channels')
            overlay.handle_command('left')
            self.assertEqual(overlay.mode,'groups')
            overlay.handle_command('left')
            self.assertEqual(overlay.mode,'hidden')

    def test_channel_list_no_sync_epg_download(self):
        source=(LIB/'main.py').read_text(encoding='utf-8')
        section=source[source.index('    def _epg_cache(self, p: dict):'):source.index('    def _epg_mgr(self, p: dict):')]
        self.assertNotIn('_refresh_portal_epg',section)
        self.assertIn('warmup_async',section)
        self.assertIn("xc.get_cached_catalog('get_live_streams')",source)

    def test_remote_epg_is_cache_only_on_gui_thread(self):
        source=(LIB/'live_overlay.py').read_text(encoding='utf-8')
        section=source[source.index('    def _epg(self):'):source.index('    def _execute(',source.index('    def _epg(self):'))]
        self.assertIn('cached_only=True',section)
        self.assertIn('threading.Thread(',section)
        self.assertNotIn('self.xc.get_short_epg(self.sid',section)

if __name__=='__main__':unittest.main()
