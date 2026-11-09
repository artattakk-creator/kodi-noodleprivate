"""Exact owned .81 graph -> large contained Hero and bounded EPG table.

Used only by existing backup/hashguard transaction. Personal/native row
bindings are never edited. An unknown installed node fails closed.
"""
import copy,json
from pathlib import Path
import xml.etree.ElementTree as E
MARKER=b'XCMate84.Contract'

def upgrade(original):
 if MARKER in original['xml/IncludesVariables.xml']:verify(original);return dict(original)
 from widget_skin80 import _node,digest
 from widget_skin50 import edit
 known=json.loads((Path(__file__).parents[1]/'bingie84_previous.json').read_text());result=dict(original)
 name='xml/IncludesHomeWidgets.xml';data=result[name];changes=[]
 for title in ('XCMate50.Hero','XCMate50.LiveRow','XCMate80.MediaRow'):
  span,end,node=_node(data,'include','name',title)
  if digest(node)!=known[title]:raise ValueError('UNVERIFIED_84_OWN_NODE')
  if title=='XCMate50.Hero':
   group=node.find('control');group.find('control/height').text='640'
   for ident in ('296751','296786'):
    image=node.find(".//control[@id='"+ident+"']");image.find('height').text='620'
    ratio=image.find('aspectratio');ratio.text='keep';ratio.set('align','left');ratio.set('aligny','center')
   portrait=node.find(".//control[@id='296783']");portrait.find('height').text='600'
   panel=node.find(".//control[@id='296750']");panel.find('height').text='620'
   for c in panel.findall('control'):
    ident=c.get('id');label=c.findtext('label','');texture=c.findtext('texture','')
    top,height=None,None
    if c.get('type')=='image':
     if c.findtext('width')=='540':top,height='0','620'
     elif 'ProgrammeLogo46' in texture:top,height='8','28'
     else:top,height='552','22'
    elif ident=='296781':top,height='46','92';c.find('font').text='Bold32'
    elif ident in ('296752','296753'):top,height='148','28'
    elif ident in ('296301','296302'):top,height='212','8'
    elif ident=='296782':top,height='326','206'
    elif 'ProgrammeChannel46' in label or ident=='296754':top,height='8','28';c.find('width').text='390'
    elif 'Remaining]' in label:top,height='182','24'
    elif 'NextTimes]' in label:top,height='232','58'
    elif 'Subtitle]' in label:top,height='296','24'
    elif 'ListItem.Duration' in label:top,height='184','108'
    elif 'ImageCredit]' in label:top,height='552','22'
    elif 'DataCredit]' in label:top,height='586','22'
    if top is not None:c.find('top').text=top;c.find('height').text=height
   shade=panel.find("control[@type='image']")
   shade.find('texture').text='special://home/addons/plugin.video.xtreammate/resources/media/panel84.png'
   shade.find('colordiffuse').text='FFFFFFFF'
   from widget_logo84 import condition
   logo_condition=condition()
   main=node.find(".//control[@id='296751']")
   logo=copy.deepcopy(main);logo.set('id','296784')
   for tag,value in (('left','480'),('top','160'),('width','560'),('height','280')):logo.find(tag).text=value
   logo.find('aspectratio').set('align','center')
   logo.find('colordiffuse').text='FFFFFFFF'
   for v in list(logo.findall('visible')):logo.remove(v)
   E.SubElement(logo,'visible').text=logo_condition
   E.SubElement(main,'visible').text='!['+logo_condition+']'
   E.SubElement(node.find(".//control[@id='296786']"),'visible').text='!['+logo_condition+']'
   group.insert(list(group).index(main)+1,logo)
  elif title=='XCMate80.MediaRow':
   node.find('control/height').text='244'
   node.find("control/control[@type='label']/height").text='26'
   node.find("control/control[@type='group']/top").text='30'
  changes.append((span['start'],end,E.tostring(node,encoding='utf-8')))
 result[name]=edit(data,changes)
 name='xml/IncludesHomeBingie.xml';data=result[name];span,end,node=_node(data,'control','id','77777')
 if digest(node)!=known['77777']:raise ValueError('UNVERIFIED_84_VIEWPORT')
 node.find('top').text='640';node.find('height').text='420'
 result[name]=edit(data,[(span['start'],end,E.tostring(node,encoding='utf-8'))])
 name='xml/IncludesVariables.xml';data=result[name];at=data.rfind(b'</includes>')
 result[name]=data[:at]+b'<variable name="XCMate84.Contract"><value>READY</value></variable>'+data[at:]
 verify(result);return result

def verify(files):
 from widget_skin78 import parse
 root=parse(files['xml/IncludesHomeWidgets.xml']);hero=root.find(".//control[@id='296751']")
 if hero is None or hero.findtext('height')!='620' or hero.findtext('width')!='1620' or hero.findtext('aspectratio')!='keep':raise ValueError('UNVERIFIED_84_GEOMETRY')
 rail=parse(files['xml/IncludesHomeBingie.xml']).find(".//control[@id='77777']")
 if rail is None or rail.findtext('top')!='640' or rail.findtext('height')!='420':raise ValueError('UNVERIFIED_84_VIEWPORT')
 panel=root.find(".//control[@id='296750']")
 for ident in ('296781','296782','296301','296302'):
  c=panel.find("control[@id='"+ident+"']")
  if c is None or int(c.findtext('top'))+int(c.findtext('height'))>620:raise ValueError('UNVERIFIED_84_OVERLAY')
 return True
