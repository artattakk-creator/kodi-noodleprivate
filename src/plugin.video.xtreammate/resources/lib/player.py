import re
import urllib.parse

import xbmc
import xbmcgui
import xbmcplugin

from utils import setting, setting_bool, setting_int, info, debug, warn, error

def detect_stream_type(url: str) -> str:
    u = url.lower().split('?')[0].split('|')[0]
    if u.endswith('.m3u8')             : return 'hls'
    if u.endswith('.mpd')              : return 'dash'
    if u.startswith('rtmp')            : return 'rtmp'
    if u.startswith('rtsp')            : return 'rtsp'
    if u.endswith(('.ts', '.mp4', '.mkv', '.avi', '.flv', '.wmv')): return 'direct'
    if '/m3u8' in u or 'playlist.m3u' in u: return 'hls'
    if '/timeshift/' in u or '/live/' in u : return 'hls'
    return 'http'

def _isa_available() -> bool:
    try:
        import xbmcaddon
        xbmcaddon.Addon('inputstream.adaptive')
        return True
    except RuntimeError:
        return False

def _build_header_string(url: str, extra_headers: dict = None) -> str:

    base_url  = url
    existing  = {}

    if '|' in url:
        base_url, hdr_part = url.split('|', 1)
        for pair in hdr_part.split('&'):
            if '=' in pair:
                k, v = pair.split('=', 1)
                existing[k.strip()] = urllib.parse.unquote(v.strip())

    ua = setting('user_agent',
                 'Mozilla/5.0 (Linux; Android 11; TV) '
                 'AppleWebKit/537.36 (KHTML, like Gecko) '
                 'Chrome/112.0.0.0 Mobile Safari/537.36')

    merged = {'User-Agent': ua}
    merged.update(existing)
    if extra_headers:
        merged.update(extra_headers)

    hdr_str = '&'.join(
        f'{k}={urllib.parse.quote(str(v), safe="")}' for k, v in merged.items()
    )
    return base_url, hdr_str


def build_playable_item(url: str,
                        title: str = '',
                        logo:  str = '',
                        headers: dict = None,
                        drm_info: dict = None) -> xbmcgui.ListItem:
    """
    Return a fully configured ListItem ready for setResolvedUrl.
    Automatically picks InputStream Adaptive for HLS/DASH when available.
    """
    if not url:
        error('build_playable_item: empty URL')
        return xbmcgui.ListItem(title)

    stype      = detect_stream_type(url)
    is_hls     = (stype == 'hls')
    is_dash    = (stype == 'dash')
    is_rtmp    = (stype == 'rtmp')
    use_isa    = False
    player_pref= setting_int('player_default', 0)

    debug('play: type={}'.format(stype))

    base_url, hdr_str = _build_header_string(url, headers)

    li = xbmcgui.ListItem(title)
    li.setArt({'icon': logo, 'thumb': logo})
    li.setInfo('video', {'title': title, 'mediatype': 'video'})
    li.setProperty('IsPlayable', 'true')

    if (is_hls or is_dash) and player_pref in (0, 1) and _isa_available():
        use_isa = True

    if use_isa:
        debug('ISA playback: URL redacted')
        li.setProperty('inputstream', 'inputstream.adaptive')
        manifest = 'hls' if is_hls else 'mpd'
        li.setProperty('inputstream.adaptive.manifest_type', manifest)
        li.setProperty('inputstream.adaptive.stream_headers', hdr_str)
        li.setProperty('inputstream.adaptive.manifest_headers', hdr_str)
        if drm_info:
            _apply_drm(li, drm_info, hdr_str)
        li.setPath(base_url)
        return li

    if is_rtmp:
        li.setPath(url)
        return li

    final = f'{base_url}|{hdr_str}' if hdr_str else base_url
    debug('direct playback: stream URL redacted')
    li.setPath(final)
    return li

def _apply_drm(li, drm_info: dict, hdr_str: str = ''):
    drm_type  = drm_info.get('type', 'com.widevine.alpha')
    lic_url   = drm_info.get('licence_url', '')
    challenge = drm_info.get('challenge', 'R{SSM}')
    response  = drm_info.get('response', '')
    li.setProperty('inputstream.adaptive.license_type', drm_type)
    li.setProperty('inputstream.adaptive.license_key',
                   f'{lic_url}|{hdr_str}|{challenge}|{response}')


