"""Additive 0.1.27 navigation. Existing playback/settings actions stay valid."""
import os
import uuid

HOME = (('Startkanal','home_start','tv.png'), ('Live-TV','home_live','tv.png'),
        ('EPG','guide_browser','epg.png'), ('Filme','movies_home','vod.png'),
        ('Serien','series_home','series.png'), ('Einstellungen','settings_home','settings.png'))
SETTINGS = (('Accounts & Portale','accounts'), ('Startkanal & Startgruppe','startup'),
            ('EPG','epg'), ('Sendergruppen & Favoriten','groups'),
            ('Fernbedienung & Tasten','remote'), ('Player & Wiedergabe','player'),
            ('Aufnahmen & Speicher','storage'), ('Darstellung & Sprache','appearance'),
            ('Wartung & Diagnose','maintenance'), ('Über XCMate & Lizenzen','about'))


def active_portal(portals, preferred=''):
    from utils import setting
    active=[p for p in portals if p.get('enabled',True)]
    chosen=preferred or setting('active_portal_id','')
    return next((p for p in active if str(p['id'])==chosen), active[0] if active else None)


def show(router, portal):
    import xbmcplugin
    import xbmcaddon
    path=xbmcaddon.Addon().getAddonInfo('path')
    xbmcplugin.setPluginCategory(router._handle,'XCMate · '+portal.get('name',''))
    xbmcplugin.setContent(router._handle,'files')
    for label,action,icon in HOME:
        router._add_dir(label,router.url(action=action,pid=portal['id']),
                        icon=os.path.join(path,'resources','media',icon),
                        plot=('Accounts, Suche und weitere Optionen' if action=='settings_home' else label))
    xbmcplugin.endOfDirectory(router._handle,cacheToDisc=False)


def probe_directory(folder, vfs):
    """Never alter the setting until a unique temporary file round-trips."""
    if not folder or not vfs.exists(folder): return False
    token=uuid.uuid4().hex
    target=os.path.join(folder,'.xcmate-write-test-'+token)
    try:
        stream=vfs.File(target,'w')
        try:
            if not stream.write(token): return False
        finally: stream.close()
        stream=vfs.File(target)
        try: return stream.read()==token
        finally: stream.close()
    except (OSError,RuntimeError): return False
    finally:
        try: vfs.delete(target)
        except (OSError,RuntimeError): pass


def settings(router, portal, section=''):
    import xbmc, xbmcgui, xbmcplugin, xbmcaddon
    pid=portal['id'] if portal else ''
    def add(label,action,**params):
        router._add_dir(label,router.url(action=action,pid=pid,**params))
    if not section:
        for label,key in SETTINGS: add(label,'settings_section',section=key)
    elif section=='accounts':
        from portals import get_active
        add('Aktiven Account wählen','account_select')
        for p in get_active():
            add('{} · {}'.format(p.get('name','Account'),p.get('type','')),'account_select',selected=p['id'])
            account_action={'xtream':'xtream_account','stb':'stb_account','m3u':'m3u_account'}.get(p.get('type'))
            if account_action:
                router._add_dir('Kontoinformationen · '+p.get('name','Account'),
                                router.url(action=account_action,pid=p['id']))
        add('Accounts hinzufügen / bearbeiten / deaktivieren','portal_manager')
        add('Einrichtungsassistent','setup_wizard')
    elif section=='startup':
        add('Startkanal und Startgruppe auswählen','startup_settings')
        add('Autostart-Diagnosepause bewusst ändern','autoplay_diagnostic_mode')
    elif section=='epg':
        add('Programmführer','guide_browser')
        add('Quellen / Priorität / Senderzuordnung','epg_sources')
        add('EPG-Status & Vorschau','epg_status')
        add('Langzeit-EPG: Quellenreichweite','guide_status')
        add('Erinnerungen verwalten / stornieren','guide_timers')
        add('EPG im Hintergrund aktualisieren','refresh_epg')
        add('EPG-Zeitraum / Aktualisierung (Kodi-Einstellungen)','settings')
    elif section=='groups':
        add('Live-/Film-/Seriengruppen verwalten','groups_manager')
        add('Bisherige Live-Favoriten','favourites')
        add('Filmfavoriten','media_favourites',kind='vod')
        add('Serienfavoriten','media_favourites',kind='series')
        add('Gemeinsame Suche: Live-TV / Filme / Serien','global_search')
    elif section=='remote':
        add('Fernbedienungstasten anlernen (Android)','remote_learn')
        add('Optionale globale Fallback-Keymap (Standard AUS)','remote_setup')
    elif section=='player':
        add('Player, Untertitel und Infoleisten-Ausblendzeit','settings')
    elif section=='storage':
        add('Aufnahmeverzeichnis auswählen und prüfen','recording_folder')
        add('Gespeicherten Aufnahmeordner prüfen','recording_folder',check='1')
        add('Bestehende Aufnahmen / Playeroptionen','settings')
        add('Aufnahmeengine: Android-Prüfung erforderlich','recording_capabilities')
    elif section=='appearance':
        add('Sprache / Darstellung / Filter','settings')
        add('BINGIE-MOD-Widgets einrichten','widget_setup')
        add('Widget-Quelle 1: Live-TV aus Startkanalgruppe','widget_live_start_group')
        add('Widget-Quelle 2: Neueste Filme','widget_recent_vod')
        add('Widget-Quelle 3: Neueste Serien','widget_recent_series')
    elif section=='maintenance':
        for label,action in (('Gemeinsame Suche','global_search'),('Lokale Kataloge aktualisieren','refresh_portal'),
            ('EPG-Status & Vorschau','epg_status'),('TV-Fernbedienung: Diagnose','remote_diagnostics'),
            ('Hintergrunddienst prüfen','service_recover'),('Popup- und Fernbedienungstest (OHNE TV)','popup_probe'),
            ('Cache löschen (mit Bestätigung)','clear_cache'),('Alle Kodi-Add-on-Einstellungen','settings')):
            add(label,action)
    elif section=='about':
        add('Version / Herkunft / Lizenzen','about_xcmate')
    xbmcplugin.endOfDirectory(router._handle,cacheToDisc=False)


def recording_folder(check_only=False):
    import xbmcgui, xbmcaddon, xbmcvfs
    from utils import setting
    old=setting('recordings_folder','special://profile/addon_data/plugin.video.xtreammate/recordings/')
    selected=old if check_only else xbmcgui.Dialog().browseSingle(0,'XCMate · Aufnahmeverzeichnis','files',defaultt=old)
    if not selected: return
    if probe_directory(selected,xbmcvfs):
        if not check_only: xbmcaddon.Addon().setSetting('recordings_folder',selected)
        from urllib.parse import urlsplit,urlunsplit
        parts=urlsplit(selected)
        display=urlunsplit((parts.scheme,parts.hostname or '',parts.path,'','')) if parts.scheme and parts.netloc else selected
        try:
            status=os.statvfs(xbmcvfs.translatePath(selected))
            space='{} MiB frei'.format(status.f_bavail*status.f_frsize//(1024*1024))
        except (AttributeError,OSError,RuntimeError): space='Freier Speicher über diesen VFS-Pfad nicht ermittelbar'
        xbmcgui.Dialog().ok('XCMate',display+'\n'+space+'\nVerzeichnis ist beschreibbar. Eine Aufnahmeengine ist damit noch nicht bestätigt.')
    else:
        xbmcgui.Dialog().ok('XCMate','Verzeichnis nicht zuverlässig beschreibbar. Die bisherige Einstellung bleibt erhalten.')
