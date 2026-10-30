"""Normalize only the exact reviewed .59 deltas; keep old scope checks live."""
import hashlib,json
from pathlib import Path
from functools import lru_cache

@lru_cache(maxsize=1)
def data59():
    root=Path(__file__).parent/'fixtures'
    hooks=json.loads((root/'xcmate_02959_reviewed_hooks.json').read_text())['modules']
    hashes={}
    for file in root.glob('xcmate_029*_protection.json'):
        if file.name>'xcmate_02959_protection.json':continue
        for path,digest in json.loads(file.read_text()).get('source_sha256',{}).items():
            hashes.setdefault(path,set()).add(digest)
    return hooks,hashes

def without_stabilization59(source,module):
    from stabilization_contract_02960 import without_stabilization60
    source=without_stabilization60(source,module)
    binary=isinstance(source,bytes);raw=source if binary else source.encode()
    hooks,hashes=data59()
    paths=[p for p in hooks if p==str(module) or p.endswith('/'+str(module).removesuffix('.py')+'.py')]
    assert len(paths)<=1,module
    if not paths:return source
    path=paths[0];digest=hashlib.sha256(raw).hexdigest()
    if digest in hashes.get(path,set()):return source
    change=hooks[path]
    assert digest==change['after_sha256'] and raw==change['new'].encode(),(module,'unreviewed .59 change')
    return change['old'].encode() if binary else change['old']
