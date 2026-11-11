import os,sys,types,subprocess,fcntl,time,json,unittest,platform
from pathlib import Path
sys.path.insert(0,'tests');sys.path.insert(0,'/tmp/xcmate80-host-deps')
from xcmate027_fixture import Fixture
from unittest import mock
from test_xcmate_02988 import png
class Case(Fixture,unittest.TestCase):pass
c=Case();c.setUp()
try:
 import portal_snapshot,logo_manifest86,logo_store89
 old=types.ModuleType('old_snapshot90');exec(subprocess.check_output(['git','show','cb37de7103bd335a344c6738c33c4b5560ba2d4c:src/plugin.video.xtreammate/resources/lib/portal_snapshot.py']),old.__dict__)
 file=c.folder/'portals.json';file.write_text(json.dumps([c.portal]));readers=[old.Snapshot(),portal_snapshot.Snapshot()]
 for r in readers:r.read(str(file),['xtream'])
 fd=os.open(c.folder/'.xcmate-config.lock',os.O_CREAT|os.O_RDWR,0o600);fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
 result=[]
 try:
  for r in readers:
   start=time.perf_counter();blocked=0
   for _ in range(5):
    try:r.read(str(file),['xtream'])
    except TimeoutError:blocked+=1
   result.append(dict(ms=round((time.perf_counter()-start)*1000,3),callbacks=5,errors=blocked))
 finally:os.close(fd)
 rows=[dict(sid=str(i),stream_icon='https://images.example.org/'+str(i)+'.png') for i in range(88)]
 facts=dict(capacity82='SAME_VOLUME_VERIFIED',free=115*1024**2,total=4034297856,volume82='same')
 with mock.patch('art_storage82.capacity',return_value=facts):
  for row in rows:logo_store89.persist(c.portal,row,png())
 oldmanifest=types.ModuleType('old_manifest90');exec(subprocess.check_output(['git','show','cb37de7103bd335a344c6738c33c4b5560ba2d4c:src/plugin.video.xtreammate/resources/lib/logo_manifest86.py']),oldmanifest.__dict__)
 reads=[];logo_manifest86._manifest90.clear()
 for m in (oldmanifest,logo_manifest86):
  with mock.patch.object(m.json,'load',wraps=m.json.load) as load:
   start=time.perf_counter()
   for row in rows:m.load(c.portal)
   reads.append(dict(ms=round((time.perf_counter()-start)*1000,3),item_callbacks=88,json_parses=load.call_count))
 report=dict(host=platform.machine(),python=platform.python_version(),platform='Synthetic Linux host, not Android',base='cb37de7103bd335a344c6738c33c4b5560ba2d4c',portal_read_under_real_flock=dict(before=result[0],after=result[1]),manifest_88_callbacks=dict(before=reads[0],after=reads[1]))
 Path('docs/XCMate/test-builds/02990/host-measurements90.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
finally:c.tearDown() if hasattr(c,'tearDown') else None;c.doCleanups()
