"""Explicit reviewed P0 hooks only; all .41 and older contracts still run."""
import json
from pathlib import Path


def without_stabilization42(source, module):
    from stabilization_contract_02943 import without_stabilization43
    source=without_stabilization43(source,module)
    binary = isinstance(source, bytes)
    changes = json.loads((Path(__file__).parent/'fixtures/xcmate_02942_reviewed_hooks.json').read_text())['modules']
    paths = [p for p in changes if p == str(module) or p.endswith('/'+str(module).removesuffix('.py')+'.py')]
    assert len(paths) <= 1, module
    if not paths:
        return source
    if binary:
        source = source.decode()
    for change in changes[paths[0]]:
        if source.count(change['new']) == 1:
            source = source.replace(change['new'], change['old'], 1)
        else:
            assert source.count(change['old']) == 1, module
    return source.encode() if binary else source
