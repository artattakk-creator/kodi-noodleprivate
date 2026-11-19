"""The single Artwork & Cache dialog; durable choices use existing settings.

Cleanup is limited to expired, unpinned, indexed XCMate temporary images.
No archive, manual choices, Kodi textures, databases, WAL or backups qualify.
"""
import hashlib
import json
import os
import re
import time
from pathlib import Path
MIB = 1024 * 1024


def check_dynamic(folder, upcoming):
    from art_storage82 import capacity
    from art_storage import ArtworkFailure, WRITE_HEADROOM
    facts = capacity(str(folder));free = facts.get('free')
    if facts.get('capacity82') != 'SAME_VOLUME_VERIFIED' or type(free) is not int:
        raise ArtworkFailure('CACHE_ERROR', 'CAPACITY_UNKNOWN', facts)
    facts = dict(facts, reserve=32*MIB)
    if free < facts['reserve'] + max(0, upcoming) + WRITE_HEADROOM:
        raise ArtworkFailure('DISK_FULL', 'BLOCKED_REAL_DISK', facts)
    return facts


def _plan():
    from artwork_temp85 import cache, active, durable
    c = cache();rows = []
    if c.checked():
        for digest, record in c.index().items():
            if not isinstance(record, dict) or not isinstance(record.get('pins', {}), dict):raise OSError('CACHE_INDEX_INVALID')
            if durable(record) or record.get('until', 0) > time.time() or any(v > time.time() for v in record['pins'].values()) or active(digest):continue
            name = record.get('file', '')
            if not re.fullmatch('[a-f0-9]{64}', digest) or not re.fullmatch(digest+r'\.(png|jpg)', name):continue
            file = c.root/name
            if file.is_symlink() or not file.is_file():continue
            stat = file.stat()
            if stat.st_size != record.get('size') or not 0 < stat.st_size <= 3*MIB:continue
            rows.append(dict(key=digest, name=name, size=stat.st_size, stamp=[stat.st_dev, stat.st_ino, stat.st_mtime_ns]))
    return c, rows


def cleanup_preview():
    c, rows = _plan()
    signature = hashlib.sha256(json.dumps([str(c.root), rows], sort_keys=True).encode()).hexdigest()
    return dict(files=len(rows), bytes=sum(r['size'] for r in rows), signature=signature)


def cleanup(preview, *, confirmed=False):
    if confirmed is not True:raise ValueError('CACHE_CONFIRMATION_REQUIRED')
    from profile_transaction import writing
    with writing(timeout=.2):
        current = cleanup_preview()
        if current != preview:raise OSError('CACHE_PREVIEW_CHANGED')
        c, rows = _plan();entries = c.index()
        # No names or target paths are accepted from the caller's preview.
        for row in rows:
            (c.root/row['name']).unlink();entries.pop(row['key'], None)
            __import__('artwork_temp85').presence(row['key'], False)
        if rows:c.atomic(c.root/'index.json', json.dumps(dict(format=1, entries=entries), separators=(',', ':')).encode())
        return current


