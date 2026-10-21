import re
import time
import json
import threading
import datetime
from concurrent.futures import ThreadPoolExecutor
from xml.etree import ElementTree as ET
from urllib.parse import unquote_plus
from epg_io import XMLTVReader, MAX_XML_BYTES, MAX_PROGRAMMES, MAX_CHANNELS, XMLTVLimitError
from network_io import ResponseLimitError

import xbmcvfs

from utils import (
    http_get, cache_get, cache_set, cache_key,
    setting_bool, setting_int, setting, debug, info, error, warn
)


_DT_RE = re.compile(r'(\d{14})\s*([+-]\d{4})?')


class Programme:
    __slots__ = ('channel', 'start', 'stop', 'title', 'desc',
                 'category', 'episode', 'icon', 'rating')

    def __init__(self, channel='', start=0, stop=0, title='', desc='',
                 category='', episode='', icon='', rating=''):
        self.channel  = channel
        self.start    = int(start  or 0)
        self.stop     = int(stop   or 0)
        self.title    = title
        self.desc     = desc
        self.category = category
        self.episode  = episode
        self.icon     = icon
        self.rating   = rating

    def progress(self):
        dur = self.stop - self.start
        if dur <= 0:
            return 0.0
        return max(0.0, min(1.0, (time.time() - self.start) / dur))

def _parse_xmltv_ts(s):
    from xmltv_stream import timestamp
    return timestamp(s)


def parse_xmltv(content: bytes):
    """Parse XMLTV incrementally instead of building a full XML document tree.

    Each finished <channel>/<programme> node is released during parsing.
    This significantly reduces peak memory on Android when using several
    large external German, Austrian or Swiss programme guides.
    """
    stream = XMLTVReader(content, max_bytes=MAX_XML_BYTES)
    channels = {}
    programmes = {}
    root_element = None
    count = skipped = 0
    try:
        for event, element in ET.iterparse(stream,
                                          events=('start', 'end')):
            if root_element is None:
                root_element = element
            if event != 'end' or element.tag not in ('channel', 'programme'):
                continue
            if element.tag == 'channel':
                cid = element.get('id', '')
                channels[cid] = element.findtext('display-name') or cid
            else:
                cid = element.get('channel', '')
                try:
                    start = _parse_xmltv_ts(element.get('start', ''))
                    stop = _parse_xmltv_ts(element.get('stop', ''))
                    if not cid or stop <= start:
                        raise ValueError('Invalid XMLTV programme interval')
                except (ValueError, OverflowError):
                    skipped += 1
                    root_element.clear()
                    continue
                count += 1
                if count > MAX_PROGRAMMES:
                    raise XMLTVLimitError('XMLTV programme limit exceeded','programmes')
                title = (element.findtext('title') or '')[:512]
                desc = (element.findtext('desc') or '')[:4096]
                cat = element.findtext('category') or ''
                icon_el = element.find('icon')
                icon = icon_el.get('src', '') if icon_el is not None else ''
                episode = ''
                for en in element.findall('episode-num'):
                    sys_ = en.get('system', '')
                    if 'xmltv_ns' in sys_:
                        parts = (en.text or '').split('.')
                        s = int(parts[0].strip()) + 1 if parts[0].strip().isdigit() else 0
                        e = int(parts[1].strip()) + 1 if len(parts) > 1 and parts[1].strip().isdigit() else 0
                        if s and e:
                            episode = f'S{s:02d}E{e:02d}'
                        break
                    elif 'onscreen' in sys_:
                        episode = en.text or ''
                rating = ''
                for r in element.findall('rating'):
                    rating = r.findtext('value') or ''
                    break
                entry = {
                    'channel': cid,
                    'start_timestamp': start,
                    'stop_timestamp': stop,
                    'name': title,
                    'descr': desc,
                    'screenshot_uri': icon,
                    'category': cat,
                    'episode': episode,
                    'rating': rating,
                }
                programmes.setdefault(cid, []).append(entry)
                channels.setdefault(cid, cid)
            # Discard all processed siblings but not an unfinished node.
            if root_element is not element:
                root_element.clear()
            if len(channels) > MAX_CHANNELS:
                raise XMLTVLimitError('XMLTV channel limit exceeded','channels')
    finally:
        stream.close()
    if skipped:
        warn('XMLTV: skipped {} invalid programme timestamps/intervals'.format(skipped))
    for cid in programmes:
        programmes[cid].sort(key=lambda x: x['start_timestamp'])
    info(f'XMLTV: {len(channels)} channels, '
         f'{sum(len(v) for v in programmes.values())} programmes')
    return channels, programmes

