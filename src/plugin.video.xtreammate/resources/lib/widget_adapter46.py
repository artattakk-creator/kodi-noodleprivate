"""Explicit opt-in, single-file BINGIE programme-card renderer.

No automatic apply. Only known widget layout includes receive a conditional
XCMate-only visual group. All original bytes, bindings, actions and focus targets
are retained. Reload hooks remain the separately approved .45 adapter's job.
"""
import json,os,stat,uuid
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.parsers import expat
from widget_adapter45 import sha,save_private,replace
LIMIT=2*1024*1024
NAMES={'widget_layout_poster','widget_layout_landscape_not_vertical_layout','widget_layout_landscapelarge','widget_layout_highlight'}
BASE='special://home/addons/plugin.video.xtreammate/resources/media/programme46/'

def card(width,height,focused=False):
 width-=12;height-=12
 g=ET.Element('control',{'type':'group','xcmate-programme46':'true'})
 ET.SubElement(g,'visible').text='String.IsEqual(ListItem.Property(XCMate.WidgetKind41),live) + !String.IsEmpty(ListItem.Property(XCMate.ProgrammeKey46))'
 def node(kind,x,y,w,h,texture=None,label=None,font=None,visible=None):
  n=ET.SubElement(g,'control',{'type':kind})
  for k,v in [('left',x),('top',y),('width',w),('height',h)]:ET.SubElement(n,k).text=str(v)
  if texture:ET.SubElement(n,'texture').text=texture
  if kind=='image':ET.SubElement(n,'aspectratio').text='keep' if texture and texture.startswith('$INFO') else 'stretch'
  if label:ET.SubElement(n,'label').text=label
  if font:ET.SubElement(n,'font').text=font;ET.SubElement(n,'textcolor').text='FFFFFFFF'
  if visible:ET.SubElement(n,'visible').text=visible
  return n
 node('image',6,6,width,height,BASE+'panel.png')
 node('image',6,6,width,height,'$INFO[ListItem.Art(landscape)]')
 node('image',14,14,min(108,width-16),66,BASE+'logo-back.png')
 node('image',22,22,min(92,width-32),50,'$INFO[ListItem.Property(XCMate.ProgrammeLogo46)]',visible='!String.IsEmpty(ListItem.Property(XCMate.ProgrammeLogo46))')
 node('label',22,28,min(92,width-32),36,label='$INFO[ListItem.Property(XCMate.ProgrammeChannel46)]',font='Reg18',visible='String.IsEmpty(ListItem.Property(XCMate.ProgrammeLogo46))')
 if focused:
  available=max(24,min(110,height-150))
  node('image',12,85,width-12,available,BASE+'logo-back.png',visible='Control.HasFocus($PARAM[widgetid])')
  description=node('textbox',18,85,width-24,available,font='Reg18',visible='Control.HasFocus($PARAM[widgetid])')
  ET.SubElement(description,'label').text='$INFO[ListItem.Property(XCMate.ProgrammeDescription46)]'
 node('image',6,height-60,width,66,BASE+'logo-back.png')
 node('label',16,height-58,width-20,30,label='$INFO[ListItem.Property(XCMate.ProgrammeTitle46)]',font='Bold22')
 node('label',16,height-29,width-20,24,label='$INFO[ListItem.Property(XCMate.ProgrammeTimes46)]',font='Reg18')
 progress=node('progress',6,height+1,width,5)
 ET.SubElement(progress,'info').text='ListItem.Property(XCMate.ProgrammePercent46)'
 ET.SubElement(progress,'texturebg').text=BASE+'track.png';ET.SubElement(progress,'midtexture').text=BASE+'progress.png'
 return ET.tostring(g,encoding='utf-8')

def patch(data):
 if len(data)>LIMIT or b'<!DOCTYPE' in data or b'<!ENTITY' in data:raise ValueError('UNSAFE_LAYOUT')
 if b'xcmate-programme46=' in data:return data,0
 parser=expat.ParserCreate();stack=[];changes=[];found=set()
 def start(tag,attrs):stack.append((tag,dict(attrs)))
 def end(tag):
  if tag in ('itemlayout','focusedlayout'):
   ancestor=next((a.get('name') for t,a in reversed(stack[:-1]) if t=='include' and a.get('name')),None)
   if ancestor in NAMES:
    attrs=stack[-1][1]
    try:w=int(attrs['width']);h=int(attrs['height'])
    except (KeyError,ValueError):raise ValueError('UNVERIFIED_LAYOUT') from None
    if not 180<=w<=1400 or not 160<=h<=800:raise ValueError('UNVERIFIED_LAYOUT')
    changes.append((parser.CurrentByteIndex,card(w,h,tag=='focusedlayout')));found.add(ancestor)
  stack.pop()
 parser.StartElementHandler=start;parser.EndElementHandler=end
 parser.StartDoctypeDeclHandler=lambda *a:(_ for _ in ()).throw(ValueError('UNSAFE_LAYOUT'))
 try:parser.Parse(data,True)
 except expat.ExpatError:raise ValueError('INVALID_LAYOUT') from None
 if found!=NAMES or len(changes)!=12:raise ValueError('UNVERIFIED_LAYOUT')
 out=data
 for index,value in sorted(changes,reverse=True):out=out[:index]+value+out[index:]
 ET.fromstring(out)
 return out,len(changes)

def folder():
 from utils import addon_data_dir
 root=Path(addon_data_dir())/'widget_adapter46';root.mkdir(mode=0o700,exist_ok=True)
 if root.is_symlink():raise ValueError('UNSAFE_BACKUP_FOLDER')
 return root

