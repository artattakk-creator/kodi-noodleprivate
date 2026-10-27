# XCMate .44 – Issue-/Gate-Abnahmematrix

Stand27.10.2026, Inventar113 offene Issues in OPEN_ISSUES_02944.json; elf alte offene PRs nur inventarisiert, keiner übernommen oder gemergt. Owner Implementierung Codex, echte Geräteabnahme/Freigabe Nutzer Box B. Historische .43-Ergebnisse bleiben unangetastet. **Alle neuen .44-Androidgates NOT_TESTED; null neu bestätigte Android-PASS.** „HOST_PASS“ gilt nur für konkret ausgeführte Testfixtures laut Testbericht.

| Issues | Entwicklung .44 / Status | Gerätegate / verbleibend |
|---|---|---|
| #233 | Kumulativer Draft mit Gates0–5, Schutz/Tests/ZIP; **PARTIAL, kein Gesamtsignoff** | A–H63 + neue Gates; keine Merge-/Releasefreigabe |
| #231 | HOST_PASS P0: additive Veröffentlichung, kein sparse-envelope-DELETE/Shortcache-Replace; explizites WAL-Backup vor Legacywrites, read-only Diagnose | EPGSAFE01–07; echter Android-Verlustpfad unbewiesen; Backup/Bestand zuerst, davor Refresh BLOCKED |
| #161 | **PARTIAL**: Source-ID-Archiv, Intervalllücken, atomarer Portalrefresh, gemeinsame DB,7T | Vollständige quellensichere manuelle Reader-/Chooserarchitektur #98, ARM32-Kapazität und gesamter HUB01–11 bleiben FOLLOW_UP/BLOCKED; keine Mappings migriert |
| #232 | HOST_PASS −7-Tage-Guard/DST/echter Historyindikator | G2/EPGSAFE06; nur reale verfügbare Historie |
| #229/#230 | HOST_PASS begrenzte indexgestützte SQLpfade, revisioniertes lokales Prewarm, Dynamic-Art-Sharing, genaue Klickziele | F1–F8/WIDGET44; reale BINGIE-Render-/KaltWarm-/Artkette noch offen, kein Gesamtwidget-PASS |
| #206/#207 | **BLOCKED/PARTIAL**: Backenddaten/Props/Art/Klicktests; fremde Skin-/Shortcutdateien unangetastet | 50%-Logos/fokussiertes EPG/reale Skin-Build-Integration erst prüfen; Adapter nur ausdrücklich genehmigt |
| #227 | **PARTIAL/HOST_PASS** konkrete PID statt alle aktiven Portale, Reasoncodes, einmaliger begrenzter transienter Retry, Intent-Fehlerabschluss | D8/SEARCHPLAY44Film+Episode; genaue Android-Unterursache nicht festgestellt, Erfolg nicht behauptet |
| #201/#190/#140/#127/#159 | Bestand/Hostregression Suche/IndexErrorLastGood/Tabs/Genre, kein Maskenredesign | D1–D7 unverändert erneut prüfen; .43-PASS nur historisch |
| #228/#151/#111 | **PARTIAL/HOST_PASS** sichtbarer getrennter Bild-/Metadateneinstieg, Kandidat ohne Bild möglich, Quell-/Fehlercodes, bewusste Speicherung | E1–E11/COVER44; echter Aladdin/Token/Netz/Decoder/NachNeustart offen; Thumbnails/manuelle Metaindexierung/EPG-Bilder Folgeumfang |
| #223 | HOST_PASS sichtbare Contentgeneration/Diffsetter,200identische Renders ohne Zeilenschreiben | A3/NAV44; Framebeweis auf Android fehlt |
| #224 | HOST_PASS separate Rail-Captions vor Collapse verbergen/löschen | B4/B5/NAV44; keine Geistertexte real prüfen |
| #225/#226 | HOST_PASS Kategorienfokus/OK/Zwei-Rechts/extraLinks, gleiche Hintergrundseite behält Items, Rückwege erhalten | C1–C3/NAV44Film+Serie + lange Kataloge, echtes IR |
| #100 | HOST_PASS ausschließlich Mikrozeilendarstellung, Streamdatenfile bytegleich | INFOMICRO01–08, B2/H2; tatsächliche Fonts/720p/1080p/Trackwerte visuell NOT_TESTED |
| #220 | Bestand: rechte Mini-Fokus-/NowFuture-Datei bytegleich; alte Regressionen aktiv | A4/A5 erneut; .43-Teil-PASS bleibt historisch |
| #203/#216/#202 | Schutz: vier .42-Dateien und Medienprogress/autoplay/state/sequence bytegleich; keine Playerengineänderung | H220/20 mit bestehendem EIN, C4–C8, H3–H8 erneut; keine OFF-/Box-A-Proben |
| #221/#194 | Historie39P/19F/5NT vollständig übernommen, neue Gates separat | Kein Issue-Close oder pauschaler Beta-/Android-PASS |

Die restlichen Issues werden durch diesen Draft weder erledigt noch geschlossen. Insbesondere #98 vollständiger manueller Quellchooser, #64 Fernbedienungslernen, #106 externe Migration, #63/#135/#136 Downloads/USB/SMB, #126 Aufnahmen, TV-Favoriten bleiben außerhalb dieses Patchumfangs. Vorhandene Funktionen erhalten, keine neuen Speicher-/Löschtests. Der vollständige offene Snapshot ist ein Inventar, keine Neutriage jeder historischen Teilanforderung.

Für jedes geänderte Runtime-Modul enthält DATEIKATALOG_02944.json Hash/Status/Zuordnung; URSACHENANALYSE_02944_DE.md beschreibt Mechanismen, Grenzen und Rückfall. Alle1582 alten Methoden bleiben im Testinventar; NEUE_TESTS_02944.json listet neue Fälle. Fremdskin-/Hub-Grenzen verhindern eine Aussage „gesamte .44 vollständig bestanden“.
