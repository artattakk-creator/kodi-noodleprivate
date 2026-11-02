"""Normalize only complete reviewed .67 deltas in historic source snapshots."""
import hashlib,json
from functools import lru_cache
from pathlib import Path
@lru_cache(maxsize=1)
def data67():
 root=Path(__file__).parent/'fixtures'
 hooks=json.loads((root/'xcmate_02967_reviewed_hooks.json').read_text())['modules'];hashes={}
 for file in root.glob('xcmate_029*_protection.json'):
  if file.name>'xcmate_02967_protection.json':continue
  for path,digest in json.loads(file.read_text()).get('source_sha256',{}).items():hashes.setdefault(path,set()).add(digest)
 return hooks,hashes
def without_stabilization67(source,module):
 binary=isinstance(source,bytes);raw=source if binary else source.encode()
 final=Path(__file__).parent/'fixtures/xcmate_02967_final_hooks.json'
 if final.exists():
  for path,delta in json.loads(final.read_text())['modules'].items():
   if path==str(module) or path.endswith('/'+str(module).removesuffix('.py')+'.py'):
    if raw==delta['new'].encode():raw=delta['old'].encode()
 source=raw if binary else raw.decode()
 hooks,hashes=data67()
 paths=[p for p in hooks if p==str(module) or p.endswith('/'+str(module).removesuffix('.py')+'.py')]
 assert len(paths)<=1,module
 if not paths:return source
 path=paths[0]
 if hashlib.sha256(raw).hexdigest() in hashes.get(path,set()):return source
 change=hooks[path]
 assert raw==change['new'].encode(),(module,'unreviewed .67 change')
 assert hashlib.sha256(change['old'].encode()).hexdigest()==change['before_sha256'],module
 return change['old'].encode() if binary else change['old']
