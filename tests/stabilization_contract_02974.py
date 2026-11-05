"""Only byte-identical reviewed .74 changes normalize for released contracts."""
from functools import lru_cache
import json
from pathlib import Path
@lru_cache(maxsize=1)
def hooks74():return json.loads((Path(__file__).parent/'fixtures/xcmate_02974_reviewed_hooks.json').read_text())['modules']
def without_stabilization74(source,module):
 from stabilization_contract_02975 import without_stabilization75
 source=without_stabilization75(source,module)
 binary=isinstance(source,bytes);raw=source if binary else source.encode()
 for path,delta in hooks74().items():
  if path==str(module) or path.endswith('/'+str(module).removesuffix('.py')+'.py'):
   if raw==delta['new'].encode():return delta['old'].encode() if binary else delta['old']
 return source
