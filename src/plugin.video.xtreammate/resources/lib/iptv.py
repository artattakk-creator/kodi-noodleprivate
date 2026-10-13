import re
import gzip
import os
import time

import xbmcvfs

from utils import (
    http_get, cache_get, cache_set, cache_key,
    setting_bool, safe_int, safe_float,
    debug, error, info, warn
)

class Channel:
    __slots__ = (
        'name', 'url', 'logo', 'group', 'tvg_id', 'tvg_name',
        'tvg_shift', 'catchup', 'catchup_source', 'catchup_days',
        'radio', 'extra', 'playlist_idx'
    )

    def __init__(self, name='', url='', logo='', group='Uncategorised',
                 tvg_id='', tvg_name='', tvg_shift=0.0,
                 catchup='', catchup_source='', catchup_days=0,
                 radio=False, extra=None, playlist_idx=0):
        self.name           = name
        self.url            = url
        self.logo           = logo
        self.group          = group
        self.tvg_id         = tvg_id
        self.tvg_name       = tvg_name
        self.tvg_shift      = tvg_shift
        self.catchup        = catchup
        self.catchup_source = catchup_source
        self.catchup_days   = catchup_days
        self.radio          = radio
        self.extra          = extra or {}
        self.playlist_idx   = playlist_idx

    def to_dict(self):
        return {s: getattr(self, s) for s in self.__slots__}

    @classmethod
    def from_dict(cls, d):
        return cls(**{k: d.get(k, getattr(cls, '__init__').__defaults__[i])
                      for i, k in enumerate(cls.__slots__)
                      if k in d})


_ATTR_RE = re.compile(
    r'([\w\-]+)'            
    r'\s*=\s*'              
    r'(?:'
        r'"([^"]*)"'        
        r"|'([^']*)'"   
        r'|([^\s,]+)'       
    r')',
    re.IGNORECASE
)

def _parse_attrs(attr_str: str) -> dict:
    result = {}
    for m in _ATTR_RE.finditer(attr_str):
        key = m.group(1).lower()         
        val = m.group(2) if m.group(2) is not None else \
              m.group(3) if m.group(3) is not None else \
              (m.group(4) or '')
        result[key] = val
    return result


def _split_extinf(line: str):
    rest = re.sub(r'^#EXTINF\s*:\s*-?\d*\.?\d*\s*', '', line, flags=re.IGNORECASE).strip()
    if not rest:
        return {}, ''

    in_dq  = False   
    in_sq  = False   
    last_comma = -1

    for i, ch in enumerate(rest):
        if ch == '"' and not in_sq:
            in_dq = not in_dq
        elif ch == "'" and not in_dq:
            in_sq = not in_sq
        elif ch == ',' and not in_dq and not in_sq:
            last_comma = i

    if last_comma == -1:
        return {}, rest.strip()

    attr_str = rest[:last_comma]
    name     = rest[last_comma + 1:].strip()
    attrs    = _parse_attrs(attr_str)
    return attrs, name



def _is_stream_url(line: str) -> bool:
    if not line or line.startswith('#'):
        return False
    if re.match(r'^[a-zA-Z][a-zA-Z0-9+\-.]*://', line):
        return True
    if line.startswith('/') or line.startswith('.'):
        return True
    return False



def _get_group(attrs: dict) -> str:
    for key in ('group-title', 'group', 'tvg-group', 'category'):
        v = attrs.get(key, '').strip()
        if v:
            return v
    return 'Uncategorised'

def _get_logo(attrs: dict) -> str:
    for key in ('tvg-logo', 'logo', 'tvg-icon', 'channel-logo'):
        v = attrs.get(key, '').strip()
        if v:
            return v
    return ''



