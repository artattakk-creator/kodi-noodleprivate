"""Exact .94 delta only; unknown edits cannot bypass any historical scope gate."""
import hashlib,json
from pathlib import Path
from functools import lru_cache
@lru_cache(maxsize=1)
def delta94():return json.loads((Path(__file__).parent/'fixtures/stabilization_02994_delta.json').read_text())
def without94(source,module):
    binary=isinstance(source,bytes);raw=source if binary else source.encode();name=str(module)
    for path,change in delta94()['modules'].items():
        if name not in (path,Path(path).name,Path(path).stem):continue
        if hashlib.sha256(raw).hexdigest()==change['new_sha256']:
            before=change['old'].encode()
            if hashlib.sha256(before).hexdigest()!=change['old_sha256']:raise ValueError('CORRUPT_94_REVIEW_FIXTURE')
            return before if binary else before.decode()
    return source
