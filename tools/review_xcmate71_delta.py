"""Generate exact baseline/current audit pairs; never silently bless other files."""
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='bcfe131becdaec86ba0d9880cc67ca8d524c5a4f'
paths=subprocess.check_output(['git','diff','--name-only',BASE,'--','src/plugin.video.xtreammate'],cwd=ROOT,text=True).splitlines()
modules={}
for path in paths:
    old=subprocess.run(['git','show',BASE+':'+path],cwd=ROOT,capture_output=True)
    if old.returncode:continue
    modules[path]=dict(old=old.stdout.decode(),new=(ROOT/path).read_text())
(ROOT/'tests/fixtures/xcmate_02971_reviewed_hooks.json').write_text(json.dumps(dict(base=BASE,modules=modules),ensure_ascii=False,indent=2)+'\n')
print('Reviewed existing modules:',len(modules))
