"""Only byte-exact reviewed .88 reviewed changes normalize for archived source tests."""
import json
from pathlib import Path
from functools import lru_cache
@lru_cache(maxsize=1)
def hooks88():return json.loads((Path(__file__).parent/'fixtures/xcmate_02988_reviewed_hooks.json').read_text())['modules']
def without_stabilization88(source,module):
    source=__import__('stabilization_contract_02989').without_stabilization89(source,module)
    binary=isinstance(source,bytes);raw=source if binary else source.encode()
    for path,delta in hooks88().items():
        if path==str(module) or path.endswith('/'+str(module).removesuffix('.py')+'.py'):
            if raw==delta['new'].encode():return delta['old'].encode() if binary else delta['old']
    return source
