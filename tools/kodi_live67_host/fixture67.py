"""Only fixture actions seed isolated state; real requests use production default."""
import sys,importlib.util
from pathlib import Path
from urllib.parse import parse_qs
import xbmcaddon,xbmcplugin
root=Path(__file__).parent;sys.path.insert(0,str(root/'resources/lib'))
params=parse_qs(sys.argv[2].lstrip('?'));handle=int(sys.argv[1])
if params.get('fixture67')==['seed']:
 from library_index import replace_catalog
 from utils import addon_data_dir
 import portals
 portal=dict(id='fixture67',name='Synthetic only',type='xtream',enabled=True,xc_host='http://127.0.0.1:18081',xc_user='synthetic',xc_pass='fixture',include_live=True,include_vod=False,include_series=False,start_group_id='a',start_stream_id='2',autoplay_start=False)
 portals.save_all([portal])
 replace_catalog('fixture67','live',[dict(stream_id=str(i),name='Synthetic '+str(i),category_id='a',epg_channel_id='xml'+str(i)) for i in range(1,7)],[dict(category_id='a',category_name='Synthetic group')])
 # Only the disposable container profile is deliberately corrupt.
 (Path(addon_data_dir())/'guide_v1.sqlite').write_bytes(b'SYNTHETIC CORRUPT GUIDE')
 xbmcplugin.endOfDirectory(handle)
elif params.get('fixture67')==['configure']:
 xbmcaddon.Addon().setSetting('live_stream_format67',params['format'][0]);xbmcaddon.Addon().setSetting('use_inputstream_hls','false')
 actual=xbmcaddon.Addon().getSetting('live_stream_format67')
 if actual!=params['format'][0]:raise RuntimeError('NATIVE_FORMAT_SETTING_NOT_APPLIED '+repr(actual))
 xbmcplugin.endOfDirectory(handle,cacheToDisc=False)
else:
 spec=importlib.util.spec_from_file_location('actual_default67',root/'default.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.run()
