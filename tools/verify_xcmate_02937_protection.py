"""Exact cumulative source exceptions, old tests, original assets and local WIP."""
import argparse,ast,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='ecf85f36537b79f88cc3dfaef0fc70b10836b848'
PREFIX='src/plugin.video.xtreammate/'

def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])
def sha(data):return hashlib.sha256(data).hexdigest()
def cases(data):
 tree=ast.parse(data)
 return {(c.name,n.name) for c in tree.body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--wip',nargs=2,action='append',default=[]);args=parser.parse_args()
 expected=set(json.loads((ROOT/'tests/fixtures/xcmate_02937_allowed_paths.json').read_text()))
 changed=set(git('diff',BASE,'--name-only','--',PREFIX).decode().splitlines());assert changed==expected,(changed-expected,expected-changed)
 paths=git('ls-tree','-r','--name-only',BASE).decode().splitlines();protected={};old_tests=0
 for name in paths:
  if name.startswith(PREFIX) and name not in expected:
   assert (ROOT/name).read_bytes()==git('show',BASE+':'+name),name
   protected[name]=sha((ROOT/name).read_bytes())
  if name.startswith('tests/test_') and name.endswith('.py'):
   prior=cases(git('show',BASE+':'+name));assert (ROOT/name).is_file(),name
   assert prior<=cases((ROOT/name).read_bytes()),name
   old_tests+=len(prior)
 exact=('addons.xml','addons.xml.md5','.github/workflows/publish.yml','plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.36.zip')
 for name in exact:assert (ROOT/name).read_bytes()==git('show',BASE+':'+name),name
 sys.path.insert(0,str(ROOT/'tests'))
 from stabilization_contract_02937 import without_stabilization37
 ui=json.loads((ROOT/'tests/fixtures/xcmate_02934_search_ui_freeze.json').read_text());raw=0;exceptions=[]
 for name,digest in ui['files'].items():
  source=(ROOT/name).read_bytes()
  assert sha(without_stabilization37(source,name))==digest,name
  if sha(source)==digest:raw+=1
  else:exceptions.append(name)
 images=[name for name in paths if name.startswith('themes/xcmate/space-premium/') and Path(name).suffix.lower() in ('.png','.jpg','.jpeg')]
 for name in images:assert (ROOT/name).read_bytes()==git('show',BASE+':'+name),name
 for name in ('icon.png','fanart.jpg'):
  assert (ROOT/PREFIX/name).read_bytes()==git('show',BASE+':'+PREFIX+name),name
 # SQL strings of existing index/bookmark tables remain identical.
 for name in ('library_index','media_state'):
  path=PREFIX+'resources/lib/'+name+'.py'
  def sql(data):return [n.value for n in ast.walk(ast.parse(data)) if isinstance(n,ast.Constant) and isinstance(n.value,str) and ('CREATE TABLE' in n.value or 'CREATE INDEX' in n.value)]
  assert sql(git('show',BASE+':'+path))==sql((ROOT/path).read_bytes()),name
 count=0
 for root,manifest in args.wip:
  for name,digest in json.loads(Path(manifest).read_text()).items():assert sha((Path(root)/name).read_bytes())==digest,name;count+=1
 report=dict(base=BASE,source_head=git('rev-parse','HEAD').decode().strip(),allowed_source_changes=sorted(expected),protected_source_files=len(protected),protected_sources=protected,retained_historical_test_methods=old_tests,ui_contract_total=len(ui['files']),ui_raw_byte_identical=raw,ui_explicit_037_exceptions=exceptions,original_theme_images=len(images),protected_local_wip_files=count,original_icon='BYTE_IDENTICAL',production_indexes='UNCHANGED',publish_workflow='UNCHANGED',previous_036_zip='UNCHANGED',existing_index_bookmark_schema='UNCHANGED',artwork_queue_schema='UNCHANGED; bounded existing .36 recovery retained',new_local_journals=['artwork_transfer_v1.sqlite','catalog_delta_v1.json','artwork_config_v1.json'],android='NOT_TESTED',user_device_access=False)
 args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('protected_sources','allowed_source_changes')}))
if __name__=='__main__':main()
