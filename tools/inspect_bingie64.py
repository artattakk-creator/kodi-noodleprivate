#!/usr/bin/env python3
"""Read-only .64 source/skin evidence from pinned .63 and official BINGIE."""
import ast,hashlib,io,json,subprocess,sys,tempfile,urllib.request,zipfile
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
BASE='4e89c3a8af29a8796f26c2b3ddb2c1484ef89769'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def baseline():
 paths=git('ls-tree','-r','--name-only',BASE).decode().splitlines()
 value=dict(base=BASE,source_sha256={},test_methods={},existing_skip_conditions={})
 for path in paths:
  if path.startswith('src/plugin.video.xtreammate/'):
   value['source_sha256'][path]=hashlib.sha256(git('show',BASE+':'+path)).hexdigest()
  elif path.startswith('tests/test') and path.endswith('.py'):
   methods=[]
   for cls in ast.parse(git('show',BASE+':'+path)).body:
    if not isinstance(cls,ast.ClassDef):continue
    for fn in cls.body:
     if isinstance(fn,ast.FunctionDef) and fn.name.startswith('test_'):
      methods.append([cls.name,fn.name])
      skip=[ast.unparse(d) for d in fn.decorator_list if 'skip' in ast.unparse(d)]
      if skip:value['existing_skip_conditions'][path+'|'+cls.name+'|'+fn.name]=skip
   if methods:value['test_methods'][path]=methods
 return value
def main():
 from run_kodi_home63_contract import SKIN_SHA,SKIN_URL
 with urllib.request.urlopen(SKIN_URL,timeout=60) as response:raw=response.read(512*1024*1024+1)
 assert len(raw)<=512*1024*1024
 assert hashlib.sha256(raw).hexdigest()==SKIN_SHA
 with tempfile.TemporaryDirectory() as folder:
  target=Path(folder)
  with zipfile.ZipFile(io.BytesIO(raw)) as z:
   assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist())
   z.extractall(target)
  skin=target/'skin.titan.bingie.mod'
  from build_bingie60_review import build
  build(skin,target/'candidate')
  print('MANIFEST63_JSON '+(target/'candidate/manifest.json').read_text().replace('\n',''))
  names=('Bingie_Screens_Fixed_Focus_Frame','Fixed_Focus_','PosterThumbFO_DefsBingie','PosterThumbBingieLayout','SetFixedVerticalNavigationProps')
  evidence=[]
  for path in sorted(skin.rglob('*.xml')):
   try:tree=E.parse(path)
   except E.ParseError:continue
   for node in tree.getroot().iter():
    name=node.get('name','')
    if any(name.startswith(n) for n in names):
     evidence.append(dict(file=path.name,name=name,xml=E.tostring(node,encoding='unicode')))
  print('BINGIE64_DEFINITIONS '+json.dumps(evidence))
  contexts=[]
  for path in sorted(skin.rglob('*')):
   if not path.is_file() or path.stat().st_size>4*1024*1024 or path.suffix.lower() not in ('.xml','.template'):continue
   text=path.read_text(errors='replace')
   for name in ('Fixed_Focus','FixedFocus','VerticalNavigation'):
    start=0
    for _ in range(6):
     pos=text.lower().find(name.lower(),start)
     if pos<0:break
     contexts.append(dict(file=str(path.relative_to(skin)),keyword=name,text=text[max(0,pos-350):pos+5500]));start=pos+len(name)
  print('BINGIE64_FOCUS_CONTEXTS '+json.dumps(contexts))
  import re
  defs=[]
  for path in skin.rglob('*.xml'):
   text=path.read_text(errors='replace');nodes=list(re.finditer(r'<include\\s+name="([^"]+)"',text))
   for i,m in enumerate(nodes):
    if m[1].startswith(('Bingie_Screens_Fixed_Focus_Frame','Fixed_Focus_Bottom','Fixed_Focus_Itemgap','SetFixedVerticalNavigationProps')):
     defs.append(dict(file=str(path.relative_to(skin)),name=m[1],xml=text[m.start():nodes[i+1].start() if i+1<len(nodes) else len(text)]))
  print('BINGIE64_RAW_DEFINITIONS '+json.dumps(defs))
 value=baseline();print('BASELINE64_JSON '+json.dumps(value,separators=(',',':')))
 print('BASELINE64_COUNTS '+json.dumps(dict(files=len(value['source_sha256']),tests=sum(map(len,value['test_methods'].values())))))
if __name__=='__main__':main()
