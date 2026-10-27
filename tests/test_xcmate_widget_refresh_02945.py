"""Real reload contract: native DirectoryProvider retained, no fake Python bind."""
import importlib,json,sys,time,types,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture

class NativeProvider:
 """Observe native re-fetch; Python wrappers cannot read/bind this provider."""
 def __init__(self,items):self.items=items;self.position=0;self.resets=0;self.refreshes=0
 def reset(self):raise AssertionError('Kodi ignores Python reset for a dynamic provider')
 def size(self):return 0 # Legacy API vecItems is empty for foreign native lists.
 def getListItem(self,i):raise IndexError('Native DirectoryProvider has no Python vecItems')

class WidgetRefresh45(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.w=importlib.import_module('widget_refresh45');self.i=importlib.import_module('widget_items45');self.h=importlib.import_module('widget_hooks45')
  self.w._next=0;self.w._seen={};self.w._last_code={}
 def row(self,sid='1',kind='vod',name='Film'):return dict(sid=sid,kind=kind,name=name,added_at=self.now,cover='',category_id='a')
 def frame(self,rows,kind='vod'):
  # Provider fetch will read the same real local catalogue, not test frame data.
  records=[dict(r,stream_id=r['sid'],series_id=r['sid'],added=self.now+len(rows)-i) for i,r in enumerate(rows)]
  self.index.import_group('p',kind,'a',records)
  import widget_data41
  fresh,code=widget_data41.snapshot(self.portal,kind,background=True)
  self.assertTrue(self.w.publish(self.portal,kind,fresh,code));return self.w.read('p',kind)
 def control(self,rows,kind='vod'):
  return NativeProvider([self.i.item(self.i.describe(self.portal,kind,r,{})) for r in rows])
 def home(self,control,kind='vod',hooks=None):
  action={'live':'widget_live_start_group','vod':'widget_recent_vod','series':'widget_recent_series'}[kind]
  hook='XCMate.Widget45.Reload.'+kind
  self.bindings={'bindings':[dict(pid='p',kind=kind,hooks=[hook] if hooks is None else hooks)]}
  def setp(key,value):
   self.properties[key]=value
   if key!=hook:return
   old=control.items[control.position].getProperty('XCMate.MediaId') if control.items else ''
   self.added.clear();self.router._params=dict(action=action,pid='p',xcmate_reload45=value);self.routes.dispatch(self.router)
   control.items=[li for _,li,_ in self.added];ids=[li.getProperty('XCMate.MediaId') for li in control.items]
   control.position=ids.index(old) if old in ids else 0;control.refreshes+=1
  window=types.SimpleNamespace(setProperty=setp,getControl=lambda _:(_ for _ in ()).throw(AssertionError('no native list access')))
  for target,attrs in [(sys.modules['xbmc'],dict(getSkinDir=lambda:'skin.titan.bingie.mod',getCondVisibility=lambda _:False)),(sys.modules['xbmcgui'],dict(getCurrentWindowId=lambda:10000,getCurrentWindowDialogId=lambda:0,Window=lambda _:window))]:
   for k,v in attrs.items():p=mock.patch.object(target,k,v,create=True);p.start();self.addCleanup(p.stop)
  p=mock.patch.object(self.h,'read',side_effect=lambda:self.bindings);p.start();self.addCleanup(p.stop)
 def test_existing_home_binding_updates_new_title_without_new_shortcut_or_root(self):
  old=[self.row('1'),self.row('2')];control=self.control(old);control.position=1;self.home(control);self.frame([self.row('3'),*old]);self.w.poll()
  self.assertEqual([x.getProperty('XCMate.MediaId') for x in control.items],['3','1','2']);self.assertEqual(control.position,2);self.assertEqual(control.refreshes,1);self.assertFalse(self.builtins)
 def test_identical_frame_never_resets_or_reassigns_items_or_focus(self):
  rows=[self.row()];control=self.control(rows);self.home(control);self.frame(rows);self.w.poll();before=list(control.items)
  for _ in range(20):self.w._next=0;self.w.poll()
  self.assertEqual(control.items,before);self.assertEqual(control.refreshes,1);self.assertEqual(control.position,0)
 def test_epg_and_art_delta_update_in_place_without_list_reset(self):
  control=self.control([self.row()]);self.home(control);self.frame([self.row(name='Corrected')]);self.w.poll()
  self.assertEqual(control.items[0].label,'Corrected');self.assertEqual(control.resets,0)
 def test_foreign_item_portal_or_url_prevents_entire_container_write(self):
  control=self.control([self.row()]);self.home(control);self.bindings['bindings'][0]['pid']='foreign';self.frame([self.row('2')]);self.w.poll()
  self.assertEqual(control.refreshes,0);self.assertEqual(control.items[0].getProperty('XCMate.MediaId'),'1')
 def test_only_verified_legacy_all_titles_footer_is_removed(self):
  self.router._params.update(action='widget_recent_vod');self.routes.dispatch(self.router)
  self.assertTrue(all(li.props.get('XCMate.WidgetKind41')=='vod' for _,li,_ in self.added));self.assertFalse(any('action=movies_home' in url for url,_,_ in self.added))
 def test_wrong_footer_is_not_mistaken_for_own_widget(self):
  from widget_hooks45 import sources
  text='<includes><content>plugin://foreign/?action=widget_recent_vod&amp;pid=p</content><content>plugin://plugin.video.xtreammate/?action=movies_home&amp;pid=p</content></includes>'
  self.assertEqual(sources(text),[])
 def test_failed_or_zero_worker_result_keeps_last_good_publication(self):
  self.frame([self.row()]);before=Path(self.w.path('p','vod')).read_bytes()
  self.assertFalse(self.w.publish(self.portal,'vod',[]));self.assertFalse(self.w.publish(self.portal,'vod',[self.row('2')],'BUDGET'));self.assertEqual(Path(self.w.path('p','vod')).read_bytes(),before)
 def test_new_interpreter_reads_atomic_published_frame(self):
  first=self.frame([self.row()]);spec=importlib.util.spec_from_file_location('separate_widget45',Path(self.w.__file__));other=importlib.util.module_from_spec(spec);spec.loader.exec_module(other)
  self.assertEqual(other.read('p','vod'),first);self.assertIsNone(other.read('other','vod'))
 def test_cancelled_foreign_modal_or_active_player_defers_gui_publication(self):
  control=self.control([self.row()]);self.home(control);self.frame([self.row('2')])
  with mock.patch.object(sys.modules['xbmcgui'],'getCurrentWindowDialogId',return_value=10138):self.w.poll()
  self.w._next=0
  with mock.patch.object(sys.modules['xbmc'],'getCondVisibility',return_value=True):self.w.poll()
  self.assertEqual(control.items[0].getProperty('XCMate.MediaId'),'1');self.assertEqual(control.refreshes,0)
 def test_three_existing_source_urls_have_only_real_title_tiles_and_exact_clicks(self):
  for action,kind in [('widget_live_start_group','live'),('widget_recent_vod','vod'),('widget_recent_series','series')]:
   self.added.clear();self.router._params['action']=action;self.routes.dispatch(self.router)
   self.assertTrue(self.added);self.assertTrue(all(li.props.get('XCMate.WidgetKind41')==kind for _,li,_ in self.added))
   for url,li,folder in self.added:self.assertEqual(url,li.props['XCMate.ClickTarget44']);self.assertIn('sid='+li.props['XCMate.MediaId'],url);self.assertFalse(folder)
 def test_live_publication_uses_actual_local_epg_and_guide_progress(self):
  guide=importlib.import_module('guide_store');guide.import_cache('p',{'xml':[dict(name='Actual news',start_timestamp=self.now-60,stop_timestamp=self.now+60)]})
  frame=self.frame([dict(self.row(kind='live'),epg_channel_id='xml')],kind='live');value=frame['items'][0]
  self.assertEqual(value['props']['XtreamMate.Now'],'Actual news');self.assertTrue(value['props']['XCMate.EpgPercent41']);self.assertIn('action=play_live',value['url'])
 def test_corrupt_oversized_or_expired_frame_is_not_published_to_home(self):
  path=Path(self.w.path('p','vod'))
  for data in ['{','x'*(self.w.MAX_BYTES+1),json.dumps(dict(pid='p',kind='vod',at=time.time()-601,items=[{}]))]:path.write_text(data);self.assertIsNone(self.w.read('p','vod'))
 def test_missing_existing_reload_hook_is_explicitly_blocked_without_faking_success(self):
  control=self.control([self.row()]);self.home(control,hooks=[]);self.frame([self.row('2')]);self.w.poll()
  self.assertFalse(control.refreshes);self.assertEqual(self.w._last_code['vod'][0],'BLOCKED_NO_RELOAD_HOOK');self.assertFalse(self.properties)
 def test_native_container_unsupported_python_wrapper_never_used(self):
  control=self.control([self.row()]);self.assertEqual(control.size(),0)
  with self.assertRaises(IndexError):control.getListItem(0)
  self.home(control);self.frame([self.row('2')]);self.w.poll();self.assertEqual(control.items[0].getProperty('XCMate.MediaId'),'2')
 def test_changed_publications_coalesce_and_rate_limit_existing_skin_hook(self):
  control=self.control([self.row()]);self.home(control);self.frame([self.row('2')]);self.w.poll();self.frame([self.row('3')]);self.w._next=0;self.w.poll();self.assertEqual(control.refreshes,1)
  for k,(sig,at) in list(self.w._seen.items()):self.w._seen[k]=(sig,at-61)
  self.w._next=0;self.w.poll();self.assertEqual(control.refreshes,2);self.assertEqual(control.items[0].getProperty('XCMate.MediaId'),'3')
