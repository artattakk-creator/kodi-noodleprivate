# XCMate .53 – Host- und Regressionstestbericht

Basis .52 auf `main`: `e17c2b2311481fa83f6f9f8ee560837eb369ce6e`. Geprüfter Quellcommit `0be8e076cb9409ba3bdd12d2462a90a2c67eeb46`. Branch `feat/xcmate-02953-epg-wizard`; Master #259 und Nutzer-Nachtrag zum Kodi-Update-Popup.

## Ergebnis

**2.240 Tests PASS in 314.586 s; 0 Fehler, 0 Failures, 0 Skips.** Alle 2.168 bisherigen Methoden bleiben erhalten und wurden ausgeführt; 72 neue. Vollständiger synthetischer Hostlog: `TESTLOG_02953.txt`; alle neuen Methoden: `NEUE_TESTS_02953.json`; Prüfsummen/Ergebnisse: `TESTERGEBNISSE_02953.json`.

Abschlusslauf aus einem sauberen `git archive` des Quellcommits: regulärer Bootstrap, alle drei Upgrade-Schritte, Paket-/Repository-Build, Sprachvalidierung de/en je 1.123 Kontexte, 92 Navigationstexturen einschließlich Lizenz, Python-compileall und vollständige unittest-Suite. Vorhandene Hostabhängigkeiten: Pillow, impacket 0.13.0, simpleeval 0.9.13. Reale lokale HTTP-/Socket-/SMB-Testserver, SQLite und echte Worker/Owner-Routinen werden mitgeprüft; dies emuliert keine Android-GUI oder Decoder.

Der erste vollständige Integrationslauf fand vier Vertragsabweichungen: drei historische Tests erwarteten den alten 12-h-Default; der neue EPG-Manager hatte normale statt bebilderter nativer Menüauswahl. EPG-Auswahl auf den vorhandenen Icon-Helper umgestellt, die sechs neuen neutralen Wizard-Dialoge explizit erfasst und den früheren dorthin verschobenen Picker berücksichtigt. Die drei historischen Settingvergleiche normalisieren ausschließlich exakt gehashte .53-Deltas; der neue Test prüft gleichzeitig das tatsächliche XML-Default 24 und erhaltene explizite Werte 6/12/36/48. 57 gezielte Integrationsprüfungen bestanden vor dem hier dokumentierten erneuten Gesamtabschluss. Keine Tests entfernt oder zusätzliche Skips eingeführt.

Frühere gezielte Entwicklungsbefunde betrafen Teststubs, das gewollte dynamische .51-WorkWindow-Testadapterverhalten und eine Null-Byte-Leseanforderung im neuen gzip-Wrapper; letzteres korrigiert und mit gültigem sowie abgeschnittenem gzip nachgeprüft. Bekannte unveränderte Warnungen: alte Escape-Sequenz im vendorten SMBProtocol und Python-AST-Aliase von simpleeval. Kein neuer Laufzeitfehler im Abschlusslog. Keine privaten Kodi-Logs oder echten Zugangsdaten verwendet.

## Neue Nachweise

