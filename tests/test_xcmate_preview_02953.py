"""Real original guide under an open narrow dialog; no preview persistence."""
import importlib,json,sys,types,unittest
from pathlib import Path
from unittest import mock
import test_xcmate_epg_binding_02948 as old
from xcmate027_fixture import ADDON


class Preview53(unittest.TestCase):
    def setUp(self):
        self.m=old.Binding48(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.w=self.m.window();module=importlib.import_module('guide_mapping48')
        self.d=module.MappingWindow48('XCMateMapping48.xml',str(ADDON),'Default','720p');self.d.configure(self.w);self.d.onInit();self.addCleanup(self.d.close)
        self.d.rows=[dict(id='xml',name='Station')];self.d.source=dict(id=self.m.bid,name='Second XMLTV');self.d.candidate=self.d.rows[0]
        p=mock.patch.object(self.d,'_submit',side_effect=lambda load,ready:ready(load()));p.start();self.addCleanup(p.stop)
    def test_short_ok_on_sender_uses_existing_context_mapping_action_without_playback(self):
        self.m.dialog.select.return_value=4;self.w._focus_zone='sender';self.w.setFocusId(730)
        self.w.native(7);self.assertTrue(self.w._mapping_request48);self.assertIsNone(self.w._play_request)
    def test_panel_stays_open_visible_and_original_grid_focus_unchanged(self):
        before=self.w.getFocusId();self.d._preview()
        self.assertTrue(self.d.getControl(900).visible);self.assertFalse(self.d._closed)
        self.assertEqual(self.w.rows[0]['events'][0]['title'],'Source 2');self.assertEqual(self.w.getFocusId(),before)
        self.assertEqual(self.d.getFocusId(),200);self.assertTrue(self.d.getControl(405).enabled)
        self.assertIn('Exact description 2',self.d.getControl(301).text)
        self.assertLessEqual(self.d.getControl(900).width,500)
    def test_multiple_sources_compare_without_json_or_guide_write(self):
        before=Path(self.m.sources._file_path()).read_bytes();guide=Path(self.m.store.path()).read_bytes()
        self.d._preview();self.d.source=dict(id=self.m.aid,name='First');self.d._preview()
        self.assertEqual(self.w.rows[0]['events'][0]['title'],'Source 1')
        self.assertEqual(Path(self.m.sources._file_path()).read_bytes(),before);self.assertEqual(Path(self.m.store.path()).read_bytes(),guide)
        self.assertIsNone(self.w._play_request)
    def test_cancel_restores_full_original_position_blocks_and_mapping(self):
        original={k:getattr(self.w,k) for k in self.d.original};focus=self.w.getFocusId();raw=Path(self.m.sources._file_path()).read_bytes()
        self.d._preview()
        with mock.patch.object(self.d,'show',side_effect=self.d.close):self.d.run()
        for key,value in original.items():self.assertEqual(getattr(self.w,key),value,key)
        self.assertEqual(self.w.getFocusId(),focus);self.assertEqual(Path(self.m.sources._file_path()).read_bytes(),raw)
    def test_save_is_linearized_before_close_and_changes_only_one_source_binding(self):
        self.d._preview();self.d.onClick(405)
        self.assertTrue(self.d.saved);self.assertTrue(self.d._closed)
        config=self.m.sources.configuration('p');self.assertEqual(config['mappings']['2'],'xml')
        self.assertEqual(config['source_mappings48']['1'],dict(channel='xml',source=self.m.bid))
    def test_search_pagination_previous_and_more_than_one_thousand_channels(self):
        rows=[('id'+str(n),'Name '+str(n)) for n in range(1101)]
        self.m.binding.stage_channels('p','many',self.m.bid,rows);self.m.binding.finish_channels('p','many',True)
        self.d.offset=1000;self.d._channels();self.assertTrue(any(r['id']=='id998' for r in self.d.rows))
        self.d.onClick(403);self.assertEqual(self.d.offset,1100);self.assertTrue(any(r['id']=='id999' for r in self.d.rows))
        self.d.onClick(407);self.assertEqual(self.d.offset,1000)
        self.d.query='Name 1100';self.d.offset=0;self.d._channels();self.assertEqual([r['id'] for r in self.d.rows],['id1100'])
    def test_closed_preview_never_applies_a_late_worker_result(self):
        from concurrent.futures import Future
        self.d.close();f=Future();f.set_result('late');self.d.future=f;self.d.apply=mock.Mock();self.d.pump();self.d.apply.assert_not_called()
