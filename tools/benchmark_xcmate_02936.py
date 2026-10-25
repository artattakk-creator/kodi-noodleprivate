"""Reproducible .35/.36 host comparisons, NOT Android or physical IR/video timing.

Real SQLite, JSON and filesystem operations behind strict Kodi stubs. No sleeps,
injected latency, HTTP or personal data. Execute from an unbuilt source checkout.
"""
import argparse
import ast
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
import types
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
LIB=ROOT/'src/plugin.video.xtreammate/resources/lib'
sys.path[:0]=[str(ROOT/'tests'),str(LIB)]
from xcmate027_fixture import Fixture

BASE='9c558c70e8abd56d071d703ff9e78909e78c85ac'


class Harness(Fixture,unittest.TestCase):pass


def old(name):
    value=types.ModuleType('benchmark_old_'+name)
    source=subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':src/plugin.video.xtreammate/resources/lib/'+name+'.py'],text=True)
    exec(compile(source,'baseline_'+name,'exec'),value.__dict__)
    return value


def search_case(version):
    h=Harness(methodName='runTest');h.setUp()
    try:
        count=2764
        h.index.replace_catalog('p','live',[dict(stream_id=str(i),category_id='a',name='Station '+str(i)) for i in range(count)],h.catalogs['get_live_categories'])
        roots=[h.folder/'cache',h.folder/'private'];[r.mkdir() for r in roots]
        io=dict(exists=0,mkdir=0)
        def private():io['mkdir']+=1;roots[1].mkdir(exist_ok=True);return str(roots[1])
        def exists(path):io['exists']+=1;return os.path.exists(path)
        utils=sys.modules['utils'];utils.cache_dir=lambda:str(roots[0]);utils._private_cache_dir=private
        utils.cache_key=lambda s:hashlib.md5(s.encode()).hexdigest()
        # Execute the actual cache_get implementation, changing only Kodi VFS
        # bindings to real host files and counting native boundary operations.
        tree=ast.parse((LIB/'utils.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='cache_get')
        ns=dict(os=os,json=json,time=time,cache_dir=utils.cache_dir,_private_cache_dir=private,
                xbmcvfs=types.SimpleNamespace(exists=exists,File=lambda p:open(p,encoding='utf-8')))
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'real_cache_get','exec'),ns)
        utils.cache_get=ns['cache_get']
        spec=importlib.util.spec_from_file_location('benchmark_real_xtream',LIB/'xtream.py')
        xc=importlib.util.module_from_spec(spec);spec.loader.exec_module(xc)
        client=xc.XtreamClient('https://provider.invalid','synthetic','synthetic')
        data=dict(epg_listings=[dict(title='Synthetic local programme',start_timestamp=h.now-60,stop_timestamp=h.now+3600)])
        ck=client._cache_key('get_short_epg',dict(stream_id='2763',limit=4))
        (roots[1]/(ck+'.json')).write_text(json.dumps(dict(ts=time.time(),data=data)))
        module=old('search_data') if version=='before' else importlib.import_module('search_data')
        sys.modules['xbmc'].LOGINFO=1;sys.modules['xbmc'].log=lambda *a:None
        start=time.perf_counter_ns()
        with mock.patch.object(module,'_short_client',return_value=client):
            cursor=module.LiveSearch(h.portal,'Synthetic local programme',h.index.Reader('p'),h.now)
            first=None;slices=0
            while not cursor.done:
                rows,_=cursor.step();slices+=1
                if rows and first is None:first=(time.perf_counter_ns()-start)/1e6
        elapsed=(time.perf_counter_ns()-start)/1e6
        assert len(rows)==1 and rows[0]['sid']=='2763'
        return dict(first_programme_ms=first,final_ms=elapsed,slices=slices,cache_channel_reads=cursor.short_rows,**io)
    finally:h.doCleanups()


