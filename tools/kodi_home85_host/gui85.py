"""Current .85 native picture regression plus manual candidate IR dialog.
Linux synthetic proof; never Android acceptance or a physical ENOSPC claim.
"""
from pathlib import Path
base=Path('/base_gui84.py').read_text()
base=base.replace('Synthetic Linux Kodi .84','Synthetic Linux Kodi .85')
# .85 prepares the visible twelve covers first, not an invisible 24-file archive.
base=base.replace('len(read(portal,kind,rows))==24','len(read(portal,kind,rows))>=12')
base=base.replace('refs=24','refs=len(read(portal,kind,rows))')
base=base.replace("Path('/root/'+('post75.json' if cold else 'visible84.json')).write_text(json.dumps(report,indent=2))",'')
exec(compile(base,'/base_gui84.py','exec'),globals())
# Then scroll to the second viewport: all 24 titles remain in the native row,
# only the newly visible sources are admitted, and the selected tile stays put.
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
 check(home.getControl(control85).getSelectedPosition()==23,('VIEWPORT85_FOCUS_RESET',kind85))
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
# Real data-binding visibility of the unconfirmed proposal label.
home.setFocusId(2510);home.getControl(2510).selectItem(0)
item85=home.getControl(2510).getListItem(0);item85.setProperty('XCMate.Provisional85','true')
xbmc.sleep(700)
check(xbmc.getCondVisibility('Control.IsVisible(296885)'),'SERIES85_PROPOSAL_LABEL_HIDDEN')
proposal85,_=capture('visible84-series85-proposal');item85.setProperty('XCMate.Provisional85','')
report['version']='0.1.29.85';report['scroll85']=scroll85;report['series85']=dict(candidate_poster_pixels=poster85,confirm_native='PASS',back_native='PASS',no_implicit_mapping_write='PASS',proposal_visible='PASS',candidate_screenshot=shot85.name,proposal_screenshot=proposal85.name,android='ANDROID_NOT_TESTED')
Path('/root/'+('post75.json' if cold else 'visible84.json')).write_text(json.dumps(report,indent=2))
