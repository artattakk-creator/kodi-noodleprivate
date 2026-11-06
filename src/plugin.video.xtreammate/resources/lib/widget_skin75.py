"""Exact reviewed .74 adapter -> fixed left-image/right-table Home.

Only invoked through the existing explicit preview/backup/consent transaction.
Bindings, generated SkinShortcuts and Space Blue settings are never rewritten.
Unknown XML is blocked. Native widgets/onclicks remain the actual data receiver.
"""
import json
from pathlib import Path
import xml.etree.ElementTree as E

def navigation_candidate(data):
    from widget_skin77 import existing_navigation
    if existing_navigation(data):return data
    from widget_transaction50 import sha
    from widget_skin50 import spans,edit
    if sha(data)!='ab30a92b13a80123cf7ac2a6a24f4b3f2e9669c3a2da769666868cc60649077b':raise ValueError('UNVERIFIED_NAVIGATION_SKIN')
    # Pinned upstream 2.2.3 contains a nested comment at line 3252. Kodi's
    # parser tolerates it, Expat does not. Repair that exact inert comment;
    # original bytes remain in the transaction backup for a full restore.
    data=data.replace(b'<!-- <!-- <param name="top" default="690"',b'<!-- <param name="top" default="690"')
    nodes=spans(data);matches=[n for n in nodes if n['tag']=='include' and n['attrs'].get('name')=='Bingie_Menu_Icon_Defs']
    if len(matches)!=1:raise ValueError('UNVERIFIED_NAVIGATION_SKIN')
    inc=E.Element('include',name='Bingie_Menu_Icon_Defs')
    for tag,value in (('width','36'),('height','36'),('aspectratio','keep'),('texture','$VAR[XCMate75.MenuIcon]')):E.SubElement(inc,tag).text=value
    var=E.Element('variable',name='XCMate75.MenuIcon')
    for ids,asset in ((('10000','home','Startseite'),'home-2'),(('livetv','pvr','Live-TV'),'device-tv'),(('movies','Filme'),'movie'),(('tvshows','series','Serien'),'playlist'),(('search','Suche'),'search'),(('settings','Einstellungen'),'settings'),(('favorites','favourites','Favoriten'),'heart')):
        condition=' | '.join('String.IsEqual(ListItem.Property(labelID),'+value+')' for value in ids)
        condition+=' | '+' | '.join('String.IsEqual(ListItem.Label,'+value+')' for value in ids)
        E.SubElement(var,'value',condition=condition).text='special://home/addons/plugin.video.xtreammate/resources/media/navigation/'+asset+'-normal.png'
    E.SubElement(var,'value').text='$INFO[ListItem.Icon]'
    node=matches[0];end=data.rfind(b'</includes>')
    return edit(data,[(node['start'],node['end']+len(b'</include>'),E.tostring(inc,encoding='utf-8')),(end,end,E.tostring(var,encoding='utf-8'))])

def extra(skin):
    from widget_transaction50 import read
    root=Path(skin).resolve();path=root/'xml/IncludesBingie.xml'
    if not path.exists():return []  # Historical four-file host fixture.
    if path.is_symlink() or root not in path.resolve().parents:raise ValueError('UNSAFE_TARGET')
    return [(path,navigation_candidate(read(path)))]

def previous_candidate(path,data):
    from widget_skin74 import candidate
    return candidate(path,data)

