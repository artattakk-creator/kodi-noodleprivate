"""Native regression plus real TLS provider covers, Kodi cache and cold proof."""
from pathlib import Path
source79=Path('/base_gui79.py').read_text(encoding='utf-8').replace("Path('/root/home75.json')","Path('/root/home75-base79.json')")
exec(compile(source79,'native-home-base79','exec'),globals())
import widget_cache79 as cache79,widget_runtime79 as runtime79
from artwork_config import choose
from widget_data41 import snapshot
from library_index import replace_catalog
from portals import get_active
import artwork_visible
from urllib.parse import urlsplit
portal79=get_active()[0];choose('dynamic')  # explicit fixture action, never a product migration
for kind79,suffix79 in (('vod','5'),('series','6')):
 rows79,_=snapshot(portal79,kind79)
 for row79 in rows79:
  row79['stream_id']=row79['series_id']=row79['sid']
  if row79['sid']=='0':row79.update(cover='https://image.tmdb.org/t/p/w500/url69-'+suffix79+'.jpg',stream_icon='https://image.tmdb.org/t/p/w500/url69-'+suffix79+'.jpg',backdrop_path='')
 replace_catalog(portal79['id'],kind79,rows79,[dict(category_id='a',category_name='Synthetic group')])
 snapshot(portal79,kind79,background=True)
original_dns79=artwork_visible.public_dns
# Isolated TLS fixture only. Production private-address rejection is separately
# tested; certificate/SNI/image decode and Kodi Curl remain real.
def isolated_dns79(url):
 p=urlsplit(url)
 if p.hostname=='image.tmdb.org' and p.path in ('/t/p/w500/url69-5.jpg','/t/p/w500/url69-6.jpg'):
  with artwork_visible._lock:artwork_visible._dns_cache[(p.hostname,443)]=(time.monotonic()+30,True)
  return True
 return original_dns79(url)
artwork_visible.public_dns=isolated_dns79
proof79=[]
for kind79,cid79,color79 in (('vod',2520,(25,145,100)),('series',2530,(145,70,120))):
 __import__('widget_fast69')._next=0;__import__('widget_fast69').prepare();home.setProperty('XCMate.Widget45.Reload.'+kind79,'new-provider79-'+kind79)
 for _ in range(100):
  home.setFocusId(cid79);home.getControl(cid79).selectItem(0);xbmc.sleep(100)
  art79=xbmc.getInfoLabel('ListItem.Art(poster)')
  expected79=cache79.read(portal79,kind79,snapshot(portal79,kind79)[0]).get('0',{}).get('poster')
  if art79.startswith('https://image.tmdb.org/') or expected79 and art79==expected79:break
 else:raise RuntimeError('NATIVE79_PROVIDER_REFERENCE_NOT_LOADED')
 for paint79 in range(15):
  xbmc.sleep(200);path79,rgb79=capture('home75-dynamic79-'+kind79)
  if max(abs(a-b) for a,b in zip(rgb79.getpixel((800,150)),color79))<=8:break
 else:
  Path('/root/cache79-error.json').write_text(json.dumps(dict(stage='INITIAL_TLS_PIXELS',pixel=rgb79.getpixel((800,150)),poster=xbmc.getInfoLabel('ListItem.Art(poster)'),fanart=xbmc.getInfoLabel('ListItem.Art(fanart)'),landscape=xbmc.getInfoLabel('ListItem.Art(landscape)'),kind=xbmc.getInfoLabel('ListItem.Property(XCMate.WidgetKind41)'))))
  raise RuntimeError('NATIVE79_INITIAL_TLS_PIXELS')
 rows79,_=snapshot(portal79,kind79)
 for _ in range(100):
  cache79._due.clear();cache79.prepare(portal79,kind79,rows79)
  retained79=cache79.read(portal79,kind79,rows79).get('0',{}).get('poster')
  if retained79:break
  xbmc.sleep(100)
 else:
  Path('/root/cache79-error.json').write_text(xbmc.executeJSONRPC(json.dumps(dict(jsonrpc='2.0',id=79,method='Textures.GetTextures',params=dict(properties=['url','cachedurl','sizes'])))))
  raise RuntimeError('NATIVE79_KODI_CACHE_NOT_VERIFIED')
 proof79.append(dict(kind=kind79,file_sha256=hashlib.sha256(Path(retained79).read_bytes()).hexdigest(),source='synthetic provider HTTPS',decode='PIL_FULL_DECODE',native_pixels='PASS',cache='EXISTING_KODI_TEXTURE',android='ANDROID_NOT_TESTED'))
# Do not run an image server during the cold acceptance. Existing local cache
# must render while exact remote endpoints return failure.
Path('/root/tls79-off').write_text('synthetic image origin unavailable')
base79=json.loads(Path('/root/home75-base79.json').read_text());base79['cache79']=proof79
Path('/root/home75.json').write_text(json.dumps(base79,indent=2))
