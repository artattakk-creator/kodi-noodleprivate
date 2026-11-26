"""Load the pinned production BINGIE includes into a disposable Kodi profile."""
from pathlib import Path
import runpy
import shutil
import sys
import xml.etree.ElementTree as ET

root = Path('/root/.kodi')
addon = root / 'addons/plugin.video.xtreammate'
skin = root / 'addons/skin.titan.bingie.mod'
shutil.copytree('/skin', skin)
sys.path.insert(0, str(addon / 'resources/lib'))
from widget_reload78 import candidate
from widget_skin78 import FILES, build103

for name, body in build103({name: (skin / name).read_bytes() for name in FILES}).items():
    (skin / name).write_bytes(body)
generated = Path('/candidate/xml/script-skinshortcuts-includes.xml').read_bytes()
(skin / 'xml/script-skinshortcuts-includes.xml').write_bytes(candidate(generated, layout80=True, fixed_live=True))
runpy.run_path('/skin_fixture66.py')
# The template was compiled by the normal BINGIE replay tool above.
(root / 'addons/script.skinshortcuts/default.py').write_text('pass\n')

descriptor = addon / 'addon.xml'
tree = ET.parse(descriptor)
for node in list(tree.getroot().findall('extension')):
    if node.get('point') == 'xbmc.service':
        tree.getroot().remove(node)
    if node.get('point') == 'xbmc.python.pluginsource':
        node.set('library', 'public_home_directory.py')
tree.write(descriptor, encoding='utf-8', xml_declaration=True)
shutil.copyfile('/harness/home_directory.py', addon / 'public_home_directory.py')
