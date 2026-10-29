# XCMate .56 – Host- und Regressionstestbericht

**2.369 Tests PASS in 326.589 Sekunden; 0 Failures, 0 Fehler, 0 Skips.** Alle 2.339 früheren Testmethoden bleiben erhalten, 30 neue Tests. Vollständige Ausgabe: `TESTLOG_02956.txt`; neue Methoden: `NEUE_TESTS_02956.json`; maschinenlesbarer Bericht: `TESTERGEBNISSE_02956.json`.

Sauberer git-archive-Quellstand `8393abf5b70cd3cd0eafdba5e79460d403d9ea6c`, kumulativ auf main .55 `c1e5816f5f24f2ebc703205bb543fd4f449a2951`. Regulärer Bootstrap, drei historische Upgrades, Repository-/ZIP-Build, Sprachvalidierung, Navigationstexturen/Herkunft und Python-compileall bestanden. Python 3.12 mit Pillow, impacket 0.13.0, simpleeval 0.9.13. Lokale HTTP-/Socket-/signierte SMB2-/WAL-/Großdaten- und Unterbrechungstests wurden tatsächlich ausgeführt; keine netzbedingten Skips.

## Neue Fälle und reproduzierbare Defekte

Die vier ersten Regressionstests scheiterten gegen .55 mit drei FAIL/einem ERROR: schreibgesperrte Snapshotdatei blendet lesbare Medien aus; gespeicherte unveränderte Routen liefern deshalb null Items; Serienjahr als String; EPG-Lesefehler bricht 150-Sender-Feed ab. Dieselben Fälle bestehen nach Korrektur. Dies ist ein Hostnachweis konkreter Codefehler, noch kein Beweis der tatsächlichen Ursache aller leeren Reihen auf Box B.

RO-Fallback für Live/Film/Serie bei echter flock-Konkurrenz, EROFS und unverändertem committed WAL-Datenbestand; keine lockfreien gemeinsamen Snapshotwrites. Zehn verschiedene Coverreferenzen samt richtigen Portal-/Detailklickzielen, getypte Serienmetadaten, deaktivierte Gruppen/fehlende Portal-ID, keine Fake-Navigationskachel, RAM-Reload bei schreibgesperrter Snapshotumgebung und unveränderte Hooks. 12.000 Serien, 24 Titel über nachgewiesene PK-Seeks ohne SCAN; keine Erhöhung des .35/.15-SQL-Budgets. 150 Sender bleiben auch ohne EPG-Anreicherung sichtbar als native ListItem-Daten; echte Androidpixel werden dadurch nicht behauptet.

Synthetischer vollständiger Harry-Potter-Titel ohne Jahr, unabhängige Detailbestätigung, Remake-/Sequel-/Teilseiten-/ID-/Jahreskollisionen, keine blinde Genreannahme, fehlende API/URL, positive persistente URL nach RAM-Neustart, stille GUI-Reader ohne API/Enqueue, Hintergrund bei unveränderter Revision, angekündigter Film nach NEXT und Programmlücke ohne NOW. Echter lokaler Guide/Event-/Artworkindex und Detail-Control 110 nutzen dieselbe URL wie der Widget-Ereignisdatensatz **erst beim selben tatsächlichen Ereignis**. Kein vorgezogenes Bild eines künftigen Films für NOW.

## Schutz und Testvertragsänderungen

602 Paketdateien: sämtliche 600 früheren Dateien vorhanden, 580 byteidentisch, 20 exakt deklarierte überprüfte Deltas, zwei additive Module. Wizard-/Import-/Stop-/Player-/Skinfreeze wird direkt auf Rohbytes geprüft; Routing-/Picker-/URL-Dateien bleiben byteidentisch, sämtliche AST-Knoten in app_routes außer der bestehenden Widgetausgabe unverändert. Der Renderer zeigt Serien-Artwork und entfernt nur die leere Navigations-Fakekachel. Kein Routingumbau. 62 Dateien fremder paralleler WIP-Arbeitsbäume ebenfalls SHA256-identisch.

Der erste volle Workspace-Lauf traf auf einen historischen Testvertrag, der für eine leere Serienquelle noch eine Navigationskachel verlangte. Diese einzelne Erwartung wurde gemäß #271 auf ehrlich leere Serienausgabe geändert; Film-/Live-Status und keine Netzwerkabfrage bleiben geprüft. Der frühere Serienmetadatentest erwartet nun int/float statt Providerstrings. Der frühere Serien-Assettest prüft nun zusätzlich die unveränderte lokale Coverdatei statt eines absichtlichen Ausschlusses aller Serienreferenzen. Der alte Idle-Session-Service-Test isoliert additive App-Worker, damit deren Importthread nach Fixture-Ende keine ersetzten Kodi-Module mehr verwendet; Session-Grace und der echte separate Warmup-Threadtest bleiben unverändert geprüft. Versionsasserts folgen .56. Keine alte Methode entfernt, kein Skip ergänzt. Historische Quellschutztests normalisieren ausschließlich die exakt gehashten, offengelegten .56-Deltas; neue Tests prüfen deren heutiges Verhalten und den unveränderten Rest direkt.

## Paket

`plugin.video.xtreammate-0.1.29.56.zip`: 3,152,719 Bytes, 602 Dateien. SHA256:

`6164dba454738a63f65958afba0ff58fdd87aa1e5d87d26578f23f54bf71b204`

CRC, Pfade, vollständige Sourcebytes/AST, keine Profile/DBs/Rohlogs/Symlinks/Bytecodes und unabhängiger deterministischer ZIP-Nachbau PASS. `PAKETPRUEFUNG_02956.json`, Dateikatalog und Schutzbericht enthalten Einzelbelege. GitHub-CI am finalen Draft-PR-Head samt Paket-SHA wird im PR verlinkt. Kein main-Merge, Produktionsindex, Release oder automatischer Skinpatch.

## Offen bis zur Geräteprüfung

**Elf Android-Gates NOT_TESTED**, siehe `ANDROID_ABNAHME_02956_DE.md`. Ohne separate Skinfreigabe ist die Ausführung des optionalen Hero-Gates BLOCKED. Film-/Serienposter, schmale horizontale native Live-Reihe, reale Harry-Potter-/Episoden-/Eventbilder, BINGIE-Texturdecodierung und Neustartpersistenz benötigen den echten Box-B-Nachweis. Box A/B und installierte Skins/Profile wurden nicht verändert. Privater nichtkommerzieller Kontext berücksichtigt; echte Provider und Bild-APIs hier nicht verfügbar. TV Spielfilm bleibt BLOCKED_NO_AUTHORIZED_API. #269 bleibt separat offen und Wizard .54 unverändert. Kein Platzhalter als Bild-PASS und keine CI-Simulation als Android-Abnahme.
