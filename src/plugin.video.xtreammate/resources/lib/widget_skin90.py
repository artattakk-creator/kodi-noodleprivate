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
MEDIA_ROW_SHA='7480de9f92b11e973021acd9e971ccd2582b7c10e9b54ee36dbeb5b241f92679'
SPINNER_SHA='908ef49af8ef38afc70c66286162c67efd8d73fc70dafed5fc6c5b95dc602533'

def media_spinners(header,kinds=None,legacy=False):
 """Reuse the verified upstream animation inside our hidden-header rows.

 The existing Home85 worker status owns the 60-second deadline. Native
 IsUpdating alone may remain true after a failed directory: it cannot keep
 this indicator alive. No new worker, polling loop or settings are added.
 """
 from widget_skin80 import digest
 originals=header.findall(".//control[@type='multiimage']")
 if len(originals)!=1 or digest(originals[0])!=SPINNER_SHA:raise ValueError('MEDIA_SPINNER_UNVERIFIED')
 result=[]
 from widget_six_sources import SPECS
 for index,(kind,_,_,_) in enumerate(SPECS if kinds is None else SPECS[:kinds]):
  prefix=str(85+index)
  node=copy.deepcopy(originals[0]);node.set('id',prefix+'$PARAM[widgetid]')
  for child in list(node):
   if child.tag=='include':node.remove(child)
  for tag,text in (('width','24'),('height','24'),('top','2'),('left','0')):node.find(tag).text=text
  state='Window(Home).Property('+('XCMate.Home85.' if kind in ('vod','series') else 'XCMate.SixRows.')+kind+'.'
  # Typed caller metadata avoids embedding a clock-bearing directory URL
  # inside a compiled Kodi visibility expression, and works before items.
  namespace='XCMate.Home85.' if kind in ('vod','series') else 'XCMate.SixRows.'
  kind_info='Window(Home).Property('+namespace+'$PARAM[xcmateKind].Kind)'
  owned='[String.IsEqual('+kind_info+','+kind+') | String.IsEqual(Container($PARAM[widgetid]).ListItem.Property(XCMate.WidgetKind41),'+kind+')]'
  if legacy:owned='[String.IsEqual("$PARAM[xcmateKind]",'+kind+') | String.IsEqual(Container($PARAM[widgetid]).ListItem.Property(XCMate.WidgetKind41),'+kind+')]'
  loading=' | '.join('String.IsEqual('+state+'State),'+value+')' for value in ('LOADING_CATALOG','LOADING_ART','READY_PARTIAL','LOADING'))
  node.find('visible').text=owned+' + String.IsEqual('+state+'Busy),true) + [Container($PARAM[widgetid]).IsUpdating | '+loading+']'
  result.append(node)
 return result

def media_heading(title,header,kinds=None,legacy=False):
 """Let Kodi measure the saved label and place its spinner 12px after it."""
 group=E.Element('control',type='grouplist',id='84$PARAM[widgetid]')
 for tag,text in (('left','130'),('top','0'),('width','756'),('height','26'),
                  ('orientation','horizontal'),('itemgap','12'),('align','left')):
  E.SubElement(group,tag).text=text
 label=copy.deepcopy(title);label.find('left').text='0'
 width=label.find('width');width.text='auto';width.set('min','1');width.set('max','720')
 group.append(label);group.extend(media_spinners(header,kinds,legacy))
 return group

