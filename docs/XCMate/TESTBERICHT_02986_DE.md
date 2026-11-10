# Testbericht XCMate 0.1.29.86 – kumulativ A bis G

## Versions- und Reviewstand

Master #409, einschließlich der Nachträge P0-F und P0-G. Entwicklung im bestehenden Branch `fix/xcmate-02986-android-live-hero-mapping`. PR #410 (A–E) wurde am 10.11.2026 um 14:03:35 UTC durch den Repository-Inhaber gemergt: `36b903c06daa7b7fb5903f9de568237c18b9e2a1`. Dieser Agent hat keinen Merge ausgeführt. Die anschließenden F/G-Korrekturen liegen in [Folge-Draft #412](https://github.com/artattakk-creator/kodi-noodleprivate/pull/412). Keine Veröffentlichung und keine Geräteänderung.

Die [bereinigte .85-Loganalyse](ANDROID_LOGANALYSE_02985_BOXB_2026-11-10_134323_DE.md) bleibt der Android-Istbefund. 165 native Indexmeldungen sind kein Beweis einer bestimmten Python-Ursache. 1.485 fehlende EPG-Datenmeldungen betrafen 14 Kanal-Hashes; 6.693 NO_SOURCE_FACTS-Meldungen 342 Event-Hashes. 688 Cache-Ready-Logereignisse sind nicht automatisch 688 vollständige Builds.

## Automatisierte Ergebnisse

- **Aktueller vollständiger lokaler Hostlauf: 3.566 Tests PASS, 0 Fehler, 543,162 s**, Add-on-Quellstand `3bea87d2ffe9fadb03e18b95d91a9f01f3bffce7`. Alle kumulativen Bestandsfälle plus 21 neue F/G-Fälle. Zusätzlich **11 Branding-Pytests PASS** (eine externe Plugin-Deprecation-Warnung), **17 PO-Kataloge PASS**. Keine Addition überlappender Einzeltestläufe.
- Neue F-Fälle: **17 gezielte Tests**, einschließlich 100 Modell-Navigationszyklen, ungültiger nativer Kontrollgröße/-position, verspäteter Generation, geschlossener Owner, bereinigter Exceptiondaten, Kodi-Abbruch, Thread-isolierung, realem langsamen Loopback-HTTP und negativem EPG-Backoff. Die Socketprüfung besteht mit erlaubtem eigenen Loopback; ein zuvor ohne Socketberechtigung gestarteter Lauf gilt nicht als funktionaler PASS.
- Neue G-Fälle: **4 gezielte Tests**; zusammen mit älteren Navigations- und Scope-Verträgen bestand eine Auswahl von **44 Tests**. Sieben unterschiedliche Alpha-Glyphen in allen vier Zuständen, keine geleerte lokale Textur bei 100 Hide/Show-Wechseln, 100 D-Pad-Zyklen ohne Stop/Retune und vorhandene USER_HOME-Aktion.
- Sprach-/Scope-Nachprüfung: **15 Tests PASS**. Eine neue PO-Zeile benötigte einen Datensatztrenner; dies wurde korrigiert. Es wurde kein Sprachtest entfernt.
- **92 lokale Tabler-PNGs** mit Original-SVG-Hashes, Manifest, MIT-Lizenz, RGBA/96×96 und voller Bildprüfung: PASS.
- Alle alten **3.451 direkt deklarierten Testmethoden und Skip-Bedingungen** bleiben erhalten. Die vollständige Suite enthält zusätzlich geerbte Fälle. Zwei vorhandene Navigationsfälle wurden um die ausdrücklich neu geforderte Icon-Zwischenebene erweitert; ursprüngliche Stream-/Fokus-/Rückkehrassertionen bleiben erhalten. Der ControlImage-Stub bewahrt nun wie Kodi die Konstruktor-Textur; ein Widget-Control-Stub meldet seine tatsächliche Listengröße.

Historischer A–E-Checkpoint b09307a: **3.545 Hostfälle**, lokal 547,052 s, CI 793,397 s, 0 Fehler; 11 zusätzliche Branding-Pytests und 17 PO-Kataloge bestanden. Sämtliche zwölf zugehörigen Workflows grün: [vollständiger Hostlauf](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42823246999), [native .86-Bilder](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42823246270), [kumulative native Prüfung](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42823245920). Diese Ergebnisse sind kein Ersatz für die neue F/G-Prüfung.

