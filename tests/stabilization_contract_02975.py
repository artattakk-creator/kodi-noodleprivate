"""Only byte-exact reviewed .75 repairs normalize for archived source tests."""
import json
from pathlib import Path
from functools import lru_cache
@lru_cache(maxsize=1)
def hooks75():return json.loads((Path(__file__).parent/'fixtures/xcmate_02975_reviewed_hooks.json').read_text())['modules']
def without_stabilization75(source,module):
    from stabilization_contract_02976 import without_stabilization76
    source=without_stabilization76(source,module)
    binary=isinstance(source,bytes);raw=source if binary else source.encode()
    for path,delta in hooks75().items():
        if path==str(module) or path.endswith('/'+str(module).removesuffix('.py')+'.py'):
            if raw==delta['new'].encode():return delta['old'].encode() if binary else delta['old']
    return source
