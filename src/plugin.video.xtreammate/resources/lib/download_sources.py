"""Resolve a user's stored media identity afresh; never persist source URLs."""
from urllib.parse import urlsplit

EXTENSIONS=frozenset(('mp4','mkv','ts','avi','mov','webm','m4v'))


class DownloadFailure(ValueError):
    def __init__(self,code):self.code=code;super().__init__(code)


def record(portal,kind,sid,series_id=''):
    from library_index import Reader
    from xtream import XtreamClient
    reader=Reader(portal['id'])
    client=XtreamClient(portal['xc_host'],portal['xc_user'],portal['xc_pass']) if portal.get('type')=='xtream' else __import__('source_adapters').for_portal(portal)
    if kind=='episode':
        series=reader.get('series',series_id)
        if not series:raise DownloadFailure('SOURCE_UNAVAILABLE')
        from media_sequence import records
        data=client._get_json('get_series_info',extra={'series_id':series_id},cached_only=True) or {}
        item=next((e for e in records(data,portal['id'],series_id) if e['sid']==sid),None)
        if item:item=dict(item,series_title=series.get('name') or '',series_id=series_id)
    else:item=reader.get('series' if kind=='series_item' else 'vod',sid)
    if not item:raise DownloadFailure('SOURCE_UNAVAILABLE')
    if any(item.get(k) for k in ('drm','drm_info','license_key','license_url','licence_url','inputstream')):raise DownloadFailure('PROTECTED_SOURCE')
    return item,client


def describe(portal,kind,sid,series_id='',target=''):
    if kind not in ('vod','episode','series_item'):raise DownloadFailure('UNSUPPORTED_SOURCE')
    item,_=record(portal,kind,str(sid),str(series_id))
    from media_art import local_art
    poster=local_art(item)['poster']
    if '://' in poster:poster=''
    result=dict(pid=str(portal['id']),kind=kind,sid=str(sid),series_id=str(series_id),target=target,title=str(item.get('name') or 'XCMate'),poster=poster)
    for key in ('season','episode','series_title','year','duration'):result[key]=str(item.get(key) or '')
    return result


def resolve(media):
    from portals import get_active
    portal=next((p for p in get_active() if str(p['id'])==media['pid']),None)
    if not portal:raise DownloadFailure('SOURCE_UNAVAILABLE')
    item,client=record(portal,media['kind'],media['sid'],media.get('series_id',''))
    extension=str(item.get('container_extension') or 'mkv').lower()
    if extension not in EXTENSIONS:raise DownloadFailure('UNSUPPORTED_SOURCE')
    if portal.get('type')=='xtream':
        url=client.vod_stream_url(media['sid'],extension) if media['kind']=='vod' else client.series_episode_url(media['sid'],extension);headers={}
    elif media['kind']=='episode':url,headers=client.episode_uri(media['series_id'],media['sid'],media['season'])
    else:url,headers=client.play_uri('series' if media['kind']=='series_item' else 'vod',media['sid'])
    validate(url)
    return url,dict(headers or {})


def validate(url):
    if not isinstance(url,str) or len(url)>16384 or any(c in url for c in ('\r','\n','\0','|')):raise DownloadFailure('UNSUPPORTED_SOURCE')
    try:parts=urlsplit(url)
    except ValueError:raise DownloadFailure('UNSUPPORTED_SOURCE') from None
    if parts.scheme not in ('http','https') or not parts.hostname or parts.username or parts.password or parts.fragment:raise DownloadFailure('UNSUPPORTED_SOURCE')
    if parts.path.lower().endswith(('.m3u8','.m3u','.mpd')):raise DownloadFailure('UNSUPPORTED_SOURCE')
    return url


def container(data):
    if data.startswith(b'\x1aE\xdf\xa3'):return 'mkv'
    if len(data)>=12 and data[4:8] in (b'ftyp',b'moov',b'wide',b'free'):
        if any(tag in data for tag in (b'pssh',b'encv',b'enca')):raise DownloadFailure('PROTECTED_SOURCE')
        return 'mp4'
    if data.startswith(b'RIFF') and data[8:12]==b'AVI ':return 'avi'
    if len(data)>=564 and all(data[n]==0x47 for n in (0,188,376)):
        if any(data[n+3]&0xc0 for n in range(0,len(data)-187,188)):raise DownloadFailure('PROTECTED_SOURCE')
        return 'ts'
    raise DownloadFailure('INVALID_MEDIA')
