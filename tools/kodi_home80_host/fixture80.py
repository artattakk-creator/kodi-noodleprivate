"""Isolated provider fixture; real XCMate actions/owners/resolver/Kodi player."""
import sys,subprocess
from pathlib import Path
from urllib.parse import parse_qs
import xbmcaddon
root=Path(xbmcaddon.Addon('plugin.video.xtreammate').getAddonInfo('path'))
sys.path.insert(0,str(root/'resources/lib'))
from xtream import XtreamClient
original80=XtreamClient._get_json
def fixture_json80(self,action,*a,**k):
 if action=='get_vod_info':return dict(info=dict(name='Synthetic native movie',plot='Native .80 movie detail'),movie_data=dict(stream_id='0',container_extension='mp4'))
 if action=='get_short_epg':return {}
 return original80(self,action,*a,**k)
XtreamClient._get_json=fixture_json80
def stream80(self,sid,extension='mp4'):
 if str(sid)!='0':raise ValueError('UNEXPECTED_SYNTHETIC_MOVIE')
 return 'http://127.0.0.1:18380/sample.mp4'
XtreamClient.vod_stream_url=stream80
exec(compile(Path('/base_fixture75.py').read_text(),'/base_fixture75.py','exec'),globals())
if parse_qs(sys.argv[2].lstrip('?')).get('fixture59')==['seed']:
 # fixture75 adds its landscape source after fixture74's first snapshot.
 # A fast runner can legitimately retain that old 15-s snapshot. Finish the
 # synthetic import through the real background revision path before opening
 # the ready-profile UI; do not delete caches or replace renderer behavior.
 from portals import get_active
 from widget_data41 import snapshot
 from programme_assets47 import prepare,read_many
 from widget_refresh45 import publish
 portal80=get_active()[0];rows80,code80=snapshot(portal80,'vod',background=True)
 prepare(portal80,'vod',rows80,provider_only=True)
 references80=read_many(portal80['id'],'vod',rows80,provider_only=True)
 if not references80.get('0',{}).get('fanart'):raise RuntimeError('FIXTURE80_FANART_SEED_UNCONFIRMED')
 if not publish(portal80,'vod',rows80,code80):raise RuntimeError('FIXTURE80_FRAME_UNCONFIRMED')
 subprocess.Popen([sys.executable,'/media80.py'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
