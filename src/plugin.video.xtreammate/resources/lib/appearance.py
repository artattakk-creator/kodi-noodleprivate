"""Lightweight XCMate-only display preferences, declarative preview and reset.

No system skin/keymap changes. Fonts are names supplied by the active Kodi
skin, not fabricated pixel sizes. Premium assets/catalogue are not downloaded.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import xml.etree.ElementTree as ET

from localization import tr

DEFAULT=dict(theme='core',background_opacity=100,panel_opacity=90,icon_opacity=100,
             background='101923',accent='159FEA',focus='2276A8',text='F0F2F5',secondary='B6BCC6',font='normal')
COLOURS=('background','accent','focus','text','secondary')
OPACITY=('background_opacity','panel_opacity','icon_opacity')
FONTS={'small':'font12','normal':'font13','large':'font16'}


def path():
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(),'appearance_v1.json')


def validate(data):
    result=dict(DEFAULT)
    if not isinstance(data,dict): return result
    for key in COLOURS:
        value=str(data.get(key,'')).upper().lstrip('#')
        if re.fullmatch('[0-9A-F]{6}',value): result[key]=value
    for key in OPACITY:
        try: result[key]=max(25 if key!='background_opacity' else 0,min(100,int(data.get(key,DEFAULT[key]))))
        except (ValueError,TypeError): pass
    if data.get('font') in FONTS: result['font']=data['font']
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


def window_source(xml_filename):
    """Generate an XCMate-only WindowXML variant; stable IDs/navigation retained.

    WindowXML reads XML/fonts at construction: reopen applies a new profile.
    All generated files live in addon_data, never in Kodi/BINGIE skin folders.
    """
    import xbmcaddon
    from utils import addon_data_dir
    original=xbmcaddon.Addon().getAddonInfo('path')
    values=read()
    if values==DEFAULT: return original
    source=Path(original)/'resources/skins/Default/720p'/xml_filename
    tree=ET.parse(source)
    for node in tree.getroot().iter():
        if node.tag=='font': node.text=FONTS[values['font']]
        elif node.tag=='textcolor' and xml_filename!='XCMateGuideGrid.xml':
            node.text=argb(values['secondary'] if node.text=='FFB6BCC6' else values['text'])
        elif node.tag=='texture' and node.text and not node.text.endswith(('xcmate_focus_neon.png','guide_focus_frame.png')):
            node.set('colordiffuse',argb('FFFFFF',values['icon_opacity']))
        elif node.tag=='texturefocus' and not (node.text or '').endswith(('xcmate_focus_neon.png','guide_focus_frame.png')): node.set('colordiffuse',argb(values['focus'],values['panel_opacity']))
        elif node.tag=='texturenofocus': node.set('colordiffuse',argb(values['background'],values['panel_opacity']))
    # Background and shade images get their own alpha; focused labels stay
    # readable even if the user makes the backdrop fully transparent.
    for control in tree.findall('./controls/control'):
        if control.get('type')=='image' and control.findtext('width')=='1280':
            texture=control.find('texture')
            if texture is not None: texture.set('colordiffuse',argb(values['background'],values['background_opacity']))
    for control in tree.getroot().iter('control'):
        font=control.find('font')
        if font is not None and values['font']=='large':
            try: height=int(control.findtext('height','0'))
            except ValueError: height=0
            if 0<height<36: font.text='font13'
    heading=tree.find("./controls/control[@id='101']/textcolor")
    if heading is not None: heading.text=argb(values['accent'])
    root=Path(addon_data_dir())/'ui_core'
    target=root/'resources/skins/Default/720p'/xml_filename
    target.parent.mkdir(parents=True,exist_ok=True)
    data=ET.tostring(tree.getroot(),encoding='utf-8',xml_declaration=True)
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
            self.controls=[]
            media=os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources/media')
            self.controls.append(xbmcgui.ControlImage(100,100,1080,520,os.path.join(media,'tv_panel.png'),
                colorDiffuse=argb(values['background'],values['background_opacity'])))
            self.controls.append(xbmcgui.ControlButton(140,170,1000,72,tr(32641),
                focusTexture=os.path.join(media,'tv_focus.png'),noFocusTexture=os.path.join(media,'tv_normal.png'),
                font=FONTS[values['font']],textColor=argb(values['text']),focusedColor=argb(values['accent'])))
            self.controls.append(xbmcgui.ControlLabel(140,300,1000,180,tr(32642),font=FONTS[values['font']],textColor=argb(values['secondary'])))
            self.addControls(self.controls)
            self.setFocus(self.controls[1])
        def show(self):
            super().show();self.setFocus(self.controls[1])
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
    fields=[(32627,'background_opacity'),(32628,'panel_opacity'),(32629,'icon_opacity'),
            (32630,'background'),(32631,'accent'),(32632,'focus'),(32633,'text'),(32634,'secondary'),(32635,'font')]
    while True:
        labels=[tr(32636)]+[tr(label)+': '+str(draft[key]) for label,key in fields]+[tr(32626),tr(32623),tr(32624),tr(32625)]
        choice=dialog.select(tr(32622),labels)
        if choice<0 or choice==len(fields)+3: return False
        if choice==0:
            dialog.ok('XCMate',tr(32642));continue
        if 1<=choice<=len(fields):
            _,key=fields[choice-1]
            if key in OPACITY:
                number=dialog.select(tr(fields[choice-1][0]),[str(n)+'%' for n in range(0,101,10)])
                if number>=0: draft[key]=number*10
            elif key=='font':
                scale=dialog.select(tr(32635),[tr(32637),tr(32638),tr(32639)])
                if scale>=0: draft[key]=('small','normal','large')[scale]
            else:
                colour=dialog.input(tr(fields[choice-1][0]),defaultt=draft[key]).upper().lstrip('#')
                if colour:
                    if re.fullmatch('[0-9A-F]{6}',colour): draft[key]=colour
                    else: dialog.ok('XCMate',tr(32640))
            draft=validate(draft)
        elif choice==len(fields)+1: preview(draft)
        elif choice==len(fields)+2:
            try: save(draft);return True
            except OSError: dialog.ok('XCMate',tr(32643));return False
        elif choice==len(fields)+4: draft=dict(DEFAULT)
