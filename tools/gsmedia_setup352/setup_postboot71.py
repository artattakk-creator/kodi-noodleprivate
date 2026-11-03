"""Read-only bounded GUI readiness. Never select/change the user's skin."""
import json
import time


def wait_active(xbmc, monitor, seconds=45):
    deadline=time.monotonic()+seconds
    stable=0
    while time.monotonic()<deadline:
        if monitor.abortRequested():return False
        try:
            request=dict(jsonrpc='2.0',id=71,method='GUI.GetProperties',params=dict(properties=['skin']))
            gui=json.loads(xbmc.executeJSONRPC(json.dumps(request))).get('result',{})
            actual=gui.get('skin',{}).get('id')
            configured=json.loads(xbmc.executeJSONRPC(json.dumps(dict(jsonrpc='2.0',id=72,
                method='Settings.GetSettingValue',params=dict(setting='lookandfeel.skin'))))).get('result',{}).get('value')
            ready=xbmc.getCondVisibility('Window.IsActive(home)') and not xbmc.getCondVisibility('System.Startup')
            stable=stable+1 if ready and actual=='skin.titan.bingie.mod' and configured==actual else 0
            if stable>=2:return True
        except (ValueError,TypeError,AttributeError,RuntimeError):stable=0
        if monitor.waitForAbort(.25):return False
    return False