def status():
    from artwork_config import read
    from programme_art46 import limit, image_root87
    from art_storage82 import capacity
    from artwork_temp85 import cache
    from logo_overrides96 import root as logos_root
    config = read();folder = Path(image_root87());c = cache();classes = []
    programme_online = True
    try:__import__('android_artwork87').check_active(write=False)
    except OSError:programme_online = False
    for role, target, maximum in [('PROGRAMME_CACHE',folder,limit()),
                                   ('TEMPORARY_CACHE',c.root,limit()),
                                   ('PERSISTENT_LOGOS',logos_root(),16*MIB)]:
        used = 0
        if target.is_dir() and not target.is_symlink():
            for p in target.iterdir():
                if not p.is_symlink() and p.is_file() and p.suffix.lower() in ('.png','.jpg'):used += p.stat().st_size
        # A removed active external mount must not report ancestor/internal free.
        facts = capacity(str(target)) if role!='PROGRAMME_CACHE' or programme_online else {}
        total = facts.get('total');free = facts.get('free')
        reserve = 32*MIB
        if role == 'PERSISTENT_LOGOS':
            reserve = max(64*MIB,min(128*MIB,int(total*.02))) if type(total) is int else 128*MIB
        elif config['mode']!='dynamic':
            reserve = __import__('art_storage').capacity(location=str(target))['reserve'] if programme_online else 1024*MIB
        safe = type(free) is int and facts.get('capacity82')=='SAME_VOLUME_VERIFIED' and free>=reserve+256*1024
        classes.append(dict(role=role,used_mib=round(used/MIB,2),budget_mib=maximum//MIB,
            free_mib=round(free/MIB,2) if type(free) is int else None,
            free_bytes=free if type(free) is int else None, used_bytes=used, budget_bytes=maximum,
            volume=facts.get('volume82'), mount=facts.get('mount82'),
            write_reserve_mib=reserve//MIB,capacity=facts.get('capacity82','UNKNOWN'),
            state='AVAILABLE' if safe else 'RAM_OR_LINK_ONLY' if role!='PERSISTENT_LOGOS' else 'WRITE_BLOCKED',
            rolling=role!='PERSISTENT_LOGOS'))
    return dict(mode=config['mode'],classes=classes,display='URL/RAM möglich; Archiv ist optional')


def cleanup_dialog():
    import xbmcgui
    from artwork_ui import job
    preview = job(lambda cancel, progress:cleanup_preview())
    if preview and xbmcgui.Dialog().yesno('Artwork & Cache', str(preview['files'])+' Dateien · '+str(preview['bytes'])+' Bytes\nNur abgelaufene temporäre XCMate-Bilder löschen?'):
        return job(lambda cancel, progress:cleanup(preview, confirmed=True))


def manage():
    import xbmcgui
    from artwork_ui import job
    dialog = xbmcgui.Dialog()
    labels = ['Verbrauch, Budget und freier Zielplatz', 'Cache-Budget: 32 / 64 / 128 / 256 MiB',
              'Speicherart und Ziel: dynamisch / intern / extern', 'Entbehrliche temporäre Bilder bereinigen']
    while True:
        choice = __import__('menu_icons45').select(dialog, 'Artwork & Cache', labels)
        if choice < 0:return
        try:
            if choice == 0:
                value = job(lambda cancel, progress:status())
                if value:
                    names={'PROGRAMME_CACHE':'Sendungsbilder (Cache)','TEMPORARY_CACHE':'Temporäre Bilder','PERSISTENT_LOGOS':'Dauerhafte Senderlogos (kein Cache)'}
                    lines=['Speicherart: '+value['mode'],value['display']]
                    for row in value['classes']:
                        lines.extend(['',names[row['role']],
                            'Belegt: '+str(row['used_mib'])+' MiB · Budget: '+str(row['budget_mib'])+' MiB',
                            'Zielvolume: '+str(row['volume'] or 'unbekannt')+' · '+str(row['mount'] or 'unbekannt'),
                            'Freier Zielplatz: '+(str(row['free_bytes'])+' Bytes · '+str(row['free_mib'])+' MiB' if row['free_bytes'] is not None else 'unbekannt'),
                            'Reale Schreibreserve: '+str(row['write_reserve_mib'])+' MiB',
                            'Schreiben möglich' if row['state']=='AVAILABLE' else 'Schreiben blockiert · URL/RAM möglich' if row['rolling'] else 'Dauerhafte Logos derzeit nur lesbar'])
                    dialog.textviewer('Artwork & Cache','\n'.join(lines))
            elif choice == 1:
                index = __import__('menu_icons45').select(dialog, 'Cache-Budget (MiB)', ['32','64','128','256'])
                if index in (0,1,2,3):
                    job(lambda cancel, progress:__import__('settings_guard96').write({'programme_art_budget46':str(index)}))
            elif choice == 2:__import__('artwork_ui').manage_archive()
            elif choice == 3:
                cleanup_dialog()
        except (OSError, ValueError, TimeoutError):dialog.ok('Artwork & Cache', 'Speichervorgang blockiert. Es wurden keine Datenbanken oder Kodi-Texturen bereinigt.')
