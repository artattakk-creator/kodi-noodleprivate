"""Only exact reviewed .69 deltas normalize historic source contracts."""
import json
from pathlib import Path
from functools import lru_cache
@lru_cache(maxsize=1)
def hooks69():return json.loads((Path(__file__).parent/'fixtures/xcmate_02969_reviewed_hooks.json').read_text())['modules']
def without_stabilization69(source,module):
 from stabilization_contract_02970 import without_stabilization70
 source=without_stabilization70(source,module)
 binary=isinstance(source,bytes);raw=source if binary else source.encode()
 for path,delta in hooks69().items():
  if path==str(module) or path.endswith('/'+str(module).removesuffix('.py')+'.py'):
   if raw==delta['new'].encode():return delta['old'].encode() if binary else delta['old']
 return source
