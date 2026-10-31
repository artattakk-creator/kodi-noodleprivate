"""Authoritative local EPG text survives any optional artwork/metadata failure."""
import os,time
from urllib.parse import urlencode

def apply(item,portal,row,info,event=None):
    from epg_handoff63 import profile_scope
    item['props']['XCMate.EpgProfile63']=profile_scope()
    if not isinstance(info,dict):return item
    from localization import tr
    import xbmcaddon
    props=item['props'];key=str(info.get('programme_key47') or '')
    # An optional renderer may straddle a programme transition. Never combine
    # the old text with a different programme's picture.
    if props.get('XCMate.ProgrammeKey47','')!=key:
        props['XCMate.ProgrammeImage46']=os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources','media','programme46','neutral.png')
        for field in ('XCMate.ProgrammeArtSource57','XCMate.ProgrammeArtCredit57'):props[field]=''
    now=bool(info.get('now'));event=event if isinstance(event,dict) and event.get('key')==key else {}
    subtitle=str(event.get('subtitle') or '')
    if type(event.get('season')) is int and type(event.get('episode')) is int:
        subtitle=('S%02d E%02d'%(event['season'],event['episode']))+(' – '+subtitle if subtitle else '')
    props.update({'XCMate.ProgrammeTitle46':str(info.get('now') or tr(36102)),
        'XCMate.ProgrammeTimes46':(info.get('now_time','')+' – '+info.get('now_end_time','')) if now else '',
        'XCMate.ProgrammeNext46':str(info.get('next') or ''),
        'XCMate.ProgrammeNextTimes48':(info.get('next_time','')+' – '+info.get('next_end_time','')) if info.get('next') else '',
        'XCMate.ProgrammeDescription46':str(info.get('description') or event.get('description') or '')[:8192],
        'XCMate.ProgrammePercent46':str(round(info['progress']*100)) if now and type(info.get('progress')) in (int,float) else '0',
        'XCMate.ProgrammeRemaining63':tr(36668,max(0,int(info.get('remaining',0)+59)//60)) if now else '',
        'XCMate.ProgrammeSubtitle63':subtitle,
        'XCMate.ProgrammeKey46':key,'XCMate.ProgrammeKey47':key,
        'XCMate.ProgrammeStart63':str(info.get('start',0)),'XCMate.ProgrammeStop63':str(info.get('stop',0))})
    if now:
        props['XCMate.ProgrammeDetails46']='plugin://plugin.video.xtreammate/?'+urlencode(dict(action='programme_details46',pid=portal['id'],sid=row['sid'],start=info['start'],stop=info['stop'],event=key))
    return item