## Native Kodi-/Skin-Prüfung

Echte Linux-Kodi-21-/BINGIE-2.2.3-Fenster, TLS-Transport, vollständig decodierte Texturen und Screenshot-Pixel werden geprüft. Metadaten, Portal und Token in der Fixture sind ausschließlich synthetisch. Kein Test greift auf eine Android-Box oder einen echten privaten Provider zu.

Die erweiterte .86-Pipeline verlangt: 88 Stationen; erster Logo-/EPG-Aufbau; großer TMDB-Backdrop vor kleinen Feedbildern; 800×1200-Poster im proportionalen offiziellen Postermodus; fremde persönliche Reihen; Fokus 23; Kandidatenbestätigung/Back; sieben tatsächlich unterschiedliche Rail-Icons samt nativem D-Pad; 100 reale Plugin-Invoker-/Detail-/Back-Zyklen unter Hintergrundupdates; anschließend zwei echte Offline-Neustarts mit sichtbaren Pixeln. Abschlussdateien werden erst nach allen zugehörigen Prüfungen geschrieben.

Ein Zwischenlauf f12d02c bestätigte die sieben tatsächlich gerenderten 1080p-Glyphen (Maskenüberdeckung 0,744–1,000). Seine 100-Zyklen-Prüfung scheiterte bei 1/100; er gilt insgesamt als FAIL. Der Prüfaufbau wartet jetzt zusätzlich auf gefüllte native Zeilen und gültigen Fokus, statt bereits auf den Modusnamen OK zu senden. Ein nachfolgender Lauf erreichte 54/100 bei null Index-/Dispatch-/Directory-/Invokerfehlern, scheiterte dann aber an einem nicht atomar geschriebenen Test-Receipt. Receipts und Abschlussdateien werden nun vollständig per temporärer Datei/Replace veröffentlicht. Auch dieser Teillauf ist kein PASS. Ein früherer Fixture-Lauf schrieb seinen Abschluss zu früh und wurde ebenfalls nicht als PASS übernommen. Fehler-/Pixelassertionen und die 100 verlangten Zyklen bleiben erhalten.

