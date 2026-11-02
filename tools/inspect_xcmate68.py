"""Read-only pinned .67 baseline and .68 compile/test runner evidence."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import inspect_bingie64
inspect_bingie64.BASE='4d8ba5ef2c7bf997af437e230ef1ec52e1e747e8'
value=inspect_bingie64.baseline()
print('BASELINE68_COUNTS '+json.dumps(dict(files=len(value['source_sha256']),tests=sum(map(len,value['test_methods'].values())))),flush=True)
