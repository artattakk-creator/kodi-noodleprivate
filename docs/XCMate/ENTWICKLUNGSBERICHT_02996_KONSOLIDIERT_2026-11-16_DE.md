# XCMate .96 – konsolidierter Entwicklungsstand

**Stand:** 16.11.2026, 08:31 UTC. **Auftrag:** #469; ergänzender Nutzerauftrag zur Konsolidierung vom 16.11.2026. **Draft-PR: [#471](https://github.com/artattakk-creator/kodi-noodleprivate/pull/471). Kein Merge, kein Release.** Dieser Bericht beschreibt den tatsächlichen Entwicklungsstand und ist keine vollständige Funktions- oder Android-Abnahme.

## 1. Branch und Herkunft

- Bestehender Entwicklungsbranch: `fix/xcmate-02996-groups-artwork-mapping`.
- Vollständiger .95-Quellstand: `c230fed998f4f2db0d9035068460cf26433e7ac4` aus Source-Draft #465.
- Aktueller Veröffentlichungsstand von main: `dfea6a72226b8c5fcccfce7d14e186e5e4007673`; Pilot .95, aber main/src noch .92.
- Lokale Integration von main in den .96-Branch: `bc8b3f04`. Dies ist **kein Merge nach main**.
- Erster .96-Code-/Build-Commit: `812ebc8640021cfdbb34ccfdf62b190b07c2f501`.
- **Konsolidierter Code-/Test-/Build-Commit: `98bc3b16e65b45522f3e75ac5002cbdeb14189e2`.** Branch auf GitHub vorhanden. Nachfolgende reine Berichtskommitierung ändert diese ausführbaren Bytes nicht.

Die .96-Entwicklung umfasst gegenüber der integrierten .95-Basis 110 geänderte/ergänzte Dateien. Der Quellvertrag prüft 47 geänderte und 13 neue Laufzeitdateien gegen die vollständige .95; keine .95-Laufzeitdatei wurde entfernt. Der PR gegen main enthält zusätzlich die noch nicht nach main übernommenen .93–.95-Quelländerungen. Deshalb ist sein Gesamtdiff größer als die reine .96-Arbeit.

## 2. Implementierte Funktionen und Grenzen

| Bereich | Implementierung im gemeinsamen Branch | Abnahmegrenze |
|---|---|---|
| Live-Sendergruppen | Eigener indizierter RO-Zielgruppenread, Generationsprüfung, Konto-/Portal-/Auswahlbindung, LastGood, maximal drei Versuche mit Backoff, Wiederaufnahme bei Katalogänderung; keine EPG-/Artwork-Abhängigkeit der Senderliste. | Gezielt getestet; tatsächliches Anzeigen und Umschalten auf RK3528 offen. |
| Settings/Quellen | Bounded Lesen gesunder nativer Einstellungen/Defaults ohne wiederholtes getSetting; ungültige XML und fehlende Rechte nicht als Opt-out behandeln. Sicherung und unabhängiges Readback expliziter Änderungen, Rücknahme fehlerhafter Fremdfeldänderungen bei Erhalt abgewiesener Bytes. | Die reale Ursache der 1.470 Kodi-Ladefehler ist ohne betroffene private Einstellungsdatei nicht bewiesen. |
| Artwork-Hub | Genau XMLTV/TMDB/TVMaze als Quellenschalter; vorhandener Token, bestehender Import und Verbindungstest; manuelle Bildzuweisung, Logoeditor und Link auf denselben Speicherdialog. Gemeinsame Testprofil-Aktion mit expliziter Zustimmung. | Keine ungefragte Aktivierung anderer Profile; Testprofil muss ohne eindeutige Gerätekennung ausdrücklich eingeschrieben werden. |
| Provider-EPG | Xtream-Grundversorgung mit Historie früherer Schalterwerte; Service/Wizard/Manager konsistent. Optionale Quellen und .95-Backup-Gate bleiben erhalten. | Mehrere bisherige Tests erwarten noch abschaltbare Grundversorgung und sind im Gegenlauf rot; Kontraktabgleich offen. |
| XMLTV-Bilder | Lokale quellen-/kanal-/ereignis-/revisionsgebundene Suche, vierte manuelle Quelle, erneute Suche, ausdrücklicher Save mit atomarem Commit/Readback. XMLTV-Alternativen bleiben bei TMDB-Ausfall erlaubt; XMLTV-AUS widerruft Anzeigezulassung, nicht Dateien. | Gezielte Suche-/Save-Tests grün; im anschließenden Rendering besteht ein bestätigter NameError. Die Gesamtbildfunktion ist damit noch nicht fertig. Reale Android-Anzeige offen. |
| Mini-EPG-Zuweisung | Gemeinsamer Controller mit echten Grid-/Mini-Adaptern; Lang-OK nur auf tatsächlicher Senderzeile, Kontext-Fallback, RAM-Vorschau, Save/Readback, vollständige Abbruchrückkehr. | Physische Fernbedienung offen; ein bisheriger Kontextmenütest erwartet weiterhin sofort „Extras“. |
| Speicher/Logos | Zentraler Dialog, dynamisch 32 MiB und 64/128/256 optional; reale Reserven bleiben. Explizite selektive Bereinigung nur temporärer Derivate. PNG/JPEG-Logoauswahl lokal/SMB mit Vorschau/Bestätigung, atomarer Override je Profil/Konto/SID, einzelnes Reset, gemeinsamer Resolver auch nach Position 512. | Tatsächliche Android-Volumes, SMB, Bilddarstellung und Neustart offen. |
| Cinematic Hero | Nach eindeutiger Identität begrenzte TMDB-images-Abfrage, bis fünf sichere breite Backdrops, Ranking nach Format/Größe/Sprache/Bewertung/Stimmen, bisherige Grafik als Fallback. | Ein integrierter uncached-Bildpipeline-Test ist in CI noch FAIL (`FETCH_FAILED` statt `LOCAL_IMAGE_READY`); Gesamtpipeline deshalb nicht als vollständig repariert melden. |

