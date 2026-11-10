# XCMate 0.1.29.87 – Test- und Auslieferungsbericht

**Draft-Testkandidat, keine Android-Abnahme, kein Merge und keine Veröffentlichung.** Master #415; Nachträge #417 separat und mit Infrastrukturblockern. Quellbasis veröffentlichte .86 `48cbdc2`, Dokumentnachträge bis `ee87ed4` übernommen. Draft #416; separater Installerentwurf #418. Box A wurde nicht kontaktiert.

## Identität und Paket

- Produktionscode: `b3738f3b73916dbc4c680dc2494663e261d5ce43`.
- Git-Quellbaum `src/plugin.video.xtreammate`: `c55c297d281d9c4cd239ae21c739d41333699f94`.
- Neuere Testharness-Commits `a3f68b5` / `cbfc590` haben exakt denselben Produktionsquellbaum und dieselbe ZIP. Der letzte betrifft ausschließlich das begrenzte Budget der erweiterten nativen Kaltstart-Teststrecke; kein produktiver Save-/Stop-Timeout wurde verändert.
- ZIP: [`test-builds/02987/plugin.video.xtreammate-0.1.29.87.zip`](test-builds/02987/plugin.video.xtreammate-0.1.29.87.zip).
- SHA256: **`e78f28fdb1f1537d42acbef55f5539d6670f4b306d07b92e9e7795cc51dff843`**.
- 3.615.817 Bytes, 825 Dateien. CRC, vollständiges Dateiinventar, sichere Pfade und Quellbyte-Parität PASS. Zwei unabhängige lokale Paketierungen bytegleich. GitHub-Git-Blob `e722dca212bd3ef00a0e5bc2f1fde0761a075db1` zurückgelesen und vollständig gegen das lokale ZIP verglichen: PASS.

## Vollständige Hostsuite

**3.639 Tests PASS in 680,030 Sekunden** auf dem finalen Produktionsquellbaum. Keine Fehler und keine fehlgeschlagenen Tests in diesem Lauf. **Elf zusätzliche pytest-Brandingprüfungen PASS**, 17 gettext-Kataloge PASS; Deutsch/Englisch enthalten 1.317 Kontexte, weitere Sprachen nutzen den vorhandenen englischen Fallback für neue Texte.

Reproduktion aus dem kumulativen Checkout:

```sh
TMPDIR=/workspace/xcmate87-test-tmp \
SQLITE_TMPDIR=/dev/shm/xcmate87-sqlite \
PYTHONPATH=/tmp/xcmate80-host-deps:tests \
python -m unittest discover -s tests -v
python -m pytest -q tests/test_xcmate_bingie_branding.py
python tools/validate_kodi_po.py
python tools/package_xcmate71.py /tmp/xcmate87-reproduction
```

Die beiden Tempverzeichnisse vorher anlegen und einen eigenen beschreibbaren Testbereich mit genügend Platz wählen. Das sind Host-Testpfade, keine Zielpfade für Kodi/Android. SQLite-Temporärdaten wurden wegen des knappen Host-`/tmp` getrennt abgelegt; explizite ENOSPC-/Reserve-/Read-only-Fehlertests bleiben in der Suite. Abhängigkeiten: Python 3.12.14, Pillow 12.3.0, simpleeval 0.9.13, impacket 0.13.0, pytest 9.x.

Schutzvertrag: alle 811 bisherigen Quelldateien vollständig vorhanden, nur 55 exakt freigegebene Altdatei-Deltas; sämtliche 3.510 vorher deklarierten Testmethoden und ihre Skip-Bedingungen erhalten. Die ausgeführte Zahl enthält zusätzlich geerbte Tests. Keine Altmethoden entfernt oder durch neue Skips ausgeblendet.

Wesentliche zusätzliche Fälle: Logo-vs-Poster-Quelle, Auth-/URL-Sperren, bestehender Kodi-Texturecache bei Schreibbudget null, vollständige 88 Sendernamen ohne Bilder; separater/gleicher/unklarer Pool, eigener fsync/Rename/Readback, fremde Dateien/Symlinks, Teilkopie, Abbruch/Wiederaufnahme, SHA, Profil-/Mountwechsel und Lesen unter Reserve; drei Medien-/Quellenarten bei manueller Zuordnung, EPG-Wechsel, echtes 5-s-/30-s-Workerblocking und spätes Cancel; unveränderte Rail ohne Reload, sichere Hero-URI-Erneuerung, feste 70/30-Geometrie und vollständige private Fremdwidget-Inventur. Gateway-/Einmalimport-Tests ausschließlich mit synthetischen Antworten, kein echter Token.

