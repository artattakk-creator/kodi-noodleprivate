# TMDB: sichere Entwicklungsprobe und Installer-Anforderung (17.11.2026)

## Entscheidung

- Das Repository-Secret `TMDB_READ_ACCESS_TOKEN` wurde vom Nutzer im GitHub-UI eingerichtet. Sein **Wert ist nicht einsehbar und seine Funktion noch nicht verifiziert**.
- Der **nächste GS Media Setup Wizard** soll die in Issue #449 beschriebene *optionale* und explizit autorisierte Funktion „TMDB-Zugang von geschütztem GS-Media-Server importieren“ erhalten.
- Erst nach Komponenteninstallation prüfen, ob bereits ein gültiger lokaler Token existiert; vorhandenen Token nicht löschen/überschreiben. Alternativen: private Datei, manuelle Eingabe, überspringen. Der restliche Installer bleibt bei 401/403, Offline, Timeout und ungültigen Daten nutzbar.
- Nur HTTPS, validiertes Zertifikat und Host-Allowlist; Zugangsdaten separat eingeben und nicht persistieren; Verzeichnisschutz/cPanel oder privater Auslieferungsendpunkt muss vom Serveradministrator eingerichtet und extern abgenommen werden.
- Den GitHub-Secret-Wert **niemals** in Installations-ZIP, Repo-Dateien, Testartefakte, öffentliche URL, Telegram-Nachrichten oder Kodi-Logs übernehmen. GitHub Secrets können nicht von einem anonymen Kodi-Client sicher abgefragt werden.
- Geplanter GS-Media-Serverimport gibt den zentralen Token an die Box aus. Er ist daher kein echtes Gateway und schützt **nicht** gegen Extraktion auf einem kompromittierten Gerät. Die stärkere, weiterhin zurückgestellte Gateway-Variante bleibt Issue #417.
- Vorhandene Funktionen `tmdb_token61.import_bytes`, `token_write64`, `tmdb_access61.py` und `tmdb_import63.py` wiederverwenden; keine eigenmächtige Änderung an produktiven Versionen. Direkter Live-Test nach Import und bestätigter persistenter Readback.

## Manuell ausführbarer CI-Smoke-Test

Der vorbereitete Workflow `.github/workflows/tmdb-token-smoke.yml` ist **ausschließlich per workflow_dispatch** startbar; es erfolgt **kein Checkout** von Pull-Request-Code und es werden keine Repo-Schreibrechte benötigt. Das GitHub-Secret wird nur in der Laufzeit-Umgebung des dedizierten Testschritts bereitgestellt.

Er überprüft:
1. `GET /3/configuration` mit Authorization Bearer: gültige Authentifizierung und gültige Bildkonfiguration.
2. `GET /3/movie/550?language=de-DE`: echte Filmmetadaten mit Posterpfad.
3. `GET https://image.tmdb.org/t/p/w185...`: Bild-HTTP-Status, Content-Type, begrenzte Bytes und Datei-Signatur.

Ausgabe ausschließlich der technischen PASS/FAIL-Kennzeichen, HTTP-Statuscodes und `KODI_ANDROID_NOT_TESTED`; keine Zugangsdaten, Pfade oder Bilddateien als Artefakte.

**Wichtig:** Dieser Test bestätigt den TMDB-Zugriff **von einem GitHub-Runner**. Er testet nicht den GS-Media-Serverimport, kein Kodi-Token-Readback und keine sichtbaren Bilder in Mini-EPG, Detailfenster oder BINGIE. Diese Tests gehören in einen getrennten Installer-/Kodi-Testblock einschließlich echter Android-Geräteabnahme.

## Aktivierung / Status

- Dieser separate Draft-PR muss technisch und sicherheitlich geprüft und ausdrücklich für main freigegeben werden. **Vorher lässt sich der Workflow nicht aus dem GitHub-Actions-Menü starten.**
- Danach: Actions → „TMDB read-token and poster smoke test (manual, no release)“ → Run workflow.
- Fehlt das Secret oder ist es ungültig, soll der Lauf mit einem anonymisierten Code fehlschlagen. Niemals zu Debugzwecken die Umgebungsvariable, HTTP-Header oder Rohantwort ausgeben.
- Kein Merge, kein Release, kein Installer-Publish und keine automatische Geräteänderung aus diesem Test.

Relevante Issues: #449 (vereinfachter Installer-Import), #417 (Gateway-Backlog), #443 (Bild-EPG-Installer), #468 / #469 (TMDB-Bildpipeline).
