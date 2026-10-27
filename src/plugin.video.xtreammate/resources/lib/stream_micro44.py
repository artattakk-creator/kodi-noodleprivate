"""Infobar-only presentation of the existing Details.read snapshot.

No player reads, network, font download or codec/quality inference here.
Coordinates scale inside the unchanged infobar, not the screen's outer corner.
"""
import math,os


def labels(values):
    video=''
    width,height=values.get('width'),values.get('height')
    if width and height:video=str(width)+'×'+str(height)
    audio=str(values.get('audio') or '').strip().upper()[:16]
    channels=str(values.get('channels') or '').strip()[:12]
    # Preserve exactly the reported channel layout. Never infer Dolby/Atmos.
    return video,' · '.join(v for v in (audio,channels) if v)


def choose_font():
    """Read only the installed skin registry; reuse existing font12 on failure."""
    try:
        import xbmcvfs,xml.etree.ElementTree as ET
        for name in ('special://skin/xml/Font.xml','special://skin/1080i/Font.xml','special://skin/720p/Font.xml'):
            if not xbmcvfs.exists(name):continue
            stream=xbmcvfs.File(name)
            try:raw=bytes(stream.readBytes(131073))
            finally:stream.close()
            if len(raw)>131072 or b'<!DOCTYPE' in raw or b'<!ENTITY' in raw:continue
            root=ET.fromstring(raw);choices=[]
            for font in root.findall('.//font'):
                ident=font.findtext('name','');size=font.findtext('size','')
                try:size=float(size)
                except ValueError:continue
                if ident and 10<=size<=14:choices.append((abs(size-13),size,ident))
            if choices:return min(choices)[2]
    except (AttributeError,ImportError,OSError,ValueError):pass
    return 'font12'  # Existing .43 infobar uses this installed-font fallback.


def geometry(width,height,video,audio):
    scale=height/1080.;icon=max(8,round(13*scale));gap=max(4,round(7*scale))
    right=width-32-max(12,round(22*scale));bottom=height-32
    y=bottom-max(12,round(15*scale))-max(16,round(18*scale))
    specs=[]
    for kind,text in (('video',video),('audio',audio)):
        if not text:continue
        textwidth=max(20,math.ceil(len(text)*max(8,13*scale)*.65)+4)
        specs.append((kind,text,icon+gap+textwidth,textwidth))
    x=right-sum(s[2] for s in specs)-gap*2*max(0,len(specs)-1)
    result={}
    for kind,text,total,textwidth in specs:
        result[kind]=dict(text=text,icon=(x,y+max(1,(max(16,round(18*scale))-icon)//2),icon,icon),label=(x+icon+gap,y,textwidth,max(16,round(18*scale))))
        x+=total+gap*2
    return result


class MicroLine:
    def __init__(self,owner,media,width,height):
        import xbmcgui
        self.owner=owner;self.width=width;self.height=height;self.icons={};self.text={}
        font=choose_font()
        for kind,name in (('video','monitor'),('audio','speaker')):
            self.icons[kind]=xbmcgui.ControlImage(0,0,13,13,os.path.join(media,'infomicro44',name+'.png'))
            self.text[kind]=xbmcgui.ControlLabel(0,0,120,18,'',font,'0xFFB6BCC6')
        self.controls=[self.icons['video'],self.text['video'],self.icons['audio'],self.text['audio']]

    def _write(self,control,method,*values):
        from render_diff44 import write
        write(self.owner,control,method,*values)

    def hide(self):
        for control in self.controls:self._write(control,'setVisible',False)
        for control in self.text.values():self._write(control,'setLabel','')

    def render(self,values):
        specs=geometry(self.width,self.height,*labels(values))
        for kind in ('video','audio'):
            icon,label=self.icons[kind],self.text[kind];spec=specs.get(kind)
            if not spec:
                self._write(icon,'setVisible',False);self._write(label,'setVisible',False);self._write(label,'setLabel','');continue
            x,y,w,h=spec['icon'];self._write(icon,'setPosition',x,y);self._write(icon,'setWidth',w)
            # Square PNG aspectRatio=keep; native binding provides setHeight.
            if hasattr(icon,'setHeight'):self._write(icon,'setHeight',h)
            x,y,w,h=spec['label'];self._write(label,'setPosition',x,y);self._write(label,'setWidth',w)
            self._write(label,'setLabel',spec['text'])
            self._write(icon,'setVisible',True);self._write(label,'setVisible',True)
