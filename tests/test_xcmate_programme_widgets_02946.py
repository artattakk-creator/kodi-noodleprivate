"""Existing widget routes, per-event shared pictures, exact click targets."""
import importlib,sys,unittest,types,time
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,ADDON,LIB
class ProgrammeWidgets46(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.items=importlib.import_module('widget_items45');self.decorate=importlib.import_module('programme_widgets46');self.events=importlib.import_module('programme_events46');self.row=dict(sid='1',name='Real station',kind='live',cover='',epg_channel_id='xml')
  self.info=dict(now='Current programme',next='Next programme',description='Saved description',start=self.now-60,stop=self.now+600,progress=.3,now_time='12:00',now_end_time='12:30',next_time='12:30',epg_id='xml',canonical46='xml',snapshot_revision=None,events=[dict(title='Current programme',description='Saved description',start=self.now-60,stop=self.now+600,source=1)])
 def value(self):return self.items.describe(self.portal,'live',self.row,{},self.info)
 def test_same_event_identity_and_picture_used_in_widget_and_details_pipeline(self):
  value=self.value();event=self.events.from_info(self.portal,self.row,self.info)
  self.assertEqual(value['props']['XCMate.ProgrammeKey46'],event['key']);self.assertEqual(value['art']['landscape'],event['placeholder']);self.assertIn(event['description'],value['info']['plot'])
 def test_actual_station_logo_is_separate_from_programme_image(self):
  cached=dict(image='/own/actual-programme.png',code='READY')
  value=dict(art={'thumb':'/own/actual-station-logo.png'},props={},info={'plot':'local plot'})
  with mock.patch('programme_art46.cached',return_value=cached):result=self.decorate.decorate(value,self.portal,self.row,self.info)
  self.assertEqual(result['props']['XCMate.ProgrammeLogo46'],'/own/actual-station-logo.png');self.assertEqual(result['art']['landscape'],'/own/actual-programme.png')
 def test_missing_logo_has_correct_station_name_and_neutral_image(self):
  value=self.value();self.assertEqual(value['props']['XCMate.ProgrammeLogo46'],'');self.assertEqual(value['props']['XCMate.ProgrammeChannel46'],'Real station');self.assertTrue(Path(value['art']['landscape']).is_file())
 def test_ok_target_preserves_original_sender_and_does_not_open_details_or_root(self):
  from urllib.parse import parse_qs,urlsplit
  q=parse_qs(urlsplit(self.value()['url']).query)
  self.assertEqual((q['action'],q['sid'],q['pid']),(['play_live'],['1'],['p']));self.assertNotIn('programme_details46',self.value()['url'])
 def test_context_info_targets_exact_programme_without_global_keymaps(self):
  value=self.value();li=self.items.item(value)
  self.assertIn('action=programme_details46',li.context[0][1]);self.assertIn('sid=1',li.context[0][1]);self.assertIn(value['props']['XCMate.ProgrammeKey46'],li.context[0][1]);self.assertEqual(li.props['IsPlayable'],'true')
 def test_actual_programme_rollover_changes_image_key_title_times_and_progress(self):
  before=self.value();self.info=dict(self.info,now='Following real show',start=self.now+600,stop=self.now+1200,now_time='12:30',now_end_time='13:00',progress=0,events=[dict(title='Following real show',start=self.now+600,stop=self.now+1200,source=1)])
  after=self.value();self.assertNotEqual(before['props']['XCMate.ProgrammeKey46'],after['props']['XCMate.ProgrammeKey46']);self.assertEqual(after['props']['XCMate.ProgrammeTitle46'],'Following real show');self.assertEqual(after['props']['XCMate.ProgrammePercent46'],'0')
 def test_no_epg_does_not_label_next_show_as_current(self):
  self.info=dict(self.info,now='',start=0,stop=0,events=[]);value=self.value();self.assertEqual(value['_programme46']['code'],'NO_EPG');self.assertEqual(value['props']['XCMate.ProgrammePercent46'],'0')
 def test_movie_and_series_widgets_keep_original_poster_metadata_and_exact_detail_route(self):
  for kind in ('vod','series'):
   row=dict(sid='selected',kind=kind,name='Actual title',cover='',added_at=self.now,year=2024)
   value=self.items.describe(self.portal,kind,row,{})
   self.assertIn('action=media_detail',value['url']);self.assertIn('sid=selected',value['url']);self.assertIn('kind='+kind,value['url']);self.assertEqual(value['info']['year'],2024);self.assertNotIn('XCMate.ProgrammeLogo46',value['props'])
 def test_focus_description_does_not_fetch_network_or_write_configuration(self):
  before=dict(self.options)
  with mock.patch('media_sources43.get',side_effect=AssertionError('network on focus')),mock.patch('programme_art46.enqueue',side_effect=AssertionError('worker from item rendering')):
   for _ in range(20):self.value()
  self.assertEqual(self.options,before);self.assertFalse(self.builtins)

 def test_real_plugin_route_and_background_frame_publish_identical_current_event(self):
  guide=importlib.import_module('guide_store')
  guide.import_cache('p',{'xml':[dict(name='Actual current programme',descr='Actual saved text',channel='xml',start_timestamp=self.now-60,stop_timestamp=self.now+600)]},'route-proof46',now=self.now)
  self.index.import_group('p','live','a',[dict(stream_id='1',name='Real station',epg_channel_id='xml',category_id='a')])
  self.router._params=dict(action='widget_live_start_group',pid='p');self.added.clear();self.routes.dispatch(self.router)
  actual=self.added[0][1];self.assertEqual(actual.props['XCMate.ProgrammeTitle46'],'Actual current programme');self.assertIn('Actual saved text',actual.info['plot'])
  from widget_data41 import snapshot
  rows,code=snapshot(self.portal,'live',background=True)
  refresh=importlib.import_module('widget_refresh45');self.assertTrue(refresh.publish(self.portal,'live',rows,code));frame=refresh.read('p','live')
  self.assertEqual(actual.props['XCMate.ProgrammeKey46'],frame['items'][0]['props']['XCMate.ProgrammeKey46']);self.assertEqual(actual.props['XCMate.ProgrammeTimes46'],frame['items'][0]['props']['XCMate.ProgrammeTimes46'])

class ProgrammeWindow46(Fixture,unittest.TestCase):
 def setUp(self):super().setUp();self.m=importlib.import_module('programme_window46')
 def test_grid_callback_only_queues_and_does_not_open_a_window(self):
  p=types.SimpleNamespace(_closed=False,_leaving=False,portal=self.portal);row=dict(sid='1',name='Station');event=dict(start=1,stop=2,title='Programme')
  with mock.patch.object(self.m,'show') as show:
   self.m.request(p,row,event);show.assert_not_called();self.m.open_pending(p);show.assert_called_once()
  self.assertFalse(self.builtins)
 def test_foreign_modal_blocks_details_without_closing_any_dialog(self):
  p=types.SimpleNamespace(_closed=False,_leaving=False,portal=self.portal,_native_dialog_id=13001)
  with mock.patch.object(sys.modules['xbmcgui'],'getCurrentWindowDialogId',return_value=12901):
   with mock.patch.object(self.m,'show') as show:self.m.request(p,dict(sid='1',name='Station'));self.m.open_pending(p);show.assert_not_called()
  self.assertFalse(self.builtins)
 def test_closed_parent_discards_pending_request_without_player_or_navigation(self):
  p=types.SimpleNamespace(_closed=True,_leaving=False,portal=self.portal);self.m.request(p,dict(sid='1',name='Station'));self.assertFalse(hasattr(p,'_programme_request46'));self.assertFalse(self.builtins)
 def test_dialog_readiness_cancellation_and_foreign_worker_never_touch_parent_state(self):
  p=types.SimpleNamespace(_closed=False,focus=1010,origin=123,category='saved');row=dict(sid='1',name='Station',kind='live')
  w=self.m.ProgrammeWindow46('XCMateProgramme46.xml',str(ADDON),'Default','720p');w.configure(self.portal,row,parent=p)
  w._shown=True;w._ready=True;w.event=None
  w.onAction(types.SimpleNamespace(getId=lambda:92));self.assertTrue(w._closed);self.assertEqual((p.focus,p.origin,p.category),(1010,123,'saved'));self.assertFalse(self.builtins)
 def test_own_window_xml_logo_is_top_left_overlay_and_has_no_extra_focus_target(self):
  import xml.etree.ElementTree as ET
  tree=ET.parse(ADDON/'resources/skins/Default/720p/XCMateProgramme46.xml');nodes={n.get('id'):n for n in tree.iter('control') if n.get('id')}
  self.assertEqual([n.get('id') for n in tree.iter('control') if n.get('type')=='button'],['501'])
  self.assertGreater(int(nodes['111'].findtext('left')),int(nodes['110'].findtext('left')));self.assertLess(int(nodes['111'].findtext('top')),int(nodes['110'].findtext('top'))+100);self.assertEqual(nodes['111'].findtext('aspectratio'),'keep')
 def test_gui_thread_ownership_is_enforced(self):
  w=self.m.ProgrammeWindow46('XCMateProgramme46.xml',str(ADDON),'Default','720p');w.configure(self.portal,dict(sid='1',name='Station'));w._owner=-1
  with self.assertRaisesRegex(RuntimeError,'OWNER_THREAD'):w.pump()

 def test_standalone_info_waits_for_natural_modal_release_without_home_navigation(self):
  import contextlib
  row=dict(sid='1',name='Station')
  with mock.patch('window_navigation.ownership',return_value=contextlib.nullcontext(True)),mock.patch.object(self.m,'permitted',side_effect=[False,True]),mock.patch.object(self.m,'show',return_value='shown') as show:
   self.assertEqual(self.m.launch_standalone(self.portal,row),'shown');show.assert_called_once()
  self.assertFalse(self.builtins)
 def test_duplicate_standalone_owner_and_persistent_foreign_dialog_are_refused(self):
  import contextlib
  row=dict(sid='1',name='Station')
  with mock.patch('window_navigation.ownership',return_value=contextlib.nullcontext(False)),mock.patch.object(self.m,'show') as show:self.m.launch_standalone(self.portal,row);show.assert_not_called()
  with mock.patch('window_navigation.ownership',return_value=contextlib.nullcontext(True)),mock.patch.object(self.m,'permitted',return_value=False),mock.patch.object(self.m.time,'monotonic',side_effect=[0,3]),mock.patch.object(self.m,'show') as show:self.m.launch_standalone(self.portal,row);show.assert_not_called()
  self.assertFalse(self.builtins)
