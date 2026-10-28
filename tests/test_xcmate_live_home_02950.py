"""Strict local start group with 88+ stations and original player click URLs."""
import importlib,sys,unittest
from unittest import mock
from xcmate050_fixture import Fixture50

class LiveHome50(Fixture50,unittest.TestCase):
    def setUp(self):
        super().setUp();self.home=importlib.import_module('widget_home50')
        self.a=[dict(stream_id='a'+str(i),category_id='a',name='Station '+str(i),epg_channel_id='xml'+str(i)) for i in range(88)]
        self.b=[dict(stream_id='b'+str(i),category_id='b',name='Other '+str(i)) for i in range(5)]
        self.index.import_group('p','live','a',self.a);self.index.import_group('p','live','b',self.b)
        self.portal.update(start_group_id='a',start_stream_id='b0')
    def test_explicit_start_group_wins_over_start_channel_in_another_group_and_all_88_are_returned(self):
        rows,code=self.home.rows(self.portal);self.assertEqual(code,'READY');self.assertEqual(len(rows),88)
        self.assertEqual({r['sid'] for r in rows},{'a'+str(i) for i in range(88)})
        self.assertTrue(all(r['category_id']=='a' for r in rows))
    def test_missing_or_unavailable_start_group_never_falls_back_to_all_enabled_groups(self):
        for cid in ('','deleted'):
            portal=dict(self.portal,start_group_id=cid);rows,code=self.home.rows(portal)
            self.assertFalse(rows);self.assertIn(code,('START_GROUP_MISSING','START_GROUP_UNAVAILABLE'))
    def test_home_route_has_no_group_folders_and_exactly_one_proven_player_target_per_station(self):
        self.router._params.update(action='widget_live_start_group',home50='1');self.routes.dispatch(self.router)
        self.assertEqual(len(self.added),88);self.assertEqual(len(self.ends),1)
        for url,item,folder in self.added:
            self.assertFalse(folder);self.assertEqual(item.getProperty('IsPlayable'),'true');self.assertEqual(item.getProperty('XCMate.Home50'),'true')
            self.assertIn('action=play_live',url);self.assertIn('pid=p',url);self.assertIn('sid=a',url)
        self.assertFalse(self.builtins);sys.modules['utils'].http_get.assert_not_called()
    def test_empty_source_has_no_placeholder_group_rows_or_forced_provider_fetch(self):
        self.portal['start_group_id']='missing';self.router._params.update(action='widget_live_start_group',home50='1');self.routes.dispatch(self.router)
        self.assertFalse(self.added);self.assertEqual(len(self.ends),1);self.assertFalse(self.builtins)
    def test_native_fast_entry_and_full_router_use_same_strict_source(self):
        from home_entry import HomeRouter
        from widget_entry46 import dispatch
        router=HomeRouter(['plugin://plugin.video.xtreammate/','31','?action=widget_live_start_group&pid=p&home50=1'])
        self.assertTrue(dispatch(router));self.assertEqual(len(self.added),88);self.assertTrue(all(item.getProperty('XCMate.Home50')=='true' for _,item,_ in self.added))
    def test_shared_now_next_event_and_honest_programme_placeholder_are_reused_without_network(self):
        import guide_store
        guide_store.import_cache('p',{'xml87':[dict(name='Programme 87',descr='Actual local description',channel='xml87',start_timestamp=self.now-60,stop_timestamp=self.now+600)]})
        values,code=self.home.values(self.portal);value=next(v for v in values if v['props']['XCMate.MediaId']=='a87')
        self.assertEqual(value['props']['XCMate.ProgrammeTitle46'],'Programme 87')
        self.assertIn('Actual local description',value['props']['XCMate.ProgrammeDescription46'])
        self.assertTrue(value['props']['XCMate.ProgrammeKey46']);self.assertTrue(value['props']['XCMate.ProgrammeImage46'])
        self.assertNotEqual(value['props']['XCMate.ProgrammeImage46'],value['props']['XCMate.ProgrammeLogo46'])
        self.assertFalse(self.builtins);sys.modules['utils'].http_get.assert_not_called()
