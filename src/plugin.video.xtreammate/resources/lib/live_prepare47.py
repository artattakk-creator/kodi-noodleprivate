"""Build immutable channel/index models in the existing catalog worker."""
import time


def trace(portal,code,rows=0):
    if code not in ('LOCAL_READ_BEGIN','START_GROUP_MODEL_READY','FULL_MODEL_READY'):
        return
    from flow46 import read
    value=read()
    if not value or value.get('kind')!='live' or value.get('pid')!=str(portal['id']):
        return
    import xbmc
    try:
        xbmc.log('[XCMate][PREPARE47] id='+value['id']+' code='+code+' rows='+str(rows)+
                 ' ms='+str(max(0,(time.monotonic_ns()-value['start'])//1000000)),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):
        pass


def model(portal,client,categories,streams):
    from iptv import Channel
    from tv_data import CatalogIndex
    from group_selection import enabled_ids
    groups=[g for g in categories if isinstance(g,dict)]
    names={str(g.get('category_id')):g.get('category_name','') for g in groups}
    channels=[]
    rows96=[dict(v,sid=str(v.get('stream_id',''))) for v in streams if isinstance(v,dict)]
    overrides96=__import__('logo_overrides96')
    scope96=overrides96.scope(portal);persistent96=__import__('artwork_config').persistent()
    base96=__import__('logo_manifest86').read(portal,rows96,with_overrides=False,with_agent=False)
    logos96=dict(base96,**overrides96.read(portal,rows96))
    for stream in streams:
        if not isinstance(stream,dict) or not stream.get('stream_id'):
            continue
        cid=str(stream.get('category_id',''))
        channels.append(Channel(name=stream.get('name',''),
            url=client.live_stream_url(stream['stream_id'],__import__('live_format67').extension()),logo=logos96.get(str(stream['stream_id']),stream.get('stream_icon','')),
            group=str(names.get(cid,cid)),tvg_id=str(stream.get('epg_channel_id') or ''),
            extra={'category_id':cid,'stream_id':str(stream['stream_id']),
                   **overrides96.binding(portal,dict(stream,sid=str(stream['stream_id'])),base96.get(str(stream['stream_id']),''),scope96=scope96,persistent96=persistent96),
                   **({'logo_local96':True} if logos96.get(str(stream['stream_id'])) else {})}))
    enabled=enabled_ids(portal['id'],'live',groups)
    index=CatalogIndex(channels)
    index.selection('*',enabled)
    return dict(groups=groups,channels=channels,enabled=enabled,index=index)
