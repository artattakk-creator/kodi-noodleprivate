"""Invert only exact reviewed .46 hooks for prior immutable source contracts."""
import hashlib,json
from functools import lru_cache
from pathlib import Path

@lru_cache(maxsize=1)
def previous_hashes():
 values={}
 for number in ('02946','02945','02944','02943','02942'):
  file=Path(__file__).parent/('fixtures/xcmate_'+number+'_protection.json')
  if not file.exists():continue
  for path,digest in json.loads(file.read_text()).get('source_sha256',{}).items():values.setdefault(path,set()).add(digest)
 return values

def without_stabilization46(source,module):
 binary=isinstance(source,bytes)
 modules=json.loads((Path(__file__).parent/'fixtures/xcmate_02946_reviewed_hooks.json').read_text())['modules']
 paths=[p for p in modules if p==str(module) or p.endswith('/'+str(module).removesuffix('.py')+'.py')]
 assert len(paths)<=1,module
 if not paths:return source
 raw=source if binary else source.encode()
 if hashlib.sha256(raw).hexdigest() in previous_hashes().get(paths[0],set()):return source
 if binary:source=source.decode()
 for change in modules[paths[0]]:
  if source.count(change['new'])==1:source=source.replace(change['new'],change['old'],1)
  else:assert source.count(change['old'])==1,module
 return source.encode() if binary else source
