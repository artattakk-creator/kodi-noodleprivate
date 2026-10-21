"""Small, allowlisted diagnostic snapshots; never persist provider identities.

One atomic file per component avoids service/plugin writers overwriting each
other. Home-window properties provide the newest in-process snapshot; disk
history remains available after Stop and after a Kodi restart.
"""
import json
import math
import os
import tempfile
import time
import threading
from collections import deque

STAGES = ('session', 'ownership', 'service', 'dialog', 'focus', 'input',
          'exit',
          'epg', 'epg_source', 'epg_list', 'performance',
          'catalog_performance', 'epg_performance')
FIELDS = frozenset(('video', 'marker', 'catalog', 'channels', 'programmes',
                    'matched', 'visible', 'now_count', 'next_count', 'loaded',
                    'failed', 'bytes', 'focus_id', 'dialog_id', 'focused',
                    'action_id', 'button_code', 'count', 'running', 'last_success',
                    'source_index', 'enabled', 'requested', 'item_tag', 'fullscreen',
                    'limit_bytes', 'limit_value', 'http_status', 'build',
                    'index_ms', 'snapshot_ms', 'render_ms', 'focus_ms', 'items',
                    'cache_ms', 'cache_hit', 'last_channels', 'last_programmes',
                    'control_id', 'focus_before', 'learned_left_action',
                    'left_received', 'left_channels', 'left_groups', 'error_line'))
FIELDS = FIELDS | {'window_id','busy','duration_ms','pending','resume_saved'}
TEXT_FIELDS = {
    'error_file': frozenset(('epg.py','epg_io.py','xmltv_stream.py','stream_epg.py','network_io.py','utils.py','epg_sources.py','library_index.py')),
    'mode_before': frozenset(('hidden','info','controls','extras','channels','groups','guide')),
    'mode_after': frozenset(('hidden','info','controls','extras','channels','groups','guide')),
    'input_source': frozenset(('native','control','bridge')),
    'command': frozenset(('left','right','up','down','ok','back','menu','epg','guide','more',
        'info','play_pause','long_left','long_right','long_up','long_down','long_ok',
        'long_back','long_menu','long_play_pause')),
    'failure_stage': frozenset(('BUILD_CONTROLS', 'CONTROL_LIST', 'WINDOW_SHOW',
                               'RENDER', 'FOCUS', 'DOWNLOAD', 'PARSE', 'MERGE')),
    'exception_class': frozenset(('TypeError', 'RuntimeError', 'ValueError',
        'ReferenceError', 'SystemError', 'MemoryError', 'TimeoutError', 'OSError',
        'XMLTVLimitError', 'ResponseLimitError', 'ParseError', 'BadGzipFile',
        'EOFError', 'error', 'HTTPError', 'HTTPStatusError', 'HTTPCompressionError', 'EmptyGuideError',
        'UnsafeXMLTV','XMLTVSyntaxError','InterruptedError','ReadTimeout', 'ConnectTimeout', 'WriteTimeout', 'PoolTimeout',
        'ConnectError', 'ReadError', 'ProxyError', 'RemoteProtocolError',
        'PermissionError', 'FileNotFoundError', 'OTHER')),
    'limit_kind': frozenset(('input_bytes', 'decoded_bytes', 'bytes',
                             'programmes', 'channels','field_bytes','nesting')),
    'failure_code': frozenset(('HTTP_INPUT_BYTES_LIMIT', 'HTTP_DECODED_BYTES_LIMIT',
        'XMLTV_INPUT_BYTES_LIMIT', 'XMLTV_DECODED_BYTES_LIMIT', 'XMLTV_BYTES_LIMIT',
        'XMLTV_PROGRAMMES_LIMIT', 'XMLTV_CHANNELS_LIMIT', 'GZIP_INVALID',
        'HTTP_COMPRESSION_FAILED', 'INVALID_XMLTV', 'PARSE_TIMEOUT',
        'XMLTV_UNSAFE_DECLARATION','XMLTV_FIELD_BYTES_LIMIT','XMLTV_NESTING_LIMIT', 'DOWNLOAD_TIMEOUT', 'DOWNLOAD_FAILED', 'PARSE_FAILED', 'EMPTY_GUIDE')),
}
_WRITTEN = {}
_INPUT_PENDING = deque(maxlen=64)
_EXIT_PENDING = deque(maxlen=64)
_INPUT_LOCK = threading.RLock()
PREFIX = 'XtreamMate.Diagnostic.'
EXPLANATIONS={
    'URL_NOT_VERIFIED':'Player-Pfad passt nicht; keine passende aktuelle ListItem-Kennung.',
    'ITEM_IDENTITY':'Aktuelles Kodi-ListItem bestätigt die XCMate-Live-Sitzung.',
    'URL_IDENTITY':'Laufender Stream stimmt mit einem konfigurierten Live-Sender überein.',
    'WAIT_FULLSCREEN':'Wiedergabe erkannt; Kodi-Vollbild ist noch nicht aktiv.',
    'CANDIDATE_CREATED':'Navigator erstellt; Zulassung und Anzeige folgen getrennt.',
    'SHOW_REQUESTED':'Dialoganzeige angefordert; Fokus und Eingaben separat prüfen.',
    'ACTIVE_DIALOG':'XCMate ist der aktuelle oberste Dialog.',
    'OTHER_DIALOG':'Ein anderer Dialog liegt oben; XCMate erzwingt keinen Fokuswechsel.',
    'REQUESTED':'Aktualisierung angefordert; der Dienst muss sie noch übernehmen.',
    'READY':'EPG erfolgreich verarbeitet und gespeichert.',
    'NO_NEW_GUIDE':'Keine neuen Guide-Daten; vorhandener Cache bleibt erhalten.',
    'XMLTV_BYTES_LIMIT':'XMLTV-Datei überschreitet das unveränderte Größenlimit.',
    'HTTP_BYTE_LIMIT':'HTTP-Antwort überschreitet das Größenlimit.',
}


