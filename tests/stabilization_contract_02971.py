"""Normalize only byte-exact, reviewed #352 deltas for frozen .70 contracts."""
import json
from functools import lru_cache
from pathlib import Path
@lru_cache(maxsize=1)
def hooks71():return json.loads((Path(__file__).parent/'fixtures/xcmate_02971_reviewed_hooks.json').read_text())['modules']
def without_stabilization71(source,module):
    binary=isinstance(source,bytes);raw=source if binary else source.encode()
    for path,delta in hooks71().items():
        if path==str(module) or path.endswith('/'+str(module).removesuffix('.py')+'.py'):
            if raw==delta['new'].encode():return delta['old'].encode() if binary else delta['old']
    return source
