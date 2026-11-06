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
source77=original.read_text()
marker77=" import_cache(portal['id'],events,'synthetic-home60',now=now,trusted_feed=True)"
assert source77.count(marker77)==1
source77=source77.replace(marker77," events['xml5'][0]['icon']='https://image.tmdb.org/t/p/w500/url69-5.jpg'\n events['xml6'][0]['icon']='https://image.tmdb.org/t/p/w500/url69-6.jpg'\n"+marker77)
exec(compile(source77,str(original),'exec'),globals())
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

    # .77 end-to-end contract: configured XMLTV event -> real TLS response ->
    # full Pillow decode -> common URL cache -> native Hero and EPG texture.
    # DNS exception is ONLY this isolated synthetic loopback TLS origin.
    from unittest import mock
    import download_redirect
    from programme_events46 import load
    from programme_urls55 import resolve
    from programme_requests68 import completed
    from library_index import Reader
    def isolated77(url,*args,**kwargs):
        from urllib.parse import urlsplit
        parsed=urlsplit(url)
        if parsed.hostname!='image.tmdb.org' or not parsed.path.startswith('/t/p/w500/url69-'):raise AssertionError('UNEXPECTED_FIXTURE_NETWORK77')
        return ['127.0.0.1']
    evidence=[]
    with mock.patch.object(download_redirect,'addresses',side_effect=isolated77):
        for sid in ('5','6'):
            channel=Reader(portal['id']).get('live',sid)
            event=load(portal,channel)
            value=resolve(event,allow_lookup=False,url_mode69=True)
            if value.get('code')!='READY' or not value.get('decoded77'):raise RuntimeError('IMAGE77_PIPELINE_FAILED '+str(value.get('code')))
            completed(event,value)
            evidence.append(dict(sid=sid,event=event['key'],decoded=value['decoded77'],width=value['image_width77'],height=value['image_height77'],source=value['source']))
    Path('/root/image77-source.json').write_text(__import__('json').dumps(evidence))
