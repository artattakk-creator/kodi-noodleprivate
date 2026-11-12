"""Disposable native six-row renderer sources; never real TMDB/audio services.

Deterministic plugin directories, local posters and WAV validate Kodi targets.
This is explicitly not a remote-source or physical Android acceptance test.
"""
from pathlib import Path
import json,time,hashlib,io,sys

def install():
 import wave,math,struct
 from PIL import Image
 root=Path('/root/.kodi/addons')
 for addon,media in (('plugin.video.themoviedb.helper','video'),('plugin.audio.m3sr2019','audio')):
  target=root/addon;target.mkdir(exist_ok=True)
  (target/'addon.xml').write_text('<addon id="'+addon+'" name="Synthetic six-row source ONLY" version="99.0.0" provider-name="Native test"><requires><import addon="xbmc.python" version="3.0.1"/></requires><extension point="xbmc.python.pluginsource" library="default.py"><provides>'+media+'</provides></extension></addon>')
  (target/'default.py').write_text('''import sys,os\nfrom urllib.parse import parse_qs\nimport xbmc,xbmcgui,xbmcplugin\nh=int(sys.argv[1]);q=parse_qs(sys.argv[2][1:]);audio='audio' in sys.argv[0]\nif q.get('play'):\n item=xbmcgui.ListItem(path=os.path.join(os.path.dirname(__file__),'tone.wav'));item.setMimeType('audio/wav');xbmcplugin.setResolvedUrl(h,True,item)\nelse:\n xbmc.sleep(600)\n xbmcplugin.setContent(h,'songs' if audio else 'tvshows' if q.get('tmdb_type')==['tv'] else 'movies')\n for i in range(6):\n  label=('Audio test ' if audio else q.get('info',['List'])[0]+' ')+str(i+1)\n  item=xbmcgui.ListItem(label=label);art=os.path.join(os.path.dirname(__file__),'poster.png');item.setArt(dict(poster=art,thumb=art,icon=art))\n  if audio:\n   item.setProperty('IsPlayable','true');item.getMusicInfoTag().setTitle(label)\n  else:item.getVideoInfoTag().setTitle(label)\n  xbmcplugin.addDirectoryItem(h,sys.argv[0]+'?play=1' if audio else sys.argv[0]+'?info=details&item='+str(i),item,not audio)\n xbmcplugin.endOfDirectory(h,True,False,False)\n''')
  Image.new('RGB',(120,180),(30,170,100) if media=='audio' else (180,70,120)).save(target/'poster.png')
  if media=='audio':
   with wave.open(str(target/'tone.wav'),'wb') as w:
    w.setparams((1,2,8000,0,'NONE','not compressed'));w.writeframes(b''.join(struct.pack('<h',int(4000*math.sin(2*math.pi*440*i/8000))) for i in range(8000*6)))

