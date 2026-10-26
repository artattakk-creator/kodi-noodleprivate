# XCMate 0.1.29.40 – kumulativer Testbericht

**1.435 Hosttests PASS**, 0 FAIL, 0 ERROR, 0 SKIP in **229,272 s**. Alle **1.403** bisherigen Methoden aus main .39 erhalten, **32 neue Tests**. **Android vollständig NOT_TESTED**, keine Geräte verändert. Kein Merge/Release.

Getesteter Quellstand: `0ab01d9e89dbf4114196fe1b8e048de975cb41d1`; Basis `main` .39 `25a640869e3b4e178945ba4f549ad7e269dd292f`, gemergter PR #198. Nachfolgende Lieferdokumente ändern keine Paketquellen. Aktueller grüner GitHub-CI-Lauf und heruntergeladener Artefaktabgleich werden vor Übergabe im Draft-PR verlinkt.

## Installationspaket

- [plugin.video.xtreammate-0.1.29.40.zip](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.40.zip): **386 Dateien / 2.648.239 Bytes**.
- [SHA256-Datei](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.40.zip.sha256)
- SHA256: `ff27c6bcaf203578b7542ce0b7bfb1422e29c41a6fa950539acbe1bc551d8d03`
- CRC, eindeutige sichere Pfade, keine Symlinks, keine Profil-/Test-/DB-/Logdateien im Add-on: PASS.
- Jede Paketdatei bytegleich zur Quelle; Python-AST validiert; unabhängiger deterministischer ZIP-Neubau bytegleich: PASS.
- Produktionsindex und .39-ZIP unverändert. Paket ausschließlich Branch-/Draft-Testkandidat, kein regulär veröffentlichtes Repo-Update.

## Reproduzierbarer Fehlernachweis

Die zwei neuen P0-Replays `test_twenty_decoder_start_fullscreen_flaps_never_authorize_a_stop` und `test_owner_view_poll_during_decoder_start_does_not_stop_or_request_return` wurden zusätzlich auf einem separaten unveränderten Git-Archiv von main .39 ausgeführt: **beide FAIL**, weil ohne Benutzeraktion ein Stop angefordert wird. Auf .40 **beide PASS**, im vollständigen grünen Lauf enthalten. Konkrete Aufrufpfade und Zeilen: [Ursachenanalyse](URSACHENANALYSE_02940_DE.md).

Das beweist einen Codefehler und seine Regression, aber nicht rückwirkend die individuelle Ursache aller neun Android-Ereignisse ohne alte Reasoncodes. Der native Live-Deadlock/MediaCodec-Root-Cause bleibt offen; Stop-Quarantäne/Workerfreigabe sind im Hostmodell nachgewiesen, keine behauptete Android-Heilung.

## Automatisierte Nachweise

| Prüfung | Ergebnis / Reichweite |
|---|---|
| Vollständige kumulative Suite | 1.435 PASS / 229,272 s, Python3.12; keine ausgelassenen alten Testmethoden |
| 16 neue P0-Tests | Kurzzeitige Fullscreenflaps; Ownerpoll/Init; expliziter Stop/Cancel; Native-Release-Warten; fremde Modals/Player; blockierter Stop mit 20 Polls und Interpreterwechsel; Resolver-/Decoderfehler; Suchdialog-Wiederanzeige; neue Starts während Stop gesperrt; Legacy-In-flight-Quarantäne |
| 9 neue Suchtests | 20 Reiterzyklen mit Pending; finale Null korrekt; gleiche Liste ohne Reset; EPG-Metadaten in bestehenden Items; getrennte zweite Seiten/Fokus; stale Query und Portal; begrenzte 24er-Seitenhaltung; Medienpublikation vor EPG-Prepare |
| 7 neue UI-Tests | Zweizeilige native TextBox bei720/1080; NOW/Fokus getrennt; 20 Clear-Zyklen; erstes-OK-OSD-Recovery; echte lokale Guide-Worker-Wartephase bei20 IR-Wechseln; strukturierte lokale Technikicons/unknown; VOD-Recovery während Fullscreenflagverlust |
| Bestehende Funktionen | Alle alten Resume/Gesehen/Autoplay/ManualNext/Staffel-/Such-/EPG-/Portal-/Wizard-/Artwork-/Sicherheits-/Download-Hosttests enthalten; nur temporäre synthetische Profile/Server |
| Sprache | DE/EN je **944** gültige PO-Kontexte |
| Icons/API | **92** gepinnte lokale MIT-Tabler-PNGs/Provenienz PASS. ControlTextBox-Signatur gegen gepinnten Kodi21.3-Header bestätigt und im strengen GUI-Vertrag ergänzt |
| Python | compileall und Paket-AST PASS. Unveränderte SMBProtocol-Vendor-Docstring-SyntaxWarning unter Python3.12, kein Kompilierungsfehler |

[Alle 32 neuen Methoden](NEUE_TESTS_02940.json), [vollständiges grünes Hostlog](TESTLOG_02940.txt), [maschinenlesbare Ergebnisse](TESTERGEBNISSE_02940.json), [386 Datei-Hashes](DATEIKATALOG_02940.json).