## 3. Subagenten und Zusammenführung

Alle vier Subagenten waren bei der Konsolidierung abgeschlossen. **Kein laufender Subagent wurde unterbrochen.** Es wurde dafür kein neuer Branch angelegt.

| Subagent | Abgeschlossene Teilaufträge | Gemeldete Prüfungen |
|---|---|---|
| `mini_mapping` | Gemeinsamer Zuordnungscontroller, Grid-/Mini-Adapter, RAM-Vorschau/Abbruch, source-qualified Save/Readback; anschließend .96-Quell-/Paketprüfungen und historische .95-Verifikation. | 99 Mapping-/EPG-/Navigationsprüfungen PASS; Paket-Scaffold geprüft, finale Erzeugung anschließend durch Root. |
| `storage_logo` | Cache-/Speicherdialog, 32-MiB-Standard, Schutz manueller Bilder, Logoeditor und Resolver in Guide/Details/Widgets. | 173 fokussierte Speicher-/Logo-/Guide-Regressionsprüfungen PASS auf damaligem Teilstand. |
| `cinematic_images` | Cinematic-Ranking und bestehende Kandidatenintegration; anschließend Provider-EPG-Baseline inklusive Historie, Wizard/Wiederaufnahme und native Testvorbereitung. | 120 Bild-/Matchingprüfungen sowie 260 Provider-/EPG-/Wizardprüfungen PASS auf jeweiligem Teilstand. |
| `review96` | Unabhängige lesende Gesamtprüfung des Laufzeitcodes. Fünf wichtige Befunde mit echten Host-Reproduktionen. | 73 PASS / 1 FAIL während parallel laufender Korrektur; nicht als endgültiger grüner Gesamtstand bewertet. |
| Root | Gruppen, native Settings-Gesundheit, Source-Hub, XMLTV-Manager und Cache-Revisionsprüfung, Live-/Dialog-Hooks, Reviewkorrekturen, Build, Integration und Dokumentation. | Aktuelle Gegenläufe siehe unten. |

Die Teilaufträge wurden direkt im **selben Worktree und Branch** bearbeitet, nicht in parallelen Produktbranches. Die Subagenten haben keine eigenen Commits oder Merges erzeugt. Root hat die gemeinsamen Änderungen committed. Dateiabgleich, AST-/Schnittstellenkontrolle und die aktuellen Integrationstests bestätigen das Vorhandensein aller Teilimplementierungen. Insbesondere sind Cinematic-Enrichment **und** neue Quellenprüfung in `programme_candidates85.py` gemeinsam erhalten; Grid-Mapping, Mini-Adapter und Logoanbindung liegen in getrennten, erhaltenen Komponenten.

**Kein verlorener Teilauftrag oder versehentlich überschriebener Agentencode wurde festgestellt.** Das ersetzt keine grüne Gesamtsuite: die untenstehenden Integrations-/Kontraktfehler bleiben offen.

## 4. Unabhängige Reviewbefunde

Alle fünf Befunde wurden vor ihrer Korrektur mit einem fehlschlagenden Test nachgewiesen:

