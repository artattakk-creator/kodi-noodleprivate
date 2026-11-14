"""Localized, bounded presentation of actual durable worker observations."""
from localization import tr
PHASE={'QUEUED':38807,'DOWNLOAD':38808,'PARSE':38809,'MATCHING':38810,'STAGING':38811,'COMMIT':38812,'READBACK':38813,'CLEANUP':38814,'DONE':38815,'FAILED':38816,'CANCELLED':38817,'WAIT_CATALOG':38818}
STATE={'QUEUED':38807,'RUNNING':38819,'CANCELLING':38820,'DONE':38815,'PARTIAL':38821,'FAILED':38816,'CANCELLED':38817,'INTERRUPTED':38822,'SERVICE_NOT_CONFIRMED':38823}


def row(job,key):
    source=job.get('sources',{}).get(key,{})
    active=job.get('state')=='RUNNING' and source.get('phase') not in ('DONE','FAILED','CANCELLED') and bool(source)
    total=source.get('total_bytes',0);size=source.get('bytes',0)
    text=tr(PHASE.get(source.get('phase'),38807))
    if source.get('phase')=='DOWNLOAD':text+=' · '+tr(38824,size,total) if total else ' · '+tr(38825,size)
    stats=tr(38826,source.get('channels',0),source.get('programmes',0),source.get('matched',0),source.get('staged',0))
    if source.get('committed') is not None:text+=' · '+tr(38827,source['committed'],source.get('verified',0))
    if source.get('error_code'):text+=' · '+source['error_code']
    return dict(text=text,stats=stats,busy=active and not job.get('stalled'),percent=min(100,100*size/total) if total and source.get('phase')=='DOWNLOAD' else None)


def summary(job):
    if not job:return ''
    text=tr(STATE.get(job['state'],38816))+' · '+tr(38828,job['id'][:8])
    source=job.get('sources',{}).get(job.get('source'),{})
    if source.get('sources'):text+=' · '+tr(38829,source.get('source_index',0),source['sources'])
    if job.get('stalled'):text+=' · '+tr(38830)
    return text