## GitHub-CI

- [Vollständige Hostprüfung auf a3f68b5](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42885588555): **3.639 PASS in 859,993 s**, elf Brandingtests PASS, PO-Validierung und byteidentische ZIP-Reproduktion PASS.
- [Normaler Repository-Workflow auf demselben Quellbaum](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42885588586): PASS, einschließlich weiterer kompletter Hostsuite, Kodi-Transport, synthetischer TS/HLS/Auto-Wiedergabe und Review-Paketierung. Der Jobname „publish“ bedeutet hier ausschließlich **PR-Artefakt**, nicht Repository-Veröffentlichung; Commit-/Publish-Schritt ist im PR gesperrt.
- Die fokussierten .68/.69/.70/.71/.72/.73- und GS-Media-Lite-Prüfungen auf a3f68b5 sind PASS. Archivierte .74 prüft bewusst den historischen Stand, keine .87-Android-Funktion.
- [Erneute vollständige Hostprüfung auf cbfc590](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42888222007): **3.639 PASS in 852,949 s**, elf Brandingtests, Sprachvalidierung und ZIP-Reproduktion PASS.

`cbfc590` wurde als reine Harness-Korrektur mit übersprungenem automatischen CI-Neustart gepusht; die beiden betroffenen Workflows wurden ausdrücklich manuell gestartet. So wird der bereits laufende echte 30-Minuten-Schutzpausentest des **identischen** Produktionsquellbaums nicht unnötig abgebrochen. Das ist keine Freigabe oder Umgehung eines fehlgeschlagenen Tests; der Bilder-/Kaltstart-Gate bleibt bis zum erfolgreichen Nachlauf offen.

## Native Linux-Kodi-Prüfungen – getrennt von Android

Native Engine nach JSON-RPC: **Kodi 21.2 stable, Revision 20250330-nogitfound, Linux x86_64**, gepinnter Debian-Trixie-Container, Xvfb/Softwarerenderer, BINGIE MOD 2.2.3 und nativer SkinShortcuts-Compiler. Keine ARM32-/RK3528-Hardware und keine behauptete Kodi-21.3-Geräteabnahme.

| Prüfung | Evidenz / Status |
|---|---|
| Vollständiges Home, Guide-Fokus, tatsächlicher Film-Detailbutton, AV-Start/Stop-ACK, Rückkehr und zwei Neustarts, 1080p | PASS im [Home-Lauf](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42885588670), Job 130073565821 |
| 720p mit realen 1.800 s DB-Schutzpause, 443 Folgeanfragen ohne neue Worker, gleiche Worker-Recovery und Bild-/Railprüfung | **PASS: 1.800,79 s, 30 Kontrollpunkte, 443 redundante Anfragen, ein Providerworker, Wiederaufnahme desselben Workers und null unbehandelte Ausnahmen**, Job 130073565729 |
| Live/Film/Episode je 20 native Stop-/ACK-Zyklen, AV-Decode und Medienfortschritt | **60 PASS**, Job 130073565281 im selben Lauf. Kein Nachweis hörbaren Tons oder Android-Vollbild-Rückwegs. |
| Bilder/Poster, 88 Sender, sieben Icon-Glyphen, 100 Invoker-/WindowXML-Detail-/Back-Zyklen, 13 fremde Definitionen aus sieben eigenständigen synthetischen Plugins, zehn Row-Wechsel und zwei native lokale WAV-Starts, je Auflösung plus zwei Offline-Neustarts | **PASS in beiden Auflösungen, jeweils vollständige Warm-/Kaltstrecke und zwei Neustarts mit abgeschaltetem Bildursprung** im [erweiterten Nachlauf](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42888216159) |

Der 100-Zyklen-Test verwendet wirkliche RunPlugin-Invoker und native Detail-/Medienfenster samt Hintergrundpublikation; er ersetzt **nicht** die komplette reale IR-Sequenz mit Live-Vollbild/Mini-EPG auf Android. Die Fremdquellen haben echte **nicht-XCMate-Plugin-IDs/Verzeichnisse** und native Konsumenten, enthalten jedoch injizierte synthetische Daten. Es sind keine produktiven MP3-Streams-/SHOUTcast-Implementierungen. Deren echte Netzfehler, Bibliotheks-/Benutzerwidgets und physischer Ton bleiben Geräteabnahme.

