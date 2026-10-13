"""NoodleMagazine website adapter. Uses public HTML, no authentication or bypass."""
import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Optional

ROOT = 'https://noodlemagazine.com'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
WATCH = re.compile(r'^https://(?:www\.|adult\.)?noodlemagazine\.com/watch/[-_0-9]+/?(?:\?.*)?$', re.I)


class SiteError(Exception):
    pass


def validated_url(url):
    url = urllib.parse.urljoin(ROOT + '/', html.unescape(url or ''))
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != 'https' or parsed.hostname not in {'noodlemagazine.com', 'www.noodlemagazine.com', 'adult.noodlemagazine.com'}:
        raise SiteError('Unzulässige Seitenadresse')
    return url


def watch_url(url):
    target = validated_url(url)
    if not WATCH.fullmatch(target):
        raise SiteError('Keine gültige Videoseite')
    return target


def source_url(path):
    resolved = urllib.parse.urljoin('https://adult.noodlemagazine.com/', html.unescape(path or ''))
    parts = urllib.parse.urlparse(resolved)
    if parts.scheme not in ('http', 'https') or not parts.hostname or parts.username or parts.password:
        raise SiteError('Ungültige Videoquelle')
    return resolved


def fetch_html(url, timeout=12):
    url = validated_url(url)
    request = urllib.request.Request(url, headers={
        'User-Agent': UA,
        'Referer': ROOT + '/',
        'Accept-Language': 'de-DE,de;q=0.8,en;q=0.6',
        'Accept': 'text/html,application/xhtml+xml',
    })
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if urllib.parse.urlparse(response.geturl()).hostname not in {'noodlemagazine.com', 'www.noodlemagazine.com', 'adult.noodlemagazine.com'}:
                raise SiteError('Unerwartete Weiterleitung')
            data = response.read(3_000_001)
            if len(data) > 3_000_000:
                raise SiteError('Webseite unerwartet groß')
            return data.decode('utf-8', errors='replace')
    except urllib.error.HTTPError as exc:
        raise SiteError('Website meldet HTTP {} (mögliche Zugriffsbeschränkung)'.format(exc.code)) from exc
    except urllib.error.URLError as exc:
        raise SiteError('Website nicht erreichbar: {}'.format(getattr(exc, 'reason', exc))) from exc


def strip_tags(fragment):
    fragment = re.sub(r'<[^>]*>', ' ', fragment or '')
    return ' '.join(html.unescape(fragment).split())


def duration_to_seconds(raw):
    nums = [int(x) for x in (raw or '').split(':') if x.isdigit()]
    if not nums or len(nums) > 3:
        return 0
    return sum(n * (60 ** i) for i, n in enumerate(reversed(nums)))


def _attr(tag, name):
    found = re.search(r'\b{}\s*=\s*(["\'])(.*?)\1'.format(re.escape(name)), tag, re.I | re.S)
    return html.unescape(found.group(2)) if found else ''


def _image(block):
    for tag in re.findall(r'<img\b[^>]*>', block, re.I | re.S):
        for field in ('data-src', 'data-original', 'src', 'data-lazy-src'):
            src = _attr(tag, field)
            if src and not src.startswith('data:'):
                src = urllib.parse.urljoin(ROOT + '/', src)
                if urllib.parse.urlparse(src).scheme == 'https':
                    return src
    # Occasionally thumbnail URL is in a CSS background image
    match = re.search(r'background-image\s*:\s*url\(["\']?(https://[^)"\']+)', block, re.I)
    return html.unescape(match.group(1)) if match else ''


