# XCMate – Issue-Triage nach Android-Abnahme 0.1.29.35 (25.10.2026)

**Repository:** https://github.com/artattakk-creator/kodi-noodleprivate. **Exakt zum Prüfzeitpunkt:** **50 offene Issues**, **11 offene Pull Requests**, `main` Add-on-Version **0.1.29.35**. Diese Liste ist ein **prüfbarer Snapshot**, keine Behauptung, dass historische Fehler noch auf `.35` reproduzierbar sind. `PERF-03` wurde nachträglich zum **15/15 PASS** bestätigt. [Finale Messungen](ANDROID_ABNAHME_02935_LOGFORENSIK_FINAL_20261025_DE.md) · [Nächster Codex-Auftrag](CODEX_AUFTRAG_02936_PERF_OSD_SEARCH_BACKLOG_20261025_DE.md).

## Regel: Backlog reduzieren durch Abschluss der Anforderungen, nicht durch künstliches Schließen

1. Jeder PR nennt **welche Issue-Akzeptanzkriterien tatsächlich implementiert wurden** und **welche nach Android-Gate noch offen** sind. Für vollständig erfüllte Issues nach realer Freigabe gezielt `Closes #N`; ansonsten kommentieren `Teil-PASS / weiterhin offen` und im neuen Folge-Issue nur restlichen prüfbaren Scope erfassen.
2. **Historische Fehlerversionen sind keine .35-Gegenwartsfehler.** Beispiel: #88 Startgruppen-Default/Guide-Senderfokus nun PASS, doch Sendungsdetails/Logos können noch offen sein; #140 schnelle Sendernamen in .35, aber Programmtitel 28 Sekunden; #87 massiver Codec-Sturm nur alter Logabschnitt; #97 wurde bereits geschlossen und wird nicht doppelt als neues offenes Issue gezählt.
3. **Nicht** PRs nur wegen gleicher Versionsziffer oder ähnlich klingender Funktion mergen. `main` und reale Installationsversion immer neu prüfen; 15 funktionale PASS schützen. Alte Drafts auf veralteten Basen nur als Referenz übernehmen.
4. Ziel ist **in kleinen Mergezyklen messbar weniger offene funktionsfähige Fehler**, ohne ungeprüfte Funktionalität, Downgrade, Löschen von Portal-/EPG-/Artwork-Daten oder kosmetische Massen-Abschlüsse.

## Bestandsaufteilung – alle 50 offenen Issues, genau einmal zugeordnet

### A · Nächster Stabilisierungskandidat (.36 vorläufig)
Messbare Programm-/Start-/OSD-Latenz und Stop/Home-Directory: zuerst echte Root Cause, fokussierter Fix; #91 nur bei tatsächlich gemessenem SQLite/Cache-Engpass.

