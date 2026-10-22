# XCMate 0.1.29.20 – Artwork und Herkunftsinformationen

Stand 22.10.2026, Europe/Berlin. Basis **main `de0b13c` / 0.1.29.19**; eigener Branch `fix/xcmate-02920-artwork`. Freie .20 vorab gegen vorhandene Versionen/Remote-Branches/Tags geprüft. Android-Tests 42–46 laut Nutzer für die tatsächlich geprüften Abläufe vollständig PASS; keine neuen Fehler daraus ableiten. .19 bleibt Rückfallbasis. Neue .20-Funktionen **Android NOT_TESTED**.

## Befund zu #41/#90

Es gibt keinen nachgewiesenen 240-Bilder-Hardstop: 240 begrenzt das native Medienfenster. `_prefetch()` fordert auch die angehängten 24er-Batches bereits auf einem Worker an. Fehlende individuelle Providerbilder können ohne Gerätedaten nicht pauschal dem Budget zugeschrieben werden. Belegt sind der 512-MiB-Default, die alte Budgetfehlermeldung als `SPACE_FULL` und erschöpfte Jobs mit attempts>=3. Zusätzlich meldete Nutzer in Test 43 Platzhalter beim tiefen Scrollen, während die Navigation PASS blieb.

Die neue read-only Diagnose unterscheidet **keine Quelle**, **ungültige Quelle**, **noch nicht eingereiht**, **PENDING/RUNNING**, **NETWORK_ERROR**, **INVALID_IMAGE**, **CACHE_ERROR**, **BUDGET_FULL**, **DISK_FULL**, alte **SPACE_FULL** und **DB_BUSY/DB_UNAVAILABLE**. Eine URL, ein Dateipfad, Token oder Exceptiontext wird dabei nicht ausgegeben. READY wird zuerst anhand des validierten lokalen Bildes festgestellt, auch wenn die Statistik vorübergehend nicht verfügbar ist. Kein erfundenes Providerbild für NO_SOURCE.

## Speicherverfahren

- `media_art_budget_mb`: neuer Default **0 = nach verfügbarem Gerätespeicher**, kein 512-MiB-Hardstop und keine 4096-MiB-Obergrenze. Positive Werte bleiben bewusst gesetzte feste MiB-Limits.
- Kodi speichert teils auch unveränderte Defaultwerte: Ein als `default="true"` gespeicherter alter 512-Wert wird beim Lesen als neuer Automatikdefault behandelt. **Explizite 512 und andere eigene Werte bleiben erhalten**, ebenso zweifelhafte ältere Werte ohne Defaultmarker. Kein Schreiben/Migrieren der Benutzereinstellungen. Falls der Status weiterhin ein bewusst gespeichertes volles Limit zeigt, kann der Nutzer selbst 0 wählen.
- `media_art_reserve_mb`: Standard **1024 MiB**, mindestens **32 MiB** als unverzichtbare Untergrenze. Vor HTTP wird genügend Platz für die maximal zulässige Datei geprüft; nach Empfang wird tatsächliche Dateigröße und erneut freier Speicher geprüft. Unbekannte Kapazität erlaubt keinen ungesicherten Download. Tatsächliches ENOSPC/Reserve und ein konfiguriertes Bildlimit bleiben getrennt. Auch neue Queue-Einträge beachten die Reserve; pro Schreibvorgang werden zusätzlich 256 KiB für SQLite-/Dateisystem-Overhead freigehalten.
- Unveränderte Datei-/Pixelgrenzen: höchstens 3 MiB, maximal 4096 je Kante/8 MiPixel, unterstützte PNG/JPEG-Dimensionen. Kein beliebig großes Providerbild; kein neuer Codec/Resizer. Schreiben in temporäre Datei, Flush/fsync und atomarer Austausch erst nach Prüfung. Vorhandene valide Bilder werden nicht erneut heruntergeladen, bereinigt oder gelöscht. Ein beschädigtes Cachebild kann erst nach erfolgreichem validiertem Download atomar ersetzt werden.
- Neue Einstellung **Bilddownloads pausieren** verhindert neue Download-/Recovery-Aufträge; ein bereits laufender Download darf innerhalb seines bestehenden Zeitlimits enden. Lesen vorhandener Bilder bleibt möglich. Keine automatische Cachebereinigung.

