"""Disposable host registry/settings only. Production skin XML is unchanged."""
from pathlib import Path
import xml.etree.ElementTree as E

root = Path('/root/.kodi')
skin = root / 'addons/skin.titan.bingie.mod'
descriptor = skin / 'addon.xml'
tree = E.parse(descriptor)
requires = tree.getroot().find('requires')
dependencies = [n.get('addon') for n in requires if n.get('addon') != 'xbmc.gui']
for node in list(requires):
    if node.get('addon') != 'xbmc.gui':
        requires.remove(node)
tree.write(descriptor, encoding='utf-8', xml_declaration=True)
# External helper startup is deliberately absent in this isolated renderer.
# Its original includes, layouts, fonts, textures and native Home remain real.
for name in dependencies:
    if name.startswith('script.'):
        target = root / 'addons' / name
        target.mkdir(exist_ok=True)
        (target / 'addon.xml').write_text('<addon id="'+name+'" name="Host no-op dependency" version="99.0.0" provider-name="Test"><requires><import addon="xbmc.python" version="3.0.1"/></requires><extension point="xbmc.python.script" library="default.py"/><extension point="xbmc.addon.metadata"><summary lang="en_GB">Synthetic host only</summary><description lang="en_GB">No network</description><platform>all</platform><license>GPL-2.0-only</license></extension></addon>')
        (target / 'default.py').write_text('pass\n')
settings = root / 'userdata/addon_data/skin.titan.bingie.mod'
settings.mkdir(parents=True, exist_ok=True)
data = E.Element('settings', version='2')
for name, value in dict(splash_screen='none', HomeLayout='bingie', widgetstyle='poster', WidgetsGlobalLimit='100', BingieFirstStartupDone='true', BingieSecondStartupDone='true', HomeMenuDefaults46='true', DisableSpotlightContent='true', DisableDummySpotlight='true', disable_trailers='true').items():
    E.SubElement(data, 'setting', id=name, type='bool' if value in ('true', 'false') else 'string').text = value
E.ElementTree(data).write(settings / 'settings.xml')

# Isolated builder: pinned native Template output, installed AFTER approval.
builder=root/'addons/script.skinshortcuts'
tree=E.parse(builder/'addon.xml');tree.getroot().set('version','2.1.0');tree.write(builder/'addon.xml')
(builder/'default.py').write_text("from pathlib import Path\nimport shutil,xbmc\nif 'XCMate50.LiveRow' not in Path('/root/.kodi/addons/skin.titan.bingie.mod/xml/IncludesHomeWidgets.xml').read_text(encoding='utf-8'): raise SystemExit\nPath('/root/builder61-called').write_text('after-explicit-menu-approval')\nshutil.copyfile('/candidate/xml/script-skinshortcuts-includes.xml','/root/.kodi/addons/skin.titan.bingie.mod/xml/script-skinshortcuts-includes.xml')\nxbmc.executebuiltin('ReloadSkin()')\n")
