"""Real local EPG resolution and bounded snapshots; no Android acceptance claim."""
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import time
import types
import unittest
from unittest import mock

LIB=Path(__file__).resolve().parents[1]/'src/plugin.video.xtreammate/resources/lib'


def module(name,file):
    spec=importlib.util.spec_from_file_location(name,LIB/file)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class ProgrammeModelTests(unittest.TestCase):
    def setUp(self):
        self.v=module('tv025_views','epg_views.py')
        self.now=1792350000
        self.cache={'id':[dict(name='Now',start_timestamp=self.now-1800,stop_timestamp=self.now+1800),
                          dict(name='Next',start_timestamp=self.now+1800,stop_timestamp=self.now+3600)]}

    def test_real_interval_progress_elapsed_remaining_and_next_boundaries(self):
        info=self.v.guide_for_channel(self.cache,'id',now=self.now)
        self.assertEqual((info['now'],info['next']),('Now','Next'))
        self.assertEqual((info['elapsed'],info['remaining'],info['progress']),(1800,1800,.5))
        edge=self.v.guide_for_channel(self.cache,'id',now=self.now+1800)
        self.assertEqual(edge['now'],'Next')
        self.assertEqual(edge['progress'],0)
        self.assertEqual(edge['start'],self.now+1800)

    def test_manual_override_beats_stale_alias_provider_and_short_epg(self):
        cache=dict(self.cache, **{'7':[dict(name='Wrong',start_timestamp=self.now-1,stop_timestamp=self.now+2)]})
        client=types.SimpleNamespace(_get_json=mock.Mock(side_effect=AssertionError('must not use short EPG')))
        info=self.v.resolve_guide(cache,'7','7',self.now,client,{'7':'id'})
        self.assertEqual(info['now'],'Now')
        self.assertEqual(info['mapping'],'MANUAL')
        missing=self.v.resolve_guide(cache,'7','7',self.now,client,{'7':'absent'})
        self.assertEqual(missing['reason'],'MANUAL_ID_MISSING')
        self.assertIsNone(missing['progress'])

    def test_cached_short_epg_fallback_when_xmltv_has_only_future_data(self):
        import base64
        raw={'epg_listings':[dict(title=base64.b64encode(b'Short News').decode(),
            start_timestamp=str(self.now-60),duration_secs='1800')]}
        client=types.SimpleNamespace(_get_json=mock.Mock(return_value=raw))
        future={'id':[self.cache['id'][1]]}
        info=self.v.resolve_guide(future,'id','7',self.now,client)
        self.assertEqual(info['now'],'Short News')
        self.assertEqual(info['remaining'],1740)
        self.assertEqual(info['source_index'],-1)
        self.assertEqual(client._get_json.call_args_list,[
            mock.call('get_short_epg',extra={'stream_id':'7','limit':12},cached_only=True),
            mock.call('get_short_epg',extra={'stream_id':'7','limit':4},cached_only=True)])

    def test_invalid_zero_negative_reversed_and_overlapping_events_never_fake_progress(self):
        bad={'x':[dict(name='Bad',start_timestamp=0,stop_timestamp=0),
                  dict(name='Bad',start_timestamp='nan',stop_timestamp=self.now+10),
                  dict(name='Bad',start_timestamp=self.now+1,stop_timestamp=self.now-1)]}
        info=self.v.guide_for_channel(bad,'x',now=self.now)
        self.assertIsNone(info['progress'])
        self.assertEqual(info['now'],'')
        self.cache['id'].insert(1,dict(name='Overlap',start_timestamp=self.now+5,stop_timestamp=self.now+10))
        self.assertEqual(self.v.guide_for_channel(self.cache,'id',now=self.now)['next'],'Next')

    @unittest.skipUnless(hasattr(time,'tzset'),'POSIX timezone fixture')
    def test_local_time_midnight_and_dst_do_not_change_timestamp_progress(self):
        import datetime
        previous=os.environ.get('TZ')
        try:
            os.environ['TZ']='Europe/Berlin'
            time.tzset()
            start=int(datetime.datetime(2026,10,24,21,30,tzinfo=datetime.timezone.utc).timestamp())
            cache={'a':[dict(name='Night',start_timestamp=start,stop_timestamp=start+7200)]}
            info=self.v.guide_for_channel(cache,'a',now=start+3600)
            self.assertEqual((info['now_time'],info['now_end_time']),('23:30','01:30'))
            self.assertEqual(info['progress'],.5)
            dst=int(datetime.datetime(2026,10,25,0,30,tzinfo=datetime.timezone.utc).timestamp())
            cache['a'][0].update(start_timestamp=dst,stop_timestamp=dst+3600)
            info=self.v.guide_for_channel(cache,'a',now=dst+1800)
            self.assertEqual(info['progress'],.5)
        finally:
            if previous is None: os.environ.pop('TZ',None)
            else: os.environ['TZ']=previous
            time.tzset()


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        path_patch=mock.patch.object(sys,'path',[str(LIB)]+sys.path)
        path_patch.start();self.addCleanup(path_patch.stop)
        self.v=module('tv025_snapshot_views','epg_views.py')
        self.props={}
        self.cache={}
        self.config={'sources':[],'mappings':{}}
        self.rev=['one']
        epg=types.ModuleType('epg')
        epg.load_cache=mock.Mock(side_effect=lambda _:self.cache)
        epg._mem_clear=mock.Mock()
        sources=types.ModuleType('epg_sources')
        sources.configuration=lambda _:self.config
        status=types.ModuleType('epg_status')
        status.revision=lambda _:self.rev[0]
        gui=types.ModuleType('xbmcgui')
        gui.Window=lambda _:types.SimpleNamespace(setProperty=self.props.__setitem__)
        logos=types.ModuleType('logo_cache')
        logos.request=mock.Mock()
        patch=mock.patch.dict(sys.modules,dict(epg=epg,epg_sources=sources,epg_status=status,
            epg_views=self.v,xbmcgui=gui,logo_cache=logos,
            guide_store=types.SimpleNamespace(events=mock.Mock(return_value=([],0)))))
        patch.start();self.addCleanup(patch.stop)
        self.d=module('tv025_data','tv_data.py')
        self.client=types.SimpleNamespace(_get_json=mock.Mock(return_value={}))
        self.snapshot=self.d.GuideSnapshot(dict(id='p',type='xtream'),self.client)
        self.channel=types.SimpleNamespace(name='Station',tvg_id='id',logo='',
                                          extra={'stream_id':'7','category_id':'a'})

    def test_worker_prepares_then_gui_reads_only_ram_and_rolls_programme_boundary(self):
        now=time.time()
        self.cache={'id':[dict(name='Now',start_timestamp=now-60,stop_timestamp=now+60),
                          dict(name='Next',start_timestamp=now+60,stop_timestamp=now+600)]}
        self.snapshot.request([self.channel])
        self.snapshot.refresh()
        self.client._get_json.side_effect=AssertionError('I/O from GUI get')
        with mock.patch.object(sys.modules['epg'],'load_cache',side_effect=AssertionError('disk from GUI')):
            self.assertEqual(self.snapshot.get('7',now)['now'],'Now')
            self.assertEqual(self.snapshot.get('7',now+61)['now'],'Next')
        self.assertEqual(self.snapshot.get('7',now+600)['now'],'')

    def test_mapping_revision_invalidates_snapshot_and_service_request_is_queued_only(self):
        self.snapshot.request([self.channel])
        self.snapshot.refresh()
        self.assertNotIn('XtreamMate.ShortGuideRequest',self.props)  # .39 viewport is strictly local.
        self.assertTrue(all(c.kwargs.get('cached_only') for c in self.client._get_json.call_args_list))
        now=time.time()
        self.cache={'manual':[dict(name='Mapped',start_timestamp=now-60,stop_timestamp=now+60)]}
        self.config['mappings']={'7':'manual'}
        self.rev[0]='two'
        self.snapshot.refresh()
        self.assertEqual(self.snapshot.get('7')['now'],'Mapped')
        self.assertEqual(self.snapshot.get('7')['mapping'],'MANUAL')

    def test_snapshot_and_requests_are_bounded_for_large_catalog(self):
        channels=[types.SimpleNamespace(name=str(i),tvg_id='',logo='',
                  extra={'stream_id':str(i),'category_id':str(i%3)}) for i in range(53664)]
        index=self.d.CatalogIndex(channels)
        rows,positions=index.selection('*',{'1'})
        self.assertEqual(len(rows),17888)
        self.assertIs(index.selection('*',{'1'})[0],rows)
        self.assertEqual(rows[positions['4']].name,'4')
        for begin in range(0,160,16):
            self.snapshot.request(channels[begin:begin+30])
            self.snapshot.refresh()
        self.assertEqual(len(self.snapshot._wanted),16)
        self.assertLessEqual(len(self.snapshot._values),128)


class SourceStatusTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        utils=types.ModuleType('utils')
        utils.addon_data_dir=lambda:self.temp.name
        self.props={}
        gui=types.ModuleType('xbmcgui')
        gui.Window=lambda _:types.SimpleNamespace(setProperty=self.props.__setitem__,
            getProperty=lambda k:self.props.get(k,''))
        diagnostics=module('tv025_safe_diagnostics','live_diagnostics.py')
        patch=mock.patch.dict(sys.modules,dict(utils=utils,xbmcgui=gui,live_diagnostics=diagnostics))
        patch.start();self.addCleanup(patch.stop)
        self.status=module('tv025_source_status','epg_status.py')

    def test_per_portal_source_success_failure_restart_and_secret_filter(self):
        self.status.update('a','provider','READY',channels=2,programmes=4)
        success=self.status.read('a')['provider']['last_success']
        self.status.update('a','provider','GZIP_INVALID',failure_stage='PARSE',
                           exception_class='EOFError',uri='https://private.invalid/token')
        self.status.update('b','provider','EMPTY_GUIDE')
        other=module('tv025_restarted_status','epg_status.py')
        self.assertEqual(other.read('a')['provider']['last_success'],success)
        self.assertEqual(other.read('a')['provider']['failure_stage'],'PARSE')
        self.assertEqual(other.read('b')['provider']['code'],'EMPTY_GUIDE')
        raw=''.join(p.read_text() for p in Path(self.temp.name).glob('*.json'))
        self.assertNotIn('private',raw)
        self.assertNotIn('token',raw)

    def test_status_source_count_is_bounded(self):
        for n in range(140): self.status.update('a',str(n),'READY')
        self.assertEqual(len(self.status.read('a')),128)


