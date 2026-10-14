"""Kodi plot and YouTube trailer metadata from provider-supplied title records.

Never guess an external trailer ID. Only known YouTube hostnames / IDs supplied
by the user's IPTV service are accepted. Additional metadata is loaded on
explicit Details selection, not on every list scroll.
"""
import re
from urllib.parse import urlparse, parse_qs, quote

_ID = re.compile(r'^[A-Za-z0-9_-]{11}$')


def provider_plot(item):
    if not isinstance(item, dict):
        return ''
    for source in (item, item.get('info'), item.get('movie_data')):
        if not isinstance(source, dict):
            continue
        for key in ('plot', 'description', 'overview', 'synopsis', 'storyline'):
            value = source.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ''


def trailer_id(item):
    if not isinstance(item, dict):
        return None
    for source in (item, item.get('info')):
        if not isinstance(source, dict):
            continue
        for key in ('youtube_trailer', 'trailer', 'trailer_url', 'youtube'):
            value = source.get(key)
            if not isinstance(value, str) or not value.strip():
                continue
            raw = value.strip()
            if _ID.fullmatch(raw):
                return raw
            try:
                url = urlparse(raw if '://' in raw else 'https://' + raw)
            except ValueError:
                continue
            host = (url.hostname or '').lower()
            video = ''
            if host in ('youtube.com', 'www.youtube.com', 'm.youtube.com', 'music.youtube.com'):
                video = (parse_qs(url.query).get('v') or [''])[0]
                if not video and url.path.startswith('/shorts/'):
                    video = url.path.split('/')[2]
                if not video and url.path.startswith('/embed/'):
                    video = url.path.split('/')[2]
            elif host in ('youtu.be', 'www.youtu.be'):
                video = url.path.strip('/').split('/')[0]
            if _ID.fullmatch(video):
                return video
    return None


def youtube_kodi_url(item):
    vid = trailer_id(item)
    return 'plugin://plugin.video.youtube/play/?video_id=' + quote(vid) if vid else ''


def enrich(item, details):
    combined = dict(item or {})
    if isinstance(details, dict):
        info = details.get('info') or details.get('movie_data') or details
        if isinstance(info, dict):
            combined.update({k:v for k,v in info.items() if v not in (None, '')})
    return combined
