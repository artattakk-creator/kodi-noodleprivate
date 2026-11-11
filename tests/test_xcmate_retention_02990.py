"""Cold/busy boundaries, source isolation and passive native picker entry."""
import contextlib,importlib,json,runpy,sys,threading,time,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
from xcmate027_fixture import Fixture,ADDON
from test_xcmate_02988 import png

class Retention90(Fixture,unittest.TestCase):
 def epg(self,sid='1'):
  info=dict(now='Programme '+sid,start=self.now-60,stop=self.now+1800,events=[dict(title='Programme '+sid,start=self.now-60,stop=self.now+1800)],snapshot_revision=('guide',1),canonical46='xml'+sid)
  h=__import__('epg_handoff63');h.remember('p',dict(sid=sid),info,{});h.register('p',('guide',1))
  return info

 def test_checkpoint_rotating_visible_groups_retains_both_valid_event_snapshots(self):
  h=__import__('epg_handoff63');m=__import__('epg_snapshot75');m._due85.clear()
  self.epg('1');self.assertTrue(m.checkpoint('p',[dict(sid='1')]))
  m._due85.clear();self.epg('2');self.assertTrue(m.checkpoint('p',[dict(sid='2')]))
  self.properties.clear();self.assertEqual(m.restore('p'),2)
  self.assertEqual(h.get('p','1')['now'],'Programme 1');self.assertEqual(h.get('p','2')['now'],'Programme 2')

 def test_checkpoint_rejects_different_account_mapping_and_expired_event_without_deleting_it(self):
  m=__import__('epg_snapshot75');m._due85.clear();self.epg();self.assertTrue(m.checkpoint('p',[dict(sid='1')]))
  file=Path(m._path('p'));before=file.read_bytes();self.properties.clear()
  self.portal['xc_user']='different account';self.assertEqual(m.restore('p'),0)
  self.portal['xc_user']='user'
  with mock.patch('epg_sources.configuration',return_value=dict(mappings={'1':'other'},sources=[])):self.assertEqual(m.restore('p'),0)
  with mock.patch('epg_handoff63.time.time',return_value=self.now+2000):self.assertEqual(m.restore('p'),0)
  self.assertEqual(file.read_bytes(),before)

 def test_unchanged_manifest_is_parsed_once_and_caller_mutation_cannot_corrupt_cache(self):
  m=__import__('logo_manifest86');row=dict(sid='1',stream_icon='https://images.example.org/one.png')
  facts=dict(capacity82='SAME_VOLUME_VERIFIED',free=115*1024**2,total=4034297856,volume82='same')
  with mock.patch('art_storage82.capacity',return_value=facts):__import__('logo_store89').persist(self.portal,row,png())
  m._manifest90.clear()
  with mock.patch.object(m.json,'load',wraps=m.json.load) as load:
   values=m.load(self.portal,True);next(iter(values.values()))['sha256']='bad'
   self.assertEqual(len(m.read(self.portal,[row],False)),1);self.assertEqual(load.call_count,1)
  record=next(iter(m.load(self.portal,True).values()));self.assertNotEqual(record['sha256'],'bad')

 def test_complete_88_logo_hydration_and_two_cold_reads_have_zero_new_fetch_or_commits(self):
  m=__import__('station_logos88');manifest=__import__('logo_manifest86');rows=[dict(sid=str(i),name='Station',stream_icon='https://images.example.org/'+str(i)+'.png') for i in range(88)]
  facts=dict(capacity82='SAME_VOLUME_VERIFIED',free=115*1024**2,total=4034297856,volume82='same')
  m._due.clear()
  with mock.patch('art_storage82.capacity',return_value=facts),mock.patch.object(m,'fetch',return_value=png()) as fetch:
   for _ in range(11):m.prepare(self.portal,rows)
   self.assertEqual(fetch.call_count,88);self.assertIsNone(m.next_delay90(self.portal,rows))
   for _ in range(2):
    manifest._manifest90.clear();__import__('logo_store89')._verified.clear()
    with mock.patch('logo_store89.atomic',side_effect=AssertionError('no duplicate commit')):self.assertEqual(m.prepare(self.portal,rows),'READY')
   self.assertEqual(fetch.call_count,88)

 def test_missing_source_is_not_an_endless_pending_download_or_false_88_of_88(self):
  m=__import__('station_logos88');row=dict(sid='no-logo',name='Station');m._due.clear()
  with mock.patch.object(m,'fetch',side_effect=AssertionError('missing source has no request')):self.assertNotEqual(m.prepare(self.portal,[row]),'READY')
  self.assertIsNone(m.next_delay90(self.portal,[row]))

 def test_changed_or_deleted_portal_file_never_reuses_cached_credentials_under_lock(self):
  m=__import__('portal_snapshot');reader=m.Snapshot();file=self.folder/'portals.json';file.write_text(json.dumps([self.portal]));reader.read(str(file),['xtream'])
  @contextlib.contextmanager
  def locked(*a,**kw):raise TimeoutError('synthetic transaction');yield
  for content in (json.dumps([dict(self.portal,xc_pass='new test value')]),None):
   if content is None:file.unlink()
   else:file.write_text(content)
   with mock.patch('profile_transaction.reading',side_effect=locked),self.assertRaises(TimeoutError):reader.read(str(file),['xtream'])

 def test_native_picker_root_with_real_portal_is_three_folders_and_never_autoplays(self):
  self.portal['autoplay_start']=True
  namespace=runpy.run_path(str(ADDON/'default.py'),run_name='entry90_test')
  with mock.patch.object(sys,'argv',['plugin://plugin.video.xtreammate/','7','']),mock.patch('xbmcgui.getCurrentWindowDialogId',return_value=10101),mock.patch('xbmc.getCondVisibility',side_effect=lambda c:c=='Window.IsVisible(script-skinshortcuts.xml)'):namespace['run']()
  from urllib.parse import urlsplit,parse_qs
  self.assertEqual([parse_qs(urlsplit(url).query)['action'][0] for url,_,_ in self.added],['widget_live_start_group','widget_recent_vod','widget_recent_series'])
  self.assertTrue(all(folder for _,_,folder in self.added));self.assertFalse(self.builtins)

 def test_native_picker_root_without_portal_is_browsable_and_does_not_launch_wizard(self):
  self.portals=[];namespace=runpy.run_path(str(ADDON/'default.py'),run_name='entry90_test')
  with mock.patch.object(sys,'argv',['plugin://plugin.video.xtreammate/','7','']),mock.patch('xbmcgui.getCurrentWindowDialogId',return_value=10101),mock.patch('xbmc.getCondVisibility',side_effect=lambda c:c=='Window.IsVisible(script-skinshortcuts.xml)'):namespace['run']()
  self.assertTrue(self.added);self.assertTrue(any('action=setup_wizard' in url for url,_,_ in self.added));self.assertFalse(self.builtins)
  self.assertFalse(any('pid=' in url for url,_,_ in self.added))

 def test_unrelated_busy_or_foreign_dialog_never_changes_root_navigation_into_widget_picker(self):
  from home_entry import HomeRouter
  router=HomeRouter(['plugin://plugin.video.xtreammate/','7',''])
  with mock.patch('xbmcgui.getCurrentWindowDialogId',return_value=10138),mock.patch('xbmc.getCondVisibility',return_value=False):self.assertFalse(__import__('picker_entry90').dispatch(router))
  self.assertFalse(self.added);self.assertFalse(self.builtins)
