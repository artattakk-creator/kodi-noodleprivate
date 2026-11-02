"""Synthetic controller state; real released-guide and mini tuning methods."""
import sys,json,types
from pathlib import Path
import xbmc,xbmcgui,xbmcaddon
native=xbmcaddon.Addon;xbmcaddon.Addon=lambda *a,**k:native(*a,**k) if a or k else native('plugin.video.xtreammate')
sys.path.insert(0,native('plugin.video.xtreammate').getAddonInfo('path')+'/resources/lib')
from portals import get_by_id
from library_index import Reader
portal=get_by_id('fixture67');kind=json.loads(Path('/root/command67.json').read_text())['kind']
if kind=='guide':
 from guide_playback import request,handoff,player_state
 from home_entry import HomeRouter
 row=Reader('fixture67').get('live','3')
 router=HomeRouter(['plugin://plugin.video.xtreammate/','-1',''])
 intent=request(portal,row,player_state(),dict(surface='window',window=13999,owner='synthetic67'))
 Path('/root/guide67.json').write_text(json.dumps(dict(dispatched=handoff(router,portal,intent))))
elif kind=='mini':
 from iptv import Channel
 from xtream import XtreamClient
 from live_overlay import LiveNavigator
 channel=Channel(name='Synthetic mini',url=XtreamClient(portal['xc_host'],portal['xc_user'],portal['xc_pass']).live_stream_url('4'),logo='',group='a',extra=dict(stream_id='4',category_id='a'))
 owner=types.SimpleNamespace(sid='3',index=types.SimpleNamespace(by_sid={'4':channel}),_guide=types.SimpleNamespace(request=lambda rows:None),_switch=lambda mode:None,portal=portal)
 LiveNavigator._tune(owner,channel)
