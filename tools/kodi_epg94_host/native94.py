"""Actual Kodi WindowXML/progress/readback. Synthetic loopback XMLTV only."""
import gzip,json,sys,threading,time,traceback,hashlib,faulthandler
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import xbmc,xbmcgui,xbmcaddon
sys.path.insert(0,'/root/.kodi/addons/plugin.video.xtreammate/resources/lib')
import utils,portals,library_index,group_selection,epg,epg_sources,epg_jobs94
utils.ADDON=xbmcaddon.Addon('plugin.video.xtreammate');utils.ADDON_ID='plugin.video.xtreammate'
utils.ADDON.setSetting('xcmate_ui_language','de_de')
owner=threading.get_ident();monitor=xbmc.Monitor();stop=threading.Event();server=None;manager=None
stacks94=open('/root/epg94-stacks.txt','w');faulthandler.dump_traceback_later(25,repeat=True,file=stacks94)
def phase94(name):Path('/root/epg94-phase.txt').write_text(name);print('EPG94_PHASE '+name,flush=True)
report=dict(android='ANDROID_NOT_TESTED',native=True,transport='SYNTHETIC_LOOPBACK_XMLTV',events=[])
def wait(predicate,message,seconds=30):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  if manager and not manager._closed:manager.pump()
  if predicate():return
  if monitor.waitForAbort(.025):raise RuntimeError('KODI_ABORTED')
 raise AssertionError(message+' · '+json.dumps(dict(job=epg_jobs94.snapshot('epg94'),pending=bool(manager and manager._pending_future),phase=Path('/root/epg94-phase.txt').read_text() if Path('/root/epg94-phase.txt').exists() else 'unknown')))
def shot(name):
 file=Path('/root/'+name+'.png');xbmc.executebuiltin('TakeScreenshot('+str(file)+')',wait=False);wait(file.exists,'SCREENSHOT_MISSING');return file.name
