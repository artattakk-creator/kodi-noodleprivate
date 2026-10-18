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

STAGES = ('session', 'ownership', 'service', 'dialog', 'focus', 'input',
          'epg', 'epg_source', 'epg_list')
FIELDS = frozenset(('video', 'marker', 'catalog', 'channels', 'programmes',
                    'matched', 'visible', 'now_count', 'next_count', 'loaded',
                    'failed', 'bytes', 'focus_id', 'dialog_id', 'focused',
                    'action_id', 'button_code', 'count', 'running', 'last_success',
                    'source_index', 'enabled', 'requested', 'item_tag', 'fullscreen','limit_bytes','build'))
_WRITTEN = {}
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
        return [e for e in (_clean(v) for v in data[-16:]) if e and e['stage']==stage]
    except Exception:
        return []


def record(stage, code, **fields):
    """Diagnostics must never break playback, even with an unwritable profile."""
    entry=_clean(dict(fields, stage=stage, code=code, at=time.time()))
    if entry is None: return
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
    previous=_WRITTEN.get(stage)
    if previous and previous['code']==code and entry['at']-previous['at']<2:
        return
    _save(entry)


def _save(entry):
    stage=entry['stage']
    target=temp=None
    try:
        target=_path(stage)
        entries=_disk(stage)
        entries.append(entry)
        fd,temp=tempfile.mkstemp(prefix='.xcmate-diag-', dir=os.path.dirname(target))
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            json.dump(entries[-16:],f,separators=(',',':'))
        os.replace(temp,target)
        _WRITTEN[stage]=entry
    except Exception:
        pass
    finally:
        if temp and os.path.exists(temp):
            try: os.unlink(temp)
            except OSError: pass


def checkpoint():
    """Flush the newest throttled input/focus state before the dialog closes."""
    for entry in snapshots().values():
        if entry!=_WRITTEN.get(entry['stage']): _save(entry)


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
    lines=['=== Gespeicherte Live-/EPG-Diagnose (auch nach Stop/Neustart) ===']
    for stage,entry in snapshots().items():
        lines.append('{}: {} [{}]'.format(stage,entry['code'],
            time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(entry['at']))))
        if entry['code'] in EXPLANATIONS: lines.append('  '+EXPLANATIONS[entry['code']])
        values=['{}={}'.format(k,entry[k]) for k in sorted(FIELDS) if k in entry]
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
    return lines