_MEM_CACHE    = {}
_MEM_LOCK     = threading.Lock()
_REFRESH_LOCK = threading.Lock()
_WARMUP_THREADS = {}
_WARMUP_LOCK  = threading.Lock()


def diagnostic(code,**fields):
    from live_diagnostics import record
    record('epg',code,**fields)


def request_refresh(portal_id,p,force=False):
    """Persist intent in Kodi, then let the long-lived service own the worker."""
    import uuid,xbmcgui
    xbmcgui.Window(10000).setProperty('XtreamMate.EPGRefreshRequest',json.dumps({
        'pid':str(portal_id),'force':bool(force),'at':time.time(),'nonce':uuid.uuid4().hex}))
    diagnostic('REQUESTED',running=False,requested=True)


_LAST_REFRESH_REQUEST=''


def poll_refresh_request():
    import xbmcgui,portals
    global _LAST_REFRESH_REQUEST
    raw=xbmcgui.Window(10000).getProperty('XtreamMate.EPGRefreshRequest')
    if not raw or len(raw)>4096: return
    try: value=json.loads(raw)
    except (ValueError,TypeError): return
    if not isinstance(value,dict) or value.get('nonce')==_LAST_REFRESH_REQUEST: return
    try:
        if not 0<=time.time()-float(value.get('at',0))<120: return
    except (ValueError,TypeError): return
    p=portals.get_by_id(value.get('pid'))
    if not p or not p.get('enabled',True): return
    warmup_async(p['id'],p,force=bool(value.get('force')))
    _LAST_REFRESH_REQUEST=value.get('nonce')


def _mem_get(portal_id):
    with _MEM_LOCK:
        return _MEM_CACHE.get(portal_id)


def _mem_set(portal_id, data):
    with _MEM_LOCK:
        _MEM_CACHE[portal_id] = data


def _mem_clear(portal_id=None):
    with _MEM_LOCK:
        if portal_id is None:
            _MEM_CACHE.clear()
        else:
            _MEM_CACHE.pop(portal_id, None)


def _disk_ck(portal_id):
    return cache_key(f'epg2_{portal_id}')


def _load_disk(portal_id, max_age):
    return cache_get(_disk_ck(portal_id), max_age=max_age)


def _save_disk(portal_id, data, notify=True):
    if cache_set(_disk_ck(portal_id), data) is False:
        from epg_status import update
        update(portal_id, 'cache', 'CACHE_WRITE_FAILED', exception_class='OSError')
        raise OSError('EPG cache could not be persisted')
    from epg_status import changed, update
    if notify: changed(portal_id)
    update(portal_id, 'cache', 'READY', channels=len(data),
           programmes=sum(len(v) for v in data.values() if isinstance(v,list)))


def load_cache(portal_id):
    cached = _mem_get(portal_id)
    if cached is not None:
        return cached
    age_s   = setting_int('epg_refresh_hours', 12) * 3600
    on_disk = _load_disk(portal_id, max_age=age_s)
    if not isinstance(on_disk, dict):
        # A failed refresh must not hide still-current/future programmes from
        # the previous successful import. Resolver rejects expired events.
        on_disk = _load_disk(portal_id,max_age=10*86400)
    if isinstance(on_disk, dict):
        _mem_set(portal_id, on_disk)
        return on_disk
    return {}


def _is_fresh(portal_id):
    age_s = setting_int('epg_refresh_hours', 12) * 3600
    return bool(_load_disk(portal_id, max_age=age_s))


def clear_cache(portal_id=None):
    _mem_clear(portal_id)


def _normalize_entries(entries):
    if isinstance(entries, list):
        return entries
    return []


def _to_int(v):
    try:
        return int(v)
    except Exception:
        return None


def _parse_hhmm(s):
    s = (s or '').strip()
    if not s or ':' not in s:
        return None
    try:
        parts = s.split(':')
        h = int(parts[0]); m = int(parts[1])
        sec = int(parts[2]) if len(parts) >= 3 else 0
        if not (0 <= h <= 23 and 0 <= m <= 59 and 0 <= sec <= 59):
            return None
        return h, m, sec
    except Exception:
        return None


