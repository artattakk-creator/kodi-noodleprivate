# -*- coding: utf-8 -*-
"""Transactional, opt-in branding patch. Python-only core, tested without Kodi.

No mutation of BINGIE navigation, focus expressions, widget URLs or SkinShortcuts.
Changes exclusively named media files and specific logo/intro-timing literals.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import tempfile
from branding_colors import edit_defaults, PALETTE, names_for_settings, safe_skin_value

ADDON_ID = 'script.gsmedia.xcmate.branding'
SKIN_ID = 'skin.titan.bingie.mod'
SKIN_VERSION = '2.2.3'
LOGO_OLD = b'home/bingie_mod_logo.png'
LOGO_NEW = ('special://home/addons/' + ADDON_ID + '/resources/media/xcmate_logo.png').encode('ascii')
MODE_VIDEOS = {
    'netflix_default': ('netflix_intro_2_1080p.mp4', 'netflix_intro_2_2160p.mp4'),
    'netflix_alternative': ('netflix_intro_1080p.mp4', 'netflix_intro_2160p.mp4'),
    'netflix_extended': ('netflix_intro_extended_1080p.mp4',),
}
# For the 7.04-second intro, keep one second to let Kodi finish its transition.
TIMING_OLD = {
    'netflix_default': [('AlarmClock(startup,ClearProperty(StartupMask,home),00:10,silent)', 2)],
    'netflix_alternative': [('AlarmClock(startup,ClearProperty(StartupMask,home),00:09,silent)', 1)],
    'netflix_extended': [('AlarmClock(startup,ClearProperty(StartupMask,home),00:22,silent)', 1)],
}
MAX_XML = 3 * 1024 * 1024
MAX_MEDIA = 130 * 1024 * 1024


class BrandingError(Exception):
    pass


def digest(data):
    return sha256(data).hexdigest()


def _read(path, limit):
    with open(path, 'rb') as file:
        data = file.read(limit + 1)
    if len(data) > limit:
        raise BrandingError('Datei zu groß: ' + path.name)
    return data


def _validate_paths(skin):
    skin = Path(skin).absolute()
    if not skin.is_dir() or skin.is_symlink():
        raise BrandingError('BINGIE-Skin-Verzeichnis nicht gefunden oder Symlink.')
    meta = _read(skin / 'addon.xml', MAX_XML).decode('utf-8-sig')
    import xml.etree.ElementTree as ET
    try:
        node = ET.fromstring(meta)
    except ET.ParseError:
        raise BrandingError('Skin-Metadaten ungültig.')
    if node.attrib.get('id') != SKIN_ID or node.attrib.get('version') != SKIN_VERSION:
        raise BrandingError('Nicht unterstützter BINGIE-Build (erfordert 2.2.3).')
    return skin


def supported(skin):
    try:
        _validate_paths(skin)
        return True
    except (BrandingError, OSError):
        return False


def _target(skin, rel):
    # No arbitrary paths or symlinks; never follow a modified skin out of root.
    if rel.startswith('/') or '\\' in rel or '..' in Path(rel).parts:
        raise BrandingError('Unsicherer relativer Pfad.')
    root = Path(skin).absolute()
    path = root.joinpath(*Path(rel).parts)
    if root not in path.resolve(strict=False).parents or not path.is_file():
        raise BrandingError('Benötigte Skin-Datei fehlt: ' + rel)
    cur = path
    while cur != root:
        if cur.is_symlink():
            raise BrandingError('Symlink als Ziel nicht zulässig: ' + rel)
        cur = cur.parent
    return path


def _replacement(data, before, after, count, rel):
    if data.count(before) != count:
        raise BrandingError('Unbekannter Skin-Stand (' + rel + '): Originaltext nicht eindeutig.')
    return data.replace(before, after), {'old': before.decode('ascii'), 'new': after.decode('ascii'), 'count': count}


def plan(skin, addon, mode):
    skin = _validate_paths(skin)
    addon = Path(addon)
    if mode not in MODE_VIDEOS:
        raise BrandingError('Nicht unterstützter Intro-Modus: ' + str(mode))
    media = addon / 'resources' / 'media'
    assets = {'intro': media / 'XCMate-intro.mp4', 'splash': media / 'xcmate_splash.png', 'logo': media / 'xcmate_logo.png'}
    manifest_path = media / 'asset_sha256.json'
    expected = json.loads(_read(manifest_path, 32768).decode('utf-8'))
    source = {}
    for key, path in assets.items():
        data = _read(path, MAX_MEDIA)
        if digest(data) != expected.get(path.name):
            raise BrandingError('Paketintegrität fehlgeschlagen: ' + path.name)
        source[key] = data
    edits = []
    for video in MODE_VIDEOS[mode]:
        edits.append(('extras/media/' + video, source['intro'], []))
    for splash in ('bingie_splash.png', 'bingie_splash2.png'):
        edits.append(('extras/media/' + splash, source['splash'], []))
    for xml in ('xml/IncludesHomeBingie.xml', 'xml/Custom_1101_StartUp.xml', 'xml/Custom_1102_StartUp2.xml'):
        rel = xml
        original = _read(_target(skin, rel), MAX_XML)
        out, delta = _replacement(original, LOGO_OLD, LOGO_NEW, 1, rel)
        deltas = [delta]
        if rel == 'xml/IncludesHomeBingie.xml':
            red = b'colordiffuse="ffE50914">bingie/line.png'
            blue = b'colordiffuse="FF159FEA">bingie/line.png'
            if out.count(red) == 1:
                out, change = _replacement(out, red, blue, 1, rel)
                deltas.append(change)
        else:
            old = b'colordiffuse="ffe50914" border="4"'
            new = b'colordiffuse="ff159fea" border="4"'
            if out.count(old) == 1:
                out, change = _replacement(out, old, new, 1, rel)
                deltas.append(change)
        edits.append((rel, out, deltas))
    mask = 'xml/Custom_1103_StartUpMask.xml'
    value = _read(_target(skin, mask), MAX_XML)
    operations = []
    for old, count in TIMING_OLD[mode]:
        new = old.replace('00:10', '00:08').replace('00:09', '00:08').replace('00:22', '00:08')
        value, delta = _replacement(value, old.encode('ascii'), new.encode('ascii'), count, mask)
        operations.append(delta)
    edits.append((mask, value, operations))
    # Named global colors complement the existing BINGIE Skin.String palette.
    colors = 'colors/defaults.xml'
    color_before = _read(_target(skin, colors), MAX_XML)
    color_after, color_deltas = edit_defaults(color_before)
    if color_deltas:
        edits.append((colors, color_after, color_deltas))
    prepared = []
    for rel, after, delta in edits:
        path = _target(skin, rel)
        before = _read(path, MAX_MEDIA)
        if before == after:
            raise BrandingError('Datei bereits verändert oder mit Branding identisch: ' + rel)
        prepared.append({'relative': rel, 'path': path, 'before': before, 'after': after,
                         'old_sha256': digest(before), 'new_sha256': digest(after),
                         'type': 'xml' if rel.endswith('.xml') else 'media', 'deltas': delta})
    return prepared


def _atomic(path, data):
    path = Path(path)
    fd, temp = tempfile.mkstemp(prefix='.xcmate-branding-', suffix='.tmp', dir=str(path.parent))
    try:
        try:
            os.fchmod(fd, path.stat().st_mode & 0o777)
        except (OSError, AttributeError):
            pass
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, str(path))
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def _state_path(userdata):
    return Path(userdata) / 'state.json'


def _load(userdata):
    path = _state_path(userdata)
    if not path.is_file():
        return None
    state = json.loads(_read(path, 131072).decode('utf-8'))
    if state.get('version') != 1 or not isinstance(state.get('files'), list):
        raise BrandingError('Statusdatei ungültig; keine Änderungen.')
    return state


def status(skin, userdata, color_get=None):
    try:
        state = _load(userdata)
    except (OSError, ValueError, TypeError, BrandingError) as exc:
        return {'state': 'error', 'message': str(exc)}
    if state is None:
        return {'state': 'not_installed'}
    if state['state'] == 'restored':
        return {'state': 'not_installed', 'history': state.get('backup_id')}
    if state['state'] not in ('pending', 'active'):
        return {'state': 'error', 'message': 'Unbekannter Backupstatus.'}
    matches = 0
    for entry in state['files']:
        try:
            if digest(_read(_target(skin, entry['relative']), MAX_MEDIA)) == entry['new_sha256']:
                matches += 1
        except (BrandingError, OSError):
            pass
    color_ok = None
    if color_get is not None and state.get('colors_after'):
        color_ok = sum(color_get(k) == v for k, v in state['colors_after'].items())
    return {'state': state['state'], 'matched': matches, 'total': len(state['files']),
            'color_matched': color_ok, 'color_total': len(state.get('colors_after', {})),
            'mode': state.get('mode'), 'backup_id': state['backup_id']}


@contextmanager
def _locked(userdata):
    root = Path(userdata)
    root.mkdir(parents=True, exist_ok=True)
    file = root / 'operation.lock'
    try:
        fd = os.open(str(file), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise BrandingError('Es besteht eine Branding-Sperre. Keine Änderungen durchgeführt. Diagnose prüfen.')
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(str(os.getpid()))
        yield
    finally:
        file.unlink(missing_ok=True)


def _write_state(userdata, data):
    _atomic(_state_path(userdata), json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True).encode('utf-8'))


def apply(skin, addon, userdata, mode, color_get=None, color_set=None):
    with _locked(userdata):
        existing = _load(userdata)
        if existing and existing.get('state') != 'restored':
            raise BrandingError('Branding bereits installiert oder unvollständige Transaktion; erst wiederherstellen.')
        if not callable(color_get) or not callable(color_set):
            raise BrandingError('BINGIE-Farbsteuerung nicht verfügbar. Keine Änderung durchgeführt.')
        colors_after = names_for_settings()
        colors_before = {key: color_get(key) for key in colors_after}
        if not all(safe_skin_value(v) for v in colors_before.values()):
            raise BrandingError('Unbekannte Farbeinstellung gefunden; Originalwerte werden geschützt.')
        entries = plan(skin, addon, mode)
        backup_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        backup_dir = Path(userdata) / 'backups' / backup_id
        backup_dir.mkdir(parents=True, exist_ok=False)
        needed = sum(len(x['before']) + len(x['after']) for x in entries)
        if shutil.disk_usage(str(backup_dir)).free < needed + 16 * 1024 * 1024:
            raise BrandingError('Zu wenig Speicherplatz für Original-Backups und Patch.')
        manifest = {'version': 1, 'state': 'pending', 'skin_path': str(Path(skin).absolute()),
                    'skin_version': SKIN_VERSION, 'backup_id': backup_id, 'mode': mode,
                    'applied_at': datetime.now(timezone.utc).isoformat(), 'files': [],
                    'colors_before': colors_before, 'colors_after': colors_after}
        for index, item in enumerate(entries):
            filename = '{:02d}.original'.format(index)
            backup_path = backup_dir / filename
            with open(backup_path, 'xb') as file:
                file.write(item['before'])
                file.flush()
                os.fsync(file.fileno())
            if digest(_read(backup_path, MAX_MEDIA)) != item['old_sha256']:
                raise BrandingError('Originalbackup konnte nicht verifiziert werden.')
            manifest['files'].append({'relative': item['relative'], 'backup': filename,
                                      'old_sha256': item['old_sha256'], 'new_sha256': item['new_sha256'],
                                      'type': item['type'], 'deltas': item['deltas']})
        _write_state(userdata, manifest)  # Crash recovery uses pending state.
        completed = []
        try:
            for item in entries:
                if digest(_read(item['path'], MAX_MEDIA)) != item['old_sha256']:
                    raise BrandingError('Skin-Datei während Installation verändert: ' + item['relative'])
                _atomic(item['path'], item['after'])
                if digest(_read(item['path'], MAX_MEDIA)) != item['new_sha256']:
                    raise BrandingError('Patch-Kontrolle fehlgeschlagen: ' + item['relative'])
                completed.append(item)
            for key, desired in colors_after.items():
                if colors_before[key] != desired:
                    color_set(key, desired)
        except Exception:
            try:
                for key, original in colors_before.items():
                    if color_get(key) != original:
                        color_set(key, original)
            except Exception:
                pass  # Pending state can be restored on next invocation.
            rollback_errors = []
            for item in reversed(completed):
                try:
                    if digest(_read(item['path'], MAX_MEDIA)) == item['new_sha256']:
                        _atomic(item['path'], item['before'])
                except Exception:
                    rollback_errors.append(item['relative'])
            if not rollback_errors:
                manifest['state'] = 'restored'
                _write_state(userdata, manifest)
            raise
        manifest['state'] = 'active'
        _write_state(userdata, manifest)
        return {'files': len(entries), 'backup': str(backup_dir)}


def restore(skin, userdata, color_get=None, color_set=None):
    with _locked(userdata):
        state = _load(userdata)
        if not state or state.get('state') == 'restored':
            raise BrandingError('Kein aktiver Backupstand.')
        if state.get('state') not in ('active', 'pending'):
            raise BrandingError('Unbekannter Patchstatus.')
        if str(Path(skin).absolute()) != state['skin_path']:
            raise BrandingError('Skin-Verzeichnis geändert; Backup nicht blind übertragen.')
        _validate_paths(skin)
        if state.get('colors_after') and (not callable(color_get) or not callable(color_set)):
            raise BrandingError('BINGIE-Farbsteuerung fehlt. Keine Wiederherstellung durchgeführt.')
        colors_before = state.get('colors_before', {})
        colors_after = state.get('colors_after', {})
        changed_colors = {}
        for key, desired in colors_after.items():
            value = color_get(key)
            if value not in (desired, colors_before.get(key, '')):
                raise BrandingError('Farbe nach dem Patch manuell verändert: '+ key + '. Originale schützen.')
            if not safe_skin_value(colors_before.get(key, '')):
                raise BrandingError('Farbbackup enthält ungültigen Wert: ' + key)
            if value != colors_before.get(key, ''):
                changed_colors[key] = desired
        backup_dir = Path(userdata) / 'backups' / state['backup_id']
        edits = []
        for rec in state['files']:
            path = _target(skin, rec['relative'])
            original = _read(backup_dir / rec['backup'], MAX_MEDIA)
            if digest(original) != rec['old_sha256']:
                raise BrandingError('Backup defekt: ' + rec['relative'])
            current = _read(path, MAX_MEDIA)
            if digest(current) == rec['old_sha256']:
                continue
            if digest(current) == rec['new_sha256']:
                output = original
            elif rec['type'] == 'xml':
                output = current
                for delta in rec['deltas']:
                    old, new = delta['old'].encode('ascii'), delta['new'].encode('ascii')
                    if output.count(new) != delta['count']:
                        raise BrandingError('XML-Konflikt bei ' + rec['relative'] + ': spätere Änderungen schützen.')
                    output = output.replace(new, old)
            else:
                raise BrandingError('Medien-Datei wurde nach Branding geändert: ' + rec['relative'])
            edits.append((path, current, output))
        done = []
        try:
            for path, current, output in edits:
                _atomic(path, output)
                done.append((path, current))
            for key in changed_colors:
                color_set(key, colors_before[key])
        except Exception:
            for key, desired in changed_colors.items():
                try:
                    if color_get(key) == colors_before[key]:
                        color_set(key, desired)
                except Exception:
                    pass
            for path, current in reversed(done):
                _atomic(path, current)
            raise
        state['state'] = 'restored'
        state['restored_at'] = datetime.now(timezone.utc).isoformat()
        _write_state(userdata, state)
        return {'files': len(edits)}


def preview(skin, addon, userdata, mode, color_get=None):
    details = status(skin, userdata, color_get)
    text = ["XCMate BINGIE Branding Manager v0.2.0 – Space Blue", "",
            "Status: {}".format(details['state']),
            "Skin: {} (nur BINGIE MOD 2.2.3)".format(skin),
            "Intro-Modus: {}".format(mode), "",
            "Enthalten: XCMate-intro.mp4, 7.04 s / H.264 1080p / AAC-Ton",
            "Logo: chromfarbenes XCMate-Asset aus dem freigegebenen Moodboard",
            "Splash: Bild aus dem Intro-Video (5.3 s)",
            "Space Blue: Deep #061322, Navy #0A2947, Blue #159FEA, Focus #42D9FF",
            "Farben: {} Kodi-Skin-Farbwerte (inklusive sichtbarer Namen)".format(len(names_for_settings())), "",
            "Änderungen (erst nach ausdrücklicher Bestätigung):"]
    if mode in MODE_VIDEOS:
        text += ['- ' + x for x in MODE_VIDEOS[mode]]
    text += ["- bingie_splash.png, bingie_splash2.png",
             "- genau ein Logo-Pfad in IncludesHomeBingie.xml",
             "- genau ein Logo-Pfad in Custom_1101_StartUp.xml und Custom_1102_StartUp2.xml",
             "- nur Start-Intro-Dauer in Custom_1103_StartUpMask.xml auf 8 Sekunden",
             "- colors/defaults.xml (benannte globale BINGIE-Farben)",
             "- BINGIE-Farbstrings: Menüs, Panels, Buttons, Info, Scroll, OSD und Fortschritt",
             "", "Unverändert: Fokus-Geometrie, Widget-Routen, SkinShortcuts, Kodi-Datenbanken, ",
             "XCMate-Konfiguration, Portal-/EPG-Daten, Fernbedienung und Player.", "",
             "Backup: userdata/addon_data/script.gsmedia.xcmate.branding/backups/<id>/",
             "Nicht Add-on-Daten löschen, solange das Branding aktiv ist.",
             "Skinupdate kann den Patch überschreiben und eine Wiederherstellung blockieren.",
             "Android-Geräteabnahme ausstehend."]
    return '\n'.join(text)
