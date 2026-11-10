"""Exact .85 owned Hero upgrade; native/user rows and shortcut bytes preserved."""
import copy,json
from pathlib import Path
import xml.etree.ElementTree as E
MARKER=b'XCMate86.Contract'
def upgrade(files):
 if MARKER in files['xml/IncludesVariables.xml']:verify(files);return dict(files)
 if b'XCMate85.Contract' not in files['xml/IncludesVariables.xml']:return dict(files)
 from widget_skin80 import _node,digest,PORTRAIT
 from widget_skin50 import edit
 from widget_skin78 import parse
 known=json.loads((Path(__file__).parents[1]/'bingie86_previous.json').read_text())
 result=dict(files);name='xml/IncludesHomeWidgets.xml';data=result[name]
 span,end,hero=_node(data,'include','name','XCMate50.Hero')
 if digest(hero)!=known['XCMate50.Hero']:raise ValueError('UNVERIFIED_86_HERO')
 group=hero.find('control');main=hero.find(".//control[@id='296751']")
 # Kodi actually processes this underlay texture before the bank is switched.
 preload=copy.deepcopy(main);preload.set('id','296886')
 preload.find('texture').text='$INFO[Window(Home).Property(XCMate.Hero86.Pending)]'
 for v in list(preload.findall('visible')):preload.remove(v)
 E.SubElement(preload,'visible').text='!String.IsEmpty(Window(Home).Property(XCMate.Hero86.Pending))'
 preload.find('colordiffuse').text='01FFFFFF'
 group.insert(list(group).index(main),preload)
 prior=hero.find(".//control[@id='296786']")
 for v in list(prior.findall('visible')):prior.remove(v)
 E.SubElement(prior,'visible').text='!String.IsEmpty(Window(Home).Property(XCMate.Hero81.PreviousImage)) + String.IsEqual(Window(Home).Property(XCMate.Hero86.PreviousEvent),Window(Home).Property(XCMate.Hero86.Event))'
 portrait=hero.find(".//control[@id='296783']")
 condition='['+PORTRAIT+'] | [String.IsEqual(ListItem.Property(XCMate.WidgetKind41),live) + String.IsEqual($VAR[XCMate86.Kind],official_poster)]'
 # $VAR does not expand in skin bools. Build guarded infolabel conditions.
 template=copy.deepcopy(parse(result['xml/IncludesVariables.xml']).find("variable[@name='XCMate63.ArtSource']"))
 template.set('name','XCMate86.Kind');branches=[];guarded=[]
 for value in template.findall('value'):
  value.text=(value.text or '').replace('.ArtSource','.Kind86').replace('XCMate.ProgrammeArtSource57','XCMate.HeroKind86').replace('XCMate.HeroArtSource63','XCMate.HeroKind86')
  field=(value.text or '').removeprefix('$INFO[').removesuffix(']');guard=value.get('condition')
  if guard:guarded.append('['+guard+']');branches.append('['+guard+' + String.IsEqual('+field+',official_poster)]')
  else:branches.append('[!['+' | '.join(guarded)+'] + String.IsEqual('+field+',official_poster)]')
 liveposter='String.IsEqual(ListItem.Property(XCMate.WidgetKind41),live) + ['+' | '.join(branches)+']'
 for v in list(portrait.findall('visible')):portrait.remove(v)
 E.SubElement(portrait,'visible').text='['+PORTRAIT+'] | ['+liveposter+']'
 for tag,text in (('left','180'),('top','12'),('width','900'),('height','596')):portrait.find(tag).text=text
 portrait.find('aspectratio').text='keep';portrait.find('aspectratio').set('align','center')
 E.SubElement(main,'visible').text='!['+liveposter+']'
 status=E.SubElement(group,'control',type='label',id='296887')
 for tag,text in [('left','280'),('top','606'),('width','1000'),('height','20'),('font','Reg18'),('textcolor','FFBCC7D2'),('label','$INFO[Window(Home).Property(XCMate.Home86.Text)]'),('visible','!String.IsEmpty(Window(Home).Property(XCMate.Home86.Text))')]:E.SubElement(status,tag).text=text
 result[name]=edit(data,[(span['start'],end,E.tostring(hero,encoding='utf-8'))])
 name='xml/IncludesVariables.xml';data=result[name];at=data.rfind(b'</includes>')
 result[name]=data[:at]+E.tostring(template,encoding='utf-8')+b'<variable name="XCMate86.Contract"><value>READY</value></variable>'+data[at:]
 verify(result);return result

def verify(files):
 from widget_skin78 import parse
 root=parse(files['xml/IncludesHomeWidgets.xml'])
 if root.find(".//control[@id='296886']") is None or root.find(".//control[@id='296887']") is None:raise ValueError('MISSING_86_PRELOAD_STATUS')
 if root.find(".//control[@id='296751']/height").text!='620':raise ValueError('UNVERIFIED_86_GEOMETRY')
 if parse(files['xml/IncludesVariables.xml']).find("variable[@name='XCMate86.Kind']") is None:raise ValueError('MISSING_86_KIND')
 return True