Vor dem endgültigen Lauf bestanden 99 gezielte neue/angrenzende Player-, API-, OSD-, Such-, Autoplay- und Next-Tests. Der erste Gesamtlauf fand einen fehlenden TextBox-Eintrag im bisherigen API-Testmodell; nach Abgleich mit dem echten Header ergänzt. Historische .40-spezifisch ersetzte Erwartungen: bloßer Fensterwechsel/onInit stoppt nicht mehr, expliziter Back/Home weiterhin; neuer Mini-Zeilenvertrag. Keine Testmethoden entfernt, alte Freeze-Fixtures nicht ersetzt; exakte .40-Hunks komponieren vor den alten Verträgen.

## Große echte Hostfixtures dieses Laufs

| Fixture | Messung |
|---|---|
| XMLTV | 160.005 gelesen /160.003 gespeichert; 95.571.948 XML-Bytes, 199.876.608 SQLite-Bytes, 12,554 s |
| Filme | 200.005 Titel, 109.380.521 lokale HTTP-Bytes, 309.522.432 SQLite-Bytes, 27,668 s |
| Serien | 200.005 Titel, 109.380.521 HTTP-Bytes, 621.727.744 kumulative SQLite-Bytes, 27,413 s |
| Katalog Peak-RSS | 59.124 KiB Host; kein ARM32-Gerätespeicherwert |
| Bestehende 2.905-Sender-/456-Alias-Fixture | Kalt erste Namensdaten4,246 ms / Abschluss36,513 ms; warm4,351 /22,974 ms; sechs Endtreffer. **Datenpublikation ohne Kodi-GUI/Android** |

Die neue Stufenreihenfolge „Namen → Medienseiten → EPG-Prepare“ wird als Reihenfolge getestet; keine erfundenen Android-Vorher/Nachher-Zeiten. .39-End-to-End Mini16,2 s/Info33,8 s und EPG39 s bleiben reale Gerätevergleichswerte für die nächste Prüfung.

## Bestandsschutz

[Schutznachweis](SCHUTZPRUEFUNG_02940.json): **364 unveränderte Add-on-Quelldateien**, alle1.403 alten Methoden vorhanden. 163 historische UI-Vertragsdateien, davon162 bytegleich zu .39; ausschließlich `media_window.py` innerhalb dieses Vertrags mit einzeln erfassten .40-Hunks. Sechs Suchmaskencontrols und Original-Icon/98 Grafiken bytegleich. Portal-/EPG-/Resume-/Autoplay-/Decoder-/Keymap-/Artwork-Modus-Module unverändert. Kein DB-Schema oder Journal ergänzt. 62 fremde lokale WIP-Dateien unverändert. Die neuen Window-Properties sind flüchtige eigene Sessionzustände, keine Profilmigration.

Box A vollständig ausgenommen. Box B Dynamisch, keine zusätzlichen Speicher-/USB-/SMB-/SD-/Migrations-/Löschtests und keine automatischen Installationen. Bestehende SMB-/Migrations-Hosttests verwenden ausschließlich temporäre Fixtures, niemals Nutzerlaufwerke. Private Rohlogs weder geöffnet noch veröffentlicht; grünes Testlog auf Credential-/URL-Leaks geprüft.

## Reproduktion

Separater frischer PR-Checkout, Python3.12, Pillow und impacket0.13.0:

```sh
python tools/build_repository.py
python tools/validate_kodi_po.py
python tools/build_xcmate_nav_icons.py --check
python -m compileall -q src
for f in tests/test_addon.py tests/test_site.py tests/test_providers.py; do
  sed -i "s@'..', 'plugin.video.noodleprivate'@'..', 'src', 'plugin.video.noodleprivate'@g" "$f"
done
python -m unittest discover -s tests -v
python tools/verify_xcmate_02940_protection.py --output /tmp/xcmate40-protection.json
```

Die Schutzprüfung benötigt das Git-Objekt der dokumentierten Mainbasis. Der Builder erzeugt auch andere Add-on-Archive/Indizes: nur im separaten Checkout ausführen und keine generierten Produktionsdateien veröffentlichen. CI installiert impacket regulär; lokal wurde die vorhandene Version per PYTHONPATH eingebunden. Reale Loopback-HTTP-/SMB-Hostserver benötigen Netzwerkfreigabe der Sandbox.

## Geräteabnahme und offene Issues

[24 Funktionsgates plus80 Checkbox-Wiederholungen](ANDROID_ABNAHME_02940_DE.md), [Status je Box](ANDROID_STATUS_02940.json), [Issue-Matrix für15 offene Tickets](ISSUE_MATRIX_02940_DE.md), [alle Änderungen gegenüber .39](AENDERUNGEN_02940_DE.md).

**#202/#203 bleiben P0-Freigabegates.** Kein neuer Android-PASS, kein Merge/Release, keine Issue-Schließung. Reale native Hängerfreiheit, Rockchip-Decoderverhalten, Kodi-OSD-Trigger, BINGIE-Rollover, tatsächliche Repaint-/Fokus-/Streamfeld-Darstellung und neue End-to-End-Latenzen sind weiterhin NOT_TESTED. Ohne erfolgreiche Film-/Episodenstarts Autoplay-Abnahme BLOCKED.