def parse_listing(document):
    """Parse site video cards. Compatible with observed 'div.item' card markup."""
    cards = re.split(r'<div\s+class=["\']item["\'][^>]*>', document, flags=re.I)
    results, seen = [], set()
    for block in cards[1:]:
        link = re.search(r'<a\b[^>]*\bhref\s*=\s*(["\'])([^"\']*/watch/[-_0-9]+(?:\?[^"\']*)?)\1', block, re.I)
        if not link:
            continue
        try:
            url = watch_url(link.group(2))
        except SiteError:
            continue
        if url in seen:
            continue
        title_match = re.search(r'class\s*=\s*["\'][^"\']*\btitle\b[^"\']*["\'][^>]*>(.*?)<', block, re.I | re.S)
        title = strip_tags(title_match.group(1)) if title_match else ''
        if not title:
            title = strip_tags(_attr(link.group(0), 'title'))
        if not title or '${video.title}' in title:
            continue
        image = _image(block)
        duration_match = re.search(r'<(?:span|div)[^>]*class=["\'][^"\']*(?:duration|length|time)[^"\']*["\'][^>]*>\s*([\d:]+)', block, re.I)
        if not duration_match:
            duration_match = re.search(r'</svg>\s*([\d:]{4,})\s*<', block, re.I)
        duration = duration_to_seconds(duration_match.group(1)) if duration_match else 0
        q = re.search(r'class=["\']hd_mark["\'][^>]*>\s*([^<]+)', block, re.I)
        item = {'url': url, 'title': title, 'image': image, 'duration': duration,
                'quality': strip_tags(q.group(1)) if q else ''}
        results.append(item)
        seen.add(url)
    # Website's 'show more' button exposes the next server-side pagination index
    more_tag = re.search(r'<[^>]*\bclass\s*=\s*["\'][^"\']*\bmore\b[^"\']*["\'][^>]*>', document, re.I | re.S)
    match = re.search(r'\bdata-page\s*=\s*["\'](\d+)["\']', more_tag.group(0)) if more_tag else None
    return results, int(match.group(1)) if match else None


def meta_tag(doc, prop):
    for tag in re.findall(r'<meta\b[^>]+>', doc, re.I):
        if _attr(tag, 'property') == prop or _attr(tag, 'name') == prop:
            return _attr(tag, 'content')
    return ''


def parse_detail(doc):
    match = re.search(r'window\.playlist\s*=', doc, re.I)
    if not match:
        raise SiteError('Keine lesbare Video-Playlist auf der Seite')
    suffix = doc[match.end():].lstrip()
    try:
        playlist, _end = json.JSONDecoder().raw_decode(suffix)
    except ValueError as exc:
        raise SiteError('Video-Playlist ist kein lesbares JSON') from exc
    out = []
    for src in playlist.get('sources', []):
        if not isinstance(src, dict) or not src.get('file'):
            continue
        try:
            url = source_url(src['file'])
        except SiteError:
            continue
        kind = str(src.get('type') or '').lower()
        hls = kind in ('hls', 'application/x-mpegurl', 'application/vnd.apple.mpegurl') or '.m3u8' in url.lower()
        out.append({'url': url, 'label': str(src.get('label') or ''), 'hls': hls})
    if not out:
        raise SiteError('Keine abspielbare Quelle in der Playlist')
    out.sort(key=lambda s: (int(re.search(r'\d+', s['label']).group(0)) if re.search(r'\d+', s['label']) else 0, not s['hls']), reverse=True)
    return {'title': meta_tag(doc, 'og:title') or 'Video',
            'description': meta_tag(doc, 'og:description'),
            'image': meta_tag(doc, 'og:image') or (source_url(playlist['image']) if playlist.get('image') else ''),
            'sources': out}


def listing_path(section, query='', page=0, sort='0', hd='0', duration='any'):
    """Public listing URLs; all paths and filter options are whitelisted."""
    section = section if section in ('popular', 'recent', 'trending', 'now', 'hd', 'short', 'long', 'search') else 'popular'
    sort = sort if sort in ('0', '1', '2') else '0'
    hd = '1' if hd == '1' or section == 'hd' else '0'
    duration = duration if duration in ('any', 'short', 'long') else 'any'
    if section in ('short', 'long'):
        duration = section
    path = {'popular':'/home', 'recent':'/home', 'trending':'/popular/trending', 'now':'/now',
            'hd':'/home', 'short':'/home', 'long':'/home', 'search':'/video/' + urllib.parse.quote(query.strip())}[section]
    params = {'sort': sort, 'hd': hd, 'len': duration, 'p': max(0, int(page))}
    if section == 'recent':
        params['range'] = 'recent'
    return ROOT + path + '?' + urllib.parse.urlencode(params)
