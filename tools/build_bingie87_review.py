#!/usr/bin/env python3
"""Pinned 2.2.3 full graph -> current guarded adapter and native template."""
import argparse
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET


def build(skin, output):
    sys.path.insert(0,str(Path(__file__).parent/'kodi_home87_host'))
    from spec87 import FOREIGN,uri
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'tests'))
    from xcmate050_fixture import Fixture50
    class Export(Fixture50, unittest.TestCase):
        pass
    fixture = Export()
    fixture.setUp()
    output.mkdir(parents=True, exist_ok=True)
    try:
        from widget_skin50 import guard
        import widget_skin78
        FILES=widget_skin78.FILES
        guard(skin)
        candidate84=widget_skin78.build({name:(skin/name).read_bytes() for name in FILES})
        manifest = {'skin_version': '2.2.3', 'shortcuts': '2.1.0', 'files': {}, 'android': 'NOT_TESTED'}
        for name in FILES:
            before = (skin / name).read_bytes()
            after = candidate84[name]
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
        for i in range(5):
            name87,addon87,content87,target87,color87=FOREIGN[i]
            props.update({k+str(i+4):v for k,v in dict(widgetPath=uri(i),widgetName=name87,widgetStyle='poster',widgetTarget=target87).items()})
        # BINGIE 2.2.3 has no widget_layout_square. Albums use its native
        # poster style; verify the chosen layout exists in the pinned bytes.
        layouts={node.get('name') for node in ET.parse(output/'xml/IncludesHomeWidgets.xml').getroot().findall('include')}
        assert all('widget_layout_'+props['widgetStyle'+str(i)] in layouts for i in range(4,9))
        compiler.replaceElements(controls, None, None, [], props)
        generated = ET.Element('includes')
        widgets = ET.SubElement(generated, 'include', name='skinshortcuts-template-Widgets')
        for child in controls:
            widgets.append(copy.deepcopy(child))
        # A second existing Home menu exercises the native eight-slot layout
        # without imposing a new global limit or suppressing any saved row.
        controls87=ET.parse(output / 'shortcuts/template.xml').getroot().find('other/controls')
        props87=dict(props,id='3')
        for i,(name87,addon87,content87,target87,color87) in enumerate(FOREIGN,1):
            props87.update({k+str(i):v for k,v in dict(widgetPath=uri(i-1),widgetName=name87,widgetStyle='poster',widgetTarget=target87).items()})
        compiler.replaceElements(controls87,None,None,[],props87)
        for child in controls87:widgets.append(copy.deepcopy(child))
        menu = ET.SubElement(generated, 'include', name='skinshortcuts-mainmenu')
        item = ET.SubElement(menu, 'item', id='2')
        ET.SubElement(item, 'label').text = 'Startseite · synthetic host only'
        ET.SubElement(item, 'onclick').text = 'ActivateWindow(Home)'
        for name, value in dict(submenuVisibility='10000', mainmenuid='2', labelID='10000').items():
            ET.SubElement(item, 'property', name=name).text = value
        item87=ET.SubElement(menu,'item',id='3');ET.SubElement(item87,'label').text='Weitere Nutzerwidgets'
        ET.SubElement(item87,'onclick').text='ActivateWindow(Home)'
        for name,value in dict(submenuVisibility='10001',mainmenuid='3',labelID='10001').items():ET.SubElement(item87,'property',name=name).text=value
        for name in ('skinshortcuts-submenu', 'skinshortcuts-powermenu'):
            ET.SubElement(generated, 'include', name=name)
        ET.ElementTree(generated).write(output / 'xml/script-skinshortcuts-includes.xml', encoding='utf-8', xml_declaration=True)
        manifest['foreign_widget_definitions']=13
        manifest['foreign_plugin_sources']=sorted({v[1] for v in FOREIGN})
        (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    finally:
        fixture.doCleanups()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skin', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build(args.skin.resolve(), args.output.resolve())