def parse_m3u(content: str, playlist_idx: int = 0) -> list:
    """
    Parse M3U text, return (channels, epg_url).
    Supports:
      - group-title="..." in EXTINF attributes
      - #EXTGRP:GroupName on a separate line
      - x-tvg-url / tvg-url in #EXTM3U header for auto EPG
    """
    channels      = []
    pending_name  = None
    pending_attrs = {}
    pending_group = None
    epg_url       = ''

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        upper = line.upper()

        if upper.startswith('#EXTM3U'):
            hdr_attrs = _parse_attrs(line[7:])
            epg_url = (hdr_attrs.get('x-tvg-url') or
                       hdr_attrs.get('tvg-url') or
                       hdr_attrs.get('url-tvg') or '')
            continue

        if upper.startswith('#EXTINF'):
            pending_attrs, pending_name = _split_extinf(line)
            continue

        if upper.startswith('#EXTGRP:'):
            pending_group = line[8:].strip()
            continue

        if line.startswith('#'):
            if pending_name is not None:
                kp = re.match(
                    r'#(?:KODIPROP|EXTVLCOPT)\s*:?\s*([\w\-]+)\s*=\s*(.*)',
                    line, re.IGNORECASE
                )
                if kp:
                    pending_attrs[kp.group(1).lower()] = kp.group(2).strip()
            continue

        if _is_stream_url(line):
            name  = (pending_name or '').strip()
            if not name:
                name = line.split('/')[-1].split('?')[0] or 'Channel'

            attrs = pending_attrs or {}

            group = _get_group(attrs)
            if group == 'Uncategorised' and pending_group:
                group = pending_group

            ch = Channel(
                name           = name,
                url            = line,
                logo           = _get_logo(attrs),
                group          = group,
                tvg_id         = attrs.get('tvg-id', ''),
                tvg_name       = attrs.get('tvg-name', name),
                tvg_shift      = safe_float(attrs.get('tvg-shift', 0)),
                catchup        = attrs.get('catchup', ''),
                catchup_source = attrs.get('catchup-source',
                                  attrs.get('catchup-template', '')),
                catchup_days   = safe_int(attrs.get('catchup-days',
                                  attrs.get('timeshift', 0))),
                radio          = str(attrs.get('radio', 'false')).lower() == 'true',
                extra          = attrs,
                playlist_idx   = playlist_idx,
            )
            channels.append(ch)
            pending_name  = None
            pending_attrs = {}
            pending_group = None

    return channels, epg_url


def _decode_bytes(raw: bytes) -> str:
    for enc in ('utf-8', 'utf-8-sig', 'latin-1', 'cp1252'):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode('utf-8', errors='replace')

def _decompress(raw: bytes, content_encoding: str = '') -> bytes:

    if 'gzip' in content_encoding:
        try:
            return gzip.decompress(raw)
        except Exception:
            pass

    if raw[:2] == b'\x1f\x8b':
        try:
            return gzip.decompress(raw)
        except Exception as e:
            warn(f'M3U gzip decompress failed: {e}')
    return raw



def load_m3u(url_or_path: str, portal_id: str = '',
             playlist_idx: int = 0,
             force_refresh: bool = False) -> list:

    if not url_or_path:
        error('load_m3u: empty URL/path')
        return []

    if portal_id and url_or_path.startswith('http'):
        try:
            from portals import detect_xtream, update as portal_update, get_by_id
            xc = detect_xtream(url_or_path)
            if xc:
                p = get_by_id(portal_id)
                if p and p.get('type') == 'm3u':
                    info(f'load_m3u: Xtream detected for portal {portal_id}, auto-upgrading')
                    portal_update(portal_id, {
                        'type'    : 'xtream',
                        'xc_host' : xc['xc_host'],
                        'xc_user' : xc['xc_user'],
                        'xc_pass' : xc['xc_pass'],
                        'm3u_url' : '',
                    })
                    from xtream import XtreamClient
                    xc_client = XtreamClient(xc['xc_host'], xc['xc_user'], xc['xc_pass'])
                    return xc_client.get_live_streams()
        except Exception as _e:
            error(f'load_m3u xtream auto-upgrade failed: {_e}')

    use_cache   = setting_bool('cache_playlists', True)
    cache_hours = 24
    ck = cache_key((portal_id or '') + url_or_path)

    if use_cache and not force_refresh:
        cached = cache_get(ck, max_age=cache_hours * 3600)
        if cached:
            debug(f'M3U cache hit: {len(cached)} channels')
            return [Channel.from_dict(d) for d in cached]

    info('Fetching M3U (URL redacted)')
    raw = b''
    ce  = ''

    try:
        if url_or_path.startswith(('http://', 'https://')):
            raw, resp_headers = http_get(url_or_path)
            ce = (resp_headers.get('content-encoding') or
                  resp_headers.get('Content-Encoding') or '')
        elif url_or_path.startswith('special://') or xbmcvfs.exists(url_or_path):
            with xbmcvfs.File(url_or_path) as f:
                data = f.read()
            raw = data if isinstance(data, bytes) else data.encode('utf-8')
        else:
            error('M3U source not found')
            return []
    except Exception as e:
        error(f'M3U fetch error: {e}')
        return []

    raw              = _decompress(raw, ce)
    content          = _decode_bytes(raw)
    channels, epg_url = parse_m3u(content, playlist_idx)

    channels = auto_group_channels(channels)

    if epg_url and portal_id:
        try:
            import portals as _p
            portal = _p.get_by_id(portal_id)
            if portal and not portal.get('epg_url', '').strip():
                _p.update(portal_id, {'epg_url': epg_url})
                info('M3U: auto-saved EPG URL')
        except Exception as e:
            warn(f'M3U: could not auto-save EPG URL: {e}')

    if channels:
        groups = {c.group for c in channels}
        info(f'M3U: {len(channels)} channels, {len(groups)} groups '
             f'(EPG: {epg_url[:40] if epg_url else "none"})')
        sample = list(groups)[:5]
        debug(f'M3U sample groups: {sample}')
    else:
        warn('M3U: 0 channels from configured source')
        debug(f'M3U content preview: {content[:500]}')

    if use_cache and channels:
        cache_set(ck, [c.to_dict() for c in channels])

    return channels


