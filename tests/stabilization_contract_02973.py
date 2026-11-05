"""Only byte-exact reviewed .73 deltas normalize to the released .72 source."""
from functools import lru_cache
import json
from pathlib import Path
@lru_cache(maxsize=1)
def hooks73():return json.loads((Path(__file__).parent/'fixtures/xcmate_02973_reviewed_hooks.json').read_text())['modules']
def without_stabilization73(source,module):
    from stabilization_contract_02974 import without_stabilization74
    source=without_stabilization74(source,module)
    binary=isinstance(source,bytes);raw=source if binary else source.encode()
    for path,delta in hooks73().items():
        if path==str(module) or path.endswith('/'+str(module).removesuffix('.py')+'.py'):
            if raw==delta['new'].encode():return delta['old'].encode() if binary else delta['old']
    return source
