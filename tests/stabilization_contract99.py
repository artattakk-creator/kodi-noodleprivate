"""Exact .99 source delta, preserving the historical .98-and-earlier contracts."""
import argparse
from difflib import SequenceMatcher
from functools import lru_cache
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'src/plugin.video.xtreammate'
FIXTURE = Path(__file__).parent / 'fixtures/stabilization_02999_delta.json'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


@lru_cache(maxsize=1)
def delta99():
    return json.loads(FIXTURE.read_text(encoding='utf-8'))


def without99(source, module):
    from stabilization_contract100 import without100
    source = without100(source, module)
    binary = isinstance(source, bytes)
    raw = source if binary else source.encode('utf-8')
    for name, change in delta99()['changed'].items():
        path = Path(name)
        if str(module) not in (name, path.name, path.stem) or digest(raw) != change['new_sha256']:
            continue
        lines = raw.decode('utf-8').splitlines(keepends=True)
        for start, stop, replacement in reversed(change['undo_edits']):
            lines[start:stop] = replacement
        before = ''.join(lines)
        if digest(before.encode('utf-8')) != change['old_sha256']:
            raise ValueError('CORRUPT_99_REVIEW_FIXTURE')
        return before.encode('utf-8') if binary else before
    return source


def runtime_without99(source):
    from stabilization_contract100 import runtime_without100
    source = runtime_without100(source)
    added = delta99()['added']
    for name in source.keys() & added.keys():
        if digest(source[name]) != added[name]:
            raise ValueError('UNREVIEWED99_ADDED_BYTES: '+name)
    return {name: without99(raw, name) for name, raw in source.items() if name not in added}


def current_runtime():
    return {path.relative_to(ROOT).as_posix(): path.read_bytes() for path in SOURCE.rglob('*')
            if path.is_file() and '__pycache__' not in path.parts and path.name != '.DS_Store'}


def baseline_runtime():
    from release_candidate98 import source98
    return {'src/'+name: raw for name, raw in source98().items()}


def undo_edits(before, after):
    old = before.decode('utf-8').splitlines(keepends=True)
    new = after.decode('utf-8').splitlines(keepends=True)
    return [[new_start, new_stop, old[old_start:old_stop]]
            for tag, old_start, old_stop, new_start, new_stop
            in SequenceMatcher(a=old, b=new, autojunk=False).get_opcodes() if tag != 'equal']


def refresh():
    from release_candidate99 import BASE
    before, current = baseline_runtime(), current_runtime()
    if before.keys() - current.keys():
        raise ValueError('REMOVED99_RUNTIME_FILES')
    added = {name: digest(current[name]) for name in current.keys() - before.keys()}
    changed = {name: dict(undo_edits=undo_edits(raw, current[name]), old_sha256=digest(raw),
                          new_sha256=digest(current[name]))
               for name, raw in before.items() if current[name] != raw}
    data = dict(base=BASE, added=added, changed=changed)
    FIXTURE.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False)+'\n', encoding='utf-8')
    delta99.cache_clear()
    return dict(base=BASE, added=len(added), changed=len(changed))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', required=True, action='store_true')
    parser.parse_args()
    print(json.dumps(refresh(), sort_keys=True))
