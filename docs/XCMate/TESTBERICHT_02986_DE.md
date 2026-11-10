# Testbericht XCMate 0.1.29.86

**Zwischenstand im Draft-PR: vollständiger Hostlauf und GitHub CI noch ausstehend. Kein Merge-/Releasekandidat.**

- 24 neue gezielte A/B/D-Tests bestanden: vollständige 88er-Identitätsleiste ohne EPG-SQL/Netz, getrennte Quelldimensionen, CSI-Null-/Thumbnail-Hysterese, Renderer-Receipt, Ereigniswechsel/Opt-out, unabhängige freie Werkrecherche, Film-/TV-Unterscheidung, fehlende EPG-Fakten, Abbruch, erneute Werkprüfung vor Save.
- 4 neue Tests am tatsächlichen BINGIE-XML-Graph bestanden: vollständiger Graph, eigener proportionaler Postermodus/Preload/Status, Byteerhalt persönlicher/native Widget-Definitionen, unbekannte Änderungen blockiert, Idempotenz.
- Bestandsschutz prüft die 3.451 direkt deklarierten alten Testmethoden plus ihre unveränderten Skip-Bedingungen. Die bisherige Gesamtsuite umfasst zusätzlich geerbte Testfälle; direkte Methodenzahl und ausgeführte Fallzahl sind verschieden.
- PO-Dateien: 17 Sprachkataloge syntaktisch validiert. Neue Texte DE/EN, bestehender englischer Fallback für weitere Sprachen.
- Erster Gesamtlauf wurde nach nachgewiesenen lokalen Reservenproblemen abgebrochen; kein vollständiges PASS. Nach Freigabe ausschließlich entbehrlicher Entwicklungskopien bestanden die zuvor betroffenen Einzeltests wieder. Kein Kodi-Benutzerprofil angefasst.
- Native lokale Docker-Versuche vor Containerstart durch Platzmangel blockiert: kein Screenshot-/Pixel-PASS daraus. Native Prüfungen werden über GitHub Actions angefordert.
- Physische Android-Prüfungen: **ANDROID_NOT_TESTED** in allen A86/B86/C86/D86/E86/REG86-Gates.

## Abnahmematrix

| Bereich | Implementierung | Host | echter Kodi/Linux | Box B |
|---|---|---|---|---|
| A – vollständige Senderleiste / lokaler Logo-Nachweis | vorhanden | gezielt PASS; Gesamtlauf ausstehend | ausstehend | ANDROID_NOT_TESTED |
| B – typed Hero / Qualität / CSI-Hysterese | vorhanden | gezielt PASS | ausstehend | ANDROID_NOT_TESTED |
| C – persönliche/native Widget-Reihen | Byteerhalt, unveränderte Pfade | XML-Graph PASS | ausstehend | ANDROID_NOT_TESTED |
| D – freie TV-/Filmsuche und sichere Zuordnung | vorhanden | gezielt PASS | ausstehend | ANDROID_NOT_TESTED |
| E – sichtbarer begrenzter Ladestatus | Controls vorhanden | XML-Graph PASS | ausstehend | ANDROID_NOT_TESTED |
| Anderer Android-Speicherpool | keine unbelegte automatische Aktivierung | negative Pfade geprüft | kein Hardwarebeweis | EXTERNAL_UNAVAILABLE / ANDROID_NOT_TESTED |
| Veröffentlichung / Merge | nicht freigegeben | bestehende .85-Kanäle bytegleich geprüft | nicht erfolgt | nicht erfolgt |

Build-Dateien und SHA256 unter `test-builds/02986/`. Nach Abschluss der Läufe werden tatsächliche Ergebnisse und CI-Links ergänzt.
