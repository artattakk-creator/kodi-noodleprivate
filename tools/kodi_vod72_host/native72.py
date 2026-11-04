"""Native Kodi UI + real worker transport/index; synthetic account only."""
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import threading
from urllib.parse import parse_qs, urlsplit
import xbmcgui
import xbmc

sys.path.insert(0, '/root/.kodi/addons/plugin.video.xtreammate/resources/lib')
import utils
import xbmcaddon
# The harness is a separate script interpreter; select the actual XCMate
# profile explicitly before seeding. Production runs from XCMate itself.
utils.ADDON=xbmcaddon.Addon('plugin.video.xtreammate')
utils.ADDON_ID='plugin.video.xtreammate'
import portals
import library_index as index
import group_selection as selection
import vodsync72
import vodsync_ui72
import menu_icons45

owner = threading.get_ident(); requests = []
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass
    def do_GET(self):
        q=parse_qs(urlsplit(self.path).query); action=q.get('action',['AUTH'])[0]; requests.append(action)
        value={
          'AUTH':{'user_info':{'auth':1,'status':'Active'}},
          'get_vod_categories':[{'category_id':'v','category_name':'Synthetic films'}],
          'get_series_categories':[{'category_id':'s','category_name':'Synthetic series'}],
          'get_vod_streams':[{'stream_id':'m1','category_id':'v','name':'Synthetic film 72'}],
          'get_series':[{'series_id':'s1','category_id':'s','name':'Synthetic series 72'}],
        }[action]
        raw=json.dumps(value).encode();self.send_response(200);self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
portal=dict(id='vod72',name='Synthetic existing provider',type='xtream',enabled=True,xc_host='http://127.0.0.1:'+str(server.server_port),
            xc_user='synthetic-test-user',xc_pass='synthetic-test-password',include_vod=False,include_series=False,start_group_id='1')
portals.save_all([portal])
index.replace_catalog(portal['id'],'live',[dict(stream_id=str(i),category_id=str(i%53),name='Synthetic live '+str(i)) for i in range(3357)],
                      [dict(category_id=str(i),category_name='Synthetic group '+str(i)) for i in range(53)])
selection.save(portal['id'],[str(i) for i in range(53)],'live');selection.save(portal['id'],[],'vod');selection.save(portal['id'],[],'series')

def live_digest():
    db=index.connect()
    try:return hashlib.sha256(json.dumps([tuple(row) for row in db.execute("SELECT * FROM readable_titles WHERE kind='live' ORDER BY sid")]).encode()).hexdigest()
    finally:db.close()
before=live_digest()
original_http_get,original_stream=utils.http_get,utils.http_stream
def off_owner(fn):
    def call(*args,**kwargs):
        assert threading.get_ident()!=owner,'NETWORK_ON_GUI_OWNER'
        return fn(*args,**kwargs)
    return call
utils.http_get=off_owner(original_http_get);utils.http_stream=off_owner(original_stream)
actual=vodsync72.Session
class Captured(actual):
    def run(self,*args,**kwargs):
        report=super().run(*args,**kwargs)
        assert report['state']=='DONE',report
        Path('/root/vod72-worker.json').write_text(json.dumps(report))
        return report
vodsync72.Session=Captured
# Only dialog answers are fixtures; the WindowXML, progress owner, actual
# Start/Back input and production worker/database code are real native Kodi.
original_dialog=xbmcgui.Dialog
class Answers:
    def yesno(self,*args,**kwargs):return True
    def ok(self,*args,**kwargs):return original_dialog().ok(*args,**kwargs)
xbmcgui.Dialog=Answers
menu_icons45.multiselect=lambda dialog,heading,items,**kwargs:list(range(len(items)))
try:
    vodsync_ui72.show(portal)
    assert live_digest()==before
    assert index.Reader(portal['id']).page('live',limit=1)[1]==3357
    assert len(index.Reader(portal['id']).groups('live'))==53
    assert index.Reader(portal['id']).page('vod',limit=1)[1]==1
    assert index.Reader(portal['id']).page('series',limit=1)[1]==1
    assert all('live' not in action and 'epg' not in action for action in requests)
    assert len(portals.load_all())==1
    assert portals.get_by_id(portal['id'])['xc_pass']==portal['xc_pass']
    Path('/root/vod72-finished.json').write_text(json.dumps(dict(native_owner_progress_start_back='PASS',live_rows=3357,live_groups=53,live_digest_unchanged=True,
        vod_rows=1,series_rows=1,scope_requests=requests,synthetic_dialog_answers=True,production_profiles=False,installer_executed=False,android='NOT_TESTED')))
finally:
    xbmcgui.Dialog=original_dialog
    server.shutdown();server.server_close()
