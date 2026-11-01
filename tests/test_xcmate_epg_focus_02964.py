"""Real local guide rows survive cache eviction; focus never reads SQL or HTTP."""
import importlib,time,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture
class Focus64(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.bridge=importlib.import_module('epg_handoff63');self.rowmod=importlib.import_module('epg_row64');self.hero=importlib.import_module('hero_epg63')
  self.row=dict(sid='1',name='DMAX HEVC fixture',epg_channel_id='dmax.fixture',category_id='a')
  events={'dmax.fixture':[dict(name='Stored DMAX fixture event',start_timestamp=self.now-60,stop_timestamp=self.now+600,descr='Local fixture description')]}
  importlib.import_module('guide_store').import_cache('p',events,'focus64',now=self.now,trusted_feed=True)
  self.info=importlib.import_module('local_epg').now_next('p',[self.row],{},now=self.now)['1']
  self.props={'XCMate.Home50':'true','XCMate.PortalId':'p','XCMate.MediaId':'1','XCMate.WidgetToken41':'1'*32}
  importlib.import_module('live_text63').apply(dict(props=self.props),self.portal,self.row,self.info)
  self.window=types.SimpleNamespace(getProperty=lambda k:self.properties.get(k,''),setProperty=lambda k,v:self.properties.__setitem__(k,v),getControl=mock.Mock())
 def label(self,expr):return self.props.get(expr.removeprefix('ListItem.Property(').removesuffix(')'),'')
 def valid(self):return self.rowmod.valid(lambda k:self.props.get(k,''),self.window,'p','1',self.bridge.profile_scope())
 def test_real_stored_dmax_row_remains_visible_after_ram_slots_are_evicted(self):
  self.assertEqual(self.info['now'],'Stored DMAX fixture event');self.assertTrue(self.valid())
  for key in list(self.properties):
   if key.startswith(self.bridge.PREFIX):del self.properties[key]
  self.properties['XCMate.Hero63.Active']='B';self.hero._next=0;self.hero._last=None
  with mock.patch('xbmc.getSkinDir',return_value='skin.titan.bingie.mod',create=True),mock.patch('xbmc.getInfoLabel',side_effect=self.label),mock.patch('xbmcgui.getCurrentWindowId',return_value=10000),mock.patch('xbmcgui.Window',return_value=self.window),mock.patch('sqlite3.connect',side_effect=AssertionError('GUI SQL')),mock.patch('urllib.request.urlopen',side_effect=AssertionError('GUI HTTP')):
   self.hero.poll()
  self.assertEqual(self.properties['XCMate.Hero63.Active'],'');self.window.getControl.assert_not_called()
  self.assertEqual(self.props['XCMate.ProgrammeTitle46'],'Stored DMAX fixture event')
 def test_row_from_another_profile_is_never_accepted(self):
  self.props['XCMate.EpgProfile63']='other';self.assertFalse(self.valid())
 def test_changed_mapping_revision_and_new_guide_publication_reject_old_row(self):
  with mock.patch('epg_status.revision',return_value='changed'):self.assertFalse(self.valid())
  self.properties[self.bridge.meta_key('p')]='new-publication';self.assertFalse(self.valid())
 def test_expired_event_stale_row_and_nonfinite_numbers_are_not_reused(self):
  for field,value in (('XCMate.ProgrammeStop63',str(time.time()-1)),('XCMate.EpgAt64',str(time.time()-301)),('XCMate.ProgrammeStart63','nan')):
   old=self.props[field];self.props[field]=value;self.assertFalse(self.valid());self.props[field]=old
 def test_preferred_sender_does_not_starve_other_start_group_events(self):
  rows=[dict(sid=str(i),name='Fixture '+str(i),epg_channel_id='x'+str(i)) for i in range(16)]
  events={'x'+str(i):[dict(name='Local event '+str(i),start_timestamp=self.now-60,stop_timestamp=self.now+600)] for i in range(16)}
  importlib.import_module('guide_store').import_cache('p',events,'rotation64',now=self.now+1,trusted_feed=True)
  work=importlib.import_module('programme_prefetch48');work._positions.clear();seen=set()
  for _ in range(4):
   calls=[];work._next.clear()
   with mock.patch('hero_epg63.focused64',return_value='15'),mock.patch('programme_urls55.enqueue',side_effect=lambda event,**kw:calls.append(event['sid']) or True):
    work.prepare(self.portal,rows)
   self.assertEqual(calls[0],'15');self.assertLessEqual(len(calls),8);seen.update(calls)
  self.assertEqual(seen,{str(i) for i in range(16)})
