# XCMate 0.1.29.43 – vollständiger Host-Testbericht

Stand 27.10.2026. Main-Basis `451f4cf0995cc09ada4b9eb4090906320d36a9fb`, Quell-/Testcommit `c022d8f` (nachfolgender Liefercommit enthält ausschließlich Paket und Berichte). Neues kumulatives Draft, kein Main-Merge/Release. **Alle .43-Androidgates NOT_TESTED.**

## Vollständiges Ergebnis

**1.582 Tests PASS in 239.216 Sekunden**, 0 FAIL, 0 ERROR, 0 SKIP. Alle **1.514 alten Testmethoden** bleiben erhalten und laufen tatsächlich mit; **68 neue Methoden**. Kein gezielter Test wird zur Gesamtsumme addiert. Vollständiger synthetischer Log: [TESTLOG_02943.txt](TESTLOG_02943.txt); maschinenlesbar [TESTERGEBNISSE_02943.json](TESTERGEBNISSE_02943.json), neue Methoden [NEUE_TESTS_02943.json](NEUE_TESTS_02943.json).

- Neue Tests: 10 Mini-Rendering, 6 Katalog-/Suchmetadaten, 16 persistente manuelle Bild-/Metadatenentscheidungen, 14 Dialog/Owner/IR/Cancel, 18 HTTP/Quellen/Fallback, 4 umfassende Bestandsschutzproben.
- Bestehende Native-Stop-/Live-Exit-, VOD/Serie/Resume/Autoplay-, EPG-/Handoff-, Rock/Rocky-/Tab-/Paging-, Genre-, Widget- und Artworktests laufen unverändert in der Gesamtsuite, abgesehen von exakt autorisierten Versions-/Menüerwartungen und expliziten Quellvergleichshooks.
- Große echte Hostfixtures: XMLTV 160.005 geparst/160.003 gespeichert; lokaler HTTP-Katalog >80 MiB/200.000 Titel, M3U 20.005 Einträge/5.002 aktiv; bestehende lokale USB-/SMB-/Migrationsmodelle ebenfalls erhalten. **Keine dieser Proben greift auf Box A oder B zu.** Keine neuen echten Speicher-/Lösch-/Netzlaufwerktests auf Geräten.
- DE/EN PO jeweils **986 Kontexte PASS**, 92 Navigationstexturen samt Provenienz PASS, compileall/AST PASS. Unveränderte Vendor-SMB-Docstring-Escape-SyntaxWarning bleibt dokumentiert, kein neuer Syntaxfehler.
- Alle **391 vorhandenen Add-on-Quelldateien** sind über SHA256 geschützt: 15 bestehende Textdateien haben explizit überprüfbare .43-Änderungsblöcke; die anderen 376 sind bytegleich. Acht neue Paketdateien ergeben **399** Dateien. Die vier kritischen Live-Exitdateien, Originalicon und eingefrorene Medien-/Such-XML sind bytegleich. Default `live_exit_fullscreen42=false`; vorhandenes Box-B-EIN wird nicht überschrieben. Keine Profilmigration.
- 62 Dateien anderer lokaler Entwicklungsstände sind SHA256-identisch geblieben. [Schutzbericht](SCHUTZPRUEFUNG_02943.json). Keine Fremdskin-/Keymapänderung, kein Zugriff/Installieren auf einer Androidbox.

## Paket

`plugin.video.xtreammate-0.1.29.43.zip`: **2.681.507 Bytes**, **399 reguläre Dateien**.

SHA256: `cc4d955fd4bf58ac8dee3d1924459921327ed034d0adb46a4303329aa6c6a117`

CRC, eindeutige Mitglieder, sichere relative Pfade, keine Symlinks, vollständiger Quellbyteabgleich und Python-AST PASS. Keine Profile, Portaldateien, Datenbanken, Rohlogs, Schlüssel oder kompilierten Hostdateien enthalten. [Dateikatalog](DATEIKATALOG_02943.json). Ein unabhängiger deterministischer Nachbau aller ZIP-Mitglieder erzeugt exakt dieselben Bytes. .42-Archiv, Produktionsindizes und Publish-Workflow wurden nicht verändert.

Der GitHub-PR-CI-Lauf baut das Paket erneut, führt die gesamte Suite aus und liefert ein Review-Artefakt. Der abschließende PR-Bericht enthält Run-/Artefaktlink und den Abgleich des heruntergeladenen Artefakts mit diesem ZIP/SHA. Im Pull-Request-Ereignis ist der Produktions-Publish-Schritt ausgeschlossen. Keine automatische Geräteinstallation.

