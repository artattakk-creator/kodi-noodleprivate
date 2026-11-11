"""Only fresh test registry/skin; no saved widget properties are synthesized."""
from pathlib import Path
import shutil
exec(compile(Path('/base_skin78.py').read_text(encoding='utf-8'),'/base_skin78.py','exec'),globals())
for p in Path('/candidate/xml').glob('*.xml'):shutil.copyfile(p,Path('/root/.kodi/addons/skin.titan.bingie.mod/xml')/p.name)
exec(compile(Path('/setup_picker90.py').read_text(encoding='utf-8'),'/setup_picker90.py','exec'),globals())
