"""Exact opt-in .65 adapter upgrade: native item-bound frames for every widget."""
import json
from pathlib import Path
import xml.etree.ElementTree as E
def previous_candidate(path,data):
 from widget_skin64 import candidate,previous_candidate as previous
 return candidate(path,data,previous)
def candidate(path,data):
 from widget_skin50 import spans,edit
 from widget_transaction50 import read,sha
 known=json.loads(read(Path(__file__).parents[1]/'bingie66_previous.json'))['files']
 if sha(data)!=known.get(path):data=previous_candidate(path,data)
 nodes=spans(data);changes=[]
 if path=='xml/IncludesHomeWidgets.xml':
  count=0
  for layout in [n for n in nodes if n['tag']=='focusedlayout']:
   for group in [n for n in nodes if n['tag']=='control' and n['attrs'].get('type')=='group' and layout['start']<n['start']<n['end']<layout['end']]:
    width=next((n['text'] for n in group['children'] if n['tag']=='width'),None);height=next((n['text'] for n in group['children'] if n['tag']=='height'),None)
    if not width or not height:continue
    for image in [n for n in group['children'] if n['tag']=='control' and n['attrs'].get('type')=='image']:
     includes=[n['text'] for n in image['children'] if n['tag']=='include']
     if 'thumbsborder_focused' not in includes or not any('FO_Defs' in value for value in includes):continue
     stop=image['end']+len(b'</control>');node=E.fromstring(data[image['start']:stop])
     from widget_skin64 import OWN
     for v in list(node.findall('visible')):node.remove(v)
     E.SubElement(node,'visible').text='Control.HasFocus($PARAM[widgetid]) + !'+OWN
     for tag,value in (('width',width),('height',height)):
      for v in list(node.findall(tag)):node.remove(v)
      E.SubElement(node,tag).text=value
     changes.append((image['start'],stop,E.tostring(node,encoding='utf-8')));count+=1
  if not 2<=count<=32:raise ValueError('UNVERIFIED_FOCUS_REGIONS')
  for node in nodes:
   if node['tag']=='include' and node['attrs'].get('content')=='SetFixedVerticalNavigationProps':
    changes.append((node['start'],node['open'],data[node['start']:node['open']].replace(b'content="SetFixedVerticalNavigationProps"',b'content="XCMate66.VerticalFocus"')))
  definition=b'<include name="XCMate66.VerticalFocus"><onfocus condition="!String.IsEqual(Window(Home).Property(CurrentWidgetID),$PARAM[widgetid])">SetProperty(PrevWidgetPos,$INFO[Window(Home).Property(CurrentWidgetPos)],Home)</onfocus><onfocus>SetProperty(CurrentWidgetPos,$INFO[Container(77777).CurrentItem],Home)</onfocus><onfocus>SetProperty(CurrentWidgetID,$PARAM[widgetid],Home)</onfocus></include>\n'
  end=data.rfind(b'</includes>');changes.append((end,end,definition))
 elif path=='xml/IncludesHomeBingie.xml':
  count=0
  for group in [n for n in nodes if n['tag']=='control' and n['attrs'].get('type')=='group']:
   if any(n['tag']=='include' and (n['attrs'].get('content','') or n['text']).startswith('Bingie_Screens_Fixed_Focus_Frame') for n in group['children']):
    changes.append((group['open'],group['open'],b'<visible>!ControlGroup(77777).HasFocus()</visible>'));count+=1
  if not 2<=count<=8:raise ValueError('UNVERIFIED_FOCUS_REGIONS')
  plots=[n for n in nodes if n['tag']=='control' and n['attrs'].get('id')=='90009']
  if len(plots)!=1:raise ValueError('UNVERIFIED_PLOT_REGION')
  plot=plots[0];stop=plot['end']+len(b'</control>');node=E.fromstring(data[plot['start']:stop])
  for tag in ('height','autoscroll','font','aligny'):
   for value in list(node.findall(tag)):node.remove(value)
  E.SubElement(node,'height').text='84';E.SubElement(node,'autoscroll').text='false';E.SubElement(node,'font').text='Reg22';E.SubElement(node,'aligny').text='top'
  changes.append((plot['start'],stop,E.tostring(node,encoding='utf-8')))
 return edit(data,changes) if changes else data
def previously_applied(skin):
 from widget_skin50 import guard,FILES
 from widget_transaction50 import read,sha
 try:
  known=json.loads(read(Path(__file__).parents[1]/'bingie66_previous.json'))['files']
  if all(sha(read(p))==known[name] for name,p in zip(FILES,guard(skin))):return True
 except (OSError,ValueError,KeyError):return False
 from widget_skin64 import previously_applied as legacy
 return legacy(skin)
