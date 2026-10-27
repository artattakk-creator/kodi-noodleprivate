"""Exact reviewed .44 blocks only; retain all historical source contracts."""
import json
from pathlib import Path


def without_stabilization44(source,module):
    from stabilization_contract_02945 import without_stabilization45
    source=without_stabilization45(source,module)
    binary=isinstance(source,bytes)
    modules=json.loads((Path(__file__).parent/'fixtures/xcmate_02944_reviewed_hooks.json').read_text())['modules']
    paths=[p for p in modules if p==str(module) or p.endswith('/'+str(module).removesuffix('.py')+'.py')]
    assert len(paths)<=1,module
    if not paths:return source
    if binary:source=source.decode()
    for change in modules[paths[0]]:
        if source.count(change['new'])==1:source=source.replace(change['new'],change['old'],1)
        else:assert source.count(change['old'])==1,module
    return source.encode() if binary else source
