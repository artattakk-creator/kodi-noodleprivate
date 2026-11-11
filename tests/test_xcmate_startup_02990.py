"""Real .89 regressions: files, worker DTOs and native route contracts.

These are host tests. Neither synthetic capacity nor a ListItem is an Android
pixel or physical-device acceptance result.
"""
import contextlib,importlib,json,sys,unittest
from concurrent.futures import Future
from types import SimpleNamespace
from unittest import mock
from xcmate027_fixture import Fixture
from test_xcmate_02988 import png


class Startup90(Fixture,unittest.TestCase):
 def test_a_missing_logos_are_processed_in_a_bounded_eight_item_round(self):
  rows=[dict(sid=str(i),name='Station',stream_icon='https://images.example.org/'+str(i)+'.png') for i in range(12)]
  module=__import__('station_logos88');module._due.clear()
  facts=dict(capacity82='SAME_VOLUME_VERIFIED',free=115*1024**2,total=4034297856,volume82='same',mount82='fuse')
  with mock.patch('art_storage82.capacity',return_value=facts),mock.patch.object(module,'fetch',return_value=png()) as fetch:
   module.prepare(self.portal,rows)
  self.assertEqual(fetch.call_count,8)
  self.assertEqual(len(__import__('logo_manifest86').read(self.portal,rows,with_fallback=False)),8)

 def test_a_logo_retry_does_not_keep_recovered_database_work_pending(self):
  import threading,time,importlib
  assets=importlib.reload(__import__('widget_assets69'));health=__import__('artwork_health82')
  row=dict(sid='1',name='Station',stream_icon='https://images.example.org/one.png')
  paused={'code':'DB_PAUSED','reason':'BUSY','until':time.time()+1800};entered=threading.Event();recovered=threading.Event()
  def guard():
   entered.set()
   if paused['code']!='READY':raise health.Deferred('DB_PAUSED',paused['until'],'BUSY')
   recovered.set()
  try:
   with mock.patch.object(assets,'_references82'),mock.patch('logo_manifest86.read',return_value={}),mock.patch('station_logos87.recover'),mock.patch('station_logos88.recover'),mock.patch('logo_manifest86.prepare'),mock.patch('station_logos88.next_delay90',return_value=60),mock.patch('artwork_display84.observe'),mock.patch('widget_cache82.prepare'),mock.patch('poster_store89.prepare'),mock.patch('render_temp85.prepare'),mock.patch.object(health,'status',side_effect=lambda:dict(paused)),mock.patch.object(health,'guard',side_effect=guard),mock.patch('render_cache81.prepare'),mock.patch('media_hero81.prepare'):
    self.assertTrue(assets.prepare(self.portal,'live',[row]));self.assertTrue(entered.wait(2));worker=assets._thread
    for _ in range(100):
     if assets._deferred82:break
     time.sleep(.01)
    self.assertTrue(assets._deferred82);self.assertTrue(assets._logo_due90)
    paused['code']='READY';self.assertTrue(recovered.wait(2))
    for _ in range(100):
     if not assets._pending:break
     time.sleep(.01)
    self.assertFalse(assets._pending);self.assertFalse(assets._deferred82);self.assertTrue(assets._logo_due90)
    self.assertIs(assets._thread,worker);self.assertTrue(worker.is_alive())
    self.assertFalse(assets.prepare(self.portal,'live',[row]))
  finally:
   assets.shutdown()
   if assets._thread:assets._thread.join(2)

 def test_b_real_channel_model_can_prepare_visible_epg_without_dictionary_attribute_error(self):
  from iptv import Channel
  channel=Channel(name='Station',url='https://fixture.invalid/live',logo='',tvg_id='xml',extra=dict(stream_id='1',category_id='a'))
  self.assertEqual(__import__('programme_prefetch48').visible75(self.portal,[channel]),[channel])

 def test_b_cold_checkpoint_accepts_the_actual_channel_model_and_restores_now_next(self):
  from iptv import Channel
  channel=Channel(name='Station',url='https://fixture.invalid/live',logo='',extra=dict(stream_id='1',category_id='a'))
  info=dict(now='Monk',start=self.now-60,stop=self.now+1800,events=[dict(title='Monk',start=self.now-60,stop=self.now+1800)],snapshot_revision=('guide',1),canonical46='xml')
  h=__import__('epg_handoff63');h.remember('p',channel,info,{});h.register('p',('guide',1))
  module=__import__('epg_snapshot75');module._due85.clear()
  self.assertTrue(module.checkpoint('p',[channel]));self.properties.clear()
  self.assertEqual(module.restore('p'),1);self.assertEqual(h.get('p','1')['now'],'Monk')

 def test_c_validated_unchanged_portal_snapshot_is_readable_during_unrelated_write_lock(self):
  module=__import__('portal_snapshot');reader=module.Snapshot();path=self.folder/'portals.json';path.write_text(json.dumps([self.portal]))
  first=reader.read(str(path),['xtream']);first[0]['name']='caller mutation'
  @contextlib.contextmanager
  def locked(*a,**kw):raise TimeoutError('synthetic unrelated profile writer');yield
  with mock.patch('profile_transaction.reading',side_effect=locked):
   self.assertEqual(reader.read(str(path),['xtream'])[0]['name'],'Demo')

 def test_d_live_start_station_does_not_invalidate_movie_or_series_lastgood(self):
  module=__import__('widget_data41')
  for kind in ('vod','series'):
   original=module.policy(self.portal,kind)
   self.assertEqual(module.policy(dict(self.portal,start_stream_id='2',start_group_id='b'),kind),original)

 def test_d_previous_movie_rows_survive_live_selection_change_and_sql_budget(self):
  module=__import__('widget_data41');rows,code=module._snapshot84(self.portal,'vod',background=True)
  self.assertTrue(rows);self.portal['start_stream_id']='2'
  with mock.patch('widget_movie47.MovieReader.state',side_effect=self.index.IndexReadError('BUDGET')):
   after,code=module._snapshot84(self.portal,'vod',background=True)
  self.assertEqual(after,rows);self.assertNotEqual(code,'EMPTY')

 def test_f_committed_mapping_is_visible_for_the_original_request_after_metadata_enrichment(self):
  q=__import__('work_requests86');mapping=__import__('programme_mapping85')
  event=dict(pid='p',sid='1',title='Monk',canonical='xml',start=self.now-60,stop=self.now+1800)
  actual=dict(event,year=2002,country=['US'],genre='Comedy')
  selected=dict(source='tmdb',id=1695,title='Monk',year=2002,country=['US'],media_type86='tv',verified85=True,url='https://image.tmdb.org/t/p/w1280/fixture.png',role='backdrop')
  with mock.patch.object(q,'authoritative',return_value=actual),mock.patch('work_search86.details',return_value=selected):
   nonce=q.request(event,'save',candidate=selected);q.drain()
  self.assertEqual(q.result(nonce)['code'],'SAVED')
  self.assertTrue(mapping.committed89(event,nonce))
  before=mapping.path().read_bytes();self.properties.clear();mapping._loaded.clear();self.assertTrue(mapping.reload())
  self.assertEqual(mapping.current(event)['id'],1695);self.assertEqual(mapping.path().read_bytes(),before)
  self.assertIsNone(mapping.current(dict(event,sid='2')))

 def test_g_failed_full_catalogue_after_partial_model_remains_pending_and_retryable(self):
  with mock.patch.dict(sys.modules),mock.patch('xbmcgui.WindowDialog',new=type('WindowDialog',(),{}),create=True):
   sys.modules.pop('live_overlay',None)
   from live_overlay import LiveNavigator
  future=Future();future.set_exception(self.index.IndexReadError('SQLITE_BUSY'))
  model=SimpleNamespace(portal=self.portal,xc=self.client,_catalog_future39=future,_catalog_ready=True,_catalog_partial46=True)
  self.assertFalse(LiveNavigator._load_catalog_from_disk(model))
  self.assertTrue(model._catalog_partial46)
  self.assertIsNone(model._catalog_future39)

 def test_h_source_browser_without_portal_exposes_setup_instead_of_failed_directory(self):
  self.portals=[];self.router._params={'action':'widget_sources49'}
  self.routes.dispatch(self.router)
  self.assertTrue(self.added)
  self.assertTrue(any('action=setup_wizard' in url for url,_,_ in self.added))
  args,kwargs=self.ends[0];self.assertTrue(args[1] if len(args)>1 else kwargs.get('succeeded',True));self.assertFalse(self.builtins)


