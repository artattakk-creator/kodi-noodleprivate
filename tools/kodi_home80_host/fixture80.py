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
 subprocess.Popen([sys.executable,'/media80.py'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
