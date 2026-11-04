"""Owner-thread rescan window; workers carry plain data and cancellation only."""
import threading

from vodsync_api72 import failure, KINDS

LABELS = dict(vod='Filme', series='Serien')
MESSAGES = {
    'SOURCE_EMPTY': 'Gültige leere Antwort. Das VOD-Angebot ist damit nicht abschließend geklärt; Zugang/Anbieter-API vergleichen.',
    'FILTERED_SOURCE': 'Die Antwort enthält keine Titel der gewählten Gruppe.',
    'SCHEMA': 'Unbekanntes Antwortformat (z. B. HTML oder nicht unterstützte JSON-Struktur).',
    'AUTH_SCHEMA': 'Die Anmeldung liefert kein gültiges Xtream-Kontoprofil.',
    'AUTH': 'Die Anmeldung wurde abgelehnt. Bestehende Zugangsdaten prüfen.',
    'ACCOUNT_DISABLED': 'Der Kontostatus ist nicht aktiv.',
    'VOD_DISABLED': 'Filme sind laut Kontoprofil für diesen Zugang deaktiviert.',
    'SERIES_DISABLED': 'Serien sind laut Kontoprofil für diesen Zugang deaktiviert.',
    'FORBIDDEN': 'Der Anbieter verweigert diesen API-Zugriff (HTTP 403).',
    'ENDPOINT_MISSING': 'Der API-Endpunkt ist nicht vorhanden (HTTP 404).',
    'RATE_LIMIT': 'Anbieterlimit erreicht. Später bewusst erneut versuchen.',
    'HTTP': 'HTTP-Fehler beim Anbieterabruf.',
    'TIMEOUT': 'Die Anbieterabfrage hat ihr Zeitlimit erreicht.',
    'NETWORK': 'Verbindungsfehler beim Anbieterabruf.',
    'TLS': 'Die gesicherte Verbindung konnte nicht verifiziert werden.',
    'PARTIAL_RESPONSE': 'Die Antwort ist unvollständig. Keine Teilgruppe veröffentlicht.',
    'TRUNCATED': 'Die Übertragung wurde vor dem vollständigen Ende unterbrochen.',
    'PAGINATION': 'Die Seitennavigation der Anbieterantwort ist nicht eindeutig.',
    'IDENTITY': 'Eine eindeutige Kategorie-/Titel-ID fehlt.',
    'DUPLICATE_ID': 'Doppelte IDs oder wiederholte Anbieterseiten. Keine Teilgruppe veröffentlicht.',
    'SPACE': 'Nicht genug freier Speicher einschließlich Sicherheitsreserve. Keine Daten löschen.',
    'READONLY': 'Der Kodi-Datenpfad ist schreibgeschützt.',
    'PERMISSION': 'Der private Datenpfad ist nicht beschreibbar.',
    'SQLITE': 'Datenbanksperre oder SQLite-Schreibfehler. Später erneut versuchen.',
    'BUSY': 'Ein Katalogauftrag arbeitet bereits. Kein zweiter Scan wurde gestartet.',
    'SOURCE_TYPE': 'Dieser sichere Nachscan unterstützt Xtream-Verbindungen. Der vorhandene andere Portaltyp bleibt unverändert.',
    'CONNECTION_CHANGED': 'Die Provider-Verbindung wurde inzwischen geändert. Neu öffnen und erneut prüfen.',
    'CANCELLED': 'Abgebrochen. Bereits vollständig verifizierte Gruppen bleiben erhalten; keine Teilgruppe freigegeben.',
}


def describe(code):
    return MESSAGES.get(code, 'Der Nachscan konnte nicht vollständig verifiziert werden. Bestand bleibt erhalten; erneut prüfen.') + ' [' + code + ']'


def preselected(pid, kind, rows):
    from group_selection import _read, _state
    state = _state(_read(), pid, kind)
    first = state is None or not state['known'] and not state['enabled']
    return [i for i, g in enumerate(rows) if first or str(g['category_id']) in state['enabled']]


def progress_text(value):
    phase = value.get('phase', '')
    text = 'Katalog aktualisieren · ' + phase
    if value.get('kind'): text += ' · ' + LABELS[value['kind']]
    if value.get('group'): text += '\nGruppe ' + str(value['group']) + ' / ' + str(value['groups'])
    for key, label in (('groups', 'Gruppen'), ('read', 'gelesen'), ('new', 'neu'), ('changed', 'geändert'), ('unchanged', 'unverändert'), ('skipped', 'übersprungen')):
        if key in value: text += '\n' + label + ': ' + str(value[key])
    return text


def result_text(report):
    heading = {'DONE': 'Nachscan verifiziert abgeschlossen.', 'PARTIAL': 'Nachscan teilweise abgeschlossen.',
               'FAILED': 'Nachscan nicht erfolgreich.', 'CANCELLED': 'Nachscan abgebrochen.'}[report['state']]
    text = heading + '\n' + str(report['groups_committed']) + ' Gruppen vollständig veröffentlicht.'
    text += '\n' + ' · '.join(LABELS[k] + ': ' + str(report['groups_found'][k]) + ' gefunden / ' + str(report['groups_selected'][k]) + ' ausgewählt' for k in report['groups_found'])
    text += '\nMeldungen/Fehler: ' + str(len(report['errors']))
    text += '\n' + ' · '.join(label + ': ' + str(report[key]) for key, label in (
        ('read', 'gelesen'), ('new', 'neu'), ('changed', 'geändert'), ('unchanged', 'unverändert'), ('skipped', 'übersprungen')))
    text += '\nDB-Readback: ' + ' · '.join(LABELS[k] + ': ' + str(v) for k, v in report['readback'].items())
    for error in report['errors']:
        text += '\n' + LABELS[error['kind']] + ': ' + describe(error['code'])
    return text


