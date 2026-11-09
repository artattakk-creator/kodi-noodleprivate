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
# Real data-binding visibility of the unconfirmed proposal label.
home.setFocusId(2510);home.getControl(2510).selectItem(0)
Path('/root/proposal85-on').touch()
from fixture66 import install as install_proposal85
install_proposal85()
# The earlier picture leases are deliberately short-lived. Refresh this exact
# synthetic event on the worker before testing a new proposal publication;
# an expired remote reference must not be labelled as a visible proposal.
proposal_errors85=[]
def prepare_proposal85():
 try:
  row85=live_rows(portal)[0];event85=load(portal,row85)
  from programme_urls55 import resolve
  value85=resolve(event85,allow_lookup=False,url_mode69=True)
  check(value85 and value85.get('code')=='READY',('SERIES85_PROPOSAL_IMAGE_NOT_READY',value85.get('code') if value85 else None))
  completed(event85,dict(value85,provisional85=True,match='PROVISIONAL_TV85'))
  from live_items62 import values
  dto85=values(portal,[row85])[0]
  print('PROPOSAL85_SOURCE '+json.dumps({k:dto85['props'].get(k) for k in ('XCMate.MediaId','XCMate.Provisional85','XCMate.ProgrammeDisplay47','XCMate.HeroArtSource63','XCMate.ProgrammeArtCode46')}),flush=True)
  check(dto85['props'].get('XCMate.Provisional85')=='true','SERIES85_PROPOSAL_DTO_MISSING')
  publish(portal,'live',live_rows(portal))
 except Exception:
  import traceback;proposal_errors85.append(traceback.format_exc())
proposal_worker85=threading.Thread(target=prepare_proposal85);proposal_worker85.start()
for _ in range(400):
 pump();xbmc.sleep(50)
 if not proposal_worker85.is_alive():break
check(not proposal_worker85.is_alive(),'SERIES85_PROPOSAL_PREPARE_TIMEOUT')
check(not proposal_errors85,proposal_errors85)
from widget_runtime79 import _plans
hooks85=_plans.get((str(portal['id']),'live'),{}).get('hooks',[])
check(hooks85,'SERIES85_NO_NATIVE_LIVE_HOOK')
for hook85 in hooks85:
 if hook85.startswith('XCMate.Widget45.Reload.') or hook85 in ('widgetreload','widgetreload2','widgetreloadmovies','widgetreloadtvshows'):home.setProperty(hook85,'synthetic85-proposal-source')
# The existing production reload throttle is 60 s; do not bypass it.
for _ in range(1600):
 pump()
 if xbmc.getInfoLabel('Container(2510).ListItem.Property(XCMate.Provisional85)')=='true':break
 xbmc.sleep(50)
check(xbmc.getInfoLabel('Container(2510).ListItem.Property(XCMate.Provisional85)')=='true','SERIES85_PROPOSAL_SOURCE_MISSING')
# The directory update and Hero bank commit are separate native frames.
for _ in range(100):
 pump();xbmc.sleep(50)
 if xbmc.getCondVisibility('Control.IsVisible(296885)'):break
else:
 bank85=home.getProperty('XCMate.Hero63.Active')
 evidence85=dict(bank=bank85,bank_flag=home.getProperty('XCMate.Hero63.'+bank85+'.Provisional85'),variable=xbmc.getInfoLabel('$VAR[XCMate85.Provisional]'),row=xbmc.getInfoLabel('Container(2510).ListItem.Property(XCMate.Provisional85)'),focus=home.getFocusId(),dialog=xbmcgui.getCurrentWindowDialogId())
 print('PROPOSAL85_HIDDEN '+json.dumps(evidence85),flush=True)
 raise RuntimeError(('SERIES85_PROPOSAL_LABEL_HIDDEN',evidence85))
proposal85,_=capture('visible84-series85-proposal');Path('/root/proposal85-on').unlink(missing_ok=True)
home.getControl(2510).selectItem(1)
for _ in range(30):pump();xbmc.sleep(50)
check(not xbmc.getCondVisibility('Control.IsVisible(296885)'),'SERIES85_PROPOSAL_LEAKED_TO_OTHER_STATION')
report['version']='0.1.29.85';report['patch85']=patch85_evidence;report['scroll85']=scroll85;report['series85']=dict(candidate_poster_pixels=poster85,confirm_native='PASS',back_native='PASS',no_implicit_mapping_write='PASS',proposal_visible='PASS',candidate_screenshot=shot85.name,proposal_screenshot=proposal85.name,android='ANDROID_NOT_TESTED')
Path('/root/'+('post75.json' if cold else 'visible84.json')).write_text(json.dumps(report,indent=2))
