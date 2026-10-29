# XCMate .54 – vollständiger Host-/Regressionstestbericht

Basis main .53 `e8d14039fd989bd952c8fdf36cdccb8c966da434`, Quell-/Testcommit `ed6cb5a978970ff5e4274b43d735f35a13593096`, Branch `fix/xcmate-02954-wizard-phases`. Nutzerauftrag vom 29.10.2026, #263, #255, #262, #261, #259, #249; Installations-Popup-Nachtrag berücksichtigt.

## Ergebnis

**2.294 Tests PASS in 313.728 s; 0 Fehler, 0 Failures, 0 Skips.** Alle 2.240 vorherigen Testmethoden erhalten und ausgeführt, 54 neue. Vollständiger synthetischer Log: `TESTLOG_02954.txt`; neue Namen: `NEUE_TESTS_02954.json`; maschinenlesbare Werte/Prüfsummen: `TESTERGEBNISSE_02954.json`.

Der Abschluss stammt aus sauberem git archive des geprüften Quellcommits. Regulärer Bootstrap und alle drei Upgrade-Schritte, kompletter Paket-/Repository-Build, Sprachdateien de/en je 1.125 Kontexte, 92 Navigationstexturen samt Herkunft/Lizenz und Python-compileall bestanden. Vorhandene Hostabhängigkeiten: Pillow, impacket 0.13.0, simpleeval 0.9.13. Alte reale lokale HTTP-/SMB-/Socket-, SQLite-, Großkatalog-, Player-/GUI-/Widget- und Autoplayprüfungen liefen mit.

Erster Gesamtlauf am vorherigen Quellstand: 2.288 Methoden ausgeführt, ein Fehler in einem alten vierargumentigen Parser-Testadapter durch das neue optionale Fortschrittskeyword. Der Importer verwendet bei deaktiviertem Progress wieder exakt den bisherigen Aufruf; der alte Dubletten-/Atomizitätstest bleibt unverändert. Danach Übernahme eigener .53-Atomheads und gezielte Crashgeneration-Recovery ergänzt. 69 gezielte Prüfungen bestanden vor dem ersten Abschlussstand; weitere Recovery-/Legacy-/Zweiquellenfälle sind im hier dokumentierten finalen Gesamtlauf enthalten. Keine weggefallenen Testmethoden und keine neuen Skips.

Vier beabsichtigte historische Vertragsänderungen sind explizit nachgeführt: per-Request statt 25-s-Gesamtbudget, keine automatische 35-s-GUI-Schließung aktiver Jobs, lokaler Changelog-Fallbacktest nun mit zukünftiger .55 statt der neu kuratierten .54, sowie historische Scopeprüfung vor Rohhashvergleich normalisiert exakt die gehashten .54-Deltas. Aktuelle Tests prüfen die neuen Laufzeit-/Sicherheitsbedingungen direkt. Versionsprüfungen auf .54 aktualisiert. Kein pauschales Ausnehmen geänderter Quellen.

Bekannte unveränderte Warnungen aus vendortem SMBProtocol (Escape-Sequenz) und simpleeval (alte AST-Aliase). Kein neuer Laufzeitfehler im Abschlusslog. Keine privaten Kodi-Rohlogs, echten Zugangsdaten oder Geräteänderungen verwendet.

## 54 neue Prüfungen

| Bereich | Methoden | Tatsächlicher Nachweis |
|---|---:|---|
| Katalog/Legacy | 14 | 45 aus 883 Gruppen, 38 vollständig vor Abbruch in 39; Retry nur 39–45, echter inode bleibt, Save vor EPG/idempotente Portal-ID, Ab-/Anwahl, Inhalts-/Namens-/Altersinvalidierung, Restart und sichere Secret-Reentry, SQLite-Fehler, echte leere vs ungültige Antworten, expliziter PARTIAL-Versuch, alte EPG-Datei blockiert Save nicht und bleibt erhalten, eigene .53-Heads übernehmen, fremde/unbewiesene nicht |
| EPG-Quellen | 19 | zwei unabhängige Quellen, bestehendes nutzbares Portal, Source 1 erhalten bei Cancel/Fehler in 2, neuer Reader/Retry überspringt verifizierte 1, Hash-/Fingerprintänderung, gleiche Lease wie Service, Backup-Gate, private Belege, Schedulerkonkurrenz unterbunden, kaputter Beleg, echte Byte-/Parse-/Storecallbacks, Read-Cancel, nicht veröffentlichtes Portal blockiert, Provider-Fehler lässt externe Quellen zu, Belegfehler nach Publish ohne Duplikate/Portalverlust, Manager-Resume, VFS-zero-read-Abwehr, nur eigene Crashgeneration bereinigen, Crash vor erster Tabelle |
| Wizard-Owner/Phasen | 12 | echter Auth-Erfolg und automatische Kategorien, verständlicher Fehler und erhaltene Eingaben/Buttons, separater Katalog-Save und EPG-Cancel mit Portal, ohne EPG direkt nutzbar, aktiver 25-min-Job ohne Gesamt-/Idle-Abbruch und manuell abbrechbar, Requestbudgets, neue RAM-Passwörter sichtbar/verdeckbar/editierbar, gespeichertes Passwort nie als Default, Neustart ohne ungeschützte Secretdatei, disjunkte UI-Bereiche, vorhandenes Portal statt Login bei EPG-Restart, DNS/TLS/HTTP/Auth/Timeout ohne Exceptiontext |
| Installation/Fanart/Startschutz | 7 | frische .54-Installation und .53-Update mit Installationserfolg/Version/Änderungen, einmal über zwei Neustarts, sichere Zurückstellung, Englisch/Passwortgrenze, gleicher Lightweight-Asset und Original-Iconbytes, kein falsches READY ohne reale Programme, tatsächliche Ownership über zwei Stunden |
| Bestandsschutz | 2 | sämtliche 590 alten Quelldateien und 2.240 alten Methoden mit exakten gehashten Deltas und erhaltenen Skipbedingungen |

