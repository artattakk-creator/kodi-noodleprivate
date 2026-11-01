"""Pinned .66 regression evidence; no devices, private feeds or network probes."""
import sys,json,sqlite3,types
from pathlib import Path
from unittest import mock
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tests'),str(ROOT/'tools')]
import inspect_bingie64
inspect_bingie64.BASE='a9a3476bc04c3624d1451dfe03899c2220138c08'
baseline=inspect_bingie64.baseline()
print('BASELINE67_JSON '+json.dumps(baseline,separators=(',',':')),flush=True)
print('BASELINE67_COUNTS '+json.dumps(dict(files=len(baseline['source_sha256']),tests=sum(map(len,baseline['test_methods'].values())))),flush=True)
from test_xcmate_epg_02952 import EPG52
case=EPG52()
try:
 case.setUp();case.put('a',[case.event(title='Existing committed programme')])
 import local_epg,epg_views
 good=local_epg.window('p',[case.channel],{},case.now,case.now+3600)
 from epg_handoff63 import register
 before=local_epg.now_next('p',[case.channel],{},case.now)
 with mock.patch('programme_flow48.enrich',side_effect=sqlite3.OperationalError('synthetic unrelated metadata table unavailable')):
  full=local_epg.window('p',[case.channel],{},case.now,case.now+3600)
  text=local_epg.window('p',[case.channel],{},case.now,case.now+3600,text_only65=True)
 print('EPG67_OPTIONAL_METADATA_REPRO '+json.dumps(dict(primary_programmes=len(good.get('a',[])),full_block_lost=full is None,text_block_lost=text is None)),flush=True)
 cache={'1':[dict(name='Expired alias',start_timestamp=case.now-1800,stop_timestamp=case.now-900)],'provider':[dict(name='Verified provider programme',start_timestamp=case.now-60,stop_timestamp=case.now+1800)]}
 current=epg_views.resolve_guide(cache,'provider','1',case.now,mappings={})
 manual=epg_views.resolve_guide(cache,'provider','1',case.now,mappings={'1':'1'})
 print('EPG67_ALIAS_REPRO '+json.dumps(dict(current=current['now'],provider_event_available=True,explicit_manual_preserved=not manual['now'])),flush=True)
 import player
 from xcmate027_fixture import ListItem
 class PlayItem67(ListItem):
  def setPath(self,value):self.path=value
  def getPath(self):return self.path
 with mock.patch.object(player.xbmcgui,'ListItem',PlayItem67),mock.patch.object(player,'_isa_available',return_value=True):
  item=player.build_playable_item('https://provider.example.test/live/synthetic/fixture/1')
 print('LIVE67_TYPE_REPRO '+json.dumps(dict(detected=player.detect_stream_type('https://provider.example.test/live/synthetic/fixture/1'),properties=item.properties if hasattr(item,'properties') else getattr(item,'props',{}))),flush=True)
except Exception:
 import traceback
 print('SYNTHETIC67_INSPECT_EXCEPTION '+traceback.format_exc(),flush=True)
 raise
finally:case.doCleanups()
