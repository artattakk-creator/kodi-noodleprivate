"""Reference infobar presentation; never read player/network/EPG from the GUI."""
import os,time
from localization import tr


def _image(rect,path,aspectRatio=0):
 import xbmcgui
 return xbmcgui.ControlImage(rect[0],rect[1],rect[2],rect[3],path,aspectRatio=aspectRatio)

def _label(rect,text,font,color,alignment=0):
 import xbmcgui
 return xbmcgui.ControlLabel(rect[0],rect[1],rect[2],rect[3],text,font,color,alignment=alignment)

def layout(width,height):
 s=min(width/1920.,height/1080.);dx=(width-1920*s)/2;dy=height-1080*s
 def box(x,y,w,h):return (round(dx+x*s),round(dy+y*s),max(1,round(w*s)),max(1,round(h*s)))
 return dict(scale=s,box=box,panel=box(26,670,1868,362),logo=box(78,720,208,138),name=box(78,874,240,44),date=box(78,923,242,34),clock=box(78,958,242,48),previous=box(378,720,994,45),badge_now=box(378,786,132,50),now=box(534,774,838,80),start=box(378,868,94,40),end=box(1301,868,91,40),track=box(477,880,796,16),badge_next=box(378,932,147,40),next=box(576,923,470,53),next_time=box(1050,934,325,34),left_sep=box(338,715,2,270),right_sep=box(1410,715,2,270))


def fonts(scale):
 """Select registered installed fonts by actual declared size, not guessed IDs."""
 targets={'title':(60,True),'name':(31,True),'next':(40,True),'clock':(40,False),'time':(27,False),'previous':(25,False),'badge':(26,True),'value':(25,True),'resolution':(21,True),'language':(22,True),'caption':(20,False),'date':(25,False)}
 available=[]
 try:
  import xbmcvfs,xml.etree.ElementTree as ET
  for filename in ('special://skin/xml/Font.xml','special://skin/1080i/Font.xml','special://skin/720p/Font.xml'):
   if not xbmcvfs.exists(filename):continue
   f=xbmcvfs.File(filename)
   try:raw=bytes(f.readBytes(262145))
   finally:f.close()
   if len(raw)>262144 or b'<!DOCTYPE' in raw or b'<!ENTITY' in raw:continue
   for node in ET.fromstring(raw).iter('font'):
    name=node.findtext('name','');size=node.findtext('size','')
    try:size=float(size)
    except ValueError:continue
    if name and 8<=size<=150:available.append((name,size,'bold' in (name+' '+node.findtext('style','')).casefold()))
   if available:break
 except (ImportError,AttributeError,OSError,ValueError):pass
 result={}
 for key,(size,bold) in targets.items():
  if available:result[key]=min(available,key=lambda f:abs(f[1]-max(12,size*scale))+(0 if f[2]==bold else 3))[0]
  else:result[key]='font16' if key in ('title','name','next','clock') else 'font13' if key in ('time','previous','badge','value') else 'font12'
 return result


def values(snapshot):
 width,height=snapshot.get('width'),snapshot.get('height')
 resolution=str(width)+' × '+str(height) if width and height else ''
 codec=str(snapshot.get('video') or '').strip()
 codec={'h264':'H.264','avc':'H.264','hevc':'HEVC','h265':'H.265'}.get(codec.casefold(),codec.upper())
 audio=' '.join(str(snapshot.get(k) or '').strip().upper() for k in ('audio','channels')).strip()
 language=str(snapshot.get('language') or '').strip()
 language={'de':tr(36041),'deu':tr(36041),'ger':tr(36041),'german':tr(36041),'en':tr(36042),'eng':tr(36042),'english':tr(36042),'fr':tr(36043),'fra':tr(36043),'fre':tr(36043),'french':tr(36043)}.get(language.casefold(),language)
 # Kodi's actual language value may be a code or a localized name; do not guess.
 subtitle=''
 if snapshot.get('subtitle_enabled') is False:subtitle=tr(36039)
 elif snapshot.get('subtitle_enabled') is True:subtitle=str(snapshot.get('subtitles') or tr(36029))
 fps=str(snapshot.get('fps') or '').strip()
 return dict(video=resolution,codec=codec,audio=audio,language=language,subtitle=subtitle,fps=(fps+' fps') if fps else '')


