"""Worker-only verification of a published page; no download or GUI claim."""
import os

def proof(portal,kind,rows):
    if kind not in ('vod','series') or not isinstance(rows,list):return None
    from widget_refresh45 import read
    from widget_data41 import policy
    from home_publication74 import source_refs,signature
    from programme_assets47 import local_uri
    from widget_assets69 import read as references
    import xbmcaddon
    frame=read(portal['id'],kind)
    if not frame or frame.get('policy')!=policy(portal,kind):return None
    selected=rows[:24];items=frame['items']
    if frame.get('source_refs74')!=source_refs(selected):return None
    if [v['props'].get('XCMate.MediaId') for v in items]!=[str(r['sid']) for r in selected]:return None
    if not items and not frame.get('empty_authoritative74'):return None
    if frame.get('signature')!=signature(items,kind):return None
    approved=references(portal,kind,selected)
    root=xbmcaddon.Addon().getAddonInfo('path')
    placeholders={os.path.join(root,'resources','media',name+'.png') for name in ('vod','series')}
    images=0
    for item in items:
        sid=item['props']['XCMate.MediaId'];known=set(approved.get(sid,{}).values());has_image=False
        if any(not isinstance(uri,str) for uri in item['art'].values()):return None
        for uri in set(item['art'].values()):
            if not uri or uri in placeholders:continue
            if not isinstance(uri,str) or not (uri in known or local_uri(uri)):return None
            has_image=True
        images+=int(has_image)
    return dict(signature=frame['signature'],count=len(items),images=images,fallbacks=len(items)-images)
