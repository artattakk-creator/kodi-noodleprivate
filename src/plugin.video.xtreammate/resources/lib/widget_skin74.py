"""Optional exact .66 -> .74 focus-only adapter, via existing backup/consent.

Never called to write a skin on update. Native vertical navigation is restored;
item-local frames follow the actual focused layout, not a global row offset.
"""
import json
from pathlib import Path
import xml.etree.ElementTree as E

def previous_candidate(path,data):
    from widget_skin66 import candidate
    return candidate(path,data)

def candidate(path,data):
    from widget_skin50 import spans,edit
    from widget_transaction50 import read,sha
    known=json.loads(read(Path(__file__).parents[1]/'bingie74_previous.json'))['files']
    if sha(data)!=known.get(path):data=previous_candidate(path,data)
    nodes=spans(data);changes=[]
    if path=='xml/IncludesHomeWidgets.xml':
        layouts=[n for n in nodes if n['tag']=='focusedlayout']
        count=0
        for layout in layouts:
            groups=[n for n in layout['children'] if n['tag']=='control' and n['attrs'].get('type')=='group']
            for group in groups:
                width=next((n['text'] for n in group['children'] if n['tag']=='width'),None)
                height=next((n['text'] for n in group['children'] if n['tag']=='height'),None)
                if not width or not height:continue
                # Highlight retains its own native timed focus/animations.
                if any(n['tag']=='include' and 'Highlight' in n['text'] for n in group['children']):continue
                end=group['end']+len(b'</control>');element=E.fromstring(data[group['start']:end])
                for image in list(element.findall("control[@type='image']")):
                    includes=[n.text or '' for n in image.findall('include')]
                    texture=image.findtext('texture','')
                    if 'thumbsborder_focused' in includes or texture.endswith('/programme55/focus.png'):
                        element.remove(image)
                # One frame at the group's true origin. Fixed/global frames
                # cannot drift or remain selected after a different row gains focus.
                frame=E.SubElement(element,'control',type='image')
                for tag,value in (('description','XCMate74.ItemFocus'),('left','0'),('top','0'),('width',width),('height',height),
                        ('aspectratio','stretch'),('visible','Control.HasFocus($PARAM[widgetid])')):
                    E.SubElement(frame,tag).text=value
                E.SubElement(frame,'texture',border='9').text='special://home/addons/plugin.video.xtreammate/resources/media/programme55/focus.png'
                changes.append((group['start'],end,E.tostring(element,encoding='utf-8')));count+=1
        if not 4<=count<=32:raise ValueError('UNVERIFIED_FOCUS_REGIONS')
        for node in nodes:
            if node['tag']=='include' and node['attrs'].get('content')=='XCMate66.VerticalFocus':
                changes.append((node['start'],node['open'],data[node['start']:node['open']].replace(b'content="XCMate66.VerticalFocus"',b'content="SetFixedVerticalNavigationProps"')))
            if node['tag']=='include' and node['attrs'].get('name')=='XCMate66.VerticalFocus':
                changes.append((node['start'],node['end']+len(b'</include>'),b''))
    elif path=='xml/IncludesHomeBingie.xml':
        count=0
        for group in [n for n in nodes if n['tag']=='control' and n['attrs'].get('type')=='group']:
            if not any(n['tag']=='include' and (n['attrs'].get('content','') or n['text']).startswith('Bingie_Screens_Fixed_Focus_Frame') for n in group['children']):continue
            # Disable only the global Home frame for locally framed rows.
            # Native Highlight/hub frames keep their original conditions.
            for visible in [n for n in group['children'] if n['tag']=='visible' and ('ControlGroup(77777)' in n['text'] or 'XCMate.WidgetKind41' in n['text'])]:
                changes.append((visible['start'],visible['end']+len(b'</visible>'),b''))
            changes.append((group['open'],group['open'],b'<visible>!Window.IsActive(Home) | String.IsEqual(Window(Home).Property(widgetstyle),highlight)</visible>'));count+=1
        if not 2<=count<=8:raise ValueError('UNVERIFIED_FOCUS_REGIONS')
    return edit(data,changes) if changes else data

def previously_applied(skin):
    from widget_skin50 import guard,FILES
    from widget_transaction50 import read,sha
    try:
        known=json.loads(read(Path(__file__).parents[1]/'bingie74_previous.json'))['files']
        if all(sha(read(p))==known[name] for name,p in zip(FILES,guard(skin))):return True
    except (OSError,ValueError,KeyError):pass
    from widget_skin66 import previously_applied as legacy
    return legacy(skin)
