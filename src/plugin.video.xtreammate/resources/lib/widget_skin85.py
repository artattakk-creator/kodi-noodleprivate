"""Exact owned .84 nodes -> stable loading labels and marked suggestions.

No external/personal widget row or path is replaced. Existing guarded updater
owns backup, preview, activation and rollback.
"""
import copy,json
from pathlib import Path
import xml.etree.ElementTree as E
MARKER=b'XCMate85.Contract'
def element(parent,kind,values,ident=None):
 c=E.SubElement(parent,'control',type=kind,**({'id':ident} if ident else {}))
 for tag,text in values:E.SubElement(c,tag).text=text
 return c
def upgrade(files):
 if MARKER in files['xml/IncludesVariables.xml']:verify(files);return __import__('widget_skin86').upgrade(files)
 if b'XCMate84.Contract' not in files['xml/IncludesVariables.xml']:return dict(files)
 from widget_skin80 import _node,digest
 from widget_skin50 import edit
 from widget_skin78 import parse
 known=json.loads((Path(__file__).parents[1]/'bingie85_previous.json').read_text());result=dict(files)
 name='xml/IncludesHomeWidgets.xml';data=result[name];changes=[]
 for title in ('XCMate50.Hero','XCMate80.MediaRow','XCMate81.PosterRow'):
  span,end,node=_node(data,'include','name',title)
  if digest(node)!=known[title]:raise ValueError('UNVERIFIED_85_OWN_NODE')
  if title=='XCMate50.Hero':
   panel=node.find(".//control[@id='296750']");description=panel.find("control[@id='296782']");description.find('height').text='180'
   element(panel,'label',[('left','20'),('top','514'),('width','500'),('height','28'),('font','Reg18'),('textcolor','FFFFD59A'),('label','Bildvorschlag – Zuordnung nicht bestätigt'),('visible','false')],ident='296885')
  elif title=='XCMate80.MediaRow':
   group=node.find('control');group.find("control[@type='label']/width").text='720'
   for kind,action in (('vod','widget_recent_vod'),('series','widget_recent_series')):
    condition='[String.Contains($PARAM[widgetPath],action='+action+') | String.IsEqual(Container($PARAM[widgetid]).ListItem.Property(XCMate.WidgetKind41),'+kind+')]'
    element(group,'label',[('left','900'),('top','2'),('width','860'),('height','24'),('font','Reg18'),('textcolor','FFBCC7D2'),('label','$INFO[Window(Home).Property(XCMate.Home85.'+kind+'.Text)]'),('visible',condition+' + !String.IsEmpty(Window(Home).Property(XCMate.Home85.'+kind+'.Text))')])
  else:
   for layout in ('itemlayout','focusedlayout'):
    row=node.find(layout);image=row.find("control[@type='image']")
    E.SubElement(image,'visible').text='!String.IsEmpty(ListItem.Art(poster)) + !String.Contains(ListItem.Art(poster),resources/media/vod.png) + !String.Contains(ListItem.Art(poster),resources/media/series.png)'
    background=E.Element('control',type='image')
    for tag,text in [('width','120'),('height','180'),('texture','special://home/addons/plugin.video.xtreammate/resources/media/panel84.png')]:E.SubElement(background,tag).text=text
    row.insert(0,background)
  changes.append((span['start'],end,E.tostring(node,encoding='utf-8')))
 result[name]=edit(data,changes)
 name='xml/IncludesVariables.xml';data=result[name];at=data.rfind(b'</includes>')
 # Reuse the existing A/B identity+profile guards, including row fallback.
 proposal=copy.deepcopy(parse(data).find("variable[@name='XCMate63.ArtSource']"))
 if proposal is None:raise ValueError('MISSING_85_BANK_TEMPLATE')
 proposal.set('name','XCMate85.Provisional')
 for value in proposal.findall('value'):
  value.text=(value.text or '').replace('.ArtSource','.Provisional85').replace('XCMate.ProgrammeArtSource57','XCMate.Provisional85').replace('XCMate.HeroArtSource63','XCMate.Provisional85')
 # Boolean skin conditions resolve infolabels, not $VAR label expansion.
 # Match the existing bank/profile/token guards explicitly. A current bank
 # with an empty flag must win over any stale selected-row proposal.
 guarded=[];branches=[]
 for value in proposal.findall('value'):
  condition=value.get('condition');field=(value.text or '').removeprefix('$INFO[').removesuffix(']')
  if condition:
   guarded.append('['+condition+']');branches.append('['+condition+' + String.IsEqual('+field+',true)]')
  else:branches.append('[!['+' | '.join(guarded)+'] + String.IsEqual('+field+',true)]')
 visible=' | '.join(branches)
 # Preserve original non-owned bytes by replacing only the exact owned Hero.
 start85,end85,node85=_node(result['xml/IncludesHomeWidgets.xml'],'include','name','XCMate50.Hero')
 node85.find(".//control[@id='296885']/visible").text=visible
 result['xml/IncludesHomeWidgets.xml']=edit(result['xml/IncludesHomeWidgets.xml'],[(start85['start'],end85,E.tostring(node85,encoding='utf-8'))])
 data=data[:at]+E.tostring(proposal,encoding='utf-8')+data[at:];at=data.rfind(b'</includes>')
 result[name]=data[:at]+b'<variable name="XCMate85.Contract"><value>READY</value></variable>'+data[at:]
 verify(result);return __import__('widget_skin86').upgrade(result)
def verify(files):
 from widget_skin78 import parse
 root=parse(files['xml/IncludesHomeWidgets.xml'])
 if parse(files['xml/IncludesVariables.xml']).find("variable[@name='XCMate85.Provisional']") is None:raise ValueError('MISSING_85_BANK_LABEL')
 if root.find(".//control[@id='296885']") is None:raise ValueError('MISSING_85_SUGGESTION_LABEL')
 if b'XCMate.Home85.vod.Text' not in files['xml/IncludesHomeWidgets.xml'] or b'XCMate.Home85.series.Text' not in files['xml/IncludesHomeWidgets.xml']:raise ValueError('MISSING_85_LOADING')
 hero=root.find(".//control[@id='296751']")
 if hero.findtext('height')!='620' or hero.findtext('width')!='1620':raise ValueError('UNVERIFIED_85_HERO')
 return True
