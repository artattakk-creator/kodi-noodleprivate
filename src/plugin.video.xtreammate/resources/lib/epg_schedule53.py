"""24-hour default, preserved explicit settings, bounded per-source retries."""
import time


def interval():
    from utils import setting_int
    return max(1,min(48,setting_int('epg_refresh_hours',24)))*3600


def plan(portal,now=None):
    from epg_report53 import configured,history,SUCCESS,BLOCKED
    from epg_status import read
    if not portal.get('epg_show',True):return []
    from wizard_epg54 import pending
    if pending(portal):return []  # Explicit setup-resume owns unfinished sources.
    now=time.time() if now is None else now;period=min(interval(),24*3600);runs=history(portal['id']);state=read(portal['id']);wanted=[]
    # Short/focus cache freshness is not proof of a complete source import.
    # A missing live catalogue is transient, not a day-long failure latch.
    from epg_source66 import restart_anchors
    anchors=restart_anchors(portal['id'])
    blocked95={'BACKUP_REQUIRED','CANCELLED','BACKUP_MISSING','BACKUP_RECEIPT_MISMATCH','BACKUP_DIR_UNAVAILABLE','DB_AUTHORIZATION_MISSING','DB_SCHEMA_MISSING','STORAGE_FULL','STORAGE_ACCESS_DENIED'}
    transient95={'DB_BUSY','BACKUP_GATE_TIMEOUT','DB_INTERRUPTED','DB_AUTHORIZATION_CHANGED','STORAGE_IO'}
    # A gate refusal precedes the import worker and may have no history row.
    # Its durable refresh status must also prevent minute-by-minute rechecks.
    refused95=state.get('refresh',{})
    if refused95.get('code') in blocked95 and 0<=now-refused95.get('at',0)<period:return []
    if refused95.get('code') in transient95 and 0<=now-refused95.get('at',0)<900:return []
    if runs and runs[-1].get('code') in blocked95 and now-runs[-1]['started']<period:return []
    if runs and runs[-1].get('code') in transient95 and now-runs[-1]['started']<900:return []
    if runs and runs[-1].get('code') in ('WAIT_ACTIVE_CATALOG','IMPORT_BUSY_OR_LOCK_UNAVAILABLE') and now-runs[-1]['started']<60:return []
    for source in configured(portal):
        if not source['enabled']:continue
        events=[s for r in runs for s in r.get('sources',[]) if s.get('id')==source['id']]
        success=max([s.get('finished',0) for s in events if s.get('code') in SUCCESS]+[state.get(source['key'],{}).get('last_success',0),anchors.get(source['id'],0) if not events else 0])
        if success and now-success<period:continue
        failures=[s for s in events if s.get('finished',0)>success and s.get('code') not in SUCCESS]
        if failures:
            first=failures[0]['started'];last=failures[-1]['finished'];attempts=len(failures)
            if now-first<period:
                if attempts>=3 or now-last<(900 if attempts==1 else 3600):continue
        wanted.append(source['id'])
    return wanted
