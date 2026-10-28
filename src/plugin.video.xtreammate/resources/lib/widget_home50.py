"""Opt-in Live Home source: explicit start group only, no group/menu fallback."""
from widget_items45 import item


def rows(portal):
    from widget_data41 import WidgetReader
    from widget_group46 import pages
    from library_index import IndexReadError
    if not portal.get('include_live',True):return [],'DISABLED'
    cid=str(portal.get('start_group_id') or '')
    if not cid:return [],'START_GROUP_MISSING'
    reader=WidgetReader(portal['id']);groups=reader.groups('live')
    if cid not in {str(g.get('cid',g.get('category_id',''))) for g in groups}:return [],'START_GROUP_UNAVAILABLE'
    start=reader.get('live',str(portal.get('start_stream_id') or ''))
    scoped=dict(portal,start_stream_id=str(start['sid']) if start and str(start.get('category_id'))==cid else '')
    values=[r for batch in pages(scoped) for r in batch]
    if any(str(r.get('category_id',''))!=cid for r in values):raise IndexReadError('FOREIGN_GROUP')
    return values,'READY'


def values(portal):
    from widget_render47 import values as render
    from widget_art44 import read
    selected,code=rows(portal);approved=read(portal['id']);result=[]
    for offset in range(0,len(selected),16):
        for value in render(portal,'live',selected[offset:offset+16],approved):
            value.pop('_programme46',None);value['props']['XCMate.Home50']='true'
            value['label']=value['props'].get('XCMate.ProgrammeChannel46') or value['label']
            result.append(value)
    return result,code


def render(router,portal):
    import xbmc,xbmcplugin
    from boot_diagnostics import finish_directory
    from library_index import IndexReadError
    try:items,code=values(portal)
    except (OSError,ValueError,IndexReadError):items,code=[],'LOCAL_UNAVAILABLE'
    xbmcplugin.setContent(router._handle,'videos')
    xbmcplugin.setPluginCategory(router._handle,'XCMate Live-TV · '+code)
    for value in items:xbmcplugin.addDirectoryItem(router._handle,value['url'],item(value),isFolder=False)
    try:xbmc.log('[XCMate][HOME50] source=LIVE_START_GROUP code='+code+' rows='+str(len(items)),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass
    finish_directory(router,succeeded=True,cacheToDisc=False)
