# VERBINDLICHE CODEX-ÜBERGABE – XCMate 0.1.29.80 (konsolidiert)

**Stand:** 08.11.2026 · **Repository:** \`artattakk-creator/kodi-noodleprivate\` · **Master:** [#389](https://github.com/artattakk-creator/kodi-noodleprivate/issues/389) · **Basis:** XCMate \`0.1.29.79\` auf \`main\` · **Ziel:** kumulative \`0.1.29.80\`.

> **Codex: Dieses Dokument ist der aktuelle Einstiegspunkt. Lies #389 und die verlinkte forensische Loganalyse. Implementiere die .80-Reparaturen, prüfe sie und stelle PR + installierbares Test-ZIP bereit. NICHT die bereits gemergte .79 erneut bauen. NICHT .80 ohne gesonderte versionsspezifische Freigabe nach main mergen oder ungeprüft in alle Installationskanäle veröffentlichen. Die alten Release-Freigaben für .78/.79 gelten nicht für .80.**

## A. Verifizierter Ausgangsstand

- Repository \`artattakk-creator/kodi-noodleprivate\`, \`main\`: Quell-\`addon.xml\` = \`plugin.video.xtreammate 0.1.29.79\`, Stand bei Übergabe Commit \`e3639a77182ad977103cf5c2723092fba9df69a4\` (letzte dokumentarische Änderung, keine .80-Implementation).
- Reguläres GS Media \`addons.xml\` und Pilot \`online-test/addons.xml\`: **0.1.29.79**. NeoDark3 wurde für .79 nicht mitgezogen; historischer Stand .78, vor weiterer Veröffentlichung prüfen.
- Zentrale forensische Analyse dieser Sitzung: [LOGANALYSE_02979_2026-11-08_1157_CODEX_FIX_02980_DE.md](./LOGANALYSE_02979_2026-11-08_1157_CODEX_FIX_02980_DE.md). Älterer Einstieg: [CODEX_START_02980_ANDROID_079_ROOT_CAUSE_FIRST_2026-11-08_DE.md](./CODEX_START_02980_ANDROID_079_ROOT_CAUSE_FIRST_2026-11-08_DE.md).
- GitHub-Folgeissues: [#387](https://github.com/artattakk-creator/kodi-noodleprivate/issues/387) (.79), [#385](https://github.com/artattakk-creator/kodi-noodleprivate/issues/385) (.78), [#366](https://github.com/artattakk-creator/kodi-noodleprivate/issues/366) (Artwork), [#367](https://github.com/artattakk-creator/kodi-noodleprivate/issues/367) (Home), [#368](https://github.com/artattakk-creator/kodi-noodleprivate/issues/368) (Player), [#380](https://github.com/artattakk-creator/kodi-noodleprivate/issues/380).
- Testhardware: Kodi **21.3 Omega** auf Android ARM **32-bit**, Rockchip **RK3528**, Mali-450/GLES2, 1920×1080, Titan BINGIE MOD **2.2.3**, SkinShortcuts 2.1.0, XCMate Media Center Installer \`script.gsmedia.setup 0.5.26\`, Space-Blue-Branding. Bestehende Kodi-Installation/Benutzerkonfiguration nicht überschreiben.
- Der umfangreiche 22-Punkte-PASS/FAIL-Android-Test wurde **wegen Unbenutzbarkeit pausiert**. Die Nachweise stammen aus privaten Nutzerfotos und Kodi-Logs. **Privatdaten (TMDB-Token, Provider-URLs, Hostnamen, Netzwerkinformationen, Profile, Rohlogs) niemals in GitHub veröffentlichen**.

## B. Was die neuen Logs tatsächlich beweisen

**Aus zwei nicht überlappenden Startläufen am 08.11.2026**:
1. \`kodi.old(20261108-115754).log\`: 11:30:52–12:01:41, **23.316 Zeilen**.
2. \`kodi(20261108-115753).log\`: 12:01:43–12:57:35, **36.834 Zeilen**; die neuen folgenden Zahlen basieren auf diesem längeren Lauf.

### B1 – Beleg für konkrete Bild-/Widget-Zustandsregression
- VOD: **90 \`HOME74 COMMIT\`** bei **24 unveränderten Filmen** und derselben \`source_revision\`. **45× \`REFERENCE_PARTIAL → REFERENCE_READY\` sowie 45× \`REFERENCE_READY → REFERENCE_PARTIAL\`**. Die wechselnden Snapshots werden über \`WIDGET45 PUBLISHED\` neu an Kodi gegeben. Das sind keine 90 Katalogaktualisierungen. Ursache in Build/Publisher/Generation/Art-Komplettheit identifizieren.
- Live: **47 COMMITs** für **88 unveränderte Sender**, davon fünf \`READY → PARTIAL\` und viele \`PARTIAL → PARTIAL\` trotz unveränderter Source-Revision. **Live-Logos und Hero-Eventbild getrennt behandeln**, damit fehlende Eventbilder nicht 88 Senderlogos leeren.
- Serie: 10 \`READY → READY\`-Snapshots; **Serienposter deutlich stabiler**. Ihre Daten-/Artwork-Strecke bei der VOD-/Live-Reparatur nicht regressieren.
- Derselbe anonymisierte Image-Event-Key erreicht um **12:02:54** \`IMAGE_DECODED → IMAGE_LEASE BOUND → LOCAL_CACHE PERSISTED\`, später um **12:06:19** \`BINGIE_SKIN_PROPERTY SOURCE_MISSING\` und \`RENDER_CONTROL SOURCE_MISSING\` (\`control=296751 visible=true\`), anschließend wieder \`BOUND/IMAGE_REQUESTED\`. Gleiches Muster für mindestens **vier Events**. **Das beweist das spätere Verschwinden einer Skin-Property-Bindung, NICHT zwingend Dateilöschung oder den exakten Bildverlust-Pixelzeitpunkt.**
- Im längeren Log **235 \`LOCAL_CACHE PERSISTED\`**, **75 \`BINGIE_SKIN_PROPERTY SOURCE_MISSING\`**, **86 \`RENDER_CONTROL SOURCE_MISSING\`**, aber kein verlässlicher letzter sichtbarer Pixel-Receipt; kein \`IMAGE_DECODED\`, \`PERSISTED\`, \`ACTIVE_CONTROL\` oder \`TEXTURE_REQUESTED\` als Android-PASS ausgeben.
- Nutzer-Sichtbeobachtung im selben Testkontext: Auf **SAT.1 Gold / Richter Alexander Hold** ist zunächst wenigstens das Senderlogo als Bild-Fallback sichtbar; **ohne Tastendruck** verschwinden nach einiger Wartezeit erst das Fallback-Bild und dann **sämtliche horizontalen Senderlogos**; die Home-Bildfläche bleibt schwarz. \`Criminal Intent\` zeigt einmal ein **tatsächlich sichtbares XMLTV-Bild** im EPG und später nicht mehr. Exakter Job, der beide Zustände invalidiert, bleibt aus Logs/Code zu korrelieren.

### B2 – VOD-Wiedergabe (wirklicher Funktionsfehler)
- Nutzer öffnet Film-Detail, betätigt **„Wiedergeben“**, sieht den endlosen Spinner, aber **kein Video**.
- Im längeren Log um **12:46:59/12:47:33** zweimal \`ROUTE action=media_detail\`, \`MEDIA44 PORTAL_READ OK\`, dann **\`NAV ANCHOR_TIMEOUT\` um 12:47:09/12:47:40**. **Kein protokolliertes \`action=play_vod\` und kein \`VideoPlayer::OpenFile\` für einen VOD-Film**. Kodi-Video-Open ist dagegen für Intro bzw. Live-TV nachweisbar. **Root-Cause ungeklärt:** Play-Dispatch/Window-Owner/URL-Resolver vor Codec/Provider prüfen. Fehlender Logeintrag bedeutet nicht automatisch unmögliche Providerstream-URL.
- Ein endloser Spinner ist P0-FAIL; der Kodi-Player muss wirklich öffnen und Video/Ton starten oder in begrenzter Zeit mit verständlicher Fehlermeldung sicher zurückspringen.

### B3 – EPG-/Helper-/SQLite-Last
- **Nur \`EPG63 stage=DB_READ\`** in zweiter Sitzung: **2.140 \`EPG_DATA_MISSING\`**, **341 \`EPG_CACHE_UNAVAILABLE\`**, **232 \`EPG_DB_BUDGET\`**, **365 \`READY\`** = 3.078 wiederholte DB-Leseereignisse, nicht 3.078 Sender/Sendungen. Häufiger Miss unter \`mapping=PROVIDER_ID\`; validierte \`STREAM_ALIAS\`-/manuelle XMLTV-Zuordnungen zeigen teilweise erfolgreiche Treffer. Kein heuristisches Vertauschen ähnlicher Sender.
- **18 \`PROGRAMME_DB69 SQLITE_BUSY_LOCKED\`** + 18 dazu korrespondierende \`PROGRAMME_DB46 PROGRAMME_DB_BUSY\` (nicht zwangsläufig 36 voneinander unabhängige Locks), **fünf \`LOCAL_CACHE RAM_ONLY\`**. Ursachen für konkurrierende SQLite-Writer/Transaktionen untersuchen, nicht pauschal Datenbank löschen oder ungesichert auf WAL umstellen.
- \`ART70\` im langen Lauf u. a. **233 \`HELPER_TIMEOUT\`**, **99 \`HELPER_BACKGROUND_UNAVAILABLE\`**, **1.010 \`NO_CONFIRMED_IMAGE\`**; externer \`plugin.video.themoviedb.helper\` zweimal \`JSONDecodeError\`. Die Tatsache, **wer** dessen Netzwerkfehler verursacht, ist noch nicht sicher; Dependency- und Call-Graph im XCMate-/Skin-Code prüfen.
- Weiterhin fehlende \`MyVideos131.db\`-\`movie_view\`, \`tvshow_view\`, \`musicvideo_view\` (im längeren Log 12 \`no such table\`-Ereignisse). Dieser **separate Kodi-Library-Defekt** kann „Neu im Kino“/native BINGIE-Bibliothekswidgets betreffen, ist nicht automatisch die Ursache jedes XCMate-Providerwidgets.
- Interne \`HOME75\`-Messwerte im späteren Lauf \`MOVIES_VISIBLE_READY elapsed_ms=67594\`, \`LIVE_HOME_READY elapsed_ms=103971\`, \`SERIES_VISIBLE_READY elapsed_ms=2578964\`: ca. 68 s, 104 s, 43 min. Dies sind **interne Stages**, keine gemessenen sichtbaren Renderzeiten – die Definition und Messung müssen verbessert werden.

## C. Weitere konkrete Bildschirm-/Bedienbefunde aus dem Gerätetest

- **Bilder fehlen/bleiben PENDING:** \`Die Tribute von Panem – Mockingjay (1)\` und \`Harry Potter und der Feuerkelch\`: EPG-Uhrzeiten/Beschreibung vorhanden, aber kein Filmbild; \`Bildprüfung im Hintergrund ausstehend\` wird nicht in angemessener Zeit abgeschlossen. \`Criminal Intent\` XMLTV-Bild gelingt und verschwindet später wieder. Bei \`Malcolm mittendrin\` Now/Next/Progress vorhanden, Bild fehlt. Kein unendlicher Pending-State; keinen angeblich sicheren TMDB-Treffer ohne tatsächliche API-/Cacheprüfung erfinden.
- **EPG-Navigation:** Aus \`Comedy Central\` über links-links-links/EPG öffnet großer EPG auf **WELT** statt auf dem aktuellen Sender. Gleiches sollte bei \`NITRO\` auf NITRO gehen: **aktuelle Kanal-ID, Gruppe, Zeitcursor und Fokus übergeben**, kein hardcodierter/zuletzt gespeicherter WELT-Anker.
- **EPG-Layout:** Bei \`sixx\`, Disney Channel und langen Kanal-/Programmtiteln überlappen Texte Zell-/Spaltengrenzen; Kopf/Fuß teilweise abgeschnitten. 720p und 1080p echte Clip/RowHeight/Hitbox-Tests. **Neongrünen Fokusrahmen** durch dieselbe dezente **graublaue Hervorhebung wie links bei der Sendergruppe** ersetzen; aktive Auswahl bleibt erkennbar. Fortschrittsbalken gesondert erhalten.
- **EPG-Beschreibung:** Texte enthalten sichtbare Literal-Escapes \`\\n\\n\`; sinnvoll vor Kodi-GUI in Absätze normalisieren und Länge/Scroll/Clipping begrenzen.
- **Home und VOD:** Live-Senderlogos verschwinden während Idle; Filmreihe anfänglich nicht sichtbar, erst nach DOWN erscheint unvollständige Reihe mit **großen Play-Platzhaltern** anstelle valider Providerposter. Wiederholt 24 Filme im Widget-Payload; das ist **kein Beleg für leeren Provider-Katalog**. \`##### GERMANY HEVC #####\` als auswählbarer Sender ist möglicherweise ein Provider-Gruppentrenner; **erst nach Klassifizierung** filtern, nicht blind Providerdaten löschen.
- **Serie:** Mehrere echte Poster in Reihe sichtbar, u. a. \`Loki\`, \`Stranger Things\`, \`After Life\`, \`The 100\`; bestehende Serien-Pipeline erhalten. \`Loki\`-Hero wird jedoch übermäßig beschnitten, Bild auf linke Hälfte reduziert und rechts steht getrennte schwarze Textfläche.
- **Verbindliches früher beschlossenes Hero-SOLL:** **Full-bleed** Header-/Hero-Hintergrund mit **Landscape Fanart/Backdrop**, proportionalem unbeschnittenem Poster-Fallback (contain) und sinnvollem Hintergrund statt entstellendem Cropping; beschreibende Informationen **halbtransparent über dem Bild**, vorzugsweise rechts: Logo/Titel, Now/Next, Fortschritt, kurze Beschreibung, EPG-Bildquelle. Kein Hero-Schrumpfen beim Fokus-/Reihenwechsel. Frühere BINGIE-Reihen einschließlich **„Neu im Kino“** müssen erhalten bleiben.

## D. Implementierungsvorgaben – Reihenfolge und technische Abnahme

### P0-1: Revisionssicherer Picture/Widget-Publisher
1. Reproduktionstest aus exakt identischem \`source_revision\`/24 Filme/88 Sender, bei dem READY/PARTIAL-Snapshots abwechselnd an Kodi publiziert werden. **Monotone last-good-Revision**, atomarer Publish, Generation/Source-ID/TTL/Provider-/Event-Identitätsprüfung. **Stale/teilweise Jobs dürfen gültige Bildzustände nicht überschreiben**; bei tatsächlichem Eventwechsel veraltete Bilder korrekt invalidieren.
2. **Drei getrennte Bild-Scopes:** persistente Kanallogos der Startgruppe, laufendes Event-Hero/Sendungsbild (oder logo fallback), VOD-/Serienposter. Fehlende EPG/TMDB-Bilder dürfen Senderlogo-Leiste nicht leeren. Kein \`REFERENCE_READY → PARTIAL\` bei identischer gültiger Revision ohne eindeutige Ursache.
3. Für die gleiche anonymisierte Event-ID \`LOCAL_CACHE PERSISTED → SKIN_PROPERTY SOURCE_MISSING\` reproduzieren; Cache-Datei-, Image-Lease-, Kodi-Property-, Skin-Control- und Texture-Binding mit Generation-Korrelation instrumentieren. Grund eines Bildverlusts explizit protokollieren, **keine Token/URL/Providerkennungen**.
4. Idle-Test **SAT.1 Gold** mehrere Hintergrundzyklen lang ohne Eingabe und \`Criminal Intent\` nach EPG/Home-Wechsel. Logo-Rail, Hero-Fallback und gültiges Eventbild bleiben sichtbar. Negative Tests: API-/Bildserverfehler, Datenbanklock, Skin-Reload, Sender-/Eventwechsel, abgelaufene Bilder, Kodi-Kaltstart. **Serie unverändert funktionsfähig.**

### P0-2: VOD-/Kodi-Play-Dispatch
1. Von \`Wiedergeben\`-Button bis Action-Handler/Media-ID/Portal-ID, VOD-Resolve, Kodi \`setResolvedUrl\`/Player-API, \`VideoPlayer::OpenFile\`, \`PLAYING\`/Fehler-Endstatus korreliert instrumentieren. Die \`NAV ANCHOR_TIMEOUT\`-Ereignisse im Film-Detail lösen – Fokusdialog darf VOD-Start nicht blockieren.
2. **VOD muss wirklich Ton+Bild auf Android abspielen**, aus Filmreihe und Detail-/Hero; bei Stream/Codec/Provider-Ablehnung gut erkennbare Fehleranzeige nach endlichem Timeout. Keine blockierende Spinner-Schleife. Live-TV/Serien-Autoplay/Stop-ACK/Zurück unverändert testen.

### P0-3: EPG-/Bild-Anreicherung und SQLite-Entlastung
1. Provider-ID → **verifizierter** Stream-Alias → gespeicherte manuelle XMLTV-Zuordnung; keine falschen Programme bei ähnlichen Titeln/Kanalnamen. Dedup nach Kanal/Event-/Source-Revision, negatives Cache/Backoff, in-flight Coalescing, klare endliche Fetch-Status.
2. Database busy: Writer/Lockowner und Transaktionsgrenzen analysieren, ggf. kompatible SQLite-Transaktionsoptimierungen. \`RAM_ONLY\` ehrlich melden, nicht \`PERSISTED\`. Kodi Library MyVideos131 read-only untersuchen (\`sqlite_master\`, Integrität, DB-Version, Query-Consumer) und **nicht automatisch reparieren oder löschen**.
3. Provider-/XMLTV-Artwork primär; für Live-Sendungen **eigene** TMDB-API mit bereits importiertem Token und TVMaze-Fallback, ohne zwingenden externen TMDB Helper. Für Filme/Serien Provider-Artwork vorziehen. Title-Matching mit deutscher/englischer Filmvariante/Teilenummer (\`Mockingjay (1)\`, Harry Potter) und Kontrollfall \`Criminal Intent\`; keine willkürlichen Falschtreffer. **Token muss byteidentisch erhalten** bleiben, nie loggen/reimportieren.
4. Priorisierter Scheduler: zuerst lokales EPG + Startgruppe/Senderlogos; dann Hero für ersten Sender und nächste vier; Rest-Live-Images nachladen; Film-/Serienposter inkrementell. Cached-last-good-Art sofort anzeigen. Remote-/SQLite-Schwerarbeit von GUI-Thread trennen, Latenzen mit tatsächlich beobachtbaren Stages messen.

### P0-4: EPG/Layout/Widget-Konfiguration
1. Großes EPG vom aufrufenden Comedy Central/NITRO/WELT öffnen, aktuelle Zeile/Zeit/Gruppe fokussiert, Rücksprung korrekt. Zellgrenzen/Fokus/Clipping und Langtext bei Sixx/Disney 1080p + 720p reparieren.
2. BINGIE/Space-Blue-Auswahlfarbe **graublau statt Neon-Grün**, Sender/Programmraster konsistent; Now/Next/Progress erhalten.
3. **Full-bleed-Hero mit transparentem Textoverlay**, Fanart/Backdrop vs Portrait-Poster korrekt skalieren. Serienreihe nicht regressieren; Filmreihe auch **ohne Fokuswechsel** sofort sichtbar. Kein vollständiger Layoutreset.
4. READ-ONLY Inventar alter SkinShortcuts und Userwidgets inklusive \`Neu im Kino\`; keine Unterdrückung durch neuen Default. Kodi-Library-Views gehören in separate, nicht destruktive Diagnose.

## E. Unverhandelbarer Bestandsschutz

- **Installer \`script.gsmedia.setup 0.5.26\` bleibt eingefroren**, keine Änderungen an dessen ZIP, Registry, Online-Installerablauf.
- Keine Deinstallation/Kodi-Neuinstallation, kein Downgrade, kein Skin-/SkinShortcuts-Reset, keine Änderung an bestehenden Kodi-DB-/Profil-/Favoriten-/Provider-/EPG-Konfigurationen oder Space Blue. Falls eine mutierende Kodi-Library-Migration unvermeidbar scheint: zunächst Root-Cause, Backup-Plan und **separate Einwilligung**, nicht automatisieren.
- Bereits importierten **TMDB-Read-Access-Token** byteidentisch erhalten; keinen fremden/öffentlichen Token committen und ihn nicht im Klartext ausgeben.
- Alte ZIP-Archive behalten, installierte Geräte via **kumulatives Kodi-Update** erreichbar halten. **Keine privaten Rohlogs/Screenshots in GitHub**.

## F. Codex-Liefergegenstände / Release-Gate

1. Nach Reproduktion der obigen Defekte **Version 0.1.29.80 kumulativ auf der aktuellen .79-main-Basis implementieren**, neuer Branch + PR. Vorher bewusst keine Komplettneuschreibung.
2. Regressionen für alle P0s, insbesondere \`READY→PARTIAL\`-Churn, persistent→missing bei identischer Event-ID, liveLogoMap≠hero, Idle+Skin-Reload, VOD-Play-Dispatch, EPG-Lock-/Mapping-/Missing-Cache und 1080p/720p Layout. Quell-/ZIP-Bytegleichheit, ZIP-CRC, SHA256, native Linux-Kodi/BINGIE-2.2.3- und Host-CI-Tests.
3. GitHub [Issue #389](https://github.com/artattakk-creator/kodi-noodleprivate/issues/389) mit Root-Cause-Tabelle, Datei-/Moduländerungen, Tests/CI-Links, PR, ZIP/SHA256, Android-Status je Gate und offenen Blockern aktualisieren.
4. **Nicht ohne weitere .80-spezifische Freigabe auf \`main\` mergen oder sofort in regulär/Pilot/NeoDark3 ausliefern.** Freigaben für .78 und .79 gelten nicht als künftige Blanket-Autorisierung. Der aktuelle Nutzerauftrag lautet Codex-Übergabe/.80-Generierung, nicht Release.
5. Keine \`ANDROID_PASS\`-Behauptung aus Hosttests. Erst Gerätetest auf realem RK3528/Android. **Kurze Abnahme statt 22-Punkte-Test**:
   - **A:** SAT.1-Gold-Idle und Criminal-Intent-Image: Hero/Fallback plus alle Senderlogos über mehrere Aktualisierungen stabil.
   - **B:** Film-/Serienwidgets inklusive richtiger Cover ohne vorher DOWN drücken; gute, uncropped Full-bleed-Hero/Overlay; frühere Reihen einschließlich „Neu im Kino“ vorhanden.
   - **C:** Film aus Detailseite startet **nachweisbar** mit Ton/Bild, keine unendliche Spinneranzeige, Zurück stabil.
   - **D:** Großes EPG öffnet Comedy Central/NITRO korrekt, keine Sixx-Textkollisionen, Mockingjay/Harry-Potter-Image-Suche endet mit sichtbarem Bild oder begründetem Fehlerstatus; Now/Next/Progress bleiben funktionsfähig.

**Erwartetes Codex-Rückgabeformat:** PR-URL, kumulatives .80-Build-Artefakt + SHA256, Root-Cause je P0, veränderte Dateien, CI-/native-Testresultate, Exit-/Navigation-Regressionen, Schutz der Userdaten, Android NOT_TESTED bis echten Fotos/Logs. Kein neues Release ohne Freigabe.
