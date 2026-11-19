"""Opt-in EPG image modes for GS Media Setup 0.5.28.

Dynamic, on-demand picture EPG is available without any hard free-space
minimum. Free-space reporting is advisory only. This installer does not
preload images, reserve quotas, migrate profiles or alter the global 1-GiB
storage safety guard. Future XCMate runtime support is required for the
extended mode's additional imagery; mode preference itself is persisted.
"""
import os
import threading

MIB=1024**2
MODES={
    'text':{'label':'EPG ohne Sendungsbilder'},
    'standard':{'label':'Standard-Bild-EPG (Bilder dynamisch laden)'},
    'extended':{'label':'Erweitertes Bild-EPG (dynamisch; zusätzliche Bilder optional)'},
}
_busy=threading.Lock()

def measure(target):
    """Advisory only: profile mount may differ from the actual artwork mount."""
    if not isinstance(target,str) or not target or '://' in target:
        return {'code':'STORAGE_UNKNOWN'}
    try:
        actual=os.path.realpath(target)
        if not os.path.isdir(actual):return {'code':'STORAGE_UNKNOWN'}
        stat=os.stat(actual);volume=os.statvfs(actual)
        free=volume.f_bavail*volume.f_frsize
        total=volume.f_blocks*volume.f_frsize
        if free<0 or total<=0 or free>total:return {'code':'STORAGE_UNKNOWN'}
        return {'code':'READY','free_bytes':free,'total_bytes':total,
                'device':stat.st_dev}
    except (OSError,ValueError,OverflowError):
        return {'code':'STORAGE_UNKNOWN'}

def can_enable(mode,report):
    """Never gate dynamic picture EPG on free disk space or an unknown mount."""
    return mode in MODES

def _profile_target():
    import xbmcaddon,xbmcvfs
    return xbmcvfs.translatePath(
        xbmcaddon.Addon('plugin.video.xtreammate').getAddonInfo('profile'))

def configure(mode,report,addon=None,installer=None):
    """Explicit choice; safe rollback; no forced local cache or quota allocation.

    The standard mode is the existing working dynamic picture EPG.
    The extended mode stores an opt-in preference only; extra-runtime
    functionality is a separate implementation/release gate.
    Existing local-artwork preference is preserved for both picture modes.
    """
    if not can_enable(mode,report):return 'INVALID_MODE'
    if not _busy.acquire(False):return 'BUSY'
    try:
        if addon is None or installer is None:
            import xbmcaddon
            if addon is None:addon=xbmcaddon.Addon('plugin.video.xtreammate')
            if installer is None:installer=xbmcaddon.Addon('script.gsmedia.setup')
        changes={'epg_show_thumbnails':'false' if mode=='text' else 'true'}
        if mode=='text':
            changes['programme_art_local69']='false'
        before={name:addon.getSetting(name) for name in changes}
        old_mode=installer.getSetting('epg_art_mode528')
        old_quota=installer.getSetting('epg_art_target_mb528')
        try:
            for name,value in changes.items():
                if addon.getSetting(name)!=value:
                    addon.setSetting(name,value)
                if addon.getSetting(name)!=value:
                    raise RuntimeError('SETTING_READBACK_FAILED')
            installer.setSetting('epg_art_mode528',mode)
            # Zero means no preallocation and no suggested disk budget.
            # Runtime storage policy remains under XCMate control.
            installer.setSetting('epg_art_target_mb528','0')
            if (installer.getSetting('epg_art_mode528')!=mode or
                installer.getSetting('epg_art_target_mb528')!='0'):
                raise RuntimeError('POLICY_READBACK_FAILED')
        except Exception:
            for name,value in before.items():
                try:addon.setSetting(name,value)
                except Exception:pass
            try:
                installer.setSetting('epg_art_mode528',old_mode)
                installer.setSetting('epg_art_target_mb528',old_quota)
            except Exception:pass
            return 'CONFIG_WRITE_FAILED'
        return 'CONFIGURED'
    finally:
        _busy.release()

def offer(profile=None,manual=False):
    import xbmcgui
    dlg=xbmcgui.Dialog()
    try: report=measure(_profile_target())
    except (OSError,RuntimeError,ValueError,AttributeError):
        report={'code':'STORAGE_UNKNOWN'}
    free=report.get('free_bytes',0)//MIB if report.get('code')=='READY' else None
    capacity=(str(free)+' MB frei auf dem Profilvolume'
              if free is not None else 'Freier Speicher nicht ermittelbar')
    info=('Das Standard-Bild-EPG lädt Bilder dynamisch. '
          'Es benötigt keinen vorab reservierten Bildcache. '
          'Dauerhafte lokale Bildspeicherung ist optional und kann bei '
          'wenig freiem Speicher eingeschränkt sein. '
          'Eine Auslagerung auf ein größeres Volume kann später gewählt werden.')
    if not manual:
        if not dlg.yesno('Bild-EPG bei Installation',info+'\n'+capacity,
                         defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):
            return 'SKIPPED'
    labels=[
       MODES['text']['label'],
       MODES['standard']['label'],
       MODES['extended']['label'],
       'Unverändert lassen / später entscheiden',
    ]
    picked=dlg.select('Bild-EPG · '+capacity,labels)
    if picked not in (0,1,2):return 'SKIPPED'
    mode=('text','standard','extended')[picked]
    note=(
       'Mehr Bilder können zusätzlichen Netzwerkverkehr und Speicherbedarf '
       'verursachen. Die erweiterte Darstellungsfunktion benötigt noch '
       'eine kompatible XCMate-Version. '
       if mode=='extended' else
       'Bilder werden bei Bedarf geladen; keine feste Speicheranforderung. '
    )
    if not dlg.yesno('Bild-EPG bestätigen',
                     MODES[mode]['label']+'\n'+capacity+'\n'+note+
                     'Keine automatische Cache-Auslagerung oder Löschung.',
                     defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):
        return 'SKIPPED'
    result=configure(mode,report)
    if result=='CONFIGURED':
        dlg.ok('Bild-EPG',
               'Auswahl gespeichert. Keine zusätzliche lokale Bildspeicherung '
               'erzwungen. Speicher-Auslagerung ist optional.')
    else:
        dlg.ok('Bild-EPG','Einstellung nicht gespeichert: '+result)
    return result