def guard(target,skin_root,version):
 root=Path(skin_root).resolve();p=Path(target)
 if version!='2.2.3':raise ValueError('UNVERIFIED_SKIN_VERSION')
 if p.is_symlink() or p.name!='IncludesHomeWidgets.xml' or p.resolve().parent.name!='xml' or root not in p.resolve().parents:raise ValueError('UNSAFE_TARGET')
 meta=ET.parse(root/'addon.xml').getroot()
 if meta.get('id')!='skin.titan.bingie.mod' or meta.get('version')!=version:raise ValueError('SKIN_METADATA_MISMATCH')
 font=ET.parse(root/'xml/Font.xml').getroot();names={n.findtext('name') for n in font.iter('font')}
 if not {'Reg18','Bold22'}<=names:raise ValueError('UNVERIFIED_FONT_BINDING')
 if not p.is_file() or p.stat().st_size>LIMIT:raise ValueError('LAYOUT_LIMIT')
 return p.resolve()

def prepare(target,skin_root,version):
 target=guard(target,skin_root,version);old=target.read_bytes();new,count=patch(old)
 if not count:return dict(code='NO_PATCH_NEEDED',count=0)
 token=uuid.uuid4().hex;root=folder();backup=token+'.original.xml';candidate=token+'.candidate.xml'
 save_private(root/backup,old);save_private(root/candidate,new)
 if sha((root/backup).read_bytes())!=sha(old) or sha((root/candidate).read_bytes())!=sha(new):raise ValueError('BACKUP_VERIFY_FAILED')
 plan=dict(code='PREPARED_NOT_APPLIED',target=str(target),skin_root=str(Path(skin_root).resolve()),version=version,backup=backup,candidate=candidate,before=sha(old),after=sha(new),count=count,mode=stat.S_IMODE(target.stat().st_mode))
 save_private(root/(token+'.json'),json.dumps(plan).encode());return plan

def apply(plan,*,confirmed=False,restore=False):
 if confirmed is not True:raise PermissionError('EXPLICIT_APPROVAL_REQUIRED')
 target=guard(plan['target'],plan['skin_root'],plan['version']);root=folder()
 if any(Path(plan[k]).name!=plan[k] for k in ('backup','candidate')):raise ValueError('UNSAFE_PLAN')
 old=(root/plan['backup']).read_bytes();new=(root/plan['candidate']).read_bytes()
 if sha(old)!=plan['before'] or sha(new)!=plan['after'] or patch(old)[0]!=new:raise ValueError('BACKUP_VERIFY_FAILED')
 expected=plan['after'] if restore else plan['before']
 if sha(target.read_bytes())!=expected:raise ValueError('TARGET_CHANGED_NO_OVERWRITE')
 content=old if restore else new;replace(target,content,plan['mode'],expected)
 if sha(target.read_bytes())!=sha(content):raise ValueError('TARGET_VERIFY_FAILED')
 return dict(code='RESTORED' if restore else 'APPLIED',sha256=sha(content),count=plan['count'])

def latest():
 for p in sorted(folder().glob('*.json'),reverse=True):
  try:
   v=json.loads(p.read_text())
   if sha(Path(v['target']).read_bytes())==v['after']:return v
  except (OSError,ValueError,KeyError):pass
 return None

def show():
 import xbmc,xbmcaddon,xbmcgui
 from localization import tr
 from menu_icons45 import select
 if xbmc.getCondVisibility('Player.HasMedia'):xbmcgui.Dialog().ok('XCMate',tr(36105));return
 dialog=xbmcgui.Dialog()
 choice=select(dialog,tr(36111),[tr(36101),tr(36113),tr(36114),tr(36115)],actions=['back','grid','shield','refresh'],preselect=0)
 if choice not in (1,2,3):return
 if choice==3:
  from widget_adapter45 import show as reload_show
  reload_show();return
 try:
  skin=xbmcaddon.Addon('skin.titan.bingie.mod');root=skin.getAddonInfo('path')
  plan=prepare(Path(root)/'xml/IncludesHomeWidgets.xml',root,skin.getAddonInfo('version')) if choice==1 else latest()
  if not plan or plan.get('code')=='NO_PATCH_NEEDED':dialog.ok('XCMate','NO_PATCH_NEEDED');return
  dialog.ok('XCMate',tr(36112)+'\n'+tr(36116))
  if select(dialog,tr(36117),[tr(36101),tr(36118)],actions=['back','shield'],preselect=0)!=1:return
  result=apply(plan,confirmed=True,restore=choice==2);dialog.notification('XCMate',result['code']);xbmc.executebuiltin('ReloadSkin()')
 except (OSError,ValueError,KeyError,ET.ParseError) as error:
  allowed={'UNVERIFIED_SKIN_VERSION','UNSAFE_TARGET','SKIN_METADATA_MISMATCH','UNVERIFIED_FONT_BINDING','LAYOUT_LIMIT','UNSAFE_LAYOUT','INVALID_LAYOUT','UNVERIFIED_LAYOUT','BACKUP_VERIFY_FAILED','TARGET_CHANGED_NO_OVERWRITE','TARGET_VERIFY_FAILED','UNSAFE_PLAN','UNSAFE_BACKUP_FOLDER','EXPLICIT_APPROVAL_REQUIRED'}
  dialog.ok('XCMate','BLOCKED: '+(str(error) if str(error) in allowed else 'LAYOUT_UNAVAILABLE'))