XCMate-Python sieht in der Bilder-Fixture absichtlich nur 27 MiB frei; Kodi-C++ besitzt tatsächlich freien Host-Texturecache. Das beweist sichere Lesereferenz-/Renderpfade unter injizierter XCMate-Reserveblockade, **keinen** realen Android-ENOSPC-Speichergewinn. Synthetische Screenshots/JSON/Logs liegen in den jeweiligen CI-Artefakten.

## Zeitmessungen und Aussagegrenzen

Stage-Traces sind redigiert und pro Ereignis begrenzt; Queue, Matching, URL-Policy, Response, Cache, Render-Control und Bank werden getrennt erfasst. `hero_timing87.summary()` liefert P50/P95 der Millisekunden **seit der ersten Beobachtung derselben Eventidentität**. Bei erneutem Fokus auf dasselbe Event sind das keine neuen Queue-Dauern; bewusst pausierte Testfälle fließen ein. Diese Werte dürfen weder als reine Netzwerkzeit noch als echte Android-Time-to-first-visible-image ausgegeben werden. Decode-/Bank-/REFERENCE_READY bedeutet ausdrücklich keinen Pixelnachweis.

P50/P95 der echten fünf Box-B-Sendungen und Warm-/Kalt-SLO ≤2/≤5 s: **ANDROID_NOT_TESTED**. „Desperate Housewives“/„American Dad“ wurden im Hosttest mit unabhängig geprüften synthetischen TMDB-TV-Antworten und Backdrop-Rolle geprüft; keine echten Nutzer-TMDB-Anfragen und keine erfundene Erklärung der gemeldeten 15 Sekunden.

## Während der Entwicklung gefundene und behobene Fehler

- Erster Host-Baseline-Versuch: sieben echte Host-Speicherpreflights im zu knappen `/tmp` fehlgeschlagen; keine Aussage über den Android-Speicher. Getrennter geeigneter Host-Testbereich, echte Fehlersimulationen weiter aktiv.
- Früher kompletter 3.611er-Lauf: acht Failures/drei Errors (u. a. atomare Hero-Commit-Reihenfolge, alte Versions-/HTML-Pins und uneinheitliche Profilfixture). Korrekturen überprüft; anschließende komplette 3.616-/3.621-/3.624er-Läufe PASS.
- 3.634er-Lauf des optionalen Clients: ein echter eigener UI-Vertragsfehler, ungeschmücktes Select-Menü; korrigiert auf vorhandenen Menü-Renderer. Finale 3.639er-Suite PASS.
- Native Vorläufe: überholter Versionszweig und vorzeitige Erfolgsdatei im verschachtelten Testharness, Fokus-Rennen mit BINGIE-Seitenmenü, Stop/GUI-Teardown-Rennen und zu kleines Budget für die inzwischen vergrößerte Kaltstartstrecke. Keine alten Fehlversuche als PASS umetikettiert. Die stärkere finale Pixelprüfung deckte tatsächlich verschwundene Rail-Logos auf; schnelle unabhängige Live-Erneuerung ergänzt. Der erweiterte Nachlauf hat anschließend in beiden Auflösungen alle unverändert strengen Pixel-/Bestandsschutz-/Neustartassertionen bestanden. Das größere begrenzte Budget gilt ausschließlich für den Testharness, nicht für die Add-on-Oberfläche.

## P0-Matrix und offene Freigabebedingungen

| Bereich | Implementierung / Host | Echte Geräteabnahme |
|---|---|---|
| A/L Senderlogos und erster Senderframe | PASS der beschriebenen Host-/Schutzfälle; native Gesamtmatrix siehe oben | ANDROID_NOT_TESTED; kein 88/88 behauptet |
| S Mount-/Budgetprüfung, Migration, Datenintegrität | PASS mit realen eigenen Testdateien und synthetischen Volume-Identitäten | ANDROID_NOT_TESTED; **separater nutzbarer Pool nicht nachgewiesen** |
| H/B Eventbilder, Rangfolge, Bildhalte-/URI-Wechsel | PASS Host; native Backdrop-/Poster-/Cache-Prüfungen separat | ANDROID_NOT_TESTED, reale Sendungserkennung/Quelle/Pixel offen |
| D2 manuelle Zuordnung/Save/Readback | PASS Host einschließlich realer 5-/30-s-Blockierung | ANDROID_NOT_TESTED |
| F/G native Guard-/Generations-/Icon-Korrekturen | PASS Host; native Zyklen/Pixel siehe Einzelbelege | ANDROID_NOT_TESTED; exakter C++-Stack der 98 alten Fehler weiter unbewiesen |
| C/E/I EPG-/Widget-/Layout-/Fremddefinitionen | PASS Host; native Gesamt-/Neustartstrecke siehe oben | ANDROID_NOT_TESTED, insbesondere echte Fremdquellenausfälle I4 |
| J Token-Erhalt | PASS synthetischer Upgrade-/Neustart-/Owner-Schutz; Writer bytegleich, Revisionspublisher explizit XCMate | ANDROID_NOT_TESTED, echte autorisierte TMDB-Abfrage offen |
| K/K1 sichere optionale Bereitstellung | Client-/Installerprototyp mit Fake-Antworten; separater Draft #418 | **BLOCKED**: echte API/Hostingrechte, Admin/MFA, Secret-Store, Replay-/Rate-/Widerrufsschutz, Nutzungsbedingungen und Deployfreigabe fehlen |