Die Zweiquellen-Langlaufprüfung verarbeitet tatsächlich zwei XMLTV-Dokumente mit je 6.000 Einträgen, prüft >5.000 persistierte Source-Rows pro Quelle und lässt eine ausschließlich beim echten Lesen fortschreitende virtuelle Uhr je Quelle über fünf Minuten laufen. Ein weiterer SAX-Fall und der native WorkWindow-Pump überschreiten virtuell zwanzig Minuten. **Keine fünf-/zwanzigminütige reale Android-Abnahme und keine künstlichen Heartbeats.** Die großen bestehenden 160.005-Programme-/95-MiB-, Katalog- und 20.000-Bildtests ergänzen Ressourcen-/Streamingregressionen.

Die eindeutige P0-Reproduktion vor/nach ergibt sich aus denselben realen API-Pfaden: alter Wizard publizierte erst nach combined scan; jetzt bietet das tatsächliche SetupWindow nach geprüftem Katalog bereits Save und hält das Portal nach EPG-Cancel. Vorheriger Scan-Neustart entfernte Arbeitsdateien; jetzt bestätigen SQLite-Katalogcounts, Generation/Digest, inode und gezählte Anbieteraufrufe 38 übersprungene Gruppen. Quellen-2-Retry bestätigt gezählt nur einen erneuten Aufruf für Quelle 2, nach weiterhin erforderlicher normaler Backup-Autorisierung.

## Paket und Schutz

**570/590 alte Quellen byteidentisch**, 20 einzeln gehashte Deltas, sechs additive Module; alle bisherigen Quellen vorhanden. Player/.42, Autoplay/Resume, Portalverwaltung, Core-Artwork, Originalgrafiken, BINGIE-Writer und Widgetbindung bleiben byteidentisch. Nur eigene Wizard-XML und Add-on-Metadaten ändern ihre Darstellung. Fremde Skin-/Keymapdateien nicht geändert; 62 fremde WIP-Dateien erneut bytegleich. Box A/B nicht bedient.

ZIP: **596 Dateien / 3140773 Bytes**. CRC, sichere eindeutige Pfade, exakte Quellbytes und Python-AST PASS. Unabhängig deterministisch rekonstruiert: bytegleich. Keine Profile, DBs, Logs, Tests oder Bytecode im Installationspaket. SHA256:

`6616abc7ee28479a722ae8b98ffcff70ab8a050c965fa6781bffbc49a4981bf5`

Liefercommit ergänzt nur Dokumentation und ZIP zum identischen geprüften Quell-/Teststand. GitHub-CI am Lieferhead wird mit Run-/Joblink, 2.294 Tests, tatsächlichem Ergebnis und identischer Paket-SHA im Draft-PR nachgewiesen. Produktiver Veröffentlichungsschritt muss dort übersprungen sein. Kein Merge/Release.

## Offene Gates

24 Box-B-Estuary-Prüfungen **NOT_TESTED**, 0 Android-PASS (`ANDROID_ABNAHME_02954_BOX_B_DE.md`). Box A bleibt unangetastet. Der native Startcrash aus #249/#259 ist **BLOCKED_LOG_EVIDENCE**, keine Ursache oder Reparatur behauptet. Reale Feedabdeckung/Langläufe, ARM32-Verhalten, native Passwortdialoge/Fokus und Fanart-Texturecache offen. Genehmigte echte Slideshowbilder fehlen: **BLOCKED_APPROVED_ASSETS**, Folgeauftrag separat dokumentiert.

Bewusste Grenzen: neuer Kodi/Python-Interpreter kann nur Passwort erneut verlangen; native DNS-Aufrufe sind nicht sicher zwangsweise abbrechbar, Lease bleibt bis Cleanup bestehen; Resume eines bereits befüllten EPG kann eine normale verifizierte Sicherung erfordern; alte .53-EPG-Arbeitsarchive werden erhalten, jedoch ohne gültigen .54-Quellenbeleg nicht als fertiger aktueller Import übersprungen. Keine Userdaten-/Cachelöschung als Reparatur.
