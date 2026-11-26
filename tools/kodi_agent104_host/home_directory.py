"""Disposable catalogue for production Live TV ListItem decoration."""
from pathlib import Path
import sys
from urllib.parse import parse_qs

import xbmcplugin

sys.path.insert(0, str(Path(__file__).parent / 'resources/lib'))
from live_rail86 import values
from widget_items45 import item

params = parse_qs(sys.argv[2].lstrip('?'))
handle = int(sys.argv[1])
if params.get('action') == ['widget_live_start_group'] and params.get('pid') == ['fixture59']:
    portal = {'id': 'fixture59', 'name': 'Public EPG replay', 'type': 'xtream'}
    rows = [dict(sid='1', name='13th Street', epg_channel_id='s1.13th.Street.Universal.de'),
            dict(sid='2', name='Comparison station', epg_channel_id='fixture-without-epg')]
    xbmcplugin.setContent(handle, 'videos')
    for row in values(portal, rows):
        xbmcplugin.addDirectoryItem(handle, row['url'], item(row), isFolder=False)
xbmcplugin.endOfDirectory(handle, cacheToDisc=False)
