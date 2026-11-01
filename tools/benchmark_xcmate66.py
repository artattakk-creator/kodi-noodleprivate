"""Synthetic cold persistent all-channel and warm RAM evidence; NOT Android."""
import argparse,json,sys,time
from pathlib import Path
from unittest import mock
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tests'))
from test_xcmate_epg_coverage_02966 import Coverage66
case=Coverage66()
try:
 case.setUp();case.populate()
 from widget_group46 import _infos63
 with mock.patch('urllib.request.urlopen',side_effect=AssertionError('NO_EPG_HTTP')):
  start=time.perf_counter();cold=_infos63(case.portal,case.rows);cold_ms=(time.perf_counter()-start)*1000
  with mock.patch('sqlite3.connect',side_effect=AssertionError('NO_WARM_SQL')):
   start=time.perf_counter();warm=_infos63(case.portal,case.rows);warm_ms=(time.perf_counter()-start)*1000
 if len(cold)!=88 or len(warm)!=88 or any(cold[str(i)]['now']!='Now '+str(i) for i in range(88)):raise RuntimeError('COLD_PERSISTENT_COVERAGE')
 value=dict(version='0.1.29.66',environment='synthetic host; NOT Android',channels=88,never_focused=88,now_next_correct=88,cold_all_ms=round(cold_ms,3),warm_all_ms=round(warm_ms,3),warm_sql=0,http=0,source='existing guide_v1.sqlite')
finally:case.doCleanups()
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
if args.output:args.output.write_text(json.dumps(value,indent=2)+'\n')
print('XCMATE66_COLD_WARM_JSON '+json.dumps(value,sort_keys=True))
