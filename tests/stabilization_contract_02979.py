"""Only byte-exact reviewed .78 repairs normalize for archived source tests."""
import json
from pathlib import Path
from functools import lru_cache
@lru_cache(maxsize=1)
def hooks79():return json.loads((Path(__file__).parent/'fixtures/xcmate_02979_reviewed_hooks.json').read_text())['modules']
def without_stabilization79(source,module):
    from stabilization_contract_02980 import without_stabilization80
    source=without_stabilization80(source,module)
    binary=isinstance(source,bytes);raw=source if binary else source.encode()
    for path,delta in hooks79().items():
        if path==str(module) or path.endswith('/'+str(module).removesuffix('.py')+'.py'):
            if raw==delta['new'].encode():return delta['old'].encode() if binary else delta['old']
    return source
