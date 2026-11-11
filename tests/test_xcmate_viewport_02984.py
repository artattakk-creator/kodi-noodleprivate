"""Five-image producer boundary, exact queue dedupe, guarded current skin."""
import importlib,json,time,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture

class Viewport84(Fixture,unittest.TestCase):
 def test_home_initial_five_scroll_right_one_new_job_and_back_no_duplicate(self):
  work=importlib.import_module('programme_prefetch48')
  from importlib import util
  spec=util.spec_from_file_location('real_queue84',Path(__file__).parents[1]/'src/plugin.video.xtreammate/resources/lib/programme_urls55.py');q=util.module_from_spec(spec);spec.loader.exec_module(q)
  q._thread=mock.Mock();q._thread.is_alive.return_value=True
  rows=[dict(sid=str(i),name='Synthetic '+str(i)) for i in range(8)];focus={'sid':'0','left':0}
  def event(portal,row,info):return dict(pid=portal['id'],sid=row['sid'],key='event-'+row['sid'],title='Synthetic',start=self.now-10,stop=self.now+1000,placeholder='/not-a-real-picture')
  with mock.patch('programme_urls55.enqueue',new=q.enqueue),mock.patch('home_schedule75.applicable',return_value=True),mock.patch('home_schedule75.rest_allowed',return_value=True),mock.patch('home_schedule75.visible_position',side_effect=lambda *a:focus['left']),mock.patch('hero_epg63.focused64',side_effect=lambda *a:focus['sid']),mock.patch('epg_coverage66.warm'),mock.patch('local_epg.now_next',return_value={}),mock.patch('programme_events46.from_info',side_effect=event),mock.patch('programme_index46.publish'),mock.patch('epg_snapshot75.checkpoint'):
   work.prepare(self.portal,rows);self.assertEqual(set(q._queue),{'event-'+str(i) for i in range(5)})
   focus.update(sid='5',left=1);work._next.clear();work.prepare(self.portal,rows)
   self.assertEqual(set(q._queue),{'event-'+str(i) for i in range(6)})
   focus.update(sid='0',left=0);work._next.clear();work.prepare(self.portal,rows)
   self.assertEqual(len(q._queue),6);self.assertEqual(next(iter(q._queue)),'event-0')
   self.assertLessEqual(len(q._pending),24)
 def test_pressure_flush_never_retries_optional_sqlite_write_on_each_poll(self):
  import programme_session69
  with mock.patch('artwork_display84.metadata_allowed',return_value=False),mock.patch('programme_writes69.permit',side_effect=AssertionError('optional persist retried')):
   for _ in range(100):self.assertFalse(programme_session69.flush())
 def test_kodi_abort_stops_existing_artwork_and_programme_worker_loops(self):
  import types
  with mock.patch('xbmc.Monitor',return_value=types.SimpleNamespace(abortRequested=lambda:True)),mock.patch('programme_transport77.verified',side_effect=AssertionError('fetch after abort')):
   importlib.import_module('widget_assets69')._run()
   importlib.import_module('programme_urls55')._run()
 def test_readonly_inventory_counts_only_files_without_following_links(self):
  from artwork_inventory84 import measure
  target=self.folder/'media_art_v1';target.mkdir();(target/'one.img').write_bytes(b'12345')
  external=self.folder/'unrelated';external.mkdir();(external/'never.img').write_bytes(b'x'*500)
  (target/'link').symlink_to(external,target_is_directory=True)
  with mock.patch('xbmcvfs.translatePath',return_value=str(self.folder/'TexturesAbsent')):
   value=measure()
  self.assertEqual(value['xcmate_media'],dict(bytes=5,files=1,code='COMPLETE'))
  self.assertEqual((external/'never.img').stat().st_size,500)

class Layout84(unittest.TestCase):
 def test_current_adapter_has_large_contained_hero_safe_table_and_reachable_rails(self):
  from test_xcmate_skin_02978 import Skin78
  h=Skin78(methodName='runTest');h.setUp();self.addCleanup(h.doCleanups)
  before=h.prop.read_bytes();new=h.m.build(h.original);self.assertEqual(h.m.build(new),new)
  r=h.m.parse(new['xml/IncludesHomeWidgets.xml']);hero=r.find(".//control[@id='296751']")
  self.assertEqual((hero.findtext('height'),hero.findtext('width'),hero.findtext('aspectratio')),('620','1760','scale'))
  panel=r.find(".//control[@id='296750']")
  title=panel.find("control[@id='296781']");description=panel.find("control[@id='296782']")
  self.assertLessEqual(int(title.findtext('top'))+int(title.findtext('height')),174)
  self.assertLessEqual(int(description.findtext('top'))+int(description.findtext('height')),552)
  rail=h.m.parse(new['xml/IncludesHomeBingie.xml']).find(".//control[@id='77777']")
  self.assertEqual((rail.findtext('top'),rail.findtext('height')),('640','420'))
  self.assertLess(640+80+244,1080);self.assertEqual(h.prop.read_bytes(),before)
 def test_changed_own_hero_rejected_no_silent_skin_overwrite(self):
  from test_xcmate_skin_02978 import Skin78
  h=Skin78(methodName='runTest');h.setUp();self.addCleanup(h.doCleanups)
  import widget_skin84
  with mock.patch.object(widget_skin84,'upgrade',side_effect=lambda x:dict(x)):old=h.m.build(h.original)
  old['xml/IncludesHomeWidgets.xml']=old['xml/IncludesHomeWidgets.xml'].replace(b'<height>400</height>',b'<height>399</height>',1)
  with self.assertRaises(ValueError):widget_skin84.upgrade(old)
