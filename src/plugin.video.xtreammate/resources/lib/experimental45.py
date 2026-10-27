"""Per-invocation UX PIN; no persisted unlock, settings write, URL token or log."""
from contextvars import ContextVar
from localization import tr
_active=ContextVar('xcmate_experimental45',default=False)
ACTIONS=frozenset(('widget_adapter45','record_now','recordings_manage','recording_folder','recording_capabilities','guide_timers','download_folder','download_capabilities','download_target_test','downloads_manage45','experimental_options45','stability_test','popup_probe','remote_diagnostics','service_recover','clear_cache','art_retry','art_db_health','autoplay_diagnostic_mode','remote_learn'))

def protected(params):
 return params.get('action') in ACTIONS or params.get('action')=='settings_section' and params.get('section') in ('experimental','downloads','recordings','diagnostics') or params.get('action')=='native_options45' and params.get('group')=='experimental'

def active():return _active.get()

def run(callback):
 if active():return callback()
 import xbmcgui
 value=xbmcgui.Dialog().input(tr(36010),type=getattr(xbmcgui,'INPUT_ALPHANUM',0),option=getattr(xbmcgui,'ALPHANUM_HIDE_INPUT',1))
 if value!='6666':
  if value:xbmcgui.Dialog().notification('XCMate',tr(36011))
  return None
 token=_active.set(True)
 try:return callback()
 finally:_active.reset(token)

def confirm():
 import xbmcgui
 from menu_icons45 import select
 return select(xbmcgui.Dialog(),'XCMate',[tr(36012),tr(36013)],actions=['back','trash'],preselect=0)==1

def route(router,callback):
 # Release a bookmarked directory request before the modal PIN, as for EPG UI.
 from boot_diagnostics import finish_directory
 handle=router._handle
 if handle>=0:finish_directory(router,succeeded=False,cacheToDisc=False)
 try:
  router._handle=-1
  return run(callback)
 finally:router._handle=handle


def open_menu(router,portal,section='experimental'):
 from settings_sections45 import EXPERIMENTAL
 from menu_icons45 import select
 import xbmcgui
 rows=EXPERIMENTAL.get(section,EXPERIMENTAL['experimental']);dialog=xbmcgui.Dialog()
 while True:
  choice=select(dialog,tr(36006)+' · '+tr(36014),[tr(label) for label,_,_ in rows],actions=[action if action!='settings_section' else 'experimental_options45' for _,action,_ in rows])
  if not isinstance(choice,int) or not 0<=choice<len(rows):return
  _,action,params=rows[choice]
  if action=='settings_section':open_menu(router,portal,params['section']);continue
  old=router._params;handle=router._handle
  try:
   router._handle=-1
   router._params=dict(old,action=action,**params)
   router.dispatch()
  finally:router._params=old;router._handle=handle
