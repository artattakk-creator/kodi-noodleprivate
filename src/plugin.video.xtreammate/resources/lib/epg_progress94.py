"""Localized, bounded presentation of actual durable worker observations."""
from localization import tr
PHASE={'QUEUED':38807,'DOWNLOAD':38808,'PARSE':38809,'MATCHING':38810,'STAGING':38811,'COMMIT':38812,'READBACK':38813,'CLEANUP':38814,'DONE':38815,'FAILED':38816,'CANCELLED':38817,'WAIT_CATALOG':38818}
STATE={'QUEUED':38807,'RUNNING':38819,'CANCELLING':38820,'DONE':38815,'PARTIAL':38821,'FAILED':38816,'CANCELLED':38817,'INTERRUPTED':38822,'SERVICE_NOT_CONFIRMED':38823}


def row(job,key):
    source=job.get('sources',{}).get(key,{})
    phase=source.get('phase')
    active=job.get('state')=='RUNNING' and phase not in ('DONE','FAILED','CANCELLED') and job.get('source',key)==key and bool(source)
    total=source.get('total_bytes',0)
    size=source.get('bytes',0)
    text=tr(PHASE.get(phase,38807))
    if 'bytes' in source:
        text+=' · '+(tr(38824,size,total) if total else tr(38825,size))
    if source.get('error_code'):
        text+=' · '+source['error_code']
    counts=[]
    if 'programmes' in source:
        prefix=f"{source['channels']} Kanäle / " if 'channels' in source else ''
        counts.append(f"Gelesen {prefix}{source['programmes']} Programme")
    elif 'channels' in source:
        counts.append(f"Gelesen {source['channels']} XMLTV-Kanäle")
    if 'matched' in source:
        selected=f"/{source['selected_streams']}" if 'selected_streams' in source else ''
        counts.append(f"IPTV-Zuordnung {source['matched']}{selected}")
    for count,channels,label in (
        ('staged','staged_channels','Staging'),
        ('committed','committed_channels','Commit'),
        ('verified','verified_channels','Readback bestätigt'),
    ):
        if count in source and not (count=='verified' and phase=='READBACK'):
            subjects=f"{source[channels]} Kanäle / " if channels in source else ''
            counts.append(f"{label} {subjects}{source[count]} Programme")
    if phase=='READBACK':
        scanned=source.get('readback_rows',source.get('verified'))
        if scanned is not None:
            counts.append(f"Readback läuft {scanned} Programme")
    if 'matched_channels' in source:
        counts.append(f"XMLTV-Zuordnung {source['matched_channels']} Kanäle")
    return dict(text=text,stats=' · '.join(counts),counts=counts,
                busy=active,percent=min(100,100*size/total) if total and phase=='DOWNLOAD' else None)


def summary(job):
    if not job:return ''
    text=tr(STATE.get(job['state'],38816))+' · '+tr(38828,job['id'][:8])
    source=job.get('sources',{}).get(job.get('source'),{})
    if source.get('sources'):text+=' · '+tr(38829,source.get('source_index',0),source['sources'])
    if source and job['state']=='RUNNING':
        text+=' · '+tr(PHASE.get(source.get('phase'),38807))
    if job.get('stalled'):
        text+=' · '+tr(38830)
    return text


def report(job, names):
    from epg_report53 import stamp
    lines=[job['state']]
    if job.get('ack'):
        lines.append('Dienstübernahme bestätigt (SERVICE_ACK) · '+stamp(job['ack']))
    if job['state'] in ('QUEUED','RUNNING','CANCELLING'):
        lines.append('Der Abschlussbericht erscheint nach Ende des Imports.')
    for key,source in job.get('sources',{}).items():
        value=row(job,key)
        lines.extend(['',names.get(key,'EPG-Quelle'),value['text'],*value['counts']])
        if source.get('phase_started') and key==job.get('source'):
            lines.append('Aktuelle Phase seit · '+stamp(source['phase_started']))
        if source.get('progress'):
            elapsed=f" · vor {job['progress_age']} s" if key==job.get('source') and 'progress_age' in job else ''
            lines.append('Letzter Fortschritt · '+stamp(source['progress'])+elapsed)
    return '\n'.join(lines)
