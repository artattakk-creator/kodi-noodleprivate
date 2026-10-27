"""#240/#241 real index/LastGood/full-group tests, not Android performance claims."""
import importlib,json,sqlite3,sys,time,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,ADDON


class WidgetMaster46(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.w=importlib.import_module('widget_data41');self.group=importlib.import_module('widget_group46')
 def records(self,n=137):return [dict(stream_id=str(i),category_id='a',name='Station '+str(i),epg_channel_id='xml'+str(i)) for i in range(n)]
 def large(self,n=137):
  self.index.import_group('p','live','a',self.records(n));self.portal.update(start_group_id='a',start_stream_id=str(n-1))
 def test_complete_live_group_pins_start_once_and_includes_final_sender(self):
  self.large();pages=list(self.group.pages(self.portal));rows=[r for page in pages for r in page]
  self.assertEqual(len(rows),137);self.assertEqual(rows[0]['sid'],'136');self.assertEqual(len({r['sid'] for r in rows}),137)
  self.assertTrue(all(len(page)<=self.group.PAGE+1 for page in pages));self.assertEqual(rows[-1]['sid'],'135')
 def test_real_existing_widget_url_renders_all_137_correct_click_targets(self):
  self.large();self.router._params['action']='widget_live_start_group';self.routes.dispatch(self.router)
  items=[(u,li) for u,li,_ in self.added if li.props.get('XCMate.WidgetKind41')=='live']
  self.assertEqual(len(items),137);self.assertEqual(items[0][1].props['XCMate.MediaId'],'136')
  self.assertEqual({li.props['XCMate.MediaId'] for _,li in items},set(map(str,range(137))))
  for url,li in items:self.assertIn('sid='+li.props['XCMate.MediaId'],url)
 def test_group_generation_read_keeps_old_snapshot_during_concurrent_publish(self):
  self.large();iterator=self.group.pages(self.portal);first=next(iterator)
  self.index.import_group('p','live','a',[dict(stream_id='new',category_id='a',name='New')])
  rows=first+[r for page in iterator for r in page]
  self.assertEqual(len(rows),137);self.assertNotIn('new',{r['sid'] for r in rows})
 def test_legacy_live_group_has_no_twelve_sender_limit(self):
  self.index.replace_catalog('p','live',self.records(79),self.catalogs['get_live_categories'])
  rows=self.group.snapshot(self.portal);self.assertEqual(len(rows),79);self.assertEqual(rows[-1]['sid'],'78')
 def test_disabled_group_cannot_reappear_from_old_snapshot(self):
  self.large();selection=importlib.import_module('group_selection')
  selection.save('p',['b'],'live')
  self.assertEqual(self.group.snapshot(self.portal),[])
 def test_event_data_is_populated_for_sender_after_first_sixteen(self):
  self.large(40);guide=importlib.import_module('guide_store')
  guide.import_cache('p',{'xml39':[dict(name='Actual final programme',channel='xml39',start_timestamp=self.now-60,stop_timestamp=self.now+600)]})
  self.router._params['action']='widget_live_start_group';self.routes.dispatch(self.router)
  li=next(li for _,li,_ in self.added if li.props.get('XCMate.MediaId')=='39')
  self.assertEqual(li.props['XCMate.ProgrammeTitle46'],'Actual final programme')
 def test_full_group_publication_survives_new_interpreter_and_bounds_artwork_queue(self):
  self.large();rows,code=self.w.snapshot(self.portal,'live');refresh=importlib.import_module('widget_refresh45')
  with mock.patch('programme_art46.enqueue') as enqueue:self.assertTrue(refresh.publish(self.portal,'live',rows,code))
  self.assertLessEqual(enqueue.call_count,16);self.assertEqual(len(refresh.read('p','live')['items']),137)
  manifest=json.loads(Path(refresh.path('p','live')).read_text());self.assertEqual(manifest['count46'],137)
  self.assertTrue(all(p['count']<=16 for p in manifest['pages46']));self.assertNotIn('items',manifest)
 def test_cyclic_background_artwork_reaches_later_group_pages(self):
  self.large(40);rows,code=self.w.snapshot(self.portal,'live');refresh=importlib.import_module('widget_refresh45');seen=set()
  with mock.patch('programme_art46.enqueue',side_effect=lambda e:seen.add(e['sid'])):
   for _ in range(3):refresh.publish(self.portal,'live',rows,code)
  self.assertEqual(seen,set(map(str,range(40))))
 def test_retained_legacy_archive_reproduces_old_budget_but_new_query_skips_it(self):
  rows=[dict(stream_id=str(i),category_id='a',name='Film '+str(i),added=self.now+i) for i in range(40005)]
  self.index.replace_catalog('p','vod',rows,self.catalogs['get_vod_categories']);self.index.import_group('p','vod','a',rows[-30:])
  db=sqlite3.connect(self.index.path());db.execute('CREATE TEMP TABLE selected_categories(cid TEXT PRIMARY KEY)');db.execute("INSERT INTO selected_categories VALUES('a')")
  callbacks=[0]
  def interrupt():callbacks[0]+=1;return callbacks[0]>10
  db.set_progress_handler(interrupt,1000)
  with self.assertRaises(sqlite3.OperationalError):db.execute("SELECT t.sid FROM titles t WHERE t.pid='p' AND t.kind='vod' AND t.cid IN(SELECT cid FROM selected_categories) AND NOT EXISTS(SELECT 1 FROM heads h WHERE h.pid=t.pid AND h.kind=t.kind AND h.cid=t.cid) ORDER BY t.added DESC,t.ordinal LIMIT 24").fetchall()
  db.close();reader=self.w.WidgetReader('p');original=reader._query;queries=[]
  def query(sql,*args,**kw):queries.append(sql);return original(sql,*args,**kw)
  started=time.perf_counter()
  with mock.patch.object(reader,'_query',side_effect=query):actual=reader.small('vod')
  self.assertEqual(len(actual),24);self.assertFalse(any('SELECT t.sid,t.cid,t.added,t.ordinal FROM titles' in s for s in queries))
  print('WIDGET46_RETAINED_ARCHIVE',json.dumps(dict(legacy_rows=40005,old_opcode_budget='INTERRUPTED',new_rows=len(actual),new_ms=round((time.perf_counter()-started)*1000,3))))
 def test_movie_busy_keeps_policy_valid_lastgood_after_ten_minutes(self):
  rows,_=self.w.snapshot(self.portal,'vod');filename,_=self.w.files('p','vod');value=json.loads(Path(filename).read_text());value['at']=time.time()-3600;Path(filename).write_text(json.dumps(value))
  error=self.index.IndexReadError('BUDGET');error.code='BUDGET'
  with mock.patch.object(self.w.WidgetReader,'state',side_effect=error):actual,code=self.w.snapshot(self.portal,'vod')
  self.assertEqual(actual,rows);self.assertEqual(code,'BUDGET')
 def test_empty_catalogue_and_budget_failure_are_distinct(self):
  self.index.replace_catalog('p','vod',[],self.catalogs['get_vod_categories'])
  self.assertEqual(self.w.snapshot(self.portal,'vod'),([], 'READY'))
  filename,_=self.w.files('p','vod');Path(filename).unlink()
  error=self.index.IndexReadError('BUDGET');error.code='BUDGET'
  with mock.patch.object(self.w.WidgetReader,'state',side_effect=error):self.assertEqual(self.w.snapshot(self.portal,'vod'),([], 'BUDGET'))
 def test_series_visibility_and_exact_ids_remain_unchanged(self):
  rows,code=self.w.snapshot(self.portal,'series');self.assertEqual(code,'READY');self.assertEqual(len(rows),3)
  self.router._params['action']='widget_recent_series';self.routes.dispatch(self.router)
  self.assertEqual({li.props['XCMate.MediaId'] for _,li,_ in self.added},{'1','2','3'})
 def test_navigator_catalog_uses_local_index_without_loading_provider_json(self):
  catalog=importlib.import_module('live_catalog');original=self.client.get_cached_catalog
  self.client.get_cached_catalog=mock.Mock(side_effect=lambda action:original(action) if action=='get_live_categories' else (_ for _ in ()).throw(AssertionError('full provider streams cache')))
  categories,streams=catalog.read(self.portal,self.client)
  self.assertTrue(categories);self.assertEqual(len(streams),3)
 def test_start_group_snapshot_is_published_before_remaining_enabled_groups(self):
  self.large(137);self.index.import_group('p','live','b',[dict(stream_id='other-'+str(i),category_id='b',name='Other') for i in range(9)])
  partial=[];full=importlib.import_module('live_catalog46').read(self.portal,partial.append)
  self.assertEqual(len(partial),1);self.assertEqual(len(partial[0][1]),137);self.assertEqual(len(full[1]),146)
  self.assertEqual({r['category_id'] for r in partial[0][1]},{'a'})
 def test_navigator_catalog_deduplicates_ids_and_preserves_start_group(self):
  self.large(30);self.index.import_group('p','live','b',[dict(stream_id='1',category_id='b',name='Duplicate'),dict(stream_id='other',category_id='b',name='Other')])
  _,streams=importlib.import_module('live_catalog46').read(self.portal)
  self.assertEqual(len(streams),31);self.assertEqual(next(r for r in streams if r['sid']=='1')['category_id'],'a')
 def test_real_entry_widget_does_not_import_or_construct_full_legacy_router(self):
  spec=importlib.util.spec_from_file_location('entry_widget46',ADDON/'default.py');entry=importlib.util.module_from_spec(spec);spec.loader.exec_module(entry)
  legacy=mock.Mock();legacy.Router.side_effect=AssertionError('legacy router imported for widget')
  with mock.patch.dict(sys.modules,main=legacy),mock.patch.object(sys,'argv',['plugin://plugin.video.xtreammate/','7','?action=widget_recent_vod&pid=p']):entry.run()
  legacy.Router.assert_not_called();self.assertEqual(len(self.added),24);self.assertEqual(len(self.ends),1)
 def test_disabled_portal_fast_entry_cannot_show_stale_lastgood_or_play(self):
  fast=importlib.import_module('widget_entry46');self.portal['enabled']=False;self.router._params['action']='widget_live_start_group'
  self.assertTrue(fast.dispatch(self.router));self.assertFalse(self.added);self.assertEqual(len(self.ends),1);self.assertFalse(self.builtins)
 def test_corrupted_large_publication_page_refuses_torn_home_frame(self):
  self.large();rows,code=self.w.snapshot(self.portal,'live');refresh=importlib.import_module('widget_refresh45');self.assertTrue(refresh.publish(self.portal,'live',rows,code))
  manifest=json.loads(Path(refresh.path('p','live')).read_text());page=Path(refresh.path('p','live')).parent/manifest['pages46'][0]['name'];page.write_bytes(b'broken')
  self.assertIsNone(refresh.read('p','live'))
 def test_failed_new_large_page_keeps_previous_complete_manifest_and_generation(self):
  self.large();rows,code=self.w.snapshot(self.portal,'live');refresh=importlib.import_module('widget_refresh45');pages=importlib.import_module('widget_pages46')
  self.assertTrue(refresh.publish(self.portal,'live',rows,code));before=Path(refresh.path('p','live')).read_bytes();original=pages.atomic
  def fail(filename,data):
   if '.page46-' in filename and filename.endswith('-1.json'):raise OSError('disk interrupted')
   return original(filename,data)
  with mock.patch.object(pages,'atomic',side_effect=fail):self.assertFalse(refresh.publish(self.portal,'live',rows,code))
  self.assertEqual(Path(refresh.path('p','live')).read_bytes(),before);self.assertEqual(len(refresh.read('p','live')['items']),137)
