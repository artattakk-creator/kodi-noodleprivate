"""Move the verified native Live call without touching saved shortcuts."""
from widget_skin50 import edit, spans
from widget_six_consumer import own_groups

ZONE = 'XCMate103.LiveZone'
ANCHOR = b'<!-- XCMate103.LiveZone -->'
WRAPPER = b'<include name="XCMate103.LiveZone">'
CLOSE = b'</include>'


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
    if (len(children) != 1 or children[0]['attrs'].get('content') != 'XCMate50.LiveRow'
            or children[0]['start'] != zone['open']
            or children[0]['end'] + len(CLOSE) != zone['end']):
        raise ValueError('HOME103_LIVE_UNVERIFIED')
    anchor = data.index(ANCHOR)
    return edit(data, [
        (anchor, anchor + len(ANCHOR), data[zone['open']:zone['end']]),
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
    templates = [n for n in spans(data) if n['tag'] == 'include'
                 and n['attrs'].get('name') == 'skinshortcuts-template-Widgets']
    if len(templates) != 1 or live not in templates[0]['children']:
        return data
    if not values.get('widgetid', '').isdigit():
        raise ValueError('HOME103_LIVE_UNVERIFIED')
    start = live['start']
    stop = live['end'] + len(CLOSE)
    position = data.rfind(b'</includes>')
    return edit(data, [
        (start, stop, ANCHOR),
        (position, position, WRAPPER + data[start:stop] + CLOSE),
    ])
