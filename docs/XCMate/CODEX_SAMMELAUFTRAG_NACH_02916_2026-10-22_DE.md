# XCMate – gebündelter Codex-Korrekturauftrag nach Android-Abnahme 0.1.29.16

**Verbindlicher Nutzerauftrag 22.10.2026:** Die vollständigen Android-Ergebnisse als PASS/FAIL/NOT_TESTED auf GitHub erfassen und einen **priorisierten gemeinsamen Änderungsvorschlag** für den nächsten Teststand ausarbeiten. **Keine automatische Integration, kein Merge, kein reguläres OTA/Release ohne neue ausdrückliche Freigabe.**

## WEITERE VERBINDLICHE PRÄZISIERUNG 22.10.2026: Infobar mit technischen Icons und EPG-Name-Matching

**Diese neueren Anforderungen ergänzen alle vorhergehenden Spezifikationen, ohne den P0-Reparaturauftrag vorzuziehen.**

### E. [#100](https://github.com/artattakk-creator/kodi-noodleprivate/issues/100) – erweiterte XCMate-Live-TV-Infobar (NEUE To-do-Anforderung, P2 nach STOP-Fix)

Bei laufendem Live-TV soll die mit **1× OK** eingeblendete, bereits auf Android funktionierende XCMate-Infobar künftig eine kompakte Reihe informativer Status-Icons erhalten, ähnlich einem TV-Receiver:

