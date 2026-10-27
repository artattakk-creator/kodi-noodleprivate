# XCMate .44 – Host-Test- und Paketbericht

Stand27.10.2026. **1.652/1.652 Hosttests PASS**, 0 Fehler/0 Fehlschläge in **261,197s**. Alle1.582 bisherigen Methoden plus70neue. Vollständiger unveränderter Lauf: [TESTLOG_02944.txt](TESTLOG_02944.txt); maschinell [TESTERGEBNISSE_02944.json](TESTERGEBNISSE_02944.json). Echte Androidgates sämtlich **NOT_TESTED**. Kein vollständiger Hub-/BINGIE-/Android-Erfolg behauptet.

Codecommit `686705c2eddf24b175332c731d32c205b979d7f7`, Basis `efaaf429b55f6db0e59344d3502de9125bd535ae`. Neue Methoden [NEUE_TESTS_02944.json](NEUE_TESTS_02944.json), Dateihashes/Gates [DATEIKATALOG_02944.json](DATEIKATALOG_02944.json), neun kritische Bytefreezes und fremde WIP-Schutzprüfung [SCHUTZPRUEFUNG_02944.json](SCHUTZPRUEFUNG_02944.json).

## Reproduktion

Sauberes `git archive` dieses Codecommits in einen separaten Scratch entpacken; ausschließlich dort bauen. Python3.12, Pillow und impacket0.13.0/SMB-Testserverabhängigkeiten; lokale HTTP-/SMB-Loopbacktests benötigen erlaubte Netzwerk-Sockets.

```sh
python tools/bootstrap_xtreammate.py
python tools/apply_xtreammate_upgrade.py
python tools/apply_xtreammate_012.py
python tools/apply_xtreammate_015.py
python tools/build_repository.py
python tools/validate_kodi_po.py
python tools/build_xcmate_nav_icons.py --check
python -m compileall -q src
python -m unittest discover -s tests -v
```

Identische Pipeline läuft im unveränderten GitHub-Workflow. Der PR enthält den abschließenden CI-Link/Head/Artefaktabgleich; keine erfundene SUCCESS-Angabe vor Abschluss. Der produktive Publish-Schritt ist nur für Push nach main, bei diesem Draft-PR muss er SKIPPED bleiben.

## Prüfbreite und Aussagegrenzen

- Gate0:24neue Methoden für sparse/0/3Feeds, Quell-ID-Kollisionen, LKG, Cache4,7Kalendertage/DST, Vortage, read-only Diagnose, Busy, Abbruch/ENOSPC, WAL-/Konfigbackup, explicit consent, legacyM3U/STB. Darunter echte zweite-Quellen-Publish-Fehler-Rollbacks und separate Leserverbindungen während der Gesamttransaktion. Kein Gerätedump.
- Gate1:9neue Methoden; 20.005V2-Titel mit realem EXPLAIN-Plan `recent_v2`, keine TEMP-B-TREE-Fullsort; 40Mehrfachgruppen→24eindeutige Titel; echte Portal/SID-Klickziele; gemeinsam validierte Dynamic-Referenzen; TTL/Revisionswechsel. Fremder Skinrenderer und Androidp50/p95 ungeprüft.
- Gate2:8neue Methoden für gewünschtes Konto, transienten Retry und Ablehnung, Memorypause/ungültige Profile, Intent/Rückkehr/Doppelstartschutz. Reale Android-Unterursache offen.
- Gate3:8neue Methoden für geteilten Einstieg, metadatenlose/bildlose Fälle, Opt-in/Token, native Modal-/Abbruch-/Fehlerpfade. Bestehende Quellen-/Bilddecoder-/Security-/Persistenztests weiter aktiv; reale TMDb/Commons/DNS/API-Fälle nicht durch Mocks ersetzt als Android-PASS.
- Gate4:9neue Methoden für Zwei-Rechts-Vertrag, gleiche Hintergrundseite ohne Reset, Sidebar/Fokus, Snapshotcontent und200identische Renderdurchläufe ohne Zeilensetter. Rechte .43Mini-Datei unverändert.
- Gate5:8neue Methoden INFOMICRO-Vertrag,720p/1080p-Geometrie, registrierte Fonts, reale statt erfundene Werte, Unknown/Trackchange/Hide, unveränderte owner-/2s-Datenquelle.
- Schutz:4neue Methoden; alle399 bisherigen Quelldateien vorhanden und nur exakt dokumentierte Deltas, alle1582 alten Testmethoden erhalten,9kritische Quellen und Originalicon/Suchlayout exaktgleich.

