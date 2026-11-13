"""Explicit alias/cancellation/budget boundaries and >128 group selections."""
import contextlib,json,sys,unittest
from concurrent.futures import Future
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
from xcmate027_fixture import Fixture
from test_xcmate_02988 import png

class Boundaries90(Fixture,unittest.TestCase):
 def event(self):return dict(pid='p',sid='1',title='Monk',canonical='xml',start=self.now,stop=self.now+3600)
 def candidate(self):return dict(source='tmdb',id=1695,title='Monk',year=2002,media_type86='tv',verified85=True,url='https://image.tmdb.org/t/p/w1280/monk.png',role='backdrop')
 def saved(self):
  q=__import__('work_requests86');m=__import__('programme_mapping85');event=self.event();actual=dict(event,year=2002,country=['US'])
  with mock.patch.object(q,'authoritative',return_value=actual),mock.patch('work_search86.details',return_value=self.candidate()):
   nonce=q.request(event,'save',candidate=self.candidate());q.drain()
  self.assertEqual(q.result(nonce)['code'],'SAVED');return q,m,event,actual
 def test_manual_enrichment_alias_has_epoch_and_reset_or_hide_reaches_same_record(self):
  q,m,event,actual=self.saved();self.assertGreater(m.epoch(event),0)
  for action in ('hide','automatic'):
   with mock.patch.object(q,'authoritative',return_value=actual):
    nonce=q.request(event,'save',action=action);q.drain()
   self.assertEqual(q.result(nonce)['code'],'SAVED');m._loaded.clear();self.assertTrue(m.reload())
   if action=='hide':self.assertTrue(m.current(event)['hidden'])
   else:self.assertIsNone(m.current(event));self.assertIsNone(m.current(actual))
 def test_manual_alias_never_crosses_account_sender_epg_source_or_work(self):
  q,m,event,actual=self.saved()
  for changed in (dict(event,sid='2'),dict(event,canonical='different'),dict(event,epg_source46='new'),dict(event,title='Different work')):self.assertIsNone(m.current(changed))
  self.portal['xc_user']='other';self.assertIsNone(m.current(event))
 def test_ambiguous_alias_never_selects_first_record(self):
  m=__import__('programme_mapping85');key='a'*64
  self.assertEqual(m.record_key90({'b'*64:dict(aliases90=[key]),'c'*64:dict(aliases90=[key])},key),key)
 def test_cancelled_or_locked_save_retains_previous_atomic_mapping(self):
  q,m,event,actual=self.saved();before=m.path().read_bytes()
  with mock.patch.object(q,'authoritative',return_value=actual),mock.patch('work_search86.details',return_value=self.candidate()):
   nonce=q.request(event,'save',candidate=self.candidate());q.cancel(nonce);q.drain()
  self.assertEqual(m.path().read_bytes(),before)
  @contextlib.contextmanager
  def locked(**kw):raise TimeoutError('synthetic lock');yield
  with mock.patch.object(q,'authoritative',return_value=actual),mock.patch('work_search86.details',return_value=self.candidate()),mock.patch('profile_transaction.writing',side_effect=locked):
   nonce=q.request(event,'save',candidate=self.candidate());q.drain()
  self.assertEqual(q.result(nonce)['code'],'PROFILE_BUSY');self.assertEqual(m.path().read_bytes(),before)
 def test_low_space_below_floor_stops_new_logo_commits_but_keeps_verified_previous(self):
  s=__import__('logo_store89');m=__import__('logo_manifest86');row=dict(sid='1',stream_icon='https://images.example.org/one.png')
  facts=dict(capacity82='SAME_VOLUME_VERIFIED',free=115*1024**2,total=4034297856,volume82='same')
  with mock.patch('art_storage82.capacity',return_value=facts):s.persist(self.portal,row,png())
  filename=m.location()[1];before=Path(filename).read_bytes()
  with mock.patch('art_storage82.capacity',return_value=dict(facts,free=40*1024**2)):
   with self.assertRaisesRegex(OSError,'LOGO_SAFETY_FLOOR'):s.persist(self.portal,dict(row,sid='2'),png())
   self.assertEqual(len(m.read(self.portal,[row],False)),1)
  self.assertEqual(Path(filename).read_bytes(),before)
 def test_twenty_groups_and_station_selections_preserve_sid_beyond_first_128_rows(self):
  groups=[dict(category_id=str(i),category_name='Group '+str(i)) for i in range(20)]
  streams=[dict(stream_id=str(i*1000+j+1),category_id=str(i),name='Station '+str(j)) for i in range(20) for j in range(137)]
  self.catalogs.update(get_live_categories=groups,get_live_streams=streams)
  model=__import__('live_prepare47').model(self.portal,self.client,groups,streams)
  with mock.patch.dict(sys.modules),mock.patch('xbmcgui.WindowDialog',new=type('WindowDialog',(),{}),create=True):
   sys.modules.pop('live_overlay',None);from live_overlay import LiveNavigator,category_rows
  future=Future();future.model47=model;future.set_result((groups,streams))
  nav=SimpleNamespace(portal=self.portal,xc=self.client,sid='1',_catalog_future39=future,_catalog_ready=False)
  self.assertTrue(LiveNavigator._load_catalog_from_disk(nav));self.assertEqual(len(nav.channels),2740)
  nav.rows=category_rows(nav.groups,nav.enabled);nav._highlight={'channels':0};nav.mode='groups';nav._page_start=128;nav._row_offset=1
  position=[0];played=[];nav.control=SimpleNamespace(getSelectedPosition=lambda:position[0]);nav._tune=lambda channel:played.append(str(channel.extra['stream_id']))
  def switch(mode):nav.mode=mode;nav.visible_channels=list(nav.index.selection(nav.category_id,nav.enabled)[0])
  nav._switch=switch
  with mock.patch('library_index.Reader._query',side_effect=self.index.IndexReadError('SQLITE_BUSY')),mock.patch('xbmc.Player',side_effect=AssertionError('navigation never controls playback')):
   for group in range(20):
    nav.mode='groups';position[0]=next(i for i,r in enumerate(nav.rows) if r[0]==str(group));LiveNavigator._select(nav)
    self.assertEqual(nav.category_id,str(group));self.assertEqual(len(nav.visible_channels),137)
    position[0]=9;LiveNavigator._select(nav);self.assertEqual(played[-1],str(group*1000+137))
  self.assertEqual(len(played),20)
 def test_failed_full_future_retains_exact_policy_first_model_on_next_prepare(self):
  module=__import__('live_catalog');from live_warm68 import portal_key,token
  key=(str(self.folder),'p',portal_key(self.portal),token(self.portal));old=Future();old.first46=([],[]);old.first_model47={'channels':[]};old.set_exception(self.index.IndexReadError('SQLITE_BUSY'));module._prepared[key]=(old,0)
  with mock.patch('threading.Thread'):
   new=module.prepare(self.portal,self.client,force=True)
  self.assertIs(new.first_model47,old.first_model47);self.assertEqual(new.first46,old.first46)
