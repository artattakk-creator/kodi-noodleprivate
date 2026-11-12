"""Only fresh test registry/skin; no saved widget properties are synthesized."""
from pathlib import Path
import shutil
exec(compile(Path('/base_skin78.py').read_text(encoding='utf-8'),'/base_skin78.py','exec'),globals())
candidate90=Path('/candidate')
for p in candidate90.rglob('*.xml'):
 destination90=Path('/root/.kodi/addons/skin.titan.bingie.mod')/p.relative_to(candidate90)
 destination90.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,destination90)
# A separate contract profile models the reported first-menu container IDs.
# Only fresh fixture defaults are reordered, before upstream SkinShortcuts
# creates any saved menu. Never alter an existing user's menu/properties.
if __import__('os').environ.get('XCMATE_CLOCK437')=='true':
 import xml.etree.ElementTree as E
 path437=Path('/root/.kodi/addons/skin.titan.bingie.mod/shortcuts/mainmenu.DATA.xml')
 menu437=E.parse(path437);root437=menu437.getroot()
 homes437=[n for n in root437.findall('shortcut') if n.findtext('label')=='10000']
 assert len(homes437)==1,'CLOCK437_DEFAULT_HOME_NOT_UNIQUE'
 root437.remove(homes437[0]);root437.insert(0,homes437[0]);menu437.write(path437,encoding='utf-8',xml_declaration=True)
exec(compile(Path('/setup_picker90.py').read_text(encoding='utf-8'),'/setup_picker90.py','exec'),globals())
# This disposable profile suppresses BINGIE's startup/settings helper. Reuse
# its exact original spinner default rather than leaving the native diffuse
# colour empty/transparent. Never apply this fixture to an installed profile.
import xml.etree.ElementTree as E
defaults438=E.parse(Path('/root/.kodi/addons/skin.titan.bingie.mod/xml/IncludesDefaultSkinSettings.xml'))
assert any((n.text or '')=='Skin.SetString(WidgetSpinnerTexture.Color,ffffffff)' for n in defaults438.iter('onload'))
settings438=Path('/root/.kodi/userdata/addon_data/skin.titan.bingie.mod/settings.xml')
tree438=E.parse(settings438)
if tree438.getroot().find("setting[@id='WidgetSpinnerTexture.Color']") is None:
 E.SubElement(tree438.getroot(),'setting',id='WidgetSpinnerTexture.Color',type='string').text='ffffffff'
 tree438.write(settings438,encoding='utf-8',xml_declaration=True)

