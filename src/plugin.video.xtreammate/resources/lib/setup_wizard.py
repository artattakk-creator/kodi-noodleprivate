"""First-run guided XtreamMate configuration: scan before save, enrich after save."""
import re
from urllib.parse import urlsplit
import xbmcgui
from utils import info, warn

CHOICES = ('Stalker-Portal (MAC)', 'M3U-Datei (lokal)', 'M3U-Link (URL)', 'Xtream Codes')
CONTENTS = ('Live-TV / Sender', 'Filme / VOD', 'Serien')

class Cancelled(Exception):
    pass


def valid_server(value):
    """Local syntax validation only; do not ping a user-supplied service."""
    value = (value or '').strip().rstrip('/')
    if not re.match(r'^https?://', value, re.I):
        raise ValueError('Bitte eine vollständige http://- oder https://-Adresse eingeben.')
    p = urlsplit(value)
    if not p.hostname or p.username or p.password or p.fragment or p.query:
        raise ValueError('Bitte nur die Serveradresse ohne Zugangsdaten und Parameter eingeben.')
    return value


def get_choices(dlg):
    indices = dlg.multiselect('XtreamMate – Welche Inhalte übernehmen?', CONTENTS,
                              preselect=[0, 1, 2])
    if indices is None:
        raise Cancelled()
    if not indices:
        raise ValueError('Mindestens ein Inhaltsbereich muss ausgewählt sein.')
    chosen = set(indices)
    return {'include_live': 0 in chosen, 'include_vod': 1 in chosen, 'include_series': 2 in chosen}


def input_data(dlg, choice):
    data = {'name': 'Meine TV-Liste', 'epg_show': True}
    if choice == 3:
        data['type'] = 'xtream'
        data['xc_host'] = valid_server(dlg.input('Xtream Codes – Server-URL (mit Port)'))
        data['xc_user'] = dlg.input('Xtream Codes – Benutzername').strip()
        data['xc_pass'] = dlg.input('Xtream Codes – Kennwort',
                                    option=getattr(xbmcgui, 'ALPHANUM_HIDE_INPUT', 0))
        if not data['xc_user'] or not data['xc_pass']:
            raise ValueError('Benutzername und Kennwort sind erforderlich.')
    elif choice == 2:
        data['type'] = 'm3u'
        value = dlg.input('M3U – Playlist-Link').strip()
        data['m3u_url'] = valid_server(value) if value else ''
        if not data['m3u_url']:
            raise Cancelled()
        data['epg_url'] = dlg.input('EPG-URL (optional; leer lassen falls unbekannt)').strip()
    elif choice == 1:
        data['type'] = 'm3u'
        data['m3u_url'] = dlg.browseSingle(1, 'M3U-Datei auswählen', 'files', mask='.m3u|.m3u8')
        if not data['m3u_url']:
            raise Cancelled()
        data['epg_url'] = dlg.input('EPG-URL (optional; leer lassen falls unbekannt)').strip()
    elif choice == 0:
        data['type'] = 'stb'
        data['stb_url'] = valid_server(dlg.input('Stalker – Portal-URL'))
        data['stb_mac'] = dlg.input('Stalker – MAC-Adresse', defaultt='00:1A:79:00:00:00').strip()
        if not re.fullmatch(r'(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}', data['stb_mac']):
            raise ValueError('Die Stalker-MAC-Adresse hat kein gültiges Format.')
    return data


def scan_contents(data, progress):
    """Read index data, not every individual movie/episode or poster.

    Results include only entries that were returned by the provider.
    API cache persists the metadata lists during the scan.
    """
    report = {'groups': 0, 'live': 0, 'movies': 0, 'series': 0, 'epg': 0}
    def status(percent, message):
        if progress.iscanceled():
            raise Cancelled()
        progress.update(percent, message)
    kind = data['type']
    status(3, 'Verbindung prüfen …')
    if kind == 'xtream':
        from xtream import XtreamClient
        xc = XtreamClient(data['xc_host'], data['xc_user'], data['xc_pass'])
        auth = xc.authenticate() or {}
        ui = auth.get('user_info', {}) if isinstance(auth, dict) else {}
        if not ui or str(ui.get('auth', '0')).lower() not in ('1', 'true'):
            raise ValueError('Xtream-Zugang konnte nicht bestätigt werden. URL und Login prüfen.')
        if data['include_live']:
            status(18, 'Sendergruppen und Live-TV einlesen …')
            cats = xc.get_live_categories()
            streams = xc.get_live_streams()
            report['groups'] = len(cats)
            report['live'] = len(streams)
            status(38, '{} Gruppen, {} Sender gefunden'.format(report['groups'], report['live']))
        if data['include_vod']:
            status(45, 'Film-Katalog und verfügbare Cover-URLs erfassen …')
            xc.get_vod_categories()
            report['movies'] = len(xc.get_vod_streams())
            status(62, '{} Filme gefunden'.format(report['movies']))
        if data['include_series']:
            status(68, 'Serien-Katalog und Metadaten erfassen …')
            xc.get_series_categories()
            report['series'] = len(xc.get_series())
            status(83, '{} Serien gefunden'.format(report['series']))
    elif kind == 'm3u':
        from iptv import load_m3u, split_m3u_sections
        status(18, 'M3U-Playlist laden und auswerten …')
        channels = load_m3u(data['m3u_url'])
        if not channels:
            raise ValueError('Die M3U-Quelle enthält keine lesbaren Einträge.')
        parts = split_m3u_sections(channels)
        live = parts.get('live') or parts.get('tv') or []
        report['live'] = len(live) if data['include_live'] else 0
        report['movies'] = len(parts.get('movies', [])) if data['include_vod'] else 0
        report['series'] = len(parts.get('series', [])) if data['include_series'] else 0
        report['groups'] = len({c.group for c in channels})
    else:
        from stalker import StalkerClient
        status(18, 'Stalker-Portal authentifizieren …')
        sc = StalkerClient(data['stb_url'], data['stb_mac'])
        if not sc.authenticate():
            raise ValueError('Stalker-Portal konnte nicht authentifiziert werden.')
        if data['include_live']:
            status(30, 'TV-Sender laden …')
            report['groups'] = len(sc.get_live_categories())
            report['live'] = len(sc.get_live_channels())
        if data['include_vod']:
            status(55, 'Film-Katalog laden …')
            report['movies'] = len(sc.get_vod())
        if data['include_series']:
            status(72, 'Serien-Katalog laden …')
            report['series'] = len(sc.get_series())
    status(90, 'Importübersicht vorbereiten …')
    return report


