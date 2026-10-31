"""Known .63 -> .64 only. Local media focus frames, no saved binding edits."""
import copy,json
from pathlib import Path
import xml.etree.ElementTree as E
OWN='[String.IsEqual(ListItem.Property(XCMate.WidgetKind41),vod) | String.IsEqual(ListItem.Property(XCMate.WidgetKind41),series)]'
def previous_candidate(path,data):
 from widget_skin63 import candidate,previous_candidate as legacy
 return candidate(path,data,legacy)
def candidate(path,data,previous):
 from widget_transaction50 import read,sha
 from widget_skin50 import spans,edit
 root=Path(__file__).parents[1]
 known=json.loads(read(root/'bingie64_previous.json'))['files']
 if sha(data)!=known.get(path):data=previous(path,data)
 if path=='xml/IncludesHomeWidgets.xml':
  nodes=spans(data);changes=[]
  definitions=E.fromstring(read(root/'bingie64/IncludesXCMate64.xml'))
  definition=definitions.find("include[@name='XCMate50.Hero']")
  matches=[n for n in nodes if n['tag']=='include' and n['attrs'].get('name')=='XCMate50.Hero']
  if len(matches)!=1:raise ValueError('UNVERIFIED_HERO_REGION')
  node=matches[0];changes.append((node['start'],node['end']+len(b'</include>'),E.tostring(definition,encoding='utf-8')))
  extra=definitions.find("variable[@name='XCMate64.Image']")
  end=data.rfind(b'</includes>');changes.append((end,end,E.tostring(extra,encoding='utf-8')+b'\n'))
  live=[n for n in nodes if n['tag']=='include' and n['attrs'].get('name')=='XCMate50.LiveRow']
  if len(live)!=1:raise ValueError('UNVERIFIED_LIVE_REGION')
  focus=[n for n in nodes if n['tag']=='control' and n['attrs'].get('type')=='image' and live[0]['start']<n['start']<n['end']<live[0]['end'] and b'programme55/focus.png' in data[n['start']:n['end']]]
  if len(focus)!=1:raise ValueError('UNVERIFIED_LIVE_FOCUS')
  changes.append((focus[0]['open'],focus[0]['open'],b'<visible>Control.HasFocus($PARAM[widgetid])</visible>'))
  count=0
  for layout in [n for n in nodes if n['tag']=='focusedlayout']:
   for group in [g for g in nodes if g['tag']=='control' and g['attrs'].get('type')=='group' and layout['start']<g['start']<g['end']<layout['end']]:
    width=next((v['text'] for v in group['children'] if v['tag']=='width'),None)
    height=next((v['text'] for v in group['children'] if v['tag']=='height'),None)
    if not width or not height:continue
    for image in [n for n in group['children'] if n['tag']=='control' and n['attrs'].get('type')=='image']:
     includes=[n['text'] for n in image['children'] if n['tag']=='include']
     if 'thumbsborder_focused' not in includes or not any('FO_Defs' in v for v in includes):continue
     stop=image['end']+len(b'</control>');raw=data[image['start']:stop]
     original=E.fromstring(raw);own=copy.deepcopy(original)
     for v in list(own.findall('visible')):own.remove(v)
     E.SubElement(own,'visible').text='Control.HasFocus($PARAM[widgetid]) + '+OWN
     for tag,value in (('width',width),('height',height)):
      for v in list(own.findall(tag)):own.remove(v)
      E.SubElement(own,tag).text=value
     for inc in list(own.findall('include')):
      if inc.text and ('FO_Defs' in inc.text or inc.text=='thumbsborder_focused'):own.remove(inc)
     texture=E.SubElement(own,'texture',border='9');texture.text='special://home/addons/plugin.video.xtreammate/resources/media/programme55/focus.png'
     E.SubElement(own,'aspectratio').text='stretch'
     E.SubElement(own,'colordiffuse').text='FFFFFFFF'
     E.SubElement(original,'visible').text='!'+OWN
     changes.append((image['start'],stop,E.tostring(original,encoding='utf-8')+E.tostring(own,encoding='utf-8')));count+=1
  if not 2<=count<=32:raise ValueError('UNVERIFIED_FOCUS_REGIONS')
  return edit(data,changes)
 if path=='xml/IncludesHomeBingie.xml':
  changes=[];nodes=spans(data)
  for group in [n for n in nodes if n['tag']=='control' and n['attrs'].get('type')=='group']:
   if not any(v['tag']=='include' and (v['attrs'].get('content','') or v['text']).startswith('Bingie_Screens_Fixed_Focus_Frame') for v in group['children']):continue
   changes.append((group['open'],group['open'],('<visible>!'+OWN+'</visible>').encode()))
  if not 2<=len(changes)<=8:raise ValueError('UNVERIFIED_FOCUS_REGIONS')
  return edit(data,changes)
 return data
def previously_applied(skin):
 from widget_skin50 import guard,FILES
 from widget_transaction50 import read,sha
 try:
  known=json.loads(read(Path(__file__).parents[1]/'bingie64_previous.json'))['files']
  return all(sha(read(p))==known[name] for name,p in zip(FILES,guard(skin)))
 except (OSError,ValueError,KeyError):return False
