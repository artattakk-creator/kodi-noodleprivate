# XCMate .96 – Fehlerkorrektur und unabhängige Qualitätssicherung

**Auftrag:** #469, bestehender Draft-PR #471. **Branch:** `fix/xcmate-02996-groups-artwork-mapping`. **Geprüfter Code-/Test-/ZIP-Commit:** `36df57c82d4036a7820a46f36ce141247201091f`.

Dieser Bericht ergänzt den historischen roten Gesamttest auf `98bc3b16`; dessen Nachweise werden nicht entfernt. Ausgangsbasis ist die vollständige .95-Quelle `c230fed9` einschließlich der schon integrierten main-Basis `dfea6a72`. Keine neue Version, kein neuer Entwicklungsbranch, kein Merge oder Release. Modell-B / PR #472 bleibt unverändert.

## Änderungen und Ursachen

Die 13 dokumentierten Fehlfälle sind gezielt korrigiert und vor dem vollständigen Gegenlauf grün geprüft. Die genaue Zuordnung jedes Fehlfalls und die RED/GREEN-Nachweise stehen im [Korrekturbericht](FEHLERKORREKTUR_02996_13_REGRESSIONEN_2026-11-16_DE.md).

- `event_art81.rank()` liefert wieder numerische Ränge. Die versehentliche, undefinierte Quellenprüfung ist entfernt; der Quellenschalter bleibt getrennt in der Anzeigezulassung erhalten.
- Optionale Cinematic-`images`-Abfragen finden nur im zugelassenen Home-Hero-Pfad statt. Allgemeines TMDB-Matching und kalte Bildmaterialisierung behalten Suche → Details → Bild bei. Damit entfallen die nachgewiesenen `StopIteration`-/`FETCH_FAILED`-Abbrüche.
- Der native Home-Fehler `-32602` war die Folge des Plugin-Seed-Abbruchs. Der RPC-Aufruf und seine nachfolgenden Anzeige-/Player-Gates wurden nicht vereinfacht; die unveränderten Movie-/TV-Seed-Blöcke sind zusätzlich durch Host-Regressionen abgesichert.
- Der echte Xtream-Quellendialog verwendet die vorhandene Icon-Dekoration. Provider-Baseline, Menüroute, Extras/Mapping/Abbruch, Fernbedienungsfokus, Portalhistorie und Tokenimport sind durch tatsächliche Callbacks geprüft. Alte Prüfungen auf Fremdfelder, Tokenbytes, Persistenz und Navigation bleiben erhalten.
- Vier zusätzliche unabhängige Review-Funde sind behoben: exakte manuelle Bildwahl erhalten; XMLTV-Provenienz über Worker, lokale Datei und temporären Cache bewahren; Logoänderungen in bereits vorhandenen Live-Channel-Objekten anzeigen; manuelle lokale XMLTV-Alternativen unabhängig von deaktivierten externen Suchdiensten zulassen. Opt-outs, Ereignisbindung und Quellenrevision bleiben wirksam.

## Unabhängigkeit und Zusammenführung

| Verantwortlich | Abgeschlossene Arbeit dieser Korrekturrunde |
|---|---|
| `cinematic_images` | Request-Reihenfolge, Hero-Admission und exakte manuelle Bildreferenzen; 175 fokussierte Prüfungen PASS. |
| `mini_mapping` | Menü-/Provider-/Token-/Fokuskontrakte und realer Wizard-Dialog; 212 fokussierte Prüfungen PASS. |
| `storage_logo` | Echter nativer Seed als Host-Reproduktion; anschließend revisionssichere bestehende Live-Logoanzeige. Letzter Logo-/Overlay-Lauf 48 PASS, darunter sieben neue Regressionen. |
| `review96_final` | Ausschließlich lesender unabhängiger Review mit isolierten Reproduktionen; abschließend 332 PASS, keine bestätigten offenen Findings im geprüften Host-Scope. |
| Root | Numeric-Rank-Fix, XMLTV-Provenienz/-Admission, Integration, Paketierung, vollständige Gegenläufe und Dokumentation. |

