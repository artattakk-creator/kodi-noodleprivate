"""Fresh local synthetic guide and warm lookups; no cold-device claims."""
import argparse,importlib,json,math,sqlite3,sys,time,unittest
from pathlib import Path
from unittest import mock
parser=argparse.ArgumentParser();parser.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--samples',type=int,default=30);parser.add_argument('--output',type=Path);args=parser.parse_args()
sys.path.insert(0,str(args.project/'tests'))
from xcmate027_fixture import Fixture
class F(Fixture,unittest.TestCase):pass
f=F();f.setUp()
def percentile(v):
 s=sorted(v);return dict(n=len(v),p50_ms=round(s[math.ceil(len(s)*.5)-1],3),p95_ms=round(s[math.ceil(len(s)*.95)-1],3))
try:
 rows=[dict(sid=str(i),stream_id=str(i),name='Station '+str(i),category_id='a',epg_channel_id='xml'+str(i)) for i in range(88)]
 events={'xml'+str(i):[dict(name='Current '+str(i),start_timestamp=f.now-60,stop_timestamp=f.now+7200),dict(name='Next '+str(i),start_timestamp=f.now+7200,stop_timestamp=f.now+14400)] for i in range(88)}
 f.index.replace_catalog('p','live',rows,[dict(category_id='a',category_name='Synthetic')]);importlib.import_module('guide_store').import_cache('p',events,'bench74',now=f.now,trusted_feed=True)
 local=importlib.import_module('local_epg');bridge=importlib.import_module('epg_handoff63');times=[];connections=[];original=sqlite3.connect
 start=time.perf_counter();local.now_next('p',rows[:16],{},display_only65=True);cold=round((time.perf_counter()-start)*1000,3)
 for _ in range(args.samples):
  calls=[]
  with mock.patch('sqlite3.connect',side_effect=lambda *a,**kw:(calls.append(True),original(*a,**kw))[1]):
   start=time.perf_counter();value=local.now_next('p',rows[:16],{},display_only65=True);times.append((time.perf_counter()-start)*1000)
  if len(value)!=16 or value['0']['now']!='Current 0':raise RuntimeError('BAD_BENCH_DATA')
  connections.append(len(calls))
 refresh=importlib.import_module('widget_refresh45');wd=importlib.import_module('widget_data41');wd.store(wd.files('p','live')[0],wd.policy(f.portal,'live'),rows,['bench',1])
 writes=[];replace=__import__('os').replace
 with mock.patch('os.replace',side_effect=lambda a,b:(writes.append(b),replace(a,b))[1]):
  for _ in range(args.samples):refresh.publish(f.portal,'live',rows)
 output=dict(version=__import__('xml.etree.ElementTree',fromlist=['parse']).parse(args.project/'src/plugin.video.xtreammate/addon.xml').getroot().get('version'),scope='Linux synthetic host, 88 local channels, first lookup cold Python/view state; OS cache uncontrolled. Not Android timings.',epg16=dict(first_ms=cold,**percentile(times),warm_sqlite_connections_min=min(connections),warm_sqlite_connections_max=max(connections)),identical_frame_calls=args.samples,atomic_metadata_writes=len(writes),android='ANDROID_NOT_TESTED')
 if args.output:args.output.write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps(output))
finally:f.doCleanups()
