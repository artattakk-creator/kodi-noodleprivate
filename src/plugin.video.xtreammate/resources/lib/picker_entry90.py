"""Native SkinShortcuts directory browsing is passive, never app autoplay.

The upstream explorer issues Files.GetDirectory with its own progress dialog
active. Ordinary Videos entry and saved widget leaf routes remain unchanged.
No skin writes, fake portal, selection save or installer dependency.
"""
def note(code):
 if code not in ('PICKER_ENTRY_READY','PICKER_ENTRY_MISSING','PICKER_PORTAL_REQUIRED','PICKER_SOURCE_LIST_EMPTY','PICKER_ROUTE_INVALID','WIDGET_DIRECTORY_EMPTY','WIDGET_BINDING_UNEXPOSED'):return
 try:
  import xbmc
  xbmc.log('[XCMate][PICKER90] code='+code,xbmc.LOGINFO)
 except (AttributeError,RuntimeError):pass

def dispatch(router):
 if router._handle<0 or router._params.get('action','root') not in ('root','xcmate_home','portal_home','app_open'):return False
 import xbmc,xbmcgui
 dialog_id=getattr(xbmcgui,'getCurrentWindowDialogId',None)
 visible=getattr(xbmc,'getCondVisibility',None)
 if not callable(dialog_id) or not callable(visible):return False
 try:
  dialog=dialog_id()
  if dialog in (0,-1,9999) or visible('Window.IsActive(Videos)'):return False
  if not visible('Window.IsVisible(script-skinshortcuts.xml)'):return False
 except RuntimeError:return False
 # No general modal-window handoff: just answer this valid directory request.
 from app_routes import portal_for
 from widget_sources49 import show
 from boot_diagnostics import finish_directory
 portal=portal_for(router)
 if router._params.get('pid') and portal is None:
  note('PICKER_ROUTE_INVALID');finish_directory(router,False,cacheToDisc=False);return True
 note('PICKER_ENTRY_READY');show(router,portal);return True
