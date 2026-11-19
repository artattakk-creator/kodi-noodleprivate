"""Build/verify an offline Pilot proposal; never modify a live repository."""
import argparse
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path
import xml.etree.ElementTree as E

ROOT = Path(__file__).resolve().parents[1]
ADDON = 'plugin.video.xtreammate'
VERSION = '0.1.29.93'
NAME = ADDON+'-'+VERSION+'.zip'
BASE = '3e1d6f87787baa95d24cc4e7c83c24914db31364'
FROZEN = ('addons.xml', 'addons.xml.md5', 'index.html',
          'online-test/addons.xml', 'online-test/addons.xml.md5',
          'online-test/manifest.json', 'online-test/index.html')

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def inspect_package(path):
    """Every member must equal the current source; reject extras and traversal."""
    raw = Path(path).read_bytes()
    source = ROOT/'src'/ADDON
    expected={ADDON+'/'+p.relative_to(source).as_posix():sha(p.read_bytes()) for p in source.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='.DS_Store'}
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(expected):
            raise ValueError('RC93_FILE_SET')
        if archive.testzip() is not None:
            raise ValueError('RC93_CRC')
        for name in names:
            if (Path(name).is_absolute() or '..' in Path(name).parts
                    or name.endswith(('.db', '.sqlite', '.log', '.pyc', '.pyo'))):
                raise ValueError('RC93_PRIVATE_OR_UNSAFE_MEMBER')
            if sha(archive.read(name)) != expected[name]:
                raise ValueError('RC93_SOURCE_BYTES')
        manifest = archive.read(ADDON+'/addon.xml')
        node = E.fromstring(manifest)
        if (node.get('id'), node.get('version')) != (ADDON, VERSION):
            raise ValueError('RC93_MANIFEST')
    return dict(version=VERSION, sha256=sha(raw), bytes=len(raw),
                files=len(names), crc='PASS', source_bytes='PASS')

def index_with_candidate(before, manifest):
    block = re.sub(r'^\s*<\?xml[^>]*\?>\s*', '', manifest.decode()).strip()
    text, count = re.subn(
        r'<addon\b(?=[^>]*\bid="plugin\.video\.xtreammate")[^>]*>.*?</addon>',
        lambda _: block, before.decode(), flags=re.S)
    if count != 1:
        raise ValueError('RC93_INDEX_AMBIGUOUS')
    old = {n.get('id'): E.tostring(n).strip() for n in E.fromstring(before)}
    new = {n.get('id'): E.tostring(n).strip() for n in E.fromstring(text)}
    if old.keys() != new.keys() or any(old[k] != new[k] for k in old if k != ADDON):
        raise ValueError('RC93_FOREIGN_INDEX_CHANGED')
    return text.encode()

def proposal_files(package):
    proof = inspect_package(package)
    raw = Path(package).read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        manifest = z.read(ADDON+'/addon.xml')
    index = index_with_candidate((ROOT/'online-test/addons.xml').read_bytes(), manifest)
    metadata = json.loads((ROOT/'online-test/manifest.json').read_text())
    metadata['zip_sha256'][ADDON] = proof['sha256']
    metadata['xcmate93'] = dict(proof, status='RELEASE_CANDIDATE',
        android_status='ANDROID_NOT_TESTED', authorization_issue=454,
        source_base=BASE, repository_released=False,
        installer_version_unchanged='0.5.26')
    # Only the nested Pilot package is proposed. No NeoDark3 or regular change.
    return {
        'online-test/addons.xml': index,
        'online-test/addons.xml.md5': (hashlib.md5(index).hexdigest()+'\n').encode(),
        'online-test/manifest.json': (json.dumps(metadata, indent=2, sort_keys=True)+'\n').encode(),
        'online-test/'+ADDON+'/'+NAME: raw,
        'online-test/'+ADDON+'/'+NAME+'.sha256': (proof['sha256']+'  '+NAME+'\n').encode(),
    }

def frozen():
    return {name: sha((ROOT/name).read_bytes()) for name in FROZEN}

def safe_output(output):
    output = Path(output).resolve()
    try:
        relative = output.relative_to(ROOT)
    except ValueError:
        return output  # Disposable external workspace, e.g. /tmp or RUNNER_TEMP.
    if relative.parts[:4] != ('docs', 'XCMate', 'test-builds', '02993'):
        raise ValueError('RC93_OUTPUT_MUST_NOT_BE_LIVE_CHANNEL')
    return output

def stage(output):
    """Write a review-only changed-file overlay, not an online repository."""
    from package_xcmate71 import build
    output = safe_output(output)
    before = frozen()
    proof = build(output)
    package = output/NAME
    if proof != inspect_package(package):
        raise ValueError('RC93_BUILD_PROOF')
    for name, raw in proposal_files(package).items():
        dest = output/'pilot-proposal'/name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
    plan = dict(version=VERSION, channel='PILOT_ONLY',
        status='REPOSITORY_STAGED_OFFLINE', source_base=BASE,
        source_merged=False, version_bump=True, zip_verified=True,
        repository_released=False, android_status='ANDROID_NOT_TESTED',
        merge_or_publish_authorized=False, live_baseline_sha256=before,
        proposed_sha256={p: sha(v) for p, v in proposal_files(package).items()},
        package=proof)
    (output/'pilot-plan.json').write_text(json.dumps(plan, indent=2, sort_keys=True)+'\n')
    if frozen() != before:
        raise ValueError('RC93_LIVE_CHANNEL_CHANGED')
    return verify(output)

def verify(output):
    output = safe_output(output)
    proof = inspect_package(output/NAME)
    if (output/(NAME+'.sha256')).read_text().split() != [proof['sha256'], NAME]:
        raise ValueError('RC93_SHA256')
    plan = json.loads((output/'pilot-plan.json').read_text())
    expected = proposal_files(output/NAME)
    files = {p.relative_to(output/'pilot-proposal').as_posix(): p.read_bytes()
             for p in (output/'pilot-proposal').rglob('*') if p.is_file()}
    if files != expected:
        raise ValueError('RC93_PROPOSAL_BYTES')
    if (plan['live_baseline_sha256'] != frozen()
            or plan['proposed_sha256'] != {p: sha(v) for p, v in expected.items()}
            or plan['package'] != proof or plan['repository_released'] is not False
            or plan['merge_or_publish_authorized'] is not False
            or plan['android_status'] != 'ANDROID_NOT_TESTED'):
        raise ValueError('RC93_PLAN_OR_BASELINE_CHANGED')
    node = next(n for n in E.fromstring(files['online-test/addons.xml']) if n.get('id') == ADDON)
    if node.get('version') != VERSION or tuple(map(int, VERSION.split('.'))) <= (0, 1, 29, 90):
        raise ValueError('RC93_NOT_AN_UPDATE')
    return dict(proof, status='RC_READY_FOR_ANDROID', repository_staged='OFFLINE_PILOT_ONLY',
                repository_released=False, android='ANDROID_NOT_TESTED')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stage', action='store_true')
    args = parser.parse_args()
    print(json.dumps(stage(args.output) if args.stage else verify(args.output), indent=2))
