"""Actual SQLite source collision, no-write preview and remote discoverability."""
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import types
import unittest
from unittest import mock
from xcmate027_fixture import Fixture,ADDON,LIB,QueuedPool

class Binding48(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        spec=importlib.util.spec_from_file_location('epg_sources',LIB/'epg_sources.py');self.sources=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.sources)
        patch=mock.patch.dict(sys.modules,epg_sources=self.sources);patch.start();self.addCleanup(patch.stop)
        patch=mock.patch.object(sys.modules['epg_status'],'changed',mock.Mock(),create=True);patch.start();self.addCleanup(patch.stop)
        self.a=dict(id='feed-a',name='First XMLTV',enabled=True);self.b=dict(id='feed-b',name='Second XMLTV',enabled=True)
        self.sources._write_all({'p':dict(sources=[self.a,self.b],mappings={'2':'xml'})})
        self.binding=importlib.import_module('epg_binding48');self.store=importlib.import_module('guide_store')
        self.local=importlib.import_module('local_epg');self.origin=self.now-120
        current=dict(channel='xml',name='Provider programme',descr='Provider exact',start_timestamp=self.now-60,stop_timestamp=self.now+600,_source_index=0)
        self.store.import_cache('p',{'xml':[current]},'provider',now=self.now,trusted_feed=True)
        for rank,source in enumerate((self.a,self.b),1):
            event=dict(current,name='Source '+str(rank),descr='Exact description '+str(rank),_source_index=rank,screenshot_uri='https://image.invalid/source'+str(rank)+'.png',cast=['Actual actor'],director=['Actual director'])
            self.store.import_cache('p',{'xml':[event]},'external'+str(rank),now=self.now,trusted_feed=True,source_records={rank:source})
        from guide_publish44 import source_id
        self.aid=source_id(self.a,1);self.bid=source_id(self.b,2)
    def row(self):return dict(sid='1',name='Station',epg_channel_id='xml',kind='live')
    def test_equal_channel_ids_remain_unambiguously_bound_to_different_sources(self):
        mappings=self.sources.configuration('p')['mappings']
        for sid,title in ((self.aid,'Source 1'),(self.bid,'Source 2')):
            preview=self.binding.preview(mappings,'1','xml',sid)
            info=self.local.now_next('p',[self.row()],preview,self.now)['1']
            self.assertEqual(info['now'],title);self.assertEqual(info['description'],'Exact description '+title[-1])
            event=importlib.import_module('programme_events46').from_info(self.portal,self.row(),info)
            self.assertIn('source'+title[-1]+'.png',event['xmltv_image']);self.assertEqual(event['cast'],['Actual actor'])
    def test_preview_preserves_json_guide_and_existing_mapping_bytes(self):
        filename=Path(self.sources._file_path());before=filename.read_bytes();guide=Path(self.store.path()).read_bytes()
        config=self.sources.configuration('p');preview=self.binding.preview(config['mappings'],'1','xml',self.bid)
        self.local.now_next('p',[self.row()],preview,self.now)
        self.assertEqual(filename.read_bytes(),before);self.assertEqual(Path(self.store.path()).read_bytes(),guide)
        self.assertEqual(self.sources.configuration('p')['mappings'],{'2':'xml'})
    def test_explicit_save_changes_only_selected_sender_and_keeps_source_priority(self):
        original=self.sources.configuration('p');self.assertTrue(self.binding.save(self.portal,'1','xml',self.bid))
        config=self.sources.configuration('p');self.assertEqual(config['sources'],original['sources']);self.assertEqual(config['mappings']['2'],'xml')
        self.assertEqual(config['mappings']['1'],'xml');self.assertEqual(self.binding.binding(config['mappings'],'1')['source'],self.bid)
        self.assertEqual(self.local.now_next('p',[self.row()],config['mappings'],self.now)['1']['now'],'Source 2')
    def test_legacy_set_mapping_clears_only_that_senders_source_binding(self):
        self.binding.save(self.portal,'1','xml',self.bid);self.sources.set_mapping('p','1','other')
        config=self.sources.configuration('p');self.assertIsNone(self.binding.binding(config['mappings'],'1'));self.assertEqual(config['mappings']['2'],'xml')
    def test_disabled_or_foreign_source_cannot_be_saved(self):
        before=Path(self.sources._file_path()).read_bytes()
        with self.assertRaises(ValueError):self.binding.save(self.portal,'1','xml','foreign')
        self.assertEqual(Path(self.sources._file_path()).read_bytes(),before)
    def test_missing_selected_source_does_not_silently_show_provider(self):
        config=self.binding.preview({},'1','xml','external:not-present')
        self.assertFalse(self.local.now_next('p',[self.row()],config,self.now)['1']['now'])
    def test_locally_available_source_channel_ids_are_searchable_without_http(self):
        rows=self.binding.channels('p',self.bid,'xm');self.assertEqual([r['id'] for r in rows],['xml'])
        sys.modules['utils'].http_get.assert_not_called()
    def test_source_channel_display_names_are_committed_only_with_source_generation(self):
        self.assertTrue(self.binding.stage_channels('p','good',self.aid,[('id-1','Das Erste')]))
        self.assertFalse(self.binding.named_channels('p',self.aid,'Erste'))
        self.binding.finish_channels('p','good',True)
        self.assertEqual(self.binding.named_channels('p',self.aid,'Erste')[0]['id'],'id-1')
        self.binding.stage_channels('p','bad',self.aid,[('id-2','Cancelled channel')]);self.binding.finish_channels('p','bad',False)
        self.assertFalse(self.binding.named_channels('p',self.aid,'Cancelled'))
    def window(self):
        module=importlib.import_module('guide_grid_window')
        with mock.patch.object(module,'ThreadPoolExecutor',QueuedPool):
            w=module.GuideGridWindow('XCMateGuideGrid.xml',str(ADDON),'Default','720p');w.configure(self.router,self.portal)
        w.show();self.addCleanup(w.close);self.settle(w);return w
    def test_empty_programme_sender_has_visible_mapping_button_and_context_action(self):
        w=self.window();w.rows[0]['events']=[];w._render()
        self.assertTrue(w.getControl(316).visible);self.assertEqual(w.getControl(316).label,'EPG zuweisen')
        w.onClick(316);self.assertTrue(w._mapping_request48)
        self.dialog.select.return_value=4;w._mapping_request48=False;w.onAction(types.SimpleNamespace(getId=lambda:117))
        self.assertTrue(w._mapping_request48)
    def test_visible_header_button_is_reachable_with_normal_remote_arrows_and_ok(self):
        w=self.window();w._focus_zone='header';w.setFocusId(315);w.native(2)
        self.assertEqual(w.getFocusId(),316);w.native(7)
        self.assertTrue(w._mapping_request48);self.assertFalse(self.builtins)
    def test_preview_uses_real_grid_and_cancel_restores_exact_snapshot(self):
        w=self.window();original=list(w.rows);before=Path(self.sources._file_path()).read_bytes()
        module=importlib.import_module('guide_mapping48');dialog=module.MappingWindow48('XCMateMapping48.xml',str(ADDON),'Default','720p')
        dialog.configure(w);dialog.onInit();dialog.source={'id':self.bid,'name':'Second XMLTV'};dialog.candidate={'id':'xml'}
        def synchronous(fn,apply):apply(fn())
        with mock.patch.object(dialog,'_submit',side_effect=synchronous):dialog._preview()
        self.assertEqual(w.rows[0]['events'][0]['title'],'Source 2');self.assertTrue(dialog.previewed)
        # run's finally is the real cancellation restoration, including focus.
        with mock.patch.object(dialog,'show',side_effect=dialog.close):dialog.run()
        self.assertEqual(w.rows,original);self.assertEqual(Path(self.sources._file_path()).read_bytes(),before)
    def test_saved_binding_is_identical_in_grid_widget_and_mini_snapshot(self):
        self.binding.save(self.portal,'1','xml',self.bid);mappings=self.sources.configuration('p')['mappings']
        info=self.local.now_next('p',[self.row()],mappings,self.now)['1'];event=importlib.import_module('programme_events46').from_info(self.portal,self.row(),info)
        grid=importlib.import_module('guide_grid_data').page(self.portal,0,self.origin,'a')
        widget=importlib.import_module('widget_items45').describe(self.portal,'live',self.row(),{},info)
        self.assertEqual(grid['rows'][0]['events'][0]['title'],'Source 2')
        self.assertEqual({grid['rows'][0]['events'][0]['programme_key47'],widget['props']['XCMate.ProgrammeKey47'],info['programme_key47']},{event['key']})

    def test_visible_mapping_button_does_not_cover_time_axis_or_first_grid_row(self):
        import xml.etree.ElementTree as E
        tree=E.parse(ADDON/'resources/skins/Default/720p/XCMateGuideGrid.xml')
        def rectangle(cid):
            node=tree.find("controls/control[@id='%s']"%cid)
            return tuple(int(node.findtext(k)) for k in ('left','top','width','height'))
        x,y,w,h=rectangle(316)
        for cid in range(600,606):
            a,b,c,d=rectangle(cid)
            self.assertFalse(x<a+c and x+w>a and y<b+d and y+h>b,cid)
        self.assertLessEqual(y+h,168)

    def test_mini_does_not_use_an_unqualified_legacy_cache_when_selected_source_is_missing(self):
        self.binding.save(self.portal,'1','xml',self.bid)
        self.cache={'xml':[dict(channel='xml',name='WRONG PROVIDER',descr='Unqualified',start_timestamp=self.now-60,stop_timestamp=self.now+600)]}
        sys.modules['epg'].load_cache=lambda pid:self.cache
        channel=types.SimpleNamespace(extra={'stream_id':'1','category_id':'a'},tvg_id='xml',logo='',name='Station')
        snapshot=importlib.import_module('tv_data').GuideSnapshot(self.portal,self.client);snapshot.request([channel])
        with mock.patch('guide_viewport.cache',return_value=None):snapshot.refresh()
        self.assertFalse(snapshot.get('1',self.now)['now'])
        self.assertEqual(snapshot.get('1',self.now)['mapping'],'MANUAL')

    def test_common_resolver_requires_source_proof_even_for_non_mini_callers(self):
        from epg_views import resolve_guide
        mappings=self.binding.preview({},'1','xml',self.bid)
        raw=dict(channel='xml',name='Candidate',descr='Text',start_timestamp=self.now-60,stop_timestamp=self.now+600)
        for source in (None,self.aid,self.bid):
            row=dict(raw)
            if source:row['source_key46']=source
            result=resolve_guide({'xml':[row]},'xml','1',self.now,mappings=mappings)
            self.assertEqual(bool(result['now']),source==self.bid)
    def test_prepared_startup_snapshot_is_invalidated_on_mapping_change(self):
        import startup_preload
        filename=Path(startup_preload.path('p'))
        filename.write_text(json.dumps(dict(at=time.time(),schema48=1,mapping48=startup_preload.mapping_stamp48(),rows=[dict(sid='1',name='Before',guide={'now':'Before','events':[dict(name='Before',title='Before',start=self.now-60,stop=self.now+600)]})])))
        self.assertEqual(startup_preload.read('p','1')['guide']['now'],'Before')
        self.binding.save(self.portal,'1','xml',self.bid)
        self.assertEqual(startup_preload.read('p','1'),{})

    def test_prepared_start_data_rolls_now_next_forward_in_ram_without_stale_title(self):
        import startup_preload
        filename=Path(startup_preload.path('p'))
        filename.write_text(json.dumps(dict(at=time.time()-120,schema48=1,mapping48=startup_preload.mapping_stamp48(),rows=[dict(sid='1',guide=dict(now='Ended',events=[dict(title='Ended',start=self.now-120,stop=self.now-30),dict(title='Current',start=self.now-30,stop=self.now+600)]))])))
        result=startup_preload.read('p','1')
        self.assertEqual(result['guide']['now'],'Current')
        self.assertTrue(result['guide']['programme_key47'])
    def test_preparation_does_not_publish_old_data_with_a_new_mapping_stamp(self):
        import startup_preload,epg_views
        startup_preload._next.clear();original=epg_views.resolve_guide;changed=[]
        def interleaved(*args,**kwargs):
            if not changed:self.binding.save(self.portal,'1','xml',self.bid);changed.append(True)
            return original(*args,**kwargs)
        with mock.patch.object(epg_views,'resolve_guide',side_effect=interleaved),mock.patch.object(epg_views,'_start_short_guides'):
            startup_preload.prepare()
        self.assertTrue(changed);self.assertFalse(Path(startup_preload.path('p')).exists())
