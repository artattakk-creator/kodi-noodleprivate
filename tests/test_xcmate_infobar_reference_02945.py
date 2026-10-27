"""Measure reference layout and real existing stream fields; Android visual NT."""
import importlib,sys,time,types,unittest
from pathlib import Path
from unittest import mock
import test_xcmate_kodi21_overlay as model
from xcmate027_fixture import Fixture

class ReferenceInfo45(unittest.TestCase):
 def setUp(self):
  self.case=model.OverlayLifecycleTests(methodName='runTest');self.case.setUp();self.addCleanup(self.case.doCleanups)
  self.o=self.case.overlay;self.m=importlib.import_module('infobar45')
  patch=mock.patch.object(sys.modules['utils'],'setting',side_effect=lambda key,default='':'de_de' if key=='xcmate_ui_language' else default);patch.start();self.addCleanup(patch.stop)
 def test_reference_panel_and_three_columns_match_measured_1080_geometry(self):
  g=self.m.layout(1920,1080)
  self.assertEqual(g['panel'],(26,670,1868,362));self.assertEqual(g['logo'],(78,720,208,138));self.assertEqual(g['left_sep'],(338,715,2,270));self.assertEqual(g['right_sep'],(1410,715,2,270))
  self.assertEqual(g['now'],(534,774,838,80));self.assertEqual(g['track'],(477,880,796,16))
 def test_720_geometry_scales_without_clipping_or_text_column_overlap(self):
  for w,h in [(1280,720),(1920,1080),(960,640)]:
   g=self.m.layout(w,h);px,py,pw,ph=g['panel']
   for key in ['logo','name','date','clock','previous','now','start','end','track','next','next_time']:
    x,y,ww,hh=g[key];self.assertGreaterEqual(x,px);self.assertGreaterEqual(y,py);self.assertLessEqual(x+ww,px+pw);self.assertLessEqual(y+hh,py+ph)
   self.assertLessEqual(g['now'][0]+g['now'][2],g['right_sep'][0]);self.assertLessEqual(g['date'][0]+g['date'][2],g['left_sep'][0])
 def test_all_six_reference_cells_use_actual_resolution_codec_audio_language_subtitles_fps(self):
  x=self.m.values(dict(width='1920',height='1080',video='h264',audio='ac3',channels='5.1',language='deu',subtitle_enabled=False,fps='25'))
  self.assertEqual(x,dict(video='1920 × 1080',codec='H.264',audio='AC3 5.1',language='Deutsch',subtitle='UT Aus',fps='25 fps'))
 def test_unknown_metadata_and_track_change_never_infer_quality_dolby_language(self):
  self.assertTrue(all(not v for v in self.m.values({}).values()))
  x=self.m.values(dict(audio='eac3',channels='2.0',language='und'))
  self.assertNotIn('Atmos',str(x));self.assertEqual(x['language'],'und');self.assertEqual(x['video'],'')
  tech=self.o._micro44;tech.render(dict(audio='aac',channels='2.0',language='eng'));self.assertEqual(tech.text['language'].label,'Englisch')
  tech.render({});self.assertTrue(all(not c.visible for c in tech.controls));self.assertTrue(all(not c.label for c in tech.text.values()))
 def test_registered_skin_fonts_are_selected_by_declared_sizes(self):
  raw=b'<fonts><fontset><font><name>real-18</name><size>18</size></font><font><name>real-bold-25</name><size>25</size><style>bold</style></font><font><name>real-bold-60</name><size>60</size><style>bold</style></font></fontset></fonts>'
  vfs=types.SimpleNamespace(exists=lambda _:True,File=lambda _:types.SimpleNamespace(readBytes=lambda n:raw,close=lambda:None))
  with mock.patch.dict(sys.modules,xbmcvfs=vfs):
   f=self.m.fonts(1);self.assertEqual(f['title'],'real-bold-60');self.assertEqual(f['value'],'real-bold-25');self.assertEqual(f['caption'],'real-18')
 def test_unchanged_technology_snapshot_has_no_repeated_setters(self):
  tech=self.o._micro44;data=dict(width='1920',height='1080',audio='aac',channels='2.0');tech.render(data)
  with mock.patch.object(tech.text['video'],'setLabel',side_effect=AssertionError('unchanged setter')):
   for _ in range(200):tech.render(data)
 def test_reference_now_next_progress_and_clock_fields_are_dynamic(self):
  bar=self.o._infobar45;info=dict(previous='Previous real title',now='Current real title',next='Following real title',now_time='20:15',now_end_time='21:00',next_time='21:00',next_end_time='22:00',progress=.5)
  bar.render('Actual channel','/local/logo.png',info,{},'Actual local date','20:36')
  self.assertEqual(bar.previous.label,'VORHER:  Previous real title');self.assertEqual(bar.now.label,'Current real title');self.assertEqual(bar.next.label,'Following real title');self.assertEqual(bar.clock.label,'20:36')
  self.assertEqual(bar.progress.width,round(bar.g['track'][2]*.5));self.assertEqual(bar.next_time.label,'21:00 – 22:00')
 def test_clear_and_reopen_restores_now_next_badges_without_ghost_text(self):
  o=self.o;o._switch('info');self.assertEqual(o._infobar45.now_badge.label,'JETZT');o._switch('channels');o._switch('info')
  self.assertEqual(o._infobar45.now_badge.label,'JETZT');self.assertEqual(o._infobar45.next_badge.label,'DANACH');self.assertFalse(o.info_hint.visible);self.assertFalse(o.info_duration.visible)
 def test_first_second_ok_back_and_20_cycles_do_not_invoke_transport(self):
  o=self.o;o._switch('hidden')
  for _ in range(20):
   o.handle_command('ok');self.assertEqual(o.mode,'info');o.handle_command('ok');self.assertEqual(o.mode,'controls');self.assertTrue(all(not c.visible for c in o._micro44.controls))
   o.handle_command('back');self.assertEqual(o.mode,'info');o.handle_command('back');self.assertEqual(o.mode,'hidden')
  self.case.player.stop.assert_not_called();self.case.player.play.assert_not_called();self.case.player.pause.assert_not_called()
 def test_existing_owner_throttled_stream_reader_remains_single_acquisition(self):
  self.o._stream_details.read=mock.Mock(return_value={});self.o._render_info();self.o._stream_details.read.assert_called_once()
  self.assertFalse(self.o.info_hint.visible);self.case.client.get_short_epg.assert_not_called();self.case.client._get_json.assert_not_called()

