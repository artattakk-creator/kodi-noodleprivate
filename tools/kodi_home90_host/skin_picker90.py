"""Only fresh test registry/skin; no saved widget properties are synthesized."""
from pathlib import Path
import shutil
exec(compile(Path('/base_skin78.py').read_text(encoding='utf-8'),'/base_skin78.py','exec'),globals())
candidate90=Path('/candidate')
for p in candidate90.rglob('*.xml'):
 destination90=Path('/root/.kodi/addons/skin.titan.bingie.mod')/p.relative_to(candidate90)
 destination90.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,destination90)
exec(compile(Path('/setup_picker90.py').read_text(encoding='utf-8'),'/setup_picker90.py','exec'),globals())
