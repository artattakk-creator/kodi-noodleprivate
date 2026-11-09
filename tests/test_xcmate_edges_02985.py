""".85 crash, foreign-dialog, source-change and independent work identity tests."""
import importlib,io,json,time,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,ADDON
class Edge85(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.temp=importlib.import_module('artwork_temp85');self.maps=importlib.import_module('programme_mapping85');self.maps.reload()
  self.event=dict(pid=self.portal['id'],sid='85',canonical='epg85',title='Modern Family',genre='Serie',start=self.now,stop=self.now+1800,key='synthetic85')
 def png(self,n=1):
  from PIL import Image
  b=io.BytesIO();Image.new('RGB',(80,60),(20,n,90)).save(b,'PNG');return b.getvalue()
 def test_crash_after_body_rename_recovers_exact_journal_and_context(self):
  c=self.temp.Cache(self.folder/'new85');atomic=c.atomic
  def write(path,body):
   if path.name=='index.json':raise OSError('SIMULATED_PROCESS_DEATH')
   return atomic(path,body)
  with mock.patch.object(c,'atomic',side_effect=write):
   with self.assertRaises(OSError):c.put(self.png(),context='event',reference={'source':'xmltv_event'})
  self.assertTrue((c.root/'pending85.json').exists());cold=self.temp.Cache(c.root);cold.recover()
  self.assertEqual(Path(cold.context('event')['image']).read_bytes(),self.png());self.assertFalse((c.root/'pending85.json').exists())
 def test_recovery_rejects_changed_journal_target_without_deleting_it(self):
  c=self.temp.Cache(self.folder/'new85');c.checked(create=True);target=c.root/('a'*64+'.png');target.write_bytes(self.png())
  (c.root/'pending85.json').write_text(json.dumps(dict(file=target.name,temp='.body85-original',sha256='a'*64,size=len(self.png()),record={})))
  with self.assertRaisesRegex(OSError,'HASH_CHANGED'):c.recover()
  self.assertEqual(target.read_bytes(),self.png())
 def test_repeated_unowned_metadata_crash_files_fail_closed(self):
  c=self.temp.Cache(self.folder/'new85');c.checked(create=True)
  for i in range(3):(c.root/('.txn-crash'+str(i))).write_bytes(b'ownedness unknown')
  with self.assertRaisesRegex(OSError,'METADATA_LIMIT'):c.put(self.png())
  self.assertEqual(len(list(c.root.glob('.txn-crash*'))),3)
 def test_gui_pin_survives_worker_pin_expiry_and_prevents_eviction(self):
  clock=[1000.];c=self.temp.Cache(self.folder/'new85',max_objects=1,clock=lambda:clock[0]);a=c.put(self.png());self.temp.touch(a['sha256']);clock[0]+=100
  with self.assertRaisesRegex(OSError,'PINNED'):c.put(self.png(2))
  self.assertTrue(Path(a['file']).exists())
 def test_failed_image_probe_is_backed_off_without_raising_source_error(self):
  m=importlib.import_module('render_temp85');from media_sources43 import SourceError
  with mock.patch('programme_assets47.sources',return_value={'poster':'https://image.tmdb.org/t/p/w500/test.png'}),mock.patch('widget_assets69.safe',return_value=True),mock.patch('render_temp85.recover',return_value=None),mock.patch('render_cache81.record_for',return_value=None),mock.patch('artwork_visible.public_dns',return_value=True),mock.patch('programme_transport77.verified',side_effect=SourceError('HTTP_NOT_FOUND')) as network:
   m.prepare(self.portal,'vod',[{'sid':'1'}]);m.prepare(self.portal,'vod',[{'sid':'1'}]);self.assertEqual(network.call_count,1)
 def test_missing_source_config_hash_changes_binding_without_touching_mapping_file(self):
  event=dict(self.event);before=self.maps.namespace(event)
  with mock.patch('epg_sources.configuration',return_value={'sources':[{'id':'one','uri':'https://public.invalid/one','enabled':True}],'mappings':{}}):self.maps.refresh_sources(event['pid'])
  after=self.maps.namespace(event);self.assertNotEqual(before,after);self.assertFalse(self.maps.path().exists())
  self.maps._source_due.clear()
  with mock.patch('epg_sources.configuration',return_value={'sources':[{'id':'two','uri':'https://public.invalid/two','enabled':True}],'mappings':{}}):self.maps.refresh_sources(event['pid'])
  self.assertNotEqual(after,self.maps.namespace(event))
 def test_authoritative_source_ignores_unknown_source_config_receipt(self):
  e=dict(self.event,source_key46='stable',epg_source46='sourceA');before=self.maps.namespace(e)
  with mock.patch('epg_sources.configuration',return_value={'sources':[{'id':'new','enabled':True}],'mappings':{}}):self.maps.refresh_sources(e['pid'])
  self.assertEqual(before,self.maps.namespace(e))
 def test_manual_series_choice_cannot_cross_into_same_named_film(self):
  self.maps.set_mapping(self.event,dict(id=1,source='tmdb',verified85=True))
  self.assertIsNone(self.maps.current(dict(self.event,genre='Spielfilm')))
 def test_foreign_modal_prevents_context_menu_and_does_not_close_foreign_window(self):
  m=importlib.import_module('series_manager85');parent=mock.Mock(event=self.event,_closed=False,_owner69='ours')
  with mock.patch('programme_window46.permitted',return_value=False),mock.patch.object(m.xbmcgui,'Dialog') as dialog:
   m.open(parent);dialog.assert_not_called()
 def candidate_dialog85(self):
  m=importlib.import_module('series_manager85');d=m.SeriesWindow85('XCMateSeries85.xml',str(ADDON),'Default','720p')
  rows=[dict(id=i,source='tmdb',year=2021,country=['US'],title='Synthetic '+str(i),original='Original '+str(i),overview='No private data',verified85=True) for i in range(8)]
  d.configure(rows,event=self.event);d.show();return d
 def test_candidate_ok_on_list_does_not_commit_until_explicit_confirm(self):
  d=self.candidate_dialog85();d.onClick(200);self.assertIsNone(d.chosen);self.assertFalse(self.maps.path().exists());d.onClick(201);self.assertEqual(d.chosen['id'],0);self.assertFalse(self.maps.path().exists())
 def test_candidate_back_closes_only_own_window_without_persisting(self):
  d=self.candidate_dialog85();d.onAction(mock.Mock(getId=lambda:92));self.assertTrue(d._closed);self.assertFalse(self.maps.path().exists())
 def test_candidate_six_gets_lazy_thumbnail_only_via_service_intent(self):
  d=self.candidate_dialog85();d.getControl(200).selectItem(5)
  with mock.patch('series_requests85.request',return_value='a'*32) as request,mock.patch('series_requests85.result',return_value=None):
   d.pump();d.pump();self.assertEqual(request.call_count,1);self.assertEqual(request.call_args.kwargs['thumbnail']['id'],5)
 def test_candidate_wrong_source_reply_cannot_replace_thumbnail(self):
  d=self.candidate_dialog85();d._nonce85='a'*32;d._requested85={0}
  with mock.patch('series_requests85.result',return_value={'code':'THUMB','binding':'wrong','rows':[dict(id=0,source='tmdb',thumb85='bad')]}):d.pump()
  self.assertFalse(d.getControl(200).getListItem(0).art)
 def test_provider_and_source_specific_context_round_trip_after_restart(self):
  e=dict(self.event,epg_source46='sourceA');self.maps.set_mapping(e,dict(id=22,source='tvmaze',verified85=True,year=2021));self.maps.window().clearProperty(self.maps.PREFIX+'Records');self.maps.reload()
  self.assertEqual(self.maps.current(dict(e,start=self.now+86400))['id'],22);self.assertIsNone(self.maps.current(dict(e,epg_source46='sourceB')))
 def test_known_series_names_do_not_require_genre_or_episode(self):
  self.options.update(programme_tmdb46=True,tmdb_research43=True,tmdb_read_token43='SYNTHETIC85_NOT_SECRET',programme_tvmaze67=False)
  engine=importlib.import_module('programme_candidates85')
  for title,official in [('Alarm für Cobra 11','Alarm für Cobra 11 – Die Autobahnpolizei'),('Die Rosenheim-Cops','Die Rosenheim-Cops'),('M*A*S*H','M*A*S*H'),('Modern Family','Modern Family'),('The Middle','The Middle'),('King of Queens','The King of Queens')]:
   def request(url,**kwargs):
    row=dict(id=85,name=official,original_name=official,first_air_date='2000-01-01',origin_country=['US'],poster_path='/synthetic85.jpg')
    if '/search/movie' in url:return dict(page=1,total_pages=0,total_results=0,results=[])
    if '/search/tv' in url:return dict(page=1,total_pages=1,total_results=1,results=[row])
    if '/alternative_titles' in url:return dict(id=85,results=[dict(title=title)])
    return row
   with self.subTest(title=title),mock.patch('tmdb_connection60.request',side_effect=request):
    result=engine.candidate(dict(self.event,title=title,genre=''));self.assertEqual(result['remote_id'],85);self.assertEqual(result['image_scope57'],'series_fallback')
 def test_verified_work_cache_reuses_identity_for_later_broadcast(self):
  engine=importlib.import_module('programme_candidates85');self.options.update(programme_tmdb46=True,tmdb_research43=True)
  row=dict(id=1,source='tmdb',year=2021,country=['US'],title='Modern Family',original='Modern Family',overview='',poster='https://image.tmdb.org/t/p/w500/t.jpg',url='https://image.tmdb.org/t/p/w500/t.jpg',role='poster',verified85=True)
  engine.remember(self.event,[row],tv_only=True)
  with mock.patch('tmdb_connection60.request',side_effect=AssertionError('unnecessary repeated work lookup')):self.assertEqual(engine.candidate(dict(self.event,start=self.now+86400))['remote_id'],1)
 def test_movie_resolver_remains_independent_of_series_manager(self):
  engine=importlib.import_module('programme_candidates85');self.options.update(programme_tmdb46=True,tmdb_research43=True)
  with mock.patch('tmdb_connection60.request',side_effect=AssertionError('series must ignore movie')):self.assertIsNone(engine.candidate(dict(self.event,genre='Spielfilm')))
 def test_short_home_memo_reuses_catalogue_and_invalidates_real_db_generation(self):
  m=importlib.import_module('widget_snapshot85');rows=[dict(sid='1',name='First')];original=mock.Mock(return_value=(rows,'READY'))
  with mock.patch('home_schedule75.applicable',return_value=True):
   self.assertEqual(m.snapshot(original,self.portal,'vod'),(rows,'READY'));self.assertEqual(m.snapshot(original,self.portal,'vod'),(rows,'READY'));self.assertEqual(original.call_count,1)
   self.index.import_group(self.portal['id'],'vod','a',[dict(stream_id=85,category_id='a',name='New fixture generation')]);original.return_value=([dict(sid='85',name='Changed')],'READY')
   self.assertEqual(m.snapshot(original,self.portal,'vod')[0][0]['sid'],'85');self.assertEqual(original.call_count,2)
 def test_tvmaze_official_alias_without_genre_is_available_for_explicit_selection(self):
  self.options.update(programme_tvmaze67=True,programme_tvmaze_optout77=False)
  module=importlib.import_module('programme_tvmaze85');show=dict(id=85,name='The King of Queens',premiered='1998-01-01',image={'original':'https://static.tvmaze.com/uploads/images/original_untouched/1/85.jpg'},network={'country':{'code':'US'}})
  with mock.patch('media_sources43.get',side_effect=[[dict(show=show)],show,[dict(name='King of Queens')]]):
   rows,done=module.search(dict(self.event,title='King of Queens',genre=''));self.assertTrue(done);self.assertEqual(rows[0]['id'],85);self.assertEqual(rows[0]['country'],['US'])
 def test_tvmaze_ghosts_country_disambiguates_verified_work_only(self):
  self.options.update(programme_tvmaze67=True,programme_tvmaze_optout77=False)
  module=importlib.import_module('programme_tvmaze67');uk=dict(id=19,name='Ghosts',premiered='2019-01-01',image={'original':'https://static.tvmaze.com/uploads/images/original_untouched/1/19.jpg'},network={'country':{'code':'GB'}});us=dict(uk,id=21,premiered='2021-01-01',network={'country':{'code':'US'}})
  with mock.patch('media_sources43.get',side_effect=[[dict(show=uk),dict(show=us)],uk,us]):
   result=module.candidate(dict(self.event,title='Ghosts',country='GB'));self.assertEqual(result['remote_id'],19);self.assertEqual(result['image_scope57'],'series_fallback')
