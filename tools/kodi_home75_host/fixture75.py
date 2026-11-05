"""Reuse .74 synthetic provider; add one verified provider fanart fixture."""
import runpy,sys,hashlib
from pathlib import Path
from urllib.parse import parse_qs
import xbmcaddon
_native_addon=xbmcaddon.Addon
xbmcaddon.Addon=lambda *a,**k:_native_addon(*a,**k) if a or k else _native_addon('plugin.video.xtreammate')
parameters=parse_qs(sys.argv[2].lstrip('?'))
original=Path(__file__).with_name('fixture74.py')
# Preserve Kodi's plugin:// sys.argv[0]; runpy.run_path temporarily replaces it
# by a filesystem path, which would make native child-directory URLs invalid.
exec(compile(original.read_text(),str(original),'exec'),globals())
if parameters.get('fixture59')==['seed']:
    import xbmcaddon
    sys.path.insert(0,str(Path(xbmcaddon.Addon('plugin.video.xtreammate').getAddonInfo('path'))/'resources/lib'))
    from portals import get_active
    from widget_data41 import snapshot
    from library_index import replace_catalog
    from utils import addon_data_dir
    from PIL import Image
    portal=get_active()[0];rows,code=snapshot(portal,'vod')
    uri='https://provider.example.test/fanart75.png'
    for row in rows:
        row['stream_id']=row['sid']
        if row['sid']=='0':row.update(backdrop_path=uri,genre='Drama',cast='Synthetic Actor A, Synthetic Actor B',duration_secs=5400,mpaa='12')
    folder=Path(addon_data_dir())/'media_art_v1'
    Image.new('RGB',(160,90),(180,100,30)).save(folder/(hashlib.sha256(uri.encode()).hexdigest()+'.img'),format='PNG')
    replace_catalog(portal['id'],'vod',rows,[dict(category_id='a',category_name='Synthetic group')])
