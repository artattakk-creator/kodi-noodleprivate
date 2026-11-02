"""Pinned .69 inventory for cumulative .70 protection."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import inspect_bingie64
inspect_bingie64.BASE='ebf12b3667df65f865d1e617457551ff9327f303'
value=inspect_bingie64.baseline()
print('BASELINE70_JSON '+json.dumps(value,separators=(',',':')),flush=True)
print('BASELINE70_COUNTS '+json.dumps(dict(files=len(value['source_sha256']),tests=sum(map(len,value['test_methods'].values())))),flush=True)
