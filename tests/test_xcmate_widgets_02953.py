"""Existing .50 Home renderer consumes .53 bindings; no actual skin changes."""
import hashlib,importlib,json,sys,unittest
from pathlib import Path
import test_xcmate_epg_binding_02948 as old


class Widgets53(unittest.TestCase):
    def setUp(self):
        self.m=old.Binding48(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        channels=[dict(stream_id=str(i),name='Station '+str(i),category_id='a',epg_channel_id='xml') for i in range(1,89)]
        self.m.index.import_group('p','live','a',channels)
        self.m.index.import_group('p','live','b',[dict(stream_id='999',name='Other group',category_id='b',epg_channel_id='xml')])
        self.m.portal.update(start_group_id='a',start_stream_id='999')
    def test_existing_home_source_keeps_all_88_start_group_senders_and_no_group_fallback(self):
        home=importlib.import_module('widget_home50');rows,code=home.rows(self.m.portal)
        self.assertEqual(code,'READY');self.assertEqual(len(rows),88)
        self.assertEqual({r['category_id'] for r in rows},{'a'});self.assertNotIn('999',{r['sid'] for r in rows})
        self.m.router._params.update(action='widget_live_start_group',home50='1');self.m.routes.dispatch(self.m.router)
        self.assertEqual(len(self.m.added),88);self.assertTrue(all(not folder for _,_,folder in self.m.added))
        self.assertFalse(self.m.builtins)
    def test_saved_source_change_is_identical_in_home_grid_mini_and_infobar_model(self):
        home=importlib.import_module('widget_home50');local=importlib.import_module('local_epg')
        self.m.binding.save(self.m.portal,'1','xml',self.m.aid)
        before,code=home.values(self.m.portal);one=next(i for i in before if i['props']['XCMate.MediaId']=='1')
        self.m.binding.save(self.m.portal,'1','xml',self.m.bid)
        after,code=home.values(self.m.portal);two=next(i for i in after if i['props']['XCMate.MediaId']=='1')
        info=local.now_next('p',[self.m.row()],self.m.sources.configuration('p')['mappings'],self.m.now)['1']
        grid=importlib.import_module('guide_grid_data').page(self.m.portal,0,self.m.origin,'a')
        self.assertEqual(info['now'],'Source 2');self.assertEqual(grid['rows'][0]['events'][0]['title'],'Source 2')
        self.assertNotEqual(one['props']['XCMate.ProgrammeTitle46'],two['props']['XCMate.ProgrammeTitle46'])
        self.assertEqual(two['props']['XCMate.ProgrammeTitle46'],'Source 2')
        self.assertEqual(two['props']['XCMate.ProgrammeKey47'],info['programme_key47'])
        self.assertFalse(self.m.builtins)
    def test_three_existing_direct_widget_actions_are_preserved(self):
        self.m.router._params.update(action='widget_setup');self.m.routes.dispatch(self.m.router)
        self.assertEqual([item.label for _,item,_ in self.m.added],['Live-TV','Filme','Serien'])
        self.assertTrue(all('action=widget_link50' in url for url,_,_ in self.m.added))
    def test_skin_writers_reload_bridge_and_52_pixel_implementation_are_byte_identical(self):
        root=Path(__file__).resolve().parents[1];baseline=json.loads((root/'tests/fixtures/xcmate_02953_protection.json').read_text())['source_sha256']
        protected={'widget_skin50.py','widget_binding50.py','widget_manager50.py','widget_home50.py','widget_refresh45.py','infobar45.py','stream_details.py','live_stop42.py','playback_exit.py'}
        found=set()
        for file,sha in baseline.items():
            if Path(file).name in protected:
                self.assertEqual(hashlib.sha256((root/file).read_bytes()).hexdigest(),sha,file);found.add(Path(file).name)
        self.assertEqual(found,protected)
