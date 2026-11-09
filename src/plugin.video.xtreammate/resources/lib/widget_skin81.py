"""Digest-guarded upgrade of owned .80 Hero and own media rows only."""
import copy,json,re
from pathlib import Path
import xml.etree.ElementTree as E
MARKER=b'XCMate81.Contract'

def credit_node(data):
 matches=list(re.finditer(rb'<variable name="XCMate75.ImageCredit">.*?</variable>',data,re.S))
 if len(matches)!=1:raise ValueError('UNVERIFIED_81_SOURCE_CREDIT')
 hit=matches[0]
 return dict(start=hit.start()),hit.end(),E.fromstring(hit[0])

def upgrade(original):
 if b'XCMate84.Contract' in original['xml/IncludesVariables.xml']:
  __import__('widget_skin84').verify(original);return __import__('widget_skin85').upgrade(original)
 if MARKER in original['xml/IncludesVariables.xml']:verify(original);return __import__('widget_skin85').upgrade(__import__('widget_skin84').upgrade(original))
 if b'XCMate80.Contract' not in original['xml/IncludesVariables.xml']:return dict(original)
 from widget_skin80 import _node,digest,PORTRAIT
 from widget_skin50 import edit
 known=json.loads((Path(__file__).parents[1]/'bingie81_previous.json').read_text());result=dict(original);name='xml/IncludesHomeWidgets.xml';data=result[name];changes=[]
 for title in ('XCMate50.Hero','XCMate50.LiveRow','XCMate80.MediaRow','XCMate80.MediaNormal'):
  span,end,node=_node(data,'include','name',title)
  if digest(node)!=known[title]:raise ValueError('UNVERIFIED_81_OWN_NODE')
  if title=='XCMate50.Hero':
   main=node.find(".//control[@id='296751']");main.find('height').text='400'
   prior=copy.deepcopy(main);prior.set('id','296786');prior.find('texture').text='$INFO[Window(Home).Property(XCMate.Hero81.PreviousImage)]'
   for visible81 in list(prior.findall('visible')):prior.remove(visible81)
   E.SubElement(prior,'visible').text='!String.IsEmpty(Window(Home).Property(XCMate.Hero81.PreviousImage))'
   group81=node.find('control');group81.insert(list(group81).index(main),prior)
   for v in list(main.findall('visible')):main.remove(v)
   E.SubElement(main,'colordiffuse').text='$VAR[XCMate81.BackgroundTint]'
   portrait=node.find(".//control[@id='296783']")
   for tag,val in (('left','540'),('top','10'),('width','740'),('height','380')):portrait.find(tag).text=val
   node.find('control/control/height').text='420'
   panel=node.find(".//control[@id='296750']");panel.find('height').text='400'
   for child in panel.findall('.//control'):
    for tag in ('top','height'):
     v=child.find(tag)
     if v is not None and (v.text or '').isdigit():v.text=str(round(int(v.text)*400/480))
   shade=panel.find("control[@type='image']/texture");shade.text='special://home/addons/plugin.video.xtreammate/resources/media/media_detail_gradient.png'
   colour=panel.find("control[@type='image']/colordiffuse")
   if colour is not None:colour.text='88FFFFFF'
  elif title=='XCMate50.LiveRow':node.find('control/height').text='80'
  elif title=='XCMate80.MediaRow':node.find('control/height').text='268'
  else:
   call=next(c for c in node.iter('include') if c.get('content')=='$PARAM[widgetStyle]');call.set('content','XCMate81.PosterRow')
  if title=='XCMate50.Hero':
   status=E.SubElement(node.find('control'),'control',type='label',id='296785')
   for tag,val in (('left','280'),('top','3'),('width','1000'),('height','20'),('font','Reg18'),('label','$INFO[Window(Home).Property(XCMate.Catalog81.Text)]'),('visible','!String.IsEmpty(Window(Home).Property(XCMate.Catalog81.Text))')):E.SubElement(status,tag).text=val
  changes.append((span['start'],end,E.tostring(node,encoding='utf-8')))
 style=E.Element('include',name='XCMate81.PosterRow')
 for tag,value in (('left','130'),('height','208')):E.SubElement(style,tag).text=value
 for layout in ('itemlayout','focusedlayout'):
  layoutnode=E.SubElement(style,layout,width='140',height='208')
  image=E.SubElement(layoutnode,'control',type='image')
  for tag,value in (('left','0'),('top','0'),('width','120'),('height','180'),('aspectratio','keep'),('texture','$INFO[ListItem.Art(poster)]')):E.SubElement(image,tag).text=value
  label=E.SubElement(layoutnode,'control',type='label')
  for tag,value in (('left','0'),('top','182'),('width','124'),('height','24'),('font','Reg18'),('label','$INFO[ListItem.Label]')):E.SubElement(label,tag).text=value
  if layout=='focusedlayout':
   frame=E.SubElement(layoutnode,'control',type='image')
   for tag,value in (('left','-4'),('top','-4'),('width','128'),('height','188')):E.SubElement(frame,tag).text=value
   E.SubElement(frame,'visible').text='Control.HasFocus($PARAM[widgetid])'
   E.SubElement(frame,'texture',border='4').text='special://home/addons/plugin.video.xtreammate/resources/media/rail_focus81.png'
 at=data.rfind(b'</includes>');changes.append((at,at,E.tostring(style,encoding='utf-8')));result[name]=edit(data,changes)
 name='xml/IncludesHomeBingie.xml';data=result[name];span,end,node=_node(data,'control','id','77777')
 if digest(node)!=known['77777']:raise ValueError('UNVERIFIED_81_VIEWPORT')
 node.find('top').text='420';node.find('height').text='640';result[name]=edit(data,[(span['start'],end,E.tostring(node,encoding='utf-8'))])
 name='xml/IncludesVariables.xml';data=result[name]
 span81,end81,credit81=credit_node(data)
 if digest(credit81)!=known['ImageCredit']:raise ValueError('UNVERIFIED_81_SOURCE_CREDIT')
 value81=E.Element('value',condition='String.IsEqual(ListItem.Property(XCMate.MediaHeroSource81),TMDB)');value81.text='Bild: TMDB';credit81.insert(0,value81)
 data=data[:span81['start']]+E.tostring(credit81,encoding='utf-8')+data[end81:];at=data.rfind(b'</includes>')
 extra=E.Element('variable',name='XCMate81.BackgroundTint');E.SubElement(extra,'value',condition=PORTRAIT).text='55FFFFFF';E.SubElement(extra,'value').text='FFFFFFFF'
 result[name]=data[:at]+E.tostring(extra,encoding='utf-8')+b'<variable name="XCMate81.Contract"><value>READY</value></variable>'+data[at:]
 verify(result);return __import__('widget_skin85').upgrade(__import__('widget_skin84').upgrade(result))

def verify(files):
 if b'XCMate85.Contract' in files['xml/IncludesVariables.xml']:return __import__('widget_skin85').verify(files)
 if b'XCMate84.Contract' in files['xml/IncludesVariables.xml']:return __import__('widget_skin84').verify(files)
 from widget_skin78 import parse
 root=parse(files['xml/IncludesHomeWidgets.xml'])
 if root.find(".//control[@id='296751']/height").text!='400' or root.find("include[@name='XCMate81.PosterRow']") is None:raise ValueError('UNVERIFIED_81_GEOMETRY')
 return True