def candidate(path,data):
    from widget_skin50 import spans,edit
    from widget_transaction50 import read,sha
    known=json.loads(read(Path(__file__).parents[1]/'bingie75_previous.json'))['files']
    if sha(data)!=known.get(path):data=previous_candidate(path,data)
    nodes=spans(data);changes=[]
    if path=='xml/IncludesHomeWidgets.xml':
        definitions=E.fromstring(read(Path(__file__).parents[1]/'bingie75/IncludesXCMate75.xml'))
        hero=next(n for n in nodes if n['tag']=='include' and n['attrs'].get('name')=='XCMate50.Hero')
        changes.append((hero['start'],hero['end']+len(b'</include>'),E.tostring(definitions.find("include[@name='XCMate50.Hero']"),encoding='utf-8')))
        end=data.rfind(b'</includes>')
        extra=b'\n'.join(E.tostring(n,encoding='utf-8') for n in definitions if n.get('name')!='XCMate50.Hero')
        changes.append((end,end,extra))
        # Keep native template content names and every saved path. Wrap the
        # existing definitions rather than replacing the shortcut vocabulary.
        for name,native in (('widget_base','XCMate75.NativeMediaBase'),('XCMate50.LiveRow','XCMate75.NativeLiveRow')):
            node=next(n for n in nodes if n['tag']=='include' and n['attrs'].get('name')==name)
            original=E.fromstring(data[node['start']:node['end']+len(b'</include>')]);original.set('name',native)
            if name=='widget_base':
                for call in original.findall('include'):
                    for direction in ('up75','down75'):E.SubElement(call,'param',name=direction,value='$PARAM['+direction+']')
            else:
                control=original.find('control')
                for direction in ('up','down'):E.SubElement(control,'on'+direction).text='$PARAM['+direction+'75]'
                # Kodi does not expose a texture-decoded callback here. Keep
                # an honest sender caption even if an approved logo later 404s.
                for caption in original.findall(".//control[@type='label']"):
                    for child in list(caption.findall('visible')):caption.remove(child)
                    caption.find('top').text='50';caption.find('height').text='20'
                for image in original.findall(".//control[@type='image']"):
                    if image.findtext('texture')=='$INFO[ListItem.Property(XCMate.ProgrammeLogo46)]':
                        image.find('top').text='8';image.find('height').text='36'
            wrapper=E.Element('include',name=name);group=E.SubElement(wrapper,'control',type='group',id='75$PARAM[widgetid]')
            E.SubElement(group,'height').text='440';E.SubElement(group,'width').text='1920'
            if name=='widget_base':E.SubElement(group,'left').text='140'
            E.SubElement(group,'visible').text='$PARAM[visibility] + [String.IsEqual(Container(900).ListItem.Property(submenuVisibility),$PARAM[submenuid]) | Skin.HasSetting(ShowAllWidgets)]'
            call=E.SubElement(group,'include',content=native)
            for param in ('containerType','contentStyle','widgetid','widgetName','submenuid','widgetTags','widgetTarget','widgetPath','widgetSortBy','widgetSortOrder','widgetLimit','widgetStyle','visibility','multiRows','up75','down75'):
                E.SubElement(call,'param',name=param,value='$PARAM['+param+']')
            changes.append((node['start'],node['end']+len(b'</include>'),E.tostring(original,encoding='utf-8')+E.tostring(wrapper,encoding='utf-8')))
        normal=next(n for n in nodes if n['tag']=='include' and n['attrs'].get('name')=='widget_base_normal')
        control=next(n for n in normal['children'] if n['tag']=='control')
        changes.append((control['open'],control['open'],b'<onup>$PARAM[up75]</onup><ondown>$PARAM[down75]</ondown>'))
        for call in nodes:
            if call['tag']=='include' and call['attrs'].get('content')=='Fixed_Focus_Navigation_Factory':
                element=E.fromstring(data[call['start']:call['end']+len(b'</include>')])
                condition=element.get('condition')
                element.set('condition','!Window.IsActive(Home)'+(' + ['+condition+']' if condition else ''))
                changes.append((call['start'],call['end']+len(b'</include>'),E.tostring(element,encoding='utf-8')))
        # Headers otherwise occupy a second grouplist slot and leak across
        # the fixed viewport. The selected title belongs in the right panel.
        for node in nodes:
            if node['tag']=='include' and node['attrs'].get('name')=='widget_header_multi':
                group=next(n for n in node['children'] if n['tag']=='control')
                changes.append((group['open'],group['open'],b'<visible>!Window.IsActive(Home)</visible>'))
    elif path=='xml/IncludesHomeBingie.xml':
        matches=[n for n in nodes if n['tag']=='control' and n['attrs'].get('id')=='77777']
        if len(matches)!=1:raise ValueError('UNVERIFIED_RAIL_VIEWPORT')
        node=matches[0];end=node['end']+len(b'</control>');rail=E.fromstring(data[node['start']:end])
        for child in list(rail):
            if child.tag in ('top','bottom','height','itemgap','animation') or child.tag=='include' and ('Fixed_Focus_' in (child.text or '') or child.get('content')=='BingieSpotlightWidget'):
                rail.remove(child)
        for tag,value in (('top','620'),('height','440'),('itemgap','0'),('scrolltime','0')):E.SubElement(rail,tag).text=value
        changes.append((node['start'],end,E.tostring(rail,encoding='utf-8')))
        # Native caption layers use scrolling animations. The new table owns
        # all Home captions, including provider/foreign movie widgets.
        parent=next(n for n in nodes if n['tag']=='control' and n['attrs'].get('id')=='9000')
        details=[n for n in parent['children'] if n['tag']=='control' and any(c['tag']=='width' and c['text']=='1920' for c in n['children']) and any(c['tag']=='height' and c['text']=='525' for c in n['children'])]
        if len(details)!=1:raise ValueError('UNVERIFIED_CAPTION_REGION')
        changes.append((details[0]['open'],details[0]['open'],b'<visible>!Window.IsActive(Home)</visible>'))
        for node in nodes:
            if node['tag']=='control' and node['attrs'].get('type')=='grouplist' and any(n['tag']=='include' and n['attrs'].get('content')=='Bingie_Headline_Item' for n in node['children']):
                changes.append((node['open'],node['open'],b'<visible>!Window.IsActive(Home)</visible>'))
    elif path=='shortcuts/template.xml':
        import re
        for node in nodes:
            if node['tag']!='include' or node['attrs'].get('content') not in ('widget_base','XCMate50.LiveRow'):continue
            ident=next((n['attrs'].get('value','') for n in node['children'] if n['tag']=='param' and n['attrs'].get('name')=='widgetid'),'')
            match=re.fullmatch(r'\$SKINSHORTCUTS\[id\]5([1-8])0',ident)
            if not match:raise ValueError('UNVERIFIED_WIDGET_NAVIGATION')
            number=int(match[1]);extra=E.Element('params')
            for name,indices in (('up75',range(number-1,0,-1)),('down75',range(number+1,9))):
                expression=''.join("id+'5"+str(i)+"0' if widgetPath"+str(i)+" else " for i in indices)
                expression+="'900'" if name=='up75' else "id+'5"+str(number)+"0'"
                E.SubElement(extra,'param',name=name,value='$PYTHON['+expression+']')
            changes.append((node['end'],node['end'],b''.join(E.tostring(n,encoding='utf-8') for n in extra)))
    return edit(data,changes) if changes else data

def previously_applied(skin):
    from widget_skin50 import guard,FILES
    from widget_transaction50 import read,sha
    try:
        known=json.loads(read(Path(__file__).parents[1]/'bingie75_previous.json'))['files']
        if all(sha(read(p))==known[name] for name,p in zip(FILES,guard(skin))):return True
    except (OSError,ValueError,KeyError):pass
    from widget_skin74 import previously_applied as legacy
    return legacy(skin)
