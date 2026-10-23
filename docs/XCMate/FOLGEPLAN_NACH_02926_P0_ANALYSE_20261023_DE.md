# XCMate – P0-Codeanalyse und Folgeplan nach 0.1.29.26

Stand: 23.10.2026. Analysebasis: Merge-Commit
`f70f9eac130029516a7858b91cdc87ef4b6e6f51` (PR #119).
Dieser PR enthält ausschließlich Analyse und Planung, keine Laufzeitänderung,
keine neue Add-on-Versionsnummer und kein zusätzliches Installationspaket.

## Verbindlicher Ausgangspunkt

- Gelesen: [vollständige Übergabe](CODEX_UEBERGABE_02925_EPG_REGRESSION_AUTOPLAY_LIGHTWEIGHT_DESIGN_20261023_DE.md),
  [aktualisierte Android-Abnahme](ANDROID_ABNAHMEERGEBNISSE_LIGHTWEIGHT_02925_20261023_DE.md),
  [Such-Logvergleich](ANDROID_SUCHCRASH_LOGVERGLEICH_02925_20261023_DE.md),
  Issues #118/#121 einschließlich aller Kommentare sowie #111/#120/#122/#123.
- Android-Abnahme von **.25 Lightweight: 22 PASS / 4 FAIL / 1 NOT_TESTED**.
  E05 ist FAIL. Jetzt/Danach bleibt PASS. Der nachgetestete Staffelwechsel ist
  ein zusätzlicher Nachweis zu P02/#85 und erhöht die 27er-Testzahl nicht.
- **Autoplay einschließlich Staffelwechsel, Stop und Resume ist eingefroren.**
  Keine Änderungen an diesen Pfaden im EPG- oder Designfix.
- Neueste ausdrückliche Nutzeranweisung: „Nimm das aber bitte als Folgeversion,
  die Version 26 mergen wir jetzt“. Deshalb wurde der unveränderte .26-Kandidat
  aus [PR #119](https://github.com/artattakk-creator/kodi-noodleprivate/pull/119)
  gemergt. Die neuen Anforderungen werden nicht nachträglich in das .26-ZIP gepackt.
- Das ist eine Merge-Freigabe, **kein Android-PASS** für .26-Suche,
  Sofortaufnahme oder Offline-Wiedergabe. #118 und #121 bleiben offen.
- Die nächste vorgesehene Entwicklung ist **0.1.29.27**, vorbehaltlich einer
  erneuten Prüfung der Versionsbelegung vor dem Paketbau. Spätere Pakete erhalten
  jeweils eine eigene höhere Version. Keine unterschiedlichen ZIPs unter .26.

## P0 #121: gesicherter Codebefund

### Großer Guide

1. `guide_grid_window.py:13–23` speichert den Playerzustand beim Konfigurieren
   des Guides, also vor dem späteren Klick auf „Jetzt ansehen“.
2. `_actions():170–195` erzeugt nur einen Intent und setzt `_leaving`.
   Der Owner-Pump schließt nach mindestens 150 ms, außerhalb des nativen
   Eingabe-Callbacks. Wiederholtes OK/Back wird währenddessen verworfen.
3. `open_grid():401–407` liefert den Intent ohne WindowXML-Referenz.
   `app_routes.py` ruft `open_route(..., after_close=guide_playback.handoff)` auf.
4. `window_navigation.py::open_route` verlässt die Ownership-Phase vor
   `after_close`. Die gewünschte Reihenfolge ist bereits vorhanden; sie darf
   nicht durch einen vorschnellen direkten Player-Aufruf ersetzt werden.
5. `guide_playback.py:27–56` verbraucht den Intent einmal und wartet höchstens
   zwei Sekunden auf das inaktive Guide-Fenster und das Ende modaler Dialoge.
   Danach folgen Player-, Portal-, Reader-/Gruppen- und Session-Prüfungen.
6. Nur bei Erfolg folgt der existierende Live-TV-Resolver über
   `PlayMedia(action=play_live)` bei Xtream beziehungsweise `source_play` bei
   M3U/STB. `DISPATCHED` bedeutet nur, dass Kodi den Startbefehl erhalten hat,
   **nicht**, dass bereits ein Bild läuft.

### Nachgewiesene Diagnose-Lücke

`guide_playback.py:59–67` fasst sämtliche False-Rückgaben und Exceptions als
`SKIPPED` zusammen und zeigt dieselbe Meldung `33122`. Die Marker enthalten
keine gemeinsame zufällige Aufrufkorrelation oder Ablehnungsgrundcodes.
Auch ein SQLite-Lesefehler ist von einem geänderten Player nicht unterscheidbar.
`Reader` verwendet hier standardmäßig zwei Sekunden SQLite-Busy-Timeout ohne
SQL-Laufzeitgrenze; die zweisekündige Fensterfrist begrenzt **nicht** den gesamten
Handoff einschließlich nachfolgender Datenbankzugriffe.

Isolierte Host-Proben mit dem bestehenden temporären Kodi-Fixture bestätigen:

| Simulierte Ursache | Ergebnis | Stufe | Meldungen |
|---|---|---|---|
| Portal stimmt nicht überein | False | SKIPPED | 1 |
| Sender fehlt im erlaubten Index | False | SKIPPED | 1 |
| Playerzustand hat sich verändert | False | SKIPPED | 1 |
| LiveSession hat sich verändert | False | SKIPPED | 1 |
| Reader wirft IndexReadError | False | SKIPPED | 1 |

Das belegt den Informationsverlust, **keine** dieser fünf Ursachen am Nutzergerät.
Das neue Fehlerlog und der konkrete Fehlertext zu E05 liegen weiterhin nicht vor.
Der ältere Wechsel `QUEUED → SKIPPED` und der spätere erfolgreiche Dispatch
beweisen weder eine zu kurze Frist noch einen defekten Provider.

### Abweichender zweiter Guide und Schutzlücken

`guide_window.py:213–218` schließt im nativen Callback und ruft sofort
`PlayMedia(action=play_live)` auf. Es gibt dort keinen nachgelagerten
`after_close`-Handoff und keine entsprechende Portaltyp-Verzweigung.
Dieser Pfad ist konkret anders, aber seine Beteiligung am aktuellen Fehler im
großen Guide ist nicht belegt. Erst durch eine eigene Reproduktion erweitern.

Die vorhandene Playergleichheitsprüfung erkennt eine **neu gestartete** fremde
Wiedergabe. Eine bereits beim Öffnen laufende, anschließend unveränderte fremde
Wiedergabe wird allein dadurch nicht als fremd ausgeschlossen. Dieser Fall muss
in den Schutztests ausdrücklich neben eigenem Live-TV und Playerwechsel stehen.

## P0 #118: .25-Befund und bereits vorhandene .26-Korrektur

Im veröffentlichten .25 setzte `MediaWindow._search()` nach der Tastatureingabe
`_next_route` und schloss das Fenster. `open_media()` startete anschließend
`Container.Update(global_search)`, während `open_route` die Navigationssperre
noch hielt. Die fast gleichzeitigen Home-/Search-Dispatches im privaten Log passen
zu einer problematischen Transition. Ein nativer Crashstack fehlt; der genaue
Android-Absturzmechanismus bleibt unbewiesen.

**Bereits in .26 enthalten:** `media_search.py` hält Eingabe, asynchrone lokale
Treffer, Rubriken LIVE-TV/FILME/SERIEN und die existierenden Medien-Details im
gleichen WindowXML-Owner. Echte Counts, Seiten zu 48 Einträgen, EPG-Jetzt-Suche,
manuelle EPG-Zuordnung, Gruppenfilter und Fehlerzustände sind vorhanden.
Live-Treffer verwenden nach Owner-Freigabe denselben `guide_playback.handoff`.
Die Behebung von #121 muss deshalb später auch diesen Such-Live-Pfad prüfen.

**Nicht vollständig abgedeckte Einstiege:**

- `guide_grid_window.py:365–369,401–403` schließt für die Suche weiterhin im
  Callback und startet `Container.Update` vor Freigabe von `open_route`.
- `guide_window.py:162–170` besitzt weiterhin einen eigenen Close/Update-Pfad.
- `app_routes.py::search()` erhält den Legacy-Directory-Pfad für positive Handles;
  dessen leere Eingabe/Abbruch und Container-Rückkehr sind eigenständig zu prüfen.
- `.26` routet negative `global_search`-Handles zur eigenen Ergebnisansicht.
  Ein Directory-Einstieg ist nicht automatisch mit diesem Action-Einstieg gleichzusetzen.

Diese Restpfade sind ein konkreter Untersuchungsumfang für eine Folgeversion.
Ohne Android-Nachtest darf weder #118 geschlossen noch ein erneuter Fix für einen
bereits in .26 korrigierten Film-/Serieneinstieg behauptet werden.

## Kleine, getrennt abnehmbare Entwicklungs-PRs

| Reihenfolge | Eigener Branch / Umfang | Tests und Android-Gate |
|---|---|---|
| A – P0, nächste Version vorzugsweise .27 | `fix/xcmate-02927-epg-handoff`: #121; zuerst zufällige Handoff-Korrelation, feste Reason-Codes und begrenzte Zugriffe; eine reproduzierte Lifecycle-Ursache mit kleinem Diff korrigieren. Keine Splash-/Detailarbeit. | Jeder Abbruchgrund einzeln; Timeout mit noch aktivem Guide und Modalzustand getrennt; Shutdown; SQLite busy; Doppel-OK; genau ein Resolverstart nach Owner-Release; eigener Live-Player und fremder Player. Android: beide „Jetzt ansehen“-Einstiege, mehrere Gruppen, Stop/EPG/Neustart, langsamer Skin, EPG-Fokus und IR. |
| B – P0-Restumfang nach .26-Nachtest | `fix/xcmate-search-entry-lifecycle`: #118/#25; verbliebene EPG-/Legacy-Suche reproduzieren, Transition erst nach Owner-Freigabe oder im vorhandenen Owner; .26-Ergebnisansicht wiederverwenden. Keine Aufnahmenerweiterung. | .26-Suche zunächst real prüfen; Upload, Abbruch, leer, Nulltreffer, DB-/Indexfehler, schnelles OK/Back, erneute Suche, Film-/Seriendetails/Back und Live-EPG-Treffer; getrennte Action-/Directory-/EPG-Einstiege. |
| C – P1, eigener UI-PR | `feat/xcmate-lightweight-splash`: #122; ausschließlich Original-Splash lokal ins Core-Bundle, einheitlicher Lightweight-Fallback für Home, Film-/Serien-Landing und sinnvolle Settings/Guide-Flächen. | Asset-Hash und ZIP-Inhalt; offline ohne Premium-Paket; keine Premium-Aktivierung, keine Änderung an Fokusgraph oder Originalicon. Android-Kontrast und IR auf allen genannten Seiten. |
| D1 – P1, eigene lokale Detailseite | `feat/xcmate-programme-details`: #123/#88; eigenes `XCMateProgramme.xml`, vorhandene Programmdaten, Logo und lokaler Fallback, ownergesteuerte Aktionen. EPG-Senderstart aus A wiederverwenden. | Lange Beschreibung, fehlende Daten, laufend/vergangen/zukünftig; Back erhält Gruppe, Achse, Sender und Zelle; Fokus sichtbar; keine GUI-Netzarbeit. Android vor Freigabe. |
| D2 – separate Erweiterung | `feat/xcmate-programme-artwork`: verifizierte Provider-/EPG-Bilder, persistenter Cache; externer Abgleich erst nach Klärung von API/Key/Attribution und eindeutiger Identität. | Kein Titel-Raten bei Nachrichten/Sport/Remakes; kein Treffer/Mehrdeutigkeit/Offline/Timeout; falsches Bild nicht speichern; vorhandene READY-Bilder erhalten. |
| E – P1, eigener Einstieg | `fix/xcmate-skin-live-shortcut`: #120; tatsächliche Skin-Action prüfen, Startsender ohne wiederholtes Lesen großer Kataloge vorbereiten; Rückkehr zu XCMate-Home und EPG. | Kalt-/Warmstart am Gerät messen, Abbruch und fehlender Cache, keine Fremdplayer-Übernahme; bestehende IR-Belegung unverändert. Kein natives PVR versprechen. |
| F – P1, eigener Artwork-PR | `fix/xcmate-poster-fallback`: #111; selektiver Retry, verifizierte alternative Quelle; TMDB nur kontrolliert und identitätsgebunden nach API-/Rechteklärung. | TIMEOUT/404/429/DB_BUSY, gleichnamige Titel/Jahre, korrektes Bild nach Neustart/offline, kein globaler Retry und keine Löschung. |

Für A: vorgeschlagene Codes `WINDOW_WAIT_TIMEOUT`, `MODAL_BLOCK`,
`PLAYER_CHANGED`, `PLAYER_UNAVAILABLE`, `FOREIGN_PLAYER`, `PORTAL_DISABLED`,
`PORTAL_MISSING`, `CHANNEL_NOT_FOUND`, `INDEX_BUSY`, `INDEX_READ_FAILED`,
`SESSION_CHANGED`, `SHUTDOWN`, `RESOLVER_START_FAILED` und `ALREADY_CONSUMED`.
Nur feste Codes und zufällige, nicht aus Portal-/Senderdaten abgeleitete Tokens
protokollieren. IDs, Namen, Stream-URLs und Exceptiontexte bleiben privat.
`DISPATCHED` von tatsächlichem Resolver-/Playererfolg trennen; ein fehlendes Bild
nach Dispatch ist kein Beweis für einen vorherigen Handoff-Fehler.

Die Zwei-Sekunden-Frist wird nicht ohne Reproduktion pauschal verlängert und die
Player-/Sessionprüfung nicht entfernt. Zunächst den konkreten Pfad messen.
Falls keine Ursache reproduzierbar ist, A ehrlich als Diagnosekandidat ausliefern,
ohne einen erfundenen Gerätefix oder Android-PASS zu behaupten.

## Paket- und Schutzregeln pro Implementations-PR

- Eigener Draft-PR, Changelog, vollständiges automatisiertes Testergebnis,
  installierbares Android-ZIP, SHA256 und eine Testanleitung mit klaren Gates.
  Keine neuen Funktionen als bestanden ausweisen, bevor der Nutzer sie getestet hat.
- Vor jedem Paket Versionsnummer gegen main/offene PRs prüfen. .26 bleibt
  unveränderter, separat installierbarer Stand; .25-ZIP bleibt Rückfalloption.
- Geschützte Autoplay-/Resume-/Live-Dateien per Hash beziehungsweise begrenztem
  Funktionsdiff prüfen. Änderungen an `media_window.py` dürfen die dortigen
  eingefrorenen Playback-/Autoplay-Teile nicht verändern.
- Keine Portale, Gruppen, EPG-Zuordnungen, Favoriten, Resume-/Gesehen-Daten,
  Artwork-Jobs oder Bilddateien löschen; kein DB-Reset und keine globalen Keymaps.
- Keine automatische Space-Premium-Aktivierung. Originalicon SHA256:
  `81da1003a2753ec6afbdd50b2a320e738a2131ad9f0d76606da1babdd0d2f135`.
- Original-Splash für C SHA256:
  `2553464f81de674f3de8726ba1ec81dcf57d7c0232d39aa3322af10ee0435fcc`.
- #98 bleibt separat geplant. M07 bleibt Android-NOT_TESTED: Aufnahmeordner
  öffnen/abbrechen und Theme-ZIP-Dateiauswahl separat mit D-Pad prüfen.
- Die einfache .26-Sofortaufnahme bleibt erhalten. EPG-Timer, Downloads und
  Meine Medien werden nicht in diese P0-Korrekturen aufgenommen. Draft #117
  bleibt ein historischer Prototyp und wird nicht zusätzlich pauschal gemergt.
- Die ausdrückliche Freigabe dieses Chats gilt für den Merge von **.26**.
  Sämtliche Folgeversionen bleiben ohne neue Freigabe ungemergt/unveröffentlicht.

## Bereits verifizierte Ergebnisse dieser Analyse

Auf unverändertem .26-Merge-Code lokal erneut ausgeführt:

- `test_xcmate_epg_handoff_02916.py`: **9 PASS**, 0,533 s.
- `test_xcmate_search_02926.py`: **14 PASS**, 0,634 s.
- Fünf isolierte Fehlerproben wie oben: alle erwarteten Ablehnungen bestätigt.
- Diese Host-Fixtures testen Python-Logik und Owner-Reihenfolge, keinen echten
  Android-Kodi-GUI-Thread und keinen nativen Crash. Vorhandene Tests sind deshalb
  kein Gegenbeweis zum gemeldeten E05-/M04-FAIL.
- .26-Lieferung: **891 lokale Tests und 891 GitHub-PR-CI-Tests PASS**,
  [Run 200](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39974618635).
- Unverändertes .26-ZIP SHA256:
  `bbf031b9e5677f04894024f4e273d57f4b4cbb470644119be7dbd02b63e26744`.
- [Android-Testanleitung für .26](ANDROID_TEST_02926_DE.md).
  Der darin noch als offen geführte alte Staffelübergang ist durch die neuere
  Nutzerabnahme zu P02/#85 überholt; das ZIP selbst bleibt unverändert.

Der reguläre main-Publish-Build nach Merge ist
[Run 39986010193](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39986010193).
**Main-Publish erfolgreich: 891 Tests in 116,145 s, keine Hintergrundthread-Ausnahme,
Publish SUCCESS.** Der tatsächlich konfigurierte raw-main-Update-Index enthält
.26; dessen MD5 stimmt. Das daraus heruntergeladene ZIP hat 1.793.918 Bytes,
166 Dateien, gültige CRCs und exakt die oben genannte SHA256 des Testkandidaten.
**.26 ist damit als reguläres GS-Media-Repository-Update verfügbar.**
Die offene Android-Abnahme wird dadurch nicht ersetzt.
