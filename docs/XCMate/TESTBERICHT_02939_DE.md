# XCMate 0.1.29.39 – Testbericht und Lieferung

**1.403 Hosttests PASS, 0 FAIL, 0 ERROR, 0 SKIP in 226,498 s.** Alle 1.357 bisherigen Testmethoden erhalten, 46 neue. Android vollständig NOT_TESTED. Kein Gerät verändert, kein Merge/Release.

Basis main .38: `d8a20a2b7887878c3d5192e355b5c642a2bdebd5`, Nutzer-Merge #184. Getesteter Stand: `81cd2d4c9e4d767c7ece9294e0c2b0bbb8240c46`; letzter funktionaler Codecommit `2fc71db`. Nachfolgende Lieferdokumente ändern den Add-on-Code nicht. Aktueller CI-Lauf und heruntergeladener Artefaktabgleich werden im Draft-PR verlinkt, bevor die Lieferung übergeben wird.

## Paket

- [Installierbares Test-ZIP](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.39.zip): **2.643.329 Bytes / 385 Dateien**.
- [SHA256-Datei](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.39.zip.sha256)
- SHA256: `5448d21b2c93761fd7ec2d6293879ea988cc15ed48e5e177c5e2ceed4f91d7f8`
- CRC, keine doppelten/unsicheren Pfade, keine Symlinks, keine Profil-/Log-/DB-/Testdateien im Add-on: PASS.
- Jede Datei bytegleich zur Quelle; Python-AST gültig; unabhängiger deterministischer ZIP-Neubau bytegleich: PASS.
- `DATEIKATALOG_02939.json`: Größe/SHA256 jeder Paketdatei. .38-ZIP und Produktionsindex unverändert.

Dieses Paket ist ein Branch-/CI-Testkandidat und wird nicht als produktives Repository-Update veröffentlicht.

## Hostnachweise

| Prüfung | Ergebnis / praktische Grenze |
|---|---|
| Gesamtsuite | 1.403 PASS / 226,498 s unter Python 3.12.14 |
| Bestehende Regressionen | 1.357 Methoden beibehalten, darunter Resume/Gesehen/Autoplay, Wizard, Gruppen, Suche, EPG und sichere Migration in temporären Profilen |
| Neue lokale EPG-Tests | 8: echte SQLite-Publikationen/Transaktionen, manuelles Mapping, Now-Rollover, Programme/Metadaten konsistent, Widgetgrenze zwölf bei 1.001 Sendern, keine DB-Reparatur oder Provider-I/O |
| Neue Stream-/OSD-Tests | 8: echte Kodi-API-Signaturen im Modell, Metadatenbudget, unbekannte Felder, Owner-/Stop-Races, 20 Standard-OSD-Replays, fremde Dialoge geschützt, größere Controls |
| Neue VOD-Return-Tests | 11: je 20 Grid/Detail/Suche-Returns, 20 Episodenreturns, tatsächliche SearchWindowXMLDialog-Wiederanzeige im Modell, Async-Back, fremde Owner, Fehlerpfad und deduplizierter Start/Abbruch |
| Neue Rail-/Mini-Tests | 5: 20 neue Links-/Rückzyklen, explizites Leeren aller Labels/Bilder/Fokusflächen, getrennte NOW-/Fokusmarkierung, 720p/1080p-Safe-Area |
| Neue Artwork-Kontexttests | 4: 20 Wiederaufbauten je 30/60/120-s-Grenze, endgültiger DNS-Fehler, neue Quelle/neues Fenster ohne alte Freigabe, RAM-Historie begrenzt |
| Neue Suchtests | 6: 2.905 Sender/456 Aliasse, Namen vor EPG/Medien-SQL, laufende Cursor nicht durch Telemetrie zurückgesetzt, Publikationsreuse und echte Zeit-/Mapping-Invalidierung |
| Neue Latenztests | 4: ausstehende Katalogarbeit blockiert native Capture nicht, keine Diagnosedateien im Callback, blockierter Writer hält keinen Inbox-Lock, datensparsame Phasenmarks |
| Sprache/Syntax/Icons | DE/EN je 939 gültige PO-Kontexte; compileall und AST erfolgreich; 92 gepinnte lokale MIT-Tabler-PNGs/Provenienz verifiziert |