- **Videoauflösung** aus der aktuell dekodierten Videobildgröße: SD/720p/1080p/2160p bzw. HD/FHD/UHD, mit sicherer Unterscheidung von Interlaced-/Progressive-Kennzeichnung, sofern Kodi sie tatsächlich liefert. **Nicht den Sendernamen als Auflösungsbeweis nutzen** – „ZDF FHD“ kann real mit einer anderen Auflösung spielen.
- **Videocodec**: H.264/AVC, H.265/HEVC, AV1 usw. nur wenn die Kodi-21.2-Player-Schnittstelle diese Information zuverlässig meldet; ggf. HDR/SDR und Bildrate, sofern belegbar.
- **Tonformat**: AAC, PCM, AC-3/**Dolby Digital**, E-AC-3/**Dolby Digital Plus**, DTS usw.; **Stereoton (2.0), 5.1, 7.1**, Audiospur-/Sprachkennzeichnung. **Dolby Atmos nur mit tatsächlichem Atmos-Nachweis**, nicht allein wegen E-AC3. Keine rechtlich ungesichert verwendeten Dolby-Markenlogos; neutrale TV-taugliche Badges („DD“, „DD+“, „5.1“, „1080p“) sind akzeptabel.
- **Untertitel/CC** verfügbar/aktiv, ggf. Sprachspur; weitere Angaben über ein sauberes technisches Detailmenü statt erster Infobar zu überladen. Fehlende oder nicht zuverlässige Kodi-Metadaten als „unbekannt“ behandeln, keine erfundenen Statussymbole.
- Aufnahmen von **aktueller, eigener XCMate-Player-Session**, nicht aus XMLTV oder Dateinamensraten. Beim Sender-/Audiotrack-/Untertitelwechsel dynamisch aktualisieren, ohne blockierenden JSON-RPC-/HTTP-Call oder D-Pad-Latenz. Kodi 21.2-Kompatibilität von InfoTag-/Player-Properties belegen, Fallback auf Unbekannt. Display-Ausgabeauflösung nicht mit Stream-Bildauflösung verwechseln.
- **1× OK bleibt Infobar**, **2× OK/↓ bleibt Steuerleiste**, Links bleibt Mini-EPG. Existierende Jetzt/Danach-/Progress-Anzeige, Fokus, Stop-Hotfix und fremde Player nicht beeinflussen; BINGIE/Estuary-Skin und Space-Premium-kompatibles Design.
- Implementierung **als separater modularer UI-Draft-PR nach P0 #97**, wenn nicht zweifelsfrei konfliktfrei kombinierbar. Realgerätetests für 720p/1080i/1080p/2160p, AC3/EAC3/AAC, Ton-/Sprachwechsel, unbekannte Streams, Subtitle-Status, Senderwechsel, Stop und Kodi-Player-Lifecycle. **Kein Android-PASS ohne Gerätetest.**

**Code:** `resources/lib/live_overlay.py::_render_info()` zeigt bisher Senderlogo, Sendung Jetzt/Danach, Zeit und Progress, aber keine technische Videospur-/Tonspur-Iconzeile. Bestehende [#17](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17) (Infoleiste), [#20](https://github.com/artattakk-creator/kodi-noodleprivate/issues/20) (Remote-Steuerleiste), [#64](https://github.com/artattakk-creator/kodi-noodleprivate/issues/64) (Kontexttasten) als Schutzregeln berücksichtigen. Volle Spezifikation [#100](https://github.com/artattakk-creator/kodi-noodleprivate/issues/100).

### F. [#98](https://github.com/artattakk-creator/kodi-noodleprivate/issues/98) – EPG-Vorschläge auch bei Sendernamen mit HD/FHD/Joyn finden (P1, verbindlich)

Der Benutzer möchte bei „**EPG zuweisen**“ nicht selbst alle EPG-Namen durchsuchen müssen. Das Dialogfenster muss **den aktuell markierten Live-Sendernamen als vorgefüllten Suchbegriff verwenden**, passende EPG-Kanäle **aller bereits bekannten Anbieter automatisch vorschlagen und oben anordnen**, ohne vorzeitiges Speichern.

- Beispiel: **„ZDF“, „ZDF HD“, „DE | ZDF FHD“, „ZDF HEVC“, „Joyn ZDF“, „ZDF (Joyn)“** sollen trotz technischer Qualitäts- und Plattformzusätze denselben **Kernsender „ZDF“** erkennen und entsprechende Vorschaukandidaten liefern.
- Case-insensitive/Unicode-normalisierte Token-Suche. **Getrennt** kontrollierte Senderpräfixe/Länder, Qualitätsangaben wie SD/HD/FHD/UHD/4K/HEVC, Plattformmarken wie Joyn als mögliche Distributionszusätze entfernen. Danach exact-core vor alias-core vor vorsichtigem Fuzzy-Vergleich. Originalnamen, Anbieter und EPG-Kanal-ID in der Liste immer sichtbar; nicht alle Senderfamilien global zusammenführen.
- **Gefährlicher Fehler, ausdrücklich vermeiden:** Ein simples `'ZDF' in sendername` würde „ZDFneo“ und „ZDFinfo“ als identische Hauptstation behandeln. Diese **verschiedenen Kernkanäle müssen getrennt bleiben**; ebenso RTL/RTL2/RTLup, ProSieben/ProSieben MAXX oder bundesweite/regionale Fenster. In unklaren Fällen nur alternative Suchtreffer mit Hinweis statt automatische Gleichsetzung.
- Automatische Vorschläge dürfen für den Nutzer den besten **temporären Previewkandidaten markieren**, aber **niemals selbst `Speichern` auslösen**. Live-Vorschau pro **Anbieter-ID + EPG-Kanal-ID**, bei keiner Programmabdeckung nächsten Treffer/Kanal/Anbieter wählen, Cancel unverändert und persistent ohne Writes, Save erst explizit.
- **Keine** teuren Internetabfragen, globale Quell-Reimports, irreversibles Matching oder automatisches Deaktivieren von Feedquellen. Existierende `epg_sources._channel_name_key` mit bisher konservativem Exact-Matching erweitern, aber ohne bisher korrekte automatische Mappings / Sicherheitsprüfungen zu verschlechtern; Preview-Ranking kann bewusst großzügiger sein als persistentes Auto-Mapping.
- Pflichttests für ZDF/Joyn/HD/FHD/HEVC und Kontrast ZDFneo/ZDFinfo, ebenso identische EPG-IDs verschiedener Feeds, regionale Quellen, echte im Raster sichtbare Programme, Save/Cancel, schnelle Senderwechsel, Kodi-IR-Fokus. Spezifikation [#98](https://github.com/artattakk-creator/kodi-noodleprivate/issues/98).

**Paketierung / Priorität:** #97 P0 Stop/Exit **zuerst**, #89 danach gezielt Android nachtesten; #98 EPG-Name-Matching **mit der transaktionalen EPG-Zuordnung** entwickeln; #100 erweiterte Infobar **als späteres, klar dokumentiertes To-do** mit eigener Draft-PR. Bereits offene P1 #99 Catch-up, #74 größere Film-/Seriencover, #90/#91 Artwork/SQLite bleiben unverändert verbindlich. **Keine Merge- oder Releasefreigabe.**

---

## VERBINDLICHE ERGÄNZUNG 22.10.2026: weitere sinnvolle offene Issues, EPG-Preview, Catch-up und größere Cover

**Diese aktuelle Präzisierung geht älteren Detailvorgaben vor.** Der Nutzer wünscht ausdrücklich, dass Codex weitere sinnvolle, thematisch passende offene Issues prüft und nicht nur die bisherige Liste abarbeitet. Vor Beginn der Entwicklung daher **alle zurzeit offenen XCMate-GitHub-Issues** inventarisieren (59 beim letzten Abruf) und eine kurze Triage-Tabelle erstellen: Issue, bestehender Stand in aktuellem main, realer Android-PASS/FAIL/NOT_RUN, technische Abhängigkeit, geeignetes gemeinsames Fixpaket, Umsetzungsentscheidung oder begründete Zurückstellung. **Keine willkürliche Aufnahme aller 59 Issues in einen untestbaren Groß-PR**; P0 STOP #97 und geschützter EPG-Playback-Retest #89 bleiben zwingend zuerst.

### A. [#98](https://github.com/artattakk-creator/kodi-noodleprivate/issues/98): EPG zuweisen mit sofortiger, nichtpersistenter Anbieter-/Kanalvorschau (P1, verbindlich)

**Exakter Nutzerablauf:**
1. Im **großen horizontalen EPG** den betreffenden TV-Sender markieren, **OK / Untermenü / EPG zuweisen** öffnen. Das ist eine Senderaktion, nicht nur ein globale Einstellungen-Seite.
2. In einem IR-bedienbaren Dialog **alle verfügbaren EPG-Kanäle aller konfigurierten Anbieter** mit **Anbietername, Kanalname, EPG-ID, Quellenstatus und soweit lokal bekannt Datenreichweite** anzeigen. Quelle und Kanal als Paar identifizieren (auch wenn zwei Anbieter gleiche IDs/Namen führen). Nutzer soll nach Sendernamen/ID suchen, plausibel gerankte Treffer sehen, Quellen/Kanäle wechseln und durch sehr große Listen navigieren können. Vorhandenes Mapping kennzeichnen.
3. **Sofort beim Auswählen** den **ausgewählten EPG-Datensatz als temporäre Vorschau im bereits geöffneten horizontalen Raster des markierten Senders** darstellen, mit echten Jetzt-/Nächste-/Zukunfts-Sendungen. Die übrigen Sender, Gruppe und Zeitposition unverändert lassen. **Kein Speichern, kein Mapping-Write, kein globaler Import, keine neue Auswahl als Standard.**
4. **Wenn kein EPG erscheint:** klarer Leer-/Nichtgeladen-/BUSY-Status, ohne falsch wirkenden versteckten SHORT_EPG-Fallback. Einfach sofort den **nächsten EPG-Anbieter und dessen Kanal** auswählen und im Raster vergleichen, beliebig oft.
5. **Erst mit „Speichern“** das zuletzt gewählte **Anbieter-ID + EPG-Kanal-ID**-Paar **nur für portal_id + stream_id** atomar dauerhaft zuweisen. Danach den betroffenen Sender im Guide, Now/Next und Langzeitdaten sofort konsistent aktualisieren. Kein Kodi-Neustart nötig; Quelle bei gleicher EPG-ID nicht vertauschen. Alte manuelle String-Mappings rückwärtskompatibel lesen.
6. **„Abbrechen“/Back** verwirft jede Probeauswahl vollständig: vorherige Zuordnung, Rasterprogramme, Zeitachse, Senderfokus/Gruppe und persistierte Dateien bleiben unverändert. Entfernen/Zurücksetzen nur als ausdrücklich bestätigte separate Speicheraktion.

**Technische Besonderheit:** epg_sources.py hat bereits configuration, available_channels und set_mapping, aber die globale _choose_mapping-Funktion schreibt sofort und ist **nicht** als Preview implementiert. guide_grid_window.py hat schon OK-Untermenü und separate SQL-/Diagnose-Reader. Der derzeit aggregierte XMLTV-Kanalindex kann die Herkunft unterschiedlicher Anbieter verschleiern. Im kombinierten SQLite-Guide können gleiche Kanal-IDs aus mehreren Feeds kollidieren. **Codex muss erst echte Source-qualified Daten-/Alias-Auflösung durchgehend gewährleisten; ein umbenanntes globales Mapping mit immer identischer Vorschau wäre ausdrücklich falsch.** Wenn nötig, rückwärtskompatibles, source-qualified Mapping und lokale Quell-Programmindexierung, atomarer Save und temporärer Worker-only Preview-State; keine zweite vollständige Datenbank, kein Full-HTTP bei Fokuswechsel, keine unsichere Profil-/DB-Migration.

**Pflichttests:** Zwei XMLTV-Anbieter mit **gleicher Kanal-ID und verschiedenen Programmen** müssen im Preview *verschiedene* Daten anzeigen; Wechsel A→B→C→Cancel bewahrt Konfigurations-/DB-Bytes exakt; Wechsel A→B→Save ändert nur genau einen Stream desselben Portals, bleibt nach Kodi-Neustart erhalten, aktualisiert Guide/Now/Next sofort; mehrdeutige Regional-/HD-Kanäle, leere Quelle, DB_BUSY, keine Daten, schneller Wechsel und Cancel während Worker, alte Mappings, Android-Fernbedienung. Vollständige Spezifikation [#98](https://github.com/artattakk-creator/kodi-noodleprivate/issues/98).

### B. [#99](https://github.com/artattakk-creator/kodi-noodleprivate/issues/99): Catch-up-/Replay-Symbol im großen EPG (P1, verbindlich)

**Verbindlich:** Gut lesbares kleines **Catch-up-Zeichen** für tatsächlich im nachträglichen Abruffenster verfügbare Sender/Sendungen, im Raster/Senderbereich und im Detail erklärt. Nur anhand **realer Provider-Capability/Stream-Metadaten** wie tv_archive/tv_archive_duration und konkretem Ereigniszeitraum kennzeichnen; vergangene XMLTV-Sendung allein beweist keine Archiv-Verfügbarkeit. Start-over für laufende Sendung getrennt von Catch-up betrachten. Solange keine **tatsächlich funktionsfähige, Android-getestete Archiv-Playerroute** vorliegt, nur informatives Symbol und **keinen scheinbar funktionierenden Replay-Button**. Unterschied zu EPG-Aufnahmen #62 sauber erhalten. BINGIE-Neonfokus #92 muss Schrift/Icons weiterhin lesbar lassen. Details/Regressionen in [#99](https://github.com/artattakk-creator/kodi-noodleprivate/issues/99).

### C. [#74](https://github.com/artattakk-creator/kodi-noodleprivate/issues/74): Film- und Seriencover deutlich vergrößern, Rail-UX korrigieren (P1, verbindlich)

**Nicht vergessen:** #74 beschreibt für **Filme UND Serien** derzeit winzige Poster (alte 100x92 px in einem 106x118 Layout) und unlesbare Titel. **Größere echte Poster im 2:3-Seitenverhältnis**, je nach 720p/1080p ungefähr **150–190 px Breite bei 720p** als Ausgangspunkt, mindestens zweizeilig gut lesbare Titel, sauber sichtbare Neon-Fokusrahmen, vertikales Scrollen zwischen hohen Reihen und keine zu kleine Überfüllung. Obere erreichbare Navigation **Kategorien / Suche**, Landing-Reihenfolge **Weiter ansehen → Meine Favoriten → Neuheiten**. Die bestehende Medien-Favoriten- und Resume-Logik (#44/#41) sowie Back- und Playerzustand erhalten.

**Vorarbeiten bewusst verwerten:** [Draft-PR #83 (0.1.29.14)](https://github.com/artattakk-creator/kodi-noodleprivate/pull/83) enthält laut GitHub-Beschreibung bereits 164x246 Poster, Rail-Neuanordnung, Neon-Fokus und Detail-Fanart, ist aber **gestapelt auf älterem Branch**, auf Android **NOT_RUN** und **nicht in main gemergt**. [Draft-PR #84 (0.1.29.15)](https://github.com/artattakk-creator/kodi-noodleprivate/pull/84) betrifft das eigene VOD-OSD und ist ebenfalls nicht integriert. **Nicht blind mergen, Versionsnummern wiederverwenden oder komplette Branches in main überschreiben.** Codex soll die relevanten Diffs/Tests prüfen und nur passende Teiländerungen auf **aktuellem main / XCMate .16** konfliktfrei in neuen Draft-PR übertragen, sonst sauber nachstellen. Echtbild-Android-Abnahme erforderlich. (#74, #83, #77, #44, #41, #79, #84).

### D. Weitere passende offene Issues prüfen, modular integrieren

**P0 zuerst und unabhängig testbar:** #97 Live-TV-STOP/Exit ohne Neustart, danach #89 EPG-Playerstart kontrolliert auf Android. Keine Playback-Schleifen.

**P1 EPG-UX/Quellpaket:** #98 manuelle Vorschau/Speichern, #99 Catch-up-Zeichen, #88 Startsendergruppe/Logos/Rich-Details, #60 Zuordnungen/Matching, #92 Fokusschrift + direkter Jetzt-Shortcut beispielsweise **BLAUE** Farbtaste, #93 Block-zu-Block-EPG und bessere Leerdaten-Diagnose, #57 Raster, #58 alte Dublettenfälle. Erst sichere technische Wechselwirkungen prüfen.

**P1 Medien-/Artwork-/Performancepaket:** #74 Covergröße und Reihen, #83 als selektiver Draft-Vergleich, #44 Favoriten/Weitersehen, #41 persistente Cover, #90 512-MB-Artworkbudget und hängende SPACE_FULL-Jobs, #91 SQLite-Retry/Queues, #69 MIGRATION_FAILED-Index und #86 Filmimport-Fehlerbanner. Bei unterschiedlichem Risiko zwei abhängige Draft-PRs statt eines Codebergs. **SQLite-Locks, WAL und echte Speicherreserve nicht deaktivieren.**

**Anschluss-Funktionen, ggf. eigener PR:** #42 kontinuierliche Senderliste ohne Seitentasten, #94 Icon-Rail, #95 zukünftige Sendungen des im Mini-EPG markierten Senders, #64 kontextbezogene Tastenprofile; #85 Serien-Autoplay bis zum bewussten Stop und Staffelwechsel sowie #79/#84 Medien-OSD erst nach STOP-/Ended-Abgrenzung, damit keine neue Autoplay-/Player-Reentrancy entsteht. Bei sinnvoll vorhandenen Vorarbeiten getrennt vorbereiten, nicht stillschweigend auslassen.

**Bewusst später/ohne funktionale Scheinzusagen:** #62 EPG-Aufnahmen/Auto-Tune nur mit echten Capabilities und Opt-in; #63 Downloads, #71 PIN, #50 Space Premium, #65 X-Wall, #30 Lightweight Core und größere Design-/Systemumbauten. Historische P0-Issues gegen aktuellen Code/Android-Stand kontrollieren, nicht blind als weiterhin reproduzierbar behandeln.

**Verpflichtende Codex-Antwort:** Issue-Triage-Tabelle (Issue, realer Stand, Relevant?, Implementieren/Separat/Zurückstellen, Begründung), Integrationsplan mit abhängigen Branches, neue regressionssichere **Draft-PR(s)**, Test-ZIP + SHA256, Android-IR-Testplan, Dokumentation der bewusst nicht enthaltenen Änderungen. **Kein Merge nach main, kein Release, keine Kodi-OTA-Aktualisierung und keine Datenlöschung ohne ausdrückliche erneute Freigabe.** Aktueller Hauptstand bleibt .16.

---

## 0. Rahmen, Basis, Ausgangslage

- Repository: https://github.com/artattakk-creator/kodi-noodleprivate
- Aktuelles produktives main: **XCMate 0.1.29.16** (PR #96 zuvor freigegeben und gemergt); Add-on-ID: plugin.video.xtreammate.
- Ziel: **nächster freier 0.1.29.x-Testkandidat** (voraussichtlich 0.1.29.17, zuvor Versions-/PR-Kollisionen prüfen). Neuen Feature-/Fix-Branch von **aktuellem main** erstellen, nicht auf historische Branches .11/.13/.14/.15 bauen.
- Prüfgerät: Android 13 / RK3528 ARM32 / Kodi 21.2 Omega / Titan BINGIE MOD 2.2.3, IR-Fernbedienung; möglichst zusätzlich Estuary.
- Bestehende validierte Teile bewahren: Live-TV-Startsender mit Bild/Ton, OK-Infoleiste + EPG, Links→Mini-EPG, Film-/Serienfenster/Back, großer horizontaler Guide, Zeitnavigation inzwischen über 14 Uhr, Diagnosefenster erreichbar, bestehende Hosttests.
- **Realer Testbericht:** [ANDROID_ABNAHME_02916_2026-10-22_DE.md](ANDROID_ABNAHME_02916_2026-10-22_DE.md), dort exakte Pass-/Teilfail-Abgrenzung. **602 PR-CI/Hosttests PASS ≠ Android-Gesamtabnahme.** Keine Logs/URLs mit Zugangsdaten publizieren.

## 1. P0 – Live-TV explizit beenden, kein automatischer Startsender-Loop (#97)

**IST auf realer Android-Box:** Hauptmenü → Startsender: PASS; Infoleiste inkl. EPG und Mini-EPG: PASS. Danach untere Info-/Steuerleiste → **Stop**: schwarzer Kodi-Ladebildschirm mit rotem Balken/drei Punkten, ursprünglicher Sender startet **ungefragt erneut** und Infoleiste öffnet sich. Erneutes normales Verlassen nicht möglich; **zweimal Back** verlässt Kodi komplett. **Das letzte Ereignis ist nicht als nativer Absturz erwiesen** (Android/Kodi-Exit vs Crash anhand Logcat prüfen).

**SOLL:** STOP/Verlassen setzt einen eindeutigen expliziten Exit-Intent, stoppt nur die eigene Wiedergabe, schließt eigenes Overlay/Sitzung konsistent und führt zur **XCMate-Hauptübersicht** ohne automatischen Neu-Start, ohne versteckte Audioausgabe und ohne Kodi zu beenden. Back-Hierarchie im Live-Betrieb bleibt kontrolliert; fremde Player nie stoppen.

**Code prüfen:** 
- src/plugin.video.xtreammate/resources/lib/live_overlay.py: _execute('controls',index==3), STOP-Key, long_back, LiveNavigator.close(), SESSION_KEY/Nonce.
- src/plugin.video.xtreammate/service.py: IPTVMasterService.run, Playback-Gap / pending_live_start, start_if_eligible, LiveSession/Overlay-Recovery, automatische Popup-Wiederherstellung.
- src/plugin.video.xtreammate/resources/lib/playback_exit.py: identity(), stop_owned(), poll(), Fullscreen-Exit/Media-Checkpoint.
- app_routes.py home_start; vorhandene Router-/Player-Startpfade und Kodi GUI-/Container-Navigation, mögliche Playlist-Wiederholung.
- XCMate-spezifische Action-/Session-Zustandsmaschine und Android-Back-Mapping.

**Vorgehen:** Sicheren, anonymen Eventtrace mit StopRequested/StopDone, Kodi.Player.isPlaying, Session-PID/SID nur gehasht, Owner/Nonce, DispatcherRoute, WindowID, Back/Stop-Action und Startgrund bauen, um **den realen erneuten Startaufruf** zu finden. Nicht behaupten, der Service starte neu, nur weil er Overlays wiederherstellt. Explizites STOP muss idempotent und ggf. als cancel marker über native Playback-Stop-Events/Service-Ticks bis zur bestätigten Terminierung bestehen. Richtige Rückroute erst nach dem Owner-Exit; nicht während offener WindowDialog-Callbacks neue Wiedergabe anstoßen. Abbruch/Recovery nach Senderwechsel, Live-Sessionwechsel, Offline und Kodi-Neustart abdecken. Keine globalen Keymap-Änderungen.

**Abnahme:** 1 normaler Start, 1 Stop→XCMate-Home, danach mindestens 10 Stop-/Back-Zyklen, mehrere Sender/Groups und Doppeldruck, ohne Replay/Audio/Player-Ownership-Leck/Kodi-Exit. Bei erneutem Prozessende Android-Gerätetest sofort stoppen; Logs **privat bereinigen**, keine Crash-Schleife. Kein Rewrite von Film-/Serien-Resume.

## 2. P0-Folgegate – EPG→„Jetzt Sender ansehen“ (#89)

Version .16 hat den nativen Window-Owner/Playback-Handoff aus PR #96 geändert, aber **dieser Weg wurde auf Android noch NICHT getestet**, weil STOP/Exit bereits scheitert. **Nicht als repariert melden.**

Nach Erfolg von Abschnitt 1 einen einzigen kontrollierten Start des **vorher über Live-TV bestätigten guten Senders** aus großem EPG→OK→„Jetzt Sender ansehen“ prüfen. Erwartet: genau ein Start über denselben bewährten Resolver, Kodi bleibt offen, Enden funktioniert. Danach 5 Wiederholungen, falls einzeln stabil. Bei erneutem Crash sofort Abbruch + Diagnose statt Schleife. Den bestehenden PR-96-Handoff **nicht vorsorglich erneut umbauen**; erst Fehlerbeleg oder Android-Ergebnis abwarten.

## 3. P1 – Guide-Fokus: Beschriftung lesbar; praxisnaher Header-Shortcut (#92, #57)

**IST:** Im horizontalen Guide verschwindet die Beschriftung des fokussierten Sendungsblocks. Header „Jetzt“/„20:15“ erfordert unrealistisches Hochscrollen durch zahlreiche Sender; der Nutzer lehnt das explizit ab.

**SOLL:** Jeder fokussierte Titel ist kontrastreich lesbar bei normaler/Neon-/Space-Premium-Fokusdarstellung; Fokus ist eindeutig, aber überschreibt keine Textlabels. Kodi-XML-Button Normal-/FocusedTextColor, Texturtransparenz, Z-Reihenfolge, BINGIE-Skin-Override und 720p/1080p prüfen. Der aktuell ausgewählte Titel sollte zusätzlich persistent im Footer/Lesezeile erscheinen, wenn Programmblock schmal ist.

**Direkter Shortcut:** Nutzer nennt **blaue Farbtaste** als bevorzugtes Beispiel, alternativ eine sinnvoll belegbare Taste oder sauber entprellter Doppeldruck. Empfohlen: konfigurierbares **Blau → Jetzt** oder **Blau → Header fokussieren** (UX klar definieren), nur bei aktivem XCMate-GuideWindow; nicht im Live-TV-Player fremde Tasten belegen. Mit kurzer Buttonhilfe / Footer anzeigen; bei Fernbedienungen ohne Farbtasten Fallback im OK-/Kontextmenü („Jetzt“, „20:15“, „Tag wählen“) oder eigener kurzer Zugriff. Kein Hochscrollen von 2.764 Sendern nötig. Native IR-Key-Codes und Bridge-Eventdedupe testen. Deaktivierte oder fremd belegte Farbtasten respektieren.

## 4. P1 – Links/Rechts **Sendungsblock → Sendungsblock**, Zeitachse bleibt frei (#93)

**Fakten:** Nutzer bestätigt unter 0.1.29.16 den Fortschritt **über 14:00** als PASS. PR #96 korrigierte den Cursor bei überlappenden Events; diese Verbesserung **nicht zurückbauen**.

**Wunsch:** Links/Rechts markiert standardmäßig das unmittelbar vorherige/nächste tatsächliche **Programm** des fokussierten Senders, nicht eine Serie freier 30-min-Schritte. Programmstart/-ende/Highlights dabei synchron. Falls kein Event im aktuellen 3h-Viewport vorhanden, asynchron und begrenzt im vorhandenen lokal gespeicherten Guide nach nächstem Event suchen; bei echten EPG-Lücken kontrollierten Fallback auf Zeitblättern anbieten. Überlappungen, identische Starts und Ereignisse über Mitternacht/DST müssen gerichtet, monoton und dedupliziert bleiben. Die sichtbare Zeitleiste nicht je Sender versetzen, Zeitsprünge transparent kennzeichnen. Keine SQLite-Abfragen/HTTP im Kodi-Key-Callback. Regressionstest speziell 12–15 Uhr langes Event plus kürzere 13/14-Uhr-Events.

## 5. P1 – Langzeitdiagnose zeigt nur Striche: Status **erklären** (#93, #60)

**IST:** Der neue Dialog „Senderdiagnose: Langzeit-EPG“ ist erreichbar und lesbar **PASS**, aber für den vom Nutzer markierten Sender lauten **First=—, Last=—, Days leer**. Dies beweist **nicht**, dass die zwei global READY XMLTV-Quellen keine Zukunftsdaten enthalten. Diagnose-/Alias-/Sender-Mapping- oder tatsächlich fehlende Programme sind zu unterscheiden.

**Code:** src/plugin.video.xtreammate/resources/lib/guide_grid_diagnostics.py: inspect(), List der IDs aus stream SID, provider_epg_channel_id und manuellem Mapping; lokal sqlite URI mode=ro, guide_alias, programmes, Timeout/Deadline, source status. Gegen exakt den **gleichen finalen kanonischen CID**, den guide_grid_data.page()/Guide-Viewport nutzt, abgleichen; prüfen, ob Alias-Kandidat vorhanden, SELECT 0 Zeilen, Quelle nicht im Cache, SQL_BUSY/Timeout oder SHORT_EPG_ONLY. Klare Anzeigen z. B. LONG_DATA_FOUND, NO_ALIAS_MATCH, NO_PROGRAMMES_FOR_CHANNEL, SHORT_EPG_ONLY, DB_BUSY, QUERY_FAILED mit ggf. empfohlenem manuellen Matching aus Kontext. Niemals unbekannte Coverage als leere Quelle präsentieren. Kein Credential-Logging, kein SQL-Write/Netzwerkimport im GUI.

**Abnahme:** Kontrollsender A mit mehrtägigem XMLTV, B ausschließlich SHORT_EPG, C mit ungültiger EPG-ID, D ohne Events, E DB-BUSY. Read-only SQL-/Datei-Bytegleichheit, Tagverteilungen, last stop, Quelle und getrennte Anzeige der Kurz-EPG-Daten.

## 6. P1 – Guide-Gruppenstart, Startsender-Fokus, Logos (#88, #90)

**IST:** Test 6 FAIL: alle Sendergruppen vermischt, Logos im neuen EPG fehlen. **Verbindliches Soll gemäß späterer Nutzerpräzisierung:** **nicht zuerst Gruppenliste**. Stattdessen EPG direkt mit dem horizontalen Raster der gespeicherten Startsendergruppe **und dem konfigurierten Startsender sichtbar fokussiert**, ohne die bestehende Reihenfolge umzuschreiben. **Links** aus Guide öffnet aktivierte Sendergruppen als echte Navigations-/Overlayebene, OK auf Gruppe → nur deren Sender/EPG. Back sauber gruppenbezogen, danach XCMate Home; Zeitachse und Fokus behalten, keine unbeabsichtigte Wiedergabe. EPG-Fernbedienungs-Links konfliktfrei mit der neuen Blocknavigation gestalten: **Links an definierter Sender-/linken Rasterkante oder eigener dedizierter Gruppenaktion** öffnet Gruppen; normale Links innerhalb Sendungsblöcken bedeutet vorheriges Programm. UI-Zustände und Key-Repeats testen.

Logos: Provider stream_icon/Reader-Payload, Priorität sichtbare Kanäle, lokaler media_art-Pfad, Bitmap/Fallback und Kodi-Texture-Control prüfen. 512-MiB-Artwork-Grenze ist plausibler Mitverursacher, **nicht bewiesene alleinige Ursache**; siehe Abschnitt 8.

## 7. P1 – EPG-Details ausbauen, „Plot“ ersetzen, echte Bilder (#88, #60)

**IST:** OK→Details öffnet und zeigt wenigstens Kurzbeschreibung **Teil-PASS**. Textviewer-Titel nur „Plot“, keine Bilder/Fanart, UI nicht zufriedenstellend.

**SOLL:** XCMate-eigene, hochwertige Kodi-Dialogansicht mit korrekt sichtbarem Sendungstitel, Senderlogo, Datum/Uhrzeit/Dauer, verfügbarer ausführlicher Beschreibung, Staffel/Folge/Genre und **passenden** Sendungs-/Episodenbildern. Bestehendes KurzEPG, XMLTV und gesicherte lokale Metadaten nutzen. Externe Ergänzung nur bei hinreichend sicherem Titel-/Staffel-/Folgen-Matching; keine irreführende fremde Grafik. Bei fehlenden Bildern Platzhalter und „keine Zusatzdaten“ statt behaupteter Einträge. Fokus/Back/IR-Funktion, spätere Integration mit Space Premium, Cache-Limits und Quellenberechtigungen berücksichtigen.

Zudem bleibt „EPG zuordnen/ändern“ direkt aus dem markierten Sender-Kontext nötig: aus gespeicherten XMLTV-Kanal-IDs auswählen, Vorschau, explizit bestätigen, persistieren/entfernen, nur betroffenen Bereich aktualisieren; kein automatisches Falschmapping und keine Gesamtimporte aus dem UI.

## 8. P1 dringend – Artwork 512 MiB entsperren und SQLite-/Queue-Engpässe lösen (#90, #91)

**Nutzerwunsch:** Alle **künstlichen** Sperren entfernen. Vorheriger Status: ca. 514/512 MiB Artwork, sehr viele SPACE_FULL-Jobs bei erheblichem physisch freiem Speicher. Bestehende .16 behebt weder 512-MiB-Default noch 4096-MiB-Clamp, versäumte Queue-Jobs oder SQLite-BUSY-Politik.

**SOLL:** Konfigurierbar „kein festes Artwork-Sammlungsbudget“ bzw. frei wählbare hohe Grenze, **echte physische Freiraumreserve** und sichere Datei-/Pixelgrößen/Concurrency weiterhin erzwingen. Vorhandene READY-Bilder unangetastet; bereits wegen künstlichen Budgets mit attempts>=3 blockierte SPACE_FULL-Jobs einmalig, kontrolliert und priorisiert (sichtbare Senderlogos zuerst) reaktivieren. Physisches DISK_FULL diagnostisch abtrennen von künstlichem BUDGET_FULL. Keine Massendownloads oder Datenbanklöschung.

**SQLite:** Keine Schutzlocks deaktivieren, **WAL/Transaktionen/ACID und Integritätsprüfung erhalten**. Stattdessen 50-ms-Gate-/SQLite-Wartezeiten, mehrsekündiges globales BUSY retry_after, Writer-/Reader-Konflikte, Katalog-Initialisierung und GUI-Snapshot-Deadlines differenziert überprüfen; moderate bounded retry/backoff, kurze Transaktionen, UI bei temporären Sperren nicht einfrieren. Keine pauschalen retries bei CORRUPT, READONLY, IO_ERROR. Maßnahmen aus bestehendem [CODEX_AUFTRAG_BREMSEN_ABBAU_2026-10-22_DE.md](CODEX_AUFTRAG_BREMSEN_ABBAU_2026-10-22_DE.md) einbeziehen. Hohe Jobmenge, 2.764 Live-Kanäle, Media-Import, Resume und TV-Live-Test unter RAM-/Disk-Druck prüfen.

Wenn dieser Abschnitt den P0-Fix verkompliziert, **als klar abhängige zweite Draft-PR** vorbereiten, statt ungeprüft in instabilen Player-Hotfix zu mischen. Der Nutzer wünscht dringend die spätere Aufhebung; nicht aus dem Projektplan streichen.

## 9. P2 – ältere Guide-Dubletten und neue Live-TV-Navigation

**#58:** Test 8 aktueller alter Programmführer **PASS**, aber unter .13 war \`SAT.1 HEVC\` mit „Richter Alexander Hold“ als zwei gleichzeitig aktive, nahezu vollständig überlappende Events fotografiert. .16 änderte die Dedup-Logik nicht. Echten alten Rohdatenfall in Testfixture reproduzieren, Sekundentoleranz und Alias/Quell-Priorisierung nur kanalbezogen korrigieren; legitime Wiederholungen/Regionalvarianten erhalten. #58 bis deterministischem Nachweis offen.

**#94 (nicht in .16 implementiert):** Live-TV-Links-Hierarchie: 1 Sender/Mini-EPG, 2 Gruppen, 3 vertikale schmale Icon-Leiste, 4 Icon-Leiste mit Text (Suchen, Favoriten, Live-TV, Filme, Serien, Einstellungen, Verlassen), 5 vollständiges Schließen aller Overlays bei weiterlaufendem TV. Menüpunkt „Verlassen“ führt zur XCMate-Hauptübersicht. **Erst nach korrigierter Stop-/Exit- und bestehender Live-Overlay-Navigation integrieren.**

**#95 (nicht in .16 implementiert):** Rechts auf im Mini-EPG **markiertem** Sender zeigt dessen Jetzt-/Danach-/zukünftige Sendungen, **nicht** zwingend des aktuell abgespielten Senders, ohne Auto-Tune; Back/Links zum identischen Fokus. Quellenhorizont ist feedabhängig.

Diese beiden Features gehören verbindlich zum **weiteren** Fahrplan. Wenn ihr Umfang sichere Android-Abnahme der ersten Fixwelle gefährdet, separat dokumentierte Draft-PRs mit klarer Integrationsreihenfolge liefern.

## 10. Entwicklungs-/Releasegate, technische Akzeptanz

1. **Keine Änderung am produktiven Stand durch diesen Auftrag.** Codex darf branchbasiert Änderungen, neue Tests, dokumentierte Diagnose und **Draft-PR(s)** erstellen, **nicht** nach main mergen, kein OTA-/Repository-Index-Update und keine bestehenden Benutzerdateien löschen/migrieren.
2. **P0 Stop/Exit zuerst** und als kleinsten verlässlich beurteilbaren Fix herausstellen. Danach lesbare und risikoarme EPG-Korrekturen modular testen. Mehrere Commitgruppen / PRs statt eines unüberschaubaren Big-Bang-Releases, aber ein **konsolidierter Integrationsplan** mit Testkandidaten und klaren Abhängigkeiten.
3. Auch bei vollständigen automatisierten Tests immer **Android=NOT_RUN**, bis Nutzer exakt diese Test-ZIP auf dem RK3528-Gerät bestätigt. Keine erfundenen PASS-Zahlen. Bestehende Tests zu .16 und .11 nicht nur auf neue Mock-Annahmen trimmen.
4. Tests für Kodi-Owner-/Service-/Player-Callbacks, Sessionmarker, UI-Thread-Reentrancy, Blue-Key/Doppel-Events, EPG-Blockscrolling/Lücken, .13-Overlaps/14-Uhr, Leerdaten und Alias, Kodi-XML-Fokus-Kontrast, EPG-Deduplizierung, Artwork-SPACE_FULL-Queue und konkurrierende SQLite-Zugriffe; systematisches Regression-Suite-Summary. ARM32/Kodi 21.2 Syntax, später Estuary.
5. Veröffentlichungskandidat: ZIP-Datei, SHA256, maschinenlesbarer Testreport, Installations-/Rückfallanleitung ohne Profil-Deinstallation, Route-/Dateidiff, Risiken und **bekannte noch offene Issues**. Vorversionen .11/.13/.16 und bestehende Profile bleiben unangetastet.
6. Sicherheit: keine Zugangsdaten oder personenbezogene/private URLs in Logs, Screenshots und öffentlichen Docs. Bei Kodi-Exit/crash nur **einmal** und dann Diagnose sichern, keine Endlosschleife.
7. Nutzerseitige nächste Android-Checkliste: Startsender → normale STOP-Funktion → XCMate Home, danach EPG-Play-Handoff einmal; erst dann weiterer Guide-/Artwork-/Navigationstest.

**Zugehörige Issues:** [#97](https://github.com/artattakk-creator/kodi-noodleprivate/issues/97), [#89](https://github.com/artattakk-creator/kodi-noodleprivate/issues/89), [#92](https://github.com/artattakk-creator/kodi-noodleprivate/issues/92), [#93](https://github.com/artattakk-creator/kodi-noodleprivate/issues/93), [#88](https://github.com/artattakk-creator/kodi-noodleprivate/issues/88), [#60](https://github.com/artattakk-creator/kodi-noodleprivate/issues/60), [#90](https://github.com/artattakk-creator/kodi-noodleprivate/issues/90), [#91](https://github.com/artattakk-creator/kodi-noodleprivate/issues/91), [#58](https://github.com/artattakk-creator/kodi-noodleprivate/issues/58), [#94](https://github.com/artattakk-creator/kodi-noodleprivate/issues/94), [#95](https://github.com/artattakk-creator/kodi-noodleprivate/issues/95).
