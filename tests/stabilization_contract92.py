"""Exact reviewed .92 delta only. Unknown edits never bypass historical guards."""
import hashlib
import json
from functools import lru_cache
from pathlib import Path
@lru_cache(maxsize=1)
def delta92():return json.loads((Path(__file__).parent/'fixtures/stabilization_02992_delta.json').read_text())
def without92(source,module):
 source=__import__('stabilization_contract93').without93(source,module)
 binary=isinstance(source,bytes);raw=source if binary else source.encode();name=str(module)
 for path,change in delta92()['modules'].items():
  if name not in (path,Path(path).name,Path(path).stem):continue
  if hashlib.sha256(raw).hexdigest()==change['new_sha256']:
   before=change['old'].encode()
   if hashlib.sha256(before).hexdigest()!=change['old_sha256']:raise ValueError('CORRUPT_92_REVIEW_FIXTURE')
   return before if binary else before.decode()
 return source
