"""Invert only the exact, individually reviewed .47 changes for older guards."""
import hashlib,json
from pathlib import Path
from functools import lru_cache


@lru_cache(maxsize=1)
def catalogues():
    root=Path(__file__).parent/'fixtures'
    baseline=json.loads((root/'xcmate_02947_protection.json').read_text())
    hooks=json.loads((root/'xcmate_02947_reviewed_hooks.json').read_text())['modules']
    hashes={p:{digest} for p,digest in baseline['source_sha256'].items()}
    for number in ('02946','02945','02944','02943','02942'):
        prior=root/('xcmate_'+number+'_protection.json')
        if prior.exists():
            for path,digest in json.loads(prior.read_text()).get('source_sha256',{}).items():hashes.setdefault(path,set()).add(digest)
    return hooks,hashes


def without_stabilization47(source,module):
    from stabilization_contract_02948 import without_stabilization48
    source=without_stabilization48(source,module)
    binary=isinstance(source,bytes)
    raw=source if binary else source.encode()
    hooks,hashes=catalogues()
    paths=[p for p in hooks if p==str(module) or p.endswith('/'+str(module).removesuffix('.py')+'.py')]
    assert len(paths)<=1,module
    if not paths:return source
    path=paths[0]
    # A prior guard may already be inspecting an older immutable revision.
    if hashlib.sha256(raw).hexdigest() in hashes.get(path,set()):return source
    text=raw.decode()
    for change in reversed(hooks[path]):
        if text.count(change['new'])==1:text=text.replace(change['new'],change['old'],1)
        else:assert text.count(change['old'])==1,module
    return text.encode() if binary else text
