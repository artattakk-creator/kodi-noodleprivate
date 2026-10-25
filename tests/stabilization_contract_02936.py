"""Exact .36 hook exception; original .26/.29 hashes remain untouched.

The fixture pins both reviewed method bodies. Any additional change fails
normalization, then the historical whole-module/AST freeze still applies.
"""
import json
from pathlib import Path


def without_stabilization36(source,module):
    binary=isinstance(source,bytes)
    if binary:source=source.decode()
    data=json.loads((Path(__file__).parent/'fixtures/xcmate_02936_reviewed_hooks.json').read_text())
    for change in data['modules'][module]['changes'].values():
        assert source.count(change['new'])==1,module
        source=source.replace(change['new'],change['old'],1)
    return source.encode() if binary else source
