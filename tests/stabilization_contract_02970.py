"""Normalize only byte-exact audited .70 changes for historical contracts."""
import json
from pathlib import Path
from functools import lru_cache
@lru_cache(maxsize=1)
def hooks70():return json.loads((Path(__file__).parent/'fixtures/xcmate_02970_reviewed_hooks.json').read_text())['modules']
def without_stabilization70(source,module):
 from stabilization_contract_02971 import without_stabilization71
 source=without_stabilization71(source,module)
 binary=isinstance(source,bytes);raw=source if binary else source.encode()
 for path,delta in hooks70().items():
  if path==str(module) or path.endswith('/'+str(module).removesuffix('.py')+'.py'):
   if raw==delta['new'].encode():return delta['old'].encode() if binary else delta['old']
 return source
