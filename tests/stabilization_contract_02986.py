"""Only byte-exact reviewed .86 display changes normalize for archived source tests."""
import json
from pathlib import Path
from functools import lru_cache
@lru_cache(maxsize=1)
def hooks86():return json.loads((Path(__file__).parent/'fixtures/xcmate_02986_reviewed_hooks.json').read_text())['modules']
def without_stabilization86(source,module):
    from stabilization_contract_02987 import without_stabilization87
    source=without_stabilization87(source,module)
    binary=isinstance(source,bytes);raw=source if binary else source.encode()
    for path,delta in hooks86().items():
        if path==str(module) or path.endswith('/'+str(module).removesuffix('.py')+'.py'):
            if raw==delta['new'].encode():return delta['old'].encode() if binary else delta['old']
    return source
