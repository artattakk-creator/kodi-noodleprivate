"""Exact authorized .38 exceptions; all historical contracts still run."""
import json
from pathlib import Path

def without_stabilization38(source,module):
    from stabilization_contract_02939 import without_stabilization39
    source=without_stabilization39(source,module)
    binary=isinstance(source,bytes)
    data=json.loads((Path(__file__).parent/'fixtures/xcmate_02938_reviewed_hooks.json').read_text())
    paths=[path for path in data['modules'] if path==str(module) or path.endswith('/'+str(module).removesuffix('.py')+'.py')]
    assert len(paths)<=1,module
    if not paths:return source
    if binary:source=source.decode()
    for change in data['modules'].get(paths[0] if paths else '',[]):
        if source.count(change['new'])==1:source=source.replace(change['new'],change['old'],1)
        else:assert source.count(change['old'])==1,module
    return source.encode() if binary else source