Die unveränderte SMBProtocol-Vendor-Datei enthält eine bekannte ungültige Escape-Sequenz im Docstring und erzeugt unter Python3.12 eine SyntaxWarning. Kompilierung/Tests erfolgreich; Vendorcode unverändert. Keine Android-/ARM32-Ausführung behauptet.

Die vollständige Suite fand während der Entwicklung eine echte Manual-Next-Return-Regression; diese wurde behoben und die 19 bisherigen Next-/Staffeltests wieder grün. Historische Erwartungen wurden nur für ausdrücklich beauftragte .39-Verträge angepasst: persistierte Widget-Fixtures, neue Back-/Rail-Kette, asynchroner Diagnostik-Flush, Namen-zuerst-Phase und Streamdatenzeile. Der Backendtest für explizite Resolver-Supersession bleibt erhalten; identische IR-Repeats werden separat dedupliziert. Keine Testmethoden entfernt. Alle neuen Methoden stehen in `NEUE_TESTS_02939.json`.

## Vergleichsmessung der Suche

`tools/benchmark_search_02939.py` führt den tatsächlichen .38-Suchcode aus main und .39 mit derselben synthetischen lokalen Fixture aus: 2.905 Sender, 456 EPG-Aliasse, fünf Namens- und ein echter Programmtreffer. **Host-Datenpublikation, ohne GUI-/Frame-/Android-Messung.**

| Vergleich | .38 | .39 |
|---|---:|---:|
| Cursor bei 20 Short-Cache-Änderungen während laufender Suche | 21 | 1 |
| Vorbereitete Now-Snapshots für zwei Queries | 2 | 1 |
| Kalte erste Namensdaten | 5,081 ms | 4,015 ms |
| Kalter Datenabschluss | 38,168 ms | 37,419 ms |
| Warme erste Namensdaten | 4,019 ms | 4,420 ms |
| Warmer Datenabschluss | 34,136 ms | 15,336 ms |

Der relevante Nachweis ist weniger wiederholte Arbeit; nicht jede einzelne Mikrozeit ist schneller. Diese Zahlen werden nicht mit den Android-24.974-ms-bis-erste-Live-Reihe gleichgesetzt. Im abschließenden Gesamtlauf lagen die .39-Fixturewerte bei 4,510/4,160 ms ersten Namensdaten und 39,489/14,919 ms Gesamtpublikation. Rohwerte und reproduzierbarer Vorher/Nachher-Vergleich: `BENCHMARK_SUCHPERFORMANCE_02939.json`.

Weitere echte große Host-Fixtures dieses Laufs:

| Fixture | Ergebnis |
|---|---|
| XMLTV | 160.005 gelesen / 160.003 gespeichert, 95.571.948 XML-Bytes, 199.876.608 SQLite-Bytes, 12,659 s |
| Filmkatalog | 200.005 Titel, 109.380.521 HTTP-Bytes, 309.522.432 SQLite-Bytes, 25,450 s |
| Serienkatalog | 200.005 Titel, 109.380.521 HTTP-Bytes, 621.727.744 kumulative SQLite-Bytes, 27,511 s |
| Katalog-Prozess Peak-RSS | 58.968 KiB – Host, kein Nachweis des tatsächlichen ARM32-RAM-Verbrauchs |

HTTP und SMB2 sind lokale Testserver mit synthetischen Daten. Bestehende Storage-/Migrations-Hosttests kopieren nur temporäre Fixtures; auf Box B wurden keinerlei Speicherprüfungen durchgeführt.

## Bestandsschutz

`SCHUTZPRUEFUNG_02939.json` und `tools/verify_xcmate_02939_protection.py` belegen:

