"""Only fresh test registry/skin; no saved widget properties are synthesized."""
from pathlib import Path
import shutil
exec(compile(Path('/base_skin78.py').read_text(encoding='utf-8'),'/base_skin78.py','exec'),globals())
candidate90=Path('/candidate')
for p in candidate90.rglob('*.xml'):
 destination90=Path('/root/.kodi/addons/skin.titan.bingie.mod')/p.relative_to(candidate90)
 destination90.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,destination90)
exec(compile(Path('/setup_picker90.py').read_text(encoding='utf-8'),'/setup_picker90.py','exec'),globals())

# Read-only parameter witnesses in the disposable skin: no content, action,
# visibility or layout replacement. Transparent labels expose Kodi's actual
# include substitutions, which source-file parsing alone cannot prove.
import xml.etree.ElementTree as E
witness_path90=Path('/root/.kodi/addons/skin.titan.bingie.mod/xml/IncludesHomeWidgets.xml')
witness_tree90=E.parse(witness_path90)
for owner90,prefix90 in (('XCMate80.MediaRow','91'),('XCMate80.NativeMediaBase','92'),('XCMate80.MediaNormal','93')):
 node90=witness_tree90.getroot().find("include[@name='"+owner90+"']")
 label90=E.SubElement(node90,'control',type='label',id=prefix90+'$PARAM[widgetid]')
 for field90,value90 in (('width','1'),('height','1'),('font','Reg18'),('textcolor','00FFFFFF'),('visible','true'),('label','TYPE=$PARAM[containerType];ID=$PARAM[widgetid];MENU=$PARAM[submenuid];VIS=$PARAM[visibility]')):E.SubElement(label90,field90).text=value90
witness_tree90.write(witness_path90,encoding='utf-8',xml_declaration=True)
