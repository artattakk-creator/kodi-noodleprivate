"""Authoritative local EPG text survives any optional artwork/metadata failure."""
import os,time,json
from urllib.parse import urlencode

def local_image(path):
    return isinstance(path,str) and bool(path) and (os.path.isabs(path) or path.startswith(('special://home/','special://profile/','special://masterprofile/')))


def apply(item,portal,row,info,event=None,labels=None):
    from epg_handoff63 import profile_scope
    item['props']['XCMate.EpgProfile63']=profile_scope()
    if labels is None:
        from localization import tr
        labels=(tr(36102),tr(36668,'{0}'))
        item['props']['XCMate.FallbackLabel63']=tr(36542)
    item['props']['XCMate.NoEpg63']=labels[0]
    item['props']['XCMate.RemainingFormat63']=labels[1]
    import xbmcaddon
    from epg_row64 import stamp
    stamp(item['props'],portal['id'],info)
    if not isinstance(info,dict):
        _hero(item['props'])
        return item
    props=item['props'];key=str(info.get('programme_key47') or '')
    # An optional renderer may straddle a programme transition. Never combine
    # the old text with a different programme's picture.
    if props.get('XCMate.ProgrammeKey47','')!=key:
        props['XCMate.ProgrammeImage46']=os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources','media','programme46','neutral.png')
        for field in ('XCMate.ProgrammeArtSource57','XCMate.ProgrammeArtCredit57','XCMate.ProgrammeImageScope57','XCMate.ArtProof69','XCMate.Provisional85'):props[field]=''
    now=bool(info.get('now'));event=event if isinstance(event,dict) and event.get('key')==key else {}
    subtitle=str(event.get('subtitle') or '')
    if type(event.get('season')) is int and type(event.get('episode')) is int:
        subtitle=('S%02d E%02d'%(event['season'],event['episode']))+(' – '+subtitle if subtitle else '')
    description=__import__('presentation80').text(info.get('description') or event.get('description'))
    if props.get('XCMate.ProgrammeImageScope57')=='series_fallback' and props.get('XCMate.FallbackLabel63'):
        description=props['XCMate.FallbackLabel63']+'\n'+description
    if props.get('XCMate.Provisional85')=='true':description='Bildvorschlag – Zuordnung nicht bestätigt.\n'+description
    props.update({'XCMate.ProgrammeTitle46':str(info.get('now') or labels[0]),
        'XCMate.ProgrammeTimes46':(info.get('now_time','')+' – '+info.get('now_end_time','')) if now else '',
        'XCMate.ProgrammeNext46':str(info.get('next') or ''),
        'XCMate.ProgrammeNextTimes48':(info.get('next_time','')+' – '+info.get('next_end_time','')) if info.get('next') else '',
        'XCMate.ProgrammeDescription46':description,
        'XCMate.ProgrammePercent46':str(round(info['progress']*100)) if now and type(info.get('progress')) in (int,float) else '0',
        'XCMate.ProgrammeRemaining63':labels[1].format(max(0,int(info.get('remaining',0)+59)//60)) if now else '',
        'XCMate.ProgrammeSubtitle63':subtitle,
        'XCMate.ProgrammeKey46':key,'XCMate.ProgrammeKey47':key,
        'XCMate.ProgrammeStart63':str(info.get('start',0)),'XCMate.ProgrammeStop63':str(info.get('stop',0))})
    facts75(props,event)
    if now:
        props['XCMate.ProgrammeDetails46']='plugin://plugin.video.xtreammate/?'+urlencode(dict(action='programme_details46',pid=portal['id'],sid=row['sid'],start=info['start'],stop=info['stop'],event=key))
    _hero(props)
    return item

def facts75(props,event):
    event=event if isinstance(event,dict) and event.get('key')==props.get('XCMate.ProgrammeKey47') else {}
    values=[str(event.get('genre') or '')[:160]]
    year=event.get('year')
    if str(year or '').isdigit() and 1800<=int(year)<=2200:values.append(str(year))
    cast=event.get('cast') or []
    if isinstance(cast,str):values.append(cast[:320])
    elif isinstance(cast,list):values.append(', '.join((str(v.get('name','')) if isinstance(v,dict) else str(v))[:80] for v in cast[:8]))
    props['XCMate.ProgrammeFacts75']=' · '.join(v for v in values if v)[:512]


def _hero(props):
    # Preserve the public .55 ProgrammeImage46 API used by legacy/details.
    # The new native Hero consumes its own local-only presentation reference.
    import xbmcaddon
    props['XCMate.HeroLong64']='true' if len(props.get('XCMate.ProgrammeTitle46',''))>26 else 'false'
    image=props.get('XCMate.ProgrammeImage46','')
    from programme_image69 import unpack
    approved69=unpack(props.get('XCMate.ArtProof69',''))
    local=local_image(image) and not '/resources/media/programme46/' in image
    if approved69 and approved69.get('key')==props.get('XCMate.ProgrammeKey47') and approved69.get('image')==image:local=True
    logo84=False
    if not local:
        logo=props.get('XCMate.ProgrammeLogo46','')
        logo84=bool(local_image(logo) and '/resources/media/' not in logo)
        image=logo if logo84 else __import__('station_logos88').reference(props) or __import__('artwork_display84').logo_reference(props)
        logo84=bool(image)
        local=logo84
    if logo84 or not local:props['XCMate.Provisional85']=''
    props['XCMate.HeroImage63']=image if local else ''
    props['XCMate.HeroArtSource63']='station_logo' if logo84 else props.get('XCMate.ProgrammeArtSource57','') if local else ''
    props['XCMate.HeroArtCode63']=props.get('XCMate.ProgrammeArtCode46','') if local else 'PENDING_LOCAL_DOWNLOAD' if str(image).startswith(('http://','https://','image://')) else 'NO_IMAGE'
