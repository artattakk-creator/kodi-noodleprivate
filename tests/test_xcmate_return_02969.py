"""Post-stop navigation safety without invoking any player transport."""
import copy,importlib,json,sys,time,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture
class Return69(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp()
  for name in ('live_return69','programme_lifecycle69'):sys.modules.pop(name,None)
  self.ret=importlib.import_module('live_return69')
  self.value=dict(session=dict(pid='p',sid='1',nonce='a'*32,at=time.time()),at=time.time(),phase='home',return_started69=10.,return_deadline69=18.,return_attempts69=0,return_stage69='BEGIN')
  self.snap=dict(window=10025,dialog=9999,modal=False,updating=False)
  self.clock=mock.patch('live_return69.time.monotonic',return_value=12.);self.clock.start();self.addCleanup(self.clock.stop)
  for target,kw in [('live_exit.state',dict(side_effect=lambda:self.value)),('live_exit._save',dict(side_effect=lambda v:setattr(self,'value',copy.deepcopy(v)))),('window_lifecycle.state',dict(side_effect=lambda:self.snap)),('window_lifecycle.lease',dict(return_value='')),('live_overlay.session_from_property',dict(return_value=None))]:
   p=mock.patch(target,**kw);p.start();self.addCleanup(p.stop)
 def test_complete_requires_usable_visible_home(self):
  self.assertTrue(self.ret.poll());self.assertEqual(self.value['return_stage69'],'COMPLETE');self.assertEqual(self.builtins,[])
 def test_post_stop_own_updating_directory_gets_one_recovery_request(self):
  self.current_folder='plugin://plugin.video.xtreammate/?action=guide_grid&pid=p';self.snap['updating']=True
  self.ret.poll();self.ret.poll()
  self.assertEqual(len(self.builtins),1);self.assertIn('action=xcmate_home',self.builtins[0]);self.assertIn('entry=return',self.builtins[0])
 def test_foreign_modal_is_not_closed_or_bypassed(self):
  self.snap.update(dialog=10103,modal=True)
  self.ret.poll();self.assertEqual(self.builtins,[])
  with mock.patch('live_return69.time.monotonic',return_value=19.):self.ret.poll()
  self.assertEqual(self.value['return_stage69'],'FAILED');self.assertEqual(self.builtins,[])
 def test_foreign_updating_directory_is_retained(self):
  self.current_folder='plugin://plugin.video.somebody/?action=home';self.snap['updating']=True
  self.ret.poll();self.assertEqual(self.builtins,[])
 def test_new_foreign_playback_aborts_navigation(self):
  with mock.patch('xbmc.Player',return_value=types.SimpleNamespace(isPlaying=lambda:True,isPlayingVideo=lambda:True)):self.ret.poll()
  self.assertEqual(self.value['return_stage69'],'FAILED');self.assertEqual(self.builtins,[])
 def test_new_session_aborts_old_return(self):
  with mock.patch('live_overlay.session_from_property',return_value=dict(nonce='b'*32)):self.ret.poll()
  self.assertEqual(self.value['return_stage69'],'FAILED');self.assertEqual(self.builtins,[])
 def test_recovery_is_bounded_by_attempts_and_deadline(self):
  self.current_folder='plugin://plugin.video.xtreammate/?action=guide_grid&pid=p'
  self.ret.poll();self.current_folder='plugin://plugin.video.xtreammate/?action=guide_grid&pid=p'
  with mock.patch('live_return69.time.monotonic',return_value=15.1):self.ret.poll()
  self.current_folder='plugin://plugin.video.xtreammate/?action=guide_grid&pid=p'
  with mock.patch('live_return69.time.monotonic',return_value=19.):self.ret.poll()
  self.assertEqual(len(self.builtins),2);self.assertEqual(self.value['return_stage69'],'FAILED')
 def test_foreign_window_is_not_replaced(self):
  self.snap['window']=10001;self.ret.poll()
  self.assertEqual(self.builtins,[]);self.assertEqual(self.value['return_stage69'],'FAILED')
 def test_registry_cancels_exact_own_detail_only(self):
  from programme_lifecycle69 import register,cancel_matching,pulse
  view=types.SimpleNamespace(portal=self.portal,_native_owner='c'*32,setProperty=lambda k,v:self.properties.__setitem__(k,v),close=mock.Mock())
  with mock.patch('xbmcgui.getCurrentWindowDialogId',return_value=13001):register(view,'DETAIL')
  self.assertEqual(cancel_matching(self.value,dict(dialog=13001,window=10025)),1)
  self.assertTrue(pulse(view));view.close.assert_called_once()
 def test_registry_never_signals_foreign_owner_or_portal(self):
  from programme_lifecycle69 import register,cancel_matching
  view=types.SimpleNamespace(portal=self.portal,_native_owner='c'*32,setProperty=lambda k,v:self.properties.__setitem__(k,v))
  with mock.patch('xbmcgui.getCurrentWindowDialogId',return_value=13001):register(view,'DETAIL')
  self.properties['XCMate.NativeOwner']='d'*32
  self.assertEqual(cancel_matching(self.value,dict(dialog=13001,window=10025)),0)
 def test_native_detail_init_exception_is_observable(self):
  from programme_lifecycle69 import initialized
  view=types.SimpleNamespace(portal=self.portal,setProperty=lambda *a:None)
  def fail(v):raise RuntimeError('synthetic')
  initialized(fail)(view)
  self.assertTrue(view._shown);self.assertTrue(view._init_error69);self.assertFalse(view._ready)
