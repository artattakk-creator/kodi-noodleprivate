"""Local, stage-specific programme image explanations; no lookups or popups."""
def _diagnostic_message84(event,art):
    if not event.get('title') or not event.get('start') or not event.get('stop'):
        return 'Keine Programmdaten: Anbieter-EPG laden und Senderzuordnung prüfen. Sender bleibt auswählbar.'
    code=art.get('code','PENDING')
    from programme_diagnosis70 import explain
    explanation70=explain(art)
    if explanation70:return explanation70
    if art.get('failure_reason68'):return str(art['failure_reason68'])+': '+str(art.get('storage68',{}))+' – keine Sicherheitsreserve automatisch verändert.'
    if art.get('code') in ('READY','READY_STALE') and art.get('source')!='placeholder' and art.get('image'):return str(art.get('status68','LOCAL_IMAGE_READY' if isinstance(art.get('image'),str) and __import__('os').path.isabs(art['image']) and not art.get('url_version55') else 'IMAGE_READY'))+': Bildreferenz bereit; Darstellung durch Kodi; sichtbare Texture separat prüfen. Quelle: '+str(art.get('source',''))
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
        'TMDB_DISABLED':'TMDB-Bildsuche nicht aktiviert. Optional beide TMDB-Schalter und privaten Token prüfen.',
        'TMDB_TOKEN_MISSING':'Kein privater TMDB Read Access Token hinterlegt. Verbindungstest in den EPG-Einstellungen verwenden.',
        'HTTP_AUTH':'TMDB-Zugriff verweigert. Privaten Token mit dem Verbindungstest prüfen.',
        'HTTP_RATE_LIMIT':'Anfragelimit erreicht. Hintergrundsuche pausiert; später erneut prüfen.',
        'NO_MATCH_AMBIGUOUS':'Mehrere passende Serien oder unvollständige Trefferliste; kein Bild ohne eindeutige Zuordnung.',
        'NO_ARTWORK':'Eindeutige Sendungszuordnung, aber kein geeignetes Serien-/Episodenbild vorhanden.',
        'FETCH_ERROR':'Zuordnung bestätigt; Bilddownload fehlgeschlagen. Text bleibt verfügbar.',
        'CACHE_ERROR':'Bild konnte nicht sicher im lokalen Cache gespeichert werden.',
        'CACHE_IO_ERROR':'Bildspeicherung fehlgeschlagen; Rechte und Speicherstatus prüfen.',
        'PROGRAMME_CACHE_BUDGET':'Internes Budget für Sendungsbilder erreicht; bestehende Bilder bleiben erhalten.',
        'NOT_CLASSIFIED_MOVIE':'Sendungstyp nicht sicher für die Bildsuche eingeordnet; kein geratenes Filmposter.',
        'TMDB_TOKEN_FILE_INVALID':'Privater TMDB-Zugang ist nicht sicher lesbar. Vorhandenen Zugang prüfen; keinen anderen Token automatisch verwenden.',
        'GUI_NOT_UPDATED':'Lokale Bilddatei vorhanden; sichtbare Kodi-Ausgabe noch nicht bestätigt.',
        'NO_MATCH':'Sendungsdaten vorhanden; kein eindeutiger Bildtreffer.',
        'PENDING':'NOT_SCHEDULED: Sendungsdaten vorhanden; noch kein Bildauftrag bestätigt.',
        'NOT_SCHEDULED':'NOT_SCHEDULED: Noch kein Auftrag für diese Sendung bestätigt.',
        'QUEUED':'QUEUED: Bildprüfung für diese Sendung eingeplant.',
        'RUNNING':'RUNNING: Bildsuche und Download werden im Hintergrund geprüft.',
        'CACHE_MISS':'CACHE_MISS: Kein gültiger lokaler Sendungseintrag verfügbar.',
        'CACHE_MISMATCH':'CACHE_MISMATCH: Quell- oder Sendungsrevision hat sich geändert; kein fremdes Bild übernommen.',
        'DB_FULL':'DB_FULL: Bild-/Programmdatenbank kann nicht schreiben; internes Limit und freien Speicher getrennt prüfen.',
        'FETCH_FAILED':'FETCH_FAILED: Hintergrundauftrag fehlgeschlagen; keine Bilddarstellung bestätigt.',
        'TMDB_LOOKUP_DISABLED':'TMDB_LOOKUP_DISABLED: Bildsuche unter EPG / TMDB-Zugang aktivieren.',
        'LOCAL_IMAGE_READY':'LOCAL_IMAGE_READY: Lokale Bilddatei geprüft. Sichtbare Kodi-Texture separat abnehmen.',
    }.get(code,'Kein bestätigtes Sendungsbild ('+str(code)+'). Programmdaten bleiben verfügbar.')


def message(event,art,diagnostic=False):
    if art.get('provisional85'):
        return 'Bildvorschlag – Zuordnung nicht bestätigt. Über das Kontextmenü Serie/Bild zuweisen oder Vorschlag ausblenden.'
    explanations85={'EVENT_CHANGED':'Die Programmdaten wurden aktualisiert. Das passende Bild wird erneut geprüft.','SOURCE_CHANGED':'Die EPG-Quelle wurde aktualisiert. Das passende Bild wird erneut geprüft.','FILE_INVALID':'Das gespeicherte Bild ist nicht verwendbar. Eine neue Bildprüfung ist eingeplant.','EXPIRED':'Die Bildfreigabe ist abgelaufen. Das Bild wird erneut geprüft.','POLICY_CHANGED':'Die Bildfreigaben haben sich geändert. Die aktuellen Einstellungen werden berücksichtigt.','NO_SOURCE_FACTS':'Lokale Programmdaten sind momentan nicht vollständig verfügbar. Die Ansicht bleibt bedienbar.'}
    text=explanations85.get(art.get('code')) or _diagnostic_message84(event,art)
    import re
    if diagnostic:
        code=str(art.get('code','PENDING'))
        return (code if re.fullmatch(r'[A-Z0-9_]{1,48}',code) else 'UNCLASSIFIED')+': '+text
    text=re.sub(r'\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b(?::\s*)?', '', text)
    text=re.sub(r'\s*\(\s*\)', '', text)
    text=re.sub(r'\s+([.;:,])',r'\1',text)
    return text.strip()
