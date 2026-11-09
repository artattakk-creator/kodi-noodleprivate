"""Fresh synthetic provider; no archive images. Never used on a real device."""
import sys,json,time,shutil,collections,importlib.util
from pathlib import Path
from urllib.parse import parse_qs
import xbmc,xbmcaddon,xbmcplugin,xbmcgui
native_addon84=xbmcaddon.Addon
xbmcaddon.Addon=lambda *a,**k:native_addon84(*a,**k) if a or k else native_addon84('plugin.video.xtreammate')
root=Path(__file__).parent
sys.path.insert(0,str(root/'resources/lib'))
BASE='https://image.tmdb.org/t/p/w500/'

def install():
    # Fault injection affects XCMate Python capacity observations only. Kodi's
    # C++ texture writer still uses actual host capacity. Not a physical-full test.
    import artwork_visible,download_redirect
    original=shutil.disk_usage
    if not getattr(original,'fault84',False):
        def usage(path):
            if 'plugin.video.xtreammate' in str(path):return collections.namedtuple('usage','total used free')(4034297856,4034297856-27*1024**2,27*1024**2)
            return original(path)
        usage.fault84=True;shutil.disk_usage=usage
    def dns(url):
        from urllib.parse import urlsplit
        if urlsplit(url).hostname!='image.tmdb.org':raise AssertionError('FIXTURE84_UNEXPECTED_ORIGIN')
        artwork_visible._dns_cache[('image.tmdb.org',443)]=(time.monotonic()+30,True)
        return True
    artwork_visible.public_dns=dns
    # Only the synthetic TLS origin is pinned to loopback in this disposable
    # fixture. Production URL/DNS/credential/redirect code remains unchanged.
    download_redirect.addresses=lambda url:['127.0.0.1'] if url.startswith(BASE) else (_ for _ in ()).throw(AssertionError('UNEXPECTED84_ORIGIN'))
    __import__('artwork_display84').observe(force=True)

def seed():
    from utils import addon_data_dir
    from library_index import replace_catalog
    import portals
    portal=dict(id='fixture59',name='Synthetic .84 only',type='xtream',enabled=True,xc_host='https://provider.example.test',xc_user='fixture',xc_pass='synthetic',include_live=True,include_vod=True,include_series=True,start_group_id='a',start_stream_id='0',autoplay_start=False)
    portals.save_all([portal]);data=Path(addon_data_dir())
    (data/'artwork_config_v1.json').write_text(json.dumps(dict(version=1,mode='internal',strategy='demand',target='',profile='1'*32)))
    for kind in ('vod','series'):
        rows=[dict(name='Synthetic '+kind+' '+str(i),stream_id=str(i),series_id=str(i),category_id='a',added=int(time.time())-i,cover=BASE+kind+'84-'+str(i)+'.png',stream_icon=BASE+kind+'84-'+str(i)+'.png',backdrop_path=[BASE+'fanart84-'+str(i)+'.png'],plot='Synthetic provider description',year='2026') for i in range(24)]
        replace_catalog(portal['id'],kind,rows,[dict(category_id='a',category_name='Synthetic media')])
    stations=[dict(stream_id=str(i),name='Station '+str(i),category_id='a',epg_channel_id='xml'+str(i),stream_icon=BASE+'logo84-'+str(i)+'.png') for i in range(88)]
    replace_catalog(portal['id'],'live',stations,[dict(category_id='a',category_name='Synthetic start group')])
    from guide_store import import_cache
    now=int(time.time());events={}
    for i in range(88):
        events['xml'+str(i)]=[dict(name='Synthetic event '+str(i),title='Synthetic event '+str(i),channel='xml'+str(i),descr='Exact synthetic programme description',category='Spielfilm',year=2024,icon=BASE+'event84-'+str(i)+'.png',start_timestamp=now-600,stop_timestamp=now+7200),dict(name='Next '+str(i),channel='xml'+str(i),descr='Next programme',start_timestamp=now+7200,stop_timestamp=now+14400)]
    import_cache(portal['id'],events,'synthetic84',now=now,trusted_feed=True)
    addon=xbmcaddon.Addon();addon.setSetting('programme_art_local69','false');addon.setSetting('programme_helper57','false');addon.setSetting('programme_catalog57','false')
    addon.setSetting('tmdb_read_token43','SYNTHETIC84_UNCHANGED_NOT_A_REAL_TOKEN')
    Path('/root/baseline84.json').write_text(json.dumps({str(p):__import__('hashlib').sha256(p.read_bytes()).hexdigest() for p in (data/'portals.json',data/'artwork_config_v1.json')}))

def run():
    p=parse_qs(sys.argv[2].lstrip('?'));handle=int(sys.argv[1])
    if p.get('fixture59')==['seed']:
        seed();xbmcplugin.addDirectoryItem(handle,'fixture',xbmcgui.ListItem('Seeded'),False);xbmcplugin.endOfDirectory(handle);return
    if p.get('fixture66'):
        # Existing personal cinema row remains real; its source is independent.
        for i in range(8):
            item=xbmcgui.ListItem('Cinema '+str(i));item.setInfo('video',dict(title='Cinema '+str(i),mediatype='movie'));item.setArt(dict(poster=BASE+'vod84-'+str(i)+'.png'))
            xbmcplugin.addDirectoryItem(handle,'plugin://plugin.video.xtreammate/?fixture84=disabled',item,False)
        xbmcplugin.setContent(handle,'movies');xbmcplugin.endOfDirectory(handle);return
    install()
    spec=importlib.util.spec_from_file_location('real_default84',root/'default.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.run()
if __name__=='__main__':run()
