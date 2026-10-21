"""Issue #12: own-stream admission, durable diagnosis, service-owned EPG jobs.

Synthetic data only. These tests do not prove Android focus or metadata transfer.
"""
import ast
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import types
import unittest
from unittest import mock

LIB=Path(__file__).resolve().parents[1]/'src/plugin.video.xtreammate/resources/lib'


def module(name,file):
    spec=importlib.util.spec_from_file_location(name,LIB/file)
    result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.r=module('issue12_recovery','live_recovery.py')
        self.portal=dict(id='p',type='xtream',enabled=True,start_stream_id='17')
        self.client=types.SimpleNamespace(
            get_cached_catalog=lambda _:[{'stream_id':17}],
            live_stream_url=lambda sid,ext:f'https://provider.invalid/live/user/password/{sid}.{ext}')
        self.factory=lambda *args:self.client
        self.portal.update(xc_host='https://provider.invalid',xc_user='user',xc_pass='password')
        self.session=dict(pid='p',sid='17',nonce='opaque',at=time.time())
        self.tag={}
        self.player=types.SimpleNamespace(isPlayingVideo=lambda:True,
            getPlayingFile=lambda:'https://redirect.invalid/opaque/output.unknown',
            getVideoInfoTag=lambda:types.SimpleNamespace(getUniqueID=lambda _:json.dumps(self.tag)))

    def test_equivalent_encoding_host_case_and_default_port_match(self):
        path='https://PROVIDER.invalid:443/live/%75ser/p%61ssword/%31%37.ts|User-Agent=Kodi'
        self.assertEqual(self.r.recover_from_player_path(path,[self.portal],self.factory),('p','17'))

    def test_new_query_token_different_origin_and_encoded_path_boundaries_fail(self):
        for path in ['https://other.invalid/live/user/password/17.ts',
                     'https://provider.invalid/live/user/password/17.ts?token=new',
                     'https://provider.invalid/live/user%2Fother/password/17.ts']:
            self.assertIsNone(self.r.recover_from_player_path(path,[self.portal],self.factory))

    def test_redirect_requires_current_matching_item_session(self):
        self.assertEqual(self.r.playback_match(self.player,[self.portal],self.factory,self.session),
                         (None,'URL_NOT_VERIFIED'))
        self.tag=dict(self.session)
        self.assertEqual(self.r.playback_match(self.player,[self.portal],self.factory,self.session),
                         (('p','17'),'ITEM_IDENTITY'))
        self.tag['nonce']='older-item'
        self.assertIsNone(self.r.playback_match(self.player,[self.portal],self.factory,self.session)[0])

    def test_disabled_portal_expired_identity_and_foreign_metadata_fail(self):
        self.tag=dict(self.session)
        self.portal['enabled']=False
        self.assertIsNone(self.r.playback_match(self.player,[self.portal],self.factory,self.session)[0])
        self.portal['enabled']=True
        self.session['at']=self.tag['at']=time.time()-90000
        self.assertIsNone(self.r.playback_match(self.player,[self.portal],self.factory,self.session)[0])
        self.tag['at']='not-a-time'
        self.session['at']='not-a-time'
        self.assertIsNone(self.r.playback_match(self.player,[self.portal],self.factory,self.session)[0])

    def test_tag_only_copies_runtime_identity_not_names_or_urls(self):
        saved={}
        item=types.SimpleNamespace(getVideoInfoTag=lambda:types.SimpleNamespace(setUniqueIDs=saved.update))
        self.assertTrue(self.r.tag_live_item(item,dict(self.session,name='private-name',url='secret-url')))
        tag=json.loads(saved['xcmate_live'])
        self.assertEqual(set(tag),{'pid','sid','nonce','at'})
        self.assertFalse(self.r.tag_live_item(object(),self.session))

    def test_disabled_or_ambiguous_url_only_portals_are_never_admitted(self):
        path=self.client.live_stream_url('17','ts')
        self.portal['enabled']=False
        self.assertIsNone(self.r.recover_from_player_path(path,[self.portal],self.factory))
        self.portal['enabled']=True
        other=dict(self.portal,id='duplicate')
        self.assertIsNone(self.r.recover_from_player_path(path,[self.portal,other],self.factory))

    def test_regular_play_infers_missing_session_ids_from_verified_source(self):
        tree=ast.parse((LIB/'main.py').read_text())
        router=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Router')
        method=next(n for n in router.body if isinstance(n,ast.FunctionDef) and n.name=='_play_live')
        namespace=dict(error=lambda *a:None,notify=lambda *a:None)
        exec(compile(ast.Module(body=[method],type_ignores=[]),'play_live','exec'),namespace)
        announced=[]
        live=types.ModuleType('live_overlay')
        live.announce=lambda *args:announced.append(args) or self.session
        portals=types.ModuleType('portals')
        portals.get_active=lambda:[self.portal]
        xtream=types.ModuleType('xtream')
        xtream.XtreamClient=self.factory
        player=types.ModuleType('player')
        player.play_stream=mock.Mock()
        with mock.patch.dict(sys.modules,dict(portals=portals,xtream=xtream,live_overlay=live,
                                             live_recovery=self.r,player=player,
                                             play_intent=types.SimpleNamespace(before_play=lambda session:True))):
            namespace['_play_live'](types.SimpleNamespace(_params={
                'url':self.client.live_stream_url('17','ts'),'sid':'999'},_handle=1))
        self.assertEqual(announced[0][:2],('p','17'))
        self.assertEqual(player.play_stream.call_args.kwargs['live_session'],self.session)


class DiagnosticTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path=Path(temp.name)
        self.props={}
        utils=types.ModuleType('utils')
        utils.addon_data_dir=lambda:str(self.path)
        gui=types.ModuleType('xbmcgui')
        gui.Window=lambda _:types.SimpleNamespace(getProperty=lambda k:self.props.get(k,''),
                                                setProperty=self.props.__setitem__)
        patch=mock.patch.dict(sys.modules,dict(utils=utils,xbmcgui=gui))
        patch.start();self.addCleanup(patch.stop)
        self.d=module('issue12_diagnostics','live_diagnostics.py')

    def test_last_input_and_rejection_survive_stop_and_restart_without_secrets(self):
        self.d.record('session','ANNOUNCED',marker=True,url='https://credentials.invalid')
        self.d.record('ownership','URL_NOT_VERIFIED',marker=True,video=True,username='private')
        self.d.record('input','NATIVE_ACTION',action_id=7,count=1)
        self.d.record('input','NATIVE_ACTION',action_id=92,count=2)
        self.d.record('dialog','CLOSED',video=False)
        self.d.checkpoint()
        self.props.clear()
        restarted=module('issue12_restarted','live_diagnostics.py')
        self.assertEqual(restarted.snapshots()['input']['count'],2)
        self.assertEqual(restarted.snapshots()['ownership']['code'],'URL_NOT_VERIFIED')
        data=''.join(p.read_text() for p in self.path.glob('*.json'))
        self.assertNotIn('credentials',data)
        self.assertNotIn('username',data)
        self.assertNotIn('private',data)

    def test_epg_last_success_survives_failed_followup(self):
        self.d.record('epg','READY',last_success=1234,channels=5)
        self.d.record('epg','REFRESH_FAILED',running=False)
        self.props.clear()
        self.assertEqual(self.d.snapshots()['epg']['last_success'],1234)

    def test_input_callbacks_buffer_without_disk_io_then_preserve_transitions_on_restart(self):
        with mock.patch.object(self.d,'_disk',side_effect=AssertionError('input disk read')), \
             mock.patch.object(self.d,'_save',side_effect=AssertionError('input disk write')):
            for i in range(80):
                self.d.record('input','COMMAND_HANDLED',action_id=1,button_code=615,
                              input_source='native',command='left',mode_before='hidden',
                              mode_after='channels',focus_before=10,focus_id=20,count=i,
                              url='https://private.invalid/secret')
            self.assertEqual(len(self.d._INPUT_PENDING),64)
        self.d.flush_input()
        self.assertEqual(len(self.d._INPUT_PENDING),0)
        self.assertEqual(len(self.d._disk('input')),64)
        self.props.clear()
        restarted=module('issue12_input_restart','live_diagnostics.py')
        history=restarted._disk('input')
        self.assertEqual((history[0]['count'],history[-1]['count']),(16,79))
        text='\n'.join(restarted.report())
        for value in ('command=left','mode_before=hidden','mode_after=channels','focus_before=10'):
            self.assertIn(value,text)
        self.assertNotIn('private',text)
        self.assertNotIn('secret',text)

    def test_failed_input_flush_retains_bounded_events_for_retry(self):
        self.d.record('input','COMMAND_HANDLED',action_id=1)
        with mock.patch.object(self.d.os,'replace',side_effect=OSError('profile unwritable')):
            self.d.flush_input()
        self.assertEqual(len(self.d._INPUT_PENDING),1)
        self.d.flush_input()
        self.assertEqual(len(self.d._INPUT_PENDING),0)
        self.assertEqual(self.d._disk('input')[0]['action_id'],1)

    def test_failure_stage_and_class_survive_close_and_restart_without_exception_text(self):
        self.d.record('dialog','SHOW_FAILED',failure_stage='CONTROL_LIST',exception_class='TypeError',
                      message='https://private.invalid/password')
        self.d.record('dialog','CLOSED',video=False)
        self.d.record('epg','PROVIDER_LIMIT',failure_stage='PARSE',exception_class='XMLTVLimitError',
                      limit_kind='channels',limit_value=10000)
        self.d.record('epg','NO_NEW_GUIDE',running=False)
        self.props.clear()
        restarted=module('issue12_failure_restart','live_diagnostics.py')
        text='\n'.join(restarted.report())
        self.assertIn('exception_class=TypeError',text)
        self.assertIn('failure_stage=CONTROL_LIST',text)
        self.assertIn('limit_kind=channels',text)
        self.assertNotIn('private',text)
        self.assertNotIn('password',text)
        restarted.record('dialog','SHOW_FAILED',exception_class='https://private.invalid',
                         failure_stage='password')
        self.assertNotIn('private','\n'.join(restarted.report()))

    def test_history_is_bounded_and_invalid_external_values_are_ignored(self):
        for index in range(40): self.d.record('focus','STATE_'+str(index),focus_id=index)
        self.assertLessEqual(len(self.d._disk('focus')),16)
        self.d.record('session','https://secret.invalid',marker=True)
        self.assertNotIn('session',self.d.snapshots())