Alle Autoren arbeiteten im selben vorgesehenen .96-Worktree mit abgegrenzten Dateibereichen; keine parallelen Produktbranches oder Agentencommits. Root führte die Änderungen gemeinsam in `3b63ae8d` und dem abschließenden `36df57c8` zusammen. Der zweite Commit enthält den letzten unabhängigen XMLTV-only-Fund. Keine verlorenen Teiländerungen festgestellt. Danach sind Code, Tests, Harness und Paket während der Verifikation eingefroren; abschließende Dokumentation verändert diese Bytes nicht.

Der [vollständige unabhängige Reviewbericht](UNABHAENGIGER_REVIEW_02996_PR471_2026-11-16_DE.md) wurde auf Nutzerauftrag in [PR #471](https://github.com/artattakk-creator/kodi-noodleprivate/pull/471#issuecomment-6913699606) veröffentlicht. Der Reviewer selbst änderte weder Dateien noch GitHub.

## Abschließende Tests

**Abschluss am 16.11.2026: vollständige Hosttests, unabhängiger Review und sämtliche 17 CI-Workflows grün. Native Kodi-Prüfungen in beiden Auflösungen bestanden. Android-Abnahme weiterhin offen.**

| Prüfung | Ergebnis / Grenze |
|---|---|
| Unabhängige Auswahl | 332 PASS / 0 FAIL, 57,56 s; drei bestehende simpleeval-Warnungen. Kein Ersatz für Gesamtsuite. |
| Vollständiges unittest | **4.142 PASS**, 1.111,159 s, Exit 0, exakt `36df57c8`. |
| Vollständiges pytest | **4.153 PASS**, 1.173,99 s, Exit 0, vier bestehende Warnungen, exakt `36df57c8`. |
| Native EPG 720p / 1080p | PASS / PASS; Linux-Kodi 21.2, synthetischer XMLTV-Transport, 600 unabhängig gelesene Datensätze, Fokus und Preview/Cancel. Kein physischer Android-Langpressnachweis. |
| Exaktes ZIP / native Widgets | PASS in 720p und 1080p; Medienreihen, Überschriften, Spinner, Fokus und unverändertes Paket. |
| Native Medien | 60 PASS: je 20 VOD-/Episoden-/Live-Zyklen mit tatsächlichem Linux-Decode, genau einem Stop und nativem ACK. Android-Decoder und Android-Fullscreen-Rückweg nicht hiermit freigegeben. |
| Nativer Home 1080p | PASS; 31 Fälle, echte Hero-/Detailbildpixel, unverändertes Benutzerlayout, Filmstart/-stop/-Detailrückkehr, Guide-Fokus und DB-Pausenwiederaufnahme. |
| Nativer Home 720p | **PASS**, einschließlich 1.800,95 s tatsächlicher DB-Pause, 443 Duplikatpolls, genau einem Worker, Wiederaufnahme desselben Workers und keiner unbehandelten Ausnahme; vollständige Folgeregressionen bestanden. |
| Compile / PO / Diff | PASS; 17 Sprachkataloge geprüft. |
| Paket | Zweimal byteidentisch; CRC, alle 899 Quellbytes, sicherer Dateisatz und SHA256 PASS. |
| GitHub CI | **17 Workflows SUCCESS / 0 FAILURE**, alle abgeschlossen. CI-unittest: **4.142 PASS**, 1.415,964 s; CI-pytest: **4.153 PASS**, 1.473,32 s, vier bestehende Warnungen. |
| Native Start-/Retentionsprüfung | PASS in **720p und 1080p**, ebenso ursprünglicher Picker. Optional ausschließlich manuell ausgelöste Diagnosejobs bleiben SKIPPED, keine abgeschwächten Gates. |
| Android | Sämtliche physischen Gerätegates ANDROID_NOT_TESTED. |

Maßgebliche CI-Läufe: [vollständige Host-/EPG-Prüfung](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43847584480), [vollständige Source-/Paket-/Kanalsicherung](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43847584277), [Home/Player 720p/1080p](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43847584260), [exaktes ZIP / Widgets](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43847584262), [Start/Retentionsprüfung](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43847584516). Alle 17 Workflow-Links und tatsächlichen Resultate stehen in [CI_36df57c8.json](test-builds/02996/CI_36df57c8.json). Teilzahlen überschneiden sich und werden nicht addiert.

Die beiden vollständigen Host-Gegenläufe nutzen getrennte temporäre Klone und 227 ausschließlich bytegeprüfte historische Testeingaben. Diese Eingaben werden nicht in den Entwicklungsbranch oder einen Veröffentlichungskanal zurückkopiert. Der vorletzte Lauf von `3b63ae8d` wurde nach dem letzten Reviewfund beendet und gilt ausdrücklich nicht als Abschlussnachweis.

## Installierbares Reviewpaket

- Version **0.1.29.96**, 4.764.280 Bytes, 899 Mitglieder.
- [ZIP auf dem geprüften Codecommit](https://github.com/artattakk-creator/kodi-noodleprivate/raw/36df57c82d4036a7820a46f36ce141247201091f/docs/XCMate/test-builds/02996/plugin.video.xtreammate-0.1.29.96.zip).
- [SHA256-Datei](https://github.com/artattakk-creator/kodi-noodleprivate/blob/36df57c82d4036a7820a46f36ce141247201091f/docs/XCMate/test-builds/02996/plugin.video.xtreammate-0.1.29.96.zip.sha256).
- **SHA256:** `249d7908d83cf7808d950e938e572fc046c2b0fc767aeebd3195b18b87b9d740`.
- Reviewplan: `REVIEW_PACKAGE_ONLY`, `repository_staged=NONE`, `repository_released=false`, keine Merge-/Publish-Aktion.
- Alle eingefrorenen Kanäle bytegleich zur Veröffentlichungsbasis `dfea6a72`; .95-Pilot-ZIP `1eed4d84…` und .90-Fallback `e95b0a0c…` unverändert geprüft.

## Offene Geräteprüfung und Sicherheitsgrenzen

[Android-Abnahmeplan](ANDROID_ABNAHME_02996_DE.md): Startgruppen/Startsender, reale Profile und alte Upgrades; sichtbare Bildsynchronität; XMLTV/TMDB/TVMaze mit vorhandenem Token; echtes Lang-OK, Fokus, Save/Cancel; geänderte Logos in sechs Ansichten und derselben geöffneten Liste; SMB/Android-Speicherreserven; Rebootpersistenz, Widgets, Autoplay und kontextuelle Player-Rückkehr. Alle Gerätegates bleiben **ANDROID_NOT_TESTED**.

Die ursprüngliche Settings-Ladestörung auf der privaten Box ist ohne deren geprüfte Datei nicht abschließend erklärt. Beschädigte Einstellungen werden nur aus verifizierter Sicherung repariert; ohne Wiederherstellungsnachweis bleibt der Vorgang BLOCKED. Keine Zugangsdaten durch geratene Defaults ersetzen.

Keine Nutzerdaten, EPG-/SQLite-/WAL-/Backup-Dateien, Token, Sendergruppen, Favoriten, SkinShortcuts oder Widgets gelöscht. Installer unverändert; Box A nicht angefasst. Der kontrollierte spätere Merge-/Pilot-Weg bleibt beim Nutzer. Regulär und NeoDark3 werden durch diesen Auftrag nicht aktualisiert.

## Git-Arbeitsstand und Übergabe

Alle Produktcode-, Test-, Harness- und ZIP-Änderungen sind in den genannten Codecommits gesichert. Dieser Abschlussbericht und die bereinigten Ergebnis-JSONs werden separat als reiner Dokumentationscommit auf demselben Branch gesichert. Source, Tests, Workflows und ZIP sind dabei bytegleich zum grün geprüften Commit `36df57c8`; keine erneute Voll-CI nur für Berichtstext. Lediglich `.superpowers/sdd/xcmate96/progress.md` bleibt als lokales untracked Arbeitsprotokoll außerhalb des Produktpakets.

**Technische Host-/CI-Qualitätsprüfung bestanden, Review-ZIP bereit für Android-Gerätetest.** Keine Hardwareabnahme vorgetäuscht; keine Merge-/Release-Aktion. Die weitere Freigabe erfolgt durch den Nutzer über den vorgesehenen kontrollierten Weg.
