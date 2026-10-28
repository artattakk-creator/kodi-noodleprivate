"""Only exact .50 routing, labels and opt-in Home entry may differ from .49."""
import hashlib,json
from pathlib import Path
from functools import lru_cache

@lru_cache(maxsize=1)
def data50():
    root=Path(__file__).parent/'fixtures'
    hooks=json.loads((root/'xcmate_02950_reviewed_hooks.json').read_text())['modules']
    hashes={}
    for file in root.glob('xcmate_029*_protection.json'):
        if file.name>'xcmate_02950_protection.json':continue
        for path,digest in json.loads(file.read_text()).get('source_sha256',{}).items():
            hashes.setdefault(path,set()).add(digest)
    return hooks,hashes

def without_widget50(source,module):
    from stabilization_contract_02951 import without_wizard51
    source=without_wizard51(source,module)
    binary=isinstance(source,bytes);raw=source if binary else source.encode()
    hooks,hashes=data50()
    paths=[p for p in hooks if p==str(module) or p.endswith('/'+str(module).removesuffix('.py')+'.py')]
    assert len(paths)<=1,module
    if not paths:return source
    path=paths[0]
    if hashlib.sha256(raw).hexdigest() in hashes.get(path,set()):return source
    text=raw.decode()
    for change in reversed(hooks[path]):
        assert text.count(change['new'])==1,(module,'unreviewed .50 change')
        text=text.replace(change['new'],change['old'],1)
    return text.encode() if binary else text
