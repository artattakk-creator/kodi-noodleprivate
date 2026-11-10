# Testbericht XCMate 0.1.29.86

**Review-Stand: Add-on-Quellstand `ae288f6ef4e8e0a67783ecba67d30a42df9eabd0`; vollständiger lokaler Hostlauf bestanden. Abschließende CI-/Langzeitläufe werden auf demselben Add-on-Inhalt ausgeführt. Der endgültige Run-/Commitstatus wird ohne erneute Add-on-Änderung in Draft-PR #410 und Issue #409 dokumentiert. Kein Merge-/Release freigegeben.**

- Neue gezielte A/B/D-Tests bestanden (weitere Fälle gegenüber dem ersten 24er-Lauf ergänzt): vollständige 88er-Identitätsleiste ohne EPG-SQL/Netz, getrennte Quelldimensionen, CSI-Null-/Thumbnail-Hysterese, Renderer-Receipt, Ereigniswechsel/Opt-out, unabhängige freie Werkrecherche, Film-/TV-Unterscheidung, fehlende EPG-Fakten, Abbruch, erneute Werkprüfung vor Save.
- 4 neue Tests am tatsächlichen BINGIE-XML-Graph bestanden: vollständiger Graph, eigener proportionaler Postermodus/Preload/Status, Byteerhalt persönlicher/native Widget-Definitionen, unbekannte Änderungen blockiert, Idempotenz.
- Bestandsschutz prüft die 3.451 direkt deklarierten alten Testmethoden plus ihre unveränderten Skip-Bedingungen. Die bisherige Gesamtsuite umfasst zusätzlich geerbte Testfälle; direkte Methodenzahl und ausgeführte Fallzahl sind verschieden.
- PO-Dateien: 17 Sprachkataloge syntaktisch validiert. Neue Texte DE/EN, bestehender englischer Fallback für weitere Sprachen.
- Erster Gesamtlauf wurde nach nachgewiesenen lokalen Reservenproblemen abgebrochen; kein vollständiges PASS. Nach Freigabe ausschließlich entbehrlicher Entwicklungskopien bestanden die zuvor betroffenen Einzeltests wieder. Kein Kodi-Benutzerprofil angefasst.
- Native lokale Docker-Versuche vor Containerstart durch Platzmangel blockiert: kein Screenshot-/Pixel-PASS daraus. Native Prüfungen wurden über GitHub Actions ausgeführt; abgeschlossene Nachweise und die abschließenden Läufe stehen unten.
- Physische Android-Prüfungen: **ANDROID_NOT_TESTED** in allen A86/B86/C86/D86/E86/REG86-Gates.

## Abnahmematrix

| Bereich | Implementierung | Host | echter Kodi/Linux | Box B |
|---|---|---|---|---|
| A – vollständige Senderleiste / lokaler Logo-Nachweis | vorhanden | PASS (vollständiger Hostlauf) | ausstehend | ANDROID_NOT_TESTED |
| B – typed Hero / Qualität / CSI-Hysterese | vorhanden | PASS (vollständiger Hostlauf) | .86 native Bild-/Neustartprüfung PASS; kein echter CSI-/Android-Beweis | ANDROID_NOT_TESTED |
| C – persönliche/native Widget-Reihen | Byteerhalt, unveränderte Pfade | XML-Graph/Host PASS | synthetische Custom-Reihen PASS; reale persönliche Reihen offen | ANDROID_NOT_TESTED |
| D – freie TV-/Filmsuche und sichere Zuordnung | vorhanden | PASS (vollständiger Hostlauf) | ausstehend | ANDROID_NOT_TESTED |
| E – sichtbarer begrenzter Ladestatus | Controls vorhanden | XML-Graph/Host PASS | ausstehend | ANDROID_NOT_TESTED |
| Anderer Android-Speicherpool | keine unbelegte automatische Aktivierung | negative Pfade geprüft | kein Hardwarebeweis | EXTERNAL_UNAVAILABLE / ANDROID_NOT_TESTED |
| Veröffentlichung / Merge | nicht freigegeben | bestehende .85-Kanäle bytegleich geprüft | nicht erfolgt | nicht erfolgt |

## Reproduzierbarer Build

