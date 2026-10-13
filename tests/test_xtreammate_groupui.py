"""Kodi group checkbox and recordings-folder regression tests."""
import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock
import xml.etree.ElementTree as ET

LIB = Path(__file__).resolve().parent.parent/'src/plugin.video.xtreammate/resources/lib'

class GroupUITests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        utils = types.ModuleType('utils')
        utils.addon_data_dir = lambda: temp.name
        patch = mock.patch.dict(sys.modules, {'utils': utils})
        patch.start()
        self.addCleanup(patch.stop)
        xtream = types.ModuleType('xtream')
        class XC:
            def __init__(self, *a): pass
            def get_live_categories(self, force_refresh=False):
                return [{'category_id': str(n), 'category_name': 'DE '+str(n)}
                        for n in range(200)]
            get_vod_categories = get_series_categories = get_live_categories
        xtream.XtreamClient = XC
        patch2 = mock.patch.dict(sys.modules, {'xtream': xtream})
        patch2.start()
        self.addCleanup(patch2.stop)
        spec = importlib.util.spec_from_file_location('xm_group_ui', LIB/'group_selection.py')
        self.groups = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.groups)
        self.portal = {'id': 'p', 'type': 'xtream', 'xc_host': 'h',
                       'xc_user': 'u', 'xc_pass': 'pw'}

    def test_bulk_off_then_check_several_without_scrolling_reset(self):
        choices = iter([2,0])
        state = {'opens':0}
        class Dialog:
            def select(self,*a,**kw): return next(choices)
            def multiselect(self,title,options,preselect=None):
                state['opens'] += 1
                self_test.assertEqual(len(options), 200)
                self_test.assertEqual(preselect, [])
                return [30,70,105]
            def notification(self,*a): pass
        self_test = self
        gui = types.ModuleType('xbmcgui')
        gui.Dialog = Dialog
        with mock.patch.dict(sys.modules, {'xbmcgui': gui}):
            self.assertTrue(self.groups.choose_groups(self.portal,'live'))
        self.assertEqual(self.groups.load('p'),{'30','70','105'})
        self.assertEqual(state['opens'],1)

    def test_cancel_does_not_commit(self):
        self.groups.save('p',['5'])
        choices=iter([0,-1])
        class Dialog:
            def select(self,*a,**kw): return next(choices)
            def multiselect(self,*a,**kw): return None
            def notification(self,*a): pass
        gui=types.ModuleType('xbmcgui')
        gui.Dialog=Dialog
        with mock.patch.dict(sys.modules,{'xbmcgui':gui}):
            self.assertFalse(self.groups.choose_groups(self.portal))
        self.assertEqual(self.groups.load('p'),{'5'})

    def test_folder_setting_opens_kodi_native_browser(self):
        tree=ET.parse(LIB.parent/'settings.xml').getroot()
        node=next(n for n in tree.iter('setting') if n.get('id')=='recordings_folder')
        self.assertEqual(node.get('type'),'folder')
        self.assertEqual(node.get('option'),'writeable')

if __name__=='__main__':
    unittest.main()
