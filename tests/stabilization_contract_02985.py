"""Only byte-exact reviewed .85 display changes normalize for archived source tests."""
import json
from pathlib import Path
from functools import lru_cache
@lru_cache(maxsize=1)
def hooks85():return json.loads((Path(__file__).parent/'fixtures/xcmate_02985_reviewed_hooks.json').read_text())['modules']
def without_stabilization85(source,module):
    from stabilization_contract_02986 import without_stabilization86
    source=without_stabilization86(source,module)
    binary=isinstance(source,bytes);raw=source if binary else source.encode()
    for path,delta in hooks85().items():
        if path==str(module) or path.endswith('/'+str(module).removesuffix('.py')+'.py'):
            if raw==delta['new'].encode():return delta['old'].encode() if binary else delta['old']
    return source