class Technology:
 def __init__(self,owner,media,geom,font):
  import xbmcgui
  self.owner=owner;self.geom=geom;self.font=font;self.icons={};self.text={};self.captions={};self.frames={};self.controls=[]
  roles=(('video','resolution',36033,1450,715),('codec','codec',36034,1692,715),('audio','audio',36035,1450,814),('language','language',36036,1692,814),('subtitle','subtitle',36037,1450,914),('fps','fps',36038,1692,914))
  for key,image,label,x,y in roles:
   box=geom['box'];frame=_image(box(x,y,64,64),os.path.join(media,'infobar45','cell.png'))
   icon=_image(box(x+14,y+14,36,36),os.path.join(media,'infobar45',image+'.png'))
   value=_label(box(x+86,y+1,151 if x==1450 else 106,33),'',font['resolution'] if key=='video' else font['language'] if key=='language' else font['value'],'0xFFF5F7F8')
   caption=_label(box(x+86,y+36,154 if x==1450 else 114,29),tr(label),font['caption'],'0xFF929BA2')
   self.icons[key]=icon;self.text[key]=value;self.captions[key]=caption;self.frames[key]=frame
   if key=='video':
    self.resolution_frame52=_image(box(x+78,y-4,160,44),os.path.join(media,'infobar45','cell.png'))
    self.controls.extend((frame,icon,self.resolution_frame52,value,caption))
   else:self.controls.extend((frame,icon,value,caption))
 def write(self,control,method,*args):
  from render_diff44 import write
  write(self.owner,control,method,*args)
 def hide(self):
  for c in self.controls:self.write(c,'setVisible',False)
  for c in self.text.values():self.write(c,'setLabel','')
 def render(self,snapshot):
  data=values(snapshot)
  for key,text in data.items():
   self.write(self.text[key],'setLabel',text)
   for c in (self.frames[key],self.icons[key],self.text[key],self.captions[key]):self.write(c,'setVisible',bool(text))
  self.write(self.resolution_frame52,'setVisible',bool(data['video']))


class InfoBar:
 def __init__(self,owner,media,width,height):
  import xbmcgui
  self.owner=owner;self.g=layout(width,height);self.font=fonts(self.g['scale']);g=self.g;self.controls=[]
  def image(key,name):
   c=_image(g[key],os.path.join(media,'infobar45',name+'.png'));self.controls.append(c);return c
  def label(key,font,color='0xFFF5F7F8',text=''):
   c=_label(g[key],text,self.font[font],color,alignment=2 if key in ('badge_now','badge_next') else 0);self.controls.append(c);return c
  self.bg=image('panel','glass');self.left_sep=image('left_sep','separator');self.right_sep=image('right_sep','separator')
  self.logo=_image(g['logo'],os.path.join(media,'tv.png'),aspectRatio=2);self.controls.append(self.logo)
  self.name=label('name','name');self.date=label('date','date','0xFF919AA2');self.clock=label('clock','clock','0xFFB9C2CC')
  self.previous=label('previous','previous','0xFFBAC1C7')
  self.badge_now=image('badge_now','now');self.badge_next=image('badge_next','next')
  self.now_badge=label('badge_now','badge','0xFF081A08',tr(36031));self.next_badge=label('badge_next','caption','0xFFD0D5D8',tr(36032))
  self.now=label('now','title');self.next=label('next','next');self.next_time=label('next_time','caption','0xFF9EA6AD')
  self.start=label('start','time');self.end=label('end','time');self.track=image('track','track');self.progress=image('track','progress')
  x,y,w,h=g['track'];self.knob=xbmcgui.ControlImage(x,y-4,max(1,round(28*g['scale'])),max(1,round(28*g['scale'])),os.path.join(media,'infobar45','knob.png'));self.controls.append(self.knob)
  self.technology=Technology(owner,media,g,self.font)
  # Compatibility handles stay blank and hidden, never a duplicate info line.
  self.hint=xbmcgui.ControlLabel(0,0,1,1,'','font12','0xFFB6BCC6');self.duration=xbmcgui.ControlLabel(0,0,1,1,'','font12','0xFFB6BCC6');self.controls.extend((self.hint,self.duration))
 def write(self,control,method,*args):
  from render_diff44 import write
  write(self.owner,control,method,*args)
 def render(self,channel,logo,info,details,date='',clock=''):
  self.write(self.now_badge,'setLabel',tr(36031));self.write(self.next_badge,'setLabel',tr(36032))
  self.write(self.logo,'setImage',logo);self.write(self.name,'setLabel',channel)
  self.write(self.date,'setLabel',date);self.write(self.clock,'setLabel',clock)
  self.write(self.previous,'setLabel',tr(36030)+':  '+str(info.get('previous') or '—'))
  self.write(self.now,'setLabel',info.get('now') or 'Für diesen Sender keine EPG-Daten verfügbar')
  self.write(self.start,'setLabel',info.get('now_time','') if info.get('now') else '')
  self.write(self.end,'setLabel',info.get('now_end_time','') if info.get('now') else '')
  self.write(self.next,'setLabel',info.get('next') or '—')
  times=' – '.join(v for v in (info.get('next_time',''),info.get('next_end_time','')) if v)
  self.write(self.next_time,'setLabel',times if info.get('next') else '')
  progress=info.get('progress');valid=isinstance(progress,(int,float)) and info.get('now')
  for c in (self.track,self.progress,self.knob):self.write(c,'setVisible',bool(valid))
  if valid:
   progress=max(0,min(1,progress));x,y,w,h=self.g['track'];diameter=max(1,round(28*self.g['scale']))
   self.write(self.progress,'setWidth',max(1,round(w*progress)));self.write(self.progress,'setVisible',progress>0)
   self.write(self.knob,'setPosition',x+round(w*progress)-diameter//2,y+(h-diameter)//2)
  self.write(self.hint,'setVisible',False);self.write(self.duration,'setVisible',False)
  self.technology.render(details)
