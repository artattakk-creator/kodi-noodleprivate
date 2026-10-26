"""Read-only source/test/WIP preservation proof against released .41."""
import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '354afc1cc524ec3b01001770e6afe6aec5fea70c'
PREFIX = 'src/plugin.video.xtreammate/'


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def methods(data):
    return {(c.name, n.name) for c in ast.parse(data).body if isinstance(c, ast.ClassDef)
            for n in c.body if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--wip', nargs=2, action='append', default=[])
    args = parser.parse_args()
    allowed = set(json.loads((ROOT/'tests/fixtures/xcmate_02942_allowed_paths.json').read_text()))
    changed = set(git('diff', BASE, '--name-only', '--', PREFIX).decode().splitlines())
    assert changed == allowed, (changed-allowed, allowed-changed)
    count = retained = 0
    for path in git('ls-tree', '-r', '--name-only', BASE).decode().splitlines():
        if path.startswith(PREFIX) and path not in allowed:
            assert (ROOT/path).read_bytes() == git('show', BASE+':'+path), path
            count += 1
        if path.startswith('tests/test_') and path.endswith('.py'):
            old = methods(git('show', BASE+':'+path))
            assert old <= methods((ROOT/path).read_bytes()), path
            retained += len(old)
    assert retained == 1479, retained
    for path in ('addons.xml', 'addons.xml.md5', '.github/workflows/publish.yml',
                 'plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.41.zip'):
        assert (ROOT/path).read_bytes() == git('show', BASE+':'+path), path
    protected_wip = 0
    for folder, manifest in args.wip:
        for path, digest in json.loads(Path(manifest).read_text()).items():
            assert hashlib.sha256((Path(folder)/path).read_bytes()).hexdigest() == digest, path
            protected_wip += 1
    result = dict(base=BASE, head=git('rev-parse', 'HEAD').decode().strip(),
                  allowed_source_paths=sorted(allowed), unchanged_source_files=count,
                  retained_041_tests=retained, other_wip_files=protected_wip,
                  player_vod_series_resume_autoplay='BYTE_IDENTICAL',
                  mini_epg_widgets_update_notice='BYTE_IDENTICAL',
                  overlay_back_and_remote_keymaps='BYTE_IDENTICAL',
                  portals_epg_artwork_and_modes='BYTE_IDENTICAL',
                  all_skin_files_and_original_art='BYTE_IDENTICAL',
                  repository_indexes_publish_workflow_041_zip='BYTE_IDENTICAL',
                  compatibility_default=False, native_deadlock_fixed='NOT_PROVEN',
                  android='NOT_TESTED', device_actions=0, profile_migrations=0)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