class ProgrammePreviewTests(unittest.TestCase):
    def test_status_search_and_actual_programme_preview_never_download(self):
        views=module('preview025_views','epg_views.py')
        now=time.time()
        cache={'mapped':[dict(name='Live News',channel='mapped',start_timestamp=now-60,stop_timestamp=now+600),
                         dict(name='Next Show',channel='mapped',start_timestamp=now+600,stop_timestamp=now+1800)]}
        outputs=[]
        choices=iter([0,0,-1])
        class Dialog:
            def select(self,heading,list,autoclose=0,preselect=-1,useDetails=False):return next(choices)
            def input(self,heading,defaultt='',type=0,option=0,autoclose=0):return 'Station'
            def textviewer(self,heading,text,usemono=False):outputs.append(text)
        gui=types.ModuleType('xbmcgui');gui.Dialog=Dialog
        epg=types.ModuleType('epg')
        epg.load_cache=lambda _:cache
        epg.request_refresh=mock.Mock(side_effect=AssertionError('opening preview must not refresh'))
        sources=types.ModuleType('epg_sources')
        sources.configuration=lambda _:dict(sources=[],mappings={'7':'mapped'})
        status=types.ModuleType('epg_status')
        status.read=lambda _:{'provider':dict(code='DOWNLOAD_FAILED',failure_stage='DOWNLOAD',exception_class='OSError')}
        status.source_key=lambda _:'unused'
        client=types.SimpleNamespace(get_cached_catalog=lambda _:[dict(name='Station HD',stream_id=7,epg_channel_id='wrong')],
            _get_json=mock.Mock(side_effect=AssertionError('manual mapping wins')),
            get_short_epg=mock.Mock(side_effect=AssertionError('no HTTP')))
        xc=types.ModuleType('xtream');xc.XtreamClient=lambda *args:client
        groups=types.ModuleType('group_selection');groups.load=lambda _:None
        with mock.patch.dict(sys.modules,dict(epg_views=views,xbmcgui=gui,epg=epg,
                epg_sources=sources,epg_status=status,xtream=xc,group_selection=groups)):
            preview=module('preview025_ui','epg_preview.py')
            preview.show(dict(id='p',type='xtream',xc_host='host',xc_user='u',xc_pass='secret'))
        self.assertIn('DOWNLOAD_FAILED',outputs[0])
        self.assertIn('1/1 (100.0%)',outputs[0])
        self.assertIn('Live News',outputs[1])
        self.assertIn('Next Show',outputs[1])
        self.assertIn('MANUAL',outputs[1])
        self.assertNotIn('secret','\n'.join(outputs))

    def test_router_closes_directory_before_native_preview_to_avoid_spinner(self):
        import ast
        tree=ast.parse((LIB/'main.py').read_text())
        router=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Router')
        method=next(n for n in router.body if isinstance(n,ast.FunctionDef) and n.name=='_epg_status')
        order=[]
        plugin=types.SimpleNamespace(endOfDirectory=lambda *args,**kwargs:order.append('closed'))
        preview=types.ModuleType('epg_preview');preview.show=lambda *args,**kwargs:order.append('shown')
        ns={'xbmcplugin':plugin}
        exec(compile(ast.Module(body=[method],type_ignores=[]),'router_status','exec'),ns)
        with mock.patch.dict(sys.modules,{'epg_preview':preview}):
            ns['_epg_status'](types.SimpleNamespace(_handle=1,_portal=lambda:{'id':'p'}))
        self.assertEqual(order,['closed','shown'])

    def test_sender_context_preview_resolves_new_manual_id_instead_of_stale_alias(self):
        import ast
        views=module('context025_views','epg_views.py')
        now=time.time()
        cache={key:[dict(name=title,start_timestamp=now-60,stop_timestamp=now+600)]
               for key,title in [('7','Stale Wrong Title'),('mapped','Correct Live News')]}
        epg=types.ModuleType('epg');epg.load_cache=lambda _:cache
        sources=types.ModuleType('epg_sources')
        sources.configuration=lambda _:dict(mappings={'7':'mapped'})
        outputs=[]
        gui=types.ModuleType('xbmcgui')
        gui.Dialog=lambda:types.SimpleNamespace(textviewer=lambda heading,text:outputs.append(text))
        plugin=types.SimpleNamespace(endOfDirectory=mock.Mock())
        tree=ast.parse((LIB/'main.py').read_text())
        router=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Router')
        method=next(n for n in router.body if isinstance(n,ast.FunctionDef) and n.name=='_epg_channel')
        ns={'xbmcgui':gui,'xbmcplugin':plugin}
        exec(compile(ast.Module(body=[method],type_ignores=[]),'context_preview','exec'),ns)
        with mock.patch.dict(sys.modules,dict(epg=epg,epg_sources=sources,epg_views=views)):
            preview=module('context025_preview','epg_preview.py')
            with mock.patch.dict(sys.modules,{'epg_preview':preview}):
                ns['_epg_channel'](types.SimpleNamespace(_portal=lambda:dict(id='p',type='xtream'),
                    _params=dict(sid='7',tvg_id='7',name='Station'),_handle=1,
                    _xc=lambda _:types.SimpleNamespace(_get_json=mock.Mock(side_effect=AssertionError('no HTTP')))))
        self.assertIn('Correct Live News',outputs[0])
        self.assertNotIn('Stale Wrong Title',outputs[0])
