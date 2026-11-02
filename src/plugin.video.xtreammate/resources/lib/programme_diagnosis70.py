"""Human-readable failure/result distinction; pure and credential-free."""
def explain(art):
 code=art.get('status68',art.get('code','PENDING'))
 ready=art.get('code') in ('READY','READY_STALE') and art.get('source') not in (None,'','placeholder') and bool(art.get('image'))
 if ready:
  if art.get('storage69')!='RAM_ONLY':return ''
  return 'Bild gefunden und geprüft. Kodi lädt die Bildadresse. Der Metadatencache ist momentan nicht beschreibbar ('+str(art.get('storage_code69','UNCONFIRMED'))+'); die Bildreferenz bleibt für diese Sitzung nutzbar.'
 reasons={'HELPER_TIMEOUT':'TMDB Helper hat nicht rechtzeitig geantwortet. Kein Sendungsbild bestätigt.',
          'HELPER_BACKGROUND_UNAVAILABLE':'TMDB Helper konnte im Hintergrund keine Auskunft liefern. Kein Sendungsbild bestätigt.',
          'HELPER_NOT_AVAILABLE':'TMDB Helper ist nicht verfügbar. Kein Sendungsbild bestätigt.',
          'HELPER_VERSION_UNSUPPORTED':'Diese TMDB-Helper-Version wird für die Bildsuche nicht unterstützt.',
          'REQUESTED':'Bildauftrag an den XCMate-Hintergrunddienst übergeben.',
          'WAITING_SERVICE':'Bildauftrag übergeben; der Hintergrunddienst hat die Bearbeitung noch nicht bestätigt.',
          'NOT_SCHEDULED':'Für diese Sendung wurde noch kein Bildauftrag bestätigt.',
          'PENDING':'Sendungsdaten vorhanden; Bildprüfung noch nicht bestätigt.'}
 if code not in reasons and art.get('storage69')!='RAM_ONLY':return ''
 text=reasons.get(code,'Kein bestätigtes Sendungsbild ('+str(code)+').')
 from programme_outcomes70 import clean
 outcomes=clean(art.get('sources70',[]));own=next((v for v in outcomes if v['source']=='tmdb'),None)
 config=art.get('lookup70') if isinstance(art.get('lookup70'),dict) else {}
 if own and own['code'] not in ('FOUND','DISABLED'):
  own_reasons={'NO_CONFIRMED_IMAGE':'keine eindeutige Bildzuordnung bestätigt','HTTP_AUTH':'Zugriff abgewiesen; bestehenden Zugang testen','HTTP_RATE_LIMIT':'Anfragelimit erreicht','TMDB_TOKEN_FILE_INVALID':'vorhandener Zugang derzeit nicht sicher lesbar','TMDB_TOKEN_MISSING':'kein verwendbarer Zugang gemeldet'}
  text+=' Eigene TMDB-Suche: '+own_reasons.get(own['code'],'nicht erfolgreich ('+own['code']+')')+'.'
 elif config and not config.get('own'):
  text+=' Die eigene TMDB-Suche ist in den vorhandenen EPG-Einstellungen ausgeschaltet; Zugang und Freigabe sind getrennte Einstellungen.'
 if art.get('storage69')=='RAM_ONLY':
  text+=' Nur der Fehlerstatus wurde für diese Sitzung gemerkt; es wartet kein gefundenes Bild auf den Download.'
  reason=art.get('storage_code69')
  if reason not in (None,'READY','UNCONFIRMED'):text+=' Metadatencache: '+str(reason)+'.'
 return text+' EPG-Text und Zurück bleiben verfügbar.'
