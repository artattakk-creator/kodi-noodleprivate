# #111 – gezielter Poster-Reparaturansatz nach .33

24.10.2026. Eigener Dokumentations-Draft auf main `6bb96547ec469e62c5f69e23a928842021bab4c4`. **Noch kein Poster-Codefix, keine neue Add-on-Version, kein zusätzlicher Android-Testauftrag.** Guide-/Such-Handoff .34 wird separat entwickelt; dieser Entwurf darf dessen Abnahme nicht verzögern.

## Nachgewiesener Istpfad

1. `detail_menu.DetailMenuMixin._detail_menu_click`, Aktion 2: Kopie des ausgewählten Datensatzes, `_request(retry, ready)` auf dem vorhandenen Owner-/Worker-System.
2. `media_art.retry_poster`: gültige Kandidaten ausschließlich aus `cover`, `stream_icon`, `movie_image`, `cover_big`. Existierende lokale Bilder bleiben erhalten; keine Suche nach neuen externen Bildkandidaten. Status/Snapshot nur für dieses Bild lesen.
3. Nach fehlgeschlagener Quelle höchstens eine andere bekannte Adresse **dieses** Datensatzes wählen, `art_store.retry_one` und priorisierte vorhandene Queue (`-20`) aufwecken. Keine Fanart oder fremden Titel mit anfordern.
4. `retry_one`: DB-Transaktion, laufenden Worker respektieren; HTTP-429- und 60-Sekunden-User-Cooldown erhalten. Einzelnen Job reaktivieren, keine globale Queue-Rücksetzung.
5. `run_one → fetch`: bestehende DB-Worker-Lease; HTTP timeout 4 s / Gesamtdauer 6 s / maximal 3 MiB / keine versteckten HTTP-Retries. Bildformat-/Pixelprüfung, Budget/Mindestfreiraumprüfung, lokale temporäre Datei, fsync, atomisches Replace und persistenter READY-Status. HTTP-, DNS-, TLS-, Timeout-, Speicher- und Cachefehler sind intern bereits klassifiziert.
6. Die unmittelbare Menü-Rückmeldung ist der **Queue-Status**, nicht der abgeschlossene Download. Ein Timeout kann daher aus unterschiedlichen Phasen stammen; ohne passende Phasenereignisse ist eine konkrete Netzursache nicht belegt. Bestehende Revisionsabfrage aktualisiert sichtbare lokale Bilder nach Worker-Erfolg.

`metadata_views` verarbeitet Providerdaten. Auf dieser main-Basis gibt es keinen TMDb-Suchclient und keinen TMDb-Kandidatenabruf im Retry. Vorhandene Fremd-WIP-Dateien werden nicht übernommen. Der .33-Logzeitraum enthält keinen ausreichenden ART-/TMDb-Fehlernachweis; der Nutzerbefund bleibt FAIL.

## Getrennter nächster Codepatch

Gezielte, begrenzte Diagnose nur nach expliziter Einzelbildaktion:

- Zufällige Retry-ID im Speicher; Zuordnung ausschließlich zum ausgewählten Bild, maximal 32 Einträge, TTL 10 Minuten. Keine neue DB-Spalte, kein Quell- oder Profilreset.
- Feste Phasen `SELECT`, `SNAPSHOT`, `QUEUE`, `CLAIM`, `HTTP`, `VALIDATE`, `SAVE`, `READY` / `FAILED`; Dauer und feste Fehlercodes. Nur interne Zuordnung zur URL, **niemals** URL/Host/Pfad, URL-Hash, Titel, Suchtext, Portal-ID, Header, Tokens oder Exceptiontext in Logs.
- Keine weiteren Requests zur Diagnose (kein zusätzliches HEAD/GET), nur bereits ausgeführten HTTP-Vorgang instrumentieren. TLS-Prüfung, Limits, Budget, SQLite-Worker-Lease und Backoff unverändert.
- Menüstatus klar zwischen „eingereiht“, „läuft“, „Wartezeit aktiv“, „lokal verfügbar“ und abgeschlossenem Fehler trennen. Worker-Endstatus im sichtbaren Detailbild anzeigen; keine GUI-Aufrufe aus Netzwerkthreads, kein neuer globaler Poller.
- Nachweisbar unveränderte Kandidaten nicht unendlich erneut testen. Bestehende manuelle 60-Sekunden-Schranke, Server-Cooldowns und begrenzte automatische Versuche bleiben. Alternativquelle gehört weiterhin zum ausgewählten Datensatz; keine Bilder anhand unscharfer Titel ungefragt ersetzen.
- Bei DB_BUSY ausschließlich verständlicher Rückgabecode; beim HTTP-Timeout Quelle/Phase unterscheiden; bei SAVE-Fehler bestehende Cachedatei und fremde Jobs erhalten. Kein globaler „Retry alle“-Aufruf.

Erst mit Phasennachweis die tatsächlich fehlerhafte Stufe reparieren. Keine Behauptung, dass längere Timeouts oder TMDb den bisherigen Android-Timeout bewiesen beheben.

## Optionaler TMDb-Fallback als eigene Erweiterung

Voraussetzungen vor Implementierung: unterstützte und sicher konfigurierte API-Authentifizierung, korrekte TMDb-Nennung/Lizenzhinweise, Film/Serie und eindeutige ID bzw. Titel/Jahr-Sprache. Zugangsdaten nur private Einstellungen; keine Schlüssel im Repo oder Log.

Explizite Aktion „Alternative Poster suchen“ für den einzelnen Titel. Kleine begrenzte Kandidatenliste mit Quelle/Jahr anzeigen, Nutzer wählt ein Bild; bei mehrdeutigen Treffern kein automatisches Ersetzen. Such-/Bildabruf abbrechbar, HTTPS, feste TMDb-API/Bildziele, Rate-Limit/Timeout/Größenbudget und negative Cache-TTL. Kein Providercredential-Forwarding. Gewähltes Poster über bestehenden persistenten Artwork-Worker laden und lokal speichern. Fehler verändern weder Providerdaten noch vorhandene Bilder.

Bis diese Voraussetzungen und Tests implementiert sind, darf der bestehende Retry nicht als „TMDb-Suche“ bezeichnet werden.

## Geplante Nachweise für den separaten Code-Draft

- Lokaler HTTP-Testserver: Erfolg, langsamer Header/Body, DNS-/TLS-Fehlerklassen, 401/403,404,429 mit Retry-After,500, ungültiges/zu großes Bild und abgebrochener Download.
- Queue und echte SQLite: nur ausgewählter Job verändert; fremde Jobs/Dateien, Worker-Lease, Cooldowns und bestehendes READY erhalten; DB_BUSY/readonly/full kontrolliert; keine Endlosschleife.
- Atomare Dateiablage, Neustart-Persistenz, sichtbare Aktualisierung ohne Fokus-/Auswahlverlust; Datenschutz mit absichtlich geheimen URLs/Titeln/Exceptions beweisen.
- Metadatenauswahl bei optionalem TMDb: Film gegen Serie, gleichnamige Titel, Jahr/Sprache, leere/mehrdeutige Kandidaten,429/Abbruch. Keine automatische Ersatzwahl bei Mehrdeutigkeit.

Vorhandene Hosttests `tests/test_xcmate_poster_retry_02928.py` decken sechs Einzelbild-/Datenintegritätsfälle ab. Deren PASS ist keine neue Android-Abnahme und kein Beleg für funktionierenden TMDb-Fallback. .34 G1–G4 bleiben die einzigen aktuell angeforderten Gerätetests. #111 bleibt offen. Keine Merges/Releases/Cachelöschungen.