def _event_start_end(ev):
    now_local = datetime.datetime.now()
    start_ts = (
        _to_int(ev.get('start_timestamp')) or
        _to_int(ev.get('start')) or
        _to_int(ev.get('begin_timestamp'))
    )
    end_ts = (
        _to_int(ev.get('stop_timestamp')) or
        _to_int(ev.get('end_timestamp')) or
        _to_int(ev.get('stop')) or
        _to_int(ev.get('finish_timestamp'))
    )
    if start_ts and end_ts:
        return start_ts, end_ts
    t_from = None
    t_to   = None
    for k in ('t_time', 'time', 'start_time', 'start'):
        v = ev.get(k)
        if isinstance(v, str) and ':' in v:
            t_from = v
            break
    for k in ('t_time_to', 'time_to', 'end_time', 'stop_time', 'stop'):
        v = ev.get(k)
        if isinstance(v, str) and ':' in v:
            t_to = v
            break
    p_from = _parse_hhmm(t_from) if t_from else None
    p_to   = _parse_hhmm(t_to)   if t_to   else None
    if p_from and p_to:
        dt_from = now_local.replace(hour=p_from[0], minute=p_from[1], second=p_from[2], microsecond=0)
        dt_to   = now_local.replace(hour=p_to[0],   minute=p_to[1],   second=p_to[2],   microsecond=0)
        if dt_to <= dt_from:
            from datetime import timedelta
            dt_to += timedelta(days=1)
        return int(dt_from.timestamp()), int(dt_to.timestamp())
    return None, None


def _fmt_hhmm(ts):
    try:
        return datetime.datetime.fromtimestamp(int(ts)).strftime('%H:%M')
    except Exception:
        return ''


def build_epg_ui(portal_id, epg_key, upcoming_count=3):
    if epg_key is None:
        return ('', '')
    key     = str(epg_key)
    cache   = load_cache(portal_id)
    entries = _normalize_entries(cache.get(key))
    if not entries:
        return ('', '')

    now_ts = int(time.time())

    structured = []
    for ev in entries:
        if not isinstance(ev, dict):
            continue
        title = (ev.get('name') or ev.get('title') or '').strip()
        if not title:
            continue
        st, en = _event_start_end(ev)
        if st is None or en is None:
            st_s = (ev.get('t_time') or ev.get('time') or '').strip()
            en_s = (ev.get('t_time_to') or ev.get('time_to') or '').strip()
            structured.append((None, None, st_s, en_s, title))
        else:
            structured.append((st, en, _fmt_hhmm(st), _fmt_hhmm(en), title))

    if not structured:
        return ('', '')

    structured.sort(key=lambda x: (x[0] is None, x[0] if x[0] is not None else 10**18))

    now_ev  = None
    idx_now = None
    for i, (st, en, st_s, en_s, title) in enumerate(structured):
        if st is not None and en is not None and st <= now_ts < en:
            now_ev  = (st_s, en_s, title)
            idx_now = i
            break

    if now_ev is None:
        for i, (st, en, st_s, en_s, title) in enumerate(structured):
            if st is not None and st > now_ts:
                now_ev  = (st_s, en_s, title)
                idx_now = i
                break

    if now_ev is None:
        st, en, st_s, en_s, title = structured[0]
        now_ev  = (st_s, en_s, title)
        idx_now = 0

    upcoming = []
    for j in range((idx_now or 0) + 1, len(structured)):
        st, en, st_s, en_s, title = structured[j]
        upcoming.append((st_s, en_s, title))
        if len(upcoming) >= int(upcoming_count):
            break

    st_s, en_s, title = now_ev
    time_part = f'{st_s} - {en_s}: ' if (st_s and en_s) else ''
    label2    = f'[COLOR=yellow][B]JETZT[/B][/COLOR]\n{time_part}{title}'.strip()

    plot_lines = [
        '[COLOR=yellow][B]JETZT[/B][/COLOR]',
        f'{time_part}{title}'.strip(),
        '',
    ]
    if upcoming:
        plot_lines.append('[COLOR=cyan][B]Programm:[/B][/COLOR]')
        for st_s, en_s, t in upcoming:
            tp = f'{st_s} - {en_s}: ' if (st_s and en_s) else ''
            plot_lines.append(f'{tp}{t}'.strip())

    plot = '\n'.join(l for l in plot_lines if l is not None).strip()
    return (label2, plot)


