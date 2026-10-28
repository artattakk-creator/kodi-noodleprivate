"""Only exact .49 routing/label hunks may differ from the published .48."""
import hashlib,json
from pathlib import Path
from functools import lru_cache

@lru_cache(maxsize=1)
def data49():
    root=Path(__file__).parent/'fixtures'
    hooks=json.loads((root/'xcmate_02949_reviewed_hooks.json').read_text())['modules']
    hashes={}
    for file in root.glob('xcmate_029*_protection.json'):
        if file.name>'xcmate_02949_protection.json':continue
        for path,digest in json.loads(file.read_text()).get('source_sha256',{}).items():
            hashes.setdefault(path,set()).add(digest)
    return hooks,hashes

def without_widget49(source,module):
    from stabilization_contract_02950 import without_widget50
    source=without_widget50(source,module)
    binary=isinstance(source,bytes);raw=source if binary else source.encode()
    hooks,hashes=data49()
    paths=[p for p in hooks if p==str(module) or p.endswith('/'+str(module).removesuffix('.py')+'.py')]
    assert len(paths)<=1,module
    if not paths:return source
    path=paths[0]
    if hashlib.sha256(raw).hexdigest() in hashes.get(path,set()):return source
    text=raw.decode()
    for change in reversed(hooks[path]):
        assert text.count(change['new'])==1,(module,'unreviewed .49 change')
        text=text.replace(change['new'],change['old'],1)
    return text.encode() if binary else text
