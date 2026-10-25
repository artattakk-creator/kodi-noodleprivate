"""Explicit artwork diagnostics/recovery; UI stays on the invoking thread."""
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import xbmc
import xbmcgui
from localization import tr


def _work(job):
    cancelled=threading.Event();pool=ThreadPoolExecutor(max_workers=1)
    dialog=xbmcgui.DialogProgress();monitor=xbmc.Monitor()
    try:
        dialog.create('XCMate',tr(32903))
        future=pool.submit(job,cancelled.is_set)
        while not future.done():
            if dialog.iscanceled():cancelled.set()
            if monitor.waitForAbort(.05):
                cancelled.set();time.sleep(.05)
        return future.result()
    finally:
        cancelled.set();dialog.close();pool.shutdown(wait=False,cancel_futures=True)


def manage():
    from artwork_db import maintain,rebuild,diagnostic
    try:result=_work(lambda cancel:maintain(force=True,cancel=cancel))
    except Exception:result=dict(code='CHECK_FAILED')
    # Fixed diagnostic fields only. No path, private URL or exception text.
    text='\n'.join(key+': '+str(result[key]) for key in ('code','phase','sqlite_code','backup') if key in result)
    xbmcgui.Dialog().textviewer(tr(32900),text)
    if result.get('code') in ('RECOVERY_REQUIRED','SCHEMA_ERROR'):
        if xbmcgui.Dialog().yesno('XCMate',tr(32902)):
            try:result=_work(lambda cancel:rebuild(confirmed=True,cancel=cancel))
            except Exception:result=dict(code='RECOVERY_FAILED')
            text='\n'.join(key+': '+str(result[key]) for key in ('code','phase','backup') if key in result)
            if result.get('background_paused'):text+='\n\n'+tr(32904)
            xbmcgui.Dialog().textviewer(tr(32900),text)


def status_text(value):
    def mib(number):return str(number//1048576) if isinstance(number,(int,float)) else '—'
    lines=[tr(32960),tr(32961,value.get('code','UNAVAILABLE')),
           tr(33427,mib(value.get('bytes')),mib(value.get('budget'))+' MiB' if value.get('budget') else tr(33401)),
           tr(33402,mib(value.get('reserve'))),tr(33407,tr(33408 if value.get('paused') else 33409)),
           tr(32963,mib(value.get('free')),mib(value.get('total'))),tr(32964)]
    if value.get('counts') is not None:lines.extend(str(k)+': '+str(v) for k,v in sorted(value['counts'].items()))
    else:lines.append(tr(32965))
    health=value.get('health',{})
    lines.extend([tr(32966,health.get('integrity_code',health.get('code','NOT_CHECKED'))),tr(32967)])
    lines.extend(['',tr(35110),tr(35111,value.get('storage_result','UNKNOWN')),
                  tr(35112,value.get('free','—'),value.get('total','—'),value.get('reserve','—'),
                     value.get('budget','—'),value.get('bytes','—'),value.get('expected_bytes','—')),
                  tr(35113,value.get('metadata_free','—'),value.get('metadata_reserve','—'))])
    observations=value.get('observations',{})
    for role in ('request','enrol','service','worker','transfer','logo'):
        item=observations.get(role,{})
        # Each observation was sanitized at its boundary; display only the
        # fixed/numeric field set again, never arbitrary property contents.
        from art_diagnostics import CODES,FIELDS
        code=item.get('code') if item.get('code') in CODES else 'UNKNOWN'
        safe={key:number for key,number in item.items() if key in FIELDS and isinstance(number,(int,float,bool))}
        if item.get('reason') in CODES:safe['reason']=item['reason']
        lines.append(role+': '+code+' '+str(safe))
    details=value.get('queue_details',{})
    allowed=('last_ready_at','last_attempt_at','exhausted','next_at','lease_until')
    lines.append(tr(35114)+' '+str({key:details[key] for key in allowed if key in details}))
    lines.append(tr(35115))
    return '\n'.join(lines)


def show_status():
    from art_store import status
    try:value=_work(lambda cancel:status(cancel=cancel))
    except Exception as exc:
        from boot_diagnostics import mark
        mark('ART_STATUS_COUNTS_FAILED',error=type(exc).__name__)
        from art_store import budget
        value=dict(code='UNAVAILABLE',budget=budget())
    xbmcgui.Dialog().textviewer(tr(32661),status_text(value))
