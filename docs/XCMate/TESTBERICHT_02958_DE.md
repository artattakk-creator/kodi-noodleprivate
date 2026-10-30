# XCMate 0.1.29.58 – vollständiger Host-Testbericht

Status: Review-/Diagnosekandidat, P0-Gesamtabnahme NICHT erreicht. #277 und #276 bleiben offen. Kein Merge/Release.

## Ergebnisse des unveränderlichen Build-Standes

- Source-Commit: `6b8c08717e88d4109d994e509c1d77ebfd27e990`. Basis main `cb58e38ff450a56a97178708db193ad0ad8b670f` (.57).
- 2463 Hosttests PASS in 329.688 s; 0 Fehler, 0 Fehlschläge, 0 Skips. Alle 2.418 bisherigen Methoden und Skipbedingungen erhalten; 45 neue Prüfungen. Vollständiger anonymisierter Host-Output: TESTLOG_02958.txt.
- Sauberes git-archive-Build mit gepinnten Bootstrap-/Upgrade-Skripten, Repositorybau, gettext-Validierung beider Sprachen, 92 Navigationsicons/Lizenzen, Python-Compile. Vorhandene ungültige Escape-Sequenz als SyntaxWarning im unveränderten vendorten SMBProtocol.py bleibt ein bekannter Host-Warnhinweis.
- 609 Add-on-Dateien: 594 bisherige Dateien byteidentisch, 12 exakt dokumentierte Source-Deltas, drei additive Module. Keine bestehenden Dateien entfernt. Prüfkatalog/Review-Hooks und SCHUTZPRUEFUNG_02958.json liefern die Einzelwerte.
- Fremde laufende Entwicklungsstände: 62 Prüfsummen unverändert.
- Installations-ZIP: 3167746 Bytes; CRC, Pfadsicherheit, sämtliche Sourcebytes, Python-AST und unabhängiger deterministischer Neuaufbau PASS.
- SHA256: `1ba592c4f4761db4d608784a8a59bfc3ebf41c96b1afc8528b5b7fe9a9286590`.
- Echter isolierter Kodi 21.2/Linux: bestehender Plugin-/Worker-RPC-Vertrag PASS, GUI/Dialog unverändert, kein Playerstart. Synthetische öffentliche Metadatenquelle; KEINE echte Helper-/Provider-/Android-/BINGIE-Pixelabnahme. KODI_HOST_TRANSPORT_02958.json enthält den begrenzten Nachweis.
- GitHub-CI: verpflichtender echter Kodi-Transportjob plus vollständiger Host-/Paketjob; exakten finalen Head-Lauf und Ergebnis im Draft-PR prüfen. Produktionsschritt darf bei PR ausschließlich SKIPPED sein. CI-Artefakt trägt den SHA256 des inneren Installations-ZIPs; der äußere Artefaktcontainer hat einen anderen Hash.

## Neue Prüfungen

Provider: echter Portal-JSON-Save und frischer Reader; Passwort-/Zweitportal-Erhalt; veralteter Dialogzustand; fehlendes Portal, Nicht-Xtream-Schalter, fehlgeschlagener oder nur vorgetäuschter Save; Aktivierung ohne Download/READY; identische und unterschiedliche XMLTV-Adressen; Providerfehler blockiert keine externe Quelle; M3U behält externe XMLTV-Einrichtung; sichtbarer Fokus/gesamter Pfeiltastengraph; 720p/1080p-Koordinaten; Abbruch. Echter Streaming-Import synthetischer XMLTV in die bestehende guide_v1.sqlite mit qualifizierten Provider-/externen Quellen; ausgeschaltete Quelle nicht geladen, alte Daten bleiben.

Widgets: native Film-/Serienausgabe liest keine manuellen Nicht-Provider-Metadaten; manuelle Dateien bleiben erhalten; Provider-Caches statt Ersatzcover; fehlendes kind korrekt normalisiert; Provider-only Asset-Grenze; tatsächlich fehlschlagender programme_helper57.lookup-Stub wird für beide Medienarten nie aufgerufen. Gespeicherte Bindung gegenüber generiertem Consumer und tatsächlichem Home getrennt; fehlender Consumer, versteckter Consumer, falscher Typ/fremdes Portal, ungebundenes Live-Home, bösartige Dateien. Unveränderte gepinnte BINGIE-2.2.3-Include-Definition löst parametrisierte Verbraucher auf; unbekannte Definition bleibt unverifiziert. Keine Skinänderung.

Live-Exit: reproduzierte native Queue-Blockade bleibt als unbestätigter Stop verriegelt; keine Player-/GUI-Abfrage und kein zweiter Stop. Prepare- und Stop-Timeout getrennt; worker_done ersetzt niemals FIFO-ACK; echter später ACK getrennt; gleiche Session-Korrelation, keine privaten Daten; Medien-/gesunder Live-Exit unberührt. Service-Beobachter läuft vor dem bestehenden blocked()-Guard. Das prüft eine sichere Diagnose, ausdrücklich keinen reparierten Rockchip-Decoder.

Bestandsschutz: alle alten Source-Dateien und Testmethoden; genaue Hooks statt pauschaler Freigaben; Routing-AST außerhalb Widgetinhalt unverändert; Widgets-Ordner, Source-URLs, Settings, Wizard, Film-/Serien-Exit/Resume/Autoplay, native Live-Stop-Strategien und Skinwriter raw-identisch. Neuer Code löscht keine Profile/Caches und schreibt keine Skin-Dateien.

## Reproduktion

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
python tools/run_kodi_helper57_contract.py --report-dir kodi-helper57-evidence
```

Host-Abhängigkeiten gemäß CI: Python 3.12, Pillow, impacket 0.13.0, simpleeval 0.9.13; echter Kodi-Transport benötigt Docker. Frisches Checkout verwenden. Keine Geräteprofile als Testdaten kopieren.

## Offene Freigabebedingungen

Alle acht Android-Gates bleiben NOT_TESTED. Kein Gerätezugang, kein echter Providerimport, keine 10+10 Home-Bildpixel und keine echten RK3528-Start/Back-Zyklen durch Codex. Historische .57-FAILs bleiben in der Issue-Matrix stehen. Die tatsächliche Home-Ausblendung und der native Freeze sind BLOCKED_DEVICE_ACCESS; für beide wird keine vollständige Reparatur behauptet. A/B-Anleitung nutzt nur den vorhandenen optionalen .42-Modus, niemals automatische Umstellung. Box A/Box B unverändert; keine Freigabe und kein automatisches Schließen der Issues.
