"""Reload only after safe native builder release; never bless file-only patches."""
import json,time
KEY='XCMate.Home78.Activation'
_next=0
def request(plan):
    import xbmcgui
    xbmcgui.Window(10000).setProperty(KEY,json.dumps(dict(plan=plan,phase='FILES_VERIFIED',at=time.monotonic(),reloads=0)))

def prepare():
    # Worker-only generated-cache/backup IO. GUI poll never scans files.
    import xbmc,xbmcgui,xbmcvfs,xbmcaddon
    window=xbmcgui.Window(10000);raw=window.getProperty(KEY)
    if not raw:return
    try:value=json.loads(raw)
    except (ValueError,TypeError):return
    if value.get('phase')!='FILES_VERIFIED' or value.get('consumer_prepared78'):return
    if window.getProperty('skinshortcuts-isrunning').lower()=='true' or xbmc.getCondVisibility('Player.HasMedia') or xbmc.getCondVisibility('Window.IsVisible(script-skinshortcuts.xml)'):return
    from widget_reload78 import repair
    repair(xbmcvfs.translatePath('special://profile/'),xbmcaddon.Addon('skin.titan.bingie.mod').getAddonInfo('path'))
    value['consumer_prepared78']=True;window.setProperty(KEY,json.dumps(value))
    from widget_hooks45 import prepare as hooks
    __import__('widget_hooks45')._next=0;hooks()

def poll():
    global _next
    import xbmc,xbmcgui
    now=time.monotonic()
    if now<_next:return
    _next=now+.5;window=xbmcgui.Window(10000);raw=window.getProperty(KEY)
    if not raw:return
    try:value=json.loads(raw)
    except (ValueError,TypeError):return
    if value.get('phase') in ('RUNTIME_READY','RELOAD_UNCONFIRMED'):return
    from widget_skin78 import runtime
    status=runtime()
    if status['code']=='RUNTIME_READY' and value.get('consumer_prepared78'):
        value['phase']='RUNTIME_READY';value['runtime']=status
        window.setProperty(KEY,json.dumps(value))
        from widget_manager50 import trace
        trace('SKIN_PATCH_VERIFIED');return
    if xbmc.getSkinDir()!='skin.titan.bingie.mod' or xbmcgui.getCurrentWindowId()!=10000:return
    if xbmcgui.getCurrentWindowDialogId() not in (0,-1,9999) or xbmc.getCondVisibility('Player.HasMedia') or xbmc.getCondVisibility('System.HasActiveModalDialog'):return
    if window.getProperty('skinshortcuts-isrunning').lower()=='true':return
    if not value.get('consumer_prepared78'):return
    if not value.get('reloads') and now-value.get('at',now)>=2:
        value.update(phase='RELOAD_POSTED',reloads=1,posted=now)
        window.setProperty(KEY,json.dumps(value));xbmc.executebuiltin('ReloadSkin()',wait=False)
    elif value.get('reloads') and now-value.get('posted',now)>15:
        value.update(phase='RELOAD_UNCONFIRMED',runtime=status);window.setProperty(KEY,json.dumps(value))
