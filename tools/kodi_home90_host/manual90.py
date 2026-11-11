"""Native candidate selection -> real queued Save/readback -> cold mapping.
Only API response identity/capacity are synthetic; no production persistence or
GUI callbacks are replaced, and no real token or external API is contacted.
"""
from pathlib import Path
import json,time,threading,shutil,collections

def run(portal,rows,pump,capture,cold,check):
 import xbmc,xbmcgui,work_requests86,work_manager86,programme_mapping85,tmdb_connection60
 from programme_events46 import load
 event=load(portal,rows[4]);key='manual90-'+str(event['sid']);receipt=Path('/root/manual90-proof.json')
 if cold:
  expected=json.loads(receipt.read_text());check(programme_mapping85.reload(),'MANUAL90_COLD_RELOAD_FAILED');mapping=programme_mapping85.current(event)
  check(mapping and mapping['id']==expected['selected_id'],'MANUAL90_COLD_MAPPING_CHANGED');return dict(status='PASS',cold_mapping=True,selected_id=mapping['id'],android='ANDROID_NOT_TESTED')
 oldrequest=tmdb_connection60.request;oldusage=shutil.disk_usage;stop=threading.Event();errors=[]
 def api(url,**kw):
  if kw.get('cancel',lambda:False)():raise __import__('media_sources43').SourceError('CANCELLED')
  def record(i):return dict(id=9000+i,name='Synthetic candidate '+str(i),original_name='Synthetic candidate '+str(i),first_air_date='2002-01-01',origin_country=['US'],overview='Synthetic API response; explicit user selection required.',poster_path='/vod84-4.png',backdrop_path='/event84-4.png')
  if '/search/tv?' in url:return dict(results=[record(i) for i in range(8)],page=1,total_pages=1)
  if '/tv/' in url:return record(int(url.split('/tv/')[1].split('?')[0])-9000)
  raise AssertionError('MANUAL90_UNEXPECTED_API_REQUEST')
 def usage(path):
  if str(path)==str(programme_mapping85.path().parent):return collections.namedtuple('usage','total used free')(4034297856,4034297856-115*1024**2,115*1024**2)
  return oldusage(path)
 usage.fault84=True
 def worker():
  while not stop.wait(.02):
   try:
    if work_requests86.pending():work_requests86.drain()
   except Exception as error:errors.append(type(error).__name__);return
 tmdb_connection60.request=api;shutil.disk_usage=usage;lane=threading.Thread(target=worker);lane.start()
 try:
  result=work_manager86.wait(event,'search',query='Synthetic candidate',kind='tv',source='tmdb',page=1)
  candidates=result.get('rows',[]);check(result.get('code')=='READY' and len(candidates)==8,('MANUAL90_SEARCH_FAILED',result.get('code')))
  chosen=[]
  def ir():
   deadline=time.monotonic()+10
   while time.monotonic()<deadline:
    count=xbmc.getInfoLabel('Container(6).NumItems')
    if count=='8' and xbmcgui.getCurrentWindowDialogId() not in (0,-1,9999,10101,10138):
     dialog=xbmcgui.Window(xbmcgui.getCurrentWindowDialogId());dialog.setFocusId(6);dialog.getControl(6).selectItem(3);xbmc.executebuiltin('Action(Select)',wait=False);chosen.append(3);return
    xbmc.sleep(50)
  remote=threading.Thread(target=ir);remote.start()
  index=xbmcgui.Dialog().select('XCMate .90 · explicit candidate', [xbmcgui.ListItem(v['title']) for v in candidates],useDetails=True)
  remote.join(1);check(index==3 and chosen==[3],('MANUAL90_NATIVE_SELECTION_FAILED',index))
  answer=work_manager86.wait(event,'save',candidate=candidates[index]);check(answer.get('code')=='SAVED',('MANUAL90_SAVE_FAILED',answer.get('code')))
  check(programme_mapping85.committed89(event,answer['nonce']),'MANUAL90_MISSING_COMMIT_RECEIPT')
  programme_mapping85._loaded.clear();check(programme_mapping85.reload(),'MANUAL90_READBACK_FAILED');check(programme_mapping85.current(event)['id']==9003,'MANUAL90_WRONG_READBACK')
  # Open, close and reopen the actual EPG detail owner, without mutating EPG.
  from programme_window46 import ProgrammeWindow46
  import xbmcaddon
  for _ in range(2):
   view=ProgrammeWindow46('XCMateProgramme46.xml',xbmcaddon.Addon('plugin.video.xtreammate').getAddonInfo('path'),'Default','720p');view.configure(portal,rows[4],event,None);view.show()
   for _ in range(20):view.pump();xbmc.sleep(50)
   check(programme_mapping85.current(event)['id']==9003,'MANUAL90_DETAIL_REOPEN_CHANGED_MAPPING');view.close()
  check(not errors,('MANUAL90_WORKER_FAILED',errors))
 finally:stop.set();lane.join(2);tmdb_connection60.request=oldrequest;shutil.disk_usage=oldusage
 report=dict(status='PASS',candidates=8,native_selected=3,selected_id=9003,save='WRITE_COMMITTED + WRITE_READBACK',detail_reopens=2,api='Synthetic TMDB JSON, no external API/token',android='ANDROID_NOT_TESTED')
 receipt.write_text(json.dumps(report,indent=2));print('MANUAL90_NATIVE '+json.dumps(report),flush=True);return report
