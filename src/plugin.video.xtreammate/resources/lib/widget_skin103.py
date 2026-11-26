"""Hash-verified fixed Hero and station rail for BINGIE Home."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from widget_skin50 import edit, spans
from widget_skin80 import _node, digest

WIDGETS = 'xml/IncludesHomeWidgets.xml'
HOME = 'xml/IncludesHomeBingie.xml'
VARIABLES = 'xml/IncludesVariables.xml'
BINGIE = 'xml/IncludesBingie.xml'
MARKER = b'XCMate103.Contract'
LIVE_ZONE = 'XCMate103.LiveZone'
LEFT = 130
WIDTH = 1760
HERO_HEIGHT = 640
LIVE_HEIGHT = 80
COVER_TOP = HERO_HEIGHT + LIVE_HEIGHT
MUSIC_DETAILS = '[!String.IsEmpty(ListItem.Artist) | !String.IsEmpty(ListItem.Album)]'
NO_HOME_ANIMATION = '![Window.IsActive(Home) + String.IsEqual(Skin.String(HomeLayout),bingie)]'
RECEIPTS = Path(__file__).parents[1] / 'bingie103_layout.json'


def set_values(node, **values):
    for tag, value in values.items():
        child = node.find(tag)
        if child is None:
            child = ET.SubElement(node, tag)
        child.text = str(value)


def hero(node):
    group = node.find('control')
    set_values(group, visible='Window.IsActive(Home) + [ControlGroup(77777).HasFocus() | '
               'ControlGroup(296903).HasFocus()] + !$EXP[IsMainMenuOpened]')
    for ident in ('296751', '296786', '296886', '296888'):
        set_values(group.find(f"control[@id='{ident}']"), height=HERO_HEIGHT)
    title = group.find(".//control[@id='296781']")
    set_values(title, width=900, height=106, autoscroll='false')
    metadata = group.find(".//control[@id='296753']")
    set_values(metadata, top=174, label='$VAR[XCMate103.MediaFacts]')
    media_label = group.find(".//control[@id='296754']")
    # The native title textbox already displays the selected item's full label.
    media_label.find('visible').text = 'false'


def live_list(node):
    control = node.find('control')
    control.set('type', 'list')
    control.remove(control.find('focusposition'))
    set_values(control, left=LEFT, width=WIDTH, height=LIVE_HEIGHT)
    for layout in control.findall('itemlayout') + control.findall('focusedlayout'):
        label = layout.find("control[@type='label']")
        set_values(label, scroll='true')


def media_wrapper(node):
    for group in node.findall("control[@type='group']"):
        set_values(group, left=0)


def native_wrapper(node):
    group = node.find("control[@type='group']")
    # Native poster rows have 330px covers. Keeping the 440px wrapper makes
    # Kodi align its oversized bottom to the 360px clip and cut off the top.
    # Hub windows keep the original dimensions.
    for tag, home in (('left', 0), ('height', 1080 - COVER_TOP)):
        original = group.find(tag)
        group.remove(original)
        for condition, value in (('Window.IsActive(Home)', home),
                                 ('!Window.IsActive(Home)', original.text)):
            call = ET.SubElement(group, 'include', content=tag, condition=condition)
            ET.SubElement(call, 'param', name=tag, value=str(value))


def poster_cards(node):
    for layout in node.findall('itemlayout') + node.findall('focusedlayout'):
        label = layout.find("control[@type='label']")
        set_values(label, width=136)
        if layout.tag == 'focusedlayout':
            set_values(label, scroll='true')
            frame = next(n for n in layout.findall("control[@type='image']")
                         if n.findtext('texture', '').endswith('/rail_focus81.png'))
            # Bound the frame to the card inside its own native item origin.
            set_values(frame, left=0, top=0, width=120, height=180)


def motion(node):
    for animation in node.findall('animation'):
        animation.set('condition', NO_HOME_ANIMATION + ' + [' + animation.get('condition') + ']')


def cover_viewport(node):
    for tag in ('top', 'height'):
        node.remove(node.find(tag))
    for condition, top, height in (('Window.IsActive(Home)', COVER_TOP, 1080 - COVER_TOP),
                                   ('!Window.IsActive(Home)', HERO_HEIGHT, 420)):
        # Includes resolve the correct dimensions for each native window.
        include = ET.SubElement(node, 'include', content='XCMate103.ViewportDimensions',
                                condition=condition)
        ET.SubElement(include, 'param', name='top', value=str(top))
        ET.SubElement(include, 'param', name='height', value=str(height))
    set_values(node, scrolltime=150)


def fixed_zone():
    group = ET.Element('control', type='group', id='296903')
    set_values(group, top=HERO_HEIGHT, width=1920, height=LIVE_HEIGHT,
               visible='Window.IsActive(Home)')
    background = ET.SubElement(group, 'control', type='image')
    set_values(background, left=LEFT, top=0, width=WIDTH, height=LIVE_HEIGHT,
               texture='colors/color_white.png', colordiffuse='FF101B2B',
               aspectratio='stretch')
    ET.SubElement(group, 'include', condition='Window.IsActive(Home)').text = LIVE_ZONE
    return group


def dimensions():
    include = ET.Element('include', name='XCMate103.ViewportDimensions')
    definition = ET.SubElement(include, 'definition')
    set_values(definition, top='$PARAM[top]', height='$PARAM[height]')
    return include


def variables():
    marker = ET.Element('variable', name=MARKER.decode())
    ET.SubElement(marker, 'value').text = 'READY'
    facts = ET.Element('variable', name='XCMate103.MediaFacts')
    ET.SubElement(facts, 'value', condition='!String.IsEmpty(ListItem.Artist) + '
                  '!String.IsEmpty(ListItem.Album)').text = '$INFO[ListItem.Artist]  ·  $INFO[ListItem.Album]'
    ET.SubElement(facts, 'value', condition=MUSIC_DETAILS).text = '$INFO[ListItem.Artist]$INFO[ListItem.Album]'
    ET.SubElement(facts, 'value').text = '$INFO[ListItem.Year]   $INFO[ListItem.Genre]'
    image = ET.Element('variable', name='XCMate103.Image')
    for field in ('fanart', 'landscape', 'poster', 'thumb'):
        info = f'ListItem.Art({field})'
        ET.SubElement(image, 'value', condition='!String.IsEmpty(' + info + ')').text = '$INFO[' + info + ']'
    cover = ET.Element('variable', name='XCMate103.MusicCover')
    for field in ('poster', 'thumb'):
        info = f'ListItem.Art({field})'
        ET.SubElement(cover, 'value', condition='!String.IsEmpty(' + info + ')').text = '$INFO[' + info + ']'
    return marker, facts, image, cover


def hero_image(node):
    standard = node.find('control')
    live_condition = 'String.IsEqual(ListItem.Property(XCMate.WidgetKind41),live)'
    from widget_logo84 import condition as station_logo

    landscape = '[!' + MUSIC_DETAILS + ' + [!String.IsEmpty(ListItem.Art(fanart)) | '
    landscape += '!String.IsEmpty(ListItem.Art(landscape))]]'
    main = standard.find("control[@id='296751']")
    cover = standard.find("control[@id='296783']")
    set_values(main, texture='$VAR[XCMate103.HeroImage]',
               visible='[' + live_condition + ' + [' + main.findtext('visible') + '] + ![' + station_logo() + ']] | [!' +
               live_condition + ' + ' + landscape + ']')
    # Keep the verified Live poster guard and use contained artwork for audio.
    set_values(cover, texture='$VAR[XCMate103.HeroImage]',
               visible=cover.findtext('visible').replace('String.IsEmpty(ListItem.Art(fanart))',
                                                        '!' + landscape))


def hero_selector():
    node = ET.Element('variable', name='XCMate103.HeroImage')
    ET.SubElement(node, 'value', condition='String.IsEqual(ListItem.Property(XCMate.WidgetKind41),live)').text = '$VAR[XCMate75.Image]'
    ET.SubElement(node, 'value', condition=MUSIC_DETAILS).text = '$VAR[XCMate103.MusicCover]'
    ET.SubElement(node, 'value').text = '$VAR[XCMate103.Image]'
    return node


def update_hero(node):
    hero(node)
    hero_image(node)


TARGETS = (
    (WIDGETS, 'include', 'name', 'XCMate50.Hero', update_hero),
    (WIDGETS, 'include', 'name', 'XCMate75.NativeLiveRow', live_list),
    (WIDGETS, 'include', 'name', 'XCMate80.MediaRow', media_wrapper),
    (WIDGETS, 'include', 'name', 'XCMate.SixRows.Row', media_wrapper),
    (WIDGETS, 'include', 'name', 'XCMate81.PosterRow', poster_cards),
    (WIDGETS, 'include', 'name', 'XCMate.SixRows.Cards', poster_cards),
    (WIDGETS, 'include', 'name', 'widget_base', native_wrapper),
    (BINGIE, 'include', 'name', 'Fixed_Focus_Navigation', motion),
    (HOME, 'control', 'id', '77777', cover_viewport),
)


def upgrade(files):
    """Replace only the reviewed stock/owned geometry on an approved plan."""
    from widget_skin78 import _append

    current = MARKER in files[VARIABLES]
    phase = 'after' if current else 'before'
    receipts = json.loads(RECEIPTS.read_text(encoding='utf-8'))
    changes = {}
    for name, tag, attr, key, transform in TARGETS:
        span, end, node = _node(files[name], tag, attr, key)
        if digest(node) != receipts[key][phase]:
            raise ValueError('HOME103_GEOMETRY_UNVERIFIED')
        if not current:
            transform(node)
            changes.setdefault(name, []).append((span['start'], end, ET.tostring(node)))
    result = dict(files)
    if not current:
        for name, patches in changes.items():
            result[name] = edit(files[name], patches)
        source = result[HOME]
        hooks = [n for n in spans(source) if n['tag'] == 'include' and n['text'] == 'XCMate50.Hero']
        if len(hooks) != 1:
            raise ValueError('HOME103_GEOMETRY_UNVERIFIED')
        position = hooks[0]['end'] + len(b'</include>')
        result[HOME] = _append(edit(source, [(position, position, ET.tostring(fixed_zone()))]),
                               b'</includes>', ET.tostring(dimensions()))
        result[VARIABLES] = _append(result[VARIABLES], b'</includes>',
                                    b'\n'.join(ET.tostring(n) for n in (*variables(), hero_selector())))
    verify_hooks(result)
    return result


def verify_hooks(files):
    from widget_skin78 import parse, verify

    verify(files)
    home = parse(files[HOME])
    parent = home.find(".//control[@id='9000']")
    fixed = parent.findall("control[@id='296903']")
    cover = parent.find("control[@id='77777']")
    dims = home.findall("include[@name='XCMate103.ViewportDimensions']")
    if (len(fixed) != 1 or cover is None or list(parent).index(fixed[0]) < list(parent).index(cover)
            or digest(fixed[0]) != digest(fixed_zone()) or len(dims) != 1
            or digest(dims[0]) != digest(dimensions())):
        raise ValueError('HOME103_GEOMETRY_UNVERIFIED')
    registry = parse(files[VARIABLES])
    for expected in (*variables(), hero_selector()):
        nodes = registry.findall(f"variable[@name='{expected.get('name')}']")
        if len(nodes) != 1 or digest(nodes[0]) != digest(expected):
            raise ValueError('HOME103_GEOMETRY_UNVERIFIED')


def skin_files(skin):
    from widget_skin78 import FILES
    from widget_transaction50 import read

    return {name: read(Path(skin) / name) for name in FILES}


def installed(skin):
    try:
        files = skin_files(skin)
        return MARKER in files[VARIABLES] and upgrade(files) == files
    except (OSError, ValueError, KeyError, ET.ParseError):
        return False


def previous_owned(skin):
    from widget_skin78 import build

    try:
        files = skin_files(skin)
        if MARKER in files[VARIABLES] or b'XCMate88.Contract' not in files[VARIABLES]:
            return False
        return bool(upgrade(build(files)))
    except (OSError, ValueError, KeyError, ET.ParseError):
        return False
