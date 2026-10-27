"""Selected-account resolution and actual Search→Detail→resolver entry paths."""
import importlib,sys,types,unittest,urllib.parse
from unittest import mock
from xcmate027_fixture import Fixture

class SearchPlay44(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.intent=importlib.import_module('media_intent');self.portal44=importlib.import_module('media_portal44')
    def params(self):
        nonce=self.intent.begin('p','vod','1');self.router._params=dict(action='media_play',pid='p',kind='vod',sid='1',intent=nonce,origin44='search');return nonce
    def test_requested_account_never_materializes_all_active_accounts(self):
        self.params()
        with mock.patch.object(sys.modules['portals'],'get_active',side_effect=MemoryError('must not copy all accounts')):
            self.assertEqual(self.routes.portal_for(self.router)['id'],'p')
    def test_temporary_profile_transaction_retry_is_once_and_intent_bound(self):
        from portal_snapshot import PortalReadError
        self.params()
        with mock.patch.object(sys.modules['portals'],'get_by_id',side_effect=[PortalReadError(reason='PROFILE_BUSY'),self.portal]) as get,mock.patch.object(self.portal44.time,'sleep') as wait:
            self.assertEqual(self.portal44.selected(self.router)['id'],'p');self.assertEqual(get.call_count,2);wait.assert_called_once_with(.03)
    def test_cancelled_intent_cannot_retry_or_resolve_after_profile_race(self):
        from portal_snapshot import PortalReadError
        nonce=self.params();self.intent.cancel('p',nonce)
        with mock.patch.object(sys.modules['portals'],'get_by_id',side_effect=PortalReadError(reason='PROFILE_RACE')) as get,mock.patch.object(self.portal44.time,'sleep') as wait:
            self.routes.dispatch(self.router);self.assertEqual(get.call_count,1);wait.assert_not_called()
        sys.modules['xbmcplugin'].setResolvedUrl.assert_called_once();self.assertFalse(sys.modules['xbmcplugin'].setResolvedUrl.call_args.args[1])
    def test_memory_or_invalid_profile_is_not_blindly_retried_and_returns_control(self):
        from portal_snapshot import PortalReadError
        for reason in ('MEMORY','MEMORY_PAUSE','INVALID_PROFILE','PROFILE_BUDGET'):
            nonce=self.params();sys.modules['xbmcplugin'].setResolvedUrl.reset_mock()
            with mock.patch.object(sys.modules['portals'],'get_by_id',side_effect=PortalReadError('https://private.invalid/SECRET',reason=reason)) as get,mock.patch.object(self.portal44.time,'sleep') as wait:
                self.routes.dispatch(self.router);self.assertEqual(get.call_count,1);wait.assert_not_called()
            self.assertTrue(self.intent.failure(nonce,'p'));self.assertFalse(sys.modules['xbmcplugin'].setResolvedUrl.call_args.args[1])
    def test_missing_or_disabled_requested_account_never_falls_back_to_another(self):
        self.params();self.portals.append(dict(self.portal,id='other'));self.portal['enabled']=False
        self.assertIsNone(self.routes.portal_for(self.router));self.router._params['pid']='missing';self.assertIsNone(self.routes.portal_for(self.router))
    def test_fixed_reason_and_origin_logs_never_include_private_ids_or_errors(self):
        with mock.patch.object(sys.modules['xbmc'],'log',create=True) as log,mock.patch.object(sys.modules['xbmc'],'LOGINFO',1,create=True):
            self.portal44.trace('PORTAL_READ','MEMORY','search');self.portal44.trace('PORTAL_READ','https://private.invalid/SECRET','foreign-account')
        text=str(log.call_args_list);self.assertIn('reason=MEMORY',text);self.assertIn('origin=other',text)
        for secret in ('SECRET','private.invalid','foreign-account'):self.assertNotIn(secret,text)
    def search_detail(self,kind):
        w=self.media_window();w._open_search('House');self.settle(w)
        w._search_click(701 if kind=='vod' else 702);self.settle(w)
        w.setFocusId(710);w._search_click(710);self.settle(w)
        self.assertEqual(w.mode,'detail');self.assertTrue(w._search_detail);return w
    def resolve(self,w,item,kind):
        before=len(self.builtins);w._play(item,kind);w._play(item,kind)
        commands=self.builtins[before:];self.assertEqual(len(commands),1)
        params=dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(commands[0][len('PlayMedia('):-1]).query))
        self.assertEqual(params['origin44'],'search');self.assertEqual(params['sid'],item['sid']);self.router._params=params
        player=importlib.import_module('player')
        playable=types.SimpleNamespace(getVideoInfoTag=lambda:types.SimpleNamespace(setUniqueIDs=lambda ids:None))
        with mock.patch.object(player,'build_playable_item',return_value=playable):self.routes.dispatch(self.router)
        self.assertTrue(sys.modules['xbmcplugin'].setResolvedUrl.call_args.args[1]);self.assertFalse(self.intent.allowed(params['intent'],'p',kind,item['sid']))
    def test_movie_search_result_reaches_exact_valid_resolver_once(self):
        w=self.search_detail('vod');self.resolve(w,w.selected,'vod');self.assertEqual(w._search_query,'House')
    def test_series_search_episode_reaches_exact_valid_resolver_once(self):
        w=self.search_detail('series');self.assertTrue(w.episodes);self.resolve(w,w.episodes[0],'episode');self.assertEqual(w._search_query,'House')