def show(portal):
    import xbmcaddon
    import xbmcgui
    from menu_icons45 import multiselect
    from setup_window import WorkWindow
    from vodsync72 import Session
    chosen = multiselect(xbmcgui.Dialog(), 'Katalog aktualisieren · Bereiche (nur Filme/Serien)',
                         ['Filme', 'Serien'], preselect=[0, 1], default='list')
    if not chosen: return
    kinds = tuple(KINDS[i] for i in chosen if type(i) is int and 0 <= i < 2)
    holder = {}  # Worker data only, never a Window reference.

    class CatalogWindow(WorkWindow):
        def onInit(self):
            if self._initialized: return
            self._initialized = True
            for cid in (5, 6, 10, 11, 12, 13, 14, 15, 19, 21, 100, 101, 102):
                self.getControl(cid).setVisible(False)
            for cid in (16, 17, 18): self.getControl(cid).setVisible(True)
            self.getControl(3).setHeight(380); self.getControl(4).setPosition(45, 485)
            self.getControl(2).setLabel('Katalog aktualisieren · bestehender Provider: ' + str(portal.get('name', ''))[:80])
            self.getControl(16).setLabel('Starten'); self.getControl(17).setLabel('Ergebnis'); self.getControl(18).setLabel('Abbrechen')
            self.setFocusId(18); self.selection = {}; self.report = None; self.stage = 'discover'
            data = self._data_state; cancelled = self.cancel.is_set
            def discover():
                if cancelled(): return None
                session = holder.get('session') or Session(portal, kinds); holder['session'] = session
                return session.discover(cancelled, lambda n, v: data.status(n, progress_text(v)))
            holder['discover'] = discover
            self.work(discover, self.discovered)

        def discovered(self, groups):
            if groups is None: self.close(); return
            session = holder['session']
            for kind in kinds:
                rows = groups.get(kind, [])
                if not rows:
                    xbmcgui.Dialog().ok('Katalog aktualisieren · ' + LABELS[kind], describe(session.errors.get(kind, 'SOURCE_EMPTY')))
                    continue
                selected = multiselect(xbmcgui.Dialog(), LABELS[kind] + ': Gruppen auswählen · neue Gruppen ausdrücklich bestätigen',
                    [str(g['category_name']) for g in rows],
                    preselect=preselected(portal['id'], kind, rows), default='list')
                if selected is None: self.close(); return
                self.selection[kind] = {str(rows[i]['category_id']) for i in selected if type(i) is int and 0 <= i < len(rows)}
            self.stage = 'ready'
            self.getControl(16).setEnabled(True)
            text = '\n'.join(LABELS[k] + ': ' + str(len(groups.get(k, []))) + ' gefunden / ' + str(len(self.selection.get(k, []))) + ' ausgewählt' for k in kinds)
            self.status(None, text + '\nStarten übernimmt nur vollständig geprüfte Gruppen. Live-TV und EPG werden nicht abgefragt oder verändert.')
            self.setFocusId(16 if any(self.selection.values()) else 18)

        def working(self):
            self.getControl(16).setEnabled(False); self.getControl(17).setEnabled(False)
            self.getControl(18).setEnabled(True); self.setFocusId(18)

        def pump(self):
            super().pump()
            if self._initialized and not self.busy and not self._closed:
                self.getControl(16).setEnabled(any(self.selection.values()) or self.stage in ('ready','failed'))
                self.getControl(17).setEnabled(self.report is not None)

        def completed(self, report):
            self.report = report; self.stage = 'result'
            self.getControl(16).setEnabled(True); self.getControl(17).setEnabled(True)
            self.status(100, result_text(report)); self.getControl(16).setLabel('Erneut prüfen / wiederholen')
            self.getControl(18).setLabel('Schließen'); self.setFocusId(17)

        def failed_work(self, exc):
            self.stage = 'failed'; self.status(None, describe(failure(exc).code))
            self.getControl(16).setLabel('Erneut versuchen'); self.setFocusId(18)

        def onClick(self, cid):
            if cid == 18: self.close(); return
            if self.busy: return
            if cid == 17 and self.report is not None:
                xbmcgui.Dialog().ok('Katalog aktualisieren · Ergebnis', result_text(self.report)); return
            if cid == 16 and not any(self.selection.values()) and self.stage in ('ready','failed'):
                self.work(holder['discover'], self.discovered); return
            if cid == 16 and any(self.selection.values()):
                # No accidental provider refresh from a focus/Back event.
                if not xbmcgui.Dialog().yesno('Katalog aktualisieren', 'Gewählte Film-/Seriengruppen jetzt sicher nachscannen?', nolabel='Abbrechen', yeslabel='Starten'): return
                data = self._data_state; cancelled = self.cancel.is_set; selected = dict(self.selection)
                self.work(lambda: holder['session'].run(selected, cancelled, lambda n, v: data.status(n, progress_text(v))), self.completed)

    window = CatalogWindow('XCMateSetup.xml', xbmcaddon.Addon('plugin.video.xtreammate').getAddonInfo('path'), 'Default', '720p')
    window.configure_work()
    # Kodi's show()/onInit is asynchronous; the owner pump may run first.
    window.selection = {}; window.report = None; window.stage = 'discover'
    window._data_state.cleanup = lambda: holder.get('session') and holder['session'].close()
    window.run()
