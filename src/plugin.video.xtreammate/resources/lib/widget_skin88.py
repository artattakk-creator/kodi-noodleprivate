"""Cinematic full-width Hero: photo right, gradient/text left, native rows intact.

Only hash-verified released own Hero and menu glyph definitions change. SkinShortcuts, foreign rows,
paths, slots, global row visibility and user settings are not patch targets.
"""
import json
from pathlib import Path
import xml.etree.ElementTree as E
MARKER=b'XCMate88.Contract'
def setv(node,tag,value):
 child=node.find(tag)
 if child is None:child=E.SubElement(node,tag)
 child.text=str(value)
def variable_node(data,name):
 import re
 hits=list(re.finditer(rb'<variable name="'+re.escape(name.encode())+rb'">.*?</variable>',data,re.S))
 if len(hits)!=1:raise ValueError('SKIN_MIGRATION_BLOCKED')
 hit=hits[0];return dict(start=hit.start()),hit.end(),E.fromstring(hit[0])
def upgrade(files):
 if MARKER in files['xml/IncludesVariables.xml']:verify(files);return dict(files)
 if b'XCMate87.Contract' not in files['xml/IncludesVariables.xml']:return dict(files)
 from widget_skin80 import _node,digest
 from widget_skin50 import edit
 known=json.loads((Path(__file__).parents[1]/'bingie88_previous.json').read_text())
 name='xml/IncludesHomeWidgets.xml';data=files[name];span,end,hero=_node(data,'include','name','XCMate50.Hero')
 if digest(hero)!=known['XCMate50.Hero']:raise ValueError('SKIN_MIGRATION_BLOCKED')
 group=hero.find('control')
 bg=group.find('control')
 for tag,val in (('left',130),('width',1760)):setv(bg,tag,val)
 for ident in ('296751','296786','296886'):
  image=hero.find(".//control[@id='"+ident+"']")
  for tag,val in (('left',130),('width',1760),('height',620)):setv(image,tag,val)
  ratio=image.find('aspectratio');ratio.text='scale';ratio.set('align','right');ratio.set('aligny','center')
  tint=image.find('colordiffuse')
  if ident=='296751' and tint is not None:tint.text='FFFFFFFF'
 for ident,left,width in (('296783',970,800),('296784',1050,680)):
  image=hero.find(".//control[@id='"+ident+"']")
  for tag,val in (('left',left),('width',width),('top',30),('height',560)):setv(image,tag,val)
 panel=hero.find(".//control[@id='296750']")
 for tag,val in (('left',150),('width',760),('height',620)):setv(panel,tag,val)
 shade=panel.find("control[@type='image']")
 setv(shade,'visible','false')
 gradient=E.Element('control',type='image',id='296888')
 for tag,val in (('left',130),('top',0),('width',1760),('height',620),('texture','special://home/addons/plugin.video.xtreammate/resources/media/hero88/left-gradient.png'),('aspectratio','stretch')):setv(gradient,tag,val)
 group.insert(list(group).index(panel),gradient)
 for child in panel.findall('control'):
  if child is shade:continue
  if child.get('type')=='image':
   if 'tmdb60' in child.findtext('texture',''):
    for tag,val in (('left',540),('top',566),('width',180),('height',32)):setv(child,tag,val)
   else:
    for tag,val in (('left',580),('top',8),('width',140),('height',46)):setv(child,tag,val)
  else:
   setv(child,'width',700)
 title=hero.find(".//control[@id='296781']");setv(title,'font','Bold40');setv(title,'top',62);setv(title,'height',104)
 description=hero.find(".//control[@id='296782']");setv(description,'top',342);setv(description,'height',152)
 # Keep the taller title, Now/Next and metadata in separate vertical slots.
 for child in panel.findall('control'):
  label=child.findtext('label','')
  if 'ProgrammeChannel46' in label:setv(child,'width',300)
  elif '$VAR[XCMate63.Times]' in label:setv(child,'top',174)
  elif '$VAR[XCMate63.Remaining]' in label:setv(child,'top',206)
  elif child.get('type')=='progress':setv(child,'top',240)
  elif '$VAR[XCMate63.NextTimes]' in label:setv(child,'top',262)
  elif '$VAR[XCMate63.Subtitle]' in label:setv(child,'top',322)
  elif '$VAR[XCMate75.ImageCredit]' in label or '$VAR[XCMate75.DataCredit]' in label:setv(child,'width',500)
 setv(description,'top',354);setv(description,'height',142)
 rating=E.SubElement(panel,'control',type='label',id='296889')
 for tag,val in (('left',330),('top',10),('width',230),('height',30),('font','Bold22'),('textcolor','FFFFFFFF'),('label','$VAR[XCMate88.Rating]')):setv(rating,tag,val)
 status=hero.find(".//control[@id='296887']")
 for tag,val in (('left',170),('top',514),('width',700)):setv(status,tag,val)
 result=dict(files);result[name]=edit(data,[(span['start'],end,E.tostring(hero,encoding='utf-8'))])
 # Only the released own menu glyph definition/variable may change;
 # native/foreign menu actions and user fallback icons remain untouched.
 name='xml/IncludesBingie.xml';data=result[name];a,b,icons=_node(data,'include','name','Bingie_Menu_Icon_Defs')
 if digest(icons)!=known['Bingie_Menu_Icon_Defs']:raise ValueError('SKIN_MIGRATION_BLOCKED')
 setv(icons,'width',48);setv(icons,'height',48)
 result[name]=edit(data,[(a['start'],b,E.tostring(icons,encoding='utf-8'))])
 name='xml/IncludesVariables.xml';data=result[name];a,b,menu=variable_node(data,'XCMate75.MenuIcon')
 if digest(menu)!=known['XCMate75.MenuIcon']:raise ValueError('SKIN_MIGRATION_BLOCKED')
 labels={'device-tv':('Live TV',),'movie':('Movies',),'playlist':('TV Shows',),'search':('Search',),'settings':('Settings',),'heart':('Favorites','Favourites')}
 for value in menu.findall('value'):
  for asset,names in labels.items():
   if (value.text or '').endswith('/'+asset+'-normal.png'):
    value.set('condition',value.get('condition','')+' | '+' | '.join('String.IsEqual(ListItem.Label,'+label+')' for label in names))
 result[name]=data[:a['start']]+E.tostring(menu,encoding='utf-8')+data[b:]
 from widget_skin78 import parse
 parse(result[name])
 name='xml/IncludesVariables.xml';data=result[name];at=data.rfind(b'</includes>');rating_var=E.Element('variable',name='XCMate88.Rating')
 for bank in ('A','B'):
  condition='String.IsEqual(ListItem.Property(XCMate.WidgetKind41),live) + String.IsEqual(Window(Home).Property(XCMate.Hero63.Active),'+bank+') + String.IsEqual(Window(Home).Property(XCMate.Hero63.'+bank+'.Identity),ListItem.Property(XCMate.WidgetToken41)) + String.IsEqual(Window(Home).Property(XCMate.Hero63.'+bank+'.Profile),ListItem.Property(XCMate.EpgProfile63))'
  E.SubElement(rating_var,'value',condition=condition).text='$INFO[Window(Home).Property(XCMate.Hero63.'+bank+'.Rating88)]'
 E.SubElement(rating_var,'value').text=''
 result[name]=data[:at]+E.tostring(rating_var,encoding='utf-8')+b'<variable name="XCMate88.Contract"><value>READY</value></variable>'+data[at:]
 verify(result);return result
