"""Owned .78/.79 adapter upgrade: full-bleed/contain Hero and immediate rows.

Only exact reviewed own nodes are replaced. Saved shortcuts, paths, unrelated
XML bytes and original native definitions are preserved by the transaction.
"""
import copy,hashlib,json
from pathlib import Path
import xml.etree.ElementTree as E
MARKER=b'XCMate80.Contract'
PORTRAIT='!String.IsEqual(ListItem.Property(XCMate.WidgetKind41),live) + String.IsEmpty(ListItem.Art(fanart))'
OWN='String.StartsWith("$PARAM[widgetPath]",plugin://plugin.video.xtreammate/)'

def digest(node):return hashlib.sha256(E.canonicalize(E.tostring(node,encoding='unicode'),strip_text=True).encode()).hexdigest()

def _node(data,tag,attribute,value):
 from widget_skin50 import spans
 rows=[n for n in spans(data) if n['tag']==tag and n['attrs'].get(attribute)==value]
 if len(rows)!=1:raise ValueError('UNVERIFIED_80_NODE')
 n=rows[0];end=n['end']+len(('</'+tag+'>').encode())
 return n,end,E.fromstring(data[n['start']:end])

def upgrade(original):
 from widget_skin78 import parse
 from widget_skin50 import edit
 if MARKER in original['xml/IncludesVariables.xml']:
  verify(original);return dict(original)
 known=json.loads((Path(__file__).parents[1]/'bingie80_previous.json').read_text());result=dict(original)
 name='xml/IncludesHomeWidgets.xml';data=result[name];changes=[]
 n,end,hero=_node(data,'include','name','XCMate50.Hero')
 if digest(hero)!=known['XCMate50.Hero']:raise ValueError('UNVERIFIED_80_HERO')
 main=hero.find(".//control[@id='296751']");main.find('width').text='1620';main.find('height').text='480';main.find('top').text='0';main.find('aspectratio').text='scale'
 E.SubElement(main,'visible').text='!['+PORTRAIT+']'
 portrait=copy.deepcopy(main);portrait.set('id','296783');portrait.find('aspectratio').text='keep';portrait.find('visible').text=PORTRAIT
 group=hero.find('control');group.insert(list(group).index(main)+1,portrait)
 group.find('control/height').text='500'
 panel=hero.find(".//control[@id='296750']");panel.find('top').text='0';panel.find('height').text='480'
 for child in panel.findall('.//control'):
  for field in ('top','height'):
   value=child.find(field)
   if value is not None and (value.text or '').isdigit():value.text=str(round(int(value.text)*480/580))
 changes.append((n['start'],end,E.tostring(hero,encoding='utf-8')))
 for include in ('widget_base','XCMate50.LiveRow'):
  n,end,node=_node(data,'include','name',include)
  if digest(node)!=known[include]:raise ValueError('UNVERIFIED_80_ROW')
  wrapper=node.find('control')
  if include=='XCMate50.LiveRow':
   wrapper.find('height').text='100';changes.append((n['start'],end,E.tostring(node,encoding='utf-8')))
  else:
   node.set('name','XCMate80.MediaRow');call=wrapper.find('include');wrapper.remove(call)
   caption=E.SubElement(wrapper,'control',type='label')
   for tag,value in (('left','130'),('top','0'),('width','1600'),('height','30'),('font','Bold22'),('label','$PARAM[widgetName]')):E.SubElement(caption,tag).text=value
   inner=E.SubElement(wrapper,'control',type='group');E.SubElement(inner,'top').text='34'
   call.set('content','XCMate80.NativeMediaBase');inner.append(call)
   at=data.rfind(b'</includes>');changes.append((at,at,E.tostring(node,encoding='utf-8')))
 # Own provider rows use the same native directory/click contract, without
 # the upstream unfocused fade or startup animation that hides populated VOD.
 for source,target in (('XCMate75.NativeMediaBase','XCMate80.NativeMediaBase'),('widget_base_normal','XCMate80.MediaNormal'),('WidgetBaseBingieIncludes','XCMate80.BaseBingie')):
  node=copy.deepcopy(parse(data).find("include[@name='"+source+"']"))
  if node is None:raise ValueError('UNVERIFIED_80_NATIVE_ROW')
  node.set('name',target)
  for parent in node.iter():
   for child in list(parent):
    if child.tag!='include':continue
    if child.get('content')=='widget_base_normal':child.set('content','XCMate80.MediaNormal')
    if child.get('content')=='WidgetBaseBingieIncludes':child.set('content','XCMate80.BaseBingie')
    if child.get('content')=='BingieUnfocusedWidgetFade' or child.text=='WidgetsBaseAnimation':parent.remove(child)
  at=data.rfind(b'</includes>');changes.append((at,at,E.tostring(node,encoding='utf-8')))
 result[name]=edit(data,changes)
 name='xml/IncludesHomeBingie.xml';data=result[name];n,end,rail=_node(data,'control','id','77777')
 if digest(rail)!=known['77777']:raise ValueError('UNVERIFIED_80_VIEWPORT')
 rail.find('top').text='500';rail.find('height').text='560';result[name]=edit(data,[(n['start'],end,E.tostring(rail,encoding='utf-8'))])
 name='xml/IncludesVariables.xml';data=result[name];at=data.rfind(b'</includes>');result[name]=data[:at]+b'<variable name="XCMate80.Contract"><value>XCMate80_READY</value></variable>'+data[at:]
 verify(result);return result

def verify(files):
 from widget_skin78 import parse
 root=parse(files['xml/IncludesHomeWidgets.xml']);main=root.find(".//control[@id='296751']");portrait=root.find(".//control[@id='296783']")
 if main is None or main.findtext('width')!='1620' or main.findtext('height')!='480' or portrait is None or portrait.findtext('aspectratio')!='keep':raise ValueError('UNVERIFIED_80_GEOMETRY')
 if MARKER not in files['xml/IncludesVariables.xml']:raise ValueError('UNVERIFIED_80_VARIABLES')
 if root.find("include[@name='XCMate80.MediaNormal']") is None:raise ValueError('UNVERIFIED_80_ROWS')
 return True
