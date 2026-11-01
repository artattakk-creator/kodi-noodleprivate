"""Synthetic before/after evidence against the exact frozen .64 sources."""
import argparse,errno,importlib,json,statistics,sys,time,types
from pathlib import Path
from unittest import mock
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tests'))
from test_xcmate_epg_02965 import EPG65
from test_xcmate_token_destination_02965 import Destination65
from test_xcmate_tmdb_token_02961 import FIXTURE
hooks=json.loads((root/'tests/fixtures/xcmate_02965_reviewed_hooks.json').read_text())['modules']
def previous(name):
 value=types.ModuleType('baseline_'+name);value.__file__=str(root/'src/plugin.video.xtreammate/resources/lib'/('baseline_'+name+'.py'))
 exec(compile(hooks['src/plugin.video.xtreammate/resources/lib/'+name+'.py']['old'],value.__file__,'exec'),value.__dict__);return value
result=dict(base='cad966081b9dd6fe75f7ff9cde2a4b286efdcf09',environment='synthetic host; NOT Android',private_data='NONE')
case=Destination65()
try:
 case.setUp();old=previous('tmdb_token61');original=case.dest.os.open
 def denied(path,*args,**kwargs):
  if path=='/':raise PermissionError(errno.EACCES,'synthetic root-listing denial')
  return original(path,*args,**kwargs)
 with mock.patch.object(case.dest.os,'open',side_effect=denied):
  try:old.read(str(case.path),missing=True)
  except (OSError,ValueError) as error:before=dict(result='BLOCKED',error=type(error).__name__,errno=getattr(error,'errno',0))
  else:raise RuntimeError('TOKEN_BEFORE_REPRO_NOT_TRIGGERED')
  case.prepare();after=case.tokens.import_bytes(FIXTURE,None)
  if case.tokens.read(str(case.path))!=FIXTURE+b'\n':raise RuntimeError('TOKEN_AFTER_READBACK')
 result['private_target65']=dict(before=before,after=after,root_walk=False)
finally:case.doCleanups()
case=EPG65()
try:
 case.setUp();case.local.now_next('p',case.channels,{},now=case.now)
 old=previous('widget_group46');new=importlib.import_module('widget_group46')
 import sqlite3
 connect=sqlite3.connect
 def measure(call):
  timings=[];count=[0]
  def counted(*args,**kwargs):count[0]+=1;return connect(*args,**kwargs)
  with mock.patch('sqlite3.connect',side_effect=counted),mock.patch('urllib.request.urlopen',side_effect=RuntimeError('UNEXPECTED_HTTP')):
   for _ in range(5):
    started=time.perf_counter();values=call(case.portal,case.channels);timings.append((time.perf_counter()-started)*1000)
    if values['2']['now']!='Stored fixture WELT':raise RuntimeError('EPG_TEXT_IDENTITY')
  return dict(repeats=5,sql_connects=count[0],median_ms=round(statistics.median(timings),3),max_ms=round(max(timings),3))
 before=measure(old._infos63);after=measure(new._infos63)
 if before['sql_connects']<=0 or after['sql_connects']!=0:raise RuntimeError('EPG_SQL_REDUCTION_NOT_PROVEN')
 result['warm_home65']=dict(before=before,after=after,http_calls=0)
finally:case.doCleanups()
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
if args.output:args.output.write_text(json.dumps(result,indent=2)+'\n')
print('XCMATE65_BEFORE_AFTER_JSON '+json.dumps(result,sort_keys=True))
