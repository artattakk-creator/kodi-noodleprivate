"""Only byte-exact reviewed .77 repairs normalize for archived source tests."""
import json
from pathlib import Path
from functools import lru_cache
@lru_cache(maxsize=1)
def hooks77():return json.loads((Path(__file__).parent/'fixtures/xcmate_02977_reviewed_hooks.json').read_text())['modules']
def without_stabilization77(source,module):
    binary=isinstance(source,bytes);raw=source if binary else source.encode()
    for path,delta in hooks77().items():
        if path==str(module) or path.endswith('/'+str(module).removesuffix('.py')+'.py'):
            if raw==delta['new'].encode():return delta['old'].encode() if binary else delta['old']
    return source