1. Automatische externe Freigaben auf normalen frischen Profilen: entfernt; vorhandene Entscheidungen bleiben.
2. XMLTV→TMDB und XMLTV→Ausblenden→Automatisch: Ereignis-/Werkrecord korrekt wechseln, Epochs monoton.
3. Logo-Overrides nach Eingabezeile 512: keine stille Eingabekappung mehr.
4. XMLTV-AUS trotz Cache: Zulassung und Cache-Scope berücksichtigen den Schalter.
5. Manuelles XMLTV-Bild trotz geänderter Faktenrevision: erneute Workerprüfung, alte Proofs für GUI-Zulassung widerrufen, frische Kandidaten separat verifizieren.

Die gezielten Gegenläufe dieser Korrekturen sind grün. Ein neuer unabhängiger Gesamt-Review nach allen letzten Änderungen wurde nicht behauptet. Der Reviewer nahm Android, echte Fernbedienung, SMB, Neustart, endgültige Paketierung und Gesamtsuite ausdrücklich von seiner Bewertung aus; diese Punkte bleiben eigene Gates.

## 5. Tatsächlich ausgeführte Tests

Teiltests überschneiden sich; ihre Zahlen werden **nicht zu einer erfundenen Gesamtzahl addiert**.

| Lauf | Quellstand/Art | Ergebnis |
|---|---|---|
| Konsolidierte gezielte Suite | Code `98bc3b16`; alle 87 neuen .96-Funktionstests plus .95-Gate/Profiltests, Preplay, Navigation und Edge-Regressionen | **176 PASS**, 11,860 s |
| Aktuelle Paket-/Vertragsprüfungen | Code `98bc3b16`; reproduzierbarer Build, CRC, alle Quellbytes, unbekannte Deltas, unveränderte Kanäle/Fallbacks | **8 PASS**, 8,642 s |
| Weiterer GUI-Gegenlauf | Code `98bc3b16`; Overlay, Infobar, Mini-Flicker, Navigation, Icons | **83 PASS / 1 FAIL** aus 84, 3,428 s |
| Gesamter erster unittest-Lauf | **Älterer** .96-Snapshot `812ebc86`; temporärer Klon mit 227 bytegeprüften historischen Testeingaben | **4.110 ausgeführt; 37 Failure-/152 Error-Einträge**, 1.046,148 s. Kein grüner Gesamtnachweis. |
| Gesamter pytest-Gegenlauf | Konsolidierter Code `98bc3b16`; gleicher isolierter historischer Kontext | **4.110 PASS / 13 FAIL**, insgesamt 4.123 Tests, vier Warnungen, 1.107,79 s. [Vollständige bereinigte Fehlerliste](test-builds/02996/PYTEST_98bc3b16_FEHLERLISTE.txt). Kein grüner Gesamtnachweis. |
| Kompilierung/Sprachen | Aktueller Laufzeitcode und 17 PO-Kataloge | Kompilierung PASS, PO-Validierung **17/17 PASS**; vorhandener Vendor-SyntaxWarning ist kein Android-Nachweis. |
| GitHub CI | Pull Request #471, Code `98bc3b16` | **7 Workflows SUCCESS / 4 FAILURE / 6 noch IN_PROGRESS** zum angegebenen Zeitpunkt; Gesamt-CI nicht grün. Native Unterjobs getrennt siehe unten. |
| Native Kodi 720p/1080p | Exaktes .96-ZIP, Linux-Kodi-CI tatsächlich ausgeführt | **PASS in beiden Auflösungen**, Linux-Kodi **21.2**: Provider-Baseline/Legacy-Historie, optionale Quellen erhalten, echtes Mappingdialog-RAM-Preview/Abbrechen mit synthetischem Mini-Parent, Fokus und unveränderte Quelldaten. [CI-Lauf](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43829247789). **Kein Android-/Langpress-PASS**. |
| Physisches Android/Kodi 21.3 RK3528 | Keine echte Geräteprüfung durch Codex | **ANDROID_NOT_TESTED** |

Der erste Gesamtlauf hat unter anderem 129 Importfehler durch die zu frühe vollständige Widget-/Logoabhängigkeit, historische Veröffentlichungserwartungen und weitere Fixture-/Kontraktabweichungen sichtbar gemacht. Die frühe Live-Abhängigkeit und mehrere Baselines sind anschließend korrigiert und gezielt gegengeprüft. **Es wird nicht behauptet, dass damit alle 189 Einträge behoben sind.** [Bereinigte Fehlerliste des ersten Snapshots](test-builds/02996/HOST_UNITTEST_812ebc86_FEHLERLISTE.txt) enthält ausschließlich Testnamen, keine privaten Rohlogs.

