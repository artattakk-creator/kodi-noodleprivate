"""Build or verify the standalone .99 Draft-PR ZIP and its SHA256 sidecar."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from xml.etree import ElementTree as ET

from package_xcmate71 import build, inspect_package as inspect_zip
from release_candidate98 import PUBLICATION_PATHS as PATHS98, baseline_frozen, frozen

ROOT = Path(__file__).resolve().parents[1]
ADDON = 'plugin.video.xtreammate'
VERSION = '0.1.29.99'
NAME = f'{ADDON}-{VERSION}.zip'
BASE = '81bd2ad0c9c5f2d49de47c693d363a686f886111'
REVIEW_DIRECTORY = Path('docs/XCMate/test-builds/02999')
PUBLICATION_PATHS = PATHS98 + (
    'docs/XCMate/test-builds/02998', '.release', 'src/repository.gsmedia',
    '.github/workflows',
)
PRIVATE_NAMES = {
    'favourites.xml', 'favorites.xml', 'portals.json', 'tmdb_read_access_token.txt',
}


def publication_changes():
    return baseline_frozen(BASE, PUBLICATION_PATHS) != frozen(PUBLICATION_PATHS)


def safe_output(output):
    path = Path(output)
    absolute = path if path.is_absolute() else Path.cwd()/path
    if any(parent.is_symlink() for parent in (absolute, *absolute.parents)):
        raise ValueError('RC99_OUTPUT_SYMLINK')
    path = absolute.resolve()
    if path == ROOT or path in ROOT.parents:
        raise ValueError('RC99_OUTPUT_MUST_NOT_BE_REPOSITORY_OR_PARENT')
    if ROOT in path.parents and path != ROOT/REVIEW_DIRECTORY:
        raise ValueError('RC99_OUTPUT_MUST_NOT_BE_LIVE_CHANNEL')
    for name in (NAME, NAME+'.sha256'):
        target = path/name
        if target.is_symlink():
            raise ValueError('RC99_OUTPUT_SYMLINK')
        if target.exists() and not target.is_file():
            raise ValueError('RC99_OUTPUT_NOT_REGULAR_FILE')
    return path


def source_hashes():
    relative_source = Path('src')/ADDON
    source = ROOT/relative_source
    if source.is_symlink() or source.parent.is_symlink():
        raise ValueError('RC99_UNSAFE_SOURCE')
    tracked = subprocess.check_output(['git', 'ls-files', '-z', '--', str(relative_source)], cwd=ROOT)
    tracked = set(os.fsdecode(tracked).rstrip('\0').split('\0'))
    actual = {}
    paths = set()
    for path in source.rglob('*'):
        rel = path.relative_to(source)
        if path.is_symlink():
            raise ValueError('RC99_UNSAFE_SOURCE')
        if '__pycache__' in rel.parts or path.name == '.DS_Store' or path.is_dir():
            continue
        lower = path.name.lower()
        private_settings = (
            (lower == 'settings.xml' and rel.as_posix() != 'resources/settings.xml')
            or (lower.lstrip('.').startswith(('settings96.', 'settings99.'))
                and lower.endswith(('.xml', '.json', '.lock', '.tmp')))
        )
        if not path.is_file() or lower in PRIVATE_NAMES or private_settings:
            raise ValueError('RC99_PRIVATE_OR_UNSAFE_SOURCE')
        paths.add(path.relative_to(ROOT).as_posix())
        actual[f'{ADDON}/{rel.as_posix()}'] = hashlib.sha256(path.read_bytes()).hexdigest()
    if paths != tracked:
        raise ValueError('RC99_SOURCE_INVENTORY')
    if subprocess.run(['git', 'diff', '--quiet', '--', str(relative_source)], cwd=ROOT).returncode:
        raise ValueError('RC99_SOURCE_NOT_STAGED')
    return actual


def inspect_package(path):
    return inspect_zip(path, source_hashes(), VERSION, 'RC99')


def require_review_scope():
    if subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, 'HEAD'], cwd=ROOT).returncode:
        raise ValueError('RC99_INCORRECT_BASE')
    if publication_changes():
        raise ValueError('RC99_LIVE_CHANNEL_CHANGED')


def verify_files(folder):
    proof = inspect_package(folder/NAME)
    if (folder/(NAME+'.sha256')).read_text(encoding='ascii').split() != [proof['sha256'], NAME]:
        raise ValueError('RC99_SHA256')
    return dict(proof, status='REVIEW_PACKAGE_ONLY', source_base=BASE,
                repository_released=False, merge_or_publish_authorized=False,
                android='ANDROID_NOT_TESTED')


def verify(output):
    folder = safe_output(output)
    require_review_scope()
    return verify_files(folder)


def stage(output):
    folder = safe_output(output)
    require_review_scope()
    source_hashes()
    source = ROOT/'src'/ADDON
    manifest = ET.parse(source/'addon.xml').getroot()
    if (manifest.get('id'), manifest.get('version')) != (ADDON, VERSION):
        raise ValueError('RC99_MANIFEST')
    folder.mkdir(parents=True, exist_ok=True)
    # Validate a complete, private staging copy before replacing either output.
    with tempfile.TemporaryDirectory(prefix='.xcmate99-', dir=folder) as temporary:
        temporary = Path(temporary)
        built = build(temporary, source=source)
        verified = verify_files(temporary)
        if any(built[key] != verified[key] for key in built):
            raise ValueError('RC99_BUILD_PROOF')
        safe_output(folder)
        for name in (NAME, NAME+'.sha256'):
            (temporary/name).replace(folder/name)
    return verify(folder)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stage', action='store_true')
    args = parser.parse_args()
    print(json.dumps(stage(args.output) if args.stage else verify(args.output), indent=2))