def fmt_report(result):
    return ('Gefundene Einträge:\n\n'
            'Sendergruppen: {groups}\n'
            'TV-Sender: {live}\n'
            'Filme: {movies}\n'
            'Serien: {series}\n\n'
            'EPG und weitere Metadaten werden nach dem Speichern geladen, sofern verfügbar.').format(**result)


def complete_metadata(portal, report, progress):
    """Fetch XMLTV where offered; do not pre-download huge poster collections."""
    if not portal.get('include_live', True) or not portal.get('epg_show', True):
        progress.update(100, 'Import abgeschlossen.')
        return
    progress.update(94, 'EPG-Programmführer aktualisieren …')
    if progress.iscanceled():
        # Portal is saved; an EPG cancellation must not destroy imported channels.
        return
    try:
        from epg import _refresh_portal_epg
        loaded = _refresh_portal_epg(portal['id'], portal)
        report['epg'] = sum(len(x) for x in loaded.values()) if isinstance(loaded, dict) else 0
    except Exception as exc:
        warn('XtreamMate EPG optional phase failed: {}'.format(type(exc).__name__))
    progress.update(100, 'Import abgeschlossen.')


def setup():
    import portals
    dlg = xbmcgui.Dialog()
    try:
        typ = dlg.select('XtreamMate – Verbindung hinzufügen', CHOICES)
        if typ < 0:
            return None
        data = input_data(dlg, typ)
        data.update(get_choices(dlg))
        data['epg_show'] = bool(data['include_live'] and dlg.yesno(
            'XtreamMate – EPG', 'Programmführer (EPG) nach dem Speichern laden?'))
        if not dlg.yesno('XtreamMate – Import starten',
                         'Ausgewählte Inhalte jetzt scannen? Zugangsdaten bleiben lokal.'):
            return None
        scan = xbmcgui.DialogProgress()
        scan.create('XtreamMate – Senderlisten scannen', 'Verbindung wird hergestellt …')
        try:
            report = scan_contents(data, scan)
        finally:
            scan.close()
        dlg.ok('XtreamMate – Scanergebnis', fmt_report(report))
        title = dlg.input('Name der Programmliste', defaultt='Meine TV-Liste').strip()
        if not title:
            return None
        data['name'] = title
        if not dlg.yesno('XtreamMate – Speichern',
                         '„{}“ speichern und verfügbare Zusatzdaten laden?'.format(title)):
            return None
        portal = portals.add(data)
        if portal.get('type') == 'xtream' and portal.get('include_live', True):
            if dlg.yesno('XtreamMate – Sendergruppen',
                         'Möchtest du jetzt mehrere Sendergruppen aktivieren oder deaktivieren?'):
                try:
                    from group_selection import choose_groups
                    choose_groups(portal)
                except Exception as exc:
                    warn('XtreamMate group selector unavailable: {}'.format(type(exc).__name__))
        post = xbmcgui.DialogProgress()
        post.create('XtreamMate – EPG und Metadaten', 'EPG laden …')
        try:
            complete_metadata(portal, report, post)
        finally:
            post.close()
        dlg.ok('XtreamMate – Bereit',
               '„{}“ wurde gespeichert.\n\n'.format(title)+fmt_report(report)+
               '\n\nCover werden beim Durchblättern nachgeladen.')
        return portal
    except Cancelled:
        return None
    except ValueError as exc:
        dlg.ok('XtreamMate – Einrichtung nicht abgeschlossen', str(exc))
        return None
    except Exception as exc:
        warn('XtreamMate setup error: {}'.format(type(exc).__name__))
        dlg.ok('XtreamMate – Einrichtung fehlgeschlagen',
               'Scan fehlgeschlagen. Bitte Verbindung und Erreichbarkeit prüfen. ' 
               'Die Zugangsdaten wurden nicht übertragen.')
        return None
