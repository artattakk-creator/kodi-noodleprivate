#!/usr/bin/env python3
"""Read-only verification of the published XCMate package and Kodi index."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import zipfile
import xml.etree.ElementTree as ET


def verify(repo, target='0.1.29.2'):
    repo=Path(repo); filename='plugin.video.xtreammate-'+target+'.zip'
    path=repo/'plugin.video.xtreammate'/filename
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    expected=path.with_suffix('.zip.sha256').read_text().split()[0]
    if digest != expected: raise ValueError('SHA-256 mismatch')
    index=(repo/'addons.xml').read_bytes()
    if hashlib.md5(index).hexdigest() != (repo/'addons.xml.md5').read_text().strip(): raise ValueError('Index MD5 mismatch')
    entry=ET.fromstring(index).find("addon[@id='plugin.video.xtreammate']")
    if entry is None or entry.get('version') != target: raise ValueError('Index version mismatch')
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None: raise ValueError('CRC failure')
        names=archive.namelist()
        if len(names)!=len(set(names)): raise ValueError('Duplicate path')
        for item in archive.infolist():
            name=PurePosixPath(item.filename)
            if name.is_absolute() or '..' in name.parts or '\\' in item.filename: raise ValueError('Unsafe path')
            if not item.filename.startswith('plugin.video.xtreammate/'): raise ValueError('Wrong addon root')
            if stat.S_ISLNK(item.external_attr >> 16): raise ValueError('Symlink')
            if set(name.parts)&{'addon_data','__pycache__','.git','tests'}: raise ValueError('Profile/build content')
            if name.suffix.lower() in ('.db','.sqlite','.sqlite3','.log','.pyc','.pyo') or name.name.endswith(('-wal','-shm')):
                raise ValueError('Private database/log content')
            if name.name in ('portals.json','settings.xml','appearance_v1.json','xtreammate_groups.json','favourites.json'):
                # Bundled Kodi settings schema is permitted, user settings.xml is not.
                if item.filename != 'plugin.video.xtreammate/resources/settings.xml': raise ValueError('User configuration')
        addon=ET.fromstring(archive.read('plugin.video.xtreammate/addon.xml'))
        if addon.get('id')!='plugin.video.xtreammate' or addon.get('version')!=target: raise ValueError('Manifest mismatch')
        for asset in addon.findall('.//assets/*'):
            if asset.tag in ('icon','fanart','screenshot') and 'plugin.video.xtreammate/'+asset.text not in names:
                raise ValueError('Missing metadata image')
    old=repo/'plugin.video.xtreammate/plugin.video.xtreammate-0.1.28.zip'
    with zipfile.ZipFile(old) as archive:
        previous=ET.fromstring(archive.read('plugin.video.xtreammate/addon.xml'))
    if previous.get('id')!=addon.get('id'): raise ValueError('Addon identity changed')
    return dict(status='PASS', version=target, sha256=digest, bytes=path.stat().st_size,
                files=len(names), crc='PASS', index_version='PASS', index_md5='PASS',
                private_profile_files='ABSENT', upgrade_same_id=True,
                android_acceptance='NOT_RUN', credentials_audit='No profile/DB/log payloads; not a runtime account audit')


if __name__=='__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
