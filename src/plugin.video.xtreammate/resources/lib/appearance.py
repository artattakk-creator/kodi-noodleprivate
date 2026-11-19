"""Lightweight XCMate-only display preferences, declarative preview and reset.

No system skin/keymap changes. Fonts are names supplied by the active Kodi
skin, not fabricated pixel sizes. Premium assets/catalogue are not downloaded.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import xml.etree.ElementTree as ET

from localization import tr

DEFAULT = dict(theme='core', background_opacity=100, panel_opacity=90, icon_opacity=100,
               dimmer=0, background='101923', panel='101923', accent='159FEA', focus='2276A8',
               text='F0F2F5', secondary='B6BCC6', heading='159FEA', active_text='F0F2F5',
               progress='42D9FF', warning='FFBC58', error='FF8A91', font='normal',
               custom_colours=())
COLOURS = ('background', 'panel', 'accent', 'focus', 'text', 'secondary',
           'heading', 'active_text', 'progress', 'warning', 'error')
OPACITY = ('background_opacity', 'panel_opacity', 'icon_opacity', 'dimmer')
FONTS = {'small': 'font12', 'normal': 'font13', 'large': 'font14', 'very_large': 'font37'}
BINGIE_FONTS = dict(FONTS, large='font16', very_large='font30')
FOCUS_ASSETS = ('xcmate_focus_neon.png', 'guide_focus_frame.png', 'guide_focus80.png')
RENDER_REVISION = '029100-appearance'


def path():
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(),'appearance_v1.json')


def validate(data):
    result=dict(DEFAULT)
    if not isinstance(data,dict): return result
    if isinstance(data.get('theme'),str) and re.fullmatch(r'[a-z][a-z0-9-]{0,47}',data['theme']):result['theme']=data['theme']
    for key in COLOURS:
        value=str(data.get(key,'')).upper().lstrip('#')
        if re.fullmatch('[0-9A-F]{6}',value): result[key]=value
    explicit = data.get('custom_colours', ())
    if not isinstance(explicit, (list, tuple)):
        explicit = ()
    result['custom_colours'] = tuple(k for k in COLOURS if k in explicit or result[k] != DEFAULT[k])
    for key in OPACITY:
        try: result[key]=max(25 if key in ('panel_opacity','icon_opacity') else 0,min(100,int(data.get(key,DEFAULT[key]))))
        except (ValueError,TypeError,OverflowError): pass
    if isinstance(data.get('font'), str) and data['font'] in FONTS:
        result['font'] = data['font']
    return result


def read():
    try:
        with open(path(),encoding='utf-8') as stream: raw=stream.read(8193)
        return validate(json.loads(raw) if len(raw)<=8192 else {})
    except (OSError,ValueError): return dict(DEFAULT)


def save(values):
    filename=path();fd,temp=tempfile.mkstemp(prefix='.appearance-',dir=os.path.dirname(filename))
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as stream:
            json.dump(validate(values),stream);stream.flush();os.fsync(stream.fileno())
        os.replace(temp,filename)
    finally:
        if os.path.exists(temp): os.unlink(temp)


def argb(colour,opacity=100):
    return '{:02X}{}'.format(round(max(0,min(100,opacity))*255/100),colour)


def palette(values, theme):
    values = validate(values)
    if theme:
        for field, colour in theme['spec']['palette'].items():
            if field in COLOURS and field not in values['custom_colours']:
                values[field] = colour.upper()
    if 'heading' not in values['custom_colours']:
        values['heading'] = values['accent']
    return values


def fonts():
    import xbmc
    return BINGIE_FONTS if getattr(xbmc,'getSkinDir',lambda:'')() == 'skin.titan.bingie.mod' else FONTS


def font_for(values, height, names):
    scale = values['font']
    if scale == 'very_large' and 0 < height < 44:
        scale = 'large'
    if scale == 'large' and 0 < height < 32:
        scale = 'normal'
    return names[scale]


def diffuse(control, colour):
    node = control.find('colordiffuse')
    if node is None:
        node = ET.SubElement(control, 'colordiffuse')
    node.text = colour


def solid(texture, left, top, width, height, colour):
    control = ET.Element('control', {'type': 'image', 'xcmate-decoration': 'true'})
    for key, value in dict(left=left, top=top, width=width, height=height, texture=texture).items():
        ET.SubElement(control,key).text = str(value)
    diffuse(control, colour)
    return control


def backdrop_layers(tree, prefs, texture):
    controls = tree.find('controls')
    # The first root-wide image is the backdrop. Add decoration without
    # altering existing IDs, remote links or foreground programme art.
    for index, control in enumerate(controls):
        if (control.get('type') == 'image' and control.findtext('width') == '1280'
                and control.findtext('height') == '720'):
            diffuse(control, argb('FFFFFF',prefs['background_opacity']))
            if 'background' in prefs['custom_colours']:
                controls.insert(index, solid(texture, 0, 0, 1280, 720, argb(prefs['background'])))
                index += 1
            if prefs['dimmer']:
                controls.insert(index+1, solid(texture, 0, 0, 1280, 720, argb('000000',prefs['dimmer'])))
            break


def window_source(xml_filename, kind='vod'):
    """Generate an XCMate-only WindowXML variant; stable IDs/navigation retained.

    WindowXML reads XML/fonts at construction: reopen applies a new profile.
    All generated files live in addon_data, never in Kodi/BINGIE skin folders.
    """
    import xbmcaddon
    from utils import addon_data_dir
    original=xbmcaddon.Addon().getAddonInfo('path')
    preferences = read()
    from theme_render import snapshot,apply_xml
    theme = snapshot()
    values = palette(preferences, theme)
    from menu_layout45 import FILES,apply as menu_layout
    if values==DEFAULT and not theme and xml_filename not in FILES:return original
    source=Path(original)/'resources/skins/Default/720p'/xml_filename
    tree=ET.parse(source)
    if theme:apply_xml(tree,theme,xml_filename,kind)
    menu_layout(tree,xml_filename)
    names = fonts()
    flat = str(Path(original)/'resources/media/appearance-solid.png')
    for control in tree.iter('control'):
        font = control.find('font')
        if font is not None:
            if values['font'] != 'normal':
                try: height = int(control.findtext('height', '0'))
                except ValueError: height = 0
                font.text = font_for(values, height, names)
            elif font.text in ('font16','font24'):
                font.text = names['large' if font.text=='font16' else 'very_large']
        render_colours = xml_filename != 'XCMateGuideGrid.xml' or bool(preferences['custom_colours'])
        if render_colours:
            for node in control.findall('textcolor'):
                colour = 'secondary' if node.text in ('FFB6BCC6', 'FFBCC7D2', 'FF99A9B8') else 'text'
                if node.text in ('FFFFBC58','FFFFCC66','FFFFB15A'):colour = 'warning'
                if node.text in ('FFFF8A91','FFFF7070'):colour = 'error'
                node.text = argb(values[colour])
        texture = control.find('texture')
        if texture is not None and texture.text:
            name = texture.text.rsplit('/', 1)[-1]
            if name in FOCUS_ASSETS:
                if 'focus' in preferences['custom_colours']:
                    texture.set('colordiffuse',argb(values['focus']))
            elif name == 'progress.png' and 'progress' in preferences['custom_colours']:
                texture.text = flat
                diffuse(control,argb(values['progress']))
            elif name in ('panel.png','logo-back.png') and (values['panel_opacity']!=DEFAULT['panel_opacity']
                                                            or 'panel' in preferences['custom_colours']):
                if 'panel' in preferences['custom_colours']:
                    texture.text = flat
                diffuse(control,argb(values['panel'] if 'panel' in preferences['custom_colours'] else 'FFFFFF',
                                     values['panel_opacity']))
            elif control.get('xcmate-menu45') or control.get('xcmate-decoration'):
                diffuse(control,argb('FFFFFF',values['icon_opacity']))
        for node in control.findall('texturefocus'):
            if not (node.text or '').endswith(FOCUS_ASSETS) or 'focus' in preferences['custom_colours']:
                tint = values['focus'] if not theme or 'focus' in preferences['custom_colours'] else 'FFFFFF'
                node.set('colordiffuse',argb(tint,values['panel_opacity']))
        for node in control.findall('texturenofocus'):
            tint = values['panel'] if not theme or 'panel' in preferences['custom_colours'] else 'FFFFFF'
            node.set('colordiffuse',argb(tint,values['panel_opacity']))
    if (values['background_opacity'] != DEFAULT['background_opacity'] or values['dimmer']
            or 'background' in preferences['custom_colours']):
        backdrop_layers(tree, values, flat)
    # Keep the known readable native plan by default and allow explicit focus text.
    if xml_filename=='XCMateMedia.xml' or 'active_text' in preferences['custom_colours']:
        for layout in tree.iter('focusedlayout'):
            for text in layout.iter('textcolor'):text.text=argb(values['active_text'])
        for button in tree.findall(".//control[@type='button']"):
            colour=button.find('focusedcolor')
            if colour is None:colour=ET.SubElement(button,'focusedcolor')
            colour.text=argb(values['active_text'])
    heading=tree.find("./controls/control[@id='101']/textcolor")
    if heading is not None: heading.text=argb(values['heading'])
    data=ET.tostring(tree.getroot(),encoding='utf-8',xml_declaration=True)
    variant=hashlib.sha256(RENDER_REVISION.encode()+data).hexdigest()[:16]
    root=Path(addon_data_dir())/('ui_'+variant+'_'+kind)
    target=root/'resources/skins/Default/720p'/xml_filename
    target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists() or target.read_bytes()!=data:
        fd,temp=tempfile.mkstemp(prefix='.ui-',dir=target.parent)
        try:
            with os.fdopen(fd,'wb') as stream: stream.write(data)
            os.replace(temp,target)
        finally:
            if os.path.exists(temp): os.unlink(temp)
    return str(root)


def preview(values):
    import xbmcgui,xbmcaddon
    class Preview(xbmcgui.WindowDialog):
        def __init__(self):
            super().__init__()
            media=os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources/media')
            flat=os.path.join(media,'appearance-solid.png')
            def colors(key,alpha=100):return '0x'+argb(values[key],alpha)
            font=fonts()[values['font']]
            self.controls=[
                xbmcgui.ControlImage(100,100,1080,520,flat,colorDiffuse=colors('background')),
                xbmcgui.ControlImage(100,100,1080,520,os.path.join(media,'lightweight_splash.jpg'),
                                     colorDiffuse='0x'+argb('FFFFFF',values['background_opacity'])),
                xbmcgui.ControlImage(100,100,1080,520,flat,colorDiffuse='0x'+argb('000000',values['dimmer'])),
                xbmcgui.ControlImage(140,150,1000,420,flat,colorDiffuse=colors('panel',values['panel_opacity'])),
                xbmcgui.ControlImage(168,247,944,75,flat,colorDiffuse=colors('focus')),
                xbmcgui.ControlButton(168,247,944,75,tr(32641),font=font,
                                     textColor=colors('text'),focusedColor=colors('active_text')),
                xbmcgui.ControlLabel(180,177,910,60,tr(32626),font=font,textColor=colors('heading')),
                xbmcgui.ControlLabel(180,350,910,48,tr(32634),font=font,textColor=colors('secondary')),
                xbmcgui.ControlImage(180,430,800,7,flat,colorDiffuse=colors('progress')),
                xbmcgui.ControlLabel(180,462,400,48,tr(39205),font=font,textColor=colors('warning')),
                xbmcgui.ControlLabel(628,462,400,48,tr(39206),font=font,textColor=colors('error')),
                xbmcgui.ControlImage(1042,184,32,32,os.path.join(media,'tv_settings.png'),
                                     colorDiffuse='0x'+argb('FFFFFF',values['icon_opacity'])),
            ]
            self.addControls(self.controls)
            self.setFocus(self.controls[5])
        def show(self):
            super().show();self.setFocus(self.controls[5])
        def onAction(self,action):
            if action.getId() in (7,9,10,92): self.close()
    window=Preview()
    try:
        # WindowDialog has no onInit; controls are built before modal display.
        window.doModal()
    finally: window.close()


def configure():
    import xbmcgui
    dialog=xbmcgui.Dialog();draft=read()
    from theme_render import snapshot
    fields=[(32627,'background_opacity'),(32628,'panel_opacity'),(32629,'icon_opacity'),(39200,'dimmer'),
            (32630,'background'),(39201,'panel'),(32631,'accent'),(32632,'focus'),
            (32633,'text'),(32634,'secondary'),(39202,'heading'),(39203,'active_text'),
            (39204,'progress'),(39205,'warning'),(39206,'error'),(32635,'font')]
    scales = dict(zip(FONTS, (32637,32638,32639,39207)))
    while True:
        theme = snapshot()
        shown = palette(draft, theme)
        design = theme['spec']['name'] if theme else tr(33801)
        labels=[tr(39208,design)] + [
            tr(label)+' · '+(tr(scales[shown[key]]) if key=='font' else str(shown[key])+('%' if key in OPACITY else ''))
            for label,key in fields]+[tr(32626),tr(32623),tr(32624),tr(32625)]
        choice=__import__('menu_icons45').select(dialog,tr(32622),labels,default='palette')
        if choice<0 or choice==len(fields)+3: return False
        if choice==0:
            __import__('theme_ui').manage();draft['theme']=read()['theme'];continue
        if 1<=choice<=len(fields):
            _,key=fields[choice-1]
            if key in OPACITY:
                number=__import__('menu_icons45').select(dialog,tr(fields[choice-1][0]),[str(n)+'%' for n in range(0,101,10)],default='palette')
                if number>=0: draft[key]=number*10
            elif key=='font':
                scale=__import__('menu_icons45').select(dialog,tr(32635),[tr(label) for label in scales.values()],default='palette')
                if scale>=0: draft[key]=tuple(scales)[scale]
            else:
                colour=dialog.input(tr(fields[choice-1][0]),defaultt=shown[key]).upper().lstrip('#')
                if colour:
                    if re.fullmatch('[0-9A-F]{6}',colour):
                        draft[key]=colour
                        if key not in draft['custom_colours']:
                            draft['custom_colours'] += (key,)
                    else: dialog.ok('XCMate',tr(32640))
            draft=validate(draft)
        elif choice==len(fields)+1: preview(palette(draft,theme))
        elif choice==len(fields)+2:
            try: save(draft);return True
            except OSError: dialog.ok('XCMate',tr(32643));return False
        elif choice==len(fields)+4: draft=dict(DEFAULT,theme=draft['theme'])
