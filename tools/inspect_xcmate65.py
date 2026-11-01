"""Freeze .64 source inventory and historic test methods from the fixed base."""
import ast,hashlib,json,subprocess
BASE='cad966081b9dd6fe75f7ff9cde2a4b286efdcf09'
def git(*args):return subprocess.check_output(['git',*args])
value=dict(base=BASE,source_sha256={},test_methods={},existing_skip_conditions={})
for path in git('ls-tree','-r','--name-only',BASE).decode().splitlines():
 if path.startswith('src/plugin.video.xtreammate/'):
  value['source_sha256'][path]=hashlib.sha256(git('show',BASE+':'+path)).hexdigest()
 elif path.startswith('tests/test') and path.endswith('.py'):
  methods=[]
  for cls in ast.parse(git('show',BASE+':'+path)).body:
   if not isinstance(cls,ast.ClassDef):continue
   for fn in cls.body:
    if not isinstance(fn,ast.FunctionDef) or not fn.name.startswith('test_'):continue
    methods.append([cls.name,fn.name])
    skip=[ast.unparse(d) for d in fn.decorator_list if 'skip' in ast.unparse(d)]
    if skip:value['existing_skip_conditions'][path+'|'+cls.name+'|'+fn.name]=skip
  if methods:value['test_methods'][path]=methods
print('BASELINE65_JSON '+json.dumps(value,separators=(',',':')))
print('BASELINE65_COUNTS '+json.dumps(dict(files=len(value['source_sha256']),tests=sum(map(len,value['test_methods'].values())))))