- Version: **0.1.29.86**.
- 811 Add-on-Dateien, ZIP **3.586.611 Bytes**.
- SHA256: `07c7f10b0f5da873c1add538c44bf2ee4c9aa5027ad98c262ec98bd5d709c7c4`.
- ZIP-CRC, Bytevergleich mit allen Paketquellen und separat heruntergeladenem GitHub-Git-Blob: **PASS**.
- Draft-PR: [#410](https://github.com/artattakk-creator/kodi-noodleprivate/pull/410).
- [Komplette Host-CI](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42821190964), [native .86-Bildprüfungen](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42821190965), [kumulative native Home-/Playerprüfung](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42821190880). Der abschließende Run-/Commitstatus steht in der PR-Beschreibung und im letzten Abschlusskommentar zu #409; die obigen abgeschlossenen Quellstand-Nachweise bleiben historisch verlinkt.

53 gezielte Handoff-/Hero-/Opt-out-/Bestandsschutz-/ältere Low-Space-Tests bestanden, anschließend 33 aktuelle Live-/Hero-/Opt-out-/Scope-Fälle einschließlich zwei neuer Live-Statusfälle bestanden. Diese überlappenden Auswahlmengen werden **nicht** zu einer angeblichen Gesamtfallzahl addiert. Zusätzlich 11 Branding-Pytests bestanden; eine externe pytest-Plugin-Deprecation-Warnung. Alle 17 PO-Kataloge validiert.

## Fehlersuche und Grenzen früherer Läufe

- Frühere CI-Läufe fanden echte Typverlust-/Kaltstart-/Texturprobleme; ihre roten Ergebnisse bleiben historisch sichtbar und gelten nicht als PASS. Insbesondere gingen `role81` und die Unterscheidung Originalauflösung/Kodi-Cacheauflösung verloren; beide Pfade haben gezielte Regressionstests.
- Die nativen Positivfixtures liefern nun real decodierte 1280×720-Szenen beziehungsweise 800×1200-Poster. Kleine negative Bildfälle bleiben abgelehnt. Es wurde weder eine Pixelprüfung entfernt noch die Quellen-/Mindestqualitätsprüfung gelockert.
- Modelltests mit globalen Kodi-Stubs müssen ihren Worker-/Modulzustand trennen; die alten Low-Space-Referenztests starten mit einem frischen eigenen Asset-Modul. Alle ursprünglichen Testmethoden und Skip-Bedingungen bleiben vorhanden.
- Keine privaten Rohlogs in PR, Paket oder CI-Artefakten. Alle für native Tests verwendeten Providerprofile, Bilder, Zertifikate und Filme sind synthetische Wegwerf-Fixtures. Kein künstlicher Python-Speicherwert wird als echter Android-ENOSPC-Nachweis ausgegeben.

Build-Dateien unter `test-builds/02986/`.

## Synthetische Hostmessung (keine Android-Zeit)

Gleiche 88 Sender, lokaler SQLite-Katalog und vorhandener lokaler EPG-RAM-Snapshot, zwölf Aufbauten je Darstellungsweg, keine Netzwerkabfrage:

| DTO-Pfad | P50 | P95 |
|---|---:|---:|
| bisheriger `live_items62.values`-Pfad | 137,390 ms | 246,961 ms |
| neuer Identitätsweg `live_rail86.values` | 14,704 ms | 16,871 ms |

Die Zeit endet mit der Datenerzeugung. Sie ist kein First-Frame-Nachweis und kein Beleg für die Android-SLO von 2/5 Sekunden.

## Zusätzliche aktuelle Regressionen

- 71 gezielte Fälle zu Provider-Metadatenvorrang, manuellen Bildern/Opt-out, exakter Offline-Cachewiederverwendung, Hero-Typen und Bestandsschutz: **PASS**.
- Der zuvor eingefrorene Gesamtlauf führte 3.544 Fälle aus, mit genau einem bestätigten Fehler im neuen Widget-Metadatenübergang. Korrektur: Bilder und Metadaten trennen. Der unveränderte alte `.58`-Provider-Metadatentest und ein zusätzlicher kombinierter Bild-/Metadatentest bestehen. Dieser frühere Gesamtlauf ist **kein vollständiges PASS**; maßgeblich ist der anschließende neue Lauf.
- Native .86-Bildprüfung auf dem vorangehenden Quellstand `af140cd5110ddc0cb4352dc864990f440109fc5d`: [beide Auflösungen bestanden](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42819586260), einschließlich proportionalem offiziellen Poster und zwei Offline-Neustarts. Die aktuelle .86-Prüfung wird erneut ausgeführt. Android bleibt ungetestet.
- Die native alte Idle-Prüfung beginnt jetzt erst nach einem begrenzten Nachweis des korrekt gerenderten Ausgangsframes. Die unveränderten Pixel-, Reihenanzahl- und Langzeitprüfungen bleiben erhalten. Fehlende Ausgangsbilder sind weiterhin ein Fehler, kein stillschweigender Skip.

## Vollständiger eingefrorener Hostlauf

Quellstand `ae288f6ef4e8e0a67783ecba67d30a42df9eabd0`, anschließend ausschließlich Korrektur des nativen Kaltstart-Prüfaufbaus, keine weiteren Add-on-Änderungen:

```text
python -m unittest discover -s tests -v
Ran 3545 tests in 547.052s
OK
```

**3.545 PASS, 0 FAIL, 0 ERROR.** Darin 3.486 beibehaltene ausführbare Basisfälle und 59 neue .86-Fälle. Direkte Testmethoden/ausgeführte geerbte Fälle bleiben getrennte Zählweisen. Die SHA-/Skip-/Kanalprüfungen laufen als Teil dieser Suite unverändert mit. Weitere 11 Branding-Pytests und 17 validierte PO-Dateien sind getrennte Prüfungen, keine zusätzlichen Unittest-Fälle.

Auf demselben Add-on-Quellstand: native .86-Bildprüfung in 1080p/720p sowie je zwei Offline-Neustarts **PASS**, [CI 42821190965](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42821190965). Native Playerprüfung mit 20 Stop-ACK-/Rückkehrzyklen je Medientyp, insgesamt 60: **PASS**, [Job 129846989976](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42821190880/job/129846989976). Alle diese Nachweise gelten für synthetisches Linux Kodi, ausdrücklich nicht für Android.

Der alte native Kaltstart-Prüfaufbau hatte seinen erforderlichen lokalen Journal-Recovery-Worker ausschließlich bei Versionsstring `.85` eingeschaltet. Er wird jetzt auch bei `.86` ausgeführt, weil diese Version denselben geschützten Journal-Worker erbt. Es bleiben zwei tatsächliche Offline-Neustarts, exakter Cache-/Verzeichnisabgleich und reale Pixelprüfungen erhalten. Die abschließenden nativen Gesamt-/Langzeitläufe werden nach Abschluss zusätzlich verlinkt.

## Reproduktion / Datenintegrität

Lokaler Testprozess: Python 3.12, Pillow 12.3.0, impacket 0.13.0, simpleeval 0.9.13, pytest 9.2.0. CI benutzt Python 3.12 und dieselben deklarierten Abhängigkeiten. Große synthetische SQLite-Sortierdaten nutzen lokal ausschließlich `SQLITE_TMPDIR`; Kodi-/Benutzerdateien werden nicht umgeleitet.

Das ZIP wurde erneut unabhängig gebaut und bytegenau verglichen. Der separat über die GitHub Git-Blobs-API gelesene Paketinhalt ist ebenfalls identisch. SHA256/CRC und sämtliche 811 Paketquellen stimmen überein. Alle bestehenden Veröffentlichungsindizes und .85-Pakete sowie Installer 0.5.26 werden durch die vollständige Suite unverändert geprüft.

Die abschließenden Workflow-Nachweise sind über [PR #410](https://github.com/artattakk-creator/kodi-noodleprivate/pull/410), [Master #409](https://github.com/artattakk-creator/kodi-noodleprivate/issues/409) und [Actions für den Entwicklungsbranch](https://github.com/artattakk-creator/kodi-noodleprivate/actions?query=branch%3Afix%2Fxcmate-02986-android-live-hero-mapping) abrufbar. PR-/Issue-Abschlussberichte unterscheiden vollständigen Hostlauf, native Pixel-/Langzeitnachweise und physische Android-Abnahme.