def original_media_row(row,header):
 """Fail closed on any unrelated geometry or animation edit."""
 from widget_skin80 import digest
 original=copy.deepcopy(row);group=original.find('control')
 params=original.findall("param[@name='xcmateKind']")
 if params:
  if len(params)!=1 or params[0].attrib!={'name':'xcmateKind','default':''}:raise ValueError('MEDIA_SPINNER_UNVERIFIED')
  original.remove(params[0])
 headings=group.findall("control[@id='84$PARAM[widgetid]']")
 if headings:
  if len(headings)!=1:raise ValueError('MEDIA_SPINNER_UNVERIFIED')
  heading=headings[0];titles=heading.findall("control[@type='label']")
  if len(titles)!=1:raise ValueError('MEDIA_SPINNER_UNVERIFIED')
  title=copy.deepcopy(titles[0]);title.find('left').text='130'
  title.find('width').text='720';title.find('width').attrib.clear()
  if digest(heading) not in (digest(media_heading(title,header)),digest(media_heading(title,header,None,True)),digest(media_heading(title,header,2,True))):
   # The first reviewed two-row variant had no generic LOADING phase.
   legacy=media_heading(title,header,2,True)
   for spinner in legacy.findall("control[@type='multiimage']"):
    condition=spinner.find('visible');condition.text=condition.text.replace(' | String.IsEqual(Window(Home).Property(XCMate.Home85.vod.State),LOADING)','').replace(' | String.IsEqual(Window(Home).Property(XCMate.Home85.series.State),LOADING)','')
   if digest(heading)!=digest(legacy):raise ValueError('MEDIA_SPINNER_UNVERIFIED')
  position=list(group).index(heading);group.remove(heading);group.insert(position,title)
 if digest(original)!=MEDIA_ROW_SHA:raise ValueError('MEDIA_SPINNER_UNVERIFIED')
 return original

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
 # Native Kodi repro: the original compiler + normal private consumer repair
 # delivers 24 items but the owned cold list stays hidden with zero items.
 # Removing this exact self-dependency alone admits both native media lists.
 # All outer menu/scope conditions and native/foreign row definitions remain.
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
 # Native sources need the same cold admission as our clone. In Kodi 21,
 # IsUpdating stays true for a completed directory until the GUI consumes it.
 # A visibility self-dependency can leave that result permanently unconsumed.
 prior=json.loads((Path(__file__).parents[1]/'bingie90_previous.json').read_text())['native_media90']
 n,end,node=_node(result[name],'include','name','widget_base_normal')
 control=node.find('control');matches=[v for v in control.findall('visible') if v.text==prior['condition']]
 if len(matches)==1:
  if digest(node)!=prior['sha256']:raise ValueError('NAV90_UNVERIFIED')
  control.remove(matches[0]);result[name]=edit(result[name],[(n['start'],end,E.tostring(node,encoding='utf-8'))])
 elif not matches:
  original=copy.deepcopy(node);gate=E.Element('visible');gate.text=prior['condition'];original.find('control').insert(prior['visible_index'],gate)
  if digest(original)!=prior['sha256']:raise ValueError('NAV90_UNVERIFIED')
 else:raise ValueError('NAV90_UNVERIFIED')
 # Kodi scrolls its last focusable child to the total grouplist extent.
 # Empty legacy wrappers otherwise retain 440px each and push the final
 # populated row entirely outside the viewport. Pending jobs stay active;
 # after consuming a genuinely empty result, the wrapper leaves the flow.
 # Keep identities, source paths, refresh hooks and geometry unchanged.
 prior=json.loads((Path(__file__).parents[1]/'bingie90_previous.json').read_text())['empty_native90']
 n,end,node=_node(result[name],'include','name','widget_base')
 control=node.find('control');matches=[v for v in control.findall('visible') if v.text==prior['condition']]
 original=copy.deepcopy(node)
 if matches:
  if len(matches)!=1:raise ValueError('NAV90_UNVERIFIED')
  original.find('control').remove(next(v for v in original.find('control').findall('visible') if v.text==prior['condition']))
 if digest(original)!=prior['sha256']:raise ValueError('NAV90_UNVERIFIED')
 if not matches:
  E.SubElement(control,'visible').text=prior['condition']
  result[name]=edit(result[name],[(n['start'],end,E.tostring(node,encoding='utf-8'))])
 # The upstream header (including its spinner) is deliberately suppressed for
 # own media rows. Keep their existing title/status/geometry, and port only
 # the original animation into that owned row under the bounded worker gate.
 n,end,row=_node(result[name],'include','name','XCMate80.MediaRow')
 _,_,header=_node(result[name],'include','name','widget_header_multi')
 original_media_row(row,header)
 group=row.find('control')
 # Keep this legacy include's plain body. Kodi requires a <definition>
 # wrapper when default declarations are added; mixing the two forms drops
 # the native list. The verified generated caller supplies xcmateKind.
 declared=row.find("param[@name='xcmateKind']")
 if declared is not None:row.remove(declared)
 headings=group.findall("control[@id='84$PARAM[widgetid]']")
 expected_title=original_media_row(row,header).find("control/control[@type='label']")
 missing=not headings or digest(headings[0])!=digest(media_heading(expected_title,header))
 if declared is not None or missing:
  if missing:
   if headings:
    position=list(group).index(headings[0]);title=original_media_row(row,header).find("control/control[@type='label']");group.remove(headings[0])
   else:
    title=group.find("control[@type='label']");position=list(group).index(title);group.remove(title)
   group.insert(position,media_heading(title,header))
  result[name]=edit(result[name],[(n['start'],end,E.tostring(row,encoding='utf-8'))])
 return __import__('widget_six_skin').upgrade(result)

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
