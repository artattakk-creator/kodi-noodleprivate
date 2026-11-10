# Optionaler TMDB-Gateway-Client .87 – Entwicklungsvertrag für #417

Status: **CLIENT_PROTOTYP / KEIN PRODUKTIVER SERVER**. Nachträge P0-J/K aus main `6c748388e04ef021de0e6e7df193c1ab812c260c` wurden übernommen. Keine Domain, kein TLS-/Adminzugang, kein zentraler Token und keine Betriebsfreigabe vorhanden. Keine automatische Provisionierung behauptet. Installer .5.27 separat; veröffentlichte .5.26 bleibt identisch.

## Bereits implementiert

`tmdb_gateway_client87.py` und `tmdb_gateway_ui87.py`: leerer optionaler HTTPS-Endpoint, Status, explizites Starten/Fortsetzen einer Anfrage, getrennte Adminfreigabe prüfen, Statusprüfung und Widerruf nur dieser Geräteberechtigung. Keine Netzwerkprovisionierung beim Kodi-Start. Vorhandener gültiger lokaler Token hat Vorrang; ungültige vorhandene Datei blockiert einen stillen Rückfall, Opt-out bleibt verbindlich. Bestehender Tokenleser/-schreiber ist bytegleich. Neue Zugangsdaten ausschließlich in der privaten eigenen Profildatei `tmdb_gateway87.json`, mit Deskriptor-/Symlinkschutz, 0600, fsync/Replace/Readback, Profil-/Endpoint-/Cancel-/Revisionsprüfung. Keine Credentials in Kodi-Properties, Installerjournal, URL, ZIP oder Protokoll.

Client-Transport: Zertifikats-/Hostnameprüfung; ausschließlich HTTPS-Port 443, keine IP-Literale, Userinfo, Query oder Pfad im Gateway-Endpoint. Alle DNS-Antworten müssen öffentlich sein, Verbindung zur geprüften IP mit Original-SNI. Feste POST-Operationen, kein Redirect, kein generischer URL-Proxy; 1 MiB Antwortgrenze und feste Fehlercodes. Ein begrenzter UI-Task; Zurück/Timeout signalisiert Cancel, verhindert späte Speicherung. Der UI-Dialog endet spätestens nach acht Sekunden; DNS-/Systemaufrufe können einen einzelnen noch abwickelnden Task verzögern, weitere Aufgaben werden nicht endlos erzeugt.

Automatische und manuelle TMDB-Pfade verwenden dieselbe bestehende Zustimmung. Nur nach erfolgreicher, ausdrücklich bestätigter Kopplung und ohne lokalen Token wird ein interner Modusmarker in den Gateway umgeleitet; er wird niemals als anonymer Bearer an TMDB gesendet. TVMaze/Provider bleiben unabhängig. Eine nicht geheime Zufallsrevision invalidiert betroffene negative Suchcache-Sichten. Der Gateway erhält ausschließlich definierte TMDB-Leseoperationen, nie Providerdaten.

## Festgelegter API-Vertrag v1, noch kein produktiver Server

- `POST /v1/pair/start`: zufälliger 48-Byte-Installationsverifier bleibt privat, Request enthält nur seinen SHA256-Challenge und `S256`. Antwort: separater kryptographisch starker `device_code`, kurzer `user_code`, 30–600 Sekunden Gültigkeit, Pollintervall 5–60 Sekunden. Der sichtbare Freigabecode ist **keine** Geräteberechtigung.
- `POST /v1/pair/poll`: privater Device-Code und Verifier ausschließlich im TLS-Body. Server prüft Challenge, Ablauf, Adminfreigabe und einmalige atomare Ausgabe; PENDING ist kein Erfolg. Nach PAIRED werden Device-Code/Verifier durch eine gerätespezifische zufällige Berechtigung ersetzt. Vor lokalem Commit muss die signierte Statusprüfung erfolgreich sein.
- `POST /v1/status`, `/v1/tmdb`, `/v1/revoke`: Geräte-ID, UTC-Zeit, zufällige Nonce und HMAC-SHA256-Proof über `operation\ntime\nnonce\nsha256(body)` in Headers, ausschließlich unter verifiziertem TLS. Kein zentraler TMDB-Token. Der Server muss Uhrtoleranz (höchstens 30 Sekunden), pro Gerät atomaren Replay-Schutz und Widerruf prüfen. Manuelle Rotation: widerrufen und neu koppeln. Kurzlebige/asymmetrische Credentials sind eine mögliche weitere Härtung, hier nicht als umgesetzt ausgegeben.
- Erlaubt: configuration, search TV/movie/person, numerische TV-/Movie-Werke und definierte alternative_titles/external_ids/images/credits; eng begrenzte Query-Schlüssel/-längen, keine doppelten Parameter. Server muss dieselbe Allowlist unabhängig durchsetzen; zentrale Upstream-Autorisierung ausschließlich serverseitig.

## Noch BLOCKED / separat erforderlich

Kein lauffähiger produktiver Gateway, keine Admin-Weboberfläche/MFA, keine serverseitige persistente Freigabe-/Nonce-/Widerrufs-Datenbank, keine HSTS-/CSRF-/Rate-Limit-/Rotation-/Secret-Store-Betriebsabnahme. Der Clientvertrag und seine Fake-Gateway-Tests ersetzen diese Arbeiten nicht. Vor Deployment: eigene Serverimplementierung/Sicherheitsreview, echte Domain/TLS/Adminidentität, TMDB-Nutzungsbedingungen/Attribution/Datenschutz, Backup und ausdrückliche Freigabe. Keine ungesicherte Token-Dateiverteilung als Ausweg. Alternative Übertragung des zentralen Tokens ist nicht implementiert.

## Tests und Grenzen

Hosttests mit synthetischem Fake-Gateway prüfen Pending ohne Adminfreigabe, Challenge, Geräteproof/Nonce, Ablauf, Widerruf, lokale Persistenz, Update-/Modulneustart, Opt-out, bestehende/ungültige lokale Tokens, TLS-/Redirect-/Auth-/Rate-/MIME-/Größenfehler und Proxy-SSRF-Ablehnung. Diese Tests injizieren HTTP-Antworten; sie sind weder ein echter öffentlich erreichbarer Server noch eine physische Android-Abnahme. Alle echten P0-J/K-Updates, authentifizierte TMDB-Abfragen und neuen Geräteprüfungen: **ANDROID_NOT_TESTED**.
