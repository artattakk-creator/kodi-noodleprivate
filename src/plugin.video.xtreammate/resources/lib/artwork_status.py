"""Localized physical storage and queue diagnosis; developer JSON is separate."""
from localization import tr


def size(value):
    if not isinstance(value,(int,float)) or value<0:return tr(35702)
    return ('{:.2f} GiB'.format(value/1073741824)) if value>=1073741824 else '{:.2f} MiB'.format(value/1048576)


def collect(cancel=lambda:False,progress=lambda **kw:None):
    from artwork_config import read
    from art_store import status
    from artwork_inventory import inventory
    from device_info import texture_inventory
    import xbmcvfs
    config=read();physical=inventory(cancel,progress)
    try:textures=texture_inventory(xbmcvfs.translatePath('special://thumbnails/'))
    except (AttributeError,OSError):textures=dict(code='UNKNOWN')
    external=None
    if config['mode']=='external':
        external=dict(files=0,bytes=0,code='OK',complete=True)
        try:
            from artwork_backend import active_backend
            for kind in ('media','logos'):
                for entry in active_backend(kind).enumerate_for_migration():
                    if cancel():external['complete']=False;break
                    external['files']+=1;external['bytes']+=entry['bytes']
                    if external['files']%64==0:progress(stage='INVENTORY',files=external['files'],bytes=external['bytes'])
        except OSError:external=dict(files=None,bytes=None,code='STORAGE_OFFLINE',complete=False)
    return dict(external=external,config=dict(mode=config['mode'],strategy=config.get('strategy','demand')),artwork=status(cancel),physical={k:v for k,v in physical.items() if k not in ('entries','roots','profile')},textures=textures)


def text(data):
    value=data['artwork'];physical=data['physical'];config=data['config'];textures=data['textures']
    modes=dict(dynamic=tr(35703),internal=tr(35704),external=tr(35705))
    reasons=dict(OK=35743,RESERVE_BLOCKED=35744,BLOCKED_REAL_DISK=35745,BUDGET_FULL=35721,STORAGE_OFFLINE=35746,DYNAMIC_NO_XCMATE_ARCHIVE=35747)
    storage=tr(reasons[value['storage_result']]) if value.get('storage_result') in reasons else tr(35702)
    lines=[tr(35706,modes.get(config['mode'],tr(35702))),tr(35707,physical['files'],size(physical['bytes'])),
           tr(35708,physical['skipped']),tr(35709,size(physical.get('free'))),
           tr(35710,size(value.get('free')),size(value.get('total'))),tr(35711,tr(35749) if config['mode']=='dynamic' else size(value.get('reserve'))),
           tr(35712,tr(35713) if value.get('budget')==0 else size(value.get('budget'))),
           tr(35714,storage),tr(35715)]
    if data.get('external'):
        external=data['external'];lines.insert(2,tr(35748,external.get('files','—'),size(external.get('bytes'))))
        if external['code']!='OK':lines.insert(3,tr(35746))
    names=dict(PENDING=35716,RUNNING=35717,READY=35718,MISSING=35719,DISK_FULL=35720,SPACE_FULL=35720,BUDGET_FULL=35721,FAILED=35722)
    counts=value.get('counts')
    if isinstance(counts,dict):
        lines.extend((tr(names[code]) if code in names else code)+': '+str(count) for code,count in sorted(counts.items()))
        if not counts:lines.append(tr(35723))
    else:lines.append(tr(35724,value.get('code','UNAVAILABLE')))
    lines.extend(['',tr(35725,textures.get('files','—'),size(textures.get('bytes'))),tr(35726) if textures.get('partial') else '',tr(35727)])
    if not physical.get('complete'):lines.append(tr(35728))
    return '\n'.join(line for line in lines if line)


def cleanup():
    import xbmcgui
    from artwork_config import read
    from artwork_ui import job
    from artwork_inventory import inventory,pending,prepare,execute
    dialog=xbmcgui.Dialog()
    if read()['mode']!='dynamic':dialog.ok('XCMate',tr(35729));return
    snapshot=job(inventory)
    if not snapshot or not snapshot.get('complete'):return
    resume=job(lambda cancel,progress:pending())
    dialog.textviewer('XCMate',tr(35707,snapshot['files'],size(snapshot['bytes']))+'\n'+tr(35709,size(snapshot['free']))+'\n'+tr(35730))
    if not snapshot['files'] and not resume:dialog.ok('XCMate',tr(35731));return
    options=[tr(35732),tr(35733),tr(35734)]
    if resume:options.append(tr(35735,resume['files'],size(resume['bytes'])))
    selected=dialog.select(tr(35700),options,preselect=0)
    if selected==1:dialog.ok('XCMate',tr(35736));return
    if selected not in (2,3) or selected==3 and not resume:return
    count=resume['files'] if selected==3 else snapshot['files'];amount=resume['bytes'] if selected==3 else snapshot['bytes']
    if not dialog.yesno('XCMate',tr(35737,count,size(amount))):return
    if not dialog.yesno('XCMate',tr(35738)):return
    challenge=resume['id'] if selected==3 else job(lambda cancel,progress:prepare(snapshot,confirmed=True))
    if not challenge:return
    result=job(lambda cancel,progress:execute(challenge,confirmed=True,cancel=cancel,progress=progress))
    if result:dialog.textviewer('XCMate',tr(35739,size(result['removed_bytes_this_run']))+'\n'+tr(35740,size(result['free_before']),size(result['free_after']))+'\n'+tr(35741,str(result['measured_free_delta']) if result['measured_free_delta'] is not None else tr(35702))+'\n'+tr(35742))