Der erste Zwischenlauf hatte15Fehler in1649Tests. Daraus wurden zwei echte Übergangs-/Themefallback-Regressionsfehler korrigiert. Alte Navigationsassertions wurden an den explizit beauftragten neuen OK/Right1/Right2-Vertrag angepasst; Kodi-Modelle um tatsächliches ControlLabel ergänzt; EPG-Testprogramme erhalten echte Zeitintervalle, eine explizite Korrektur verwendet verifizierten Vollfeed statt Kurzcache. Kein alter Testfall entfernt, kein Skip hinzugefügt. Drei zusätzliche Atomizitäts-/Sperrtests führen zum grünen1652erEndlauf. Ein isolierter Teillauf ohne erlaubte Sockets war umgebungsbedingt fehlgeschlagen; voller Endlauf mit Loopbackberechtigung erfolgreich.

Weitere Checks: gettext de/en jeweils1010Kontexte PASS;92gepinnte Navigationstexturen/Lizenz PASS; compileall PASS. Bereits vorhandener SMB-Vendorcode meldet unter Python3.12 eine SyntaxWarning für Escape-Sequenz, keinen Compile-/Testfehler; dieser Vendorcode bleibt unverändert.

## Vorher/Nachher und Lasttest

[WIDGET_PERF_02944.json](WIDGET_PERF_02944.json): derselbe20.005-Titel-V2-Katalog, je5neueReader, gleicher Sharedhost, beide Versionen24Treffer. .43Median **67,683ms**, .44Median **33,439ms**; etwa51% weniger in dieser synthetischen Probe. Kein ARM32-/Kaltstartversprechen und kein Beweis, jeden Android-BUDGET-Fall beseitigt zu haben. Unveränderte .75s/.25s-Grenzen. Queryplan/Mechanismus sind die belastbareren strukturellen Belege.

Volltests enthalten echten XMLTV-Stream **160.005Programme /95.571.948XMLbytes**, persistent303.685.632SQLitebytes, **16,281s** auf diesem Host; anschließender kurzer Updatecache verdrängt keinen Langbestand. Großer realer lokaler HTTP-/JSON-Import, SMB-/Redirect-/Resume- und übrige alte Regressionen bestehen. Keine solchen Last-/Speicherproben auf Box A/B durchgeführt.

## Installationspaket

`plugin.video.xtreammate-0.1.29.44.zip`: **412Dateien /2709640Bytes**.

SHA256:

```text
0497979676b72cf6907ffdb6204920a3f0636dd029c71df17c64847520261fa8
```

CRC, eindeutige relative Pfade, keine Symlinks/Traversal/Tests/private DB/Logs/pycache, alle ZIP-Quelldateien bytegleich, Python-AST und unabhängige deterministische Reproduktion PASS. Nur neues44ZIP+SHA übernommen; main-Index/produziertes43ZIP unverändert. Add-on-ID unverändert `plugin.video.xtreammate`, Python3-Addon für KodiOmega. GitHub-CI muss dieselben Paketbytes erzeugen und wird unabhängig heruntergeladen verglichen.

## Noch gesperrt

[Issue-Matrix](ISSUE_MATRIX_02944_DE.md) und [Ursachenanalyse](URSACHENANALYSE_02944_DE.md): vollständiger quellensicherer Hub/Chooser, exakter Geräte-PortalReadError und BINGIE-Fremdskinrenderer offen; eigene Tokens/reale Quellen/Fonts/Frame-/Stop-/Persistenzbeweise Android-NOT_TESTED. Entsprechend **Draft zur Prüfung, keine vollständige Freigabe**. Erst explizite konsistente EPG-Sicherung, danach Androidplan [ANDROID_ABNAHME_02944_DE.md](ANDROID_ABNAHME_02944_DE.md). Kein Merge/Release/Installieren/Profilreset/Box-A-Eingriff.
