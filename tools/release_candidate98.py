"""Build/verify the .98 review ZIP and proof; never stage a live-channel overlay."""
import argparse
from functools import lru_cache
import hashlib
import fnmatch
import io
import os
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ADDON = 'plugin.video.xtreammate'
VERSION = '0.1.29.98'
NAME = ADDON+'-'+VERSION+'.zip'
BASE = 'eb6c0857e4cb3abf20ffb94a0ed31e48b7daf59a'
SOURCE_COMMIT = 'c5ecd2ea69bb84e648cae9433d250613dceff46e'
PUBLICATION_PATHS = ('addons.xml', 'addons.xml.md5', 'index.html',
    'online-test', 'plugin.video.xtreammate', 'plugin.video.noodleprivate',
    'repository-programme', 'repository.gsmedia', 'script.gsmedia.setup',
    'src/script.gsmedia.setup', 'script.gsmedia.xcmate.branding', 'testversionen',
    'artwork', 'themes', 'language_packs', 'integrations')
PUBLICATION_PATHS += ('docs/XCMate/test-builds/02996', 'docs/XCMate/test-builds/issue482')
PUBLICATION_ROOT_GLOBS = ('repository.gsmedia-*.zip',)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


@lru_cache(maxsize=1)
def source98():
    """Read the original .98 source from its immutable Git tree."""
    source = 'src/'+ADDON
    raw = subprocess.check_output(['git', 'archive', SOURCE_COMMIT, '--', source], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        return {member.name.removeprefix('src/'): archive.extractfile(member).read()
                for member in archive if member.isfile() and '__pycache__' not in Path(member.name).parts
                and Path(member.name).name != '.DS_Store'}


def inspect_package(path):
    from package_xcmate71 import inspect_package as inspect_zip
    expected = {name: sha(raw) for name, raw in source98().items()}
    return inspect_zip(path, expected, VERSION, 'RC98')


def build_historical(output):
    from package_xcmate71 import build
    with tempfile.TemporaryDirectory(prefix='xcmate98-source-') as folder:
        for name, raw in source98().items():
            target = Path(folder)/name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        return build(output, source=Path(folder)/ADDON)


def historical_input(name, raw):
    # The complete-suite runner materializes removed pre-.90 test inputs in
    # a disposable clone. Ignore only their immutable verified bytes there;
    # changed/unapproved files still fail the full publication comparison.
    if not os.environ.get('XCMATE94_REVIEW_ROOT'):return False
    from run_host94_contract import manifest, read_archived
    if name not in manifest(ROOT):return False
    return read_archived(ROOT, name) == raw


def frozen(paths=PUBLICATION_PATHS):
    result = {}
    for name in paths:
        root = ROOT/name
        if root.is_file():
            result[name] = sha(root.read_bytes())
        elif root.is_dir():
            for path in root.rglob('*'):
                if path.is_file():
                    name=path.relative_to(ROOT).as_posix();raw=path.read_bytes()
                    if not historical_input(name,raw):result[name]=sha(raw)
    for pattern in PUBLICATION_ROOT_GLOBS:
        for path in ROOT.glob(pattern):
            if path.is_file():result[path.relative_to(ROOT).as_posix()] = sha(path.read_bytes())
    return result


def baseline_frozen(base=BASE, paths=PUBLICATION_PATHS):
    # Some protected namespaces do not exist in this baseline; a later
    # untracked addition there still appears in frozen() and fails equality.
    selected = subprocess.check_output(['git', 'ls-tree', '--name-only', base, '--', *paths], cwd=ROOT).decode().splitlines()
    roots = subprocess.check_output(['git', 'ls-tree', '--name-only', base], cwd=ROOT).decode().splitlines()
    selected += [name for name in roots if any(fnmatch.fnmatch(name, pattern) for pattern in PUBLICATION_ROOT_GLOBS)]
    raw = subprocess.check_output(['git', 'archive', base, '--', *selected], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        return {member.name: sha(archive.extractfile(member).read())
                for member in archive if member.isfile()}


def safe_output(output):
    output = Path(output).resolve()
    try:
        relative = output.relative_to(ROOT)
    except ValueError:
        if output in ROOT.resolve().parents:
            raise ValueError('RC98_OUTPUT_MUST_NOT_BE_REPOSITORY_PARENT')
    else:
        if relative.parts[:4] != ('docs', 'XCMate', 'test-builds', '02998'):
            raise ValueError('RC98_OUTPUT_MUST_NOT_BE_LIVE_CHANNEL')
    for name in (NAME, NAME+'.sha256', 'review-plan98.json'):
        if (output/name).is_symlink():
            raise ValueError('RC98_OUTPUT_SYMLINK')
    return output


def stage(output):
    """Write only canonical ZIP, SHA256 sidecar and review plan."""
    output = safe_output(output)
    before = frozen()
    if before != baseline_frozen():
        raise ValueError('RC98_LIVE_CHANNEL_CHANGED')
    proof = build_historical(output)
    if proof != inspect_package(output/NAME):
        raise ValueError('RC98_BUILD_PROOF')
    plan = dict(version=VERSION, status='REVIEW_PACKAGE_ONLY', source_base=BASE,
        source_merged=False, repository_released=False, repository_staged='NONE',
        merge_or_publish_authorized=False, android_status='ANDROID_NOT_TESTED',
        live_baseline_sha256=before, package=proof)
    (output/'review-plan98.json').write_text(json.dumps(plan, indent=2, sort_keys=True)+'\n')
    if frozen() != before:
        raise ValueError('RC98_LIVE_CHANNEL_CHANGED')
    return verify(output)


def verify(output):
    output = safe_output(output)
    proof = inspect_package(output/NAME)
    if (output/(NAME+'.sha256')).read_text().split() != [proof['sha256'], NAME]:
        raise ValueError('RC98_SHA256')
    plan = json.loads((output/'review-plan98.json').read_text())
    expected = dict(version=VERSION, status='REVIEW_PACKAGE_ONLY', source_base=BASE,
        source_merged=False, repository_released=False, repository_staged='NONE',
        merge_or_publish_authorized=False, android_status='ANDROID_NOT_TESTED',
        live_baseline_sha256=baseline_frozen(), package=proof)
    if plan != expected or plan['live_baseline_sha256'] != frozen():
        raise ValueError('RC98_PLAN_OR_BASELINE_CHANGED')
    return dict(proof, status='REVIEW_PACKAGE_ONLY', source_base=BASE,
                repository_staged='NONE', repository_released=False,
                merge_or_publish_authorized=False, android='ANDROID_NOT_TESTED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stage', action='store_true')
    args = parser.parse_args()
    print(json.dumps(stage(args.output) if args.stage else verify(args.output), indent=2))
