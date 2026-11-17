"""Native existing Hero description binding for injected producer states.

The pipeline and healthy pixels are checked by the surrounding production
worker/TLS/texture tests. This part isolates status projection on a fresh,
synthetic RAM event. It never changes consent or a real user's settings.
"""
import copy
import epg_handoff63
import programme_requests68
from epg_sources import configuration
from status_fixture482 import build

row482=live_rows(portal)[0];sid482=str(row482['sid'])
def context482(event=None):
 active=home.getProperty('XCMate.Hero63.Active');prefix='XCMate.Hero63.'+active+'.'
 result=dict(window=xbmcgui.getCurrentWindowId(),dialog=xbmcgui.getCurrentWindowDialogId(),
     focus=home.getFocusId(),home50=xbmc.getInfoLabel('ListItem.Property(XCMate.Home50)')=='true',
     pid_match=xbmc.getInfoLabel('ListItem.Property(XCMate.PortalId)')==str(portal['id']),
     sid_match=xbmc.getInfoLabel('ListItem.Property(XCMate.MediaId)')==sid482,
     token_length=len(xbmc.getInfoLabel('ListItem.Property(XCMate.WidgetToken41)')),
     rail_visible=xbmc.getCondVisibility('Control.IsVisible(2510)'),
     sideblade=home.getProperty('ShowViewSubMenu')=='show',bank_status=home.getProperty(prefix+'ArtStatus'))
 if event:
  current=epg_handoff63.get(portal['id'],sid482)
  result['same_programme']=bool(current and current.get('programme_key47')==event.get('programme_key47'))
  result['producer_result']=programme_requests68.result(event).get('code')
 return result
# close() returns before Kodi's modal/focus restoration frame. Require real
# Home/ListItem receipts; never disable the production eligibility guards.
contexts482=[dict(phase='before_focus',**context482())];stable482=0
for attempt482 in range(100):
 if xbmcgui.getCurrentWindowId()==10000 and xbmcgui.getCurrentWindowDialogId() in (0,-1,9999):
  home.setFocusId(2510);home.getControl(2510).selectItem(0)
 xbmc.sleep(50);receipt482=context482()
 good482=receipt482['window']==10000 and receipt482['dialog'] in (0,-1,9999) and receipt482['focus']==2510 and receipt482['home50'] and receipt482['pid_match'] and receipt482['sid_match']
 stable482=stable482+1 if good482 else 0
 if stable482>=3:break
contexts482.append(dict(phase='focus_ready',**context482()))
Path('/root/status482-context.json').write_text(json.dumps(contexts482,indent=2))
check(stable482>=3,('STATUS482_NATIVE_FOCUS_NOT_READY',context482()))
original482=epg_handoff63.get(portal['id'],sid482)
check(original482 is not None,'STATUS482_NO_EXISTING_EPG')
info482=build(portal['id'],row482,time.time(),original482)
cid482=info482['canonical46']
mappings482=configuration(portal['id'])['mappings']
epg_handoff63.remember(portal['id'],row482,info482,mappings482)
published482=epg_handoff63.get(portal['id'],sid482,mappings=mappings482)
check(published482 and published482['now']=='Native status482','STATUS482_SNAPSHOT_NOT_PUBLISHED')
event482=dict(published482['events'][0],pid=str(portal['id']),sid=sid482,canonical=cid482,revision=published482['snapshot_revision'])
request482=programme_requests68.request
programme_requests68.request=lambda *a,**k:False
status_cases482=[]
try:
 for code482,needle482 in (('REQUESTED','angefordert'),('RUNNING','Bildsuche'),('SETTINGS_XML_INVALID','Bildeinstellungen'),('IMAGE_EPG_DISABLED','deaktiviert')):
  programme_requests68.status(event482,code482)
  for frame482 in range(80):
   hero_epg63._next=0;hero_epg63.poll();xbmc.sleep(50)
   bank482=home.getProperty('XCMate.Hero63.Active');prefix482='XCMate.Hero63.'+bank482+'.'
   if home.getProperty(prefix482+'ArtStatus')==code482:break
  if home.getProperty(prefix482+'ArtStatus')!=code482:
   contexts482.append(dict(phase='status_failure',expected=code482,**context482(event482)))
   Path('/root/status482-context.json').write_text(json.dumps(contexts482,indent=2))
   capture('visible84-status482-failed')
  check(home.getProperty(prefix482+'ArtStatus')==code482,('STATUS482_NOT_BOUND',code482,context482(event482)))
  check(needle482.casefold() in home.getProperty(prefix482+'Description').casefold(),('STATUS482_NO_DESCRIPTION',code482))
  xbmc.sleep(200);picture482,_=capture('visible84-status482-'+code482.lower())
  status_cases482.append(dict(code=code482,screenshot=picture482.name,bank=bank482,description_binding=True))
finally:
 programme_requests68.request=request482
 epg_handoff63.remember(portal['id'],row482,original482,mappings482)
report['status482']=dict(status='PASS',mode='INJECTED_PRODUCER_STATE_NATIVE_HERO_PROJECTION',
    cases=status_cases482,settings_mutated=False,android='ANDROID_NOT_TESTED')
