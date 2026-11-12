"""Byte-exact reviewed .90 deltas; historical assertions remain executable."""
import json
from functools import lru_cache
from pathlib import Path
@lru_cache(maxsize=1)
def hooks90():return json.loads((Path(__file__).parent/'fixtures/xcmate_02990_reviewed_hooks.json').read_text())['modules']
def without_stabilization90(source,module):
 source=__import__('clock50_contract437').without_clock437(source,module)
 binary=isinstance(source,bytes);raw=source if binary else source.encode()
 for path,delta in hooks90().items():
  if path==str(module) or path.endswith('/'+str(module).removesuffix('.py')+'.py'):
   if raw==delta['new'].encode():return delta['old'].encode() if binary else delta['old']
 return source