def start_case(version):
    h=Harness(methodName='runTest');h.setUp()
    try:
        rows=[dict(stream_id=str(i),name='Station '+str(i),category_id='a',provider_extra='x'*4096) for i in range(2764)]
        h.index.replace_catalog('p','live',rows,h.catalogs['get_live_categories'])
        filename=h.folder/'global-live.json';filename.write_text(json.dumps(rows));io=dict(reads=0,bytes=0)
        def catalog(action):
            assert action=='get_live_streams';io['reads']+=1;data=filename.read_bytes();io['bytes']+=len(data)
            return json.loads(data)
        h.client.get_cached_catalog=catalog
        h.client.live_stream_url=lambda sid,ext:'https://provider.invalid/live/u/p/'+sid+'.'+ext
        sys.modules['xbmcgui'].WindowDialog=object
        sys.modules['xbmc'].LOGINFO=1;sys.modules['xbmc'].log=lambda *a:None
        if version=='before':main=old('main');routes=old('app_routes')
        else:
            spec=importlib.util.spec_from_file_location('benchmark_current_main',LIB/'main.py');main=importlib.util.module_from_spec(spec);spec.loader.exec_module(main)
            routes=importlib.import_module('app_routes')
        router=main.Router(['plugin://plugin.video.xtreammate','-1','?action=home_start&pid=p']);router._xc=lambda p:h.client
        router._play_start_direct=lambda:router._startup_playable()
        with mock.patch.dict(sys.modules,player=types.SimpleNamespace(build_playable_item=lambda *a,**kw:object())):
            start=time.perf_counter_ns();routes.dispatch(router);elapsed=(time.perf_counter_ns()-start)/1e6
        return dict(metadata_to_prepared_item_ms=elapsed,**io)
    finally:h.doCleanups()


def catalogue_case(version):
    h=Harness(methodName='runTest');h.setUp()
    try:
        rows=[dict(stream_id=str(i),name='Station '+str(i),category_id='a',provider_extra='x'*4096) for i in range(2764)]
        h.index.replace_catalog('p','live',rows,h.catalogs['get_live_categories'])
        filename=h.folder/'global-live.json';filename.write_text(json.dumps(rows));io=dict(reads=0,bytes=0)
        def catalog(action):
            if action=='get_live_categories':return h.catalogs[action]
            io['reads']+=1;data=filename.read_bytes();io['bytes']+=len(data);return json.loads(data)
        h.client.get_cached_catalog=catalog;h.client.live_stream_url=lambda sid,ext:'https://provider.invalid/live/u/p/'+str(sid)+'.'+ext
        sys.modules['xbmcgui'].WindowDialog=object
        if version=='before':source=subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':src/plugin.video.xtreammate/resources/lib/live_overlay.py'],text=True)
        else:source=(LIB/'live_overlay.py').read_text()
        cls=next(n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name=='LiveNavigator')
        fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='_load_catalog_from_disk')
        ns=dict(time=time,trace=lambda *a,**kw:None)
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'real_catalogue_method','exec'),ns)
        nav=types.SimpleNamespace(portal=h.portal,xc=h.client)
        # Channel itself has no Kodi dependencies; execute its exact dataclass
        # equivalent from source, avoiding unrelated iptv network imports.
        channel=next(n for n in ast.parse((LIB/'iptv.py').read_text()).body if isinstance(n,ast.ClassDef) and n.name=='Channel')
        bindings={};exec(compile(ast.Module(body=[channel],type_ignores=[]),'real_Channel','exec'),bindings)
        with mock.patch.dict(sys.modules,iptv=types.SimpleNamespace(Channel=bindings['Channel'])):
            start=time.perf_counter_ns();assert ns['_load_catalog_from_disk'](nav)
        return dict(catalogue_preparation_ms=(time.perf_counter_ns()-start)/1e6,channels=len(nav.channels),**io)
    finally:h.doCleanups()