def _clean(value):
    if not isinstance(value, dict) or value.get('stage') not in STAGES:
        return None
    code = value.get('code', '')
    if not isinstance(code, str) or len(code)>64 or not code or any(
            c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789' for c in code):
        return None
    at = value.get('at')
    if not isinstance(at, (int,float)) or not math.isfinite(at): return None
    result = {'stage': value['stage'], 'code': code, 'at': at}
    for key in FIELDS:
        v = value.get(key)
        if isinstance(v, (int,float,bool)) and math.isfinite(v): result[key]=v
    for key, allowed in TEXT_FIELDS.items():
        v = value.get(key)
        if isinstance(v, str): result[key] = v if v in allowed else 'OTHER'
    return result


def _path(stage):
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(), 'xcmate_diagnostic_'+stage+'.json')


def _disk(stage):
    try:
        with open(_path(stage), encoding='utf-8') as f:
            raw=f.read(32769)
        if len(raw)>32768: return []
        data=json.loads(raw)
        return [e for e in (_clean(v) for v in data[-(64 if stage=='input' else 16):]) if e and e['stage']==stage]
    except Exception:
        return []


def record(stage, code, **fields):
    """Diagnostics must never break playback, even with an unwritable profile."""
    entry=_clean(dict(fields, stage=stage, code=code, at=time.time()))
    if entry is None: return
    if stage=='input' and code=='NATIVE_ACTION' and entry.get('action_id') in (9,10,92):
        try:
            import xbmc
            xbmc.log('[XCMate][EXIT] BACK_RECEIVED '+json.dumps(entry,sort_keys=True),xbmc.LOGINFO)
        except Exception: pass
    if stage=='epg' and 'last_success' not in entry:
        for prior in reversed(_disk(stage)):
            if 'last_success' in prior:
                entry['last_success']=prior['last_success']
                break
    try:
        import xbmcgui
        xbmcgui.Window(10000).setProperty(PREFIX+stage,json.dumps(entry))
    except Exception:
        pass
    if stage in ('input','exit'):
        # Native callbacks only enqueue bounded data. Service/Stop flushes it;
        # no profile reads, fsync or JSON-file rewrite for each remote press.
        with _INPUT_LOCK: (_INPUT_PENDING if stage=='input' else _EXIT_PENDING).append(entry)
        return
    previous=_WRITTEN.get(stage)
    if previous and previous['code']==code and entry['at']-previous['at']<2:
        return
    _save(entry)