## Vorher/Nachher, Fehlergeschichte und Aussagegrenzen

[Mini-Probe](MINI_RENDER_PROBE_02943.json), ausführbar mit `python tools/probe_xcmate_mini_02943.py`: bei 200 gleichen Ticks **9.000→0** Setter, maximale Fokusrahmen **5→1**. Das reproduziert einen Fehler im Reihenfolge-/Repaintvertrag; es beweist weder Android-GPU-Rendering noch native Codecstabilität. Keine neue objektive Player-/Startsenderbeschleunigung behauptet. Die subjektiv schnellere .42 bleibt eine Nutzerbeobachtung.

Bestehende Host-Suchmessung im endgültigen Log: 2.905 gescannte Programme, sechs Ergebnisse; kalt erste Namen 5.543 ms/gesamt43.608 ms, warm4.504/16.294 ms. Widgetfixture20.005 Zeilen→24 Einträge18.978 ms. Dies sind isolierte Hostwerte, keine Androidlatenzen und kein belastbarer Vorher/Nachher-Optimierungsnachweis.

Der erste Volltest hatte 1.581 Fälle mit genau einem FAIL: ein zweiter historischer Detailmenütest erwartete fünf Einträge statt der jetzt ausdrücklich beauftragten sechs. Beide alten Menütests erwarten nun sechs; alle bisherigen Aktionen bleiben auf ihren ursprünglichen Indizes. Ein zusätzlicher Test schützt fertig gewordene, noch nicht vom Owner konsumierte Ergebnisse vor einem schnellen Quellenwechsel. Der endgültige Gesamtlauf oben enthält sämtliche Korrekturen. In den isolierten neuen Tests wurden außerdem ein Testaufbau für fehlendes Pillow und ein ungültiger leerer Importfixture korrigiert; keine Produktionsfehler als PASS umgedeutet, keine Assertion entfernt/Tests übersprungen.

Netzwerkproben verwenden kontrollierte lokale HTTP-/SMB-Server und gemockte offizielle APIs. Reale Provider-/TMDb-/Commons-Erreichbarkeit, privater Token, Geräte-Pillow/ARM32, IR und BINGIE-Grafik sind **NOT_TESTED**. Der optionale APIschalter und Fallback sind AUS. Fehlerhafte/vorhandene Provider-URL wird nicht blind durch TMDb ersetzt; explizite Quellenwahl bleibt verfügbar. Native RK3528-MediaCodec-/AudioTrack-Rückkehr wird durch Hosttests nicht bewiesen. Private Kodi-Rohlogs wurden nicht veröffentlicht.

## Reproduzieren

In einem isolierten Checkout/Scratch mit Python3.12, Pillow>=11,<13 und impacket0.13.0: die vorhandenen Bootstrap-/Upgrade-/012-/015-Skripte, `tools/build_repository.py`, `tools/validate_kodi_po.py`, `tools/build_xcmate_nav_icons.py --check`, `python -m compileall -q src` und `python -m unittest discover -s tests -v` ausführen. Die vorhandenen HTTP-/SMB-Tests benötigen lokalen Socketzugang. Der Builder ändert Archiv/Repositoryindizes; deshalb nicht in ungesicherten fremden WIP-Ständen ausführen. Das fertige .43-Testpaket liegt im PR ohne Änderung der Produktionsindizes.

## Offene Abnahmen

[Ursachen/Dateien/Grenzen](URSACHENANALYSE_02943_DE.md), [Issue-Matrix](ISSUE_MATRIX_02943_DE.md), [Gesamtabnahme Box B](ANDROID_ABNAHME_02943_DE.md). #151/#111/#108 bleiben ausdrücklich PARTIAL/FOLLOW_UP; Fremdskin #206/#207 BLOCKED/PARTIAL; #98/#161/#64, Storage/Downloads/Aufnahmen DEFERRED. Kein Issue schließen. Historischer .42-Einzel-PASS mit EIN bleibt erhalten, alle .43-Gates neu NOT_TESTED.

Nutzer prüft den Draft und erteilt ausdrücklich Mergefreigabe. **Erst nach diesem Merge folgt die vollständige Android-Abnahme auf Box B.** Kein eigenmächtiger Merge oder Release, kein Eingriff auf Box A.
