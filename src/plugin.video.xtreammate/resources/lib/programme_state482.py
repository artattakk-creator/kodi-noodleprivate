"""Pure bounded image-state vocabulary for workers, details and Live Hero."""
POLICY={'IMAGE_EPG_DISABLED','IMAGE_EPG_DEFERRED','STORAGE_POLICY_INVALID'}
SETTINGS={'SETTINGS_XML_INVALID','SETTINGS_UNREADABLE','SETTINGS_API_UNAVAILABLE',
          'SETTINGS_READBACK_FAILED','SETTINGS_UNRELATED_CHANGED'}
ERRORS=POLICY|SETTINGS
TEXT={
 'IMAGE_EPG_DISABLED':'Bild-EPG ist deaktiviert. Bei Bedarf in der Bildverwaltung aktivieren.',
 'IMAGE_EPG_DEFERRED':'Bild-EPG wurde auf später verschoben. Die vorhandene Freigabe bitte in der Bildverwaltung prüfen.',
 'STORAGE_POLICY_INVALID':'Die Bildspeicher-Einstellung ist nicht lesbar. Bitte die Speicherverwaltung prüfen.',
 'SETTINGS_XML_INVALID':'Die Bildeinstellungen sind beschädigt. In der Bildverwaltung die vorhandene Sicherung prüfen.',
 'SETTINGS_UNREADABLE':'Die Bildeinstellungen sind nicht lesbar. Zugriff und vorhandene Sicherung prüfen.',
 'SETTINGS_API_UNAVAILABLE':'Kodi kann die Bildeinstellungen momentan nicht lesen. Bitte später erneut versuchen.',
 'SETTINGS_READBACK_FAILED':'Die Änderung der Bildeinstellungen konnte nicht bestätigt werden. Vorhandene Einstellungen prüfen.',
 'SETTINGS_UNRELATED_CHANGED':'Die Änderung der Bildeinstellungen konnte nicht sicher bestätigt werden.',
 'REQUESTED':'Bildsuche angefordert …','WAITING_SERVICE':'Bildsuche wartet auf den Hintergrunddienst …',
 'QUEUED':'Bildsuche eingeplant …','RUNNING':'Bildsuche läuft …',
 'LOCAL_IMAGE_READY':'Sendungsbild gefunden.',
 'IMAGE_URL_READY':'Bildadresse geprüft; Kodi lädt das Bild …',
 'IMAGE_URL_READY_RAM':'Bildadresse geprüft; Kodi lädt das Bild …',
 'FETCH_FAILED':'Bildsuche fehlgeschlagen. Bitte in den Sendungsdetails erneut versuchen.',
 'IMAGE_LOOKUP_TIMEOUT':'Bildsuche hat das Zeitbudget erreicht. Bitte erneut versuchen.',
 'TMDB_LOOKUP_DISABLED':'Eigene TMDB-Bildsuche ist nicht freigegeben. Vorhandene Einstellungen prüfen.',
 'TMDB_DISABLED':'Eigene TMDB-Bildsuche ist nicht freigegeben. Vorhandene Einstellungen prüfen.'}


def code(art):
    return str(art.get('retry_status74') or art.get('status68') or art.get('code') or '')


def text(art):return TEXT.get(code(art),'')


def error(error):
    value=getattr(error,'code','')
    return value if value in ERRORS else 'FETCH_FAILED'
