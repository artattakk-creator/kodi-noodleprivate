import sys,time,types,importlib,subprocess,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
from unittest import mock
sys.path.insert(0,str(ROOT/'tests'))
from xcmate027_fixture import Fixture
import unittest
class Case(Fixture,unittest.TestCase):pass
case=Case();case.setUp()
try:
 entries=[dict(stream_id=str(i),category_id='a',name='Needle station' if i==2763 else 'Station '+str(i),epg_channel_id='xml'+str(i)) for i in range(2764)]
 case.index.replace_catalog('p','live',entries,case.catalogs['get_live_categories'])
 base=types.ModuleType('baseline_search_034');exec(compile(subprocess.check_output(['git','show','030b81569d5b96b153ba1060be8525c24d27dcf3:src/plugin.video.xtreammate/resources/lib/search_data.py']),'<baseline .34>','exec'),base.__dict__)
 current=importlib.import_module('search_data');reports=[]
 for name,module in [('baseline .34',base),('candidate .35',current)]:
  clock=[0.0];reads=[];pages=[];module.time=types.SimpleNamespace(time=time.time,monotonic=lambda:clock[0],monotonic_ns=time.monotonic_ns)
  def short(client,sid,now=None):clock[0]+=.04;reads.append(sid);return {'now':''}
  original_page=case.index.Reader.page
  def page(reader,kind,*a,**kw):pages.append(kind);return original_page(reader,kind,*a,**kw)
  cursor=None;first=None;steps=0;started=time.perf_counter()
  with mock.patch('epg_views.cached_short_guide',side_effect=short),mock.patch.object(case.index.Reader,'page',page):
   while steps<4000:
    value=module.search(case.portal,'Needle',kind='live',incremental=True,continuation=cursor,now=case.now);steps+=1
    if value['live']['rows'] and first is None:first=clock[0]
    cursor=value.get('_continuation')
    if cursor is None:break
  reports.append(dict(version=name,channels=2764,synthetic_short_cache_cost_ms=40,first_name_model_seconds=round(first,3),full_scan_model_seconds=round(clock[0],3),short_cache_reads=len(reads),media_page_queries=len(pages),steps=steps,host_wall_ms=round((time.perf_counter()-started)*1000,3)))
 # Restore current module clock before independent wall measurements.
 current.time=time;wall=[]
 for run in range(3):
  started=time.perf_counter();value=current.search(case.portal,'Needle',kind='live',incremental=True)
  assert value['live']['rows'][0]['sid']=='2763'
  wall.append(round((time.perf_counter()-started)*1000,3))
 report=dict(evidence='Synthetic host fixture, not Android latency; 40 ms injected per cache-only read, no sleeps or network',runs=reports,host_first_name_2764_ms=wall,android='NOT_TESTED')
 print(json.dumps(report,indent=2));open('docs/XCMate/PERFORMANCE_02935_HOST.json','w').write(json.dumps(report,indent=2)+'\n')
finally:case.doCleanups()
