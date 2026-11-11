"""Opt-in EPG image modes for GS Media Setup 0.5.28.

Read-only filesystem capacity measurement; no cache deletion or migration.
Only explicitly requested known XCMate settings may be changed. The installer
records requested cache limits but XCMate's future runtime must enforce them.
"""
import os
import threading

GIB=1024**3
MIB=1024**2
MODES={
    'text':{'min_free':0,'cache_mb':0,'label':'EPG ohne zusätzliche Bilder'},
    'standard':{'min_free':2*GIB,'cache_mb':512,
                'label':'Standard-Bild-EPG – mindestens 2 GB frei (bis 512 MB Bildcache)'},
    'extended':{'min_free':6*GIB,'cache_mb':3072,
                'label':'Erweitertes Bild-EPG – mindestens 6 GB frei (bis 3 GB Bildcache)'},
}
KNOWN_IDS=('epg_show_thumbnails','programme_art_local69')
_busy=threading.Lock()

def measure(target):
    """Measure exactly the volume on which XCMate profile data is stored.

    This is not a guarantee that all artwork is on the same volume.
    Unknown filesystems are fail-closed (text-EPG only).
    """
    if not isinstance(target,str) or not target or '://' in target:
        return {'code':'STORAGE_UNKNOWN'}
    try:
        actual=os.path.realpath(target)
        if not os.path.isdir(actual):
            return {'code':'STORAGE_UNKNOWN'}
        stat=os.stat(actual)
        volume=os.statvfs(actual)
        free=volume.f_bavail*volume.f_frsize
        total=volume.f_blocks*volume.f_frsize
        if free<0 or total<=0 or free>total:
            return {'code':'STORAGE_UNKNOWN'}
        return {'code':'READY','free_bytes':free,'total_bytes':total,
                'device':stat.st_dev}
    except (OSError,ValueError,OverflowError):
        return {'code':'STORAGE_UNKNOWN'}

def can_enable(mode,report):
    if mode not in MODES:
        return False
    if mode=='text':
        return True
    # Check actual free bytes, not advertised capacity. Reserve is included
    # in the min-free threshold, never bypass the global 1-GiB reserve.
    return report.get('code')=='READY' and report.get('free_bytes',0)>=MODES[mode]['min_free']

def _profile_target():
    import xbmcaddon,xbmcvfs
    addon=xbmcaddon.Addon('plugin.video.xtreammate')
    root=addon.getAddonInfo('profile')
    return xbmcvfs.translatePath(root)

def configure(mode,report,addon=None,installer=None):
    """Explicit choice, fail closed on low space, preserve original settings.

    Quotas written as installer intent only: current XCMate has no dedicated
    per-EPG-image quota setting. DO NOT modify global media_art_budget_mb.
    """
    if mode not in MODES:return 'INVALID_MODE'
    if not can_enable(mode,report):return 'INSUFFICIENT_SPACE'
    if not _busy.acquire(False):return 'BUSY'
    try:
        import xbmcaddon
        addon=addon or xbmcaddon.Addon('plugin.video.xtreammate')
        installer=installer or xbmcaddon.Addon('script.gsmedia.setup')
        previous={name:addon.getSetting(name) for name in KNOWN_IDS}
        old_mode=installer.getSetting('epg_art_mode528')
        old_quota=installer.getSetting('epg_art_target_mb528')
        desired={
            'epg_show_thumbnails':'false' if mode=='text' else 'true',
            'programme_art_local69':'false' if mode=='text' else 'true'
        }
        try:
            for name,value in desired.items():
                if addon.getSetting(name)!=value:
                    addon.setSetting(name,value)
                if addon.getSetting(name)!=value:
                    raise RuntimeError('SETTING_READBACK_FAILED')
            installer.setSetting('epg_art_mode528',mode)
            installer.setSetting('epg_art_target_mb528',str(MODES[mode]['cache_mb']))
            if (installer.getSetting('epg_art_mode528')!=mode or
                installer.getSetting('epg_art_target_mb528')!=str(MODES[mode]['cache_mb'])):
                raise RuntimeError('POLICY_READBACK_FAILED')
        except Exception:
            for name,value in previous.items():
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
    import xbmcaddon,xbmcgui
    dlg=xbmcgui.Dialog()
    try:
        target=_profile_target()
        report=measure(target)
    except (OSError,RuntimeError,ValueError,AttributeError):
        report={'code':'STORAGE_UNKNOWN'}
    free=report.get('free_bytes',0)//MIB if report.get('code')=='READY' else None
    amount=str(free)+' MB frei auf XCMate-Profilvolume' if free is not None else 'Speicherplatz nicht prüfbar'
    warning=('Mehr Sendungsbilder benötigen viel lokalen Speicher. '
             'Entscheidend ist der freie Platz auf dem tatsächlichen Cachevolume. '
             'EPG-Programmdaten bleiben auch ohne Bilder verfügbar. '
             'Das Cachelimit muss in einer kompatiblen XCMate-Version '
             'separat durchgesetzt werden.')
    if not manual:
        if not dlg.yesno('Bild-EPG bei Installation',warning+'\n'+amount,
                         defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):
            return 'SKIPPED'
    labels=[
        'Ohne zusätzliche Bilder (kein zusätzlicher Bildcache)',
        MODES['standard']['label'],
        MODES['extended']['label'],
        'Unverändert lassen / später entscheiden'
    ]
    picked=dlg.select('Bild-EPG: '+amount,labels)
    if picked not in (0,1,2):
        return 'SKIPPED'
    mode=('text','standard','extended')[picked]
    if not can_enable(mode,report):
        dlg.ok('Bild-EPG: Speicherplatz',
               'Nicht genügend freier Speicher auf dem tatsächlichen XCMate-Profilvolume. '
               'Erforderlich: mindestens '+str(MODES[mode]['min_free']//MIB)+
               ' MB frei. '+amount+'. Einstellungen wurden nicht verändert.')
        return 'INSUFFICIENT_SPACE'
    if not dlg.yesno('Bild-EPG bestätigen',
                     MODES[mode]['label']+'\n'+amount+
                     '\nVorhandene Bilder und andere Kodi-Daten werden nicht gelöscht. '
                     'Änderung nur nach Bestätigung.',
                     defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):
        return 'SKIPPED'
    result=configure(mode,report)
    dlg.ok('Bild-EPG',('Auswahl gespeichert. Für die eigene Cachebegrenzung ist '
                      'eine kompatible XCMate-Laufzeit erforderlich.'
                      if result=='CONFIGURED' else
                      'Einstellung nicht gespeichert: '+result))
    return result