class ShortGuideJobs(unittest.TestCase):
    def setUp(self):
        self.m=module('issue12_views','epg_views.py')
        self.portal=dict(id='p',type='xtream',xc_host='host',xc_user='u',xc_pass='pw')
        self.view='plugin://plugin.video.xtreammate/?action=live_channels&pid=p'
        self.current=self.view
        self.props={}
        self.jobs=[]
        self.cached={}
        self.commands=[]
        now=int(time.time())
        self.guide={'epg_listings':[{'title':'News','start_timestamp':now-60,'stop_timestamp':now+600}]}
        self.client=types.SimpleNamespace(
            _get_json=lambda action,extra,**kw:self.cached.get(extra['stream_id']),
            get_short_epg=lambda sid,**kw:self.cached.setdefault(sid,self.guide))
        gui=types.ModuleType('xbmcgui')
        gui.Window=lambda _:types.SimpleNamespace(getProperty=lambda k:self.props.get(k,''),
                                                setProperty=self.props.__setitem__)
        xbmc=types.ModuleType('xbmc')
        xbmc.getInfoLabel=lambda _:self.current
        xbmc.getCondVisibility=lambda _:False
        xbmc.executebuiltin=self.commands.append
        portals=types.ModuleType('portals');portals.get_by_id=lambda _:self.portal
        xtream=types.ModuleType('xtream');xtream.XtreamClient=lambda *a:self.client
        patch=mock.patch.dict(sys.modules,dict(xbmc=xbmc,xbmcgui=gui,portals=portals,xtream=xtream))
        patch.start();self.addCleanup(patch.stop)
        real_thread=threading.Thread
        def thread(*args,**kw):
            if kw.get('name')=='XCMateShortGuide':
                return types.SimpleNamespace(start=lambda:self.jobs.append(kw['target']))
            return real_thread(*args,**kw)
        self.thread=mock.patch('threading.Thread',side_effect=thread)
        self.thread.start();self.addCleanup(self.thread.stop)

    def request(self):
        channels=[types.SimpleNamespace(extra={'stream_id':'17'})]
        self.m.prefetch_short_guides(self.portal,channels,view_path=self.view)

    def test_ui_only_enqueues_and_service_worker_refreshes_matching_page(self):
        self.request()
        self.assertEqual(self.jobs,[])
        self.assertEqual(self.cached,{})
        self.m.poll_short_guides()
        self.assertEqual(len(self.jobs),1)
        self.jobs.pop()()
        self.assertEqual(self.commands,['Container.Refresh'])
        self.assertEqual(self.m.cached_short_guide(self.client,'17')['now'],'News')

    def test_different_container_and_fullscreen_are_not_refreshed(self):
        self.request();self.m.poll_short_guides()
        self.current='plugin://another.addon/?action=live_channels&pid=p'
        self.jobs.pop()()
        self.assertEqual(self.commands,[])
        self.m._SHORT_SEEN.clear();self.cached.clear()
        self.current=self.view
        sys.modules['xbmc'].getCondVisibility=lambda _:True
        self.request();self.m.poll_short_guides();self.jobs.pop()()
        self.assertEqual(self.commands,[])

    def test_empty_download_does_not_trigger_an_endless_refresh_or_long_cooldown(self):
        self.client.get_short_epg=lambda *a,**kw:{}
        self.request();self.m.poll_short_guides();self.jobs.pop()()
        self.assertEqual(self.commands,[])
        self.assertNotIn(('p','17'),self.m._SHORT_SEEN)

    def test_completed_request_is_not_repeated(self):
        self.request();self.m.poll_short_guides();self.jobs.pop()()
        self.m.poll_short_guides()
        self.assertEqual(self.jobs,[])

    def test_corrupt_or_expired_request_is_ignored_without_blocking_service(self):
        for raw in ['not-json','[]',json.dumps({'nonce':'n','at':'bad'}),
                    json.dumps({'nonce':'n','at':time.time()-500,'pid':'p','sids':['17']})]:
            self.props['XtreamMate.ShortGuideRequest']=raw
            self.m.poll_short_guides()
        self.assertEqual(self.jobs,[])
        self.request();self.m.poll_short_guides()
        self.assertEqual(len(self.jobs),1)