| Gruppe | Neue Methoden | Prüfbereich |
|---|---:|---|
| EPG-Manager / Varianten | 16 | 24-h-XML-Default, explizite Intervalle, LastGood-Alter, quellenselektiver Retry/Backoff/Versuchsgrenze, Backup-Sperre, echte Read-only-Zahlen/Horizonte, 16-Berichte-Rotation, lesbare Deltas, Name-Redaktion, realer Import-Observer, Owner-Worker-UI, WELT/Comedy SD/HD/+1/Land |
| Offenes Raster | 7 | kurzer OK-Kontext, echtes ursprüngliches Raster bei offenem Panel, Quellvergleich ohne Writes, vollständiges Cancel, ein gezielter Save, Suche/Blättern über 1.000 Kanäle, späte Ergebnisse nach Close |
| Kalte Kandidaten | 10 | RAM-Katalog nach Name/ID, bislang unimportierte Programme im Raster, Bytevergleich aller Dateien vor/nach Preview/Cancel, expliziter Save und neuer Offline-Reader, Quellkollision, Schreibfehler ohne Mapping, gültiges/kaputtes gzip, Cancel, Bytes/512-Ereignisse/45-s-Deadline, DTD-Abwehr |
| Wizard | 27 | private nichtgeheime Wiederaufnahme, Fehlerspeicherung, Original-UUID/Staging/Gruppen, gültige Scan-Wiederverwendung, kaputter/alter Scan, Save-Retry, Back/Tabs/Summary, bestätigtes Discard, Netzwerkfehler, geheime URL-Redaktion, Abschluss/Crash, fremder Pfad/Anbieter, nur Passwort nach Restart, sichtbare/neutrale Neueingabe, gespeichertes Passwort unsichtbar, Lease/Cancel ohne GUI-Workerzugriff, korruptes Intent und erstbestätigte Eingabe |
| Wizard-Quellbeweis | 1 | .52-Quellalias nach endgültiger neuer Portalveröffentlichung erhalten, vorhandene andere Beweise bleiben |
| Widgets | 4 | volle 88-Sender-Startgruppe, identische gespeicherte Quelle in Home/Grid/Mini/Infobar-Modell, drei direkte Aktionen, byteidentische .50-Skinwriter/Reload und .52-Pixel-/Player-Kerne |
| Update-Popup | 5 | konkrete .53-Änderungen de/en, einmal über zwei Neustarts, spätere lokale Changelogversion, unbekannte Version, Player-gesteuerte Verschiebung |
| Bestandsschutz | 2 | alle 580 alten Quellen und 2.168 Methoden ohne zusätzliche Skip-Ausnahme |

Die bisherigen EPG52-Tests führen −7/+20, LastGood, source-qualified Quellenunion, Beschreibungs-/Bildherkunft und Sommer-/Winterzeit weiterhin aus. Die bisherigen Serien-/Widget-/Skincompiler-, Pixel-, Player-/Autoplay- und Wizard51-Großlistenprüfungen laufen ebenfalls unverändert beziehungsweise mit genau dokumentierten .53-Vertragsanpassungen.

## Bestandsschutz / Paket

**561 von 580 alten Quelldateien byteidentisch**, 19 exakt gehashte Deltas, 10 additive Dateien. Alle alten Dateien vorhanden. Keine Änderung externer BINGIE-Dateien, Keymaps, Original-Icon, Player/.42-Kompatibilitätsmodus, Medien-/Autoplay-Kernen oder bestehenden Artworkdateien. Die Änderungen an eigenen XML-Dialogen sind im Dateikatalog einzeln erfasst. 62 fremde WIP-Dateien erneut byteidentisch. Box A/B unverändert.

ZIP: **590 Dateien, 3126953 Bytes**. CRC, eindeutige sichere Pfade, jeder Quellbyte und Python-AST PASS; unabhängig deterministisch rekonstruiert, byteidentisch. Keine Profile, Datenbanken, Logs oder Tests im Installationspaket.

SHA256: `f2db23aa383212ba42a26c0022d49a41b22d029d868fbf93bacd9a6fc97bcd37`.

Der Liefercommit ergänzt Berichte und geprüftes ZIP zu identischem getesteten Quell-/Teststand. GitHub-CI am finalen Draft-PR-Head wird im PR mit Run-/Joblink, Testanzahl, Artefakt und übereinstimmender ZIP-SHA dokumentiert. Der produktive Publish-Schritt muss dort übersprungen sein. Keine eigene Merge-/Releaseaktion.

## Offene Abnahme

**36 Androidtests pro Box, 72 NOT_TESTED, 0 Android-PASS.** Siehe `ANDROID_ABNAHME_02953_DE.md`. Öffentliche echte Feedabdeckung ist durch die Workspace-Netzwerkpolicy BLOCKED_NETWORK, nicht als leer oder defekt gewertet. Eine neu nötige tatsächliche BINGIE-Skinaktivierung bleibt BLOCKED_SKIN_APPROVAL. Die bereits vorhandene freigegebene Integration bleibt erhalten. Live-Darstellung, Fernbedienung, private Quellenabdeckung, ARM32-Ressourcen und sichere Android-Dateimodi müssen real geprüft werden. Kein Vorgang auf Box A/B ausgeführt.