def run(home,bindings,spinner_observer,service_poll):
 import xbmc,xbmcgui
 import widget_six_runtime as runtime
 from widget_six_sources import EXTRAS
 from widget_six_consumer import runtime_binding
 from epg_handoff63 import profile_scope
 target=Path('/root/.kodi/addons/skin.titan.bingie.mod/xml/script-skinshortcuts-includes.xml')
 binding=runtime_binding(target.read_bytes())
 if binding is None:raise RuntimeError('SIX438_NATIVE_CALLS_MISSING')
 originals={key:home.getProperty(key) for key in ('XCMate.Home75.Schedule',)}
 # Isolated RAM source plan only: keep the original saved SkinShortcuts exact.
 sources={}
 for kind,title,cid,widget_target in EXTRAS:
  uri='plugin://plugin.audio.m3sr2019/' if kind=='mp3' else 'plugin://plugin.video.themoviedb.helper/?info='+{'cinema':'now_playing','disney':'discover','trend':'trending_week'}[kind]+'&tmdb_type='+('tv' if kind=='trend' else 'movie')+('&with_watch_providers=337&watch_region=DE&with_id=True' if kind=='disney' else '')
  sources[kind]=dict(kind=kind,title=title,cid=cid,target=widget_target,code='WAITING',uri=uri,source_hash=hashlib.sha256(uri.encode()).hexdigest())
 runtime._plan=dict(binding=binding,sources=sources,scope=('SYNTHETIC_RENDER_ONLY','fixture59'),profile_scope=profile_scope())
 runtime._rows={};runtime._scope=None
 # Previous native Live/Film/Series receipts have already observed all items.
 schedule=json.loads(home.getProperty('XCMate.Home75.Schedule') or '{}');schedule['phase']=3;home.setProperty('XCMate.Home75.Schedule',json.dumps(schedule))
 start=time.monotonic();states=[]
 try:
  for _ in range(600):
   runtime.poll()
   states.append({kind:row['state'] for kind,row in runtime._rows.items()})
   if len(runtime._rows)==4 and all(row['state']=='READY' for row in runtime._rows.values()):break
   xbmc.sleep(100)
  else:raise RuntimeError(('SIX438_NATIVE_SOURCE_NOT_READY',runtime._rows))
  if not all(any(s.get(kind)=='LOADING' for s in states) for kind,_,_,_ in EXTRAS):raise RuntimeError('SIX438_LOADING_NOT_OBSERVED')
  if any(sum(s.get(k)=='LOADING' for k in sources)>1 for s in states):raise RuntimeError('SIX438_CONCURRENT_PROVIDERS')
  rows=[]
  for kind,title,cid,widget_target in EXTRAS:
   xbmc.executebuiltin('Action(Down)',wait=False)
   deadline=time.monotonic()+5
   while home.getFocusId()!=cid and time.monotonic()<deadline:runtime.poll();xbmc.sleep(50)
   if home.getFocusId()!=cid:raise RuntimeError(('SIX438_FOCUS_MISSING',kind,home.getFocusId()))
   count=xbmc.getInfoLabel('Container('+str(cid)+').NumItems')
   if count!='6':raise RuntimeError(('SIX438_ITEMS_MISSING',kind,count))
   heading=xbmc.getCondVisibility('Control.IsVisible(84'+str(cid)+')')
   if not heading:raise RuntimeError(('SIX438_HEADER_HIDDEN',kind))
   path=Path('/root/picker90-six438-'+kind+'.png');xbmc.executebuiltin('TakeScreenshot('+str(path)+')',wait=False);xbmc.sleep(400)
   from PIL import Image
   with Image.open(io.BytesIO(path.read_bytes())) as image:
    rgb=image.convert('RGB').resize((1920,1080));color=(30,170,100) if kind=='mp3' else (180,70,120)
    pixels=sum(max(abs(a-b) for a,b in zip(p,color))<10 for p in rgb.crop((260,640,1890,1040)).getdata())
   if pixels<1500:raise RuntimeError(('SIX438_COVER_PIXELS_MISSING',kind,pixels))
   rows.append(dict(kind=kind,title=title,control=cid,target=widget_target,items=6,heading_visible=True,pixels=pixels,screenshot=path.name))
  # Real native audio resolve/click, using only a local synthetic six-second WAV.
  xbmc.executebuiltin('Action(Select)',wait=False);deadline=time.monotonic()+5
  while not xbmc.Player().isPlayingAudio() and time.monotonic()<deadline:xbmc.sleep(50)
  audio=xbmc.Player().isPlayingAudio()
  if not audio:raise RuntimeError('SIX438_AUDIO_CLICK_DID_NOT_PLAY')
  xbmc.Player().stop();xbmc.sleep(500)
  # Return through native IR focus, then verify each actual original spinner.
  home.setFocusId(bindings['series'])
  extra_bindings={kind:cid for kind,_,cid,_ in EXTRAS}
  spinner_receipts=spinner_observer(home,extra_bindings,kinds=[r[0] for r in EXTRAS])
  report=dict(status='PASS',rows=rows,spinner=spinner_receipts,audio_played=True,elapsed_ms=int((time.monotonic()-start)*1000),source='SYNTHETIC_NATIVE_DIRECTORIES_NOT_REMOTE_SERVICES',android='ANDROID_NOT_TESTED')
  Path('/root/picker90-six438.json').write_text(json.dumps(report,indent=2));return report
 finally:
  for key,value in originals.items():home.setProperty(key,value)
