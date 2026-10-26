# XCMate 0.1.29.38 – Testbericht und Lieferung

**Host: 1.357 PASS, 0 FAIL, 0 ERROR, 0 SKIP in 198,999 s. Android: NOT_TESTED.** Basis main .37 `e25020c80703d440b0606b6d66559428dfc96cca`. Kein Merge, Release oder Gerätezugriff.

Die 1.298 bestehenden Testmethoden sind erhalten. 59 neue Tests prüfen Autostart, reale SQLite-Historie/Locks, dynamische Cover, Rail/IR/Fokus, Player-Capabilities/Stop, read-only Inventur und freiwillige Bereinigung. `NEUE_TESTS_02938.json` listet jede Methode. Historische Erwartungen wurden nur für ausdrücklich geänderte .38-Verträge angepasst: neue Version/Iconpfade, temporäre Diagnosepause, Vordergrund-Einstieg, Mini-Programmfokus, VOD-Back/async Stop und native Sichtbarkeit. Alte UI-Freeze-Fixtures bleiben erhalten; die .38-Ausnahmen sind einzeln und exakt in `xcmate_02938_reviewed_hooks.json` dokumentiert.

## Geprüftes Paket

- [Installierbares Test-ZIP](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.38.zip): **2.631.990 Bytes, 380 Dateien**.
- [SHA256-Datei](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.38.zip.sha256)
- SHA256: `8bc6af0ba8195f0ab452d3c9162392c3bf92c0ad5e4abd93af65a98de42ca238`
- CRC, eindeutige/sichere Pfade, keine Symlinks, keine Profile/Logs/DBs/Tests im Add-on, jede Datei bytegleich zur Quelle, Python-AST und byteidentischer reproduzierbarer Neubau: PASS.
- `DATEIKATALOG_02938.json` enthält Größen und SHA256 aller 380 Paketdateien. Original-XCMate-Icon und 98 Original-Themengrafiken unverändert.

Das Paket liegt ausschließlich auf dem Entwicklungsbranch und als CI-Testartefakt. Produktionsindex und .37-ZIP bleiben unverändert. Es wird nicht als reguläres Repository-Update veröffentlicht.

## Nachweise

| Prüfung | Ergebnis / Grenze |
|---|---|
| Vollständige unittest-Suite | 1.357 PASS / 198,999 s, Host Python 3.12.14 |
| PO-Dateien Deutsch/Englisch | je 918 Kontexte, gültige Kodi-gettext-Syntax |
| Lokale Tabler-Icons | 92 PNGs, fest gepinnte SVG-/Lizenz-/SHA256-Provenienz geprüft |
| Syntax | compileall/AST erfolgreich; unveränderter SMBProtocol-Vendor-Docstring erzeugt bekannte SyntaxWarning |
| Startup | 13 neue Tests: Diagnose-Altdefault, Aliase, 20 Refreshs, Background, fremder Player, doppelte Tokens und Resolver-Race |
| Cover-TTL | 4 neue Tests: mehrere Ablaufgrenzen ohne Referenz-/Revisionswechsel bei Erfolg; strengere neue Zulassung bleibt bestehen |
| Live-Rail/Mini | 9 neue Tests: 20 vollständige Links-Ketten, Rückweg, Vollhöhe, echte lokale Vorher/Jetzt/Danach-DB, Mitternacht und leerer EPG |
| Medien/Guide/Fokus | 8 neue Tests: Medien-Rail/IR/Back, eingefrorene Suche, verzögerter Modal-Handoff, Control 300; Guide 20 Öffnen-/Schließen-Zyklen |
| VOD/Stop | 8 neue Tests zusätzlich zu alter Player-Suite: Seek-Capabilities, Zeiten, Kodi-Spulen, Back, asynchroner Stop, expliziter Retry, Home erst nach Stop |
| Inventur/Bereinigung | 10 neue Tests: keinerlei Schreibzugriff bei Inventur, doppelte Bestätigung, eigene Dateien, Symlink-/Hardlink-/Rootaustauschschutz, Abbruch/Journal/DB-Busy, neue Dateien erhalten |
| SQLite | 4 neue Tests: fehlende DB, Schema und exklusive Sperre mit echten temporären Datenbanken; Query-Unterbrechung per Fehlerklassifikation |
| Box-A-Vorprüfung | 3 neue Tests nur mit Testprofilen: bytegleiche Bestände, Sicherungsabgleich bei ruhendem Profil, Symlink-Ablehnung |
| Bestandsmigration | Bestehende .37-Hash-/Interrupt-/VFS-/SMB2-Tests weiterhin grün; keine reale Box-Migration |

Die Suite enthält echte Loopback-HTTP-/SMB2- und große SQLite-Fixtures, keine Provider-Zugangsdaten. Gemessene Hostwerte dieses Laufs:

