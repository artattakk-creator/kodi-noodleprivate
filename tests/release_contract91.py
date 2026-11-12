"""Normalize only the two exact .91 metadata files for historical scope gates."""
import hashlib
import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def metadata91():
    return json.loads((ROOT/'tests/fixtures/release_02991_metadata.json').read_text())

@lru_cache(maxsize=2)
def original91(path):
    raw = metadata91()['modules'][path]['old'].encode()
    assert hashlib.sha256(raw).hexdigest() == metadata91()['modules'][path]['old_sha256']
    return raw

def without_release91(source, module):
    binary = isinstance(source, bytes)
    raw = source if binary else source.encode()
    path = str(module)
    delta = metadata91()['modules'].get(path)
    if delta and hashlib.sha256(raw).hexdigest() == delta['new_sha256']:
        before = original91(path)
        return before if binary else before.decode()
    return source
