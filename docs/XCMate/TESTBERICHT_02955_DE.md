# XCMate .55 – vollständiger Host-/Regressionstestbericht

**2.339 Tests PASS in 321.431 s; 0 Fehler, 0 Failures, 0 Skips.** Alle 2.294 alten Testmethoden erhalten, 45 neue. Vollständiger synthetischer Log `TESTLOG_02955.txt`, Namen der neuen Tests `NEUE_TESTS_02955.json`, Prüfwerte `TESTERGEBNISSE_02955.json`.

Basis main .54 `2d08ff1e650505aa4d78a1128640d8baacb929c5`; sauberer git-archive-Abschlussstand `4d1487d8595006171d108c2635ecee99acad5c00`. Regulärer Bootstrap und drei Upgrade-Schritte, vollständiger Repository-/Paketbuild, de/en-Sprachvalidierung (je 1.128 Kontexte), 92 Navigationstexturen mit Herkunft/Lizenz, Python-compileall bestanden. Python 3.12, vorhandene Pillow-/impacket-0.13.0-/simpleeval-0.9.13-Hostabhängigkeiten. Reale lokale HTTP-, Socket-, signierte SMB2-, SQLite-/WAL-/Großdaten- und Unterbrechungstests liefen mit; keine Skips wegen fehlender Netzrechte.

## Neue Prüfungen und unveränderte Schutzgates

Propertyverlust/ungültiger Handoff, fremde Session/Owner/Modal, echter Overlay-Eingabegate-Aufruf, Back vor Übergabe, Settings erneut genau einmal, unveränderter Stop-Kern. Persistente positive/negative URLbelege, Zeitablauf, Quellen-/Portal-/Kanal-/Titelkollision, lokale Leser ohne HTTP/DNS/Enqueue, Hoständerung, Zugangsdaten im Pfad, Private-DNS-Antwort, PNG-/JPEG-Vorprüfung, 404, Jobgrenze24/Deduplizierung, Cancel/DB-busy sowie ein veralteter Producer-RAM-Zustand gegen einen bereits committed URL-Datensatz.

150 echte lokale Senderdatensätze ohne Kürzung; bestehende 88-Sender-, Quellenmapping-, DST-/UTC-/Tagesgrenzen-, Now/Next-, Autoplay-/Resume-, Suchmasken- und Player-/Fernbedienungstests unverändert mit ausgeführt. SQLite-Guide → native Home-ListItems → EPG-Detail verwenden dieselbe Eventbindung und gespeicherte URL. Zusätzlich originale native Picker-/2.1.0-Compiler-/Profilleserprüfungen, vier Datei-Backups, alle Austauschfehler/Crashpositionen, unbekannte Hashes/Fremdänderungen, exakter .50-Upgrade-/Rückrollpfad und Erkennung eines überholten .50-Anwendungsbelegs.

600 Paketdateien: 596 frühere Dateien vorhanden, davon 574 exakt unverändert und 22 exakt deklarierte/normalisierte Deltas; vier additive Dateien. Wizard-/Import-/Stop-Freeze: 36 Dateien direkt **ohne Normalisierung** auf identische Bytes geprüft. Original-Icon, Suchmaske, Portale, Gruppen-/Resume-/Autoplay-Code und alte Kunstdateien erhalten. 62 fremde WIP-Dateien in den beiden anderen Arbeitsbäumen zusätzlich SHA256-identisch. Keine Gerätedaten, installierten Skinprofile, Box A oder Box B angefasst.

## Zwischenbefunde transparent

Ein früher unfreigegebener Workspace-Lauf konnte lokale HTTP-/SMB-Server wegen fehlender Socketrechte nicht öffnen. Der dokumentierte Abschlusslauf lief mit den notwendigen Netzrechten und allen realen lokalen Serverfällen. Der erste saubere vollständige Lauf hatte zwei Testprobleme: historischer direkter Rohhashvertrag für die ausdrücklich geänderte Skin-Datei und ein URL-Hintergrundjob, der Kodi-Teststubs nach Fixture-Ende weiter importierte. Der Vertrag normalisiert nun ausschließlich die exakt gehashten .55-Deltas; aktuelle Tests prüfen die neue Implementierung direkt. Unbeteiligte GUI-Fixtures isolieren die Hintergrundqueue wie bereits die vorhandenen Medienworker; Rotation und tatsächliche Queuegrenzen besitzen gesonderte Tests. Keine Abschwächung der Daten-/Ziel-/Back-/Freigabegates, keine zusätzlichen Skips.

Danach bestand ein vollständiger Wiederholungslauf mit 2.337 Tests in 320.838s. Danach bestanden 2.338 Tests in 318,570s inklusive Schutz vor älteren RAM-Vorschauen. Ein weiterer gezielter Test reproduzierte den fehlerhaften ACTIVE-Abgleich zweier leerer Owner-Leases; nichtleere echte Ownership ist jetzt Voraussetzung. Auch dieser Fall ist im hier maßgeblichen 2.339er Gesamtlauf enthalten. Historische Sechs-Einträge-Tests sind nur um den beauftragten passiven Widgets-Ordner ergänzt; Testmethodennamen bleiben erhalten. Versionsasserts auf .55, Producer-Testdoubles auf die neue Referenzqueue angepasst. Die bereits früher vorhandenen SMB-Vendor-Syntax-/simpleeval-AST-Warnungen wurden nicht durch unaufgeforderte Vendoränderungen überdeckt.

## Paket und CI

`plugin.video.xtreammate-0.1.29.55.zip`: 3,148,833 Bytes, 600 Dateien. SHA256:

`c7a92d5513d43faa6fc4b0da6330c7729ff71847b9b0f7d6336e00005b87596b`

CRC, sichere Pfade, keine Symlinks, keine Profile/DBs/Rohlogs/Bytecodes, jedes Sourcebyte/AST und ein unabhängiger deterministischer ZIP-Nachbau PASS. Kein Repository-Index/Produktivrelease veröffentlicht. Vier-Dateien-BINGIE-Prüfarchiv mit eigenem SHA256 separat unter integrations. Der abschließende GitHub-CI-Run am finalen Draft-PR-Head und die Gleichheit seines Android-Testartefakts werden im PR verlinkt und geprüft; kein erneuter Quellenumbau für reine CI-Verlinkungen.

## Geräteabnahme und Grenzen

**24 Android-Gates NOT_TESTED, 0 Android-PASS behauptet.** `ANDROID_ABNAHME_02955_DE.md`: zuerst vertikale Navigation/Settings/Back, danach native drei Widgetbindungen, separat freigegebener Home-Adapter, 88+/150 Sender, dieselben echten Bilder für Film/konkrete Episode/XMLTV-Event in Hero und EPG-Detail, Neustart, 404/Offline, Medien und Popup. Keine Pixel-/Bild-/Kodi-Core-Erfolge aus ListItem-/Hostsimulation ableiten.

Reale Nutzerprovider, tatsächliche TMDb-Zuordnung und BINGIE-Texturdecodierung sind hier nicht verfügbar. Weitere Bildhosts erfordern exakte vertrauenswürdige Freigabe; fehlende Lizenz/Schnittstelle bei TV Spielfilm bleibt explizit blockiert. Ein neutraler Fallback zählt nicht als echtes Sendungsbild-PASS. Der reproduzierte lokale Eingabeblocker ist beseitigt; der neue Android-Hänger ist damit noch nicht als vollständig abgenommen erklärt. Kein Merge/Release ohne ausdrückliche Freigabe.