Bekannter aktueller GUI-FAIL: `test_xcmate_kodi21_overlay.OverlayLifecycleTests.test_dpad_menu_back_and_visible_focus_textures` erwartet nach Kontextmenü sofort `mode='extras'`; .96 hält die Senderliste für die neue EPG-Zuweisung/Context-Auswahl. Dieser Erwartungs-/Verhaltensabgleich bleibt ausdrücklich offen.

### Die 13 aktuellen Fehlfälle

- 1 Kontextmenü-/Extras-Erwartung; 3 Provider-Baseline-/Fokus-Erwartungen; 1 bisheriger TMDB-Menülabel-Vertrag. Diese fünf Fälle müssen gegen den neuen .96-Vertrag geprüft werden, ohne fehlende Funktionen durch bloß geänderte Assertions zu verdecken.
- 1 echte UI-Regelverletzung: neuer nativer Auswahldialog in `setup_window.py:265` ist im Icon-/Dekorationstest nicht korrekt eingebunden.
- 1 TMDB-Requestzählung erwartet zwei statt jetzt drei Anfragen; 4 TMDB-/Programme56-Fälle laufen in `StopIteration` bei vorbereiteten Antworten. Die zusätzliche Cinematic-images-Abfrage ist dabei zu untersuchen; die bisherigen Bild-/Persistenzprüfungen bleiben verbindlich.
- 1 integrierte Bildpipeline meldet `FETCH_FAILED` statt `LOCAL_IMAGE_READY`.
- **1 bestätigter Laufzeitfehler:** `event_art81.py:18`, `rank()`, ruft `setting_bool` ohne Definition auf. Im Root-Abgleich ist hier ein fehlerhafter Quellenschaltercheck in die Rangfunktion gelangt. Das ist ein echter offener Fehler, nicht nur ein veralteter Test. Die Zulassungsprüfung gehört in `allowed()`; das numerische Ranking muss erhalten bleiben.

Damit ist die Zusammensetzung der Teilaufträge nachweisbar, aber die vollständige Bildreparatur noch nicht abgeschlossen. Gemäß dem Folgeauftrag wurden die neuen Gegenlaufbefunde dokumentiert und keine zusätzliche Reparaturrunde begonnen.

Bestätigte CI-Fehler des aktuellen Codes:

- [.68-Review](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43829248053): `test_uncached_sqlite_event_reaches_token_matching_valid_png_and_exact_status` → `FETCH_FAILED` statt `LOCAL_IMAGE_READY`. Ursache im integrierten Lauf noch offen; nicht als bloß veraltete Testerwartung abtun.
- [.69-Review](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43829247786): drei Provider58-Tests zu abschaltbarer Grundversorgung/alter Startfokussierung FAIL. Die .96-Baseline ist absichtlich anders, dennoch muss der vollständige Kontraktabgleich erfolgen.
- [.70-Review](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43829248113) bestätigt denselben uncached-Bildpipeline-FAIL. Kein grünes Gesamt-CI behauptet.

Weitere native Ergebnisse auf dem PR-Head:

- [Exaktes ZIP / Clock-Widget-Vertrag](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43829248070): **720p und 1080p PASS**, tatsächliches Linux-Kodi. Kein Android-PASS.
- [Nativer vollständiger Home-Gegenlauf](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43829247861): `native-media77` PASS, aber **Home 720p und 1080p FAIL**. Der Probe-Einstieg `Files.GetDirectory(...fixture59=seed...)` bricht mit JSON-RPC `-32602 / Invalid params` ab. Die genaue Plugin-/Seed-Ursache ist offen; aus diesem Lauf folgen kein erfolgreicher Hero-/Receiver-/Detail-Playback-Nachweis und keine Hardwarediagnose.
- Der Workflowname „Publish GS Media Kodi updates“ ist kein Veröffentlichungsbeleg: Bei diesem Pull-Request wird geprüft/gebaut; der Veröffentlichungsschritt verlangt ausdrücklich Push nach main und Freigabegate. Kein solcher Push/Merge wurde ausgeführt.

## 6. Commit- und Arbeitsumgebungsstatus

Alle bisher implementierten Laufzeit-, Test-, Harness- und Buildänderungen sind in `812ebc86` und `98bc3b16` committed und auf dem oben genannten Entwicklungsbranch hochgeladen. **Keine uncommitted Produktcodeänderung.** Bericht und Ergebnisanhänge werden als separater Dokumentationscommit auf demselben Branch gesichert. Ausschließlich ein lokales `.superpowers/sdd/xcmate96/progress.md`-Arbeitsprotokoll bleibt untracked; es ist kein Produktcode und kein Bestandteil des ZIP. Temporäre Testlogs liegen außerhalb des Repositorys unter `/tmp`; keine privaten Kodi-Rohlogs werden veröffentlicht.

