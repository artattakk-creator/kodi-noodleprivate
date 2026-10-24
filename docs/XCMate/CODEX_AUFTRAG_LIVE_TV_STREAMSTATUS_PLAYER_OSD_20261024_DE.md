# XCMate – Codex-Entwicklungsauftrag: Streaminformationen in der ersten Live-TV-Infobar und echtes Player-OSD

**Auftrag / verbindlicher Nutzerwunsch:** 24.10.2026  
**Status:** SPEZIFIZIERT – NOCH NICHT IMPLEMENTIERT / KEIN ANDROID-PASS  
**Produkt:** XCMate / GS Media – Kodi-Add-on `plugin.video.xtreammate`  
**Repository:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Test-Baseline beim Schreiben:** `main` Add-on 0.1.29.30; aktuell läuft ein gesonderter .31-Codex-Testzyklus  
**Android:** RK3528 ARM32 / Android TV 13 / Kodi 21.2 Omega / Titan BINGIE MOD 2.2.3 / IR-Remote / 1920×1080; gegen Estuary und 720p skalieren.

> **Verbindliche Übergangsregel (#143):** Der bereits laufende Codex-Entwicklungs-/Testzyklus wird zunächst abgeschlossen und auf Android geprüft. **Diesen Auftrag erst im folgenden freigegebenen Entwicklungszyklus implementieren**; keine Änderungen in laufende .31-Branches injizieren. Keine eigenmächtigen Merges, Releases, Änderungen am Nutzerprofil, Downgrades oder Datenlöschungen. Der Auftrag beschreibt nicht einen bereits bestehenden Android-PASS.

## 1. Bezug / Abgrenzung

- **#17:** 1× OK = vorhandene erste Infoleiste; 2× OK bzw. Runter = zweite Player-Leiste. Sender-/Gruppen-/Mini-EPG-Navigation, Now/Next und Fortschrittsbalken schützen.
- **#100:** Die bereits erfassten tatsächlichen Streaminformationen sind **nun ausdrücklich verbindlicher Bestandteil der *ersten* Infoleiste**, mit Mini-Icons am **untersten Rand**, nicht erst auf einer separaten technischen Detailseite.
- **#94 / #150:** künftige gemeinsame vertikale Rail; diese Erweiterung darf deren fünf Links-Ebenen oder den Sidebar-Fokus nicht überschreiben.
- **#79:** Film-/Serien-Player-OSD ist **separat**. Gemeinsame Icon-/Action-Contracts sind erwünscht, aber hier **nur Live-TV** ändern und VOD nicht ungetestet übernehmen.
- **#63 / #126 / #62 / #135 / #136:** Video-Downloads und Aufnahmen gemäß neuer Roadmap zurückgestellt. Keine Wiedereinführung von Aufnahme-/Download-Projekten durch diesen Auftrag.
- **#99:** Catch-up ist eine separate echte Provider-Archivfunktion, nicht mit lokalem Timeshift verwechseln.
- **Original-XCMate-App-Icon, Portal-/EPG-/Favoriten-/Resume-Daten sowie Staffel-Autoplay** unverändert.

## 2. Ist-Code bei Prüfung von `main` am 24.10.2026

Relevante Dateien in `src/plugin.video.xtreammate/resources/lib/`:

- `live_overlay.py::LiveNavigator._build_controls`: vorhandene `info_*`-Kontrollen und `_info_controls`; `main_buttons` mit Index 0 Pause/Weiter, 1 −10 s, 2 +30 s, 3 Stop, 4 Weitere, 5 Live-Ende; `extra_buttons` mit Ton, Bild, Untertitel, EPG, Einstellungen, Gruppen.
- `_render_info()` zeichnet EPG-Senderlogo, Jetzt-/Danach-Titel, Zeiten und Fortschritt, **bisher ohne technische Stream-Badges**.
- `_render_transport()` wechselt bereits das erste Symbol abhängig von `Player.Paused` zwischen `tv_play.png` und `tv_pause.png` – **nicht neu erfinden**, sondern einheitlich zu echtem Player-Design ausbauen.
- `_can_seek()` prüft derzeit `Player.SeekEnabled` plus endliche `getTotalTime()>5`; **für Live/Timeshift hinsichtlich echter Seek-Fähigkeit und Grenzen verifizieren**, keine pauschalen Annahmen.
- `_execute()` sendet Pause, −10/+30 s, Live-Ende, Stop; aktuell keine getrennten optischen Funktionen für „Spulen“ und „Sprungmarke/Kapitel“.
- `_handle_command()`: `hidden → OK → info → OK/Down → controls`; `controls → Down → extras`; Back von `controls` zu `info`, Back von `info` zu `hidden`. D-Pad-Left/Right in `controls` bewegt den Fokus. Bestehende `remote_control.py` / `remote_bridge.py` und Native-`onAction`-`onControl`-Dedupe schützen.

**Kodi-Quellen zur API-Prüfung:** [offizielle InfoLabels](https://kodi.wiki/view/InfoLabel) und [Kodi-Entwicklerreferenz](https://xbmc.github.io/docs.kodi.tv/master/kodi-dev-kit/modules__infolabels_boolean_conditions.html) dokumentieren unter anderem `VideoPlayer.VideoResolution`, `VideoPlayer.VideoCodec`, `VideoPlayer.AudioCodec`, `VideoPlayer.AudioChannels`, `VideoPlayer.VideoAspect`, `VideoPlayer.VideoBitrate`. Die [Kodi JSON-RPC-Beispiele](https://kodi.wiki/view/JSON-RPC_API/Examples) zeigen `Player.GetActivePlayers`, `Player.GetItem(...streamdetails...)` und `Player.PlayPause`; auf **Kodi 21.2** Verfügbarkeit und Aktualität des jeweils tatsächlich aktiven Streams testen. Kein Aufruf unbestätigter Kodi-22-APIs.

## 3. Erste Infoleiste (1× OK): winzige Stream-Statuszeile am unteren Rand

**Bisherige Programminformationen und deren Layout/Funktion bleiben:** Senderlogo, Name, Sendung jetzt/nächste, Start–Ende, EPG-Progress, verstrichene/verbleibende Zeit, vorhandener Bedienhinweis.

**NEU** als zusätzliche kleine, optisch zurückhaltende unterste Zeile innerhalb der Infobar (in der Safe-Area):

| Piktogramm | Angezeigte Information | Sicherer Datenursprung / Anzeige |
| --- | --- | --- |
| Lautsprecher | `Stereo` / `Mono` / `5.1` / `7.1` | tatsächlich aktiver Audiotrack mit belegten Kanälen, nicht aus Codec abgeleitet |
| Audio/Badge | `AAC`, `AC-3 / DD`, `E-AC-3 / DD+`, ggf. PCM/DTS | tatsächlich gemeldeter Audiocodec; **kein Atmos aus DD+ ableiten** |
| Bildschirm/Auflösung | `720p`, `1080p`, `2160p` oder `1920×1080` | Dekodierstream, nicht Sendername / TV-HDMI-Ausgabe; **p/i nur wenn tatsächlich belegbar**, sonst neutral `1080` bzw. Pixelmaß |
| Film/Codec | `H.264`, `HEVC`, `AV1` | tatsächlich aktueller Videocodec |
| Optional | `25 fps`, `50 fps`, `16:9`, HDR, aktive Sprache/Untertitel | **nur wenn** Kodi-21-API/aktive Spur diese Werte verlässlich bietet |

**Wichtig:** Kanalkennungen wie „UHD“, „HD“, „Dolby“ oder XMLTV-/Provider-EPG-Angaben sind **kein Beweis** für die tatsächlich dekodierte Eigenschaft. Nicht aus Kanalnamen ableiten. Codec ≠ Lautsprecher-Ausgabeformat; `5.1` beschreibt belegte Quell-Audiokanäle, nicht automatisch die physische Lautsprecherkonfiguration. Fehlt eine verlässliche Information, Badge weglassen oder neutral `–`/`Unbekannt`; keinerlei Fantasiewerte, kein falsches `1080p` für nachweislich interlaced bzw. unbekannte Scanart.

### Gestaltung
- Winzige, aber auf ca. 2–3 m TV-Abstand noch lesbare Schrift und 16–24-px-Basissymbole auf 1080p, Kontrast auch auf hellen Szenen; innerhalb der Infobar unten links/rechts ausrichten, **nicht außerhalb des sichtbaren Panels**.
- Dezent, einheitlich XCMate-Space-/Lightweight-Grau, mit Safe-Area; bei Platzmangel Abkürzungen oder weniger Badges statt EPG-Titel / Zeit / Fortschritt zu verdrängen. `info_hint` ggf. sauber versetzen.
- Kleine Icons **einheitlich aus Tabler Icons**, keine proprietären Dolby-/DTS-Logos. Benötigte Assets upstream versionsgepinnt beziehen, Lizenz-/Copyrightvermerk (MIT) erhalten und offline nutzbare PNGs im minimalen XCMate-Build mitliefern. Die genauen Namen gegen die gepinnte Version prüfen (z. B. speaker/volume, device-tv, movie, subtitles).
- Die Infozeile darf beim ersten Öffnen leer sein und nach Beginn von Kodi-Streammetadaten gezielt aktualisiert werden; keine endlosen Animations-/Spinner-Schleifen.

## 4. Zweite Ebene (Info → Down / 2× OK): echtes Player-OSD

**Visuelles Ziel:** Ein sofort wiedererkennbarer Videoplayer mit **deutlich erkennbaren, symmetrisch angeordneten Transport-Symbolen**, nicht nur Text-Buttons. Laufendes Video bleibt sichtbar.

**Beispiel der Aktionslogik (die konkrete Gruppierung kann ergonomisch optimiert werden):**

`[Zurückspulen] [−10 s] [Play/Pause] [+30 s] [Vorspulen] [Live-Ende] [Stop] [Weitere]`

- **Dynamisches Play/Pause-Piktogramm:** Wenn Wiedergabe **pausiert** ist, Dreieck **Play (▶)** als nächste Aktion anzeigen; bei **laufender Wiedergabe** Balken **Pause (Ⅱ)** als nächste Aktion. Nach OK aktualisiert die UI erst mit **bestätigtem** Playerzustand; keine voreilige Anzeige, wenn Pause nicht unterstützt wird. Der zweite OK-Tastendruck zum Öffnen des Players **darf keine Play/Pause-Aktion auslösen**.
- **Zurück-/Vorspulen:** Für tatsächlich seek-/trickplayfähige Player ggf. zeitliche Navigation auf der Timeline; konkrete FF/REW-Modi nur über auf Kodi 21.2 nachweislich unterstützte Aktionen mit korrektem Status/Rate. **Nie** unimplementierte FF/REW-Icons als aktiv vortäuschen. Zulässig: sichtbare deaktivierte Icons bei Live ohne Timeshift.
- **Sprung zurück/vor:** Distinkte `−10 s` und `+30 s` als verlässliche Zeit-Sprünge nur innerhalb des echten seekbaren Zeitfensters. Kapitel-/Sprungmarken-Icons (⏮/⏭) **nur bei echten Kapiteln/Marken** aktiv; niemals still als Senderwechsel oder unbekannten EPG-Event-Skip verwenden. Label/Tooltip macht Bedeutung verständlich.
- **Live-Ende:** nur aktiv, wenn bekanntes Timeshift-/Seekfenster und eine unterstützte „zum Live-Rand“-Funktion existiert; sonst nicht anbieten/ausgrauen.
- **Stop:** führt bewusst nur zum bereits implementierten sicheren XCMate-Live-Exit (kein Stop fremder Player, kein versehentliches Kodi-Home; Back ist **nicht** Stop).
- **Weitere:** öffnet die dritte Ebene mit funktionierenden, verifizierten Aktionen **Ton**, **Bild**, **Untertitel**, **EPG**, **Einstellungen**, **Gruppen**. Icons für diese Bereiche ebenfalls aus Tabler; Kodi-native Settings nur wenn sie am aktiven Player funktionieren und Fokus sicher zurückkehrt.
- **Status-/Timeline:** Falls seekbar, echte Zeitposition, Gesamtdauer/seek window, hervorgehobener Timeline-Marker; bei linearem Live ohne Timeshift statt Fake-Timeline eindeutiger **LIVE**-Status. EPG-Sendungsfortschritt darf nicht fälschlich die Video-Seekposition ersetzen.
- Fehlende Funktion **sichtbar deaktiviert** und von Fokusnavigation übersprungen; keine Taste auf verbotene Aktion. Kurze Erklärung etwa `Spulen bei Live-TV ohne Timeshift nicht verfügbar` nur nach explizitem Versuch/Hinweis – keine ständigen Benachrichtigungspopups.

### Layout / Icons
- TV-taugliche einheitliche Player-Darstellung, mittige Play/Pause-Aktion optisch prominenter, echte Play-Dreieck- und Pause-2-Balken-Symbole, klare Gruppierung der Pfeile/Skip.
- Tabler Icons aus derselben Bibliothek wie #94/#150 (exakte Upstream-Iconnamen und Lizenz beim Build prüfen): `player-play`, `player-pause`, `player-stop`, `player-skip-back`, `player-skip-forward`, `rewind-backward-10` / `rewind-forward-30` bzw. kompatible Gegenstücke, `volume`, `subtitles`, `settings`, `device-tv`. Kein Google/CDN-Laufzeitabruf. Nur benötigte Icondateien; für Kodi PNG-Texturen vorbereiten, Fokusfarben per UI-Theme.
- Zustände **normal, fokussiert, aktiv, pausiert, deaktiviert** eindeutig unterscheidbar (Kontrast/Fokusrahmen nicht bloßer Farbschimmer). Offen, Back oder Senderwechsel darf keine Pixel-/Control-Überlagerung zurücklassen.

## 5. Bedienung / Zustandsmaschine – NICHT brechen

| Ausgangszustand | Taste | Gewünschter Folgezustand / Wirkung |
| --- | --- | --- |
| Live-Vollbild (`hidden`) | OK | `info`; kein Pause/Stop, kein Kodi-OSD |
| `info` | OK **erneut** / Down | `controls`; **nur öffnen**, auf demselben Tastendruck keine Buttonaktion |
| `info` | Back | `hidden`; Wiedergabe läuft weiter |
| `controls` | Left/Right | genau **einen fokussierten** Player-Button bewegen, keine Sendernavigation |
| `controls` | OK | genau **eine** fokussierte und unterstützte Player-Aktion |
| `controls` | Down | `extras` (Ton/Bild/Untertitel/EPG/Einstellungen/Gruppen) |
| `controls` | Back / Up | `info`, keine Playback-Unterbrechung |
| `extras` | Back/Up | `controls`, vorherigen Player-Fokus erhalten |
| `hidden` | Up/Down | bestehenden Senderwechsel ±1 unverändert |
| `hidden/info` | Left | bestehende Mini-EPG-/Senderliste, nicht Kodi-OSD |
| `channels` / `groups` | Left | #94 Nav-Rail-Migration später in eigenem Auftrag; niemals durch Player-Leiste beschädigen |
| beliebiger eigener Live-Zustand | expliziter Stop/Exit | Besitz-/Sessionprüfung und sichere Rückkehr |

- Native Kodi-IR und optionales XCMate-Bridge-Keymap-Fallback entprellen/deduplizieren; **kein globaler Kodi-Keymap-Eingriff**, keine Fremd-Add-on-Interaktion. `onAction`, `onControl` und Fokus-ID nur bei sichtbarem, enabled Control ansteuern; vorhandene Kodi-`Control 120 … can't focus`-Fehler bei Media-Window getrennt untersuchen.
- Nach Ton-/Untertitel-/Bildeinstellungen in den richtigen XCMate-Kontext zurückkehren; bei Playerwechsel/Stop/Window-Exit keine Leiste über fremdem Video. Live-Tune/Session-Nonce, Startsender, Favoriten, EPG und gespeicherte Einstellungen erhalten.

## 6. Technische Realisierung und Leistungsbudget

- Für Video- und Audiostatus Kodi-21-`VideoPlayer.*`-InfoLabels und/oder tatsächlich vorhandene aktive Player-Streaminfos nutzen; auf TV-Gerät vergleichen, ob aktuell gemeldete Daten verlässlich sind. **Keine nicht dokumentierten Kodi-22-only-APIs voraussetzen**.
- Leichtgewichtiges `LiveStreamInfoSnapshot` mit `session_nonce / pid / sid`, Audio-/Video-Signalwerten, Zeitstempel und Source/Validität; kein Polling für 2.764 Sender. Bei Streamstart ggf. kurz Unknown, danach gedrosselt **nur für aktiven eigenen Live-Player** aktualisieren (z. B. höchstens 1×/s, soweit nötig), schnelle Aktualisierung bei Sender-/Track-Wechsel. Kodi GUI nur auf GUI-Thread aktualisieren; kein HTTP, XMLTV, SQL-Abfrage, Bilddownload im IR-Handler.
- Der Kodi-Player ist weiterhin die Wiedergabeengine. **Keinen eigenen Decoder**, keinen neuen Stream-Proxy und keinen neuen Timeshift-/Recorder-Backendaufbau für diese UI-Funktion entwickeln. Capability-Featureflags vom aktiven Kodi-Player bestimmen; sichere positive Capabilities von tatsächlichem Seek/Pause trennen, nicht blind nur `duration>5` als Seekbeweis.
- Bestehende `_render_info`, `_render_transport`, `_can_seek`, `_execute`, `_build_controls` lokal erweitern statt Overlay-Navigation neu zu schreiben. Layout auf 1920×1080 / 1280×720 sowie Titan BINGIE MOD und Estuary prüfen; bestehende Player-Fokus-ID und die #94-Rail-Routen schützen.
- Keine vollständigen Stream-URLs, Zugangsdaten, Medien-/Benutzer-IDs, Cookies, private Logs oder vertrauliche Sendernamen öffentlich protokollieren. Fehlerdiagnose nur aggregiert und datensparsam.

## 7. Verbindliche Akzeptanztests

### Statuszeile (INFOSTREAM)
- **INFOSTREAM1:** 1× OK zeigt unveränderte Sender-/Jetzt-/Danach-EPG-Info plus unten kleine Stream-Icon-Reihe ohne Überlappung.
- **INFOSTREAM2:** Aktiver AAC-2.0-/AC3-5.1-/EAC3-Stream zeigt **belegte** Audio-/Kanalwerte, kein erfundenes Atmos. Audio-Track-Wechsel aktualisiert korrekt.
- **INFOSTREAM3:** SD/720/1080/2160-Auflösung auf realem dekodiertem Stream; Sendername „UHD“ bei tatsächlich 720 zeigt NICHT 4K. `p/i` nur bei gültigen Scanmetadaten.
- **INFOSTREAM4:** Keine/verspätete Kodi-Streaminfos: kein falscher Wert, kein UI-Hänger, spätere Statusaktualisierung möglich.
- **INFOSTREAM5:** Senderwechsel, EPG-Now/Next, Back/OK und Untertitelwechsel aktualisieren Snapshot ohne alten Sender-/Player-Status.
- **INFOSTREAM6:** Layout in 720p/1080p, optional Space Premium und Standard-Lightweight; Audio/Icon-Safe-Area und Fernbedienbarkeit.

### Player-OSD (PLAYEROSD)
- **PLAYEROSD1:** 1× OK = Info, 2× OK = Player; **zweites OK pausiert nicht**; Down aus Info = Player.
- **PLAYEROSD2:** Bei tatsächlich pausierbarem Player **Play → nach erfolgreicher Wiedergabe Pause-Icon**, Pause → nach bestätigtem Pausenstatus Play-Icon; Icon folgt dem echten Zustand, keine Ghost-Toggles.
- **PLAYEROSD3:** Live ohne seekbares Fenster: FF/REW, ±10/30 s, Kapitel/Live-Ende deaktiviert; Play/Pause nur soweit tatsächlich möglich; Stream läuft stabil.
- **PLAYEROSD4:** Seekbarer Timeshift-/Archiv-Teststream: ±10 s / +30 s trifft korrekt begrenzte Position; FF/REW und Kapitel nur wenn jeweilige Kodi21-Capability bestätigt, sonst deaktiviert.
- **PLAYEROSD5:** Fokus Links/Rechts jeweils exakt ein Button; D-Pad/OK keine Doppelaktion, klarer Focus Frame; versteckte/deaktivierte Controls nie fokussieren.
- **PLAYEROSD6:** Down öffnet echte extras, Ton/Untertitel/Bild nur unterstützte native Dialoge, Back/Up zurück; keine native Kodi-OSD-Übernahme.
- **PLAYEROSD7:** Stop über XCMate-eigene Aktion beendet nur eigenen Live-Stream; Back schließt nur Leiste; keine Fremdplayer-Störung oder Hintergrundton.
- **PLAYEROSD8:** EPG-Senderliste, Gruppen, späterer Rail-Pfad (#94/#150), Zap Up/Down im Vollbild und Startsender bleiben unverändert.
- **PLAYEROSD9:** Wiederholung von mindestens **20 IR-Zyklen** (OK→OK→Left/Right/Back) und schnelles Drücken, wechselnde Kanal-/Codec-/Audiozustände, kein Fokusverlust oder GUI-Block.
- **PLAYEROSD10:** Kodi 21.2/RK3528/Android 13 BINGIE MOD und zusätzlich Estuary; Offline-Assets, keine nachgeladenen CDN-Icons, Original-XCMate-Icon unverändert.

**Regression:** S1–S5 gemäß #143 bei einem neuen Release einmal, gezielte #17/#100/#94/#125-/EPG-/Live-Exit-Tests; **keine ungefragte vollständige Wiederholung historisch bestandener 29 Tests**. Codex-Unit-Tests können die Android-IR-/Player-Abnahme nicht ersetzen.

## 8. Lieferumfang von Codex

1. Dokumentiere vor Implementierung die **aktuell wirklich vorhandenen Kodi-21-Capabilities** (Status und Seek/PlayPause, Fallback bei fehlenden Infos), bisherige Icons/OSD-Kontrollen und eine kompakte State-/Fokusmatrix.
2. Implementiere die beiden UI-Ergänzungen additiv aus aktueller freigegebener `main`-Basis **nach Abschluss des bereits laufenden Codex-Zyklus**; Branch plus **Draft-PR**, nicht in bestehende unfertige .31-PRs mischen.
3. Liefere nur erforderliche, lizenziell dokumentierte Tabler-PNG-Texturen und Asset-Manifest mit Upstream-Version/Quelle/Hash + MIT-Notice.
4. Automatisierte Unit-/Integrationstests für Statusklassifizierung, verspätete Playerinfos, dynamische Play/Pause-Icons, Seek-Capability, Player-State-/Remote-Transitions, Focus/Dedupe, Back/Stop/Owner, Nicht-Verfügbarkeit.
5. Android-Test-ZIP + **SHA256**, kurze Abnahmecheckliste mit INFOSTREAM1–6 / PLAYEROSD1–10 und **Status NOT_TESTED vor echtem Gerätetest**, verständlicher Changelog und Risiko-/Regressionserklärung.
6. Dokumentations-/Fehlermeldungen ohne Zugangsdaten oder sensible Kodi-Rohlogs. **Kein selbstständiger Merge, Release oder OTA-Update; Nutzer entscheidet nach Android-Test.**

**Priorität:** nach Abschluss des gegenwärtigen .31-Testkandidaten, im neuen UI-/EPG-Roadmap-Zyklus. Ausdrücklich keine neue Download-/Aufnahme-Implementierung durch diesen Auftrag.
