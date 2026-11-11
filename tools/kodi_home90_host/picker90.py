"""Original BINGIE manager + original SkinShortcuts explorer, real IR actions.
No select/explorer/save replacement, no fake saved WidgetPaths. Disposable data.
"""
import ast,json,time,hashlib
from pathlib import Path
import xbmc,xbmcgui,xbmcaddon
home=xbmcgui.Window(10000);history=[]
xbmcaddon.Addon('script.skinshortcuts').setSetting('enable_logging','true')
for method90 in ('Addons.GetAddons','Addons.Getaddons'):
 response90=json.loads(xbmc.executeJSONRPC(json.dumps(dict(jsonrpc='2.0',id=90,method=method90,params=dict(content='video',properties=['name','path','thumbnail','enabled'])))))
 print('PICKER90_REGISTRY '+json.dumps(dict(method=method90,result=response90)),flush=True)
 Path('/root/picker90-registry.json').write_text(json.dumps(response90,indent=2))
def check(value,reason):
 if not value:raise RuntimeError(str(reason))
def until(predicate,reason,seconds=30):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  if predicate():return
  # Upstream's first-use shared-menu question: keep the fresh profile local.
  if reason=='PICKER90_MANAGER_NOT_VISIBLE' and xbmcgui.getCurrentWindowDialogId()==10100 and xbmc.getInfoLabel('System.CurrentControl')=='No':
   xbmc.executebuiltin('Action(Select)',wait=False)
  xbmc.sleep(100)
 raise RuntimeError((reason,xbmcgui.getCurrentWindowId(),xbmcgui.getCurrentWindowDialogId(),xbmc.getInfoLabel('System.CurrentControl')))
def action(value):xbmc.executebuiltin('Action('+value+')',wait=False);xbmc.sleep(250)
def entries():
 count=xbmc.getInfoLabel('Container(6).NumItems')
 return [xbmc.getInfoLabel('Container(6).ListItemAbsolute('+str(i)+').Label') for i in range(int(count or 0))]
def select(index):
 # Kodi excludes the '..' parent from CurrentItem numbering. Match the
 # actual highlighted label and send native Down/Select, never infer an index
 # from that counter or reconstruct another interpreter's Python-owned list.
 values=entries();target=values[index]
 for _ in range(len(values)+1):
  highlighted=xbmc.getInfoLabel('Container(6).ListItem.Label')
  if highlighted.strip('[]')==target.strip('[]'):break
  xbmc.executebuiltin('Action(Down)',wait=False);xbmc.sleep(100)
 else:raise RuntimeError(('PICKER90_NATIVE_FOCUS_NOT_FOUND',target,highlighted))
 print('PICKER90_NATIVE_SELECTED '+json.dumps(dict(index=index,label=highlighted,current=xbmc.getInfoLabel('Container(6).CurrentItem'))),flush=True)
 action('Select')
def manager():
 xbmc.executebuiltin('RunScript(script.skinshortcuts,type=manage&group=mainmenu)',wait=False)
 until(lambda:xbmc.getCondVisibility('Window.IsVisible(script-skinshortcuts.xml)') and int(xbmc.getInfoLabel('Container(211).NumItems') or 0)>0,'PICKER90_MANAGER_NOT_VISIBLE',60)
 dialog=xbmcgui.Window(xbmcgui.getCurrentWindowDialogId());dialog.setFocusId(211);dialog.getControl(211).selectItem(0);xbmc.sleep(200);return dialog