class RefreshJobTests(unittest.TestCase):
    def test_manual_request_is_consumed_by_service_only_once(self):
        props={}
        gui=types.ModuleType('xbmcgui')
        gui.Window=lambda _:types.SimpleNamespace(getProperty=lambda k:props.get(k,''),setProperty=props.__setitem__)
        portals=types.ModuleType('portals')
        portals.get_by_id=lambda _:dict(id='p',enabled=True)
        # Only these functions are needed; run original definitions without a
        # fake HTTP implementation or bypassing the real queue semantics.
        tree=ast.parse((LIB/'epg.py').read_text())
        nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('request_refresh','poll_refresh_request')]
        started=[]
        ns=dict(json=json,time=time,_LAST_REFRESH_REQUEST='',diagnostic=lambda *a,**kw:None,
                warmup_async=lambda *a,**kw:started.append((a,kw)))
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'epg jobs','exec'),ns)
        with mock.patch.dict(sys.modules,dict(xbmcgui=gui,portals=portals)):
            ns['request_refresh']('p',{'id':'p'},force=True)
            self.assertEqual(started,[])
            ns['poll_refresh_request']();ns['poll_refresh_request']()
            self.assertEqual(len(started),1)
            self.assertTrue(started[0][1]['force'])


class PlayerContractTests(unittest.TestCase):
    def test_resolver_transfers_the_same_live_identity_to_its_listitem(self):
        r=module('issue12_tag_recovery','live_recovery.py')
        tree=ast.parse((LIB/'player.py').read_text())
        method=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='play_stream')
        tag={}
        item=types.SimpleNamespace(getVideoInfoTag=lambda:types.SimpleNamespace(setUniqueIDs=tag.update))
        resolved=[]
        ns=dict(error=lambda *a:None,info=lambda *a:None,
                build_playable_item=lambda *a,**kw:item,
                xbmcplugin=types.SimpleNamespace(setResolvedUrl=lambda *a:resolved.append(a)))
        exec(compile(ast.Module(body=[method],type_ignores=[]),'play_stream','exec'),ns)
        live=types.ModuleType('live_overlay');live.trace=lambda *a,**kw:None
        session=dict(pid='p',sid='17',nonce='current',at=time.time())
        with mock.patch.dict(sys.modules,dict(live_recovery=r,live_overlay=live)):
            ns['play_stream'](7,'https://provider.invalid/live/u/pw/17.ts',live_session=session)
        self.assertEqual(resolved,[(7,True,item)])
        self.assertEqual(json.loads(tag['xcmate_live']),session)


