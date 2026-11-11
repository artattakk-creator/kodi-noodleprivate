# GS Media Setup Wizard 0.5.28 – optionaler Import eines privaten TMDB-Tokens

**Status: ENTWICKLUNGSENTWURF – nicht veröffentlicht, nicht produktiv installiert.**  
GitHub-Branch: `feat/gsmedia-0528-cloud-tmdb-token-import`  
Ausgangspaket: veröffentlichtes Setup `0.5.26`, bytegenau per SHA-256 `5aa5d101a57adda5dbb1f5d05319da1ec185676dc784817b25dea267322ae0af` geprüft.  
Ein separater Draft für das Paarungs-Gateway (`0.5.27`, PR #418) bleibt offen und **wird hier nicht als bereits produktiv oder funktionsfähig ausgegeben**. Das Gateway #417 bleibt zurückgestellt.

## Benutzerauftrag / tatsächlicher Umfang

Bei erfolgreicher Installation (48 Komponenten, BINGIE-Branding) optional anzeigen:

**„TMDB-Token importieren“**

Die Benutzerwahl **Überspringen** oder fehlende/ungültige Quelle darf die erfolgreiche Installation nicht rückgängig machen, nicht die Konfiguration löschen und nicht zu einem zweiten 48-Komponentenlauf führen. Dieselbe Aktion ist später aus dem Installer-Menü `TMDB-Token importieren (privates GitHub / Google Drive)` erreichbar.

### Unterstützte private Quellen – keine Freigabe des Tokens als öffentliche Datei!

1. **Privates GitHub-Repository:** Nutzer gibt `owner/repo/path/to/token.txt` und **einmalig** einen *Fine-grained Personal Access Token*, idealerweise nur mit `Contents: Read-only` für dieses einzelne Repository, ein. Kodi ruft ausschließlich den fest codierten GitHub-API-Host über HTTPS auf, ohne Redirect, ohne Zugangsdaten in der URL oder im Journal. Der PAT wird **nicht gespeichert**. Die Datei bleibt im privaten Repository, nicht im öffentlichen Release-ZIP, `addons.xml` oder einer Konfigurationsdatei.
2. **Privates Google Drive:** Nutzer gibt die **Datei-ID** einer privaten Textdatei und **ein bereits autorisiertes, kurzlebiges Google OAuth Access Token** mit Berechtigung für genau diesen Zugriff ein. Der Installer nutzt `GET https://www.googleapis.com/drive/v3/files/{fileId}?alt=media` über TLS und ohne Redirect. **Das ist ein authentifizierter API-Download, aber noch keine vollständig integrierte Google-Kontoanmeldung.** Die in diesem Chat verbundene Google-Drive-App kann ihre OAuth-Sitzung nicht an Kodi übertragen.
3. **Beliebige öffentliche GitHub-Raw-URLs, öffentliche Drive-Sharing-Links oder beliebige HTTP/HTTPS-Webverzeichnisse werden absichtlich NICHT als sicherer TMDB-Tokenimport unterstützt.** Eine ungeprüfte, öffentlich lesbare Token-Datei würde den Zugriff für beliebige Besucher offenlegen. Ein privater eigener Web-Endpunkt benötigt eine dedizierte Anmeldung/Token-Issuance und wird erst nach konkreter Backend-Freigabe entwickelt.

**Wichtige Google-Einschränkung:** Googles OAuth-Gerätefluss für Fernseher erlaubt nur `drive.file` oder `drive.appdata`, **nicht `drive.readonly` für beliebige bestehende private Drive-Dateien**. Das normale `add_token.txt` einer persönlichen Ablage wird dadurch nicht automatisch lesbar. Eine direkte, nutzerfreundliche Google-Konto-Verknüpfung erfordert eine autorisierte App-/Backend-/Picker-Lösung und eine neue Sicherheitsabnahme; ist **nicht** durch dieses Modul implementiert. Quelle: https://developers.google.com/identity/protocols/oauth2/limited-input-device

## Sicherheits- und Datenvertrag

- Keine Zugangsdaten aus ChatGPT-Connectoren oder fremden Apps übernehmen. Kein Zugriff auf den tatsächlichen TMDB-Token durch den Chat/Entwicklungsprozess; der Dateiinhalt verbleibt beim Nutzer.
- **Keine Tokens oder Provider-IDs in GitHub, Kodi-Logs, Journal-/Statusdateien, UI-Properties, ZIPs oder Fehlermeldungen.** Einmalige Lesecredentials werden ausschließlich zur jeweiligen HTTPS-Anfrage im Arbeitsspeicher gehalten und danach verworfen; kein dauerhaftes GitHub-/Google-Login.
- Host und API-Pfad strikt beschränkt auf `api.github.com/repos/{owner}/{repo}/contents/{path}?ref=main` bzw. `www.googleapis.com/drive/v3/files/{fileId}?alt=media`; keine beliebigen Quell-Hosts, keine IP-Adressen, keine Redirects, keine `file://`- oder `smb://`-Angaben als Webpfad.
- Maximal 4.097 Bytes für Token-Rohdaten und 16 KiB für GitHub-API-JSON; per Content-Length und begrenztem Lesevorgang. Nur tatsächliche UTF-8-Textdatei mit formal gültigem TMDB Read Access JWT akzeptieren.
- **Live-Validierung** mit der bereits vorhandenen `tmdb_connection60.request(... /configuration)`. Erst nach 200/korrektem TMDB-Bildschema wird mit `tmdb_token61.import_bytes(...,expected=None)` in die XCMate-Kodi-Profildatei geschrieben, mit atomarem Rename, fsync und Readback. Kein Überschreiben eines vorhandenen Datei-Tokens, selbst wenn dieser ungültig ist; kein Überschreiben des Legacy-Einstellungstokens oder einer deaktivierten TMDB-Suche.
- Der Dialog wird auf dem Kodi-Hauptthread angezeigt, Netzwerk/Schreibjob läuft begrenzt in einem Hintergrundworker. Bei Abbruch/Timeout darf kein neuer Auftrag im Hintergrund unbemerkt später schreiben; Cancel vor Commit prüfen. Erfolgsstatus erst nach erfolgreichem Readback.
- Das neue Modul verwendet kein `tmdb_gateway_client87`-Server-Pairing und installiert keinen zusätzlichen Drittanbieter-Helper. `script.gsmedia.setup 0.5.26` bleibt in allen Repos unverändert.

## Was noch fehlt, um es „automatisch aus meinem Drive holen“ nennen zu dürfen

Für einen echten, mit einem Fernseh-Code startbaren Google-Drive-Import muss zunächst ein **Google Cloud OAuth Client** bzw. eine abgesicherte private Freigabe existieren, die Zugriff auf die konkrete Datei ermöglicht. Der Nutzer muss den Zugriff einmalig auf einem Gerät mit Browser bestätigen. Ohne diese Berechtigung kann Kodi **nicht** auf ein privates Google-Drive-Konto zugreifen, auch wenn die Datei über die ChatGPT-Drive-App auffindbar ist. Ein Apps-Script- oder Gateway-Endpunkt ist noch nicht freigegeben oder eingerichtet.

Deshalb **nicht** behaupten, die private Drive-Datei werde bereits automatisch ohne Einrichtung aus der Cloud geladen. Der vorhandene Import funktioniert nur, wenn ein gültiger temporärer OAuth-Zugang bereits bereitgestellt wurde.

## Entwickler-Testmatrix und Release-Gates

- **Host:** unveränderte `0.5.26`-ZIP-Mitglieder, deterministischer `0.5.28`-Build, exakt 48 Komponenten, Basispaket-SHA, ZIP-CRC, keine Änderungen an regulärem/Pilot/NeoDark3-Katalog.
- **Import:** synthetischer privater GitHub-JSON-Contents-Response und synthetisches Drive-`alt=media`; keine echten Bearer/Credentials in Tests; ungültige URI, Path-Traversal, zu große Antwort, Redirect, ungültiger TMDB-JWT, TMDB-401, Schreibblockade, vorhandener Token, Opt-out, Cancel und zwei gleichzeitige Anfragen.
- **Android:** Kodi 21.3/ARM32 mit echter Installation und Test-Cloud-Zugang; 48/48 + Branding, Skip/Retry, bereits existierenden Token schützen, Live-Abfrage bestätigen, Kodi-Neustart und XCMate `TMDB-Verbindung testen`. Noch **ANDROID_NOT_TESTED**.
- **Lieferung:** branch + **Draft PR** + GitHub-Actions-Artefakt `script.gsmedia.setup-0.5.28.zip` inkl. SHA256 und `verification.json`; ausdrücklich **keine automatische Veröffentlichung**.

## Produktionsfreigabe

Kein Merge, kein Release/Repo-Update, keine Annahme von Host-PASS als Android-PASS. Die direkte Google-Kontoverbindung bleibt von diesem Review-Entwurf getrennt. Benutzerdaten, BINGIE-Widgets, lokale TMDB-Datei und XCMate 0.1.29.88/0.1.29.89 bleiben unverändert.
