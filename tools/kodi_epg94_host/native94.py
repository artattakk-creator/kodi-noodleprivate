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
 portal=dict(id='epg94',name='Native source',type='xtream',enabled=True,xc_host='http://127.0.0.1:'+str(server.server_port),xc_user='synthetic',xc_pass='synthetic',provider_epg_enabled=False,epg_show=False,epg_opt_out94=True,provider_epg_opt_out94=True,start_group_id='a',start_stream_id='1')
 portals.save_all([portal]);group_selection.save('epg94',['a'],'live')
 library_index.import_group('epg94','live','a',[dict(stream_id='1',category_id='a',name='Native station',epg_channel_id='xml')])
 from epg_manager53 import Manager53
 manager=Manager53('XCMateEPGManager53.xml',xbmcaddon.Addon('plugin.video.xtreammate').getAddonInfo('path'),'Default','720p');manager.configure(portal);manager.show()
 wait(lambda:manager.rows and manager._pending_future is None,'MANAGER_NOT_READY')
 assert not manager._init_error,repr(manager._init_error)
 saved=portals.get_by_id('epg94')
 assert saved['epg_show'] and saved['provider_epg_enabled'] and saved['provider_baseline96'],saved
 prior=saved['provider_baseline_history96'][0]['values']
 assert prior==dict(epg_show=False,provider_epg_enabled=False,epg_opt_out94=True,provider_epg_opt_out94=True),prior
 assert not xbmc.getCondVisibility('Control.IsEnabled(410)')
 assert manager.rows[0]['enabled'] and manager.rows[0]['id']=='provider'
 report['provider_baseline96']=dict(verified=True,legacy_flags_archived=True)
 # Optional sources retain their own switch and are never enabled by baseline.
 optional=epg_sources.add_source('epg94','Disabled optional source',portal['xc_host']+'/optional.xml')
 epg_sources.edit_source('epg94',optional['id'],'toggle')
 optional_before=epg_sources.configuration('epg94')['sources']
 assert len(optional_before)==1 and optional_before[0]['enabled'] is False
 manager._load();wait(lambda:manager._pending_future is None,'OPTIONAL_SOURCE_LIST_NOT_READY')
 assert len(manager.rows)==2 and manager.rows[1]['enabled'] is False
 portal=saved
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
 # .95 gate proof runs on the existing owner worker, with slow I/O and >128 entries.
 gate95=[]
 def verify95():
  import sqlite3
  from unittest import mock
  folder=Path(path()).parent/'guide_backups44'
  for n in range(150):(folder/('unrelated-native-'+str(n))).write_text('USER_DATA')
  real=sqlite3.connect
  class Slow(sqlite3.Connection):
   def execute(self,sql,*a,**k):
    if sql.startswith('SELECT 1 FROM programmes'):time.sleep(.08)
    return super().execute(sql,*a,**k)
  with mock.patch.object(sqlite3,'connect',side_effect=lambda *a,**k:real(*a,**dict(k,factory=Slow))):
   return __import__('epg_gate95').inspect(path())
 manager._request(verify95,gate95.append);wait(lambda:bool(gate95),'GATE95_WORKER_NOT_COMPLETED')
 assert gate95[0]['code']=='IMPORT_AUTHORIZED',gate95
 report['gate95']=gate95[0]
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
 assert epg_sources.configuration('epg94')['sources']==optional_before
 report['provider_baseline96']['optional_source_preserved']=True
 # Actual native mapping dialog + shared MiniAdapter, with a synthetic parent.
 # This is a cancel-preview smoke, not a receiver/Android longpress acceptance.
 phase94('mini_mapping96_cancel_preview')
 from types import SimpleNamespace
 from tv_data import GuideSnapshot
 from mapping_context96 import MiniAdapter
 from guide_mapping48 import MappingWindow48
 from source_adapters import for_portal
 snapshot=GuideSnapshot(portal,for_portal(portal))
 snapshot._values['1']=dict(now='Original native snapshot',start=now-60,stop=now+3600,events=[])
 channel=SimpleNamespace(name='Native station',tvg_id='xml',extra=dict(stream_id='1',category_id='a'))
 restored_focus=[]
 parent=SimpleNamespace(portal=portal,_guide=snapshot,_closed=False,mode='channels',category_id='a',
     _page_start=0,_row_offset=0,_highlight={'channels':0},_mini=SimpleNamespace(focused=False,signature='original'),
     control=SimpleNamespace(getId=lambda:501,getSelectedPosition=lambda:0),visible_channels=[channel],
     getFocusId=lambda:501,setFocusId=restored_focus.append,_render=lambda **kw:None)
 adapter=MiniAdapter(parent,channel)
 child=MappingWindow48('XCMateMapping48.xml',xbmcaddon.Addon('plugin.video.xtreammate').getAddonInfo('path'),'Default','720p')
 child.configure(parent,adapter)
 before=(Path(path()).read_bytes(),Path(epg_sources._file_path()).read_bytes())
 try:
  child._shown=True;child.show();wait(lambda:child._ready,'MINI_MAPPING96_NOT_READY')
  child.source=dict(id='provider',name='Anbieter-EPG');child.candidate=dict(id='xml',name='Native station')
  child._preview()
  def preview_ready96():
   child.pump();return child.previewed
  wait(preview_ready96,'MINI_MAPPING96_PREVIEW_FAILED')
  assert snapshot.get('1',time.time())['mapping']=='PREVIEW_RAM96'
  assert before==(Path(path()).read_bytes(),Path(epg_sources._file_path()).read_bytes())
  child.onClick(406)
 finally:
  child.close();adapter.finish(False);snapshot.close()
 assert not child.saved and not snapshot._preview96
 assert snapshot.get('1',time.time())['now']=='Original native snapshot'
 assert restored_focus==[501],restored_focus
 assert before==(Path(path()).read_bytes(),Path(epg_sources._file_path()).read_bytes())
 report['mini_mapping96']=dict(native_dialog=True,parent='SYNTHETIC_MINI_ADAPTER_OWNER',preview_bytes_unchanged=True,cancel_restored=True,android='ANDROID_NOT_TESTED')
 # Issue474: actual native Save/worker/cold-readback/apply and failed-write dialog.
 phase94('mapping474_save')
 adapter=MiniAdapter(parent,channel)
 child=MappingWindow48('XCMateMapping48.xml',xbmcaddon.Addon('plugin.video.xtreammate').getAddonInfo('path'),'Default','720p')
 child.configure(parent,adapter)
 try:
  child._shown=True;child.show();wait(lambda:child._ready,'MAPPING474_NOT_READY')
  child.source=dict(id='provider',name='Anbieter-EPG');child.candidate=dict(id='xml',name='Native station')
  child._preview()
  def ready474():child.pump();return child.previewed
  wait(ready474,'MAPPING474_PREVIEW_FAILED');child.onClick(405)
  def saved474():child.pump();return child.saved
  wait(saved474,'MAPPING474_SAVE_FAILED')
  assert child._closed
  manual474=epg_sources.configuration(portal['id'])['source_mappings48']['1']
  assert manual474==dict(channel='xml',source='provider'),manual474
  assert snapshot.get('1',time.time())['mapping']=='MANUAL'
 finally:
  child.close();adapter.finish(child.saved)
 phase94('mapping474_write_failure')
 before474=Path(epg_sources._file_path()).read_bytes()
 adapter=MiniAdapter(parent,channel)
 child=MappingWindow48('XCMateMapping48.xml',xbmcaddon.Addon('plugin.video.xtreammate').getAddonInfo('path'),'Default','720p')
 child.configure(parent,adapter);write474=epg_sources._write_all
 try:
  child._shown=True;child.show();wait(lambda:child._ready,'MAPPING474_RETRY_NOT_READY')
  child.source=dict(id='provider',name='Anbieter-EPG');child.candidate=dict(id='xml',name='Native station');child._preview()
  wait(ready474,'MAPPING474_RETRY_PREVIEW_FAILED')
  def failed_write474(*a,**k):raise OSError('SYNTHETIC_FAILURE')
  epg_sources._write_all=failed_write474;child.onClick(405)
  def failed474():
   child.pump();return child.future is None and not child._saving53
  wait(failed474,'MAPPING474_FAILURE_NOT_RETURNED')
  assert not child.saved and not child._closed
  assert 'MAPPING_WRITE_FAILED' in child.getControl(103).getText()
  assert before474==Path(epg_sources._file_path()).read_bytes()
 finally:
  epg_sources._write_all=write474;child.close();adapter.finish(False);snapshot.close()
 report['mapping474']=dict(native_dialog=True,parent='SYNTHETIC_MINI_ADAPTER_OWNER',save_cold_readback=True,
     actual_snapshot_applied=True,write_failure_kept_open=True,write_failure_preserved_bytes=True,android='ANDROID_NOT_TESTED')
 Path('/root/epg94-finished.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
except BaseException:
 Path('/root/epg94-error.tmp').write_text(traceback.format_exc());Path('/root/epg94-error.tmp').replace('/root/epg94-error.txt');raise
finally:
 faulthandler.cancel_dump_traceback_later();stop.set()
 if manager and not manager._closed:manager.close()
 if server:server.shutdown();server.server_close()
