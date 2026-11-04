"""Normalize only byte-identical reviewed #355 deltas for .71 contracts."""
import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def hooks72():
    return json.loads((Path(__file__).parent / 'fixtures/xcmate_02972_reviewed_hooks.json').read_text())['modules']


def without_stabilization72(source, module):
    binary = isinstance(source, bytes); raw = source if binary else source.encode()
    for path, delta in hooks72().items():
        if path == str(module) or path.endswith('/' + str(module).removesuffix('.py') + '.py'):
            if raw == delta['new'].encode(): return delta['old'].encode() if binary else delta['old']
    return source
