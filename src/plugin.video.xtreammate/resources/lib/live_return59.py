"""Post-ACK GUI readiness, independent of the native Stop deadline."""
def stop_confirmed(value,job):
    from playback_exit import _same
    if not job or not job.get('native_posted') or not job.get('worker_done') or job.get('result')!='complete':return False
    if not _same(tuple(job['token']),('live',value['session'])):return False
    from native_stop41 import returned
    return returned(job)


def ready(value):
    from window_lifecycle import state,lease
    snapshot=state()
    if snapshot['modal'] or snapshot['dialog'] not in (0,-1,9999):code='MODAL'
    elif lease():code='OWNER'
    elif snapshot['window'] not in (10000,10025,12005):code='WINDOW'
    elif snapshot['updating']:code='DIRECTORY'
    else:return True
    from live_return47 import guard
    status,fresh=guard(value)
    if status!='READY':return False
    if fresh.get('return_wait59')!=code:
        from live_exit import _save,_trace
        fresh['return_wait59']=code;_save(fresh);_trace('RETURN_WAIT_'+code+'59',fresh['session'])
    return False
