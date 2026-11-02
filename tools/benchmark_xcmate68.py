"""Synthetic host timing only: bounded local read and RAM-only warm seed."""
import json,statistics,sys,time
from pathlib import Path
from unittest import mock
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'tests'),str(ROOT/'src/plugin.video.xtreammate/resources/lib')]
from test_xcmate_epg_02952 import EPG52
case=EPG52();case.setUp()
try:
 case.put('a',[case.event(title='Synthetic warm programme')])
 from local_epg import now_next
 from tv_data import GuideSnapshot
 started=time.perf_counter();info=now_next('p',[case.channel],{},case.now);cold=(time.perf_counter()-started)*1000
 warm=[]
 for _ in range(30):
  with mock.patch('sqlite3.connect',side_effect=AssertionError('WARM_SQL')),mock.patch('builtins.open',side_effect=AssertionError('WARM_FILE')),mock.patch('media_sources43.get',side_effect=AssertionError('WARM_HTTP')):
   started=time.perf_counter();snapshot=GuideSnapshot(case.portal,None,initial_sid='1');value=snapshot.get('1');warm.append((time.perf_counter()-started)*1000)
   assert value['now']=='Synthetic warm programme'
 result=dict(platform='GitHub Actions Linux host; synthetic isolated SQLite/RAM',android='NOT_TESTED',cold_sqlite_now_next_ms=round(cold,3),warm_ram_median_ms=round(statistics.median(warm),3),warm_ram_max_ms=round(max(warm),3),samples=len(warm),warm_sql_queries=0,warm_file_reads=0,warm_http=0)
 target=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'xcmate68-host-evidence.json';target.write_text(json.dumps(result,indent=2))
 print('BENCHMARK68_JSON '+json.dumps(result),flush=True)
finally:case.doCleanups()
