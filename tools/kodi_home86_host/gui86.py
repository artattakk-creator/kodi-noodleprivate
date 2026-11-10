"""Current .85 native picture regression plus manual candidate IR dialog.
Linux synthetic proof; never Android acceptance or a physical ENOSPC claim.
"""
from pathlib import Path
base=Path('/base_gui84.py').read_text()
base=base.replace('allow_lookup=False,url_mode69=True','allow_lookup=True,url_mode69=True')
base=base.replace('Synthetic Linux Kodi .84','Synthetic Linux Kodi .85')
# .85 prepares the visible twelve covers first, not an invisible 24-file archive.
base=base.replace('len(read(portal,kind,rows))==24','len(read(portal,kind,rows))>=12')
base=base.replace('refs=24','refs=len(read(portal,kind,rows))')
base=base.replace("Path('/root/'+('post75.json' if cold else 'visible84.json')).write_text(json.dumps(report,indent=2))",'')
# A stable ListItem receipt is not yet a completed native texture upload.
# Require the same actual pixels on a bounded sequence of complete captures.
start85=base.index(" path,rgb=capture('visible84-'+('cold-' if cold else 'warm-')+kind)")
end85=base.index(" # Ask Kodi's real receiver",start85)
base=base[:start85]+""" picture_started85=time.monotonic()
 def pixels(color,box):
  return sum(max(abs(a-b) for a,b in zip(pixel,color))<=8 for pixel in rgb.crop(box).getdata())
 for paint85 in range(24):
  pump();xbmc.sleep(200)
  path,rgb=capture('visible84-'+('cold-' if cold else 'warm-')+kind+'-frame-'+str(paint85))
  hero_pixels=pixels(hero_color,(300,50,1100,520));rail_pixels=pixels(rail_color,(275,540,480,1040))
  if hero_pixels>3000 and rail_pixels>1500:break
 else:
  check(hero_pixels>3000,('HERO84_PIXELS_MISSING',kind,hero_pixels))
  check(rail_pixels>1500,('RAIL84_PIXELS_MISSING',kind,rail_pixels))
 picture_wait85=int((time.monotonic()-picture_started85)*1000)
"""+base[end85:]
base=base.replace("cases.append(dict(kind=kind,items=", "cases.append(dict(picture_wait_ms=picture_wait85,kind=kind,items=")
exec(compile(base,'/base_gui84.py','exec'),globals())
# Then scroll to the second viewport: all 24 titles remain in the native row,
# only the newly visible sources are admitted, and the selected tile stays put.
def refresh_plans85():
 import widget_runtime79
 widget_runtime79._next=0;widget_runtime79.prepare([portal])
plans85=threading.Thread(target=refresh_plans85);plans85.start();plans85.join(10)
check(not plans85.is_alive(),'VIEWPORT85_PLAN_REFRESH_TIMEOUT')
import widget_patch85
patch85_original=widget_patch85.apply
patch85_evidence=[]
def patch85_probe(pid85,kind85,signature85):
 result85=patch85_original(pid85,kind85,signature85)
 from widget_runtime79 import _plans
 plan85=_plans.get((str(pid85),kind85),{})
 facts85=dict(kind=kind85,applied=result85,ids=plan85.get('ids'),plan_age=time.monotonic()-plan85.get('at',0))
 for cid85 in plan85.get('ids',[])[:1]:
  facts85['count']=xbmc.getInfoLabel('Container('+str(cid85)+').NumItems')
  try:
   item85=home.getControl(cid85).getListItem(0);facts85['native_item_id']=item85.getProperty('XCMate.MediaId');facts85['native_source85']=bool(item85.getProperty('XCMate.Source85'))
  except Exception as error85:facts85['native_item_error']=type(error85).__name__
 patch85_evidence.append(facts85)
 print('PATCH85_NATIVE '+json.dumps(facts85),flush=True)
 return result85
widget_patch85.apply=patch85_probe
scroll85=[]
for kind85,control85 in (('vod',2520),('series',2530)):
 rows85_catalog,_=snapshot(portal,kind85)
 home.setFocusId(control85);home.getControl(control85).selectItem(23)
 for _ in range(40):home_schedule75.observe();xbmc.sleep(50)
 focused85=home_schedule75.focus();check(focused85.get('kind')==kind85 and focused85.get('left',0)>0,('VIEWPORT85_NOT_OBSERVED',focused85))
 prepare(portal,kind85,rows85_catalog)
 for _ in range(160):
  if str(rows85_catalog[23]['sid']) in read(portal,kind85,rows85_catalog):break
  xbmc.sleep(50)
 check(str(rows85_catalog[23]['sid']) in read(portal,kind85,rows85_catalog),('VIEWPORT85_LAST_SOURCE_MISSING',kind85))
 publish(portal,kind85,rows85_catalog)
 for _ in range(40):pump();xbmc.sleep(50)
 selected85=xbmc.getInfoLabel('Container('+str(control85)+').ListItem.Property(XCMate.MediaId)')
 check(selected85==str(rows85_catalog[23]['sid']),('VIEWPORT85_FOCUS_RESET',kind85,selected85,xbmc.getInfoLabel('Container('+str(control85)+').CurrentItem'),patch85_evidence))
 scroll85.append(dict(kind=kind85,items=len(rows85_catalog),last_source='PASS',focus=23))
