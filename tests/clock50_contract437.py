"""Only the byte-exact reviewed clock repair normalizes historical guards."""
import json
from functools import lru_cache
from pathlib import Path
@lru_cache(maxsize=1)
def delta437():
 return json.loads((Path(__file__).parent/'fixtures/pr437_reviewed_delta.json').read_text())
def without_clock437(source,module):
 binary=isinstance(source,bytes);raw=source if binary else source.encode()
 spinner=json.loads((Path(__file__).parent/'fixtures/media_spinner_reviewed_delta.json').read_text())
 if (str(module)==spinner['path'] or str(module) in ('widget_skin90','widget_skin90.py')) and raw==spinner['new'].encode():
  source=spinner['old'].encode() if binary else spinner['old'];raw=source if binary else source.encode()
 delta=delta437()
 if (str(module)==delta['path'] or str(module) in ('widget_reload78','widget_reload78.py')) and raw==delta['new'].encode():
  return delta['old'].encode() if binary else delta['old']
 return source
