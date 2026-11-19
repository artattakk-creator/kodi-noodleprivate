"""Pilot-only 0.1.29.97 builder/publisher, pinned to vetted issue #474 source."""
import argparse
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

VERSION = '0.1.29.97'
ADDON = 'plugin.video.xtreammate'
NAME = ADDON + '-' + VERSION + '.zip'
VERIFIED96 = '64d08c78581d074a9c86fee26ba94011119c1ab0f297de6a0bc9afee13cf1ba9'
PILOT96 = '249d7908d83cf7808d950e938e572fc046c2b0fc767aeebd3195b18b87b9d740'
SOURCE_COMMIT = 'bc06f521d23ee5c1e6c9aaca456c2b3cc062f3fc'
SOURCE_ROOT = Path(__file__).resolve().parents[1]
SOURCE96 = SOURCE_ROOT / 'docs/XCMate/test-builds/02996/plugin.video.xtreammate-0.1.29.96.zip'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inspect(filename):
    data = filename.read_bytes()
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = archive.namelist()
        assert len(names) == 899 and len(set(names)) == len(names), 'ZIP_FILE_SET'
        assert archive.testzip() is None, 'ZIP_BAD_CRC'
        assert not any(x.startswith('/') or '..' in x.split('/') or x.endswith(('.sqlite', '.log', '.pyc', '.db')) for x in names), 'ZIP_UNSAFE_MEMBER'
        node = ET.fromstring(archive.read(ADDON + '/addon.xml'))
        assert (node.get('id'), node.get('version')) == (ADDON, VERSION), 'ZIP_VERSION'
    return dict(version=VERSION, sha256=digest(data), bytes=len(data), files=len(names), crc='PASS')


def build(target):
    from package_xcmate71 import build as package_build
    old = SOURCE96.read_bytes()
    assert digest(old) == VERIFIED96, 'SOURCE96_PROVENANCE_FAILED'
    src_xml = (SOURCE_ROOT / 'src' / ADDON / 'addon.xml').read_bytes()
    assert ET.fromstring(src_xml).get('version') == VERSION, 'SOURCE_VERSION'
    target.mkdir(parents=True, exist_ok=True)
    proof = package_build(target)
    zipfile97 = target / NAME
    observed = inspect(zipfile97)
    assert proof == dict(observed, source_bytes='PASS'), 'PACKAGE_PROOF_FAILED'
    with zipfile.ZipFile(io.BytesIO(old)) as before, zipfile.ZipFile(zipfile97) as after:
        assert before.testzip() is None
        oldnames, newnames = set(before.namelist()), set(after.namelist())
        assert oldnames == newnames and len(oldnames) == 899, 'SOURCE_FILE_SET_CHANGED'
        changed = [n for n in oldnames if before.read(n) != after.read(n)]
        assert changed == [ADDON + '/addon.xml'], ('UNAPPROVED_SOURCE_CHANGE', changed[:10])
        assert after.read(ADDON + '/addon.xml') == src_xml, 'XML_SOURCE_BYTE_DIFFERENCE'
    assert (target / (NAME + '.sha256')).read_text().split() == [observed['sha256'], NAME], 'SHA256_SIDECAR'
    (target / 'proof.json').write_text(json.dumps(observed, indent=2, sort_keys=True) + '\n')
    print('XCMATE97_VERSIONED_ZIP_PR478_SOURCE_PRESERVED PASS', json.dumps(observed))


