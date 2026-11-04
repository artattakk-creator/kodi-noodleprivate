"""Real Kodi background dialog, native input + complete persisted catalog job."""
import json
import sys
import threading
import time
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit,parse_qs
import xbmc,xbmcgui,xbmcaddon
sys.path.insert(0,'/root/.kodi/addons/plugin.video.xtreammate/resources/lib')
import utils
utils.ADDON=xbmcaddon.Addon('plugin.video.xtreammate');utils.ADDON_ID='plugin.video.xtreammate'
import portals,library_index as index,group_selection as selection
import catalog_jobs73 as jobs,catalog_progress73 as progress
owner=threading.get_ident();requests=[]
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  q=parse_qs(urlsplit(self.path).query);action=q.get('action',['AUTH'])[0];requests.append(action)
  if action=='AUTH':value={'user_info':{'auth':1,'status':'Active'}}
  elif action.endswith('_categories'):value=[{'category_id':'a','category_name':'Synthetic native group'}]
  else:
   time.sleep(.8)
   key='series_id' if action=='get_series' else 'stream_id'
   value=[{key:'1','category_id':'a','name':'Synthetic native title'}]
  raw=json.dumps(value).encode();self.send_response(200);self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
portal=dict(id='catalog73',name='Synthetic',type='xtream',enabled=True,xc_host='http://127.0.0.1:'+str(server.server_port),xc_user='synthetic-user',xc_pass='synthetic-password',include_vod=True,include_series=True,start_group_id='a',start_stream_id='1')
portals.save_all([portal])
for kind in jobs.KINDS:selection.save(portal['id'],['a'],kind)
jobs.request(portal)
original=(utils.http_get,utils.http_stream)
def off_owner(fn):
 def call(*a,**kw):
  assert threading.get_ident()!=owner,'GUI_NETWORK_IO'
  return fn(*a,**kw)
 return call
utils.http_get=off_owner(original[0]);utils.http_stream=off_owner(original[1])
stop=threading.Event();errors=[]
def work():
 try:
  while not stop.is_set():
   jobs.run_next(stop.is_set);progress.prepare()
   if jobs.jobs()[-1]['state'] in ('DONE','FAILED'):return
   time.sleep(.1)
 except BaseException as exc:errors.append(type(exc).__name__)
thread=threading.Thread(target=work,daemon=True);thread.start()
observed=False;ready=False;monitor=xbmc.Monitor();started=time.monotonic()
try:
 while thread.is_alive() and time.monotonic()-started<45:
  progress.poll()
  if progress._dialog is not None and not xbmc.getCondVisibility('System.HasActiveModalDialog'):
   observed=True
   if not ready:
    Path('/root/catalog73-observe.json').write_text(json.dumps(dict(nonmodal=True,window=xbmcgui.getCurrentWindowId())))
    ready=True
  if monitor.waitForAbort(.05):break
 thread.join(1);progress.poll()
 row=jobs.jobs()[-1]
 assert not errors,errors
 assert row['state']=='DONE',row['code']
 assert observed
 assert row['readback']==dict(live=1,vod=1,series=1)
 assert portals.get_by_id(portal['id'])==portal
 Path('/root/catalog73-finished.json').write_text(json.dumps(dict(native_nonmodal_progress='PASS',worker_network_off_owner=True,
    actual_group_commits=3,readback=row['readback'],requests=requests,android='NOT_TESTED',production_profiles=False)))
finally:
 stop.set();thread.join(1);server.shutdown();server.server_close()