def guide_case(version):
    h=Harness(methodName='runTest');h.setUp()
    try:
        cache={'xml'+str(i):[dict(channel='xml'+str(i),name='Now',descr='x'*2048,start_timestamp=h.now-60,stop_timestamp=h.now+3600)] for i in range(2764)}
        guide=importlib.import_module('guide_store');guide.import_cache('p',cache)
        filename=h.folder/'portal-epg.json';filename.write_text(json.dumps(cache));io=dict(reads=0,bytes=0)
        def load(pid):io['reads']+=1;data=filename.read_bytes();io['bytes']+=len(data);return json.loads(data)
        sys.modules['epg'].load_cache=load
        module=old('tv_data') if version=='before' else importlib.import_module('tv_data')
        snapshot=module.GuideSnapshot(h.portal,h.client)
        snapshot.request([types.SimpleNamespace(tvg_id='xml2763',logo='',name='Station',extra={'stream_id':'2763'})])
        with mock.patch('logo_cache.request'):
            start=time.perf_counter_ns();snapshot.refresh();elapsed=(time.perf_counter_ns()-start)/1e6
        assert snapshot.get('2763',h.now)['now']=='Now'
        return dict(one_channel_worker_ms=elapsed,**io)
    finally:h.doCleanups()


def genre_cases():
    result={}
    for count in (1000,50000):
        h=Harness(methodName='runTest');h.setUp()
        try:
            genre=importlib.import_module('genre_search')
            rows=[dict(stream_id=str(i),category_id='a',name='Sci-Fi Archive' if i==0 else 'Item '+str(i),
                       genre='Science Fiction' if i%10==0 else 'Drama') for i in range(count)]
            h.index.replace_catalog('p','vod',rows,h.catalogs['get_vod_categories'])
            reader=h.index.Reader('p',timeout=.15,query_seconds=1)
            start=time.perf_counter_ns();_,before=reader.page('vod','Sci-Fi');title_ms=(time.perf_counter_ns()-start)/1e6
            start=time.perf_counter_ns();batches=[]
            while True:
                tick=time.perf_counter_ns();worked=genre.advance('p','vod')
                if not worked:break
                batches.append((time.perf_counter_ns()-tick)/1e6)
            build_ms=(time.perf_counter_ns()-start)/1e6
            samples=[]
            for _ in range(5):
                tick=time.perf_counter_ns();found,total=reader.page('vod','Sci-Fi');samples.append((time.perf_counter_ns()-tick)/1e6)
            assert before==1 and total==count//10 and found[0]['sid']=='0'
            result[str(count)]=dict(title_only_before_ms=title_ms,title_only_before_hits=before,
                completed_genre_hits=total,genre_query_samples_ms=samples,genre_query_median_ms=statistics.median(samples),
                host_materialization_ms=build_ms,transactions=len(batches),maximum_transaction_ms=max(batches),
                batch_rows=genre.BATCH,includes_service_scheduling=False)
        finally:h.doCleanups()
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--samples',type=int,default=5);args=parser.parse_args()
    result=dict(baseline=BASE,platform=platform.platform(),python=platform.python_version(),channels=2764,
        measurement='Host real filesystem/SQLite/JSON behind Kodi stubs; no injected latency; no Android/IR/first-frame result',cases={})
    for name,fn in (('sparse_short_cache_tail',search_case),('menu_start_local_metadata',start_case),
                    ('navigator_catalogue_only',catalogue_case),('guide_viewport_worker',guide_case)):
        result['cases'][name]={}
        for version in ('before','after'):
            samples=[fn(version) for _ in range(max(1,min(args.samples,10)))]
            result['cases'][name][version]=dict(samples=samples,median={key:statistics.median(s[key] for s in samples) for key in samples[0]})
    result['genre']=genre_cases()
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({name:{v:x['median'] for v,x in values.items()} for name,values in result['cases'].items()},indent=2))
    print(json.dumps(result['genre'],indent=2))


if __name__=='__main__':main()
