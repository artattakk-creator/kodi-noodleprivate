"""Normalize exact reviewed .68 changes before historic immutable contracts."""
import json
from functools import lru_cache
from pathlib import Path
@lru_cache(maxsize=1)
def hooks68():
 return json.loads((Path(__file__).parent/'fixtures/xcmate_02968_reviewed_hooks.json').read_text())['modules']
def without_stabilization68(source,module):
 binary=isinstance(source,bytes);raw=source if binary else source.encode()
 for path,delta in hooks68().items():
  if path==str(module) or path.endswith('/'+str(module).removesuffix('.py')+'.py'):
   if raw==delta['new'].encode():return delta['old'].encode() if binary else delta['old']
 return source
