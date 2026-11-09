"""Every .80 native case plus both rails visible and the compact .81 layout."""
from pathlib import Path
source81=Path('/base_gui80.py').read_text()
for old,new in (("'((270,0),1620,480)'","'((270,0),1620,620)'"),('getpixel((330,525))','getpixel((330,665))'),('getpixel((350,800))','getpixel((350,770))'),('range(480,1040)','range(640,1040)')):
 source81=source81.replace(old,new)
# The first-frame test must see the series row before any Down/focus too.
needle81="check(max(abs(a-b) for a,b in zip(initial80_rgb.getpixel((300,150)),(20,80,130)))<=8,'HERO80_NOT_FULL_BLEED')"
assert needle81 in source81
source81=source81.replace(needle81,needle81+"\\ncheck(max(abs(a-b) for a,b in zip(initial80_rgb.getpixel((350,1020)),(100,50,20)))<=8,'SERIES81_NOT_VISIBLE_BEFORE_FOCUS')")
# Same exact HTTPS/pixel/cache acceptance, now including the explicit .81
# durable-cache producer rather than requiring a remote-only intermediate URI.
def cache_contract81(text):
 prefix="""import download_redirect as redirects81
original_addresses81=redirects81.addresses
def isolated_addresses81(url,*args,**kwargs):
 from urllib.parse import urlsplit
 parsed81=urlsplit(url)
 if parsed81.hostname=='image.tmdb.org' and parsed81.path in ('/t/p/w500/url69-5.jpg','/t/p/w500/url69-6.jpg'):return ['127.0.0.1']
 return original_addresses81(url,*args,**kwargs)
redirects81.addresses=isolated_addresses81
"""
 text=prefix+text
 needle=" __import__('widget_fast69')._next=0;"
 prewarm=""" from render_cache81 import prepare as persist81,references as refs81
 rows81,_=snapshot(portal79,kind79,background=True)
 errors81=[]
 def producer81():
  try:
   __import__('render_cache81')._due.clear();persist81(portal79,kind79,rows81[:1])
  except Exception as exc:errors81.append(type(exc).__name__)
 thread81=threading.Thread(target=producer81);thread81.start()
 for _ in range(150):
  if not thread81.is_alive():break
  xbmc.sleep(100)
 check(not thread81.is_alive() and not errors81,'DURABLE81_WORKER_FAILED')
 check(refs81(portal79,kind79,rows81[:1]).get('0',{}).get('poster','').startswith('/'),'DURABLE81_NOT_PERSISTED')
"""
 assert needle in text;text=text.replace(needle,prewarm+needle)
 text=text.replace("expected79=cache79.read(portal79,kind79,snapshot(portal79,kind79)[0]).get('0',{}).get('poster')","expected79=(cache79.read(portal79,kind79,snapshot(portal79,kind79)[0]).get('0',{}).get('poster') or refs81(portal79,kind79,snapshot(portal79,kind79)[0]).get('0',{}).get('poster'))")
 text=text.replace("retained79=cache79.read(portal79,kind79,rows79).get('0',{}).get('poster')","retained79=(cache79.read(portal79,kind79,rows79).get('0',{}).get('poster') or refs81(portal79,kind79,rows79).get('0',{}).get('poster'))")
 text=text.replace('worker79.join(2)','worker79.join(15)')
 return text.replace("cache='EXISTING_KODI_TEXTURE'","cache='EXISTING_KODI_TEXTURE' if 'Thumbnails' in retained79 else 'DURABLE_RENDER81'")
source81=source81.replace("exec(compile(cache80,'native-home80-cache','exec'),globals())","exec(compile(cache_contract81(cache80),'native-home81-cache','exec'),globals())")
exec(compile(source81,'native-home81','exec'),globals())