class SenderListIntegrationTests(unittest.TestCase):
    setUp=ShortGuideJobs.setUp

    def test_actual_sender_page_shows_now_next_after_service_owned_prefetch(self):
        import urllib.parse
        now=int(time.time())
        self.guide['epg_listings'].append(dict(title='Next',start_timestamp=now+600,stop_timestamp=now+1200))
        tree=ast.parse((LIB/'main.py').read_text())
        router=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Router')
        method=next(n for n in router.body if isinstance(n,ast.FunctionDef) and n.name=='_live_channels')
        items=[]
        class Item:
            def __init__(self,ch): self.label=ch.name
            def setLabel(self,label): self.label=label
            def setInfo(self,*args): pass
            def addContextMenuItems(self,*args): pass
        plugin=types.SimpleNamespace(setContent=lambda *a:None,setPluginCategory=lambda *a:None,
            addDirectoryItem=lambda handle,url,item,folder:items.append(item),
            addSortMethod=lambda *a:None,SORT_METHOD_NONE=0,endOfDirectory=lambda *a,**kw:None)
        ns=dict(time=time,setting_int=lambda key,default=0:50 if key=='items_per_page' else 0,
                xbmcplugin=plugin,apply_lang_sort=lambda values:values,_L=lambda *a:'Live',
                is_favourite=lambda _:False,_ICON_SETTINGS='')
        exec(compile(ast.Module(body=[method],type_ignores=[]),'actual sender page','exec'),ns)
        channel=types.SimpleNamespace(name='TV',group='A',tvg_id='station',
            extra={'stream_id':'17'},url='https://provider.invalid/live/u/pw/17.ts',
            logo='',catchup=False,catchup_days=0)
        player=types.ModuleType('player');player.channel_list_item=Item
        epg=types.ModuleType('epg');epg.load_cache=lambda _:{}
        sources=types.ModuleType('epg_sources');sources.configuration=lambda _:dict(mappings={})
        groups=types.ModuleType('group_selection');groups.filter_channels=lambda channels,pid:channels
        diag=module('sender_diag','live_diagnostics.py')
        view=types.SimpleNamespace(_portal=lambda:self.portal,_params={},_handle=7,
             _load_channels=lambda _:[channel],_xc=lambda _:self.client,
             url=lambda **kw:'plugin://plugin.video.xtreammate/?'+urllib.parse.urlencode(kw))
        with mock.patch.dict(sys.modules,dict(player=player,epg=epg,epg_sources=sources,
                group_selection=groups,epg_views=self.m,live_diagnostics=diag)):
            ns['_live_channels'](view)
            self.assertEqual(items[-1].label,'TV')
            self.assertEqual(self.jobs,[])
            self.m.poll_short_guides();self.jobs.pop()()
            self.assertEqual(self.commands,['Container.Refresh'])
            ns['_live_channels'](view)
            self.assertIn('News',items[-1].label)
            self.assertIn('Jetzt:',items[-1].label)
            self.assertIn('Danach: Next',items[-1].label)
            self.assertEqual(diag.snapshots()['epg_list']['matched'],1)


if __name__=='__main__':unittest.main()