def build_now_inline(portal_id, epg_key):
    if epg_key is None:
        return ''
    key     = str(epg_key)
    cache   = load_cache(portal_id)
    entries = _normalize_entries(cache.get(key))
    if not entries:
        return ''

    now_ts = int(time.time())

    current = None
    for ev in entries:
        if not isinstance(ev, dict):
            continue
        st, en = _event_start_end(ev)
        if st and en and st <= now_ts < en:
            current = (ev, st, en)
            break

    if current is None:
        best = None
        for ev in entries:
            if not isinstance(ev, dict):
                continue
            st, en = _event_start_end(ev)
            if st and en and st > now_ts:
                if best is None or st < best[1]:
                    best = (ev, st, en)
        current = best

    if current is None:
        return ''

    ev, st, en = current
    title = (ev.get('name') or ev.get('title') or '').strip() or '?'
    return f'[COLOR=yellow]jetzt:[/COLOR] {_fmt_hhmm(st)} - {_fmt_hhmm(en)}: {title}'


def _parse_epg_id_from_cmd(cmd: str):
    if not cmd:
        return None
    try:
        cmd_decoded = unquote_plus(str(cmd))
    except Exception:
        cmd_decoded = str(cmd)
    m = re.search(r'/ch/(\d+)_', cmd_decoded)
    if not m:
        m = re.search(r'/ch/(\d+)(?:\b|/|$)', cmd_decoded)
    if not m:
        m = re.search(r'\bch_id=(\d+)', cmd_decoded)
    if not m:
        m = re.search(r'\bid=(\d+)', cmd_decoded)
    if not m:
        m = re.search(r'(\d+)_?\s*$', cmd_decoded)
    return m.group(1) if m else None


def resolve_epg_key(portal_id, channel: dict):
    if not isinstance(channel, dict):
        return None
    cache      = load_cache(portal_id)
    cache_keys = set(cache.keys()) if isinstance(cache, dict) else set()

    candidates = []
    cmd    = channel.get('cmd') or ''
    cmd_id = _parse_epg_id_from_cmd(cmd)
    if cmd_id:
        candidates.append(cmd_id)
    for k in ('epg_channel_id', 'epg_id', 'ch_id', 'id'):
        v = channel.get(k)
        if v is None:
            continue
        s = str(v).strip()
        if s and s.isdigit():
            candidates.append(s)

    for c in candidates:
        if str(c) in cache_keys:
            return str(c)

    if not cache_keys and candidates:
        return str(candidates[0])

    debug(f'[EPG] no cache match for {channel.get("name")} candidates={candidates}')
    return str(candidates[0]) if candidates else None


def _refresh_portal_epg(portal_id, p, force=False):
    # Several portals/GUI invocations must not parse large guides concurrently.
    # A duplicate worker must not wait indefinitely during a Kodi update/stop.
    if not _REFRESH_LOCK.acquire(timeout=0.1):
        diagnostic('REFRESH_BUSY',running=False)
        return None
    try:
        diagnostic('RUNNING',running=True)
        try:
            result=_refresh_portal_epg_inner(portal_id,p,force=force)
            if result:
                diagnostic('READY',running=False,channels=len(result),
                           programmes=sum(len(v) for v in result.values()),last_success=time.time())
                from epg_views import refresh_visible_page
                refresh_visible_page(portal_id)
            else:
                diagnostic('NO_NEW_GUIDE',running=False)
            if force:
                try:
                    import xbmcgui
                    from epg_status import read
                    state=read(portal_id).get('refresh',{})
                    code=state.get('code','READY' if result else 'NO_NEW_GUIDE')
                    xbmcgui.Dialog().notification('XCMate EPG',code+' · '+str(state.get('loaded',0))+' / '+str(state.get('failed',0)))
                except Exception: pass
            return result
        except Exception:
            diagnostic('REFRESH_FAILED',running=False)
            raise
        finally:
            from live_diagnostics import checkpoint
            checkpoint()
    finally:
        _REFRESH_LOCK.release()