- 359 unveränderte Add-on-Dateien; alle geänderten bestehenden Module einzeln in der exakten .39-Hookliste und alle neuen Quellen in der Ausnahmeliste erfasst.
- Alle 1.357 bisherigen Testmethoden vorhanden. Originale historische Freeze-Fixtures bleiben erhalten; neue Ausnahmen komponieren davor und können keine beliebigen weiteren Änderungen ausblenden.
- 163 historische UI-Vertragsdateien geprüft, davon 161 bytegleich zu .38. Nur `media_window.py` und `search_results.py` innerhalb dieses Vertrags haben einzeln geprüfte .39-Ausnahmen. Suchmasken-XML und seine sechs Tabs-/Ergebniscontrols byteäquivalent.
- Original-XCMate-Icon und 98 Originalgrafiken unverändert; neue OSD-Skizzen liegen ausschließlich in der Dokumentation.
- Legacy-Artwork-Modus-Gate, Portal-/EPG-Quell-/Guide-Store-/Resume-/Gesehen-/Autoplay-/Decoder-/Keymap-Module bytegleich. Kein neues DB-Schema oder Journal in .39.
- Produktionsindex, .38-Paket und CI-Publish-Bedingung unverändert; 62 fremde lokale WIP-Dateien gegen ihre vorherigen Hashinventare unverändert.

## Reproduktion

In einem frischen separaten Checkout des PRs; Python3.12, Pillow und impacket0.13.0:

```sh
python tools/build_repository.py
python tools/validate_kodi_po.py
python tools/build_xcmate_nav_icons.py --check
python -m compileall -q src
for f in tests/test_addon.py tests/test_site.py tests/test_providers.py; do
  sed -i "s@'..', 'plugin.video.noodleprivate'@'..', 'src', 'plugin.video.noodleprivate'@g" "$f"
done
python -m unittest discover -s tests -v
python tools/verify_xcmate_02939_protection.py --output /tmp/xcmate39-protection.json
python tools/benchmark_search_02939.py --output /tmp/xcmate39-search.json
```

Der Benchmark benötigt das lokale Git-Objekt der dokumentierten .38-Basis. Der Repository-Builder erzeugt Dateien für mehrere Add-ons; ausschließlich im separaten Checkout ausführen und keine generierten Produktionsarchive/-indizes veröffentlichen. Lokal nutzte der Hostlauf die vorhandene impacket-Abhängigkeit über PYTHONPATH; CI installiert dieselbe Version regulär. Der PR-Workflow erzeugt ein eigenes ZIP samt Testlog/Verifikations-JSON. Der echte CI-/Downloadabgleich steht im PR, ohne produktiven Publish.

## Offene Android-Abnahme

[40 Android-Gates](ANDROID_ABNAHME_02939_DE.md), [Status je Box](ANDROID_STATUS_02939.json), [Ursachenanalyse](URSACHENANALYSE_02939_DE.md), [Issue-Matrix](ISSUE_MATRIX_02939_DE.md), [Playerentwürfe A/B](OSD_VARIANTEN_02939_DE.md), [Kodi21-Feldgrenzen](KODI21_STREAMFELDER_02939_DE.md), [Widget-/Opt-in-Vertrag](WIDGET_ADAPTER_02939_DE.md).

**Nicht als fertig abgenommen:** fortlaufendes BINGIE-Home-Rollover, echte native InfoTag-/Fokus-/Return-Darstellung, tatsächliche Streamfeld-Verfügbarkeit, sporadischer OSD-Trigger und physische 19–49-s-Phasen-/MediaCodec-Ursache. Keine Host-CI kann das ersetzen. #98/#161 getrennt; geerbte physische Metadaten-Auslagerung und dauerhaftes ungespeichertes Wizard-Scanresume bleiben offen. Keine Downloads-/Aufnahmenreparatur.

Box A vollständig ausgeschlossen; Box B bleibt Dynamisch ohne weitere Storage-/Migrations-/Löschtests. Keine privaten Kodi-Rohlogs veröffentlicht. Kein Merge, kein produktiver Release, keine automatische Installation oder Issue-Schließung.
