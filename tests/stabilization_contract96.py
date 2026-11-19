"""Exact reviewed .96 delta; unknown bytes never bypass historical guards.

Refresh only after the .96 runtime has finished changing:
  PYTHONPATH=tests python tests/stabilization_contract96.py --refresh
The refresh command records a review fixture; it does not publish a package.
"""
import argparse
import hashlib
import io
import json
from functools import lru_cache
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
# Source .95 was never published to main; its pilot ZIP was published alone.
BASE = 'c230fed998f4f2db0d9035068460cf26433e7ac4'
FIXTURE = Path(__file__).parent/'fixtures/stabilization_02996_delta.json'
PREFIX = 'src/plugin.video.xtreammate/'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


@lru_cache(maxsize=1)
def delta96():
    return json.loads(FIXTURE.read_text(encoding='utf-8'))


def without96(source, module):
    from stabilization_contract99 import without99
    source = without99(source, module)
    binary = isinstance(source, bytes)
    raw = source if binary else source.encode()
    name = str(module)
    for path, change in delta96()['modules'].items():
        if name not in (path, Path(path).name, Path(path).stem):
            continue
        if sha(raw) == change['new_sha256']:
            before = change['old'].encode()
            if sha(before) != change['old_sha256']:
                raise ValueError('CORRUPT_96_REVIEW_FIXTURE')
            return before if binary else before.decode()
    return source


def runtime_without96(source):
    """Remove only hash-proven additions, then undo exact reviewed edits."""
    from stabilization_contract99 import runtime_without99
    source = runtime_without99(source)
    additions = delta96()['added']
    for name, digest in additions.items():
        if name not in source or sha(source[name]) != digest:
            raise ValueError('UNREVIEWED96_ADDED_BYTES: '+name)
    return {name: without96(raw, name) for name, raw in source.items() if name not in additions}


def baseline_runtime():
    raw = subprocess.check_output(['git', 'archive', BASE, PREFIX], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        return {member.name: archive.extractfile(member).read()
                for member in archive if member.isfile()}


def refresh():
    """Record current exact bytes against the fixed .95/current-main base."""
    original = baseline_runtime()
    source = {PREFIX+p.relative_to(ROOT/PREFIX).as_posix(): p.read_bytes()
              for p in (ROOT/PREFIX).rglob('*')
              if p.is_file() and '__pycache__' not in p.parts and p.name != '.DS_Store'}
    if set(original)-set(source):
        raise ValueError('REMOVED96_RUNTIME_FILES')
    delta = dict(base=BASE, modules={}, added={})
    for name, raw in sorted(source.items()):
        if name not in original:
            delta['added'][name] = sha(raw)
        elif raw != original[name]:
            delta['modules'][name] = dict(old=original[name].decode(), old_sha256=sha(original[name]), new_sha256=sha(raw))
    FIXTURE.write_text(json.dumps(delta, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    delta96.cache_clear()
    return dict(base=BASE, modules=len(delta['modules']), added=len(delta['added']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true', required=True)
    parser.parse_args()
    print(json.dumps(refresh(), sort_keys=True))