def _refresh_portal_epg_inner(portal_id, p, force=False):
    if p.get('type')=='xtream' or p.get('source_schema')==1:
        from stream_epg import refresh
        import xbmc
        cancel = xbmc.Monitor().abortRequested if hasattr(xbmc,'Monitor') else lambda: False
        return refresh(p,force=force,cancel=cancel)
    epg_url = p.get('epg_url', '')
    if not epg_url:
        ptype = p.get('type', 'm3u')
        if ptype == 'xtream':
            from xtream import XtreamClient
            xc = XtreamClient(p['xc_host'], p['xc_user'], p['xc_pass'])
            epg_url = xc.get_xmltv_epg_url()
        elif ptype == 'stb':
            epg_url = _probe_stb_epg_url(_stb_base_url(p.get('stb_url', '')))

    programmes = {}
    channels   = {}

    if epg_url:
        from epg_status import update as source_status
        source_status(portal_id, 'provider', 'RUNNING', running=True)
        info('[EPG] fetching XMLTV guide (URL redacted)')
        stage, raw = 'DOWNLOAD', None
        try:
            raw, _ = http_get(epg_url, max_bytes=MAX_XML_BYTES, max_seconds=60)
            stage = 'PARSE'
            channels, programmes = parse_xmltv(raw)
            if not programmes:
                from epg_errors import EmptyGuideError
                raise EmptyGuideError('XMLTV contains no valid programmes')
            source_status(portal_id, 'provider', 'READY', running=False,
                          channels=len(channels), programmes=sum(len(v) for v in programmes.values()),
                          bytes=len(raw))
        except Exception as e:
            from epg_errors import failure_details
            _, fields = failure_details(e, stage)
            source_status(portal_id, 'provider', fields['failure_code'], running=False,
                          bytes=len(raw) if raw is not None else 0, **fields)
            diagnostic('PROVIDER_LIMIT' if isinstance(e,(XMLTVLimitError,ResponseLimitError))
                       else 'PROVIDER_FAILED',running=True,
                       bytes=len(raw) if raw is not None else 0, **fields)
            error('[EPG] fetch failed: {}'.format(type(e).__name__))

    if not programmes and p.get('type') == 'stb':
        warn('[EPG] XMLTV leer – verwende STB get_epg_info bulk')
        programmes, channels = _fetch_stb_bulk(p)

    if not programmes and p.get('type') == 'stb':
        warn('[EPG] bulk leer – verwende get_short_epg im EPG-Worker')
        # Already running in an EPG worker; do not spawn an untracked second
        # refresh that can race the next request or bypass the memory gate.
        programmes, channels = _fetch_stb_short_epg(p)

    # Preserve native Xtream/M3U/STB EPG, then overlay configured XMLTV feeds.
    # Each feed is optional: a failed remote URL never deletes working guide data.
    try:
        from epg_sources import merge_sources
        programmes, loaded, failed = merge_sources(
            portal_id, programmes, parse_xmltv)
        if loaded or failed:
            info('[EPG] external feeds loaded={} failed={}'.format(loaded, failed))
    except Exception as exc:
        error('[EPG] external source manager failed: {}'.format(type(exc).__name__))

    if programmes:
        from epg_views import _as_int
        now=time.time()
        usable=sum(1 for entries in programmes.values() for e in entries if isinstance(e,dict)
                   and _as_int(e.get('stop_timestamp'))>max(now,_as_int(e.get('start_timestamp')))
                   and 0<_as_int(e.get('start_timestamp'))<now+10*86400)
        if not usable:
            # A syntactically valid but obsolete feed must not replace a good
            # guide. Parsing success is distinct from usable cache publication.
            from epg_status import update
            update(portal_id,'cache','NO_CURRENT_WINDOW',running=False)
            diagnostic('NO_CURRENT_WINDOW',running=True)
            return {}
        _save_disk(portal_id, programmes)
        _mem_set(portal_id, programmes)
        info(f'[EPG] {portal_id}: {len(programmes)} channels saved')
    return programmes


def _fetch_stb_bulk(p):
    from stalker import client_for_portal
    stb = client_for_portal(p)
    if not stb or not stb.authenticate():
        return {}, {}
    try:
        raw, _ = http_get(stb._portal, params={
            'type'          : 'itv',
            'action'        : 'get_epg_info',
            'period'        : '5',
            'JsHttpRequest' : '1-xml',
        }, headers=stb._headers())
        data = json.loads(raw)
    except Exception as e:
        error(f'[EPG] get_epg_info failed: {e}')
        return {}, {}
    js = data.get('js', {}) if isinstance(data, dict) else {}
    if isinstance(js, dict) and 'data' in js:
        js = js['data']
    if not isinstance(js, dict):
        return {}, {}
    channels = {}
    for ch_id, entries in js.items():
        if isinstance(entries, list):
            for ev in entries:
                if isinstance(ev, dict):
                    name = ev.get('ch_name') or ev.get('name') or ''
                    if name:
                        channels[str(ch_id)] = name
                        break
    return js, channels


