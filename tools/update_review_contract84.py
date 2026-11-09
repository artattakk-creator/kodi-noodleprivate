"""Refresh exact reviewed .84 deltas against the published .83 main baseline."""
import ast,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE='ee42712655cb9adcdcb11b09d591a1737d899844'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def run():
 paths=git('ls-tree','-r','--name-only',BASE,'src/plugin.video.xtreammate').decode().splitlines()
 old={p:git('show',BASE+':'+p) for p in paths if '__pycache__' not in p and not p.endswith('.pyc')}
 changes={p:dict(old=raw.decode(),new=(ROOT/p).read_text()) for p,raw in old.items() if (ROOT/p).read_bytes()!=raw}
 protection=dict(base=BASE,source_sha256={p:hashlib.sha256(raw).hexdigest() for p,raw in old.items()},test_methods={},existing_skip_conditions={})
 for path in git('ls-tree','-r','--name-only',BASE,'tests').decode().splitlines():
  if not Path(path).name.startswith('test_') or not path.endswith('.py'):continue
  tree=ast.parse(git('show',BASE+':'+path));cases=[]
  for cls in tree.body:
   if not isinstance(cls,ast.ClassDef):continue
   for fn in cls.body:
    if not isinstance(fn,ast.FunctionDef) or not fn.name.startswith('test_'):continue
    cases.append([cls.name,fn.name]);protection['existing_skip_conditions'][path+'|'+cls.name+'|'+fn.name]=[ast.unparse(d) for d in fn.decorator_list if 'skip' in ast.unparse(d)]
  protection['test_methods'][path]=cases
 (ROOT/'tests/fixtures/xcmate_02984_reviewed_hooks.json').write_text(json.dumps(dict(modules=changes),indent=2)+'\n')
 (ROOT/'tests/fixtures/xcmate_02984_protection.json').write_text(json.dumps(protection,indent=2)+'\n')
 print('Reviewed changed files:',len(changes),'preserved source files:',len(old))
if __name__=='__main__':run()