from xcmate050_fixture import Fixture50
class ForeignNavigation90(Fixture50,unittest.TestCase):
 def test_e_native_fixed_focus_factory_is_not_disabled_for_all_foreign_home_rows(self):
  import base64,lzma
  from xcmate027_fixture import ROOT
  graph=__import__('widget_skin78')
  extra=json.loads(lzma.decompress(base64.b64decode((ROOT/'tests/fixtures/bingie223_graph78.json.xz.b64').read_bytes())))
  for name,text in extra.items():(self.skin/name).write_text(text)
  files=graph.build({name:(self.skin/name).read_bytes() for name in graph.FILES})
  root=graph.parse(files['xml/IncludesHomeWidgets.xml'])
  for owner in ('widget_header_multi','WidgetBaseBingieIncludes'):
   calls=[n for n in root.find("include[@name='"+owner+"']").iter('include') if n.get('content')=='Fixed_Focus_Navigation_Factory']
   self.assertEqual(len(calls),1)
   self.assertNotIn('!Window.IsActive(Home)',calls[0].get('condition',''))
  own=root.find("include[@name='XCMate80.BaseBingie']/include[@content='Fixed_Focus_Navigation_Factory']")
  self.assertEqual(own.get('condition'),'!Window.IsActive(Home)')

 def test_d_original_compiler_owned_media_has_explicit_inner_bounds(self):
  import base64,lzma
  from xcmate027_fixture import ROOT
  graph=__import__('widget_skin78')
  extra=json.loads(lzma.decompress(base64.b64decode((ROOT/'tests/fixtures/bingie223_graph78.json.xz.b64').read_bytes())))
  for name,text in extra.items():(self.skin/name).write_text(text)
  files=graph.build({name:(self.skin/name).read_bytes() for name in graph.FILES})
  root=graph.parse(files['xml/IncludesHomeWidgets.xml']);row=root.find("include[@name='XCMate80.MediaRow']/control")
  inner=row.find("control[@type='group']")
  self.assertEqual(inner.findtext('width'),row.findtext('width'))
  self.assertEqual(int(inner.findtext('top'))+int(inner.findtext('height')),int(row.findtext('height')))
  self.assertEqual(root.findtext("include[@name='XCMate80.MediaNormal']/control/width"),'100%')
  conditions=[n.text for n in root.findall("include[@name='XCMate80.MediaNormal']/control/visible")]
  self.assertEqual(len(conditions),2);self.assertFalse(any('IsUpdating' in c or 'NumItems' in c or 'Control.IsVisible' in c for c in conditions))
  self.assertTrue(__import__('widget_skin90').verify(files))
  bad=dict(files);bad['xml/IncludesHomeWidgets.xml']=bad['xml/IncludesHomeWidgets.xml'].replace(b'<include name="XCMate80.MediaRow">',b'<include name="XCMate80.MediaRow"><param name="unknown-custom" default="true" />')
  with self.assertRaisesRegex(ValueError,'NAV90_UNVERIFIED'):__import__('widget_skin90').upgrade(bad)