## Queue, Wiederaufnahme und SQLite (#69 berücksichtigen)

`jobs` und seine Spalten bleiben bestehen. Eine additive Tabelle `art_recovery(ident,policy)` merkt die gezielte Wiederaufnahme; kein Löschen/Neuaufbau der Queue. Je unveränderter Konfiguration aus Limit/Reserve erhält ein blockierter Job höchstens **eine automatische Wiederaufnahme**. Freiraumschwankungen erzeugen ausdrücklich keinen neuen Policy-Token. Nach erneuter Speicherblockade bleibt der Job gesperrt bis Konfigurationsänderung oder expliziter Wiederholen-Aktion. Neu erstmals blockierte Jobs können damit nach freigegebenem Platz einmal automatisch wieder anlaufen.

Nach positiver Kapazitätsprüfung werden höchstens **32** SPACE_FULL/BUDGET_FULL/DISK_FULL-Jobs je Durchlauf, maximal einmal pro fünf Sekunden/Interpreter, reaktiviert; auch attempts>=3. Auswahl priorisiert sichtbare Anforderungen. Der Policy-Eintrag und Statuswechsel erfolgen zusammen in einer SQLite-Transaktion, sodass mehrere Interpreter dieselbe Wiederaufnahme nicht doppelt vergeben. READY und Netzwerk-/ungültige Bildfehler werden dabei nicht zurückgesetzt. Netzwerk-/Cachefehler bleiben auf drei Jobversuche mit Backoff begrenzt; ungültige Quellen/Bilder werden nicht automatisch immer wieder geladen. Die vorhandene ausdrücklich aufgerufene Wiederholen-Aktion bleibt ein eigener Nutzerbefehl.

`media_art.request()` schreibt nicht mehr synchron aus GUI-/D-Pad-Callbacks in SQLite. Ein begrenzter flüchtiger Eingang (2048 deduplizierte URLs; ältere niedrig priorisierte **unpersistierte** Anforderungen dürfen bei Überlast weichen) wird von einem eigenen Worker in Portionen bis 48 eingetragen. Bereits persistierte Jobs werden nie dafür entfernt. SQLite-Anmeldung maximal drei Versuche, nach Fehlern fünf Sekunden Abstand; sichtbare Anforderungen bleiben währenddessen vorgemerkt. Ein separater Downloader übernimmt die persistente Queue. Höchstens ein Anmelde- und ein Downloadthread je Interpreter; der bestehende DB-Lease begrenzt Downloads zusätzlich zwischen Interpretern. Keine geteilten SQLite-Verbindungen/Deaktivierung der Threadprüfung.

Sichtbare Live-/EPG-Logos erhalten Priorität -10, sichtbare Cover 0, Hintergrund-VOD 20. Jeder achte erfolgreiche Claim berücksichtigt den ältesten berechtigten Job, damit niedrigere Prioritäten im laufenden Worker vorankommen. Ein verlorener Jobclaim gibt seinen Lease sofort wieder frei; ein veralteter Worker überschreibt weder READY eines Nachfolgers noch dessen Lease mit einer späten Fehlermeldung.

Maintenance-Locks, Online-Backups einschließlich WAL, bestehende Fehlerklassifikation und bewiesene Index-Reparaturregeln bleiben unverändert. Keine automatische Wartung/Reparatur durch diese neue Diagnose, kein REINDEX/Reset/Rebuild zum Beheben fehlender Poster. Bestehende allgemeine DB-BUSY-Backoffs werden nicht als pauschal behoben behauptet. #69/#91 bleiben entsprechend offen.

## Sichtbare Aktualisierung und Status

Medien-Owner übernimmt heruntergeladene lokale Dateien weiter ohne Listenreset; vorhandener Fokus, Position und Posterlayout bleiben erhalten. Der bestehende Zwei-Sekunden-Watch bereitet zusätzlich eine private, read-only Diagnose des aktuell fokussierten Titels auf dem Worker vor. Die Fußzeile zeigt den lesbaren Posterstatus neben der Back-Hilfe. Initialer Continue-/Favoritenfokus wird dabei korrekt berücksichtigt. EPG-Logos verwenden denselben persistenten Store und die bestehende lokale Aktualisierung im Guide; keine neue Player-/Zeitachsensteuerung.