def _fetch_stb_short_epg(p):
    from stalker import client_for_portal
    stb = client_for_portal(p)
    if not stb or not stb.authenticate():
        return {}, {}

    channels_list = stb.get_live_channels()[:MAX_CHANNELS]
    programmes    = {}
    ch_names      = {}
    lock          = threading.Lock()
    deadline = time.monotonic() + 60

    def _fetch(ch):
        if time.monotonic() >= deadline:
            return
        ch_id  = str(ch.get('id', ''))
        tvg_id = ch.get('epg_channel_id') or ch_id
        entries = stb.get_short_epg(ch_id, count=10)
        if entries:
            with lock:
                programmes[tvg_id] = entries
                ch_names[tvg_id]   = ch.get('name', tvg_id)

    workers = min(4, max(1, len(channels_list)))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(_fetch, channels_list))

    return programmes, ch_names


def cache_has_data(portal_id) -> bool:
    return bool(load_cache(portal_id))


def warmup_async(portal_id, p, force=False):
    if not force and _is_fresh(portal_id):
        return
    with _WARMUP_LOCK:
        t = _WARMUP_THREADS.get(portal_id)
        if t and t.is_alive():
            return

        def _run():
            import xbmc
            xbmc.sleep(200)
            try:
                _refresh_portal_epg(portal_id, p, force=force)
            except Exception as exc:
                error('[EPG] background refresh failed: ' + type(exc).__name__)

        t = threading.Thread(target=_run, daemon=True, name=f'epg_warmup_{portal_id}')
        t.start()
        _WARMUP_THREADS[portal_id] = t


def ensure_epg_loaded_for_portal(p: dict, force: bool = False):
    portal_id = p.get('id', 'unknown')
    if force or not _is_fresh(portal_id):
        _refresh_portal_epg(portal_id, p, force=force)
    data = load_cache(portal_id)
    return data if data else None


def _stb_base_url(stb_url: str) -> str:
    base = stb_url.rstrip('/')
    for sfx in ('/c', '/stalker_portal/c', '/stalker_portal'):
        if base.endswith(sfx):
            return base[:-len(sfx)]
    return base


def _probe_stb_epg_url(base: str) -> str:
    candidates = [
        base + '/xmltv.php',
        base + '/epg.xml',
        base + '/stalker_portal/xmltv.php',
    ]
    result = [None]
    lock   = threading.Lock()

    def _try(url):
        try:
            raw, _ = http_get(url, timeout=2)
            if raw and len(raw) > 200 and b'<tv' in raw[:512]:
                with lock:
                    if result[0] is None:
                        result[0] = url
                        info(f'[EPG] XMLTV found at: {url}')
        except Exception:
            pass

    with ThreadPoolExecutor(max_workers=len(candidates)) as ex:
        list(ex.map(_try, candidates))

    return result[0] or ''


_managers = {}

def get_manager(playlist_idx: int):
    return None

def ensure_epg_loaded(playlist_idx: int, force=False):
    return None

class EPGManager:
    def __init__(self, data: dict):
        self._programmes = data


    def has_data(self) -> bool:
        return bool(self._programmes)

    def get_channel_name(self, tvg_id: str) -> str:
        return str(tvg_id)

    @staticmethod
    def _entry_to_programme(e: dict) -> Programme:
        return Programme(
            channel  = e.get('channel', ''),
            start    = e.get('start_timestamp', 0),
            stop     = e.get('stop_timestamp',  0),
            title    = e.get('name',            ''),
            desc     = e.get('descr',           ''),
            category = e.get('category',        ''),
            episode  = e.get('episode',         ''),
            icon     = e.get('screenshot_uri',  ''),
            rating   = e.get('rating',          ''),
        )

    def get_current(self, tvg_id: str, now: float = None) -> Programme:
        if now is None:
            now = time.time()
        for e in self._programmes.get(str(tvg_id), []):
            s = e.get('start_timestamp', 0)
            t = e.get('stop_timestamp',  0)
            if s <= now < t:
                return self._entry_to_programme(e)
        return None

    def get_range(self, tvg_id: str, from_ts: float, to_ts: float):
        result = []
        for e in self._programmes.get(str(tvg_id), []):
            s = e.get('start_timestamp', 0)
            t = e.get('stop_timestamp',  0)
            if t > from_ts and s < to_ts:
                result.append(self._entry_to_programme(e))
        return result
