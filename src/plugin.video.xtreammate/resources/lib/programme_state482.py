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
 'RESERVE_BLOCKED':'Bildspeicherung durch die Sicherheitsreserve begrenzt. Speicherverwaltung prüfen.',
 'SAFE_RESERVE_BLOCKED':'Bildspeicherung durch die Sicherheitsreserve begrenzt. Speicherverwaltung prüfen.',
 'NO_IMAGE':'Für diese Sendung wurde kein passendes Bild gefunden.',
 'NO_MATCH':'Für diese Sendung wurde kein eindeutiger Bildtreffer gefunden.',
 'NO_MATCH_AMBIGUOUS':'Mehrere Bildtreffer. In den Sendungsdetails eine Zuordnung prüfen.',
 'HTTP_AUTH':'Die Bildquelle verweigert den Zugriff. Freigaben in der Bildverwaltung prüfen.',
 'HTTP_RATE_LIMIT':'Die Bildquelle begrenzt Anfragen. Später erneut versuchen.',
 'TIMEOUT':'Die Bildquelle hat das Zeitbudget erreicht. Bitte erneut versuchen.',
 'BLOCKED_IMAGE_HOST_OR_URL':'Die Bildquelle wurde aus Sicherheitsgründen gesperrt.',
 'TMDB_TOKEN_MISSING':'Der vorhandene TMDB-Zugang ist momentan nicht verfügbar. Einstellungen prüfen.',
 'PROGRAMME_DB_UNAVAILABLE':'Bilddatenbank momentan nicht verfügbar. Bitte später erneut versuchen.',
 'DISK_FULL':'Nicht genügend freier Speicher für das Bild. Speicherverwaltung prüfen.',
 'BUDGET_FULL':'Das Bildspeicherbudget ist erreicht. Speicherverwaltung prüfen.',
 'FETCH_FAILED':'Bildsuche fehlgeschlagen. Bitte in den Sendungsdetails erneut versuchen.',
 'IMAGE_LOOKUP_TIMEOUT':'Bildsuche hat das Zeitbudget erreicht. Bitte erneut versuchen.',
 'TMDB_LOOKUP_DISABLED':'Eigene TMDB-Bildsuche ist nicht freigegeben. Vorhandene Einstellungen prüfen.',
 'TMDB_DISABLED':'Eigene TMDB-Bildsuche ist nicht freigegeben. Vorhandene Einstellungen prüfen.'}


def code(art):
    return str(art.get('retry_status74') or art.get('status68') or art.get('code') or '')


def text(art):
    value=code(art)
    return TEXT.get(value,'Bildstatus nicht verfügbar. Bitte die Sendungsdetails prüfen.' if value and value not in ('READY','READY_STALE','IMAGE_READY') else '')


def error(error):
    value=getattr(error,'code','')
    return value if value in ERRORS else 'FETCH_FAILED'
