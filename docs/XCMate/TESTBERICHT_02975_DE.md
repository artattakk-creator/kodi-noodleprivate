# XCMate 0.1.29.75 – Abschlussbericht für den Pilot-Kanal

**Automatisierte Code-Gates: PASS. Android: ANDROID_NOT_TESTED. Regulärer Kanal: weiterhin .74.**

Kumulative Basis: `ad5c337c0ca9ea6f85e458c17383fb32c19e3fc2`. Abschließend geprüfter Code: `c34663e47feb5181bf31fca0b52df320367b854a`. PR [#369](https://github.com/artattakk-creator/kodi-noodleprivate/pull/369), Aufträge #366/#367/#368. Die spätere Dokumentationsrevision ändert weder Anwendungscode noch ZIP. Merge und Pilot-Veröffentlichung sind vom Nutzer nach bestandenen automatisierten Gates ausdrücklich autorisiert; die tatsächliche öffentliche Kanalprüfung wird anschließend im PR dokumentiert.

## Paket

- [Vollständiges Installations-ZIP](test-builds/02975/plugin.video.xtreammate-0.1.29.75.zip): **3.425.286 Bytes**, 728 Dateien.
- [SHA256-Datei](test-builds/02975/plugin.video.xtreammate-0.1.29.75.zip.sha256):

```text
83acfaf48b1877dc32fb8879c470bcbc178c90d85a4296dc88c716f560ea1392
```

CRC, eindeutige/sichere ZIP-Pfade, Manifest, Add-on-ID, Version und bytegenauer Quellvergleich **PASS**. Der frühere Zwischenstand mit SHA `0d0cbf...` ist überholt. Der aktuelle Pilot-Index enthält ausschließlich das neue XCMate-Paket; die anderen Add-ons und der Installer bleiben unverändert. Kein Installer wird ausgeführt.

## Automatisierte Ergebnisse

| Prüfung | Ergebnis |
|---|---|
| Vollständiger aktueller Hostlauf in GitHub | **3.097/3.097 PASS**, 501,719 s |
| Bestehende pytest-Brandingtests | **11/11 PASS**, 0,21 s in CI |
| Neue .75-Funktions-/Schutztests | **43/43 PASS**, lokal 4,916 s; zusätzlich in CI |
| Gezielte frühere .68/.69/.70-Regressionen | **37/39/24 PASS** |
| Exaktes isoliertes Legacy-CI-Paket | **197/197 PASS**, lokal 18,021 s; anschließend in CI |
| Gettext | **17 Kataloge PASS** |
| Tabler-Texturen, Originale und Lizenz | **92 Texturen PASS** |
| Aktueller nativer Kodi-21.2-Home-Test | **720p und 1080p PASS**, jeweils 29 Bild-/Fokusfälle, 20 echte Auf-/Ab-Wechsel, Seitenmenü, fehlende Progress-Controls |
| Nativer Kodi-Prozessneustart / Reload | **beide Auflösungen PASS**; sieben Bild-/Fokusfälle, 88/24/24 Einträge, 32 geschützte Dateien bytegleich |
| Verspätetes Live-Stop-ACK im leeren eigenen Vollbild | **20 Hostzyklen PASS**, Rückkehr genau einmal |
| Native Linux-Wiedergabe-/Transport- und historische Integrationsgates | **PASS** |
| Sämtliche Android-Tests | **ANDROID_NOT_TESTED** |

Alle **zehn** Workflows für den aktuellen Code sind erfolgreich: [CI-Übersicht und URLs](test-builds/02975/evidence/ci75.json). Insbesondere [vollständiger Test-/Paketworkflow](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42108327326) und [aktuelle native .75-Prüfung](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42108327402). Die alten, mit dem neuen Layout absichtlich inkompatiblen UI-Geometrieverträge werden zusätzlich auf dem freigegebenen .74-Archiv `fca469c` geprüft. Sämtliche aktuellen Hosttests bleiben erhalten, ohne neue Skips; das neue Layout hat eigene aktuelle Pixel-, Fokus- und Fremdmedienprüfungen.

## Tatsächlicher Langzeitnachweis und Grenzen

Der native 1080p-UI-Lauf lief **3.600,405 Sekunden** mit echter monotoner Uhr, ohne Zeitvorlauf. Zuvor 23 Bild-/Fokusfälle und 20 echte Richtungswechsel. Bei 0/15/30/45 Minuten: **88 Live-Sender, 24 Filme, 24 Serien**. Eine zusätzliche Messung nach 3.692 Sekunden bestätigt dieselben Zahlen und **keine aktive Wiedergabe**. Keine Python-Exception, unverändertes Hero-Rechteck und eine aktive Rail.

- [Messdaten](test-builds/02975/evidence/native1080-soak.json)
- [Start](test-builds/02975/evidence/1080-soak-0.png), [30 Minuten](test-builds/02975/evidence/1080-soak-30min.png), [60 Minuten](test-builds/02975/evidence/1080-soak-60min.png)

**Präziser Scope:** Der Langzeitlauf prüft den identischen .75-Renderer, lokalen Snapshot und dessen Leser; der vollständige Add-on-Service ist in der synthetischen nativen Fixture deaktiviert. Währenddessen kam noch die separat hostgetestete Fokus-Queue-Korrektur hinzu. Die unveränderten Renderer-/Snapshot-Dateien und URL-/Status-Leser wurden bytegenau beziehungsweise per AST nachgewiesen: [Quellvergleich](test-builds/02975/evidence/soak-source-scope75.json). Das ist kein 60-Minuten-Nachweis der gesamten finalen Service-Pipeline und kein Android-PASS. Die abschließende kurze native CI prüft das vollständige aktuelle ZIP in beiden Auflösungen.

## Bild-, Reihenfolge- und Laufzeitbelege

[Live](test-builds/02975/evidence/720-home75-live-0.png), [Film mit Fanart](test-builds/02975/evidence/720-home75-vod-0.png), [Hochkantposter](test-builds/02975/evidence/720-home75-vod-1.png), [Serie](test-builds/02975/evidence/720-home75-series-0.png), [Seitenmenü](test-builds/02975/evidence/720-home75-menu.png), [fremde Poster](test-builds/02975/evidence/720-home75-foreign-poster-0.png), [Musik](test-builds/02975/evidence/720-home75-foreign-music-0.png), [fremde TV-Quelle](test-builds/02975/evidence/720-home75-foreign-television-0.png), [nach Neustart/Reload](test-builds/02975/evidence/720-after-restart-and-reload.png).

Alle Bilder sind echte Kodi-Screenshots mit **synthetischen** Inhalten und Wasserzeichen. Keine privaten Nutzerbilder oder Rohlogs. [29 Fälle](test-builds/02975/evidence/native720.json), [Neustart/PID-/Dateischutz](test-builds/02975/evidence/restart720.json), [Phasentrace](test-builds/02975/evidence/load-order720.json), [Fokus unter voller Queue](test-builds/02975/evidence/focus-queue75.json).

Der kontrollierte Empfängertrace zeigt `LIVE_HOME_READY → MOVIE_WARM_BEGIN → MOVIES_PREPARED → MOVIES_VISIBLE_READY → SERIES_WARM_BEGIN → SERIES_PREPARED → SERIES_VISIBLE_READY → REST_WARM_BEGIN`. `PREPARED` wird nicht als sichtbares Rendering ausgegeben. Die automatische Folgephase wartet in der strikten Spezifikationsauslegung auf die tatsächlich angezeigte vorherige Reihe; ein direkter Fokuswechsel bleibt möglich. Die vorgelegte Präzisierungsfrage zur Freigabe unsichtbar vorbereiteter Reihen ist unbeantwortet; deshalb wurde keine entsprechende Ausnahme eingebaut.

Die protokollierten `settled_render_ms` enthalten **1.500 ms feste Settle-Wartezeit**, Screenshoterstellung und Python-Pixelprüfung. Sie messen weder die Android-Kaltstartlatenz noch einen privaten TMDB-Abruf. Es wird kein `<2 s`- oder Android-p95-Erfolg behauptet. Text- und Bildlatenz auf dem echten Gerät sind getrennt im Android-Plan zu messen.

## Fehlernachweise und frühere Fehlversuche

- Fehlende Controls 296301/296302 brachen früher die gesamte Bankpublikation ab. Jetzt werden EPG-Text, Identität, Quelle und Bild unabhängig vom optionalen Balken veröffentlicht; Host und native Prüfung PASS.
- Ein nicht persistenter Now/Next-Handoff verlor den Prozessneustart. Der private, begrenzte und profil-/konfigurations-/zeitgebundene Checkpoint ergänzt den vorhandenen Guide ohne zweite Datenbank; neue Guide-Generationen gewinnen.
- Native Caption-Layer, Scrollanimationen und unvollständige Nachbarziele verursachten Geistertexte beziehungsweise nicht funktionierende vertikale Wechsel. Der neue native Viewport und die kompilierten Nachbarziele sind pixel-/tastengetestet.
- Ein komplett priorisierter 24er Lookup-Puffer konnte den neuen Fokus ablehnen. Jetzt hat der aktuelle Fokus Aufnahme-/Reihenfolgevorrang; bereits wartende exakte Intentionen werden ohne zweiten Lookup vorgezogen. Nur ein flüchtiger wartender Auftrag kann verdrängt werden; gespeicherte Jobs/Bilder bleiben unangetastet.
- Im isolierten 2.000-Schritte-Test fehlte das in Kodi vorhandene `xbmcvfs`. Profiling belegt **70.738 negative Importsuchen**. Die Fixture modelliert nun die echte native API. Der unveränderte 5-s-Test besteht; lokal kompletter Einzelfall einschließlich Setup 0,856 s. [Messwerte](test-builds/02975/evidence/navigation-fixture75.json).
- Frühere Gesamtläufe waren FAIL (unter anderem native Parameterassertion und nicht reproduzierte Katalog-BACKUP/INTERNAL-Fehler). Die Parameterassertion prüft jetzt zusätzlich die neuen nativen Nachbarziele. Die Katalogfehler traten in den anschließenden vollständigen Läufen nicht wieder auf; ihre damalige Ursache ist ungesichert. Kein Katalogkern wurde dafür verändert. Aktuelle Backup-/Readback-/Faulttests PASS.
- Ein paralleler Diagnoselauf endete durch Arbeitsumgebungs-OOM mit exit 137 und zählt nicht als PASS. Die Parallelität wurde anschließend reduziert. Frühe Neustart-Harness-Versuche prüften zu früh: HTTP-Ping konnte noch vom auslaufenden Kodi stammen, und die normale BINGIE-Startmaske war noch sichtbar. Die aktuelle Harness weist andere Prozess-IDs, das Ende der Maske und tatsächliche Bildpixel nach.

Ausführlich: [Ursachenanalyse](URSACHENANALYSE_02975_DE.md).

## Issue-Matrix und offene Geräteabnahme

| Issue / Bereich | Umsetzung | Verbleibend |
|---|---|---|
| #367 Home, EPG-Kaltstart, eine Rail, Fokus, Icons, Ladepriorität | Implementiert; Host und native Linux-Prüfungen PASS | Reale private Space-Blue-Version, echte EPG-/Bildlatenzen und Android-Gesamtabnahme offen |
| #366 Bilder, direkte geprüfte HTTPS-Quellen, Source-Bindung, 296301/296302 | Implementiert; Host-/Rendererprüfungen PASS | Reale private Provider-/TMDB-/TVmaze-Treffer **ANDROID_NOT_TESTED** |
| #368 Rückkehr nach positivem verspätetem ACK | 20 Hostzyklen PASS | **Teilweise behoben:** nativer ARM32-Stop ohne zurückkehrendes ACK bleibt unbewiesen/offen |
| Kodi MyVideos131 | Begrenzte read-only Diagnose | Keine native Kodi-Datenbankreparatur oder Migration durchgeführt |
| Profile, Token, Daten, Widgetrouten, Skin | Bestandsschutztests PASS; Vorschau/SHA-Backup/Zustimmung/Restore, unbekannte Skin-XML blockiert | Keine Benutzerbox verändert; private unbekannte Skin-Hashes nicht als unterstützt ausgegeben |

Alle `HERO75-R1..R8`, `H75-01..H75-10`, `PREFETCH75-1..8`, `LOAD75-A..F` und 20× Android-Back bleiben **ANDROID_NOT_TESTED**. Ausführbare Checkliste und Updateweg: [Android-Abnahme](ANDROID_ABNAHME_02975_DE.md). Zuerst einmal Live-TV-Zurück, erst bei PASS die Wiederholungen. Der bestehende .42-Kompatibilitätswert bleibt erhalten.

## Reproduktion und Releaseweg

```sh
python -m pip install 'Pillow>=11,<13' 'impacket==0.13.0' 'simpleeval==0.9.13' 'pytest>=8,<10'
python -m unittest discover -s tests -v
python -m pytest -q tests/test_xcmate_bingie_branding.py
python tools/validate_kodi_po.py
python tools/build_xcmate_nav_icons.py --check
python tools/run_kodi_home75_contract.py --report-dir /tmp/home75-720 --resolution 1280x720
python tools/run_kodi_home75_contract.py --report-dir /tmp/home75-1080 --resolution 1920x1080 --idle-seconds 3600
python tools/package_xcmate71.py /tmp/package75
cmp /tmp/package75/plugin.video.xtreammate-0.1.29.75.zip docs/XCMate/test-builds/02975/plugin.video.xtreammate-0.1.29.75.zip
python tools/publish_xcmate75_pilot.py
python tools/release_channel75.py
# Erst nach autorisiertem Merge / öffentlicher Pilot-Veröffentlichung:
python tools/publish_xcmate75_pilot.py --public
python tools/run_pilot75_native.py --report-dir /tmp/pilot75-public
```

Docker und Loopback-/Netzwerkberechtigung werden benötigt. Der letzte Befehl prüft Kodis echte Update-Liste anhand separater Metadaten-Fixtures; weder Installer noch XCMate-Anwendung werden ausgeführt. Vorab erkannte dieselbe Harness korrekt die öffentliche .74 und Setup .5.21.

**Pilot ausschließlich:** Root-`addons.xml` bleibt bytegleich auf `.74`; die reguläre CI-Veröffentlichung ist für .75 ohne gesonderte ausdrückliche Android-Freigabe gesperrt. Eine entsprechende Freigabedatei ist nicht enthalten. Kein neues Repository, kein Installerlauf, kein Datenreset. Öffentliche ZIP-/SHA-/Index-/MD5-/Manifest- und native Update-Erkennung erst nach tatsächlicher Veröffentlichung als RELEASED im PR/Issue bestätigen.
