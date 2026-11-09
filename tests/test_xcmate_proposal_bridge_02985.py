"""A proposal remains unconfirmed through the real native-row and A/B Hero DTOs."""
import importlib,types,time,unittest
from unittest import mock
class ProposalBridge85(unittest.TestCase):
 def setUp(self):
  from test_xcmate_epg_handoff_02963 import Handoff63
  self.h=Handoff63('runTest');self.h.setUp();self.addCleanup(self.h.doCleanups);self.info=self.h.read()
 def test_native_live_row_copies_only_required_proposal_and_art_proof_fields(self):
  h=self.h;key=self.info['programme_key47'];image=str(h.folder/'verified-series.png')
  enriched=dict(props={'XCMate.MediaId':'1','XCMate.ProgrammeKey47':key,'XCMate.ProgrammeImage46':image,'XCMate.Provisional85':'true','XCMate.ArtProof69':'','PRIVATE_TEST_FIELD':'must not pass'},info={'plot':'Actual EPG plot'},_programme46={'key':key})
  with mock.patch('widget_group46.infos',return_value={'1':self.info}),mock.patch('widget_render47.values',return_value=[enriched]):values=importlib.import_module('live_items62').values(h.portal,[h.row])
  self.assertEqual(values[0]['props']['XCMate.Provisional85'],'true');self.assertIn('XCMate.ArtProof69',values[0]['props']);self.assertNotIn('PRIVATE_TEST_FIELD',values[0]['props']);self.assertIn('Bildvorschlag',values[0]['props']['XCMate.ProgrammeDescription46'])
 def test_event_rollover_clears_previous_proposal_flag_and_proof(self):
  item=dict(props={'XCMate.ProgrammeKey47':'old','XCMate.Provisional85':'true','XCMate.ProgrammeImage46':'/verified/old.png','XCMate.ArtProof69':'old proof'})
  importlib.import_module('live_text63').apply(item,self.h.portal,self.h.row,self.info)
  self.assertEqual(item['props']['XCMate.Provisional85'],'');self.assertEqual(item['props']['XCMate.ArtProof69'],'');self.assertEqual(item['props']['XCMate.ProgrammeTitle46'],self.info['now'])
 def test_dynamic_hero_bank_keeps_proposal_flag_and_clears_it_after_confirmation(self):
  h=self.h;info=self.info;hero=importlib.import_module('hero_epg63');hero._next=0;hero._last=None;hero._focus=None;hero._art=None
  from localization import tr
  selected={'XCMate.NoEpg63':tr(36102),'XCMate.RemainingFormat63':tr(36668,'{0}'),'XCMate.Home50':'true','XCMate.PortalId':'p','XCMate.MediaId':'1','XCMate.WidgetToken41':'1'*32}
  label=lambda expr:selected.get(expr.removeprefix('ListItem.Property(').removesuffix(')'),'')
  raw=next(e for e in info['events'] if e.get('start')==info['start'] and e.get('title')==info['now']);event=dict(raw,pid='p',sid='1',canonical=info.get('canonical46') or info.get('epg_id',''),revision=info['snapshot_revision'])
  import programme_requests68 as requests
  from programme_art46 import fingerprint
  art=dict(key=info['programme_key47'],code='READY',source='tmdb_series',match='PROVISIONAL_TV85',provisional85=True,image=str(h.folder/'verified-series.png'),fingerprint=fingerprint(event),scope69=requests.identity(event),profile69=requests.scope(),until=time.time()+60)
  requests.completed(event,art)
  window=types.SimpleNamespace(getControl=lambda cid:types.SimpleNamespace(setPercent=lambda p:None),getProperty=lambda k:h.properties.get(k,''),setProperty=lambda k,v:h.properties.__setitem__(k,v),clearProperty=lambda k:h.properties.pop(k,None))
  with mock.patch('xbmc.getSkinDir',return_value='skin.titan.bingie.mod',create=True),mock.patch('xbmc.getInfoLabel',side_effect=label),mock.patch('xbmcgui.getCurrentWindowId',return_value=10000),mock.patch('xbmcgui.Window',return_value=window),mock.patch('sqlite3.connect',side_effect=AssertionError('GUI SQL')),mock.patch('builtins.open',side_effect=AssertionError('GUI filesystem')):
   hero.poll();bank=h.properties['XCMate.Hero63.Active'];self.assertEqual(h.properties['XCMate.Hero63.'+bank+'.Provisional85'],'true');self.assertIn('Bildvorschlag',h.properties['XCMate.Hero63.'+bank+'.Description'])
   requests.completed(event,dict(art,provisional85=False,match='MANUAL_CONFIRMED'));hero._next=0;hero.poll();bank=h.properties['XCMate.Hero63.Active'];self.assertEqual(h.properties['XCMate.Hero63.'+bank+'.Provisional85'],'')