| Fixture | Messwert |
|---|---|
| XMLTV | 160.005 gelesen / 160.003 gespeichert, 95.571.948 XML-Bytes, 199.876.608 DB-Bytes, 12,254 s |
| Filmkatalog | 200.005 Titel, 109.380.521 HTTP-Bytes, 309.522.432 DB-Bytes, 25,253 s |
| Serienkatalog | 200.005 Titel, 109.380.521 HTTP-Bytes, 621.727.744 kumulative DB-Bytes, 25,081 s |
| Katalog-Prozess Peak-RSS | 57.384 KiB; Hostmessung, kein ARM32-RAM-Beweis |
| Kaltes Fenster im Kodi-Modell | 4,210 ms; kein echter Kodi-/Android-Latenzwert |

Vorher/Nachher sind für die Fixes als reproduzierbare Zustands-/Aufrufnachweise belegt: der alte Diagnose-Default blockiert den Portalstart nicht mehr; 20 Refreshs ergeben genau einen statt wiederholter Starts; TTL-Grenzen erzeugen bei erfolgreicher Prüfung keine leere Zwischenreferenz; Markieren/Programm-IR löst keinen Tune aus; Stop läuft nicht synchron im GUI-Callback. Es liegen keine neuen Vorher/Nachher-Android-Messwerte vor.

## Bestandsschutz

`SCHUTZPRUEFUNG_02938.json` / `tools/verify_xcmate_02938_protection.py` prüfen die explizite Quell-Ausnahmeliste, 251 unveränderte Add-on-Dateien, alle 1.298 alten Testmethoden, 163 historische UI-Vertragsdateien (159 bytegleich zu .37, vier einzeln geprüfte Hook-Ausnahmen), sechs unveränderte Such-XML-Controls, Originalbilder/Icon, Decoder, Portal-/EPG-/Resume-/Autoplay- und Keymap-Module. Produktionsindex, altes .37-Paket und CI-Publish-Bedingung bleiben unverändert. Zusätzlich 62 fremde lokale WIP-Dateien gegen vorherige Hashinventare unverändert.

## Reproduktion

In einem frischen separaten Checkout des PRs, Python 3.12 mit Pillow und impacket 0.13.0:

```sh
python tools/build_repository.py
python tools/validate_kodi_po.py
python tools/build_xcmate_nav_icons.py --check
python -m compileall -q src
for f in tests/test_addon.py tests/test_site.py tests/test_providers.py; do
  sed -i "s@'..', 'plugin.video.noodleprivate'@'..', 'src', 'plugin.video.noodleprivate'@g" "$f"
done
python -m unittest discover -s tests -v
python tools/verify_xcmate_02938_protection.py --output /tmp/xcmate38-protection.json
```

Der Builder erzeugt Repository-Artefakte für mehrere Add-ons; nur im separaten Checkout ausführen und diese generierten Produktionsdateien nicht veröffentlichen. Der Hostlauf benutzte die bereits lokal vorhandene impacket-Abhängigkeit über PYTHONPATH; GitHub CI installiert dieselbe Version regulär. Der CI-Lauf des Draft-PRs muss vor Übergabe grün sein; der Publish-Schritt ist bei Pull Requests gesperrt. Die CI erzeugt zusätzlich ihr eigenes ZIP und ihren Testbericht; deren SHA wird mit diesem Paket abgeglichen.

## Abnahme und offene Punkte

[Android-Testplan](ANDROID_ABNAHME_02938_DE.md), [57 Geräte-Gates](ANDROID_STATUS_02938.json), [Ursachenanalyse](URSACHENANALYSE_02938_DE.md), [68-Issue-Matrix](ISSUE_MATRIX_02938_DE.md), [drei OSD-Varianten](OSD_VARIANTEN_02938_DE.md).

Box B bleibt Dynamisch, keine weiteren Kopier-/Migrations-/Löschtests. Box-A-Version UNKNOWN; erst lesende Inventur und geprüfte Sicherung. Alle .38-Gerätetests NOT_TESTED. Host-Kodi-APImodelle beweisen keine realen Android-Dialog-IDs, Fokusübergaben, IR-Tastenwiederholungen, native DNS/TLS-Transporte, Decoder oder mehrstündige ARM32-Stabilität.

Teilumfänge bleiben ausdrücklich offen: permanente Home-Rail und vollständige rubrikübergreifende Scroll-Restauration, endgültige OSD-Designabnahme, physischer externer Metadatenbestand (#171), dauerhaftes ungespeichertes Wizard-Scanresume (#43/#164), quellensichere manuelle EPG-Zuweisung (#98). #161 EPG-Hub und #182 Widget-Architektur (.39) getrennt. Keine Downloads-/Aufnahmenreparatur. Kein Issue wird durch Hosttests geschlossen.