Alle elf geschützten Kanal-/Installerdateien wurden lokal **und als committed Git-Bytes** mit der Ausgangsbasis verglichen: PASS. Die drei veröffentlichten .86-ZIPs bleiben SHA256 `07c7f10b0f5da873c1add538c44bf2ee4c9aa5027ad98c262ec98bd5d709c7c4`; Setup .5.26 bleibt `5aa5d101a57adda5dbb1f5d05319da1ec185676dc784817b25dea267322ae0af`. Keine Datenbanken, Bilder, Profile, Token oder Caches gelöscht; kein Installationslauf auf einer Box.

Private Rohreferenz für den Pixelvergleich: **REFERENZBILD_NICHT_VERFÜGBAR**. Die schriftlich freigegebene 70/30-Geometrie bleibt verbindlich; keine fiktiven Referenzbilder.

Freigabe: **NEIN**. Draft und manuell installierbarer Testkandidat zur Prüfung, Original/Pilot/NeoDark3 und .5.26 unverändert. Kein Merge oder Release ohne tatsächliche Abnahme und erneute ausdrückliche Freigabe.

## Stabile native Belege

Zusammenfassung mit Messwerten: [`native-summary.json`](test-builds/02987/native-summary.json). Tatsächliche native Aufnahmen: [720p Hero](test-builds/02987/native-linux-720-hero.png), [1080p Hero](test-builds/02987/native-linux-1080-hero.png), [720p Fremdreihe](test-builds/02987/native-linux-720-foreign.png), [1080p Fremdreihe](test-builds/02987/native-linux-1080-foreign.png). Farbbilder sind synthetisch; die sichtbare Fußzeile nennt noch die wiederverwendete .85-Fixture, die tatsächliche Add-on-Version wird separat zur Laufzeit als .87 geprüft. Kein Downgrade und keine Android-Aufnahme. Medienreihen sind in diesen späten Bildern nach dem Test auf Position 23 gescrollt; nicht als frischer erster Home-Frame ausgeben.

Vier kalte Logo-Pixelprüfungen: 3.495/3.740 ms (720p), 3.817/3.553 ms (1080p), jeweils ab Start der Testscriptphase. 153.456/156.800 passende Logo-Pixel, gemessene 560×280-Größe im normalisierten Kontrollraum. Die Screenshot-Wartephase der bereits stabil angewählten Medien beträgt 562–1.161 ms; das schließt vorherige bewusste Testwartezeiten aus und ist **keine** gemessene Android-Time-to-first-image. Die finale synthetische 1080p-Aufnahme meldet 18 lesbare Cache-Logos von 88; kein 88/88-PASS.

Die 13 Fremddefinitionen/acht eigenständigen Zeilen (sieben Plugin-IDs), zehn Wechsel, sieben unterschiedliche Icon-Masken und 100 Invoker-/Detail-/Back-Zyklen bleiben native Linux-Belege. Reale Drittanbieter-Netzwerkausfälle und die vollständige Android-Mini-EPG-/IR-Sequenz sind weiter offen.

Nach dem grünen Quell-/CI-Stand wird ausschließlich dieser Bericht mit Belegen nachgeführt. Produktionsquellbaum und Installations-ZIP bleiben unverändert; keine Veröffentlichung.

Der separate Installer-Draft #418 hat vier eigene Hosttests und seinen eigenen Build-/Pairingjob PASS. Seine geerbte Bildmatrix auf unverändertem .86-Code enthält weiterhin einen 1080p-Hero-FAIL; er darf nicht als vollständig grün oder produktiv freigegeben bezeichnet werden. Diese alte .86-Quellprüfung ist getrennt von den hier bestandenen .87-Läufen.
