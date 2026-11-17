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

home.setFocusId(2510);home.getControl(2510).selectItem(0)
row482=live_rows(portal)[0];sid482=str(row482['sid'])
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
  check(home.getProperty(prefix482+'ArtStatus')==code482,('STATUS482_NOT_BOUND',code482,home.getProperty(prefix482+'ArtStatus')))
  check(needle482.casefold() in home.getProperty(prefix482+'Description').casefold(),('STATUS482_NO_DESCRIPTION',code482))
  xbmc.sleep(200);picture482,_=capture('visible84-status482-'+code482.lower())
  status_cases482.append(dict(code=code482,screenshot=picture482.name,bank=bank482,description_binding=True))
finally:
 programme_requests68.request=request482
 epg_handoff63.remember(portal['id'],row482,original482,mappings482)
report['status482']=dict(status='PASS',mode='INJECTED_PRODUCER_STATE_NATIVE_HERO_PROJECTION',
    cases=status_cases482,settings_mutated=False,android='ANDROID_NOT_TESTED')