Der Bericht wird separat committed. Die maßgebliche ausführbare Quelle bleibt `98bc3b16`; ein reiner Dokumentationscommit ist kein neuer getesteter Codebuild. Main, Pilot, regulär, NeoDark3, Installer und Box A wurden nicht geändert.

## 7. Vollständiges .96-Paket

**Vorhanden: vollständiges installierbares Review-ZIP, noch kein abgenommener Release Candidate.**

- [ZIP, exakt auf Code `98bc3b16`](https://github.com/artattakk-creator/kodi-noodleprivate/raw/98bc3b16e65b45522f3e75ac5002cbdeb14189e2/docs/XCMate/test-builds/02996/plugin.video.xtreammate-0.1.29.96.zip)
- [SHA256-Datei](https://github.com/artattakk-creator/kodi-noodleprivate/blob/98bc3b16e65b45522f3e75ac5002cbdeb14189e2/docs/XCMate/test-builds/02996/plugin.video.xtreammate-0.1.29.96.zip.sha256)
- SHA256: `a9e3b483ae4e961a1a75d6e0fedc44045303e94224d49857fdddb6507919bd47`
- 4.762.310 Bytes, 899 ZIP-Mitglieder; CRC und vollständiger Quellbytevergleich PASS.
- Reviewplan: `repository_staged=NONE`, `repository_released=false`, `merge_or_publish_authorized=false`.
- Aktueller Veröffentlichungsbaum bytegleich zu main `dfea6a72`; .95-Pilot und geschütztes .90-Fallback unverändert geprüft.

## 8. Offen, blockiert und nächste Freigabegates

1. Bestätigten `NameError` im XMLTV-Bildranking korrigieren und integrierte uncached-Bildpipeline (`FETCH_FAILED`) analysieren; anschließend alle 13 Fehlfälle prüfen. Noch kein Pipeline-Gesamt-PASS.
2. Kontextmenü- und Provider-Baseline-Erwartungen mit .96-Vertrag abgleichen; verbleibende Gesamtlauf-/CI-Fehler vollständig auswerten. Aktuelle Änderungen sind deshalb **nicht mergebereit**.
3. Vollständigen grünen Host-/CI-Gegenlauf erreichen und weitere native Widget-/Player-Ergebnisse auswerten. Die bereits grünen nativen EPG-Prüfungen ersetzen diese Gesamtgates nicht.
4. Reale Settings-Ladeursache auf der betroffenen Box erheben. Ist keine geprüfte Settings-Sicherung vorhanden, bleibt Reparatur bewusst BLOCKED statt Zugangsdaten durch Defaults zu verlieren.
5. Echte Android-Abnahme: Gruppenwechsel und Senderwiedergabe zuerst; danach lokale EPG-/Bildsynchronität, XMLTV/TMDB/TVMaze, Token-/Schalterpersistenz, Mini-Lang-OK/kurzes OK/Abbruch/Save/Reboot, sechs Logoansichten, SMB, echte Speicherreserven, Widgets und kontextuelle Player-Rückkehr.

Alle Gerätegates stehen in [ANDROID_ABNAHME_02996_DE.md](ANDROID_ABNAHME_02996_DE.md) auf **ANDROID_NOT_TESTED**. Kein Gerät wurde automatisch aktualisiert. Es gibt keine Merge- oder Veröffentlichungsfreigabe.

## 9. Festgehaltene Entscheidungen

- Der bestehende detaillierte Implementierungsauftrag galt als Arbeitsgrundlage; keine neue Design-/Freigaberunde und kein Neustart der Planung.
- Ohne eindeutige Gerätekennung wird die bereits erlaubte Testkonfiguration nur nach ausdrücklicher Aktion auf diesem Profil angewandt. Andernfalls könnten fremde Installationen ungefragt externe Quellen aktivieren.
- Der neue Provider-Baseline-Vertrag hat Vorrang vor alten Opt-out-Erwartungen; alte Werte bleiben als Historie erhalten. Rote Kontrakttests bleiben sichtbar, bis der Abgleich vollständig geprüft ist.
- Beschädigte Einstellungen ohne geprüfte Wiederherstellungskopie bleiben BLOCKED; ein geratener Neuaufbau könnte Zugangsdaten verlieren.
- Native Linux-Prüfungen und physisches Android bleiben strikt getrennt. Kein vorgetäuschter Geräte-PASS.
