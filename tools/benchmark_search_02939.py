"""Reproduce cursor/publication changes against .38 with synthetic local data.

Development checkout only; imports strict host fixtures, no Kodi/device/provider.
Does not compare a host timing with the user's Android first-visible timings.
"""
import argparse,importlib,importlib.util,json,subprocess,sys,tempfile,time
from pathlib import Path
from unittest import mock
ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    sys.path[:0]=[str(ROOT/'tests'),str(ROOT/'src/plugin.video.xtreammate/resources/lib')]
    from test_xcmate_search_perf_02939 import SearchPerf39
    case=SearchPerf39(methodName='runTest');case.setUp()
    baseline='d8a20a2b7887878c3d5192e355b5c642a2bdebd5';results=[]
    try:
        with tempfile.TemporaryDirectory() as folder:
            source=subprocess.check_output(['git','show',baseline+':src/plugin.video.xtreammate/resources/lib/search_data.py'],cwd=ROOT)
            path=Path(folder)/'baseline.py';path.write_bytes(source)
            spec=importlib.util.spec_from_file_location('benchmark38',path);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
            for version,module in [('.38',old),('.39',case.data)]:
                if hasattr(module,'_PREPARED'):module._PREPARED.clear()
                timing=[]
                with mock.patch.object(module,'_now_events',wraps=module._now_events) as scans:
                    for phase in ('cold','warm'):
                        started=time.perf_counter();value=module.search(case.portal,'Rock','live',incremental=True,now=case.now)
                        first_ms=(time.perf_counter()-started)*1000;cursor=value['_cursor']
                        while not cursor.done:cursor.step()
                        timing.append(dict(phase=phase,first_names_ms=round(first_ms,3),total_ms=round((time.perf_counter()-started)*1000,3),names=cursor.counts['name_hits'],programmes=cursor.counts['programme_hits'],results=len(cursor.result)))
                    snapshots=scans.call_count
                with mock.patch.object(module,'LiveSearch',wraps=module.LiveSearch) as created:
                    value=module.search(case.portal,'Rock','live',incremental=True,now=case.now);cursor=value['_cursor']
                    for n in range(20):
                        case.properties['XCMate.ShortGuideRevision.p']=version+str(n)
                        if not cursor.valid():cursor=module.search(case.portal,'Rock','live',incremental=True,now=case.now)['_cursor']
                    generations=created.call_count
                results.append(dict(version=version,timings=timing,now_snapshots_for_two_queries=snapshots,cursor_generations_during_twenty_inflight_short_revisions=generations))
        assert results[0]['cursor_generations_during_twenty_inflight_short_revisions']==21
        assert results[1]['cursor_generations_during_twenty_inflight_short_revisions']==1
        assert results[0]['now_snapshots_for_two_queries']==2 and results[1]['now_snapshots_for_two_queries']==1
        report=dict(baseline=baseline,fixture=dict(channels=2905,epg_aliases=456,synthetic=True),measurements=results,level='HOST_DATA_PUBLICATION; no GUI/frame/device timing',android='NOT_TESTED')
        args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
    finally:case.doCleanups()


if __name__=='__main__':main()
