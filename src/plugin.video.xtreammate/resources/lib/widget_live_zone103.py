"""Move the verified native Live call without touching saved shortcuts."""
import xml.etree.ElementTree as ET

from widget_skin50 import edit, spans
from widget_six_consumer import own_groups, params

ZONE = 'XCMate103.LiveZone'
ANCHOR = b'<!-- XCMate103.LiveZone -->'
WRAPPER = b'<include name="XCMate103.LiveZone">'
CLOSE = b'</include>'


def presence(widget_id):
    if not widget_id.isascii() or not widget_id.isdigit():
        raise ValueError('HOME103_LIVE_UNVERIFIED')
    control = ET.Element('control', type='label', id='296904')
    ET.SubElement(control, 'left').text = '-100'
    ET.SubElement(control, 'width').text = '1'
    ET.SubElement(control, 'height').text = '1'
    ET.SubElement(control, 'visible').text = (
        f'Control.IsVisible({widget_id}) + Integer.IsGreater(Container({widget_id}).NumItems,0)'
    )
    return ET.tostring(control)


def inline_live(data):
    """Recover the original call when an older layout is restored or rebuilt."""
    if ANCHOR not in data and WRAPPER not in data:
        return data
    nodes = spans(data)
    fixed = [n for n in nodes if n['tag'] == 'include' and n['attrs'].get('name') == ZONE]
    if data.count(ANCHOR) != 1 or len(fixed) != 1:
        raise ValueError('HOME103_LIVE_UNVERIFIED')
    zone = fixed[0]
    children = zone['children']
    if not children or children[0]['attrs'].get('content') != 'XCMate50.LiveRow' or children[0]['start'] != zone['open']:
        raise ValueError('HOME103_LIVE_UNVERIFIED')
    end_live = children[0]['end'] + len(CLOSE)
    if data[end_live:zone['end']] not in (b'', presence(params(children[0]).get('widgetid', ''))):
        raise ValueError('HOME103_LIVE_UNVERIFIED')
    anchor = data.index(ANCHOR)
    return edit(data, [
        (anchor, anchor + len(ANCHOR), data[zone['open']:end_live]),
        (zone['start'], zone['end'] + len(CLOSE), b''),
    ])


def move_live(data):
    if ZONE.encode() in data:
        raise ValueError('HOME103_LIVE_UNVERIFIED')
    roots = own_groups(data)
    if len(roots) != 1:
        return data
    _, group = roots[0]
    live, values = group['live']
    nodes = spans(data)
    templates = [n for n in nodes if n['tag'] == 'include'
                 and n['attrs'].get('name') == 'skinshortcuts-template-Widgets']
    if len(templates) != 1 or live not in templates[0]['children']:
        return data
    if any(n['tag'] == 'control' and n['attrs'].get('id') == '296904' for n in nodes):
        raise ValueError('HOME103_LIVE_UNVERIFIED')
    marker = presence(values.get('widgetid', ''))
    start = live['start']
    stop = live['end'] + len(CLOSE)
    position = data.rfind(b'</includes>')
    return edit(data, [
        (start, stop, ANCHOR),
        (position, position, WRAPPER + data[start:stop] + marker + CLOSE),
    ])
