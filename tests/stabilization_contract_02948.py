"""Invert only exact .48 reviewed hunks; unknown or changed hunks fail closed."""
import hashlib,json
from pathlib import Path
from functools import lru_cache

@lru_cache(maxsize=1)
def data48():
    root=Path(__file__).parent/'fixtures'
    hooks=json.loads((root/'xcmate_02948_reviewed_hooks.json').read_text())['modules']
    hashes={}
    for file in root.glob('xcmate_029*_protection.json'):
        if file.name>'xcmate_02948_protection.json':continue
        for path,digest in json.loads(file.read_text()).get('source_sha256',{}).items():hashes.setdefault(path,set()).add(digest)
    return hooks,hashes

def without_stabilization48(source,module):
    from stabilization_contract_02949 import without_widget49
    source=without_widget49(source,module)
    binary=isinstance(source,bytes);raw=source if binary else source.encode()
    hooks,hashes=data48()
    paths=[p for p in hooks if p==str(module) or p.endswith('/'+str(module).removesuffix('.py')+'.py')]
    assert len(paths)<=1,module
    if not paths:return source
    path=paths[0]
    if hashlib.sha256(raw).hexdigest() in hashes.get(path,set()):return source
    text=raw.decode()
    for change in reversed(hooks[path]):
        assert text.count(change['new'])==1,(module,'unreviewed .48 change')
        text=text.replace(change['new'],change['old'],1)
    return text.encode() if binary else text