def _save(entry, batch=None):
    stage=entry['stage']
    target=temp=None
    try:
        target=_path(stage)
        entries=_disk(stage)
        entries.extend(batch if batch is not None else [entry])
        fd,temp=tempfile.mkstemp(prefix='.xcmate-diag-', dir=os.path.dirname(target))
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            json.dump(entries[-(64 if stage=='input' else 16):],f,separators=(',',':'))
        os.replace(temp,target)
        _WRITTEN[stage]=entry
        return True
    except Exception:
        pass
    finally:
        if temp and os.path.exists(temp):
            try: os.unlink(temp)
            except OSError: pass


def checkpoint():
    """Flush the newest throttled input/focus state before the dialog closes."""
    flush_input(include_exit=False)
    for entry in snapshots().values():
        if entry['stage']=='exit': continue
        if entry!=_WRITTEN.get(entry['stage']): _save(entry)


def flush_input(include_exit=True):
    """Called by the service timer and on close; retain a 64-event input trail."""
    with _INPUT_LOCK:
        if _INPUT_PENDING and _save(_INPUT_PENDING[-1], list(_INPUT_PENDING)):
            _INPUT_PENDING.clear()
        if include_exit and _EXIT_PENDING and _save(_EXIT_PENDING[-1], list(_EXIT_PENDING)):
            _EXIT_PENDING.clear()


def snapshots():
    results={}
    for stage in STAGES:
        entries=_disk(stage)
        try:
            import xbmcgui
            current=_clean(json.loads(xbmcgui.Window(10000).getProperty(PREFIX+stage)))
            if current and current['stage']==stage: entries.append(current)
        except Exception: pass
        if entries: results[stage]=max(entries,key=lambda e:e['at'])
    return results


def report():
    flush_input()
    lines=['=== Gespeicherte Live-/EPG-Diagnose (auch nach Stop/Neustart) ===']
    for stage,entry in snapshots().items():
        lines.append('{}: {} [{}]'.format(stage,entry['code'],
            time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(entry['at']))))
        if entry['code'] in EXPLANATIONS: lines.append('  '+EXPLANATIONS[entry['code']])
        values=['{}={}'.format(k,entry[k]) for k in sorted(FIELDS | TEXT_FIELDS.keys()) if k in entry]
        if values: lines.append('  '+', '.join(values))
        if stage=='epg_list':
            lines.append('  Jetzt/Danach-Treffer: {}/{} sichtbare Sender'.format(
                entry.get('matched',0),entry.get('visible',0)))
        if entry.get('last_success'):
            lines.append('  Letzte erfolgreiche Aktualisierung: '+time.strftime(
                '%Y-%m-%d %H:%M:%S',time.localtime(entry['last_success'])))
        history=_disk(stage)
        if history:
            lines.append('  Verlauf: '+' → '.join(e['code'] for e in history[-8:]))
            if stage=='input':
                for event in history:
                    values=['{}={}'.format(k,event[k]) for k in ('input_source','action_id',
                        'button_code','command','mode_before','mode_after','focus_before','focus_id',
                        'control_id','learned_left_action') if k in event]
                    lines.append('  {} {} {}'.format(time.strftime('%H:%M:%S',time.localtime(event['at'])),
                                                      event['code'],' '.join(values)))
            failure = next((e for e in reversed(history) if 'exception_class' in e), None)
            if failure:
                details = ['{}={}'.format(k, failure[k]) for k in sorted(FIELDS | TEXT_FIELDS.keys())
                           if k in failure and k != 'last_success']
                lines.append('  Letzter gespeicherter Fehler: {} [{}] {}'.format(
                    failure['code'], time.strftime('%Y-%m-%d %H:%M:%S',
                    time.localtime(failure['at'])), ', '.join(details)))
    return lines
