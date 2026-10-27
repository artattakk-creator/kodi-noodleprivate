"""Existing Live widget -> same event DTO/art as the graphical programme view."""
import os
from localization import tr

def decorate(value,portal,channel,info):
 from programme_events46 import from_info,summary
 from programme_art46 import cached
 event=from_info(portal,channel,info or {});art=cached(event)
 logo=value['art'].get('thumb','');real=bool(logo) and os.path.basename(logo) not in ('tv.png','icon.png','icon-81da1003a2753ec6.png')
 image=art.get('image') or event['placeholder']
 value['art'].update(poster=image,thumb=image,landscape=image,fanart=image)
 props=value['props'];props.update({'XCMate.ProgrammeKey46':event['key'],'XCMate.ProgrammeImage46':image,'XCMate.ProgrammeLogo46':logo if real else '', 'XCMate.ProgrammeChannel46':event['channel'], 'XCMate.ProgrammeTitle46':event['title'] or tr(36102), 'XCMate.ProgrammeTimes46':((info.get('now_time','')+' – '+info.get('now_end_time','')) if event['title'] else ''),'XCMate.ProgrammeNext46':info.get('next',''),'XCMate.ProgrammeDescription46':event.get('description',''),'XCMate.ProgrammePercent46':str(round(info['progress']*100)) if event['title'] and isinstance(info.get('progress'),(int,float)) else '0', 'XCMate.ProgrammeDetails46':event['details_url'], 'XCMate.ProgrammeArtCode46':art.get('code','PENDING')})
 if event['title']:value['info']['title']=event['title']
 value['info']['plot']=summary(event)+'\n\n'+value['info']['plot']
 value['menus46']=[(tr(36100),'RunPlugin('+event['details_url']+')')]
 value['_programme46']=event
 return value
