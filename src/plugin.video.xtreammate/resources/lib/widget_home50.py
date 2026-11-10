"""Live-only native start-group source; saved URLs and media widgets unchanged."""
def rows(portal):
    from live_home62 import rows as read
    return read(portal)


def values(portal):
    from live_items62 import values as decorate
    import time
    started86=time.monotonic()
    selected,code=rows(portal)
    __import__('home_status86').note('GROUP_READ_MS',ms=int((time.monotonic()-started86)*1000),count=len(selected))
    return (__import__('live_rail86').values(portal,selected) if __import__('home_schedule75').applicable() else decorate(portal,selected)),code


def ordered(router,portal,items):
    # Legacy saved sources pin the configured start station once; Home50 keeps
    # its existing provider ordering. Neither source URL is rewritten.
    if router._params.get('home50')=='1':return items
    sid=str(portal.get('start_stream_id') or '')
    selected=[v for v in items if v['props'].get('XCMate.MediaId')==sid]
    return selected+[v for v in items if v['props'].get('XCMate.MediaId')!=sid] if selected else items

def render(router,portal):
    import xbmc,xbmcplugin
    from boot_diagnostics import finish_directory
    from widget_items45 import item
    from live_home62 import trace,CODES
    from widget_diagnostics47 import note
    note(portal['id'],'live','DIRECTORY','DIRECTORY_INVOKED')
    items,code=values(portal)
    items=ordered(router,portal,items)
    from widget_runtime79 import generation,directory
    tag79=generation(portal,'live',[dict(sid=v['props']['XCMate.MediaId']) for v in items],{v['props']['XCMate.MediaId']:v['art'] for v in items})
    for v79 in items:v79['props']['XCMate.Directory79']=tag79
    directory(portal,'live',items,tag79)
    xbmcplugin.setContent(router._handle,'videos')
    xbmcplugin.setPluginCategory(router._handle,'XCMate Live-TV · '+code)
    for value in items:xbmcplugin.addDirectoryItem(router._handle,value['url'],item(value),isFolder=False)
    try:xbmc.log('[XCMate][HOME50] source=LIVE_START_GROUP code='+(code if code in CODES else 'INTERNAL_ERROR')+' rows='+str(len(items)),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass
    stage='ITEMS_READY' if items else 'DIRECTORY_EMPTY'
    note(portal['id'],'live','ITEMS',stage,items=len(items));trace('DIRECTORY','READY' if items else code,len(items))
    finish_directory(router,succeeded=bool(items) or code in ('DISABLED','EMPTY_GROUP'),cacheToDisc=False)
