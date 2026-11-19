"""Single source-control surface; storage and private import reuse existing APIs."""
def onboarding(dialog):
 import xbmcaddon,xbmcgui
 from menu_icons45 import select
 from localization import tr
 from artwork_sources96 import token_valid
 if token_valid():return True
 choice=select(dialog,tr(39000),[tr(36661),tr(36621),tr(36012)],default='settings')
 if choice not in (0,1):return False
 import tmdb_token61 as tokens
 from tmdb_access61 import imported
 imported(7 if choice==0 else 0,dialog,xbmcaddon.Addon(),xbmcgui,tokens,activate_import=False)
 return token_valid()

def show():
 import xbmcgui
 from menu_icons45 import select
 from localization import tr
 from settings_guard96 import SettingsError
 from artwork_sources96 import status,choose,enroll_test_profile
 from settings_rebuild99_ui import LABEL as rebuild_label,confirm as confirm_rebuild
 dialog=xbmcgui.Dialog()
 while True:
  value=status();healthy=value['settings'] in ('READY','NOT_CREATED')
  def state(source):
   if not healthy:return tr(39004)
   if value.get(source):
    if source=='tmdb' and not value['token_valid']:return tr(39209)
    return tr(39002) if value.get('images_enabled') else tr(39210)
   return tr(39003)
  labels=['XMLTV: '+state('xmltv'),'TMDB: '+state('tmdb'),'TVMaze: '+state('tvmaze'),tr(39005),tr(39006),tr(39007),tr(39008),tr(39009),tr(39010),tr(39011),tr(39029),tr(rebuild_label),tr(36012)]
  action=select(dialog,tr(39000),labels,default='settings')
  if not isinstance(action,int) or not 0<=action<12:return
  try:
   if action==11:
    if confirm_rebuild():return
    continue
   if action==10:
    __import__('manual_image96').manage();continue
   if action in (0,1,2):
    source=('xmltv','tmdb','tvmaze')[action];on=not value.get(source,False)
    if on and source!='xmltv' and not dialog.yesno(tr(39000),tr(39012,source.upper()),defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):continue
    if on and source=='tmdb':
     if not onboarding(dialog):continue
     from tmdb_connection60 import launch
     if launch()!='TMDB_OK':continue
    choose(source,on);dialog.ok(tr(39000),tr(39013))
   elif action==3:
    text=tr(39014,value['settings'])+'\n'+'\n'.join(labels[:3])+'\n'+tr(39015,tr(39002 if value.get('token_valid') else 39003))
    if healthy and not value.get('images_enabled'):text+='\n'+tr(39016)
    dialog.ok(tr(39000),text)
   elif action==4:
    from programme_diagnostic74 import show as diagnostic
    diagnostic()
   elif action==5:
    if onboarding(dialog):
     from tmdb_connection60 import launch
     launch()
   elif action==6:
    from logo_editor96 import manage
    manage()
   elif action==7:
    from storage_artwork96 import manage
    manage()
   elif action==8:
    if dialog.yesno(tr(39000),tr(39017),defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):
     from settings_guard96 import repair
     repair();dialog.ok(tr(39000),tr(39018))
   elif action==9:
    if not dialog.yesno(tr(39000),tr(39019),defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):continue
    if not onboarding(dialog):continue
    from tmdb_connection60 import launch
    if launch()!='TMDB_OK':continue
    enroll_test_profile();dialog.ok(tr(39000),tr(39013))
  except (SettingsError,OSError,ValueError) as exc:
   from artwork_errors96 import message
   dialog.ok(tr(39000),message(getattr(exc,'code',str(exc))))
