"""Reproduce actual SQLite INTERRUPT + clean busy-settings route in disposable profiles.
Run: python docs/XCMate/02995/HOST_SONDERPROBEN.py
These are host probes with fake Kodi APIs, never Android acceptance.
"""
import importlib,json,sqlite3,sys,unittest
from pathlib import Path
from unittest import mock
root=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(root/'tests'))
from xcmate027_fixture import Fixture

class Probe(Fixture,unittest.TestCase):pass
case=Probe();case.setUp();result={}
try:
 guide=importlib.import_module('guide_store');guide.connect().close();gate=importlib.import_module('epg_gate95');real=sqlite3.connect
 class Interrupted(sqlite3.Connection):
  def set_progress_handler(self,handler,n):return super().set_progress_handler(lambda:1,1)
 with mock.patch.object(sqlite3,'connect',side_effect=lambda *a,**k:real(*a,**dict(k,factory=Interrupted))):
  proof=gate.inspect(guide.path())
 assert proof['code']=='DB_INTERRUPTED' and proof['sqlite_code']==sqlite3.SQLITE_INTERRUPT,proof
 result['real_sqlite_progress_interrupt']=dict(code=proof['code'],sqlite_code=proof['sqlite_code'],status='PASS')
 error=importlib.import_module('portal_snapshot').PortalReadError(reason='PROFILE_BUSY')
 portal_file=case.folder/'portals.json';before=json.dumps([case.portal]).encode();portal_file.write_bytes(before)
 case.router._params.update(action='guide_backup44')
 with mock.patch.object(case.routes,'portal_for',side_effect=error):case.routes.dispatch(case.router)
 assert len(case.ends)==1 and case.ends[0][1].get('succeeded') is not False,case.ends
 assert portal_file.read_bytes()==before,'PROFILE_CHANGED'
 result['busy_epg_settings_route']=dict(directory_finishes=1,profile_reset=False,status='PASS')
 result.update(android='ANDROID_NOT_TESTED',profile='DISPOSABLE_SYNTHETIC_ONLY')
 print(json.dumps(result,indent=2))
finally:case.doCleanups()
