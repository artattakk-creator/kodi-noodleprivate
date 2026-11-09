# XCMate 0.1.29.85 – vollständiger Host-Testbericht

Stand: 09.11.2026, Europe/Berlin. **Draft, kein Release.**

PR: [#408](https://github.com/artattakk-creator/kodi-noodleprivate/pull/408). Basis: veröffentlichte .84, aktueller main-Dokumentationsstand `b7ab7be88bee6c202f987062798484b18ba0c860`. Der vollständige lokale Lauf unten erfolgte auf `58c46c40a5a414b2ff3c3ea7a9bae93fe5cde8af`. Danach wurde ausschließlich der Skin-Bindingfehler des Vorschlagshinweises korrigiert und die native Fixture präzisiert. 50 gezielte echte Skin-/XML-/Hero-/Scope-Tests bestehen danach (6,791 s); vollständige abschließende Source-CI wird im PR dokumentiert.

## Ergebnis und Grenzen

| Prüfung | Tatsächliches Ergebnis |
|---|---|
| Vollständige kumulative unittest-Suite | **3.484 PASS, 0 Fehler, 0 Fehlschläge, 0 Skips**, 524,470 s |
| Historische .84-Testmethoden und Skip-Bedingungen | Alle 3.408 erhalten; Scope-Test PASS |
| Zusätzliche Branding-Pytests | **11 PASS**, 0,13 s; eine externe pytest-Plugin-Deprecation-Warnung |
| Kodi-PO-Kataloge | **17 PASS**; Deutsch/Englisch je 1.267 Kontexte; bestehender Fallback bleibt erhalten |
| Python-Kompilierung / echter BINGIE-XML-Graph | PASS; 63 gezielte Skin-/Hero-/Scope-Tests PASS in 8,041 s |
| Paket CRC / exakte Quellbytes / zweiter Build | **PASS**, byteidentisch |
| Regulär / Pilot / NeoDark3 / Installer | Veröffentlichte .84-Kanäle und Installer 0.5.26 unverändert; Scope-/Kanal-Schutztests PASS |
| Aktuelle GitHub-CI | Separate vollständige Host-, native Bild- und 30-Minuten-Regressionsläufe; verbindlicher Abschlussstatus und Links im PR-Prüfbereich und Abschlusskommentar |
| Echte Android-Box B | **ANDROID_NOT_TESTED** für sämtliche neuen Gates |

Die vollständige lokale Ausgabe wurde unter `/tmp/xcmate85-full8.txt` erzeugt; GitHub Actions lädt die vollständigen Hostberichte und nativen Artefakte hoch. Keine privaten Kodi-Rohlogs oder realen Provider-/TMDB-Zugangsdaten werden veröffentlicht.

## Arbeitspaket A – Stabilität und dynamisches Laden

Geprüft: neuer eigener Cache-Namensraum mit Byte-/Objektlimits, LRU/TTL und aktiven Pins; SHA256/Decode; atomare Manifestveröffentlichung; Journal nach Abbruch; keine Übernahme/Löschung fremder Dateien; Symlinkschutz; Reserveblockade vor Allokation; begrenzter Backoff; semantische Widgetgeneration ohne vollständiges Reload bei reiner Leaseverlängerung; unabhängige Logo-/Event-/Coverreferenzen; sichtbares Fünferfenster; verständliche Ladezustände; EPG-Rollover sowie Event-, Quellen-, Policy-, Datei- und Ablaufgründe.

Der optionale Art-Patch prüft Profil, Portal, Art, Medien-ID, URL, Titel und Quellidentität vor jedem Eingriff. Er setzt weder Liste noch Auswahl zurück. Wenn Kodis DirectoryProvider keine einzelnen Python-ListItems zugänglich macht, wird der vorhandene sichere Reload-Hook verwendet. Ein Python-Index `-1` ist **kein Beleg für einen echten Fokusverlust**; native Tests prüfen die tatsächliche fokussierte Medien-ID.

Die rote Speicherlage der echten Box ist nicht durch Hosttests aufgehoben: zuletzt 26.935.296 Bytes frei bei 80.685.957 Bytes effektiver Reserve im dokumentierten FUSE-Pool von ca. 3,76 GiB. Der neue Cache umgeht diese Reserve nicht. Kein physischer Schreib-/Persistenz-PASS wird behauptet.

## Arbeitspaket B – Serienidentität und manueller Manager

Geprüft: Ghosts UK/USA, Jahr/Land/Werk-IDs, drei Suchseiten und maximal 60 Einträge, unabhängige Root-Details und offizielle Aliase, unvollständige Seiten, M*A*S*H-Kanonisierung, Movie-Konfliktprüfung, bewusste Quellen-Deaktivierung und vorhandene Filmabfrage. Testfälle umfassen Cobra 11, Die Rosenheim-Cops, Modern Family, The Middle und King of Queens.

Manuelle Auswahl: Kontext/Links, sechs bis acht nachladende Kandidaten, ausdrückliches Bestätigen, Abbrechen/Zurück, Korrektur falscher EPG-Jahre nur im expliziten Manager, Quelle/Portal/Profil-Isolation, atomare Speicherung und Cold-Readback, Fehler ohne falschen Erfolgshinweis, Ändern/Automatik/Ausblenden und Epochenschutz gegen alte Bilder.

Unbestätigte Serienposter erhalten keine bestätigte Identität und keine geratenen Episodenfakten. Drei zusätzliche Integrationstests prüfen die tatsächlich verwendete Live-DTO-Whitelist, den A/B-Hero-Puffer und das Löschen des Hinweises beim Eventwechsel. Die bisherige Live-Whitelist hatte die Vorschlagskennung sowie den benötigten Bildnachweis verworfen; beide Felder werden jetzt ausdrücklich und begrenzt weitergegeben.

## Native Linux-Kodi-Prüfung

Verwendet echtes Kodi, gepinntes BINGIE 2.2.3, SkinShortcuts, HTTPS, echte Texturdateien und Screenshot-Pixel; Auflösungen 1920×1080 und 1280×720. Ausschließlich synthetische Programme/Bilder und entbehrliche Linux-Profile. Die 27-MiB-Kapazitätsinjektion betrifft XCMate-Python; Kodi C++ hat tatsächlich freien Hostspeicher. **Kein physischer ENOSPC-/Android-Test.**

Geprüfte Schritte: 88 Sender; begrenztes sichtbares Senderlogo vor Eventbild; Live → Filme → Serien in dieser Reihenfolge; zunächst zwölf sichtbare Cover statt verpflichtendem Archiv aller 24; Nachladen bis Titel 24 mit Medien-ID 23 im Fokus; echte Kandidatenposter, native Bestätigen-/Back-Aktionen ohne implizites Mapping; unbestätigter Hinweis im tatsächlichen Hero; zwei Offline-Kaltstarts. Allgemeine Regression zusätzlich mit 1.800 s Ruhephase sowie Player-/Stop-ACK-Fällen.

Die Vorschlagsfixture erneuert vor dem späten Hinweis-Test auf dem Worker den Bildnachweis desselben synthetischen Events. Abgelaufene URL-Leases dürfen nicht als sichtbare Vorschläge gelten. Der vorhandene 60-s-Reloadschutz wird im Test abgewartet, nicht im Produkt umgangen. Endgültige CI-Ergebnisse werden im PR-Abschlussbericht getrennt von Android dokumentiert.

## Große Host-Fixtures und Messwerte

| Datenpfad | Umfang | Vollständiger letzter Hostlauf |
|---|---|---|
| XMLTV → SQLite | 160.005 Programme, 95.571.948 XML-Bytes | 21,422 s; 303.685.632 DB-Bytes |
| HTTP-Filmimport | 200.005 Titel, 109.380.521 HTTP-Bytes | 26,480 s |
| HTTP-Serienimport | 200.005 Titel, 109.380.521 HTTP-Bytes | 26,156 s |
| Beide Kataloge persistent | 400.010 Titel | 621.731.840 DB-Bytes; Prozess-Peak-RSS 141.968 KiB |
| Bestehender 40.005-Titel-Archivpfad | 24 lokale Ergebnisse | Alter Opcode-Budgetpfad INTERRUPTED, neuer Lesepfad 2,758 ms |
| V2-Katalogindex, 20.005 Titel | 24 Ergebnisse | 3,178 ms, vorhandener Indexplan |

Das sind Linux-Hostmesswerte, keine Android-Beschleunigungsbehauptung. Ein früher Lauf scheiterte am real zu kleinen lokalen SQL-Tempvolume; nur das SQLite-Testtempziel wurde auf ein ausreichend großes Laufwerk gelegt. Der Katalogcode und seine Reserven wurden dafür nicht verändert.

## Gefundene und korrigierte Zwischenfehler

Frühere Läufe sind keine endgültigen PASS: TVMaze-Legacy-/Sicherheitsverhalten, Readonly-Frame-Nachweis, präzise Revisionszustände, semantische `Source85`-Metadaten und die echte Live-/Hero-Vorschlagsweitergabe wurden nach Regressionen korrigiert. Die echte BINGIE-Variablendatei enthält historische rohe Ampersands; der neue Patch verwendet den vorhandenen begrenzten Parser statt einer unpassenden generischen XML-Annahme. Die vollständige Suite besteht danach.

Native Testannahmen zu 24 vorab archivierten Covern, falschen Control-IDs und unzugänglichen Python-DirectoryProvider-Indizes wurden ebenfalls korrigiert. Diese Fixturefehler werden nicht als nachgewiesene Produkt-Fokusfehler ausgegeben. Unterbrochene, durch spätere Quelländerungen überholte Läufe zählen nicht als Abnahme.

## Reproduzieren

```sh
python -m pip install 'Pillow>=11,<13' 'impacket==0.13.0' 'simpleeval==0.9.13' 'pytest>=8,<10'
python -m unittest discover -s tests -v
python -m pytest -q tests/test_xcmate_bingie_branding.py
python tools/validate_kodi_po.py
python tools/package_xcmate71.py /tmp/xcmate85-build
cmp /tmp/xcmate85-build/plugin.video.xtreammate-0.1.29.85.zip docs/XCMate/test-builds/02985/plugin.video.xtreammate-0.1.29.85.zip
python tools/run_kodi_home85_contract.py --report-dir /tmp/native85 --resolution 1920x1080
python tools/run_kodi_home85_contract.py --report-dir /tmp/native85-720 --resolution 1280x720
python tools/run_kodi_home82_contract.py --report-dir /tmp/reg85-720 --resolution 1280x720 --fault-idle-seconds 1800
python tools/run_kodi_media77_contract.py --report-dir /tmp/media85
```

Bei begrenztem Host-Tempvolume ausschließlich `SQLITE_TMPDIR` auf ausreichend großes Testlaufwerk setzen; `TMPDIR` unverändert lassen, damit Speicherpool-Tests vergleichbar bleiben. Native Befehle verwenden nur entbehrliche Linux-Container und installieren nichts auf Android.

## Reproduzierbarer Build

- Version: `0.1.29.85`, **801 Dateien, 3.561.826 Bytes**.
- SHA256: `c50c2cf4a9883afd414960c1c3ed7fe8677a9a89187cbd5f79a77d14409e8477`.
- [ZIP / Prüfsumme / Anleitung](test-builds/02985/README_DE.md).
- [Implementierung](IMPLEMENTIERUNG_02985_DE.md), [Issue-Matrix](ISSUE_MATRIX_02985_DE.md), [Android-Abnahmeplan](ANDROID_ABNAHME_02985_DE.md).
- Keine automatische Installation, kein Merge, keine Veröffentlichung. .84 bleibt nutzbare Rückfallbasis ohne Downgrade-Empfehlung.

## Offen und Abnahmegrenzen

#401 bleibt für reale Kapazität/EPG/Bildpersistenz auf Box B offen. #406 benötigt echte passende Bilder, IR-Navigation und dauerhaft bestätigte Zuordnungen nach Neustart. Neues zusätzliches Eventbild direkt in der Mini-EPG-Liste bleibt P1 OPEN; bestehende Details sind erhalten. Kodi-Library-Views wurden nicht destruktiv neu angelegt. Externe/SMB-Tests sind nicht freigegeben und wurden nicht ausgeführt. Alle Box-B-Gates bis zur tatsächlichen Prüfung **ANDROID_NOT_TESTED**.

## Nachtrag: native Vorschlagskennzeichnung

Die native Prüfung erreichte nach erneuertem Bildnachweis die echte Senderzeile mit `Provisional85=true`, aber zunächst nicht den sichtbaren Hinweis. Das Skin-Binding verwendete eine `$VAR`-Expansion in einer booleschen Sichtbarkeitsbedingung; außerdem zeigte dessen Row-Fallback auf `HeroArtSource63`. .85 nutzt nun ausdrücklich die vorhandenen Bank-/Profil-/Tokenprüfungen mit direkter `String.IsEqual`-Auswertung der Vorschlagsfelder, einschließlich korrektem Row-Fallback. Die native Prüfung wartet getrennt auf den asynchronen Verzeichnisframe und Hero-Puffercommit. Der vorherige ZIP-Hash `021689b4…` ist überholt; oben steht der aktuelle Build.
