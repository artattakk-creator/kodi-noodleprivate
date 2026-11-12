"""Only the byte-exact reviewed clock repair normalizes historical guards."""
import json
from functools import lru_cache
from pathlib import Path
@lru_cache(maxsize=1)
def delta437():
 return json.loads((Path(__file__).parent/'fixtures/pr437_reviewed_delta.json').read_text())
def without_clock437(source,module):
 delta=delta437();binary=isinstance(source,bytes);raw=source if binary else source.encode()
 if (str(module)==delta['path'] or str(module) in ('widget_reload78','widget_reload78.py')) and raw==delta['new'].encode():
  return delta['old'].encode() if binary else delta['old']
 return source