def _from_dict(cls, d):
    defaults = {
        'name': '', 'url': '', 'logo': '', 'group': 'Uncategorised',
        'tvg_id': '', 'tvg_name': '', 'tvg_shift': 0.0,
        'catchup': '', 'catchup_source': '', 'catchup_days': 0,
        'radio': False, 'extra': {}, 'playlist_idx': 0,
    }
    defaults.update({k: v for k, v in d.items() if k in defaults})
    return cls(**defaults)

Channel.from_dict = classmethod(_from_dict)



def auto_group_channels(channels: list, min_per_group: int = 5) -> list:

    if not channels:
        return channels
    uncat = sum(1 for c in channels if c.group == 'Uncategorised')
    if uncat / len(channels) < 0.95:
        return channels  
    raw_groups: dict = {}
    assigned = []
    for ch in channels:
        name  = ch.name
        group = 'Uncategorised'
        if '|' in name:
            parts = name.split('|', 1)
            g = parts[0].strip()
            n = parts[1].strip()
            if g and 1 <= len(g) <= 25 and n:
                group = g
                name  = n
        raw_groups.setdefault(group, 0)
        raw_groups[group] += 1
        assigned.append((ch, name, group))

    result = []
    for ch, name, group in assigned:
        if group != 'Uncategorised' and raw_groups[group] < min_per_group:
            group = 'Uncategorised'
            name  = ch.name   
        result.append(Channel(
            name=name, url=ch.url, logo=ch.logo, group=group,
            tvg_id=ch.tvg_id, tvg_name=ch.tvg_name, tvg_shift=ch.tvg_shift,
            catchup=ch.catchup, catchup_source=ch.catchup_source,
            catchup_days=ch.catchup_days, radio=ch.radio,
            extra=ch.extra, playlist_idx=ch.playlist_idx,
        ))

    groups = {c.group for c in result}
    info(f'auto_group: {len(groups)} groups (min {min_per_group}/group) '
         f'from {len(result)} channels')
    return result

def group_channels(channels: list) -> dict:
    groups = {}
    for ch in channels:
        groups.setdefault(ch.group, []).append(ch)
    return groups


_MOVIE_KW = re.compile(
    r'\b(vod|movie|film|cinema|кино|pelicul|cine)\b'
    r'|(\|\s*movies?)$',
    re.IGNORECASE
)

_SERIES_KW = re.compile(
    r'\b(series|serie[s]?|show[s]?|episode[s]?|season[s]?|сериал|novela|dorama)\b'
    r'|(\|\s*series?)$',
    re.IGNORECASE
)

_LIVE_KW = re.compile(
    r'\b(live|news|sport[s]?|channel[s]?|tv|radio|adult)\b',
    re.IGNORECASE
)


def classify_group(group_name: str) -> str:
    g = group_name or ''
    if _SERIES_KW.search(g):
        return 'series'
    if _MOVIE_KW.search(g):
        return 'movies'
    return 'live'


def split_m3u_sections(channels: list) -> dict:
    section_map = {} 
    result = {'live': [], 'movies': [], 'series': []}

    for ch in channels:
        g = ch.group
        if g not in section_map:
            section_map[g] = classify_group(g)
        result[section_map[g]].append(ch)

    total = len(channels)
    vod   = len(result['movies']) + len(result['series'])
    if total > 0 and vod / total < 0.05:
        result['live'] = channels
        result['movies'] = []
        result['series'] = []
        debug('split_m3u_sections: VOD ratio <5%, treating as live-only')
    else:
        debug(f'split_m3u_sections: live={len(result["live"])} '
              f'movies={len(result["movies"])} series={len(result["series"])}')

    return result

def search_channels(channels: list, query: str) -> list:
    q = query.lower()
    return [c for c in channels
            if q in c.name.lower() or q in c.group.lower()]