Unter Einstellungen → Speicher → Bildspeicherstatus stehen freier/gesamter Platz, Mindestreserve, fester oder automatischer Grenzwert, Pause und Jobzahlen. Queue-Bytes können ältere noch nicht registrierte Cachedateien auslassen; reale Kapazität wird deshalb separat vom Dateisystem gelesen. Der alte SPACE_FULL-Zähler ist kein Beweis eines physisch vollen Laufwerks.

## Nutzerwunsch zu Titel und Lizenzen

Add-on-Name bleibt **XCMate**, Anbieterzeile wird **GS Media** ohne „Fork of mr-evil1“. Add-on-ID und Profile ändern sich nicht. Die Add-on-Informationsbeschreibung enthält den Herkunftshinweis weiterhin. Neues Menü Einstellungen → Info → **Lizenzen und Herkunft anzeigen** öffnet die vollständigen bestehenden `ORIGIN_AND_CHANGES.txt` und `LICENSE` auch ohne aktives Portal. Beide Dateien und ihre Hinweise bleiben bytegleich. Der Source-Link im Add-on zeigt nun zum tatsächlich veränderten Projekt; Upstream-Link und GPL-Urheberschaft bleiben in Beschreibung/Origin sichtbar. Kein Lizenzwechsel, keine Entfernung von Copyright.

## Prüfung und Grenzen

Neue Regressionen verwenden je **500 synthetische Film-/Serientitel mit insgesamt 1000 unterschiedlichen Bildadressen** und einer gültigen PNG-Testgrafik: echte lokale Dateien/SQLite, tiefe Kategorieansicht >240, sichtbare Übernahme, Rückscrollen und Modulneustart ohne erneuten HTTP-Aufruf. Kein echter Provider-/Androidtest und keine Behauptung 1000 unterschiedlicher Motive. Weitere Tests betreffen reale Worker/SQLite, physische Reserve vor/nach HTTP, explizite Limits/default-Marker, erschöpfte Space-Jobs, persistente Retry-Marker, Fehlertypen/Datenschutz, Pause, Priorität/Fairness, Claim-/Lease-Races, alte Schema-Daten und Lizenzroute.

Ursprüngliche Freeze-Hashes werden nicht pauschal ersetzt: genau benannte unveränderte .19-Artwork-Funktionen für Dateiübernahme/Lock/Backup/Repair bleiben AST-geprüft; neue Queue-/Budgetteile erhalten eigene Tests. Die einzige Navigationserweiterung ist die ausdrücklich benannte Lizenz-Dialogroute. Media-Resolver/Next/Resume/Stop/Live/EPG-Playback bleiben geschützt. Vollsuite/ZIP/SHA stehen im folgenden Lieferbericht.

**Rest:** echte Android-Poster-/Logoabdeckung, 500 Titel, Neustart/Offline, Mehrportal und reale Speicher-/Dateisystemeigenschaften prüfen. Fehlende oder ungültige Providerbilder werden nicht erfunden. #41/#90 nicht ohne Geräteabnahme schließen; #69 nicht als Datenbankreparatur abgeschlossen markieren. [Android-Checkboxen](ANDROID_TEST_02920_DE.md). **Autoplay #85 ist nicht enthalten**, siehe [separate technische Vorbereitung](AUTOPLAY_VORBEREITUNG_NACH_TEST46_DE.md). Kein Merge/Release/OTA, kein produktiver Index geändert.

## Gelieferter Prüfstand

**709 Tests PASS in 88,278 s**, 0 Fehler/Fehlschläge, keine unbehandelten Worker-Ausnahmen; **27 neue Tests**. [Vollständiges Protokoll](TESTLOG_02920.txt) · [Prüfbericht](TESTERGEBNISSE_02920.json). ZIP: 147 Dateien / 449728 Bytes, CRC/Pfade/Quellbytegleichheit und unabhängig reproduzierbarer Neuaufbau PASS. Python-3.11-Grammatik für 89 Dateien PASS (kein 3.11-Laufzeittest). Geschützte Playback-/Live-/EPG-Dateien, Service, Medien-XML, Lizenz/Herkunft und alte ZIPs bytegleich; 35 fremde WIP-Dateien unverändert. Android .20 **NOT_TESTED**.

SHA256: `970323bb740ba74dcb03e7e4fe255e77b586f8cb748ea3f9a26ade2681f79e89`.
