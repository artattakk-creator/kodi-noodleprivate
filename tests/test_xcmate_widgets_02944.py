"""Actual v2 query plans, shared approved Dynamic art and widget identities."""
import hashlib,importlib,json,sqlite3,time,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture

class Widgets44(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.w=importlib.import_module('widget_data41');self.art=importlib.import_module('widget_art44')
    def test_duplicate_titles_in_40_groups_still_fill_24_unique_tiles(self):
        for group in range(40):
            cid='g'+str(group)
            self.index.import_group('p','vod',cid,[dict(stream_id=str(i),category_id=cid,name='Title '+str(i),added=self.now+i) for i in range(30)])
        rows,code=self.w.snapshot(self.portal,'vod');self.assertEqual(code,'READY');self.assertEqual(len(rows),24);self.assertEqual(len({r['sid'] for r in rows}),24)
        self.assertEqual(rows[0]['sid'],'29')
    def test_real_v2_index_returns_24_without_union_view_sort_or_full_payload_scan(self):
        self.index.import_group('p','vod','a',[dict(stream_id=str(i),category_id='a',name='Film '+str(i),added=self.now+i) for i in range(20005)])
        reader=self.w.WidgetReader('p');original=reader._query;calls=[]
        def query(sql,args=(),kind=None):calls.append((sql,args,kind));return original(sql,args,kind)
        before=time.perf_counter()
        with mock.patch.object(reader,'_query',side_effect=query):rows=reader.small('vod',limit=24)
        elapsed=time.perf_counter()-before
        self.assertEqual(len(rows),24);self.assertEqual(rows[0]['sid'],'20004')
        thin=[q for q,a,k in calls if 'FROM items_v2 i INDEXED' in q][0]
        self.assertNotIn('payload',thin);self.assertNotIn('readable_titles',thin)
        db=sqlite3.connect(self.index.path());db.execute('CREATE TEMP TABLE selected_categories(cid TEXT PRIMARY KEY)');db.executemany('INSERT INTO selected_categories VALUES(?)',[('a',),('b',)])
        statement,args,_=next(v for v in calls if 'FROM items_v2 i INDEXED' in v[0])
        plan=' '.join(str(r) for r in db.execute('EXPLAIN QUERY PLAN '+statement,args));db.close()
        self.assertIn('recent_v2',plan);self.assertNotIn('TEMP B-TREE FOR ORDER BY',plan)
        self.assertLess(elapsed,.75);print('WIDGET44_V2_HOST',json.dumps(dict(records=20005,returned=len(rows),ms=round(elapsed*1000,3),plan=plan)))
    def test_undated_provider_uses_deterministic_local_order_without_fake_new_date(self):
        records=[dict(series_id='undated-'+str(i),category_id='undated',name='Series '+str(i)) for i in range(30)]
        self.index.import_group('p','series','undated',records)
        reader=self.w.WidgetReader('p');first=reader.small('series',category='undated');again=reader.small('series',category='undated')
        self.assertEqual(len(first),24);self.assertEqual([r['sid'] for r in first],[r['sid'] for r in again]);self.assertTrue(all(r['added_at'] is None for r in first))
    def test_shared_dynamic_reference_survives_new_interpreter_ram_without_image_archive(self):
        row=dict(kind='vod',sid='1',cover='https://images.example/poster.jpg');visible=importlib.import_module('artwork_visible')
        def approve(url):visible._dns_cache[('images.example',443)]=(time.monotonic()+30,True);return True
        with mock.patch('artwork_config.persistent',return_value=False),mock.patch.object(visible,'public_dns',side_effect=approve),mock.patch('media_art.cached',return_value=''):
            self.art.prepare('p',[row]);visible._values.clear()
            with mock.patch.object(visible,'public_dns',side_effect=AssertionError('DNS in presentation')),mock.patch.object(visible,'dynamic',side_effect=AssertionError('queue in presentation')):
                art=self.art.art(row,self.art.read('p'))
            self.assertTrue(art['poster'].startswith(row['cover']));self.assertEqual(art['poster'],art['thumb'])
        self.assertFalse((self.folder/'media_choices43').exists());self.assertFalse(list(self.folder.rglob('*.jpg')))
    def test_expired_or_changed_source_reference_cannot_bypass_dns_policy(self):
        url='https://images.example/p.jpg';key=hashlib.sha256(url.encode()).hexdigest();row=dict(kind='vod',sid='1',cover=url)
        from artwork_visible import KODI_OPTIONS
        with mock.patch('artwork_config.persistent',return_value=False),mock.patch('media_art.cached',return_value=''):
            for uri,until in [(url+KODI_OPTIONS,time.time()-1),(url+KODI_OPTIONS,time.time()+1000),('https://other.invalid'+KODI_OPTIONS,time.time()+20)]:
                art=self.art.art(row,{key:dict(uri=uri,until=until)});self.assertTrue(art['poster'].endswith('vod.png'))
    def test_metadata_limit_and_other_portal_cannot_supply_unrelated_art(self):
        path=Path(self.art.path('p'));path.write_text('x'*(self.art.MAX_BYTES+1));self.assertEqual(self.art.read('p'),{})
        path.write_text('{}');self.assertEqual(self.art.read('other'),{})
    def test_widget_click_targets_stay_exact_and_no_tile_focus_starts_playback(self):
        for action,kind in [('widget_live_start_group','live'),('widget_recent_vod','vod'),('widget_recent_series','series')]:
            self.added.clear();self.router._params['action']=action;self.routes.dispatch(self.router)
            for url,li,folder in self.added:
                if li.props.get('XCMate.WidgetKind41'):
                    self.assertEqual(li.props['XCMate.ClickTarget44'],url);self.assertIn('sid='+li.props['XCMate.MediaId'],url);self.assertFalse(folder)
            self.assertFalse(self.builtins)
    def test_authoritative_guide_revision_and_actual_progress_are_exposed_to_widget(self):
        guide=importlib.import_module('guide_store');guide.import_cache('p',{'xml':[dict(channel='xml',name='Real programme',start_timestamp=self.now-60,stop_timestamp=self.now+60)]},revision='verified-guide')
        self.router._params['action']='widget_live_start_group';self.routes.dispatch(self.router)
        items=[li for _,li,_ in self.added if li.props.get('XCMate.WidgetKind41')=='live']
        self.assertTrue(any(li.props.get('XtreamMate.Now')=='Real programme' for li in items))
        self.assertTrue(all(li.props.get('XtreamMate.Progress')!='' for li in items))
