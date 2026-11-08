"""Home widget actions finish only their own directory before opening detail."""
import importlib,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture

class PlayNavigation80(Fixture,unittest.TestCase):
 def anchor(self,dialog):
  navigation=importlib.import_module('window_navigation')
  router=types.SimpleNamespace(_handle=7,url=lambda **k:'plugin://plugin.video.xtreammate/?action=xcmate_home')
  state={'dialog':dialog}
  def finish(*a,**k):state['dialog']=9999
  with mock.patch('xbmcgui.getCurrentWindowId',return_value=10000),mock.patch('xbmcgui.getCurrentWindowDialogId',side_effect=lambda:state['dialog']),mock.patch('xbmc.getInfoLabel',return_value=''),mock.patch('boot_diagnostics.finish_directory',side_effect=finish) as done,mock.patch('home_menu.show'),mock.patch('xbmc.executebuiltin') as command,mock.patch('xbmc.Monitor',return_value=types.SimpleNamespace(waitForAbort=lambda n:True)):
   result=navigation._anchor_home(router,self.portal,'a'*32)
  return result,done,command
 def test_positive_widget_handle_releases_own_busy_without_directory_navigation(self):
  result,done,command=self.anchor(10138);self.assertTrue(result);done.assert_called_once();command.assert_not_called()
 def test_foreign_modal_is_not_closed_or_navigated_around(self):
  result,done,command=self.anchor(10100);self.assertFalse(result);done.assert_not_called();command.assert_not_called()

 def test_changed_flag_does_not_short_circuit_actual_consumer_preparation(self):
  import home_activation78 as activation
  activation.request('a'*32,consumers_changed=True)
  with mock.patch('xbmc.getCondVisibility',return_value=False),mock.patch('widget_reload78.repair',return_value=True) as repair,mock.patch('widget_hooks45.prepare'):
   activation.prepare()
  repair.assert_called_once()
