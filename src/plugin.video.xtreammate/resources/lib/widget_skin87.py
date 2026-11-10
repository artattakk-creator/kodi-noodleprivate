"""Keep the approved 1080/540 image/table split and every native widget row.

Only the exact released own Hero is edited. No template limit, native row,
shortcut path/name/order, global visibility flag or Home regeneration changes.
"""
import json
from pathlib import Path
import xml.etree.ElementTree as E
MARKER=b'XCMate87.Contract'
def upgrade(files):
 if MARKER in files['xml/IncludesVariables.xml']:verify(files);return dict(files)
 if b'XCMate86.Contract' not in files['xml/IncludesVariables.xml']:return dict(files)
 from widget_skin80 import _node,digest
 from widget_skin50 import edit
 known=json.loads((Path(__file__).parents[1]/'bingie87_previous.json').read_text())
 name='xml/IncludesHomeWidgets.xml';data=files[name];span,end,hero=_node(data,'include','name','XCMate50.Hero')
 if digest(hero)!=known['XCMate50.Hero']:raise ValueError('SKIN_MIGRATION_BLOCKED')
 # No metadata/status labels over the left artwork. The optional compact
 # catalogue status is deferred to its existing completion notification.
 catalog=hero.find(".//control[@id='296785']")
 for v in list(catalog.findall('visible')):catalog.remove(v)
 E.SubElement(catalog,'visible').text='false'
 status=hero.find(".//control[@id='296887']")
 for tag,value in (('left','1370'),('top','514'),('width','500'),('height','28'),('font','Reg18')):status.find(tag).text=value
 proposal=hero.find(".//control[@id='296885']").findtext('visible')
 status.find('visible').text='!String.IsEmpty(Window(Home).Property(XCMate.Home86.Text)) + !['+proposal+']'
 # Share the small status slot only when no unconfirmed proposal is shown.
 result=dict(files);result[name]=edit(data,[(span['start'],end,E.tostring(hero,encoding='utf-8'))])
 name='xml/IncludesVariables.xml';data=result[name];at=data.rfind(b'</includes>')
 result[name]=data[:at]+b'<variable name="XCMate87.Contract"><value>READY</value></variable>'+data[at:]
 verify(result);return result

def verify(files):
 from widget_skin78 import parse
 root=parse(files['xml/IncludesHomeWidgets.xml']);hero=root.find("include[@name='XCMate50.Hero']")
 panel=hero.find(".//control[@id='296750']")
 if [panel.findtext(k) for k in ('left','width','height')]!=['1350','540','620']:raise ValueError('SKIN_MIGRATION_BLOCKED')
 if hero.find(".//control[@id='296751']/height").text!='620' or hero.find(".//control[@id='296783']/aspectratio").text!='keep':raise ValueError('SKIN_MIGRATION_BLOCKED')
 for control in panel.findall('control'):
  if int(control.findtext('left','0'))+int(control.findtext('width','0'))>540 or int(control.findtext('top','0'))+int(control.findtext('height','0'))>620:raise ValueError('SKIN_MIGRATION_BLOCKED')
 if hero.find(".//control[@id='296887']/left").text!='1370':raise ValueError('SKIN_MIGRATION_BLOCKED')
 return True
