"""Explicitly preapproved candidate skin in the disposable fixture only."""
from pathlib import Path
import shutil
exec(compile(Path('/base_skin78.py').read_text(),'/base_skin78.py','exec'),globals())
# The existing general native CI separately tests user opt-in and rollback.
exec(compile(Path('/skin78.py').read_text().replace("exec(compile(Path('/base_skin78.py').read_text(encoding='utf-8'),'/base_skin78.py','exec'),globals())",''),'/skin78.py','exec'),globals())
for path in Path('/candidate/xml').glob('*.xml'):
 shutil.copyfile(path,Path('/root/.kodi/addons/skin.titan.bingie.mod/xml')/path.name)
