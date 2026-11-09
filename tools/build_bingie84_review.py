"""Pinned full graph -> current guarded adapter; disposable synthetic profile."""
import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'tests'))
from build_bingie66_review import build
from test_xcmate_skin_02978 import Skin78
p=argparse.ArgumentParser();p.add_argument('--skin',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
build(a.skin,a.output)
h=Skin78(methodName='runTest');h.setUp()
try:
 source={name:(a.skin/name).read_bytes() for name in h.m.FILES}
 current=h.m.build(source)
 for name,raw in current.items():(a.output/name).write_bytes(raw)
finally:h.doCleanups()
