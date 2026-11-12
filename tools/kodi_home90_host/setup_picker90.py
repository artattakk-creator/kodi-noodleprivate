"""Fresh disposable picker profile; installs actual pinned SkinShortcuts 2.1.0."""
from pathlib import Path
import hashlib,zipfile
root=Path('/root/.kodi/addons')
raw=Path('/skinshortcuts90.zip').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='865ee5ea5bf0accee27b82539caabce1c8a9fbb8f94b2900fe5ace4f82c80b23'
with zipfile.ZipFile('/skinshortcuts90.zip') as z:
 assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist());z.extractall(root)
for addon in ('script.module.unidecode','script.module.simpleeval'):
 target=root/addon;target.mkdir(exist_ok=True)
 (target/'addon.xml').write_text('<addon id="'+addon+'" name="Disposable apt module registry" version="99.0.0" provider-name="Test"><extension point="xbmc.python.module" library="/usr/lib/python3/dist-packages"/></addon>')
script=root/'script.xcmate.picker90';script.mkdir(exist_ok=True)
(script/'addon.xml').write_text('<addon id="script.xcmate.picker90" name="Native picker observer" version="1.0.0" provider-name="Test"><requires><import addon="xbmc.python" version="3.0.1"/></requires><extension point="xbmc.python.script" library="main.py"/></addon>')
(script/'main.py').write_text("import runpy,traceback,gc,sys\nfrom pathlib import Path\nsys.path.insert(0,'/')\ntry:\n if Path('/root/picker90-cycle.txt').exists():\n  from picker_check90 import run\n  run(int(Path('/root/picker90-cycle.txt').read_text()))\n else:runpy.run_path('/picker90.py',run_name='__main__')\n gc.collect();Path('/root/picker90-returned').write_text('RETURNED')\nexcept Exception:Path('/root/picker90-error.txt').write_text(traceback.format_exc());raise\n")

# Disposable renderer-only sources; no credentials or real remote requests.
import sys
sys.path.insert(0,'/')
from six_rows438 import install as install_six438
install_six438()