def verify(files):
 from widget_skin78 import parse
 hero=parse(files['xml/IncludesHomeWidgets.xml']).find("include[@name='XCMate50.Hero']")
 if hero is None or MARKER not in files['xml/IncludesVariables.xml']:raise ValueError('SKIN_MIGRATION_BLOCKED')
 image=hero.find(".//control[@id='296751']");panel=hero.find(".//control[@id='296750']")
 if [image.findtext(k) for k in ('left','width','height')]!=['130','1760','620'] or image.findtext('aspectratio')!='scale':raise ValueError('SKIN_MIGRATION_BLOCKED')
 if [panel.findtext(k) for k in ('left','width')]!=['150','760'] or panel.find("control[@type='image']/visible").text!='false':raise ValueError('SKIN_MIGRATION_BLOCKED')
 if hero.find(".//control[@id='296888']/texture") is None:raise ValueError('SKIN_MIGRATION_BLOCKED')
 for child in panel.findall('control'):
  if child.findtext('visible')=='false':continue
  if int(child.findtext('left','0'))+int(child.findtext('width','0'))>760 or int(child.findtext('top','0'))+int(child.findtext('height','0'))>620:raise ValueError('SKIN_MIGRATION_BLOCKED')
 icons=parse(files['xml/IncludesBingie.xml']).find("include[@name='Bingie_Menu_Icon_Defs']")
 if icons is None or (icons.findtext('width'),icons.findtext('height'))!=('48','48'):raise ValueError('SKIN_MIGRATION_BLOCKED')
 return True

def previous_owned(skin):
 """Recognize the released .87 own Hero; do not authorize a silent write."""
 from widget_skin78 import FILES,verify as graph_verify
 from widget_transaction50 import read
 from widget_skin80 import _node,digest
 try:
  files={name:read(Path(skin)/name) for name in FILES}
  if MARKER in files['xml/IncludesVariables.xml'] or b'XCMate87.Contract' not in files['xml/IncludesVariables.xml']:return False
  graph_verify(files);__import__('widget_skin87').verify(files)
  _,_,hero=_node(files['xml/IncludesHomeWidgets.xml'],'include','name','XCMate50.Hero')
  return digest(hero)==json.loads((Path(__file__).parents[1]/'bingie88_previous.json').read_text())['XCMate50.Hero']
 except (OSError,ValueError,KeyError,E.ParseError):return False
