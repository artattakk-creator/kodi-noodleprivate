"""Real SQLite regressions for sender/source-qualified ephemeral guide views."""
import importlib
import types
import unittest
from pathlib import Path
from unittest import mock
import test_xcmate_epg_binding_02948 as binding_tests


class SourceViews474(unittest.TestCase):
    def setUp(self):
        fixture=binding_tests.Binding48(methodName='runTest');fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        for name in ('portal','sources','binding','store','local','now','a','b','aid','bid','origin','client'):
            setattr(self,name,getattr(fixture,name))
        self.binding.save(self.portal,'1','xml',self.aid)
        self.binding.save(self.portal,'2','xml',self.bid)
        self.binding.save(self.portal,'3','xml',self.aid)
        self.mappings=self.sources.configuration('p')['mappings']
        self.rows=[dict(sid=str(i),name=name,epg_channel_id='xml',kind='live')
                   for i,name in enumerate(('Disney Channel','Das Erste','ZDF'),1)]

    def assert_sources(self,view,rows=None):
        resolve=importlib.import_module('epg_views').resolve_guide
        for row in rows or self.rows:
            expected='Source 2' if row['sid']=='2' else 'Source 1'
            info=resolve(view,'xml',row['sid'],self.now,mappings=self.mappings)
            self.assertEqual(info['now'],expected,row['name'])
            self.assertEqual(info['description'],'Exact description '+expected[-1])
            self.assertEqual(info['events'][0]['source_key46'],self.bid if row['sid']=='2' else self.aid)

    def test_collision_isolated_in_full_and_text_windows_in_either_sender_order(self):
        for text in (False,True):
            for rows in (self.rows,list(reversed(self.rows)),[self.rows[1],self.rows[0],self.rows[2]]):
                with self.subTest(text=text,order=[r['sid'] for r in rows]):
                    view=self.local.window('p',rows,self.mappings,self.now,self.now+7200,text_only65=text)
                    self.assert_sources(view,rows)

    def test_grid_resolves_exact_source_per_sender_and_keeps_shared_source(self):
        grid=importlib.import_module('guide_grid_data')
        for rows in (self.rows,list(reversed(self.rows))):
            reader=types.SimpleNamespace(page=lambda *a,**k:(rows,3),groups=lambda *a:[])
            with mock.patch('library_index.Reader',return_value=reader):
                result=grid.page(self.portal,0,self.origin,'a',mappings48=self.mappings)
            self.assertEqual([r['events'][0]['title'] for r in result['rows']],
                             ['Source 2' if r['sid']=='2' else 'Source 1' for r in rows])
            self.assertEqual(len({r['events'][0]['programme_key47'] for r in result['rows']}),3)

    def test_selected_programme_snapshot_does_not_read_other_senders_flat_cid(self):
        events=[dict(channel='xml',name='Source 2' if i==0 else 'Source 2 future '+str(i),descr='Exact description 2',
                     start_timestamp=self.now-60+i*600,stop_timestamp=self.now-60+(i+1)*600,_source_index=2)
                for i in range(61)]
        self.store.import_cache('p',{'xml':events},'selected-history',now=self.now,trusted_feed=True,source_records={2:self.b})
        channels=[types.SimpleNamespace(extra=dict(stream_id=r['sid'],category_id='a'),tvg_id='xml',logo='',name=r['name']) for r in self.rows]
        snapshot=importlib.import_module('tv_data').GuideSnapshot(self.portal,self.client)
        snapshot.request(channels);snapshot.request_programme('2');snapshot.refresh()
        for sid,title in (('1','Source 1'),('2','Source 2'),('3','Source 1')):
            self.assertEqual(snapshot.get(sid,self.now)['now'],title)
        self.assertEqual(snapshot.get('2',self.now)['programme_events'][0]['title'],'Source 2')
        self.assertEqual(len(snapshot.get('2',self.now)['programme_events']),61)

    def test_retained_facts_fallback_keeps_each_sender_source(self):
        fallback=importlib.import_module('programme_snapshot47').fallback_window
        for rows in (self.rows,list(reversed(self.rows))):
            self.assert_sources(fallback('p',rows,self.mappings,self.now,self.now+7200),rows)

    def test_empty_first_source_does_not_hide_another_senders_retained_facts(self):
        mappings=self.binding.preview(self.mappings,'1','xml','external:not-present')
        view=importlib.import_module('programme_snapshot47').fallback_window('p',self.rows,mappings,self.now,self.now+7200)
        self.assertIsNotNone(view)
        resolve=importlib.import_module('epg_views').resolve_guide
        self.assertFalse(resolve(view,'xml','1',self.now,mappings=mappings)['now'])
        self.assertEqual(resolve(view,'xml','2',self.now,mappings=mappings)['now'],'Source 2')

    def test_ram_lastgood_fallback_keeps_each_sender_source(self):
        handoff=importlib.import_module('epg_handoff63')
        resolve=importlib.import_module('epg_views').resolve_guide
        for row in self.rows:
            single=self.local.window('p',[row],self.mappings,self.now,self.now+7200)
            info=resolve(single,'xml',row['sid'],self.now,mappings=self.mappings)
            info['snapshot_revision']=single.revision;handoff.register('p',single.revision)
            handoff.remember('p',row,info,self.mappings)
        fallback=importlib.import_module('epg_fallback67').window
        for rows in (self.rows,list(reversed(self.rows))):
            self.assert_sources(fallback('p',rows,self.mappings,self.now,self.now+7200,48),rows)

    def test_empty_first_sender_window_does_not_hide_another_senders_ram_rows(self):
        handoff=importlib.import_module('epg_handoff63')
        resolve=importlib.import_module('epg_views').resolve_guide
        for row in self.rows:
            single=self.local.window('p',[row],self.mappings,self.now,self.now+7200)
            info=resolve(single,'xml',row['sid'],self.now,mappings=self.mappings)
            if row['sid']!='2':
                info['events']=[dict(info['events'][0],start=self.now+10000,stop=self.now+11000)]
            info['snapshot_revision']=single.revision;handoff.register('p',single.revision)
            handoff.remember('p',row,info,self.mappings)
        view=importlib.import_module('epg_fallback67').window('p',self.rows,self.mappings,self.now,self.now+7200,48)
        self.assertIsNotNone(view)
        self.assertFalse(resolve(view,'xml','1',self.now,mappings=self.mappings)['now'])
        self.assertEqual(resolve(view,'xml','2',self.now,mappings=self.mappings)['now'],'Source 2')

    def test_legacy_plain_dict_and_single_sender_lookup_remain_compatible(self):
        raw={'xml':[dict(name='Legacy',start_timestamp=self.now-60,stop_timestamp=self.now+60)]}
        self.assertIs(self.local.for_channel(raw,'2'),raw)
        single=self.local.window('p',[self.rows[1]],self.mappings,self.now,self.now+7200)
        self.assertEqual(single['xml'][0]['name'],'Source 2')
        self.assertFalse(self.local.for_channel(single,'missing'))

    def test_reimport_and_source_reorder_reload_preserve_saved_source_identity(self):
        before=Path(self.sources._file_path()).read_bytes()
        event=dict(channel='xml',name='Source 2',descr='Exact description 2',start_timestamp=self.now-60,stop_timestamp=self.now+600,_source_index=1)
        self.store.import_cache('p',{'xml':[event]},'reimport',now=self.now,trusted_feed=True,source_records={1:self.b})
        config=self.sources.configuration('p');config['sources'].reverse();self.sources._save('p',config)
        self.sources=importlib.reload(self.sources);self.mappings=self.sources.configuration('p')['mappings']
        self.assertEqual(self.binding.binding(self.mappings,'1')['source'],self.aid)
        self.assertEqual(self.binding.binding(self.mappings,'2')['source'],self.bid)
        self.assert_sources(self.local.window('p',self.rows,self.mappings,self.now,self.now+7200))
        self.assertNotEqual(Path(self.sources._file_path()).read_bytes(),before)

    def test_automatic_provider_cannot_reuse_another_senders_manual_source(self):
        mappings=self.binding.preview({},'1','xml',self.aid)
        resolve=importlib.import_module('epg_views').resolve_guide
        for text in (False,True):
            view=self.local.window('p',self.rows,mappings,self.now,self.now+7200,text_only65=text)
            self.assertEqual(resolve(view,'xml','1',self.now,mappings=mappings)['now'],'Source 1')
            self.assertEqual(resolve(view,'xml','2',self.now,mappings=mappings)['now'],'Provider programme')

    def test_missing_agent_binding_keeps_provider_visible_in_guide_and_now_next(self):
        self.binding.save(self.portal,'1','missing-agent','agent')
        mappings=self.sources.configuration('p')['mappings']
        resolve=importlib.import_module('epg_views').resolve_guide
        grid=importlib.import_module('guide_grid_data')
        reader=types.SimpleNamespace(page=lambda *a,**k:(self.rows,3),groups=lambda *a:[])
        for enabled in (True,False):
            with self.subTest(enabled=enabled), mock.patch('epg_agent100.enabled',return_value=enabled):
                view=self.local.window('p',self.rows,mappings,self.now,self.now+7200,text_only65=True)
                self.assertEqual(resolve(view,'xml','1',self.now,mappings=mappings)['now'],'Provider programme')
                with mock.patch('library_index.Reader',return_value=reader):
                    result=grid.page(self.portal,0,self.origin,'a')
                self.assertEqual(result['rows'][0]['events'][0]['title'],'Provider programme')
                self.assertEqual(result['rows'][0]['events'][0].get('source_key46','provider'),'provider')
        self.assertEqual(self.binding.binding(self.sources.configuration('p')['mappings'],'1'),
                         dict(channel='missing-agent',source='agent'))

    def test_saving_cold_preview_does_not_replace_newer_exact_source_slot(self):
        from epg_candidate53 import publish
        from programme_index46 import window

        args=('p','xml',self.now-60,self.now+600)
        before=window(*args,source48=self.aid)
        self.assertTrue(before)
        stale=dict(before[0],name='Stale preview title',title='Stale preview title')
        publish(self.portal,self.aid,'xml','Fixture',[stale])
        after=window(*args,source48=self.aid)
        self.assertEqual(after[0]['name'],before[0]['name'])

    def test_grid_empty_qualified_mapping_keeps_explicit_channel_identity(self):
        mappings=self.binding.preview(self.mappings,'2','empty-channel',self.bid)
        reader=types.SimpleNamespace(page=lambda *a,**k:(self.rows,3),groups=lambda *a:[])
        with mock.patch('library_index.Reader',return_value=reader):
            value=importlib.import_module('guide_grid_data').page(self.portal,0,self.origin,'a',mappings48=mappings)
        row=value['rows'][1]
        self.assertEqual(row['events'],[])
        self.assertEqual(row['mapping'],'MANUAL')
        self.assertEqual(row['epg_id'],'empty-channel')