try:
 now=int(time.time());stamp=lambda t:time.strftime('%Y%m%d%H%M%S +0000',time.gmtime(t))
 raw=('<tv><channel id="xml"><display-name>Native station</display-name></channel>'+''.join('<programme channel="xml" start="'+stamp(now+i*1800-1800)+'" stop="'+stamp(now+i*1800)+'"><title>Native programme '+str(i)+'</title><desc>'+''.join(hashlib.sha256((str(i)+':'+str(j)).encode()).hexdigest() for j in range(16))+'</desc></programme>' for i in range(600))+'</tv>').encode()
 compressed=gzip.compress(raw)
 class Handler(BaseHTTPRequestHandler):
  def log_message(self,*a):pass
  def do_GET(self):
   self.send_response(200);self.send_header('Content-Length',str(len(compressed)));self.send_header('Content-Encoding','gzip');self.end_headers()
   try:
    for i in range(0,len(compressed),4096):self.wfile.write(compressed[i:i+4096]);self.wfile.flush();time.sleep(.05)
   except (BrokenPipeError,ConnectionResetError):pass
 server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 portal=dict(id='epg94',name='Native source',type='xtream',enabled=True,xc_host='http://127.0.0.1:'+str(server.server_port),xc_user='synthetic',xc_pass='synthetic',provider_epg_enabled=True,epg_show=True,start_group_id='a',start_stream_id='1')
 portals.save_all([portal]);group_selection.save('epg94',['a'],'live')
 library_index.import_group('epg94','live','a',[dict(stream_id='1',category_id='a',name='Native station',epg_channel_id='xml')])
 from epg_manager53 import Manager53
 manager=Manager53('XCMateEPGManager53.xml',xbmcaddon.Addon('plugin.video.xtreammate').getAddonInfo('path'),'Default','720p');manager.configure(portal);manager.show()
 wait(lambda:manager.rows and manager._pending_future is None,'MANAGER_NOT_READY')
 assert not manager._init_error,repr(manager._init_error)
 original=utils.http_stream
 def worker_only(*a,**kw):
  assert threading.get_ident()!=owner,'GUI_NETWORK_IO'
  return original(*a,**kw)
 utils.http_stream=worker_only
 def poll():
  while not stop.wait(.05):epg.poll_refresh_request()
 worker=threading.Thread(target=poll,daemon=True);worker.start()
 phase94('first_request');manager.setFocusId(402);xbmc.executebuiltin('Action(Select)',wait=False)
 wait(lambda:epg_jobs94.read('epg94').get('state')=='RUNNING','SERVICE_ACK_MISSING')
 job=epg_jobs94.read('epg94');identity=job['id'];report['job_id']=identity;report['ack_seconds']=job['ack']-job['requested'];assert report['ack_seconds']<=15
 wait(lambda:epg_jobs94.read('epg94').get('sources',{}).get('provider',{}).get('bytes',0)>0,'WIRE_BYTES_MISSING')
 manager.setFocusId(200);manager.getControl(200).selectItem(0)
 Path('/root/epg94-observe.json').write_text(json.dumps(dict(ready=True)))
 wait(lambda:getattr(manager,'_job94',{}).get('sources',{}).get('provider',{}).get('phase')=='DOWNLOAD' and manager.getControl(200).getListItem(0).getProperty('Busy94')=='true','DOWNLOAD_NOT_RENDERED')
 report['download_screenshot']=shot('epg94-downloading')
 # Native RPC drives focus concurrently while this owner pumps.
 wait(lambda:Path('/root/epg94-input-complete').exists(),'NATIVE_INPUT_NOT_COMPLETED',10)
 report['list_identity_before']=len(manager.rows)
 wait(lambda:epg_jobs94.read('epg94').get('state') in epg_jobs94.TERMINAL,'IMPORT_NOT_COMPLETED',60)
 job=epg_jobs94.read('epg94');assert job['state']=='DONE',job
 wait(lambda:manager._job94.get('state')=='DONE','TERMINAL_UI_NOT_UPDATED')
 source=job['sources']['provider'];assert source['bytes']==len(compressed),(source,len(compressed));assert source['verified']==600 and source['matched']==1,source
 assert not manager.getControl(200).getListItem(0).getProperty('Busy94')
 assert manager.getControl(200).getSelectedPosition()==0
 phase94('first_readback_done');report['completed_screenshot']=shot('epg94-completed');report['source']=source
 report.update(status='PASS',wire_bytes_verified=True,cold_readback_rows=600,native_focus_usable=True,spinner_stopped=True,source_rows_preserved=len(manager.rows)==report['list_identity_before'])
 # A second real import is cancelled via the actual control during download.
 from guide_backup44 import authorize
 from guide_store import path
 phase94('backup_begin');backup94=[]
 manager._request(lambda:authorize(path()),backup94.append)
 wait(lambda:bool(backup94),'BACKUP_WORKER_NOT_COMPLETED')
 assert backup94[0]['code']=='BACKUP_VERIFIED';phase94('backup_done')
 assert __import__('epg_gate46').access(path())=='READY'
 wait(lambda:not epg._WARMUP_THREADS['epg94'].is_alive(),'PRIOR_WORKER_NOT_RETURNED')
 wait(lambda:manager._pending_future is None,'PRIOR_GUI_JOB_NOT_RETURNED')
 phase94('retry_request');manager.setFocusId(402);xbmc.executebuiltin('Action(Select)',wait=False);phase94('retry_submitted');wait(lambda:epg_jobs94.read('epg94').get('id')!=identity and epg_jobs94.read('epg94').get('state')=='RUNNING','RETRY_NOT_STARTED')
 wait(lambda:epg_jobs94.read('epg94').get('sources',{}).get('provider',{}).get('bytes',0)>0,'RETRY_NO_BYTES')
 wait(lambda:getattr(manager,'_job94',{}).get('id')==epg_jobs94.read('epg94')['id'],'CANCEL_UI_STALE')
 phase94('cancel_request');manager.setFocusId(413);xbmc.executebuiltin('Action(Select)',wait=False);phase94('cancel_submitted');wait(lambda:epg_jobs94.read('epg94').get('state')=='CANCELLED','CANCEL_NOT_ACKNOWLEDGED')
 from wizard_epg54 import stored
 assert stored(portal,'provider')['rows']==600
 report['cancel_preserved_lastgood']=True
 phase94('close_manager');xbmc.executebuiltin('Action(Back)',wait=False);wait(lambda:manager._closed,'NATIVE_BACK_NOT_CLOSED')
 report['back_closed_only_manager']=True
 Path('/root/epg94-finished.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
except BaseException:
 Path('/root/epg94-error.tmp').write_text(traceback.format_exc());Path('/root/epg94-error.tmp').replace('/root/epg94-error.txt');raise
finally:
 faulthandler.cancel_dump_traceback_later();stop.set()
 if manager and not manager._closed:manager.close()
 if server:server.shutdown();server.server_close()
