"""Restore native foreign-row focus factories in the released own adapter.

Two hash-reviewed .75 focus conditions and the owned media cold-load gate
change. Hero geometry, native row
definitions, saved properties, widget paths and menu order remain untouched.
Existing backed-up transaction/explicit confirmation owns any installation.
"""
import copy,json
from pathlib import Path
import xml.etree.ElementTree as E
TARGETS={'widget_header_multi':'String.IsEqual(Skin.String(HomeLayout),bingie)','WidgetBaseBingieIncludes':''}

def upgrade(files):
 if b'XCMate88.Contract' not in files['xml/IncludesVariables.xml']:return dict(files)
 from widget_skin50 import spans,edit
 from widget_skin80 import digest
 known=json.loads((Path(__file__).parents[1]/'bingie90_previous.json').read_text())['xml/IncludesHomeWidgets.xml']
 allowed={v['sha256'] for v in known};name='xml/IncludesHomeWidgets.xml';data=files[name];changes=[];seen=0;nodes=spans(data)
 for span in nodes:
  if span['tag']!='include' or span['attrs'].get('content')!='Fixed_Focus_Navigation_Factory':continue
  end=span['end']+len(b'</include>');node=E.fromstring(data[span['start']:end]);condition=node.get('condition','')
  parents=[n for n in nodes if n['tag']=='include' and n['attrs'].get('name') and n['start']<span['start']<n['end']]
  if not parents:raise ValueError('NAV90_UNVERIFIED')
  owner=min(parents,key=lambda n:n['end']-n['start'])['attrs']['name'];original=copy.deepcopy(node)
  target=TARGETS.get(owner)
  if target is not None and condition==target:
   original.set('condition','!Window.IsActive(Home)'+(' + ['+target+']' if target else ''))
  elif not condition.startswith('!Window.IsActive(Home)'):raise ValueError('NAV90_UNVERIFIED')
  if digest(original) not in allowed:raise ValueError('NAV90_UNVERIFIED')
  seen+=1
  if target is not None and condition!=target:
   if target:node.set('condition',target)
   else:node.attrib.pop('condition',None)
   changes.append((span['start'],end,E.tostring(node,encoding='utf-8')))
 if seen!=len(known):raise ValueError('NAV90_UNVERIFIED')
 result=dict(files)
 if changes:result[name]=edit(data,changes)
 # The original SkinShortcuts compiler uses the owned MediaRow, unlike
 # historical fixture templates. A cold native consumer has zero items and
 # is hidden until its own IsVisible/NumItems expression becomes true;
 # Kodi cannot publish that hidden list. Keep the outer menu/scope gates,
 # remove only this exactly reviewed self-dependency from the owned clone.
 from widget_skin80 import _node
 prior=json.loads((Path(__file__).parents[1]/'bingie90_previous.json').read_text())['owned_media90']
 n,end,node=_node(result[name],'include','name','XCMate80.MediaNormal')
 control=node.find('control');matches=[v for v in control.findall('visible') if v.text==prior['condition']]
 if len(matches)==1:
  if digest(node)!=prior['sha256']:raise ValueError('NAV90_UNVERIFIED')
  control.remove(matches[0]);result[name]=edit(result[name],[(n['start'],end,E.tostring(node,encoding='utf-8'))])
 elif not matches:
  original=copy.deepcopy(node);gate=E.Element('visible');gate.text=prior['condition'];original.find('control').insert(prior['visible_index'],gate)
  if digest(original)!=prior['sha256']:raise ValueError('NAV90_UNVERIFIED')
 else:raise ValueError('NAV90_UNVERIFIED')
 return result

def verify(files):
 return upgrade(files)==files

def previous_owned(skin):
 from widget_skin78 import FILES,verify as graph_verify
 from widget_transaction50 import read
 try:
  files={name:read(Path(skin)/name) for name in FILES}
  if b'XCMate88.Contract' not in files['xml/IncludesVariables.xml']:return False
  graph_verify(files);__import__('widget_skin88').verify(files)
  return upgrade(files)!=files
 except (OSError,ValueError,KeyError,E.ParseError):return False