class PreviousEPG45(Fixture,unittest.TestCase):
 def setUp(self):super().setUp();self.g=importlib.import_module('guide_store');self.m=importlib.import_module('infobar_epg45');self.local=importlib.import_module('local_epg')
 def test_previous_event_from_same_published_revision_is_readonly(self):
  events=[dict(name='Before',start_timestamp=self.now-1800,stop_timestamp=self.now-1),dict(name='Now',start_timestamp=self.now,stop_timestamp=self.now+1800)]
  self.g.import_cache('p',{'xml':events},revision='actual')
  channel=dict(sid='1',epg_channel_id='xml');view=self.local.window('p',[channel],{},self.now,self.now+3600)
  before=Path(self.g.path()).read_bytes();self.assertEqual(self.m.previous('p',channel,{},self.now,view.revision),'Before');self.assertEqual(Path(self.g.path()).read_bytes(),before)
 def test_revision_change_or_no_real_history_never_fabricates_previous_title(self):
  self.g.import_cache('p',{'xml':[dict(name='Only current',start_timestamp=self.now,stop_timestamp=self.now+1800)]},revision='actual')
  channel=dict(sid='1',epg_channel_id='xml');view=self.local.window('p',[channel],{},self.now,self.now+3600)
  self.assertEqual(self.m.previous('p',channel,{},self.now,view.revision),'');self.assertEqual(self.m.previous('p',channel,{},self.now,('old',0)),'')
 def test_previous_event_honors_manual_mapping_before_provider_alias(self):
  self.g.import_cache('p',{'wrong':[dict(name='Wrong',start_timestamp=self.now-100,stop_timestamp=self.now-1)],'right':[dict(name='Chosen',start_timestamp=self.now-100,stop_timestamp=self.now-1)]},revision='actual')
  channel=dict(sid='1',epg_channel_id='wrong');view=self.local.window('p',[channel],{'1':'right'},self.now,self.now+3600)
  self.assertEqual(self.m.previous('p',channel,{'1':'right'},self.now,view.revision),'Chosen')