- [#140](https://github.com/artattakk-creator/kodi-noodleprivate/issues/140)
- [#127](https://github.com/artattakk-creator/kodi-noodleprivate/issues/127)
- [#120](https://github.com/artattakk-creator/kodi-noodleprivate/issues/120)
- [#17](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17)
- [#35](https://github.com/artattakk-creator/kodi-noodleprivate/issues/35)
- [#75](https://github.com/artattakk-creator/kodi-noodleprivate/issues/75)
- [#91](https://github.com/artattakk-creator/kodi-noodleprivate/issues/91)

### B · Kleine optionale Einzelaufgaben nach Scope-Gate
Genresuche, gezielter Poster-Retry und kleine EPG-Qualitäts-/Dublettendiagnostik. Keine große DB-Migration oder Senderkonfliktfusion im Stabilisierungskandidaten. Wenn isoliert nicht sicher: unmittelbar eigene Folge-Drafts.

- [#159](https://github.com/artattakk-creator/kodi-noodleprivate/issues/159)
- [#111](https://github.com/artattakk-creator/kodi-noodleprivate/issues/111)
- [#60](https://github.com/artattakk-creator/kodi-noodleprivate/issues/60)
- [#58](https://github.com/artattakk-creator/kodi-noodleprivate/issues/58)

### C · Nächste zugesagte TV-UI-Phasen
Mini-EPG als dauerhaft zweispaltige Sender-/Programmliste, Links→Mini→GRUPPEN→bildschirmhohe Rail; danach echte Live-/VOD-Player-Buttons. Rich Detail/Art/Themes nur in zugehörigen Design-Phasen und nach visueller Geräteabnahme.

- [#94](https://github.com/artattakk-creator/kodi-noodleprivate/issues/94)
- [#95](https://github.com/artattakk-creator/kodi-noodleprivate/issues/95)
- [#150](https://github.com/artattakk-creator/kodi-noodleprivate/issues/150)
- [#100](https://github.com/artattakk-creator/kodi-noodleprivate/issues/100)
- [#79](https://github.com/artattakk-creator/kodi-noodleprivate/issues/79)
- [#123](https://github.com/artattakk-creator/kodi-noodleprivate/issues/123)
- [#74](https://github.com/artattakk-creator/kodi-noodleprivate/issues/74)
- [#31](https://github.com/artattakk-creator/kodi-noodleprivate/issues/31)
- [#27](https://github.com/artattakk-creator/kodi-noodleprivate/issues/27)
- [#14](https://github.com/artattakk-creator/kodi-noodleprivate/issues/14)

### D · EPG-Hub, Zuordnungen, Replay-Vorbereitung
Zentrale Quellen-/Sender-IDs, 7 Tage Geschichte soweit belegt, zeitliche Lücken, lokale Snapshot-Indexe und manuelle Source-Mappings; keine Catch-up-Scheinfunktion. #88 Startgruppen-Teil in .35 auf Android PASS, andere Rich-Details/EPG-Teile bleiben eigenständig.

- [#161](https://github.com/artattakk-creator/kodi-noodleprivate/issues/161)
- [#98](https://github.com/artattakk-creator/kodi-noodleprivate/issues/98)
- [#88](https://github.com/artattakk-creator/kodi-noodleprivate/issues/88)
- [#34](https://github.com/artattakk-creator/kodi-noodleprivate/issues/34)
- [#99](https://github.com/artattakk-creator/kodi-noodleprivate/issues/99)

### E · Artwork, Queue, Speicherung, Space Premium
Queue-/Storage-Budgets, sichere Dateiverschiebung, automatischer Refresh/GC, Artwork-Quellenwahl und Premium-Fokus als eigener Daten-/Grafik-Workstream. #111 nur lokal kleiner Retry, kein Sammelreset.

- [#90](https://github.com/artattakk-creator/kodi-noodleprivate/issues/90)
- [#69](https://github.com/artattakk-creator/kodi-noodleprivate/issues/69)
- [#106](https://github.com/artattakk-creator/kodi-noodleprivate/issues/106)
- [#108](https://github.com/artattakk-creator/kodi-noodleprivate/issues/108)
- [#115](https://github.com/artattakk-creator/kodi-noodleprivate/issues/115)
- [#151](https://github.com/artattakk-creator/kodi-noodleprivate/issues/151)

### F · Aufnahmen, Downloads, Speicherorte
Redirect-/Storage-/SMB-/USB- und Streamaufnahme als eigener integrierter Service-PR mit echten 0-MB-/Ziel-/Platz-/Fehlerfällen, nicht mit EPG-Performance-Fix vermischen.

- [#126](https://github.com/artattakk-creator/kodi-noodleprivate/issues/126)
- [#63](https://github.com/artattakk-creator/kodi-noodleprivate/issues/63)
- [#135](https://github.com/artattakk-creator/kodi-noodleprivate/issues/135)
- [#136](https://github.com/artattakk-creator/kodi-noodleprivate/issues/136)
- [#113](https://github.com/artattakk-creator/kodi-noodleprivate/issues/113)
- [#62](https://github.com/artattakk-creator/kodi-noodleprivate/issues/62)

### G · Katalog, Erststart, Playback-Sonderfälle, Optionen und Compliance
Setup-Assistent, Stream-Stabilität, tatsächliche Film-/Serien-Vollständigkeit und Infinite Scroll (24-Titel-Befund!), IR-Mappings, alter Codec-Sturm, PIN, X-Wall, installierbare Themes/Sprachen, Home-Widgets und Lizenz-Audit. #19 V2-Gate; nicht automatisiert schließen.

- [#43](https://github.com/artattakk-creator/kodi-noodleprivate/issues/43)
- [#107](https://github.com/artattakk-creator/kodi-noodleprivate/issues/107)
- [#102](https://github.com/artattakk-creator/kodi-noodleprivate/issues/102)
- [#64](https://github.com/artattakk-creator/kodi-noodleprivate/issues/64)
- [#87](https://github.com/artattakk-creator/kodi-noodleprivate/issues/87)
- [#71](https://github.com/artattakk-creator/kodi-noodleprivate/issues/71)
- [#65](https://github.com/artattakk-creator/kodi-noodleprivate/issues/65)
- [#30](https://github.com/artattakk-creator/kodi-noodleprivate/issues/30)
- [#29](https://github.com/artattakk-creator/kodi-noodleprivate/issues/29)
- [#26](https://github.com/artattakk-creator/kodi-noodleprivate/issues/26)
- [#19](https://github.com/artattakk-creator/kodi-noodleprivate/issues/19)

### H · Master-Nachverfolgung
Fortlaufende Abnahme-/Issue-Verknüpfung, kein Software-Feature und nicht als erledigt zählen, solange Folgepakete offen.

- [#143](https://github.com/artattakk-creator/kodi-noodleprivate/issues/143)

## Offene PRs – keine davon ist automatisch mergefähig auf aktuellem main

**11 historische/offene PRs im Snapshot**: [#157 Poster-Retry-Dokumentationsentwurf](https://github.com/artattakk-creator/kodi-noodleprivate/pull/157); [#124 alte P0-Analyse](https://github.com/artattakk-creator/kodi-noodleprivate/pull/124); [#117 native Direct-TS-Engine](https://github.com/artattakk-creator/kodi-noodleprivate/pull/117); [#50 alter Space-Premium-Branch](https://github.com/artattakk-creator/kodi-noodleprivate/pull/50); [#78 Artwork-/USB-Migration](https://github.com/artattakk-creator/kodi-noodleprivate/pull/78); [#83 Neon-/Fokus-Design](https://github.com/artattakk-creator/kodi-noodleprivate/pull/83); [#84 früher VOD-OSD](https://github.com/artattakk-creator/kodi-noodleprivate/pull/84); [#77 größere Medienreihen](https://github.com/artattakk-creator/kodi-noodleprivate/pull/77); [#72 frühere Konsolidierung](https://github.com/artattakk-creator/kodi-noodleprivate/pull/72); [#51 GS-Media-Repository-Erweiterung](https://github.com/artattakk-creator/kodi-noodleprivate/pull/51); [#3 TiviMate-Keymap-Vergleich](https://github.com/artattakk-creator/kodi-noodleprivate/pull/3). Ohne vollständigen diff/base/CI/Android-Vergleich **weder mergen noch automatisch schließen**. Erst nach Portierung ins aktuelle kumulative main und Nutzerfreigabe archivierte Drafts bereinigen.

## Verbindliche Phasen und Risiko-Abhängigkeiten

- **Phase 1 – nächster kleiner kumulativer Draft (vorläufig 0.1.29.36):** #140, #120, #17, #35, #75 plus klar nachgewiesene #91/127-Unterpunkte. Optional **höchstens isolierte** #159, #111, #60/#58-Subtasks, sofern nicht Blocker oder DB-Risiko. Ziel: Sekunden statt 28-s-Titelsuche, schneller Startsender/Infobar, korrektes Stop/Home. Hosttests/ZIP/SHA/Draft, **keine eigenmächtige Releasehandlung**.
- **Phase 2 – zugesagte TV-UX nach Stabilisierung:** #95 Mini-EPG **rechte permanente Vorher-Jetzt-Danach-Spalte** sowie #94 volle Höhe Rail **nach** Gruppenebene; #150 später für andere Rubriken. Mit echten IR-Tests auf 720p/1080p.
- **Phase 3 – echte Player-Buttons und VOD-Qualität:** #100/#79, bei Gelegenheit #102 Scrolllimit/Totalzähler und #111 Poster-Fallback, separate Kodi-/Staffel-Autoplay-Regression.
- **Parallel fachlich vorbereitet, in kleinen datensicheren PRs:** EPG-Hub #161 mit #98, #34, #58/#60 und später Catch-up #99; keine ungetestete Großmigration in den UI-PR.
- **Eigenständige Workstreams:** Artwork/USB/Queue, Recorder/Downloads, Erststart/Internationalisierung, Streaming/Codec und Legal. Keine künstliche Schließung aufgrund älterer Host-CI-Zahlen.

**Codex soll nach jedem genehmigten Android-Merge eine Matrix `voll erfüllt / teilweise / weiterhin offen / nicht getestet` mit exakten Belegen im Master-Issue #143 führen.** So wird die 50-Issue-Liste in den folgenden Abnahmen schrittweise wahrheitsgetreu kleiner.
