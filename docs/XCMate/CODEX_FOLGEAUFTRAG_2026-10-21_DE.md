> **Aktueller Einstieg (21.10.2026):** [Zentrale Roadmap](ROADMAP_ZENTRAL_DE.md) und [vollständige Issue-Integrationsmatrix](ISSUE_INTEGRATIONSMATRIX_DE.md). Produktiv **0.1.29.6**, Testkandidaten **0.1.29.7 / 0.1.30.1**, primäres Gerät **Kodi 21.2 / ARM32**. Die folgenden früheren Statusangaben bleiben unverändert als Historie; aktuelle Code-, CI- und Gerätebelege stehen in der zentralen Roadmap. Kein neuer Merge/Release freigegeben.

> **AKTUELLER VERÖFFENTLICHUNGSSTAND – 21.10.2026:** **XCMate 0.1.29.6 ist mit ausdrücklicher Nutzerfreigabe über das reguläre GS Media Repository veröffentlicht.** [PR #68](https://github.com/artattakk-creator/kodi-noodleprivate/pull/68) gemergt (`17f5f634e8d5ac74310b7bed95b5636664f92456`); [Publish 39646892896](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39646892896) SUCCESS. Produktiver `addons.xml`-Katalog listet 0.1.29.6, Index-MD5 geprüft; ZIP 389853 Bytes, SHA-256 `f8188f156b8d43d741706813ba6e9946d7f2be66b035e4977dadb32464afe40e`. PR-CI und Publish-CI jeweils **521/521 Tests bestanden**. **Android-Abnahme von 0.1.29.6 bleibt NOT_RUN; #67 bleibt offen.** Das Geräte-Log von 0.1.29.5 belegt Directory-Fehler und verweigerte Fensteraktivierung wegen aktiver modaler Dialoge; 0.1.29.6 korrigiert den gemeinsamen Startübergang und bewahrt Dedup/Live-Remote. [Ursachenanalyse und Android-Testanleitung](HOTFIX_0296_FENSTERSTART_DE.md). **0.1.29.4-Backup behalten; 0.1.29.5 wegen negativer Geräteabnahme nicht als stabil empfehlen.** PR #50/0.1.30 bleibt separat; keine unfertigen 0.1.30.1-Arbeiten veröffentlicht. Die folgenden älteren Versionsangaben sind historische Snapshots.

> **RELEASE-KORREKTUR 21.10.2026:** Der Hotfix **0.1.29.5 aus PR #61 ist inzwischen in `main` gemergt und über das reguläre Kodi-Repository veröffentlicht** (Workflow [39639332756](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39639332756) SUCCESS). Vor neuen Arbeiten den aktuellen `main`-Stand verwenden; **#58/#59/#60 nicht blind erneut implementieren**, sondern realen Android-Gerätetest von 0.1.29.5 abwarten. 0.1.29.4 als Rollback erhalten, #50/0.1.30 weiter Draft. Dieser Hinweis supersediert die zeitlichen Basisangaben im ursprünglichen Folgeauftrag.

# XCMate – Codex-Folgeauftrag / verbindliche Übergabe 21.10.2026

**VOR JEDER CODE-ÄNDERUNG:** Lies [Projektstatus / Übergabe](PROJEKTSTATUS_UEBERGABE_2026-10-21_DE.md), sämtliche Issues **#57, #58, #59, #60, #62, #63, #64** samt Kommentarverlauf, sowie Draft-PR **#50** und den neuesten `main`-Stand. Stelle zunächst fest, was Codex bereits umgesetzt hat und was noch offen ist. Die heute dokumentierten Issue-Inhalte sind verbindlich; nicht automatisch jeden Zukunftswunsch in 0.1.30 hineinimplementieren.

## Unveränderliche Ausgangsbasis
- Repo: https://github.com/artattakk-creator/kodi-noodleprivate
- Add-on: `plugin.video.xtreammate`; Name XCMate.
- **0.1.29.4 ist per #55 gemergt und über GS Media Repository 1.7.0 regulär veröffentlicht**. Auf der Android-Box installiert und per EZ Maintenance+ gesichert.
- **0.1.30 Draft PR #50** `feat/xcmate-space-premium-installer`: 98 Space-Premium-Originalbilder, separater Theme-Installer, frühere CI-Tests; **nicht gemergt**, Android-Theme-Abnahme ausstehend. Kein Zurückfallen hinter die 0.1.29.4-Korrekturen.
- Keine Konten, Profile, Lieblingssender, EPG-Mappings, Downloads, Resume-Daten, Startkanal, Kodi-Skin-Konfiguration oder fremde Add-ons löschen/überschreiben.
- Live-IR-Steuerung als funktionierenden Bestand behandeln, Erweiterungen rückwärtskompatibel und opt-in.

## P0: sofort / stabilisieren
1. **#58**: Doppelte Xtream-Kurz-EPG-Sendungen (konkreter ProSieben-Fall 15:06 und 15:07 `Two and a Half Men`), sichere Near-Duplikat-Erkennung, Senderzeilen nur einmal, zwei XMLTV-Feeds/Provider-Fallback und GUI-Thread-Kontrollen.
2. **#59**: Zurück aus EPG/Filme/Serien zur XCMate-Hauptübersicht, nicht Add-on verlassen oder EPG neu laden. Kodi/IR-BINGIE-Regressionstests.
3. **#60**: 288/2.764 XMLTV-zugeordnet; Alias-/HEVC-/HD-/Regionen-Matching verbessern, manuelle Zuordnung, Quellenstatus; WAITING-Provider nicht als fehlend behandeln. Kein pauschaler Reset.
4. Teste diese P0-Korrekturen ggf. als eigenes **0.1.29.5-Draft-Testpaket**, ohne Produktivupdate.

## P1: Programmzeitschrift, Metadaten, Tasten
5. **#57**: Kurz-EPG im Live-TV (lokal/sofort) klar vom **Langzeit-EPG = eigene horizontale XCMate-Programmzeitschrift** trennen. Fixe Senderlogos/-liste, gemeinsame proportionale Zeitachse, EPG-Jetzt-Linie, Details, Suche/Filter, manuelle EPG-Zuordnung durch lang OK/Menütaste, echte Quellenabdeckung.
6. **TMDB** für das **nichtkommerzielle** XCMate als Film-/Serien-/Episoden-Metadatenquelle verwenden; Poster, Szenenbild, Episode, Beschreibung, Cast, Genre, Rating; konservatives Matching, Attribution/Token-Sicherheit. XMLTV/Xtream bleibt authoritative für lineare Sendetermine. Keine TV-Spielfilm-Inhalte kopieren.
7. **Catch-up**: bereits bei Anbieter vorhanden. Bei Xtream `tv_archive` / `tv_archive_duration` in SQLite importieren, M3U-Catch-up-Attribute ggf. ebenfalls; Rückspulsymbol und Archivtage in Senderliste/Guide, Filter; `xtream.catchup_url()` vorhanden, funktioniert erst nach echtem Playback-Test. Vergangene EPG-Events für Archiv berücksichtigen. Kein FFmpeg dafür nötig.
8. **#64**: Universelle Fernbedienung mit frei belegbaren Rot/Grün/Gelb/Blau und allen von Kodi sinnvoll empfangenen Tasten; Ablauf Taste anlernen -> aus Aktionskatalog wählen -> speichern/testen; mehrere Boxen und Fernbedienungsprofile, Import/Export, kontextabhängige Aktionen, native Fallbacks. Altes Live-Mapping nicht beschädigen.
9. **#50**: Diese Korrekturen mit Space-Premium-Theme/Installer-Zweig integrieren, ohne Grafiken oder Theme-Verbraucher zu verlieren; Core- und Theme-ZIP getrennt testen. Nichts mergen ohne Freigabe.

## P2: Aufnahme und Downloads – tatsächliche Funktion statt Platzhalter
10. **#62**: Aufnahme- und Umschalttimer aus EPG: Erinnern, automatisch auf Sender schalten, Aufnahme planen/jetzt aufnehmen, Status/Stop. Nutzer erlaubt gleichzeitige Streams bei seinem Anbieter. **Zentrales Akzeptanzkriterium:** **Sender A im Hintergrund unabhängig aufnehmen, während Sender B über den einzigen Kodi-Player live läuft und nach C gewechselt werden kann.** Player-/IR-Navigation darf Recorderjob nicht abbrechen. USB/HDD/SMB als getestetes Ziel, echtes Android-Backend, Zeit-/Konfliktbehandlung, korrektes Offline-Resultat. `guide_timers.py` erinnert bisher nur; `recordings.py` hängt an FFmpeg CLI; FFmpeg auf Android nicht voraussetzen. Installations-Helper-/Store-Dialog erst nach verifizierter kompatibler Engine; VLC allein keine FFmpeg-CLI. Alternative erlaubte direkte Transportstream-Speicherung prüfen.
11. **#63**: Film-/Episoden-/Staffeldownload auf wählbares dauerhaftes USB/HDD/SMB-Verzeichnis bei berechtigt herunterladbaren DRM-freien Quellen; reale Queue/Retry/Resume soweit technisch möglich, Fortschritt, Speicherprüfung, Neustart, lokale Offline-Wiedergabe; Downloader getrennt von Video-/GUI-Thread.

## Explizite Nichtziele und Qualität
- **#66 Multiview ist ausdrücklich gestrichen und geschlossen.** **KEIN PiP, kein Split-Screen, keine zwei sichtbaren Video-Fenster, keine Multi-Decoder-/Player-Engine und keine Multiview-Fernbedienungsaktionen.** Paralleles Aufnehmen und Ansehen bleibt P2-Aufgabe in #62.
- **#65 X-Wall / weitere Kodi-Oberflächen/Medienquellen** ist ein späterer Ideenparkplatz, **kein aktiver Implementierungsauftrag**.
- Nicht versuchen, alle großen Features erzwungen in 0.1.30 zu stopfen. Rückwärtskompatible, klar abgegrenzte Etappen und Draft-PRs mit echter Testbarkeit wählen.
- Kodi 21.3 / Android + BINGIE/Estuary, ≥2.764 Sender, echte Fernbedienungen, SQLite/WAL-Migration, schwache Netzwerkverbindungen, Speicherrechte und USB-Abzug testen.
- Kein DRM-Bypass, keine geheimen Tokens oder Portalpasswörter in Issues, Builds, GitHub oder Logs.
- CI-Erfolg, Android-Hardwaretest und GitHub-Veröffentlichung immer gesondert ausweisen.

## Gewünschte nächste Codex-Antwort
1. **Issue-Matrix** für #57/#58/#59/#60/#62/#63/#64 plus #50: bereits vorhanden, fehlt, betroffene Module, PR, Abnahmekriterien.
2. Welche bestehenden Branches auf welchen Commit basieren und wie die 0.1.29.4-Basis **ohne Regression** in den 0.1.30-Entwicklungszweig kommt.
3. Konkrete **Implementierungsreihenfolge P0 -> P1 -> P2**, inklusive getrenntem Aufnahme-/Player-Backend ohne Multiview.
4. Danach die priorisierten Änderungen implementieren, Regressionstests durchführen, Test-ZIPs/SHA-256, Changelog und Android-Checkliste liefern. Fehlende Geräteproben ausdrücklich `NOT_RUN` markieren.
5. **Keine eigenmächtigen Merges, Releases, Produktivindex-Updates oder Android-Geräteänderungen.** Vor Veröffentlichungen ausdrückliche Nutzerfreigabe einholen.
