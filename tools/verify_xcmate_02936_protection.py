"""Explicit .36 exception list; verify frozen data/player/UI and optional local WIP."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
BASE='9c558c70e8abd56d071d703ff9e78909e78c85ac'
PREFIX='src/plugin.video.xtreammate/'
ALLOWED={PREFIX+p for p in ('addon.xml','changelog.txt','service.py',
    'resources/lib/app_routes.py','resources/lib/app_services.py','resources/lib/boot_diagnostics.py',
    'resources/lib/genre_search.py','resources/lib/guide_viewport.py','resources/lib/library_index.py',
    'resources/lib/live_catalog.py','resources/lib/live_exit.py','resources/lib/live_overlay.py',
    'resources/lib/live_start.py','resources/lib/live_timing.py','resources/lib/main.py',
    'resources/lib/media_search.py','resources/lib/search_data.py','resources/lib/search_profile.py',
    'resources/lib/short_cache_inventory.py','resources/lib/startup_preload.py','resources/lib/tv_data.py')}


def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])
def sha(data):return hashlib.sha256(data).hexdigest()


def methods(source,cls):
    node=next(n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name==cls)
    return {n.name:ast.dump(n,include_attributes=False) for n in node.body if isinstance(n,ast.FunctionDef)}


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--wip',nargs=2,action='append',default=[],metavar=('ROOT','MANIFEST'));args=p.parse_args()
    changed=set(git('diff',BASE,'--name-only','--','src/plugin.video.xtreammate').decode().splitlines())
    assert changed==ALLOWED,(changed-ALLOWED,ALLOWED-changed)
    paths=git('ls-tree','-r','--name-only',BASE).decode().splitlines();protected={}
    for name in paths:
        if name.startswith(PREFIX) and name not in ALLOWED:
            data=(ROOT/name).read_bytes();assert data==git('show',BASE+':'+name),name
            protected[name]=sha(data)
    exact=('addons.xml','addons.xml.md5','.github/workflows/publish.yml',
           'plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.35.zip')
    for name in exact:assert (ROOT/name).read_bytes()==git('show',BASE+':'+name),name
    ui=json.loads((ROOT/'tests/fixtures/xcmate_02934_search_ui_freeze.json').read_text())
    for name,digest in ui['files'].items():assert sha((ROOT/name).read_bytes())==digest,name
    images=[name for name in paths if name.startswith('themes/xcmate/space-premium/') and Path(name).suffix.lower() in ('.png','.jpg','.jpeg')]
    for name in images:assert (ROOT/name).read_bytes()==git('show',BASE+':'+name),name
    for name,cls,allowed in (('live_overlay','LiveNavigator',{'__init__','_load_catalog_from_disk','show','_switch','handle_command'}),
                             ('main','Router',{'_startup_playable','_play_start','_play_start_direct'})):
        path=PREFIX+'resources/lib/'+name+'.py'
        old=methods(git('show',BASE+':'+path),cls);new=methods((ROOT/path).read_text(),cls)
        assert set(old)==set(new)
        assert {key for key in old if old[key]!=new[key]}==allowed,(name,'unexpected AST change')
    count=0
    for root,manifest in args.wip:
        for name,digest in json.loads(Path(manifest).read_text()).items():
            assert sha((Path(root)/name).read_bytes())==digest,name
            count+=1
    report=dict(base=BASE,reviewed_main='46b4f9f',allowed_source_changes=sorted(ALLOWED),
        protected_source_files=len(protected),protected_sources=protected,
        ui_asset_lifecycle_freeze_files=len(ui['files']),original_theme_images=len(images),protected_local_wip_files=count,
        live_renderers_player_and_native_callbacks='AST_IDENTICAL',guide_and_search_window_lifecycle='BYTE_IDENTICAL',
        original_icon='BYTE_IDENTICAL',autoplay_resume_watched_portal_mapping_sources='BYTE_IDENTICAL',
        downloads_and_recordings='BYTE_IDENTICAL',production_indexes='UNCHANGED',publish_workflow='UNCHANGED',previous_035_zip='UNCHANGED',
        genre_schema='TWO_ADDITIVE_DERIVED_TABLES; ORIGINAL_ROWS_VIEWS_COLUMNS_UNCHANGED_BY_HOST_TEST',
        android='NOT_TESTED')
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:value for key,value in report.items() if key not in ('protected_sources','allowed_source_changes')}))


if __name__=='__main__':main()
