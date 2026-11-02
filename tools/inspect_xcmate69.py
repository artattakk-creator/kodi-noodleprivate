"""Pinned .68 source/test inventory, read-only."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import inspect_bingie64
inspect_bingie64.BASE='cf62f5d554634acca5c2676c6af3d524747f8f40'
v=inspect_bingie64.baseline()
print('BASELINE69_JSON '+json.dumps(v,separators=(',',':')),flush=True)
print('BASELINE69_COUNTS '+json.dumps(dict(files=len(v['source_sha256']),tests=sum(map(len,v['test_methods'].values())))),flush=True)
