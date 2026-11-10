"""Cinematic full-width Hero: photo right, gradient/text left, native rows intact.

Only the hash-verified released own Hero changes. SkinShortcuts, foreign rows,
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
 status=hero.find(".//control[@id='296887']")
 for tag,val in (('left',170),('top',514),('width',700)):setv(status,tag,val)
 result=dict(files);result[name]=edit(data,[(span['start'],end,E.tostring(hero,encoding='utf-8'))])
 name='xml/IncludesVariables.xml';data=result[name];at=data.rfind(b'</includes>');result[name]=data[:at]+b'<variable name="XCMate88.Contract"><value>READY</value></variable>'+data[at:]
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
 return True
