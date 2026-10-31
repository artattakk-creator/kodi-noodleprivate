"""Worker prepares IDs; GUI samples existing Home controls from RAM only."""
import threading,time
_lock=threading.Lock();_plans={};_observed={}


def prepare(pid):
    from hero_epg63 import prepare as hero63
    from skin_upgrade63 import prepare as upgrade63
    import sqlite3
    try:hero63(pid)
    except (OSError,ValueError,TypeError,KeyError,RuntimeError,AttributeError,sqlite3.Error):pass
    try:upgrade63()
    except (OSError,ValueError,TypeError,KeyError,RuntimeError,AttributeError,sqlite3.Error):pass
    from widget_consumer58 import status
    with _lock:prior=_plans.get(str(pid))
    if not prior or time.monotonic()-prior[0]>=60:
        value=status(pid)
        with _lock:_plans[str(pid)]=(time.monotonic(),{k:dict(v) for k,v in value.get('kinds',{}).items() if k in ('live','vod','series')})
    with _lock:
        observations=[(kind,dict(v)) for (portal,kind),v in _observed.items() if portal==str(pid)]
        while len(_plans)>8:_plans.pop(next(iter(_plans)))
    # All SQLite work remains on this existing data worker.
    from widget_diagnostics47 import save
    for kind,value in observations:save(pid,kind,'SKIN',value)


def poll():
    import xbmc,xbmcgui
    if xbmc.getSkinDir()!='skin.titan.bingie.mod' or xbmcgui.getCurrentWindowId()!=10000 or xbmcgui.getCurrentWindowDialogId() not in (0,-1,9999):return
    from widget_diagnostics47 import note
    with _lock:plans=dict(_plans)
    for pid,(at,kinds) in plans.items():
        if time.monotonic()-at>180:continue
        for kind,state in kinds.items():
            known=[]
            for cid in state.get('control_ids59',[])[:8]:
                if not isinstance(cid,int) or not 0<cid<1000000:continue
                count=xbmc.getInfoLabel('Container('+str(cid)+').NumItems')
                if not str(count).isdigit():continue
                known.append((bool(xbmc.getCondVisibility('Control.IsVisible('+str(cid)+')')),int(count)))
            code=('NATIVE_HOME_ITEMS' if any(v and n>0 for v,n in known) else 'NATIVE_HOME_HIDDEN' if known and not any(v for v,n in known) else 'NATIVE_HOME_EMPTY' if known else 'NATIVE_HOME_UNVERIFIED')
            value=note(pid,kind,'SKIN',code,items=sum(n for v,n in known),directory_ok=int(any(v and n>0 for v,n in known)),decode_verified=-1)
            with _lock:
                _observed[(pid,kind)]=value
                while len(_observed)>16:_observed.pop(next(iter(_observed)))