def play_stream(handle: int, url: str,
                title: str = '', logo: str = '',
                headers: dict = None, drm_info: dict = None):

    if not url:
        error('play_stream: no URL provided')
        xbmcplugin.setResolvedUrl(handle, False, xbmcgui.ListItem())
        return
    info('play_stream: URL redacted')
    li = build_playable_item(url, title=title, logo=logo,
                             headers=headers, drm_info=drm_info)
    xbmcplugin.setResolvedUrl(handle, True, li)

def play_catchup(handle: int, url: str,
                 start_ts: int = 0, stop_ts: int = 0,
                 title: str = '', logo: str = '',
                 headers: dict = None):

    if not url:
        error('play_catchup: no URL provided')
        xbmcplugin.setResolvedUrl(handle, False, xbmcgui.ListItem())
        return
    info('play_catchup: URL redacted')
    li = build_playable_item(url, title=title, logo=logo, headers=headers)
    xbmcplugin.setResolvedUrl(handle, True, li)

def channel_list_item(channel, current_prog=None, progress: float = 0.0):
    title = channel.name
    if current_prog:
        title = f'{channel.name}  [{current_prog.title}]'
    li = xbmcgui.ListItem(title)
    li.setArt({'icon': channel.logo, 'thumb': channel.logo})
    info_d = {'title': channel.name, 'mediatype': 'video'}
    if current_prog:
        info_d.update({
            'plot'    : current_prog.desc or current_prog.title,
            'genre'   : current_prog.category,
            'duration': max(0, current_prog.stop - current_prog.start),
        })
    li.setInfo('video', info_d)
    li.setProperty('IsPlayable', 'true')
    if progress > 0:
        li.setProperty('ProgressPercentage', str(int(progress * 100)))
    return li

def vod_list_item(vod: dict):
    from utils import safe_int, safe_float, safe_year
    from metadata_views import provider_plot, youtube_kodi_url
    title = vod.get('name', '')
    year  = safe_year(vod.get('year'))
    li    = xbmcgui.ListItem(f'{title} ({year})' if year else title)
    li.setArt({
        'icon'  : vod.get('stream_icon', ''),
        'thumb' : vod.get('stream_icon', ''),
        'poster': vod.get('stream_icon', ''),
    })
    cast = vod.get('cast', '')
    li.setInfo('video', {
        'title'    : title,
        'plot'     : provider_plot(vod),
        'trailer'  : youtube_kodi_url(vod),
        'year'     : year,
        'rating'   : safe_float(vod.get('rating')),
        'genre'    : vod.get('genre', ''),
        'director' : vod.get('director', ''),
        'cast'     : cast.split(',') if isinstance(cast, str) and cast else [],
        'duration' : safe_int(vod.get('duration_secs')),
        'mediatype': 'movie',
    })
    li.setProperty('IsPlayable', 'true')
    return li

def series_list_item(series: dict):
    from metadata_views import provider_plot, youtube_kodi_url
    from utils import safe_float
    title = series.get('name', '')
    li    = xbmcgui.ListItem(title)
    cover = series.get('cover', '')
    fan   = (series.get('backdrop_path', ['']) or [''])[0] \
            if isinstance(series.get('backdrop_path'), list) \
            else series.get('backdrop_path', '')
    li.setArt({'icon': cover, 'thumb': cover, 'poster': cover, 'fanart': fan})
    li.setInfo('video', {
        'title'    : title,
        'plot'     : provider_plot(series),
        'trailer'  : youtube_kodi_url(series),
        'rating'   : safe_float(series.get('rating')),
        'genre'    : series.get('genre', ''),
        'mediatype': 'tvshow',
    })
    li.setProperty('IsPlayable', 'false')
    return li

def episode_list_item(ep: dict, show_name: str = ''):
    from utils import safe_int
    ep_num = ep.get('episode_num', '')
    title  = ep.get('title', f'Episode {ep_num}')
    full   = f'{show_name} - {title}' if show_name else title
    li     = xbmcgui.ListItem(full)
    img    = (ep.get('info') or {}).get('movie_image', '')
    li.setArt({'icon': img, 'thumb': img})
    li.setInfo('video', {
        'title'    : title,
        'season'   : safe_int(ep.get('season')),
        'episode'  : safe_int(ep.get('episode_num')),
        'plot'     : (ep.get('info') or {}).get('plot', ''),
        'duration' : safe_int((ep.get('info') or {}).get('duration_secs')),
        'mediatype': 'episode',
    })
    li.setProperty('IsPlayable', 'true')
    return li
