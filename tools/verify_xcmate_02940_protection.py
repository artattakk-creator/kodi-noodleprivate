"""Explicit .40 source exceptions; old tests, UI skeleton, assets and WIP."""
import argparse,ast,hashlib,json,subprocess,sys
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
BASE='25a640869e3b4e178945ba4f549ad7e269dd292f'
PREFIX='src/plugin.video.xtreammate/'

def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])
def sha(data):return hashlib.sha256(data).hexdigest()
def cases(data):
 tree=ast.parse(data)
 return {(c.name,n.name) for c in tree.body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--wip',nargs=2,action='append',default=[]);args=p.parse_args()
 expected=set(json.loads((ROOT/'tests/fixtures/xcmate_02940_allowed_paths.json').read_text()))
 changed=set(git('diff',BASE,'--name-only','--',PREFIX).decode().splitlines());assert changed==expected,(changed-expected,expected-changed)
 paths=git('ls-tree','-r','--name-only',BASE).decode().splitlines();protected={};old_tests=0
 for name in paths:
  if name.startswith(PREFIX) and name not in expected:
   assert (ROOT/name).read_bytes()==git('show',BASE+':'+name),name;protected[name]=sha((ROOT/name).read_bytes())
  if name.startswith('tests/test_') and name.endswith('.py'):
   prior=cases(git('show',BASE+':'+name));assert prior<=cases((ROOT/name).read_bytes()),name;old_tests+=len(prior)
 assert old_tests==1403,old_tests
 for name in ('addons.xml','addons.xml.md5','plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.39.zip'):
  assert (ROOT/name).read_bytes()==git('show',BASE+':'+name),name
 assert (ROOT/'.github/workflows/publish.yml').read_bytes()==git('show',BASE+':.github/workflows/publish.yml')
 # Exact unchanged tab/result layout, independent of permitted 820 detail-edge guard.
 xml=PREFIX+'resources/skins/Default/720p/XCMateMedia.xml';old=ET.fromstring(git('show',BASE+':'+xml));new=ET.parse(ROOT/xml).getroot()
 controls=(700,701,702,710,720,721)
 for cid in controls:
  assert ET.tostring(old.find(".//control[@id='"+str(cid)+"']"))==ET.tostring(new.find(".//control[@id='"+str(cid)+"']")),cid
 sys.path.insert(0,str(ROOT/'tests'));from stabilization_contract_02940 import without_stabilization40
 ui=json.loads((ROOT/'tests/fixtures/xcmate_02934_search_ui_freeze.json').read_text());same38=0;exceptions=[]
 for name in ui['files']:
  current=(ROOT/name).read_bytes();baseline=git('show',BASE+':'+name)
  assert without_stabilization40(current,name)==baseline,name
  if current==baseline:same38+=1
  else:exceptions.append(name)
 images=[name for name in paths if name.startswith('themes/xcmate/space-premium/') and Path(name).suffix.lower() in ('.png','.jpg','.jpeg')]
 for name in images:assert (ROOT/name).read_bytes()==git('show',BASE+':'+name),name
 for name in ('icon.png','fanart.jpg','resources/lib/artwork_config.py','resources/lib/portals.py','resources/lib/epg_sources.py','resources/lib/guide_store.py','resources/lib/media_state.py','resources/lib/media_progress.py','resources/lib/media_autoplay.py','resources/lib/player.py','resources/lib/remote_control.py','resources/lib/remote_profiles.py'):
  assert (ROOT/PREFIX/name).read_bytes()==git('show',BASE+':'+PREFIX+name),name
 wip=0
 for folder,manifest in args.wip:
  for name,digest in json.loads(Path(manifest).read_text()).items():assert sha((Path(folder)/name).read_bytes())==digest,name;wip+=1
 result=dict(base=BASE,head=git('rev-parse','HEAD').decode().strip(),allowed_source_changes=sorted(expected),protected_source_files=len(protected),protected_sources=protected,retained_baseline_test_methods=old_tests,search_xml_controls_byte_equivalent=list(controls),ui_contract_total=len(ui['files']),ui_raw_identical_to_039=same38,explicit_040_exceptions=exceptions,original_theme_images=len(images),original_icon='BYTE_IDENTICAL',profile_mode_gate='BYTE_IDENTICAL',portal_epg_resume_autoplay_data_modules='BYTE_IDENTICAL',decoder_player='BYTE_IDENTICAL',remote_keymap_modules='BYTE_IDENTICAL',existing_job_schema='BYTE_IDENTICAL to .39',new_journal='NONE added in .40',production_index='UNCHANGED',previous_039_zip='UNCHANGED',ci_publish_condition='BYTE_IDENTICAL; PR publish skipped by existing condition',protected_local_wip_files=wip,android='NOT_TESTED',device_mutation=False)
 args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('protected_sources','allowed_source_changes')}))
if __name__=='__main__':main()
