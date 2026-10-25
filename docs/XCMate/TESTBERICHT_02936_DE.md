# XCMate .36 – Test- und Paketbericht

Stand 25.10.2026 (Europe/Berlin). Quellen für Paket und Gesamtlauf: **d354175**, kumulativ auf main **46b4f9f** / Add-on-Codebasis .35 **9c558c7**. Spätere Dokumentationscommits ändern den Add-on-Quellbaum nicht. GitHub-CI/Head und direkter Paketlink werden im Draft-PR referenziert.

**Lokaler Gesamtlauf: 1.214 Tests PASS, 0 Fehler, 0 Fehlschläge, 125,286 s.** Unittest-Hostmodelle, reale SQLite-/Datei-/HTTP-/SMB-Testfixtures; darunter Kodi-21/Omega-API-, WindowDialog-/WindowXMLDialog-, Fokus-/Fernbedienungs-/Player-Verträge. **Kein nativ gestartetes Kodi 21.2 und kein Android-Gerätetest.** Alle Android-Ergebnisse bleiben NOT_TESTED.

58 neue gezielte Fälle: 11 Suche/Cache-Inventar, 7 Startsender, 7 Viewport/Katalog, 4 Timing/Privacy, 6 Stop/Home, 23 Genre/Nachindizierung. Bestehende 1.156 Tests weiter bestanden. Der Gesamtlauf prüft zusätzlich M3U/Stalker-Cached-Navigation: der SQLite-Adapter wird nur bei Xtream importiert. Ältere Short-Cache-Modelle enthalten jetzt tatsächliche Cache-Dateinamen; ihr vollständiger Cache-only-/Timeout-Testumfang bleibt erhalten. Frühere fehlgeschlagene Entwicklungsdurchläufe sind keine Liefer-PASS-Wertung.

Reproduktion aus separatem Scratch-Checkout (Builder verändert Paketindizes; nicht im Arbeitsbranch bauen):

```bash
git archive HEAD | tar -x -C /pfad/zum/leeren/scratch
cd /pfad/zum/scratch
python tools/build_repository.py
python tools/validate_kodi_po.py
python -m compileall -q src
python -m unittest discover -s tests -v
```

Die drei historischen Noodle-Testpfade werden im Scratch wie in CI auf `../src/plugin.video.noodleprivate` normalisiert; keine Änderung dieser Fremd-Addon-Quellen. Dependencies/HTTP-/SMB-Testumgebung gemäß bestehendem Workflow `.github/workflows/publish.yml`. Gesamter erfolgreicher Lauf: [TESTLOG_02936.txt](TESTLOG_02936.txt).

| Prüfung | Ergebnis |
| --- | --- |
| Repository-Builder / Add-on .36 | PASS, nur Scratch-Indizes geschrieben |
| Deutsche/englische PO-Dateien | PASS, jeweils 788 Kontexte |
| Python compileall / ZIP-AST | PASS; vorhandene Vendor-SyntaxWarning im unveränderten SMB-Code kein neuer .36-Fix |
| ZIP-Dateianzahl / Größe | **264 Dateien / 2.391.921 Bytes** |
| CRC, eindeutige sichere Pfade, reguläre Dateien | PASS |
| Jede gepackte Datei gegen aktuellen Quellinhalt | PASS |
| Reproduzierbare ZIP-Bytes | PASS |
| Profile/DB/Rohlogs/pycache im Paket | Keine |
| UI-/Owner-/Handoff-Freeze | 163 Dateien bytegleich; Original-Space-Premium 98 Bilder bytegleich |
| Geschützte vorhandene Add-on-Quellen | 243 unverändert; 21 explizit geprüfte geänderte/neue Quellpfade |
| Player/Renderer/native Live-Callbacks | AST-identisch außerhalb exakt benannter Daten-/Timing-Hooks; bestehende historische Hashfixtures nicht überschrieben |
| Autoplay/Resume/Gesehen/Portal-/Mapping-/Download-/Aufnahmecode | Unverändert |
| Unabhängige vorhandene lokale WIP-Dateien | 62 Hashes unverändert |
| Produktiv-Index/Publishworkflow/.35-Rückfall-ZIP | Unverändert; keine Freigabe/Veröffentlichung |

ZIP: `plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.36.zip`.

```text
a7cd88d07d1da3b1c14a94c2dc3983ffe8082a00e5dfc107f2d5cae69042fdca  plugin.video.xtreammate-0.1.29.36.zip
```

Maschinenbericht [TESTERGEBNISSE_02936.json](TESTERGEBNISSE_02936.json), vollständiger [Dateikatalog](DATEIKATALOG_02936.json), [Schutzprüfung](SCHUTZPRUEFUNG_02936.json), [reproduzierbare Messwerte](HOST_MESSWERTE_02936.json), [Ursachen/Migration/Messgrenzen](URSACHENANALYSE_02936_DE.md), [Android-Checkliste](ANDROID_ABNAHME_02936_DE.md) und [Issue-Matrix aller 50 offenen Issues](ISSUE_MATRIX_02936.json).

Der PR-Workflow baut und prüft den Kandidaten erneut. Sein Publish-Schritt muss **SKIPPED** sein; ein grüner PR-Check ist keine Release-/Merge-/Android-Freigabe. #111 neuer Poster-/TMDb-Fix BLOCKED, bestehender selektiver Retry geschützt. #159 implementiert, noch Android-abzunehmen. Keine Issues geschlossen, keine Produktivinstallation vorgenommen.
