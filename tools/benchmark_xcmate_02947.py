"""Synthetic host comparison. Fresh readers/DBs, warm OS cache; no Android IO.

Use --project with an independently archived .46/.47 source tree. No provider
network: the published existing host fixture supplies synthetic catalog data.
"""
import argparse,importlib,json,math,sqlite3,sys,time,unittest
from pathlib import Path
from unittest import mock


def summary(values):
    ordered=sorted(values)
    return dict(n=len(values),p50_ms=round(ordered[math.ceil(len(values)*.5)-1],3),
                p95_ms=round(ordered[math.ceil(len(values)*.95)-1],3))


def run(project,samples):
    sys.path.insert(0,str(project/'tests'))
    from xcmate027_fixture import Fixture
    class F(Fixture,unittest.TestCase):pass
    widget_times=[];connections=[]
    for _ in range(samples):
        fixture=F();fixture.setUp()
        try:
            records=[dict(stream_id=str(i),category_id='a',name='Station '+str(i),epg_channel_id='xml') for i in range(88)]
            fixture.index.import_group('p','live','a',records)
            importlib.import_module('guide_store').import_cache('p',{'xml':[dict(channel='xml',name='Programme',descr='Local text',start_timestamp=fixture.now-60,stop_timestamp=fixture.now+600)]},trusted_feed=True)
            rows,_=importlib.import_module('widget_data41').snapshot(fixture.portal,'live')
            publish=importlib.import_module('widget_refresh45').publish;original=sqlite3.connect;opened=[]
            def connect(*a,**kw):opened.append(True);return original(*a,**kw)
            with mock.patch.object(sqlite3,'connect',side_effect=connect),mock.patch('programme_art46.enqueue'):
                start=time.perf_counter();assert publish(fixture.portal,'live',rows);widget_times.append((time.perf_counter()-start)*1000)
            connections.append(len(opened))
        finally:fixture.doCleanups()
    fixture=F();fixture.setUp();movie_times=[]
    try:
        fixture.index.import_group('p','vod','a',[dict(stream_id=str(i),category_id='a',name='Film '+str(i),added=fixture.now+i) for i in range(60000)])
        if (project/'src/plugin.video.xtreammate/resources/lib/widget_movie47.py').exists():reader_type=importlib.import_module('widget_movie47').MovieReader
        else:reader_type=importlib.import_module('widget_data41').WidgetReader
        for _ in range(samples):
            reader=reader_type('p')
            try:
                start=time.perf_counter();rows=reader.small('vod');movie_times.append((time.perf_counter()-start)*1000)
                assert len(rows)==24
            finally:
                if hasattr(reader,'close'):reader.close()
    finally:fixture.doCleanups()
    import xml.etree.ElementTree as ET
    return dict(version=ET.parse(project/'src/plugin.video.xtreammate/addon.xml').getroot().get('version'),
        measurement='Synthetic host; fresh readers and published local data, warm OS cache; no Android/cold-device inference',
        live88=dict(summary(widget_times),sqlite_connections_min=min(connections),sqlite_connections_max=max(connections)),
        movies60000=summary(movie_times))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--samples',type=int,default=25)
    args=parser.parse_args()
    if not 1<=args.samples<=100:parser.error('samples must be 1..100')
    print(json.dumps(run(args.project.resolve(),args.samples),indent=2))