Die bestehende kumulative CI prüft zudem 20 Stop-ACK-/Rückkehrzyklen je Live/Film/Serie (60 insgesamt) und eine 1.800-s-Datenbankpause mit 443 wiederholten Polls, begrenzter Workerzahl und Recovery. Das versionsgebundene abschließende CI-Protokoll mit Endergebnis und Run-/Joblinks wird in [PR #412](https://github.com/artattakk-creator/kodi-noodleprivate/pull/412) und [Master #409](https://github.com/artattakk-creator/kodi-noodleprivate/issues/409) gepflegt. Dieses Dokument hält den lokal bereits vollständig geprüften Add-on-Stand fest; spätere CI-Resultate werden dort ohne weitere Add-on-/Paketänderung ergänzt. Kein Ergebnis wird vor Abschluss als PASS ausgegeben.

## Messwerte und ihre Grenzen

Synthetischer Host, 100 Aufbauten der vollständigen 88er-Identitätsleiste bei blockierter Bildpipeline: P50 **2,021 ms**, P95 **3,275 ms**, Maximum **18,409 ms**. Keine EPG-/Artwork-SQL-, DNS- oder Bilddateiarbeit pro Station; lokale Logo-Belege gebündelt. Diese Messung ist weder eine Android-Startzeit noch ein Pixel-SLO. Historische .85-Android-Zeiten 463.372/147.811 ms sowie Worker-Median 14,7/13,2 s bleiben getrennte Referenzdaten.

Der reale langsame Loopback-HTTP-Test weist den Abbruch des bestehenden Owner-Workers innerhalb der Assertion **<1,6 s nach Fensterende** nach. Andere Threads behalten unveränderte HTTP-Retry-/Timeoutwerte. OS-DNS ist nicht hart präemptiv abbrechbar; keine garantierte Android-Invoker-Latenz behaupten.

## Abnahmematrix

| Bereich | Code/Host | Linux Kodi | Physische Box B |
|---|---|---|---|
| A: vollständige Startgruppenleiste, unabhängige Logo-Belege | implementiert, vollständiger Hostlauf PASS | vorheriger A–E-Nachweis PASS, abschließender Runstatus siehe PR #412 | ANDROID_NOT_TESTED |
| B: Qualitätsklassen, TMDB-Priorität, CSI-Hysterese, Poster | implementiert, vollständiger Hostlauf PASS | frühere Bild-/Neustartbelege PASS, abschließender Runstatus siehe PR #412 | ANDROID_NOT_TESTED |
| C: persönliche Film-/Serien-/Custom-Reihen | exakter Byte-/Pfaderhalt im vollständigen Hostlauf PASS | synthetische persönliche Reihen geprüft | ANDROID_NOT_TESTED |
| D: TV-/Film-Freitext, Kandidaten, eigene Bilder, reversible Wahl | implementiert, vollständiger Hostlauf PASS | tatsächlicher Charmed-/Monk-Match nicht geprüft | ANDROID_NOT_TESTED |
| E: echte Zähler, begrenzte Statusanzeige | implementiert, vollständiger Hostlauf PASS | Controls/Pixels im nativen Test | ANDROID_NOT_TESTED |
| F: Index/Generation/Abbruch/Retry/100 Zyklen | vollständiger Hostlauf mit 17 neuen Fällen PASS | verbindlicher 100-Zyklen-Abschluss siehe PR #412 | ANDROID_NOT_TESTED |
| G: sieben eindeutige Icons/Links-Ebenen | vollständiger Hostlauf mit 4 neuen Fällen PASS | sieben 1080p-Glyphen nachgewiesen; finaler Runstatus siehe PR #412 | ANDROID_NOT_TESTED |
| Anderer Android-Speicherpool / dauerhaftes lokales Archiv | Reserve-/Negativpfade geprüft; kein automatischer Umzug | keine Hardware-Mountverifikation | EXTERNAL_UNAVAILABLE / ANDROID_NOT_TESTED |
| Channels / Installer 0.5.26 / Nutzerdaten | vollständiger Schutzvertrag | keine Geräteinstallation | unverändert lassen |

## Paket und Reproduktion

- Version **0.1.29.86**, **814 Dateien**, **3.591.570 Bytes**.
- SHA256: `44d3437f6838301e441642c8853d8925542d6f23709964c89067ea2e32355e20`.
- [ZIP](test-builds/02986/plugin.video.xtreammate-0.1.29.86.zip), [Prüfsumme](test-builds/02986/plugin.video.xtreammate-0.1.29.86.zip.sha256), [Android-Testplan](ANDROID_ABNAHME_02986_DE.md), [Codeanalyse](IMPLEMENTIERUNG_02986_DE.md).
- Paketbauer: `python tools/package_xcmate71.py <Ausgabeordner>`. ZIP-CRC und bytegenaue Paket-/Quellübereinstimmung PASS. Unabhängiger Reproduktionsvergleich und GitHub-Git-Blob-Readback **PASS**: Blob `f4a158870e9635edd33f3e000baac8519a3569c7`, 814 Dateien, alle Bytes und CRC identisch.
- Python 3.12; Pillow 12.3.0, impacket 0.13.0, simpleeval 0.9.13, pytest 9.2.0. Lokal große SQLite-Sortiertemporärdateien ausschließlich mit `SQLITE_TMPDIR`; kein Benutzerprofil umgeleitet. Komplette Unittests, Branding-Pytests und PO-Validierung sind getrennte Prüfungen.

## Offene Hardwaregates und Freigabe

Alle A86/B86/C86/D86/E86/F86/G86/REG86-Gerätetests im Android-Protokoll bleiben **ANDROID_NOT_TESTED**. Insbesondere reale Charmed-/Monk-Kandidaten, 20 Minuten CSI: Vegas, Warm-/Kaltstart-P50/P95, tatsächlicher anderer Mount/Schreib-/Lesetest, persönliche Widgets und 100 Android-Navigationszyklen sind offen. Private Rohlogs werden nicht veröffentlicht. Die eigenen Linux-Screenshots sind synthetisch und keine Android-Belege.

Kein Merge des Folge-Drafts und keine Veröffentlichung in regulär, Pilot oder NeoDark3 ohne gesonderte Nutzerfreigabe. Die bisherigen veröffentlichten .85-Pakete/Indizes und Installer 0.5.26 werden byteidentisch geschützt. Der neue Quellstand auf main aus dem externen #410-Merge bedeutet keinen von diesem Agent ausgeführten Repository-Release.
