#!/usr/bin/env python3
"""Exact official 2.2.3 bytes -> reviewed candidate and native 2.1.0 template."""
import argparse
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET


def build(skin, output):
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'tests'))
    from xcmate050_fixture import Fixture50
    class Export(Fixture50, unittest.TestCase):
        pass
    fixture = Export()
    fixture.setUp()
    output.mkdir(parents=True, exist_ok=True)
    try:
        from widget_skin50 import patch, FILES, guard
        guard(skin)
        manifest = {'skin_version': '2.2.3', 'shortcuts': '2.1.0', 'files': {}, 'android': 'NOT_TESTED'}
        for name in FILES:
            before = (skin / name).read_bytes()
            after = patch(name, before)
            dest = output / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(after)
            manifest['files'][name] = dict(before=hashlib.sha256(before).hexdigest(), after=hashlib.sha256(after).hexdigest())
        # Unmodified native Skinshortcuts 2.1.0 expression/template compiler.
        compiler = fixture.native_reference().Template()
        controls = ET.parse(output / 'shortcuts/template.xml').getroot().find('other/controls')
        props = dict(id='2', submenuid='Home', multiWidgets='true')
        for i in range(1, 9):
            for name in ('widgetTarget','contentStyle','widgetPath','widgetName','widgetTags','widgetStyle','widgetSortBy','widgetSortOrder','widgetLimit','widgetInfoPanel','widgetFixedFocus'):
                props[name + str(i)] = ''
            props.update({k + str(i): v for k, v in dict(widgetStyle='poster', widgetFixedFocus='disabled', widgetTarget='videos', contentStyle='normal').items()})
        # Use the existing .59 native picker source byte-for-byte. This is
        # only the disposable host fixture, never a saved user binding edit.
        from widget_binding50 import source as saved_source
        props.update(widgetPath1=saved_source('live', 'fixture59'), widgetName1='Live-TV',
                     widgetPath2='plugin://plugin.video.xtreammate/?action=widget_recent_vod&pid=fixture59', widgetName2='Filme',
                     widgetPath3='plugin://plugin.video.xtreammate/?action=widget_recent_series&pid=fixture59', widgetName3='Serien')
        compiler.replaceElements(controls, None, None, [], props)
        generated = ET.Element('includes')
        widgets = ET.SubElement(generated, 'include', name='skinshortcuts-template-Widgets')
        for child in controls:
            widgets.append(copy.deepcopy(child))
        menu = ET.SubElement(generated, 'include', name='skinshortcuts-mainmenu')
        item = ET.SubElement(menu, 'item', id='2')
        ET.SubElement(item, 'label').text = 'Startseite · synthetic host only'
        ET.SubElement(item, 'onclick').text = 'ActivateWindow(Home)'
        for name, value in dict(submenuVisibility='10000', mainmenuid='2', labelID='10000').items():
            ET.SubElement(item, 'property', name=name).text = value
        for name in ('skinshortcuts-submenu', 'skinshortcuts-powermenu'):
            ET.SubElement(generated, 'include', name=name)
        ET.ElementTree(generated).write(output / 'xml/script-skinshortcuts-includes.xml', encoding='utf-8', xml_declaration=True)
        (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    finally:
        fixture.doCleanups()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skin', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build(args.skin.resolve(), args.output.resolve())
