#!/usr/bin/env python3
"""Controlled .68/.69 failed-write replay measurement; no private API/device."""
import argparse,importlib.util,json,statistics,subprocess,sys,time,types,unittest
from pathlib import Path
from unittest import mock
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'tests'),str(ROOT/'src/plugin.video.xtreammate/resources/lib')]
from xcmate027_fixture import Fixture
class Environment(Fixture,unittest.TestCase):pass
env=Environment();env.setUp()
try:
 from programme_events46 import describe
 import programme_urls55 as current,programme_session69 as session
 event=describe(env.portal,dict(sid='69',name='Synthetic'),dict(title='Synthetic film',start=env.now-30,stop=env.now+1800,year=2024,genre='Spielfilm'),'a',('revision',1))
 source=subprocess.run(['git','show','cf62f5d554634acca5c2676c6af3d524747f8f40:src/plugin.video.xtreammate/resources/lib/programme_urls55.py'],check=True,capture_output=True,text=True).stdout
 previous=types.ModuleType('frozen_urls68');exec(compile(source,'<pinned-.68>','exec'),previous.__dict__)
 results={}
 for name,module,options in (('pinned_68_url_persistence',previous,{}),('candidate_69_url_persistence',current,dict(url_mode69=True))):
  session._values.clear();session._outcomes.clear();session._attempts.clear();session._outcome_bytes=0
  def lookup(*a,**kw):
   time.sleep(.002)
   return dict(url='https://image.tmdb.org/t/p/w500/SYNTHETIC.jpg',source='xmltv_event',match='EXACT_EVENT',attribution='Synthetic XMLTV')
  lookup_=mock.Mock(side_effect=lookup);times=[]
  with mock.patch('programme_index46.art',return_value=None) as old_write,mock.patch('programme_index46.event',return_value=False),mock.patch('programme_index46.publish_result69',return_value=False) as atomic,mock.patch('programme_writes69.permit',return_value=True),mock.patch('programme_writes69.last',return_value='SAFE_RESERVE_BLOCKED'):
   for _ in range(18):
    start=time.perf_counter();value=module.resolve(event,allow_lookup=True,match=lookup_,check=mock.Mock(),**options);times.append((time.perf_counter()-start)*1000)
  results[name]=dict(requests=18,matching_calls=lookup_.call_count,metadata_publish_attempts=atomic.call_count if options else sum(c.args[1:]!=() for c in old_write.call_args_list),median_ms=round(statistics.median(times),3),total_ms=round(sum(times),3),code=value['code'],storage=value.get('storage69','NOT_PERSISTED'))
 assert results['pinned_68_url_persistence']['matching_calls']==18
 assert results['candidate_69_url_persistence']['matching_calls']==1
 assert results['candidate_69_url_persistence']['code']=='READY'
 output=dict(scope='controlled host resolver replay, 2ms synthetic lookup, failing metadata writes; no physical Android timings',results=results,android='NOT_TESTED')
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
 if args.output:args.output.write_text(json.dumps(output,indent=2)+'\n')
 print('PERFORMANCE69_JSON '+json.dumps(output,sort_keys=True))
finally:env.doCleanups()
