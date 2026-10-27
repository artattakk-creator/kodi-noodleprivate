# XCMate 0.1.29.45 – Host-Testbericht

**1.725 Tests PASS**, 0 Fehler, 0 fehlgeschlagene Tests, 288,134 Sekunden. Darin alle 1.652 bisherigen Testmethoden und 73 neue .45-Methoden. Android vollständig **NOT_TESTED**; kein Gerätezugriff, Main-Merge oder produktiver Release.

Geprüfter Implementierungscommit: `5e31f75ab56c865df0fadec51118c1bbbee9c1e5`, auf bestehendem `freeze/xcmate-02944-box-b-baseline-20261027`, Referenz main `aace7f0f85cea8b9d132b0090563e28c9941bc4a`. Nachfolgende Dokument-/Paketcommits ändern keine Runtime-Quelldatei. Vollständiger Log: [TESTLOG_02945.txt](TESTLOG_02945.txt), maschinenlesbar [TESTERGEBNISSE_02945.json](TESTERGEBNISSE_02945.json).

## Verfahren

Sauberes `git archive` dieses Commits nach isoliertem Scratch-Verzeichnis, pinned Bootstrap und bestehende Upgrades 0.1.1/0.1.2/0.1.5, vollständiger Repository-Build dort, PO-Validierung, Navigationstexturprüfung, Python-Compile und `python -m unittest discover -s tests -v`. Host Python3.12/Pillow, bestehender isolierter Impacket0.13-SMB-Testserver. Loopback-Testserver sind Hostfixtures, keine neuen USB-/SMB-/Speichertests auf Box B. Originales Arbeitsrepository und vorhandene .44-Archive/Indizes werden durch den Build nicht verändert.

| Prüfung | Ergebnis |
|---|---|
| Gesamte Host-Suite | 1.725 / 1.725 PASS, 288,134s |
| Neue Widget-/native Hooktests | 15 Methoden; reale native Providergrenze, Routing, Daten/Revision, LastGood, kein globaler Refresh |
| Optionaler Adapter | 12 Methoden; nur künstlicher Temp-Skin, Version/Pfad/Symlink/Hashes/Abbruch/Restore/Kollisionen |
| Settings/PIN/Optionsaktionen | 18 Methoden; exakt6666, falsche PIN/666/Cancel, Direktaufruf/Reentry, unveränderte Werte/IDs, released Handle |
| Menüicons | 9 Methoden;35 unterschiedliche transparente lokale Glyphen, native ListItems, XML-ID-/Remote-/Hitrect-Erhalt |
| Referenz-Infobar/Previous | 13 Methoden; Layout/Fonts/echte Werte/Readonly-Mapping/Revision/Diffsetter/Bedienung |
| Kumulative Schutzverträge | 6 neue Methoden, sämtliche historischen Verträge weiterhin aktiv |
| PO en_GB/de_DE | Je1.051 Kontexte PASS |
| Gepinnte Navigationstexturen/Lizenz | 92 Texturen PASS |
| Python-Syntax | PASS; bekannte unveränderte SMB-Vendor-Escape-Warnung ohne Fehler |
| Geschützte Fremd-WIP-Dateien | 35 +27 Dateien SHA256 unverändert |
| Android Box A / Box B | Nicht bedient / alle .45-Fälle NOT_TESTED |

Zwischenläufe deckten auch veraltete Testmodelle auf: zehn statt sieben Rubriken, String- statt echter ListItem-Zeilen, alter Infobaraufbau und fehlende bewusste PIN-Autorisierung. Diese Erwartungen wurden für die ausdrücklich angeforderte UI aktualisiert. Keine bisherigen Testmethoden entfernt, keine pauschalen Skips oder Abschaltung des PIN-Schutzes. Eine zunächst untersuchte native Listenbindung wurde nach Abgleich mit Kodi21.3 verworfen und durch tatsächliche Reload-Hooks ersetzt; die endgültigen Tests modellieren diese API-Grenze ausdrücklich.

## Paketprüfung

- Datei: `plugin.video.xtreammate-0.1.29.45.zip`
- Größe: 2,969,898 Bytes, 510 Dateien.
- SHA256: `641b3ed82e4290711e606efaafc42de68c537add77615af4ce50d8204fec5e8a`
- CRC, eindeutige/sichere Pfade, keine Symlinks, vollständige Bytegleichheit ZIP ↔ Runtimequellen, AST sämtlicher Python-Dateien: PASS.
- Unabhängiger zweiter ZIP-Writer mit fixierten Zeitstempeln/Modi und sortierten Einträgen erzeugt exakt dieselben Bytes: PASS.
- Keine privaten Konfigurationen, DB-/Logdateien oder Nutzerdaten im Add-on-ZIP. Keine Änderung produktiver addons.xml/MD5/alten ZIPs. Die Workflow-Publikation darf im Draft nur SKIPPED sein; CI und tatsächliches Actions-Artefakt werden im PR nachgeprüft.

## Host-Messwerte und Grenzen

In derselben vollständigen Suite: 20.005 Widgetdatensätze →24 Ergebnisse mit indexiertem SQLplan, 32,832ms; ältere direkte Widgetfixture2,821ms. Suchfixture2.905Sender: erster kalter Name4,521ms / Gesamt38,169ms, warm erster Name5,310ms / Gesamt16,909ms. Das sind unterschiedliche Hostfixtures und keine Vorher-/Nachher- oder Android-Beschleunigungsgarantie. Großtests speichern160.005EPG-Events aus95,6MBXML und je200.005Film-/Serientitel aus109,4MBHTTP-Testdaten; Details im Log.

Die neue Hintergrundaktualisierung ist nur bei vorhandenem verifiziertem Skin-Reload-Hook automatisch sichtbar. Ohne Hook **BLOCKED_NO_RELOAD_HOOK**; optionaler Adapter braucht eigene Aktion/PIN/Bestätigung und wurde auf keinem Gerät angewandt. Keine Aussage „alle BINGIE-Widgets vollständig abgenommen“. Native Widgetlayout-/Fokusdarstellung und die Bildgleichheit der Infobar sind weiter echte Gerätegates.

## Review-Unterlagen

- [Ursachen, Grenzen und Quellen](URSACHENANALYSE_02945_DE.md)
- [Issue-Matrix](ISSUE_MATRIX_02945_DE.md)
- [Menü-/Iconmatrix](MENU_MATRIX_02945_DE.md)
- [Android-Gesamtabnahme](ANDROID_ABNAHME_02945_DE.md)
- [Neue Testmethoden](NEUE_TESTS_02945.json), [Runtime-Dateikatalog](DATEIKATALOG_02945.json), [Bestandsschutz](SCHUTZPRUEFUNG_02945.json)
- [1080p-Hostvorschau](INFOBAR45_HOST_1080.png), [720p-Hostvorschau](INFOBAR45_HOST_720.png). Testdaten/Hostfonts, keine Android-Screenshots. Das aktuelle Bildmuster ersetzt frühere Mikro-/Schlankheitsvorgaben.

Bis zur echten Box-B-Abnahme bleiben alle Androidgates NOT_TESTED. EPG-Refresh ausschließlich nach verifizierter konsistenter SQLite-Sicherung und ausdrücklicher Einwilligung. Keine automatischen Merges, Releases, Installationen, Resets oder Löschungen.
