# XCMate 0.1.25 – implementierter Testkandidat, EPG und Android-Abnahme

Stand: 18.10.2026. Grundlage: `origin/main` / `09b04e0`, XCMate 0.1.24. Branch: `fix/xcmate-infobar-epg-navigation`. Technische Kodi-ID unverändert: `plugin.video.xtreammate`.

| Prüfebene | Stand |
| --- | --- |
| Implementiert | Auf Entwicklungsbranch: zweistufige TV-UI, lokale Sender-/EPG-Snapshots, Programm- und Quellenvorschau. |
| Lokal geprüft | **237 Tests**, vor und nach isoliertem Build; **24 Cache-/HTTP-Tests** zusätzlich mit httpx. |
| GitHub-CI / PR | Wird im zentralen [Statusdokument](CODEX_STATUS_CURRENT_DE.md) mit PR-/Run-Link festgehalten. |
| Auf `main` veröffentlicht | **Nein. Produktiv bleibt 0.1.24.** |
| Android-TV bestätigt | **Nein.** Nur 0.1.24-Overlaystart ist historisch beobachtet; alle unten genannten 0.1.25-Gerätefälle sind offen. |

Vollständig gelesene Anforderungen: [Arbeitsauftrag](CODEX_ARBEITSAUFTRAG_025_TV_INFOBAR_EPG_STABILISIERUNG_DE.md), [UX-Spezifikation](TV_OSD_EPG_REMOTE_UX_SPEC_DE.md), [Gerätebefund 0.1.24](ANDROID_DEVICE_TEST_024_EPG_NAV_DE.md), Designsystem und Issues [#17](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17), [#13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13), [#12](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12), [#14](https://github.com/artattakk-creator/kodi-noodleprivate/issues/14). Skin #14 wird hier nicht umgesetzt.

## Bedienung und tatsächliche Darstellung

| Zustand | Eingabe | Ergebnis |
| --- | --- | --- |
| `LIVE_FULL` / intern `hidden` | Erstes OK | Nur `INFO_BAR`: lokales Senderlogo/Platzhalter, Name, JETZT, lokale Beginn-/Endzeit, gültiger Fortschritt, vergangene/verbleibende Minuten, DANACH. Keine Playeraktion. |
| `INFO_BAR` | Zweites OK oder Runter | `PLAYER_CONTROLS`, Fokus auf Pause/Weiter; **dieser Druck führt noch keine Aktion aus**. |
| `PLAYER_CONTROLS` | Weitere | `MORE_SETTINGS`: Ton, Bild, Untertitel, EPG, Einstellungen, Gruppen. |
| Vollbild / Infobar | Links | `CHANNEL_LIST` aus vorbereitetem Index. Acht sichtbare Zeilen mit Logo, Name, JETZT, Von–bis; nächste Sendung der fokussierten Zeile im Footer. |
| Senderliste | Hoch/Runter, OK | Kodi bewegt die Liste einmal; OK stimmt genau die absolute Sender-ID ab. Seitenlinks blättern, ohne zu tunen. `LIVE` kennzeichnet den spielenden Sender unabhängig vom Fokus. |
| Senderliste / Gruppen | Links / Zurück | Links öffnet Gruppen; Zurück aus Gruppen zur Liste, aus Liste zum TV. |
| Controls / Extras / Infobar | Zurück | Extras → Controls → Infobar → Vollbild, ohne Stop. Zurück im bereits freien Vollbild gibt den Navigator frei. |
| Vollbild | Hoch/Runter | Direktes Zapping im aktiven Gruppenfilter. Runter in der Infobar öffnet dagegen die Bedienung. |
| Infobar | Inaktivität | Nach 3–30 Sekunden konfigurierbar, Standard 8 Sekunden, ausblenden. Lokaler Zeit-/Sendungswechsel wird vom Service-Timer behandelt. |
| Wiedergabe | Stop | Wiedergabe stoppen, eigenen Dialog/Worker schließen und Fokus freigeben. |

Spulen erscheint nur bei `Player.SeekEnabled` und einer nutzbaren Dauer. Die Funktionen nutzen `osdaudiosettings`, `osdvideosettings`, `osdsubtitlesettings`; die Namen sind gegen Kodis `21.0-Omega/xbmc/input/WindowTranslator.cpp` geprüft. Menü und gelernte OK-Actions bleiben nutzbar. Keine zeitbasierte Entprellung verwirft schnelle getrennte Eingaben.

Native `onControl`-Ausführung wird nicht zusätzlich durch `onAction(SELECT)` wiederholt. Ein programmatischer `WindowDialog` erhält weiterhin keinen erfundenen `onInit()`-Aufruf. `WindowXMLDialog` im separaten Diagnosetest behält seine XML-Callbacks.

Die neue Slate-Leiste liegt innerhalb einer Safe-Area, verwendet dezente blaue/silberne Akzente und mitgelieferte PNG-Icons. Die bisher als Kästchen dargestellten Player-Symbolglyphen entfallen. Fokusflächen sind gleichmäßig dunkel und kontrastieren mit weißem Text; keine breit gezogenen weißen Glanztexturen hinter weißen Texten. Senderlogos gelangen nur als lokale Dateien zu Kodi; ein begrenzter Hintergrundcache lädt PNG/JPEG nach. Offline oder bei ungeeigneten Bildern erscheint der neutrale TV-Platzhalter.

**Layoutmodelle, ausdrücklich mit Fixtures und ohne nativen Kodi-Renderer:** [Infobar](assets/025/infobar-layout.png), [Senderliste](assets/025/channels-layout.png), [Bedienung/Weitere](assets/025/controls-layout.png). Sie stammen aus den tatsächlichen Control-Koordinaten, sind aber **keine Android-Screenshots und kein Nachweis echten Geräte-EPGs**. Reproduzierbar mit Pillow über `tools/render_xcmate_tv_icons.py` und `TZ=Europe/Berlin PYTHONDONTWRITEBYTECODE=1 python -B tools/render_xcmate_tv_preview.py`.

## Nachgewiesene Daten- und Performancefehler

1. **Verschiedene Guide-Datenwege:** Das 0.1.24-Overlay ignorierte vorhandenes Kurz-EPG. `epg_views.resolve_guide()` wird jetzt von normaler Senderliste, TV-Snapshot, Statusvorschau und Sender-Kontextvorschau verwendet. Explizite manuelle IDs haben Vorrang, auch gegenüber einem alten Stream-Alias im Cache. Fehlende manuelle Ziel-ID wird als solche angezeigt und nicht still durch einen anderen Sender ersetzt.
2. **Unvollständiges Zeitmodell:** Now/Next enthält validierte Start-/Stop-Werte, lokale Von–bis-Zeiten, kommende Programme, Quelle und Zuordnungsart. Fortschritt entsteht nur bei `start <= now < stop`; keine Stream-Wiedergabezeit und kein 0/0-Balken. Kurzes Xtream-EPG berücksichtigt `stop_timestamp`, `end_timestamp` oder ein eindeutig benanntes `duration_secs`. Die Einheit eines generischen `duration` wird nicht geraten.
3. **EPG-Button ohne Programmseite:** Die Guide-Ansicht zeigt jetzt echte laufende/kommende Sendungen mit Zeiten und Beschreibung. Bei fehlenden Daten erscheint ein klarer Hinweis. Hintergrunddaten aktualisieren die Ansicht ohne erneutes Öffnen und ohne `setFocus()`. `EPG jetzt` verwendet ebenfalls die tatsächliche Sender-/Programmvorschau statt roher XMLTV-IDs. Native Modaldialoge schließen zuerst Kodis Directory-Anforderung, um einen bleibenden Spinner zu verhindern.
4. **Katalogzugriff auf jedem Tastendruck:** Die Ownership-Prüfung konnte jedes Mal den vollständigen gecachten Xtream-Katalog lesen. Der Navigator verwendet nun eine gleichwertige Zulassung über seinen vorbereiteten ID-Index; URL-/Item-Identität und Portalprüfung bleiben bestehen. Kategorie-, Sender- und Positionsindizes entstehen im Hintergrunddienst beim Katalogaufbau, einschließlich vorbereiteter Auswahl für aktivierte Gruppen.
5. **Wiederholte GUI-Arbeit:** 100er-Seiten und absolute IDs bleiben erhalten; nur acht sichtbare Zeilen werden mit lokalen EPG-Informationen dargestellt. `ControlList.reset/addItems` erfolgt bei geänderten Listeninhalten/Seiten, nicht bei jedem Fokuswechsel. Snapshotdaten sind auf 128 Sender, ein Viewport-Auftrag auf 16 Sender begrenzt. Ein lokaler Worker pro Navigator; Kurz-EPG nutzt den vorhandenen begrenzten Service-Worker, Logos einen gemeinsamen Worker mit begrenzter Queue und maximal 128 Cachedateien.
6. **Cache-Verlust bei Schreibfehler:** Schreiben direkt in die Zieldatei konnte vorhandene Daten abschneiden. Cachedateien entstehen nun temporär mit anschließendem Replace/Rename; misslingt dies, bleibt die bisherige Datei erhalten. Der Leser findet auch einen neueren internen Fallback, wenn später der externe Ordner wieder verfügbar ist. Quellen, Konten und manuelle Zuordnungen liegen weiterhin getrennt.
7. **Altes EPG nach Ablauf des Refresh-TTL unsichtbar:** Ein fehlgeschlagener Refresh verbarg auch noch gültige alte Programme. Der lokale Leser kann bis zu sieben Tage alte Imports weiterverwenden; abgelaufene Sendungen werden beim Auflösen ausgeschlossen. Das gilt nicht als frischer Import. Ein syntaktisch lesbarer, aber vollständig überholter Guide überschreibt keinen guten Cache; Ergebnis `NO_CURRENT_WINDOW` / `NO_NEW_GUIDE`.

## EPG-Status und echte Programmvorschau

Im Portalmenü steht **„EPG-Status & Vorschau“** neben der Verwaltung und EPG jetzt. Öffnen und lokale Statusaktualisierung starten keinen Download. Die Ansicht zeigt:

- Anbieter-XMLTV, persistenten Guide-Cache und jede konfigurierte externe Quelle mit lokalem Namen/Index, aktiv/aus, Ergebnis, Zeitstempel, letztem bestätigten Erfolg und letzten erfolgreichen Sender-/Programmzahlen.
- Fehlerstufe/-klasse, Bytegrenzen getrennt nach Eingang/Entpacken, Kanal-/Sendungslimits, HTTP-Status, eingelesene Bytes. Unvollendete alte RUNNING/READ-Einträge erscheinen nach Ablauf als unterbrochen/veraltet.
- XMLTV-Zuordnungsquote für tatsächlich aktivierte Xtream-Gruppen, manuell / konservativ automatisch / Anbieter-ID / ohne Zuordnung. Kurz-EPG wird separat senderweise aufgelöst und nicht als XMLTV-Treffer ausgegeben.
- Gültige, deduplizierte Programme bis +48 Stunden; Auswahl/Suche nach Sendernamen, Jetzt/Danach, Von–bis und kommende Sendungen mit Beschreibung, Quelle und EPG-ID. Die Auswahl ist auf 200 Treffer begrenzt; für größere Kataloge Suche eingrenzen.

Quellstatus wird atomar pro Portal mit stabilen gehashten Quellkennungen gespeichert; Fehler behalten Last-success. Keine Provideradressen, Zugangsdaten oder Exception-Texte im Diagnosestatus. Quellen-/Cache-Fortschritt bleibt von tatsächlicher erfolgreicher Speicherung getrennt. Vorhandene XMLTV-Limits (80 MiB, 150.000 Programme, 10.000 Kanäle) wurden nicht erhöht. Einzelausfälle löschen keine Konfiguration und keinen guten Guide.

**Öffentliche DACH-Prüfung in dieser Cloud:** DE-, AT- und CH-EPGShare01 wurden einzeln angefragt. Alle drei scheiterten vor dem Einlesen mit `ProxyError`, `failure_stage=DOWNLOAD`, **0 Bytes**. Das belegt die Cloud-Netzwerkgrenze, weder Unverfügbarkeit der Feeds noch einen neuen Android-Providerfehler. Die historischen 0.1.23-Codes `PROVIDER_LIMIT` und `DOWNLOAD_FAILED` sind kein neuer 0.1.24/0.1.25-Gerätebefund. Ein echter Import auf dem Android-TV ist weiterhin erforderlich.

## Prüfungen und Paket

- **237/237 Tests bestanden** im Checkout und nach vollständigem Build in wegwerfbarer Repositorykopie, Python 3.12.14. Darunter **29 Overlay-/Callbacktests**, **13 neue Modell-/Snapshot-/Status-/Vorschautests** und **24 Cache-/HTTP-Tests**. Die komplette bestehende Suite anderer Add-ons lief mit; deren Quellcode blieb unverändert.
- Ein Integrationstest lädt komprimiertes XMLTV, importiert eine externe Quelle, speichert den Guide, liest ihn neu ein, berücksichtigt eine manuelle ID und liefert Now/Next/Progress an den echten lokalen Snapshot. Weitere Regressionen prüfen neuen manuellen Kontext trotz altem Alias, ungültige/überlappende Zeitfenster, Tages-/Zeitzonenwechsel, defekte Quellen, gescheiterte Cachewrites und ältere brauchbare Daten.
- Cache-/HTTP-Tests zusätzlich mit System-Python/httpx 0.28.1 bestanden; im Build-Venv ohne httpx wird urllib geprüft. Syntaxprüfung, ZIP-CRC, Repository-Index-MD5 und Installerkopien in der isolierten Kopie bestanden.
- Native Signaturen gegen [Kodi 21.0-Omega Control.h](https://github.com/xbmc/xbmc/blob/21.0-Omega/xbmc/interfaces/legacy/Control.h): `ControlList(_itemHeight,_space)`, `ControlButton(textOffsetX,...)`, `ControlImage(aspectRatio,...)`, `ControlLabel`, `setImage(imageFilename,useCache)`, `setPosition(x,y)`, `setWidth(width)`. Explizite GUI-Testsignaturen und repositoryweiter Aufrufvertrag bestehen. **Echte Bindings/Renderer wurden in der Cloud nicht ausgeführt.**
- Paketversion **0.1.25 / service build=25**: [ZIP](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.25.zip), **259497 Bytes**, **75 Dateien bytegenau gegen Quellen geprüft**. [SHA-Datei](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.25.zip.sha256): `583026db01ffceb410e67784113e479746d1ea4e91cea38727d3a3b86f7775b4`.
- `tools/build_repository.py` schreibt die XCMate-SHA jetzt bei jedem Packen neu. Der spätere Main-Publish darf die Kandidaten-SHA nicht für einen neu erzeugten ZIP-Container übernehmen. CI-Artefakte enthalten ihre eigene korrekte Prüfsumme.

Lokale Befehle: `PYTHONDONTWRITEBYTECODE=1 python -B -m unittest discover -s tests -v`. Den vollständigen Repositorybuilder ausschließlich in einer wegwerfbaren Kopie ausführen; er erzeugt auch andere Pakete/Artwork. Im Entwicklungsbranch wurden deren Quellen, bestehende Pakete, `addons.xml` und `addons.xml.md5` nicht angefasst.

### Performance: Messwert und Ziel unterscheiden

| Synthetischer Fall | Objekte + Index | Warme Infobar, Median | Warme Liste, Median |
| --- | ---: | ---: | ---: |
| 2.746 Sender | 2,44 ms | 0,022 ms | 0,057 ms |
| 53.664 Sender | 70,33 ms | 0,022 ms | 0,057 ms |

**Nur Python-Modell mit Control-Doubles**, 40 Öffnungen je Zustand: kein nativer Kodi-Renderer, kein kalter Katalog-Dateiimport, keine Netzwerk-/GPU-/Android-Latenz. Diese Zahlen sind ausschließlich Regressions-/Skalierungsindikatoren. Ziele am echten TV bleiben **<250 ms Infobar / <500 ms warme Liste**; noch ungemessen.

Gespeicherte Diagnose trennt `catalog_performance` (Cache-Lesen/Indexaufbau), `epg_performance` (Cache-Hit, Datenworker/Snapshot) und `performance` (GUI-Zustand, Indexauswahl, Snapshot-Zugriff, Render-/Fokusaufruf). Der EPG-Timer überschreibt dadurch nicht den letzten GUI-Messwert. Die Phasen enden beim Python-Fokusaufruf; Geräte-Video/Fokusbeobachtung muss zusätzlich die native Darstellung und Eingabewarteschlange erfassen.

## Vollständiger Android-TV-Testplan – alle Fälle OFFEN

1. **Vorbereitung und Installation:** PR/CI/Test-ZIP prüfen; für einen Test das Kandidaten-ZIP als Update auf bestehendes XCMate installieren, ohne Deinstallation oder Profillöschung. Globale Fallback-Keymap ausgeschaltet lassen. Kodi vollständig neu starten; Add-on-Version **0.1.25**, Dienstdiagnose **build=25** bestätigen. Quellen, Konten, Gruppen, Startsender und zwei manuelle Zuordnungen vorher/nachher vergleichen.
2. **Start und First OK:** Einen regulären EPG-tauglichen Sender starten, etwa einen tatsächlich vom Konto angebotenen Nachrichten-/ÖR-Sender, nicht ausschließlich 4K-Relax-Testkanäle. TV bleibt zunächst frei. Erstes OK: nur kompakte Infobar, lokales Logo/Platzhalter und korrekter Sendername; kein Pause/Stop und kein Kodi-Standard-OSD. Screenshot mit Titel/Zeiten aufnehmen.
3. **Second OK / Down:** Zweites OK öffnet nur die Bedienung, Fokus sichtbar, Bild läuft weiter. Zurück → Infobar; Runter öffnet ebenfalls nur Bedienung. Erst ein weiterer OK auf Pause pausiert. Mehrfach schnell 1×/2×/3× OK testen, ohne Zeit-Debounce oder doppelte Aktion.
4. **Infozeit und Missing-State:** Einen Sender mit echter aktueller Sendung gegen Anbieterprogramm prüfen: Start/Ende in lokaler Zeitzone, Prozent, vergangene und verbleibende Minuten, nächste Sendung. Sender ohne Guide: klare Fehlanzeige, kein Balken und keine 0/0-Minuten; Name/Logo sofort sichtbar. Sendungswechsel, Mitternacht und bei Gelegenheit Zeitzonen-/Sommerzeitfälle prüfen. Ausblendzeit 3/8/30 Sekunden testen; Eingabe erneuert Inaktivität.
5. **Bedienleiste / Weitere:** Links/Rechts/Hoch/Runter sichtbar; jede OK-Aktion genau einmal. Nicht seekbarer Stream blendet Seek aus, unterstützter Timeshift erlaubt -10/+30. Ton, Bild und **Untertitel** öffnen die korrekten Kodi-Dialoge; Zurück ohne Fokusverlust. XCMate-Einstellungen und Gruppen erreichbar, nichts unten abgeschnitten.
6. **Links-Senderliste:** Kalt und warm getrennt messen, inklusive erster sichtbarer Fokusmarkierung. Acht sichtbare Zeilen, Logo/Name/JETZT/Von–bis; `LIVE` vom Fokus unterscheiden. Einmal Hoch/Runter bewegt einmal. Auf einen anderen Sender OK: genau dieser spielt. Gruppe links öffnen, deaktivieren/reaktivieren, Zurück zur Liste; Filter und manuelle EPG-IDs bleiben erhalten.
7. **Große Kataloge:** Gruppen mit 2.746 und ggf. Katalog mit 53.664 Sendern testen. 100er-Seitenlinks, native Page-Up/Down, erster/letzter Sender und Suche prüfen. Keine Vollkatalog-/XMLTV-Verarbeitung auf Tastendruck. `catalog_performance`, `epg_performance`, `performance`, `focus`, `input` vor und nach Stop auslesen. Native Latenz zu den Zielwerten gesondert protokollieren.
8. **Realer EPG-Import:** EPG-Status ohne Wiedergabe öffnen; jeder gespeicherten Quelle ihren Index/Namen zuordnen. Zunächst genau einen kleineren DE-Feed aktivieren und Aktualisierung explizit anfordern; UI während Download weiter bedienen. „Lokalen Status / Cache neu einlesen“ nutzen. READ/Parsing und tatsächlich gespeicherten READY-Cache unterscheiden. Anschließend AT/CH einzeln prüfen. Große Masterquelle separat, 80-MiB-Limit nicht erhöhen.
9. **Tatsächliche Vorschau und Fallback:** Im EPG-Status einen Sender suchen, echte Jetzt-/Danach-Titel mit Zeiten anzeigen; mindestens ein regulärer Sender muss am TV nachweislich korrekt sein. Bei fehlendem XMLTV Kurz-EPG prüfen und Quelle `SHORT_EPG` von XMLTV unterscheiden. Normaler Sender-Kontext, Overlayliste, Infobar und Programmseite müssen dieselbe Zuordnung zeigen. EPG-Button zeigt Programme/Beschreibungen statt Sendernamen.
10. **Hintergrundaktualisierung:** Programmfenster oder Liste geöffnet lassen, neuen Import/Kurz-EPG abwarten. Titel aktualisieren sich ohne Fokuswechsel und ohne erneut den EPG-Button drücken zu müssen. Gerät kurz offline: Navigation weiter nutzbar, vorhandene brauchbare Daten bleiben sichtbar; kein vorgetäuschter neuer Erfolg.
11. **Persistenz und Fehlerfälle:** Nach fehlgeschlagener Quelle und nach Stop Diagnose ansehen, Kodi neu starten, Quelle/Last-success/Fehlerstufe/-klasse wiederfinden. Cacheordner-Schreibbarkeit und internen Fallback auf echter Android-/SAF-Umgebung testen. Keine Zugangsdaten, privaten URLs oder unbereinigten Logs weitergeben.
12. **Isolation:** Stop, dann BINGIE MOD und VOD aus anderem Add-on bedienen; keine XCMate-Tasten/Fokusreste. Erneuten eigenen Live-Sender starten. Zurück/Stop dürfen keine schwarzen Screens oder Kodi-weiten Hänger verursachen. Separater XML-Popup-Test gilt nicht als Live-TV-Abnahme.

**Freigabekriterium:** Mindestens ein echter Sender mit korrektem Now/Next, Von–bis und Fortschritt auf dem Android-TV, plus bestandene OK-/Fokus-/Seiten-/Isolationsfälle. Bis dahin #12, #13 und #17 offen lassen. Kein „EPG funktioniert am Gerät“ aus Fixturetests ableiten.

## Regulärer Repository-Updateweg

Vorab nur Review/Testkandidat und PR-Artefakt. **Kein selbständiger Merge oder Publish.** Nach erfolgreichem Review/Gerätetest und ausdrücklicher Nutzerfreigabe: PR nach `main`, vorhandenen „Publish GS Media Kodi updates“-Workflow abwarten, dann Manifest/`addons.xml` auf 0.1.25 und neue ZIP-SHA/Index-MD5 vergleichen. Erst dann in Kodi über GS Media nach Updates suchen und XCMate regulär aktualisieren, Kodi vollständig neu starten. Kein gesonderter GitHub-Release nötig. Daten-/Quellenkonfiguration behalten.