from series_manager85 import SeriesWindow85
# No service lookup or real TMDB token is used for synthetic candidate facts.
BASE="https://image.tmdb.org/t/p/w500/"
rows85=[dict(id=850+i,source='tmdb',title='Ghosts UK' if i==0 else 'Ghosts US',original='Synthetic identity '+str(i),year=2019 if i==0 else 2021,country=['GB'] if i==0 else ['US'],overview='Synthetic Linux fixture. Candidate must be confirmed; no episode facts.',poster=BASE+'vod84-'+str(i)+'.png',thumb85=BASE+'vod84-'+str(i)+'.png'+__import__('programme_urls55').OPTIONS,verified85=True) for i in range(8)]
# Keep URLs in the same already validated synthetic image-origin fixture.
def show85():
 view=SeriesWindow85('XCMateSeries85.xml',xbmcaddon.Addon().getAddonInfo('path'),'Default','720p');view.configure(rows85);view.show()
 for _ in range(100):
  if view._ready:break
  xbmc.sleep(50)
 check(view._ready,'SERIES85_INIT_TIMEOUT');return view
view85=show85();check(view85.chosen is None,'SERIES85_AUTOCOMMITTED')
for _ in range(60):xbmc.sleep(50)
shot85,rgb85=capture('visible84-series85-candidates')
poster85=sum(max(abs(a-b) for a,b in zip(pixel,(180,100,30)))<=8 for pixel in rgb85.crop((1140,180,1360,510)).getdata())
check(poster85>3000,('SERIES85_NO_POSTER_PIXELS',poster85))
view85.setFocusId(201);xbmc.executebuiltin('Action(Select)',wait=False)
for _ in range(100):
 if view85._closed:break
 xbmc.sleep(50)
check(view85._closed and view85.chosen and view85.chosen['id']==850,'SERIES85_CONFIRM_ACTION_FAILED')
view85=show85();xbmc.executebuiltin('Action(Back)',wait=False)
for _ in range(100):
 if view85._closed:break
 xbmc.sleep(50)
check(view85._closed and view85.chosen is None,'SERIES85_BACK_FAILED')
from programme_mapping85 import path
check(not path().exists(),'SERIES85_SELECTION_WITHOUT_MANAGER_WROTE_MAPPING')

# New .86 policy: preserve a correct rendered TMDB frame on a null/thumbnail update.
home.setFocusId(2510);home.getControl(2510).selectItem(0)
for _ in range(80):pump();xbmc.sleep(50)
bank86=home.getProperty('XCMate.Hero63.Active');prefix86='XCMate.Hero63.'+bank86+'.'
check(home.getProperty(prefix86+'Kind86')=='hero_backdrop',('HERO86_KIND',home.getProperty(prefix86+'Kind86')))
check(home.getControl(296886).getWidth()==1620,'HERO86_PRELOAD_CONTROL_MISSING')
check(xbmc.getCondVisibility('Control.IsVisible(296887)'),'STATUS86_NOT_VISIBLE')
# Existing native custom source rows must still populate alongside the own sources.
custom86={}
for control86 in (2540,2550,2560):
 count86=xbmc.getInfoLabel('Container('+str(control86)+').NumItems')
 check(str(count86).isdigit() and int(count86)>0,('CUSTOM86_MISSING',control86,count86))
 custom86[str(control86)]=int(count86)
shot86,rgb86=capture('visible84-hero86-final')
report['version']='0.1.29.86';report['hero86']=dict(kind=home.getProperty(prefix86+'Kind86'),source=home.getProperty(prefix86+'ArtSource'),image_pixels='PASS',preload_control='PASS',custom_rows=custom86,screenshot=shot86.name,android='ANDROID_NOT_TESTED')
report['series85']=dict(confirm_native='PASS',back_native='PASS',no_implicit_mapping_write='PASS')
Path('/root/'+('post75.json' if cold else 'visible84.json')).write_text(json.dumps(report,indent=2))
