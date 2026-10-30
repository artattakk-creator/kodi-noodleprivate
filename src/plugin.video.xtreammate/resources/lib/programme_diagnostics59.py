"""Local, stage-specific programme image explanations; no lookups or popups."""
def message(event,art):
    if not event.get('title') or not event.get('start') or not event.get('stop'):
        return 'Keine Programmdaten: Anbieter-EPG laden und Senderzuordnung prüfen. Sender bleibt auswählbar.'
    code=art.get('code','PENDING')
    if art.get('source')!='placeholder' and art.get('image'):return 'Bildreferenz bereit; Darstellung durch Kodi. Quelle: '+str(art.get('source',''))
    return {
        'BLOCKED_IMAGE_HOST_OR_URL':'Bildadresse vorhanden, aber Host oder URL nicht freigegeben. Zulässige Bildquelle prüfen.',
        'BLOCKED_CREDENTIAL_URL':'Bildadresse enthält private Zugangsdaten und wird nicht angezeigt.',
        'HTTP_NOT_FOUND':'Bildquelle liefert kein Bild (HTTP 404/410). Programmdaten bleiben verfügbar.',
        'TIMEOUT':'Bildquelle antwortet zu langsam. EPG bleibt bedienbar.',
        'IMAGE_PREFLIGHT_FAILED':'Bildquelle momentan nicht erreichbar oder nicht überprüfbar.',
        'INVALID_IMAGE':'Geladene Daten sind kein unterstütztes Bild.',
        'URL_EXPIRED':'Gespeicherte Bildadresse abgelaufen; Hintergrundaktualisierung ausstehend.',
        'AWAITING_BACKGROUND_REFRESH':'Sendungsdaten vorhanden; Bildprüfung im Hintergrund ausstehend.',
        'NO_IMAGE':'Sendungsdaten vorhanden; keine passende Bildquelle bestätigt.',
        'NO_MATCH':'Sendungsdaten vorhanden; kein eindeutiger Bildtreffer.',
        'PENDING':'Sendungsdaten vorhanden; Bildstatus noch nicht bestätigt.',
    }.get(code,'Kein bestätigtes Sendungsbild ('+str(code)+'). Programmdaten bleiben verfügbar.')