def stage(root, source):
    root = root.resolve()
    pilot = root / 'online-test'
    archive = source / NAME
    proof = inspect(archive)
    assert (source / (NAME + '.sha256')).read_text().split() == [proof['sha256'], NAME], 'SOURCE_SHA'
    assert json.loads((source / 'proof.json').read_text()) == proof, 'SOURCE_PROOF'
    oldside = (pilot / ADDON / (ADDON + '-0.1.29.96.zip.sha256')).read_text().split()[0]
    assert oldside == PILOT96, 'PILOT_PREVIOUS_SHA_CHANGED'
    rootxml = (root / 'addons.xml').read_text()
    assert ET.fromstring(rootxml).find("./addon[@id='plugin.video.xtreammate']").get('version') == '0.1.29.91', 'REGULAR_VERSION_CHANGED'
    assert ET.parse(root / 'src' / ADDON / 'addon.xml').getroot().get('version') == '0.1.29.92', 'MAIN_SOURCE_CHANGED'
    catalog = pilot / 'addons.xml'
    raw = catalog.read_text()
    assert (pilot / 'addons.xml.md5').read_text().strip() == hashlib.md5(raw.encode()).hexdigest(), 'PREVIOUS_PILOT_MD5_INVALID'
    begin = raw.index('<addon id="plugin.video.xtreammate"')
    end = raw.index('</addon>', begin) + len('</addon>')
    assert ET.fromstring(raw[begin:end]).get('version') == '0.1.29.96', 'PREVIOUS_PILOT_VERSION_CHANGED'
    with zipfile.ZipFile(archive) as zipreader:
        newaddon = zipreader.read(ADDON + '/addon.xml').decode()
    newpart = re.sub(r'^<\?xml[^>]*\?>\s*', '', newaddon).strip()
    replacement = raw[:begin] + newpart + raw[end:]
    check = ET.fromstring(replacement)
    entries = [x for x in check.findall('addon') if x.get('id') == ADDON]
    assert len(entries) == 1 and entries[0].get('version') == VERSION, 'CATALOG_VERSION'
    catalog.write_text(replacement)
    (pilot / 'addons.xml.md5').write_text(hashlib.md5(replacement.encode()).hexdigest() + '\n')
    manifest = pilot / 'manifest.json'
    value = json.loads(manifest.read_text())
    assert value.get('xcmate96', {}).get('sha256') == PILOT96, 'PILOT_MANIFEST96_CHANGED'
    assert 'xcmate97' not in value, 'PILOT_VERSION_ALREADY_EXISTS'
    value['xcmate97'] = dict(
        addon_id=ADDON, version=VERSION, source_pr=478, source_commit=SOURCE_COMMIT,
        sha256=proof['sha256'], bytes=proof['bytes'], files=proof['files'],
        channels=['pilot'], android_status='ANDROID_NOT_TESTED', user_approved_pilot_release=True,
        user_approved_regular_release=False, regular_channel_unchanged=True,
        neodark3_direct_unchanged=True, installer_version_unchanged='0.5.26',
        status='PILOT_ONLY_HOST_NATIVE_PASS_ANDROID_NOT_TESTED',
        pilot_zip='online-test/' + ADDON + '/' + NAME)
    manifest.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    landing = pilot / 'index.html'
    html = landing.read_text()
    a = html.index('<p><strong>Pilot-Update:</strong>')
    b = html.index('</p>', a) + len('</p>')
    html = html[:a] + ('<p><strong>Pilot-Update:</strong> XCMate 0.1.29.97 wird nur ueber das '
        'GS Media Pilot-Repository 1.9.12 zur Android-Abnahme der manuellen EPG-Zuordnung (#474/#478) '
        'bereitgestellt. Native Kodi-Linux-Tests und ZIP-Integritaet geprueft; Android-Gerätetest offen. '
        'Regulaer und NeoDark3-Direkt-ZIP bleiben auf 0.1.29.91.</p>') + html[b:]
    landing.write_text(html)
    destination = pilot / ADDON / NAME
    assert not destination.exists(), 'PILOT_TARGET_EXISTS'
    shutil.copyfile(archive, destination)
    (pilot / ADDON / (NAME + '.sha256')).write_text(proof['sha256'] + '  ' + NAME + '\n')
    allowed = {
        'online-test/addons.xml', 'online-test/addons.xml.md5',
        'online-test/manifest.json', 'online-test/index.html',
        'online-test/' + ADDON + '/' + NAME,
        'online-test/' + ADDON + '/' + NAME + '.sha256'}
    changes = subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain', '--untracked-files=all'], text=True)
    found = {line[3:] for line in changes.splitlines()}
    assert found == allowed, ('UNAPPROVED_PILOT_FILE_DIFF', sorted(found ^ allowed))
    assert hashlib.sha256(destination.read_bytes()).hexdigest() == proof['sha256'], 'PILOT_COPY_SHA'
    assert hashlib.md5(catalog.read_bytes()).hexdigest() == (pilot / 'addons.xml.md5').read_text().strip()
    print('XCMATE97_PILOT_SIX_FILES_SCOPE_AND_SHA_PASS', proof['sha256'])


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('mode', choices=['build', 'stage'])
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--root', type=Path)
    args = p.parse_args()
    if args.mode == 'build':
        build(args.out)
    else:
        if args.root is None:
            p.error('--root is required for stage')
        stage(args.root, args.out)
