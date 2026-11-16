"""Real dispatch function integration, no device/renderer claims."""
import ast,importlib,unittest
from types import SimpleNamespace
from unittest import mock
from xcmate027_fixture import Fixture,LIB

class Integration96(Fixture,unittest.TestCase):
 def test_mini_long_ok_is_consumed_before_player_or_programme_action(self):
  tree=ast.parse((LIB/'live_overlay.py').read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='LiveNavigator');node=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='_handle_command')
  ns={};exec(compile(ast.Module(body=[node],type_ignores=[]),'real-handle96','exec'),ns)
  nav=SimpleNamespace(mode='channels',_mini=SimpleNamespace(command=mock.Mock(side_effect=AssertionError('must consume before Mini command'))))
  with mock.patch('guide_mapping48.request_mini',return_value=True) as request:
   ns['_handle_command'](nav,'long_ok')
  request.assert_called_once_with(nav)
 def test_manual_xmltv_search_stays_in_existing_worker_and_uses_current_event(self):
  import work_requests86 as worker
  event=dict(pid='p',sid='1',canonical='xml',start=self.now,stop=self.now+100,title='Show')
  nonce=worker.request(event,'search',source='xmltv_event',kind='event')
  with mock.patch('xmltv_art96.search',return_value=dict(code='ZERO_RESULTS',rows=[])) as search:
   worker.drain()
  self.assertEqual(worker.result(nonce)['code'],'ZERO_RESULTS');self.assertEqual(search.call_args[0][0]['canonical'],'xml')
