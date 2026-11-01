"""Accept only complete reviewed .66 changes; runtime tests execute new code."""
import hashlib,json
from functools import lru_cache
from pathlib import Path
@lru_cache(maxsize=1)
def data66():
 root=Path(__file__).parent/'fixtures'
 baseline=json.loads((root/'xcmate_02966_protection.json').read_text())
 hooks=json.loads((root/'xcmate_02966_reviewed_hooks.json').read_text())['modules']
 return hooks,baseline['source_sha256']
def without_stabilization66(source,module):
 binary=isinstance(source,bytes);raw=source if binary else source.encode()
 hooks,hashes=data66();paths=[p for p in hooks if p==str(module) or p.endswith('/'+str(module).removesuffix('.py')+'.py')]
 assert len(paths)<=1,module
 if not paths:return source
 path=paths[0]
 if hashlib.sha256(raw).hexdigest()==hashes.get(path):return source
 change=hooks[path]
 assert raw==change['new'].encode(),(module,'unreviewed .66 change')
 assert hashlib.sha256(change['old'].encode()).hexdigest()==change['before_sha256'],module
 return change['old'].encode() if binary else change['old']
