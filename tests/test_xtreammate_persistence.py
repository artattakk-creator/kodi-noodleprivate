import importlib.util
import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent / 'src/plugin.video.xtreammate'
LIB = ROOT / 'resources/lib'


def import_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class XtreamMateV011Tests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        stubutils = types.ModuleType('utils')
        stubutils.addon_data_dir = lambda: self.folder.name
        stubutils.error = stubutils.info = stubutils.debug = stubutils.warn = lambda *args, **kwargs: None
        self.patch_utils = mock.patch.dict(sys.modules, {'utils': stubutils,
                'xbmcvfs': types.SimpleNamespace(exists=os.path.exists)})
        self.patch_utils.start()
        self.addCleanup(self.patch_utils.stop)
        self.portals = import_file('xm_test_portals', LIB/'portals.py')
        self.groups = import_file('xm_test_groups', LIB/'group_selection.py')
        self.portals._DB_FILE = None

    def test_verified_portal_save_and_read(self):
        data = {'type':'xtream', 'name':'Deutsch TV', 'xc_host':'https://example.test',
                'xc_user':'user', 'xc_pass':'secret'}
        p = self.portals.add(data)
        self.assertEqual(self.portals.get_by_id(p['id'])['name'], 'Deutsch TV')
        self.assertEqual(len(self.portals.get_active()), 1)
        self.assertTrue(os.path.exists(os.path.join(self.folder.name, 'portals.json')))

    def test_fail_closed_if_write_fails(self):
        with mock.patch.object(self.portals.os, 'replace', side_effect=PermissionError('disk')):
            with self.assertRaises(OSError):
                self.portals.add({'name':'New','type':'xtream'})
        self.assertEqual(self.portals.load_all(), [])

    def test_corrupt_existing_portal_db_is_not_overwritten(self):
        path = os.path.join(self.folder.name, 'portals.json')
        Path(path).write_text('{bad json', encoding='utf-8')
        with self.assertRaises(RuntimeError):
            self.portals.add({'name':'New','type':'xtream'})
        self.assertEqual(Path(path).read_text(encoding='utf-8'), '{bad json')

    def test_legacy_live_selection_is_preserved(self):
        Path(self.groups._path()).write_text(json.dumps({'portal-1':['10']}),encoding='utf-8')
        self.assertEqual(self.groups.load('portal-1', 'live'), {'10'})
        self.assertIsNone(self.groups.load('portal-1', 'vod'))
        self.groups.save('portal-1', ['21'], 'vod', known=['21','22'])
        self.assertEqual(self.groups.load('portal-1', 'live'), {'10'})
        self.assertEqual(self.groups.load('portal-1', 'vod'), {'21'})

    def test_manual_bulk_ops_and_save(self):
        dialog = types.SimpleNamespace(selections=[2,0], messages=[])
        def select(title, rows, **kwargs):
            dialog.messages.append(rows)
            return dialog.selections.pop(0)
        dialog.select=select
        dialog.multiselect=lambda title, rows, preselect=None: [1]
        dialog.notification=lambda *args,**kw:None
        dialog.ok=lambda *args,**kw:None
        xtream = types.ModuleType('xtream')
        class XC:
            def __init__(self,*args):pass
            def get_live_categories(self,force_refresh=False):
                return [{'category_id':'10','category_name':'DE All'},
                        {'category_id':'11','category_name':'DE Other'}]
        xtream.XtreamClient=XC
        gui = types.ModuleType('xbmcgui')
        gui.Dialog=lambda:dialog
        from menu45_fixture import install
        install(gui)
        with mock.patch.dict(sys.modules,{'xbmcgui':gui,'xtream':xtream}):
            result=self.groups.choose_groups({'id':'p','type':'xtream', 'xc_host':'h', 'xc_user':'u','xc_pass':'pw'})
        self.assertTrue(result)
        # 2 -> all disabled, checkbox dialog checks the second category and saves.
        self.assertEqual(self.groups.load('p','live'),{'11'})
        self.assertTrue(any('Alle deaktivieren' in row.getLabel() for row in dialog.messages[0]))
        self.assertEqual(len(dialog.messages),2)

    def test_new_groups_opt_in_and_disabled_stay_disabled(self):
        self.groups.save('p',['10'],'live',known=['10','11'],auto_new=True)
        allcats=[{'category_id':cid} for cid in ['10','11','12']]
        self.assertEqual(self.groups.enabled_ids('p','live',allcats),{'10','12'})
        self.assertEqual(self.groups.load('p','live'), {'10'})
        self.groups.save('p',['10'],'live',known=['10','11','12'],auto_new=False)
        self.assertEqual(self.groups.enabled_ids('p','live',allcats),{'10'})

    def test_separate_vod_and_series_category_filters(self):
        self.groups.save('p',['1'],'vod',known=['1','2'])
        self.groups.save('p',['9'],'series',known=['9','10'])
        vals=[{'category_id':'1','name':'One'},{'category_id':'2','name':'Two'}]
        self.assertEqual([x['name'] for x in self.groups.filter_entries(vals,'p','vod')],['One'])
        self.assertEqual(self.groups.enabled_ids('p','series',[{'category_id':'9'},{'category_id':'10'}]),{'9'})

    def test_cancel_does_not_change_saved_selection(self):
        self.groups.save('p',['1'],'live',known=['1','2'])
        dlg=types.SimpleNamespace(select=lambda *_:-1,ok=lambda *_:None)
        gui=types.ModuleType('xbmcgui');gui.Dialog=lambda:dlg
        from menu45_fixture import install
        install(gui)
        xtream=types.ModuleType('xtream')
        class XC:
            def __init__(self,*args):pass
            def get_live_categories(self,force_refresh=False):
                return [{'category_id':'1','category_name':'A'}, {'category_id':'2','category_name':'B'}]
        xtream.XtreamClient=XC
        with mock.patch.dict(sys.modules,{'xbmcgui':gui,'xtream':xtream}):
            self.assertFalse(self.groups.choose_groups({'id':'p','type':'xtream','xc_host':'h','xc_user':'u','xc_pass':'pw'}))
        self.assertEqual(self.groups.load('p'), {'1'})

if __name__=='__main__':
    unittest.main(verbosity=2)