def choose(dialog,slot,kind=None,noportal=False):
 dialog.setFocusId(1312);action('Select');dialog.setFocusId(90011+slot*10);action('Select')
 seen=[]
 for step in range(16):
  until(lambda:bool(entries()) or xbmcgui.getCurrentWindowDialogId()==10103,'PICKER90_EMPTY_SELECT')
  if xbmcgui.getCurrentWindowDialogId()==10103:
   xbmc.executeJSONRPC(json.dumps(dict(jsonrpc='2.0',id=90,method='Input.SendText',params=dict(text='XCMate '+str(kind),done=True))));break
  values=entries();seen.append(values);history.append(dict(step=step,kind=kind,labels=values,window=xbmcgui.getCurrentWindowDialogId(),current=xbmc.getInfoLabel('Container(6).CurrentItem')));Path('/root/picker90-history.json').write_text(json.dumps(history,indent=2));print('PICKER90_NATIVE_LIST '+json.dumps(history[-1]),flush=True)
  if noportal and any('Portal' in v or 'einrichten' in v or 'setup' in v.casefold() for v in values):
   check(not any('pid=' in v for v in values),'PICKER90_FAKE_PORTAL');action('Back');return seen
  target=None
  if any('XCMate' in v for v in values):target=next(i for i,v in enumerate(values) if 'XCMate' in v)
  # Root source names are localized through XCMate's real English PO.
  words={'live':('live-tv','start group','startgruppe'),'vod':('movies','filme'),'series':('series','serien')}.get(kind,())
  if kind and any(any(w in v.casefold() for w in words) for v in values):target=next(i for i,v in enumerate(values) if any(w in v.casefold() for w in words))
  if target is None:
   for candidates in (('video add-ons','video addons','video-addons','video add-on'),('add-ons','addons','add-on'),('use as widget','als widget','hier verwenden')):
    options=[i for i,v in enumerate(values) if any(w in v.casefold() for w in candidates)]
    if options:target=options[0];break
  check(target is not None,('PICKER90_UNKNOWN_NATIVE_BRANCH',values));selected=values[target];select(target)
  if 'use as widget' in selected.casefold() or 'als widget' in selected.casefold():
   until(lambda:xbmcgui.getCurrentWindowDialogId()==10103 or xbmc.getCondVisibility('Window.IsActive(script-skinshortcuts.xml)'),'PICKER90_SELECT_DID_NOT_RETURN')
   if xbmcgui.getCurrentWindowDialogId()==10103:xbmc.executeJSONRPC(json.dumps(dict(jsonrpc='2.0',id=90,method='Input.SendText',params=dict(text='XCMate '+kind,done=True))))
   break
 else:raise RuntimeError('PICKER90_RECURSION_LIMIT')
 until(lambda:xbmc.getCondVisibility('Window.IsActive(script-skinshortcuts.xml)'),'PICKER90_MANAGER_NOT_RETURNED')
 return seen
def close(dialog):
 dialog.setFocusId(211)
 for _ in range(4):
  action('Back')
  if not xbmc.getCondVisibility('Window.IsVisible(script-skinshortcuts.xml)'):return
 raise RuntimeError('PICKER90_MANAGER_NOT_CLOSED')
folder=Path('/root/.kodi/userdata/addon_data/script.skinshortcuts');portal=Path('/root/.kodi/userdata/addon_data/plugin.video.xtreammate/portals.json')
check(not portal.exists(),'PICKER90_NOT_FRESH_PROFILE')
dialog=manager();choose(dialog,0,noportal=True);close(dialog)
# Explicit test-provider setup, not an installer or production data reset.
result=json.loads(xbmc.executeJSONRPC(json.dumps(dict(jsonrpc='2.0',id=90,method='Files.GetDirectory',params=dict(directory='plugin://plugin.video.xtreammate/?fixture59=seed',media='files')))))
check('error' not in result and portal.exists(),'PICKER90_FIXTURE_SETUP_FAILED')
dialog=manager()
for slot,kind in enumerate(('live','vod','series')):choose(dialog,slot,kind)
close(dialog)
properties=folder/'skin.titan.bingie.mod.properties';until(lambda:properties.exists(),'PICKER90_NO_SAVED_PROPERTIES')
rows=ast.literal_eval(properties.read_text(encoding='utf-8'));paths=[r[3] for r in rows if r[2].startswith('widgetPath')]
for expected in ('widget_live_start_group','widget_recent_vod','widget_recent_series'):check(any(expected in p and 'pid=fixture59' in p for p in paths),('PICKER90_PATH_NOT_SAVED',expected))
before=hashlib.sha256(properties.read_bytes()).hexdigest();dialog=manager();close(dialog);check(hashlib.sha256(properties.read_bytes()).hexdigest()==before,'PICKER90_REOPEN_REWROTE_PROPERTIES')
report=dict(status='PASS',original_skinshortcuts='2.1.0',fresh_noportal=True,saved_widget_paths=paths,original_dialog_branches=history,properties_sha256=before,android='ANDROID_NOT_TESTED')
Path('/root/picker90.json').write_text(json.dumps(report,indent=2));print('PICKER90_RESULT '+json.dumps(report),flush=True)
