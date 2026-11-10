# XCMate 0.1.29.87 – verbindlicher Codex-Masterauftrag nach realen Android-Tests der .86

**Stand:** 10.11.2026 · **Status:** BEAUFTRAGT / IMPLEMENTIERUNG AUSSTEHEND · **Priorität:** P0 · **Ziel:** `plugin.video.xtreammate` **0.1.29.87** im **eigenen Entwicklungsbranch mit Draft-PR**. **Keine automatische Veröffentlichung oder Behauptung einer Android-Abnahme.**

## 0. Ausgangspunkt, richtige Version und vorhandene Arbeit

- GitHub: `artattakk-creator/kodi-noodleprivate`, Haupt-Addon `src/plugin.video.xtreammate`.
- **0.1.29.86** ist bereits in `main` gemergt (Source-PR [#410](https://github.com/artattakk-creator/kodi-noodleprivate/pull/410), Merge-Commit `36b903c06daa7b7fb5903f9de568237c18b9e2a1`) und in **GS Media Original, GS Media Pilot, NeoDark3** veröffentlicht (Release-Commit `d01a968567bcbbbdc29b8c84d59002c4d86c0f36`; [grüner Veröffentlichungslauf](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42846106242)). **Dieselben Versionen/ZIPs nicht überschreiben.**
- **[PR #412](https://github.com/artattakk-creator/kodi-noodleprivate/pull/412)** ist am 10.11. noch **DRAFT/OFFEN**, beinhaltet vorläufige native Index-/Navigationskorrekturen und eigene verschiedene Tabler-Icons, aber weiter Paketversion **.86** und **keine physische Android-Abnahme**. In der PR-Beschreibung: 3.566 Hosttests PASS, native 720p/1080p-Simulationen PASS und 100 Invoker-Zyklen; **beides ist kein Gegenbeweis gegen reale Android-Fehler**. Codex muss die nutzbaren Änderungen nach sicherer Diff-/Versionsprüfung in einen **neuen 0.1.29.87-Branch** übertragen, Konflikte beheben und erneut testen, **nicht** PR #412 mit identischer veröffentlichter Versionskennung unbesehen mergen.
- Primäre reale Logbasis: [vertraulich bereinigter Android-.86-Loganalysebericht](ANDROID_LOGANALYSE_02986_BOXB_2026-11-10_161710_161714_DE.md) und [vorangehende .85-Analyse](ANDROID_LOGANALYSE_02985_BOXB_2026-11-10_134323_DE.md). Original-`kodi.log`/`kodi.old.log` nur im Chat, **NICHT öffentlich ins Repo oder CI hochladen**. Große Datei beginnt mit **.85** und wechselt erst um **16:37:30** auf **.86**; frisches Log startet **.86 um 17:10:37**. Messungen nicht vermischen.
- P0-Referenzen: [#414](https://github.com/artattakk-creator/kodi-noodleprivate/issues/414) (88/0 Logos, Speicher, Index, Hero), [#413](https://github.com/artattakk-creator/kodi-noodleprivate/issues/413) (manuelle Suche/Save bricht nach ~30s ab), [#401](https://github.com/artattakk-creator/kodi-noodleprivate/issues/401) (Speicher/Mount), [#409](https://github.com/artattakk-creator/kodi-noodleprivate/issues/409) (.86-P0-Master), [#406](https://github.com/artattakk-creator/kodi-noodleprivate/issues/406) (EPG/Artwork), [älterer .86-Master](CODEX_FOLGEAUFTRAG_02986_ANDROID85_LIVE_HERO_WIDGETS_BILDSUCHE_2026-11-10_DE.md).
- Gerät: Test-Box B, Kodi 21.3 Omega, Android ARM32 RK3528, Titan BINGIE MOD 2.2.3, 1080p, GS Media Pilot 1.9.12, Setup 0.5.26. **Box A und persönliche Kodi-Profile nicht verändern**.

## 1. P0-A / P0-L: Live-TV – 88 Sender, 0 Logos, Cache/Persistenz

### Belege aus echter .86
- `HOME86 GROUP_READ_MS {count:88,ms:865}`, `WIDGET79 SOURCE_READY / DIRECTORY_ITEMS count=88` – Sender sind schon verfügbar.
- `HOME86 LOGOS_LOCAL_READY count=0,total=88`: **11× im frischen .86-Neustart**, 28× im Teil nach dem .86-Update des älteren Logs. `DISPLAY84 live REFERENCE_HANDED count=0`; `WIDGET47 NO_RENDERABLE_REFERENCE dynamic_images=0 local_images=0 logo_sources=88 poster_sources=88`. **Quellenbekanntheit ≠ zugelassene lokale Bildreferenz ≠ echte Pixel.**
- `WIDGET79 CONTROL_EMPTY` trotz 88 `DIRECTORY_ITEMS`; erste `RELOAD_ACK count=88` ca. **72 Sekunden später**, `RAIL_CONTROL_READY_MS` **396×** wiederholt; keine Bestätigung tatsächlich sichtbarer Logos.

### Codex muss umsetzen
1. **Eindeutige Logo-Quelle pro Sender** aus dem Provider sauber identifizieren, nicht unkontrolliert Poster-/Coversuche als Senderlogo missbrauchen. Pro Sender/Suchquelle sanitisierte Gründe protokollieren: `SOURCE_MISSING`, `URL_SCHEME_OR_HOST_BLOCKED`, `AUTH_SCOPE`, `LEASE_PENDING`, `DOWNLOAD_FAILED`, `IMAGE_INVALID`, `STORAGE_RESERVE_BLOCKED`, `LOCAL_READY`, `TEXTURE_VISIBLE`. **Keine URL-/SSRF-Sicherheitslockerung**, Zugangsdaten nicht loggen.
2. `logo_manifest86.py`, `live_rail86.py`, `widget_assets69.py`, `widget_cache79/82`, `widget_render47.py` und Skin-Bridge prüfen: bei vorhandenem lokalem, sicher geprüftem Senderlogo **direkt** an Kodi/BINGIE übergeben. Bestandslogo-Cache **read-only** übernehmen, wenn Scope/Hash und Pixelvalidierung stimmen; keine Fremddateien löschen.
3. Senderleiste und Sendernamen unabhängig von EPG, TMDB und Hero-Warmup zuverlässig anzeigen. **Nicht** mehrere Minuten auf `CONTROL_EMPTY`-/Reload-Zyklen warten; keine `ready`-Meldung ohne passende Kontrollgeneration/Renderer-Receipt. UI muss bei fehlendem Logo trotzdem fokussierbare Namen/neutralen Fallback anzeigen.
4. Echte Android-Abnahme: Warm-/Kaltstart 88er-Leiste in bestehender SLO (≤2s/≤5s nach Home-Anzeige bei vorhandener lokaler Cachebasis), sichtbar gespeicherte Logos, nach Neustart stabil. **Keinen 88/88-PASS erfinden**, wenn Provider-/Storage-Bedingungen tatsächlich nicht erfüllt sind.

## 2. P0-S: Artwork-Speicher und tatsächliche Android-Mount-Wahl

### Beweise
- `ART_STORAGE82 backend=LOCAL mount=fuse capacity82=SAME_VOLUME_VERIFIED`, ca. **4.034.297.856 Byte Gesamtvolumen (3,76 GiB)**, am Ende ca. **240 MiB frei**, Sicherheitsreserve **1.073.741.824 Byte**, **Schreibbudget = 0**, `RESERVE_BLOCKED`.
- `logo_manifest86.prepare()` prüft vor Download/Manifestwrite die Reserve. Unter diesen Bedingungen kann es **keine neuen persistenten Logos anlegen**. Andere Pfadnamen auf gleichem FUSE-/Storage-Pool lösen das nicht.
- Android meldet `/storage/emulated/0` als zugreifbar; **das allein beweist nicht**, dass die gewünschte Cache-Datei auf einem anderen Volume landet.

### Codex muss umsetzen
1. Für Kodi-App tatsächlich zugreifbare Speicheroptionen **statvfs, dev-/Mountidentität, effective file permission, app-scoped Schreibrechte, Besitzkontext, atomaren Tempfile→fsync→rename→Readback** testen; nur bei bestätigtem echten anderem Zielpool mit ausreichendem Budget eigene Artwork-/Logo-/Programmdateien sicher dorthin auslagern.
2. Falls auf Android FUSE/Emulated-Datenpfad derselbe Pool ist: **ehrlich `NO_SEPARATE_WRITABLE_VOLUME`** melden; nicht 224 GiB vom angeblichen Hauptspeicher annehmen, nicht über fremde Settings/USB/Netzwerk automatisch gehen.
3. **1-GiB-Sicherheitsreserve beibehalten**, fremde Kodi-/Addon-/Skin-Dateien unangetastet; keine Datenbank-/Cache-Massenlöschung, kein Nutzerprofil-Reset. Schrittweise geprüfte Migration mit Rollback, ohne Duplikatüberlauf, nur eigene eindeutig inventarisierte Artefakte.
4. **Gültige bereits in RAM oder im Kodi-eigenen Texturecache lesbare Bildreferenzen** nicht wegen fehlender neuer Persistenz künstlich unsichtbar machen; Safe-Policy, Rechte und Render-Proof weiterhin einhalten. Fehlende Persistenz als Problem **nicht** als „Bilder gefunden“/PASS kaschieren.
5. Diagnosestatus mit `active_mount`, `reserve`, `budget`, `last_write_readback` und Logo-/Hero-Hit-Rate, ohne private Pfade/Secrets. Regression für ENOSPC, same-volume, fremde Dateien, Netzwerkausfall, einmalige/sichere Recovery.

## 3. P0-H / P0-B: BINGIE-Hero zeigt keine oder sehr spät Bilder

### Reale Nutzertests (nach dem jüngsten vorliegenden Log, daher nicht als zeitlich direkt im Log bewiesen!)
- **„Desperate Housewives“:** kein Hero-Bild; Wortlaut „Six Desperate Housewives“ beim Diktat, konkrete Werkidentität/TV-Event erst mit künftiger EPG-Trace sicher prüfen.
- **„American Dad“:** erstes sichtbares Hero-Bild erst nach **ca. 15 Sekunden**. Zuvor nach .85/.86 andere Sendungen nach Wartezeit, Schwarzbild oder XMLTV-Mini-Cover statt TMDB-Backdrop.
- .86-Log zeigt für *andere* pseudonymisierte Events teils `TMDB FOUND`, teils `NO_CONFIRMED_IMAGE` und einzelne `IMAGE_DECODED`; **nicht** automatisch die beiden aktuell genannten Werke betroffen.

### Codex muss umsetzen
1. **End-to-End Artwork-Tracing pro EPG-Event**, ohne private Sendungstitel im öffentlichen Log: korrekt identifizierte Sendung/Serie → sichere TMDB-TV/TMDB-Movie/TVMaze-ID → echtes `backdrop_path`/Szenenbild → URL-Policy → Bilddownload → Decode → verfügbare lokale/geschützte RAM-Referenz → A/B-Hero-Bank → Kodi-Texture-Receipt/**sichtbare Pixel**. Detaillierte P50/P95 und Time-to-First-Image, getrennt nach EPG/Quelle/Netzwerk/DB/Skin.
2. **Rangfolge**: echtes breites hochwertiges **TMDB-Backdrop**; geeignetes echtes TVMaze-/Provider-Szenenbild; **offizielles Poster** in proportionalem eigenem Poster-Hero-Layout (kein Querziehen eines Hochformats); erst danach Senderlogo bzw. stabiler Text-Hero. Niemals XMLTV-Thumb oder kleines Cover aufgeblasen in die Hero-Fläche.
3. Bekannte **gültige** Bildreferenz direkt aus RAM/Bestands-Cache nutzen; asynchrone Verbesserung darf einen bislang sichtbaren, **zur selben Eventidentität gehörenden** Hero nicht auf `Image=''` oder Schwarz zurücksetzen. Bei Eventwechsel niemals Bild von anderer Sendung anzeigen; Sendername, jetzt/danach, Fortschritt und Fokus bleiben stabil.
4. Live-Artwork/EPG-Worker, Speicher und BINGIE-First-Frame **entkoppeln**, Warteschlangen priorisieren; die **~15s** bis American-Dad-Bild erklären und begrenzen. Wenn keine valide Quelle, nicht unsichtbar, sondern verlässlich Fallback + klarer Diagnosegrund.
5. Android-Prüfung „Desperate Housewives“ und „American Dad“ plus ≥3 weitere Events, schneller Senderwechsel, Cold/Warm/Offline-Neustart, 1080p/720p, echte Screenshots und Pixel-/Texture-Nachweise. Kein Host-PASS ersetzt das.

## 4. P0-D2: TMDB-/TVMaze-Treffer lassen sich nicht zuordnen

### Reale Nutzer-Reproduktion
Mini-EPG → Sendungsdetail ohne Bild → Links → Werk/Bild zuweisen → **TMDB · TV** oder **TVMaze · TV** findet passende Treffer → Auswahl per OK / Bestätigung → allgemeiner Such-/Wartedialog → nach geschätzt **~30 Sekunden** „Abgebrochen“. **Bei beiden Quellen**. Ursache ohne operationsechten `WORK86`-Trace **noch nicht zweifelsfrei identifiziert**.

### Quellcode-Risiken / Codex-Aufgaben
- `work_manager86.wait()` hat ein **30s-Deadline**, die beim Ablauf **genau denselben `CANCELLED`-Code wie echten Nutzerabbruch** zurückgibt. Außerdem verwendet Save denselben Dialogtext „Suche wird vorbereitet“. Klare Zustände `USER_CANCELLED` vs `REQUEST_TIMEOUT` vs `WORKER_BUSY`/`WORKER_STOPPED` vs `EPG_REVISION_CHANGED` vs `NETWORK_TIMEOUT` vs `PERSISTENCE_BLOCKED`.
- `work_requests86.request/result/drain/save` (Window10000 Nonce/Scope/Properties) und `programme_requests68._run()` (arbeitet bisher `live_warm68.prepare` **vor** dem manuellen Drain) prüfen. Manuell bestätigte Arbeit sicher priorisieren und abrechenbar machen; kein unsicherer neuer paralleler Kodi-GUI-Worker, kein nachträglicher Doppel-Save. Laufzeitstufen `ENQUEUED→PICKED→SOURCE_REVERIFIED→EPG_SCOPE_REVALIDATED→WRITE/READBACK→DELIVERED→UI_CONSUMED` redigiert mit Zeit.
- EPG-/Sendungsrevision darf keine Zuordnung auf fremde Sendung übertragen; bei Wechsel gezielt neu bestätigen lassen, aber explizite Auswahl nicht kommentarlos verwerfen.
- **Speichern verifizieren:** gewählte TMDB-/TVMaze-/Film-/Serien-Identität, Work-ID, Quelle, Jahr, Medium, Rolle/Backdrop oder Poster im Scope dauerhaft ablegen; danach passendes Bild in Mini-EPG-Detailansicht anzeigen und **nach Kodi-Neustart** bestätigen. Bestehende manuelle Zuordnung nicht durch automatische URL- oder XMLTV-Auswahl überschreiben.
- Tests **TMDB-TV**, **TVMaze-TV** und **TMDB-Movie**, Serien `Charmed – Zauberhafte Hexen` (1998 vs 2018), `Monk`, verschiedene Titelvarianten, echte Save-Fehler, EPG-Wechsel, Worker 5s/30s geblockt, Kodi-Stop, Back/Cancel, fehlender Speicher; kein falsches `CANCELLED`.

## 5. P0-F: native GUI-Ausnahmen, Detailnavigation und Reload-Sturm

- Frisches .86-Log: **98× `EXCEPTION: Index out of range`**, 17:12:21–17:16:40, nahe den nativen 88-Sender-Control-/Reload-ACKs. Der exakte Ursprungs-Stack fehlt, **nicht** behaupten, dass es sicher nur Python oder nur Skin ist.
- Bereits .85: mehrfach `CPythonInvoker script didn't stop in 5 seconds`, `DISPATCH_FAILED` und `GetDirectory`-Ausfälle. Aus PR #412 vorhandene Guards/Generations- und Diagnoseänderungen übernehmen, aber gegen echten Android-Zustand überprüfen.
- Auf jeder Kodi-List-/Control-API echten Count, SelectedIndex, GUI-Window-Lebensdauer, Kontext-/Refresh-Generation und Fokus atomar absichern, niemals `getListItem` auf nicht exponierte Controls oder ungültige Positionen. Kein SQL/HTTP im Remote-Keycallback.
- Abnahme **100× Home→Live→Senderfokus→Mini-EPG→Details→Zurück→Filme→Serien→Zurück** bei Hintergrundreload: **0 Indexfehler, 0 XCMate-GetDirectory-Fehler, 0 erzwungene Python-5s-Kills, 0 Focusverlust**. Instrumentierung ohne private Titel, Portalendpunkte oder Credentials.

## 6. P0-G: linke Navigation muss echte verschiedene Icons zeigen

**Einheitliche Hauptreihe:**
1. **Suche** – Lupe → globale Suche.
2. **Favoriten** – Herz/Stern → Favoriten.
3. **Live-TV** – Fernseher → aktuelle Live-Senderliste.
4. **Filme** – Filmklappe/Filmstreifen → Filme.
5. **Serien** – unterscheidbares Episoden-/Seriensymbol (nicht identisch mit Live-TV).
6. **Einstellungen** – Zahnrad.
7. **Verlassen** – Tür/Home-Rückkehr → **XCMate-Home**, nicht versehentlich Kodi-Home/Player-Abbruch.

Für EPG, Sendergruppen, Startsender existieren eigene unterschiedliche Extrasymbole. Bisheriger `nav_rail.py` und das Tabler-Icon-Buildsystem existieren; #412 hat laut PR bereits sieben getestete Glyphen im nativen Test-Renderer. Trotzdem **reale Box B** im tatsächlichen BINGIE-/Live-Navigationskontext testen, nicht nur PNG-Verfügbarkeit:
- Live-Vollbild, Links-Stufen **Sender → Gruppen → schmale reine Icon-Rail → erweiterte Rail mit Labels**; Hoch/Runter/OK/Zurück, Fokuszustand, stabile Zeichen trotz Artwork-Refresh; Icons lokal/offline, unabhängig von TMDB/EPG.
- 720p/1080p-Pixel-Screenshots bei je sieben Punkten. Keine ungefragte SkinShortcuts-Neuinstallation, kein Verlust persönlicher Kodi-Hauptmenüs.

## 7. P0-C/E: Bestandswidgets, EPG und Nutzerstatus

- BINGIE-Hauptseite **„Frisch im Kino“**, **„Diese Woche aktuell“**, Neueste Filme/Serien und nutzereigene Reihen beibehalten, wenn Live-TV-Hero aktiviert wird. Persönliche Shortcuts/Layouts byte- und semantisch schützen. Keine Reset-/Widget-Neugenerierung ohne vorheriges Nutzer-Backup.
- Film-/Serienbilder aus dem Provider, ohne unbegründeten TMDB-Helper-Zwang; TMDB-/TVMaze-Suche für **Live-EPG-Bilder**, manuelle Auswahl nach Nutzeraktion. Eigener gespeicherter TMDB-Token unberührt.
- Vorhandenes EPG selbst bei `EPG_CACHE_UNAVAILABLE`, `EPG_DATA_MISSING`, `EPG_DB_BUDGET`, `NO_SOURCE_FACTS` **nicht durch leere Generationen überschreiben**. Exakte Kanal-/Quellenrevision, Negativ-TTL, DB-WAL-/Lesesperren und Retry-Backoff; nicht für jeden Sender dieselben Fehler in kurzer Folge wiederholen. Keine ungenehmigte EPG-Datenbankbereinigung.
- **Echte kleine Statusanzeigen** mit `Sender 88`, `Logos 0/88`, `EPG X`, `Bild gefunden / geprüft / sichtbar / blockiert`; niemals „bereit“, wenn nur URL entdeckt, aber noch kein Bild sichtbar ist. Drosselung/Singleflight bei mehrfachen Widget-Abfragen, eindeutige First-Frame-Messung. Erst Senderrail, dann Logos/erste fünf Sendungsbilder, anschließend Rest; VOD-/Serien-Bilder nachrangig, ohne ihre bestehenden schnellen Cachebilder zu verlieren.

## 8. Präzise Implementation/Gates

**Arbeitsreihenfolge:** (A) Speicher-Mount + 88/0 Diagnose und Skin-Logo-Übergabe, (B) 98 GUI-Exceptions/Control-Reload-Rennen, (C) 30s falsches Cancel + tatsächliches manuelles Speichern, (D) Hero-first-texture und EPG-Datenstabilität, (E) linke Icon-Rail + Bestandswidgets + vollständige Integration. Die Punkte dürfen parallel bearbeitet werden, aber Version/Tests/Release bleiben einheitlich.

**Pflicht-Auslieferung:**
1. GitHub-Branch `fix/xcmate-02987-android86-p0-stability` (oder gleichwertig), **echte** neue Add-on-Version `0.1.29.87`, eigenständiger **Draft PR nach main**; Beiträge aus #412 nach Prüfung selektiv übernehmen und dort Status/Querverweis vermerken. CI/Review nicht mit der veröffentlichten .86 vermischen.
2. Neue redigierte Markdown-Übergabe `docs/XCMate/IMPLEMENTIERUNG_02987_DE.md`, Testbericht `TESTBERICHT_02987_DE.md`, `ANDROID_ABNAHME_02987_DE.md` mit PASS/FAIL/NOT_TESTED pro P0 und Quell-Hash; automatische Tests dürfen **nicht** `ANDROID_PASS` vortäuschen.
3. Reproduzierbare neue ZIP **0.1.29.87** + SHA256 + CRC/Dateiinventar/Quellparität, kein privater Log-/Tokeninhalt. 3 Kodi-Kanäle und Installer **unverändert**, keine automatische Freigabe/Veröffentlichung. `script.gsmedia.setup` bleibt 0.5.26, sofern getrennt nicht beauftragt.
4. Vor Änderung Schutztests: Kodi 21.3 ARM32, Box B, BINGIE 2.2.3, 1080p/720p, Profil-/Token-/EPG-Erhalt, SkinShortcuts/Fokus, alte .86-Installationsfähigkeit, Offline-Neustart. Tests der betroffenen Pfade plus vorhandene komplette Hostsuite mit reproduzierbaren CI-Receipts.
5. **Release-Gates:** 88 Sender ohne verlorenen Fokus; nachweislich sichtbare Logos oder explizit als echtes Speicher-/Quelle-Gate blockiert; BINGIE-Hero auf echten Sendungen, sichere Backdrops/Poster; TMDB+TVMaze manuelle Zuordnung → Save/Readback/Detailbild; null Index-Out-of-Range/Directory-Kills; sieben deutlich verschiedene linke Icons; alle persönlichen Widgets weiterhin vorhanden. Nur echte Android-Gerätetests als ANDROID_PASS. **Vor vollständiger Prüfung und erneuter expliziter Benutzerfreigabe kein Merge nach `main` und kein Release in Original/Pilot/NeoDark3.**

**Wichtig:** Ein als `READY` beschrifteter Status, 3.566 bestandene Hosttests aus PR #412 oder ein erfolgreiches temporäres TMDB-`FOUND` genügt **nicht** als Nachweis, dass das Bild auf dem RK3528-Android-Gerät sichtbar ist. Dokumentiere jeden noch offenen Gate ehrlich.

## 9. Sofort ausführbarer Codex-Einstieg

> Öffne diesen Masterauftrag und die referenzierten GitHub-Issues/PRs, prüfe zuerst den aktuellen Merge-/Versionsstand, übernimm nutzbare #412-Fixes in einen separaten **.87**-Branch, implementiere P0-A/S/L/H/D2/F/G/C/E mit reproduzierbaren Tests und Android-Abnahmematrix, erstelle einen Draft-PR mit neuer ZIP + SHA256; **keinen Merge/Release**, bis der Nutzer nach Prüfung eine neue ausdrückliche Freigabe erteilt. Arbeite ohne Rückfragen zu schon hier geklärten Soll-Anforderungen; markiere unerfüllbare Android-Hardwarebeweise als `ANDROID_NOT_TESTED` statt als PASS.


## 10. P0-I – Nutzerabgenommenes BINGIE-MOD-Hero-Layout und ALLE externen Kodi-Widgets bewahren

**Neuer ausdrücklicher Nutzerauftrag vom 10.11.2026:** „Berücksichtige bitte auch das Aussehen, wie es auf der Bingimod-Seite aussehen soll. Da habe ich dir ein Beispiel für hochgeladen. Und dass die anderen Widgets auch angezeigt werden sollen. wie MP3, in Kino und Serien und die ich noch anders eingerichtet habe, nicht nur die über XMate.“

**Referenzstatus korrekt kennzeichnen:** Der Nutzer hat das BINGIE-Ziellayout zuvor anhand eines eigenen Bildbeispiels freigegeben. Die **schriftliche und nach sechs echten früheren Nutzer-Screenshots dokumentierte Layoutentscheidung** ist vorhanden unter [CODEX_02975_ANDROID_HOME_HERO_ONE_RAIL_SCREENSHOTS_2026-11-05_DE.md](CODEX_02975_ANDROID_HOME_HERO_ONE_RAIL_SCREENSHOTS_2026-11-05_DE.md), insbesondere Kapitel 1 (Fotos 1–6), 2 (Layout und rechte Tabelle) und die Testcases `HERO75-R1..R8`/`H75-01..H75-10`; kurze zusammenfassende Vorgabe in [CODEX_START_HIER_02975_HOME_2026-11-05_DE.md](CODEX_START_HIER_02975_HOME_2026-11-05_DE.md). Auch [CODEX_AUFTRAG_02978_HOME_WIDGET_NAV_ARTWORK_DIRECT_MAIN_2026-11-07_DE.md](CODEX_AUFTRAG_02978_HOME_WIDGET_NAV_ARTWORK_DIRECT_MAIN_2026-11-07_DE.md) enthält die Schutzregeln für alte Widgets. **Die Originalbilder wurden vom Nutzer privat im Chat bereitgestellt und sind hier nicht als nachweislich im Repo vorhandene Rohbilder zu behaupten.** Codex nutzt die bestehende dokumentierte Freigabe, ohne ein neues Layout zu erfinden; für pixelgenauen A/B-Vergleich nur eine tatsächlich zugängliche Referenz verwenden, keine fiktiven Screenshots.

### I-1. Verbindliche BINGIE-MOD-Bild- und Bedienungsgeometrie

- **Großer Hero dauerhaft in stabiler Höhe**, vom oberen Startseitenbereich bis knapp über die aktive horizontale Zeile, bei Kategorie-/Fokus-/Seitennavigation **kein Schrumpfen/Verspringen/Überdecken**.
- **Linke ca. 66–70 % Hero:** bildfüllendes, **zum fokussierten Werk/Event passendes breites TMDB-Backdrop** oder sicherer geeigneter Szenen-Fallback, höchstens dezenter Titel. **Keine lange Beschreibung, Meta-Tabelle, EPG-Zeiten/Progress und keine TMDB-/TVMaze-Quellenlogos links über dem Bild.** Hochformatposter nur in eigens komponiertem unverzerrten Poster-Modus, keine kleinen Covers riesig ziehen.
- **Rechte ca. 30–34 % Hero:** lesbare halbtransparente **Informationstafel** mit tatsächlichem Sendernamen/Logo, **JETZT / DANACH**, Sendezeiten, Fortschritt/Restzeit, Beschreibung; bei Filmen/Serien korrekte Medienmetadaten. Quellenbelege `Bild: TMDB/TVMaze/Provider` und ggf. `Daten: ...` klein am **unteren Rand der rechten Tafel** und nur für tatsächlich belegte Quellen; keine falschen Quelllogos.
- **Direkt darunter genau EINE aktive, zum Fokus passende kompakte horizontale Rail** für Live-Sender-Logos **oder** XCMate-Filme/Serien-Cover; keine zwei konkurrierenden Rails gleichzeitig *innerhalb der aktiven Hero-Komposition*, keine horizontalen Rails quer durch das Seitenmenü. Fokusrahmen exakt um das ausgewählte Element, Hero-Identität + EPG + Quelle synchron dazu. Live-Startgruppe dynamisch aus Nutzerkonfiguration (88 nur derzeitige Momentaufnahme; auch 5/256 Sender korrekt).
- **Linke Haupt-Icon-Navigation** in XCMate Space Blue wie P0-G beschrieben; SkinShortcuts und persönliches BINGIE-Home-Menü unangetastet. Kein ungefragtes globales Skin-Reset oder „Reparieren“ durch vollständige Home-Neugenerierung.
- **WICHTIGE Unterscheidung:** Die Regel „eine aktive Rail direkt unter dem Hero“ gilt nur für die gerade **fokussierte Hero-Komposition**. Sie ist **kein** Auftrag, weitere unterhalb konfigurierte eigenständige **BINGIE-Startseiten-Widget-Reihen auszublenden oder zu löschen**. Mehrere unterschiedliche Nutzer-Widget-Abschnitte bleiben in der regulären **vertikalen BINGIE-Home-Seite** sichtbar, navigierbar und in ihrer Reihenfolge erhalten. Bei Fokuswechsel kann jeweils nur die aktive zugehörige Rail im Hero-Fokus dargestellt werden, ohne dass alle anderen konfigurierten Reihen verschwinden.

### I-2. Fremdwidgets – nicht nur XCMate erhalten

**Explizit schützen und auch tatsächlich wieder sichtbar machen** (jeweils sofern bereits vom Nutzer eingerichtet):
- **Musik/MP3:** `MP3 Streams Echoed` (Kodi-Addon `plugin.audio.m3sr2019`), ggf. **SHOUTcast** sowie andere Audio-/Musikwidgets;
- **Kino:** „Im Kino“, „Neu im Kino“, „Frisch im Kino“, „Diese Woche aktuell“, „Diese Woche im Trend“ und andere bereits vorhandene Kinoreihen/Empfehlungen, einschließlich Quellen anderer Add-ons;
- **Serien:** selbst konfigurierte Serien-/Streaming-/Trend-Widgets, einschließlich derjenigen von anderen Add-ons, nicht nur `widget_recent_series`;
- **Alle sonstigen** bestehenden manuell eingerichteten Home-Abschnitte, Shortcuts, Fremd-Add-on-Widgetpfade, Bibliotheks- und Favoritenwidgets, Kategorien und Unterreihen.

**Ein Widget mit fremdem `plugin://...` oder SkinShortcuts-Eintrag ist eine bestehende Nutzerkonfiguration; niemals nur deshalb entfernen oder durch XCMate ersetzen, weil es sich nicht um `plugin.video.xtreammate` handelt.** BINGIE darf die fremden Widgets weder via `visible=false`, überschreibender `Skin.String`, leere `Container.Content`-Zuordnung, Widget-Scheduler-Gate noch über globale Widget-Limits still unterdrücken. Falls die fremde Datenquelle selbst vorübergehend ausfällt, ihre Widget-Definition und Position erhalten, einen lokal verfügbaren letzten Stand oder ehrlichen Lade-/Fehlerstatus darstellen und später selbstständig wieder füllen; nicht als erfolgreiche Leerstelle oder mit XCMate-Items kaschieren.

### I-3. Migration/Datenschutz und Regressionen

1. **Vor jeder Skin-/XML-/Widget-Änderung read-only Snapshot** der tatsächlichen Skin-Revision, `SkinShortcuts`-Konfiguration, individuellen Menü-/Widgetdefinitionen, Reihenfolge, Bezeichnungen, `plugin://`-Quellen, Aktivierungsstatus, Focus-/Property-Scope und aktiven Includes – lokal/privat und mit Checksumme. Benutzerdateien niemals in öffentliches GitHub/CI hochladen. Automatisches Patchen nur nach verified active Skin-Hash, **idempotent** und mit atomarem Backup/Revert.
2. **Provisorische Erweiterung statt Ersetzung:** XCMate-Zeilen dem existierenden Home gezielt hinzufügen, niemals einen Benutzerhome-Abschnitt global neu generieren. Keine Reinitialisierung von SkinShortcuts, `Home.xml`, globalen Skin-Strings, Nutzer-Reihen, Shortcut-Caches oder Drittanbieter-Add-ons. Bei nicht unterstütztem Skinzustand `SKIN_MIGRATION_BLOCKED` melden und alte Konfiguration lassen.
3. **Die alten Widgets müssen vor und nach dem Live-Hero-Nachladen vorhanden und sichtbar bleiben**, nicht nur noch in einer XML-Datei stehen. Verifizierte Qualität im BINGIE-Home: Musik/MP3 Streams, Kino, Serien, ≥2 beliebige andere manuell erstellte externe Widgets mit nicht-XCMate-`plugin://`-Quellen; Kategorien, Direktstart mit OK, Inhalt nach Cold/Warm/Offline-Neustart.
4. **Native 720p und 1080p Android A/B-Abnahme** anhand verfügbarer alter Layoutvorgaben: Hero links Bild/rechts Tabelle; konstante Höhe; keine Rails/Details/Fokus-Überlappungen; sichtbare Benutzerreihen einschließlich MP3, Kino und Serien; korrektes vertikales Scrollen zwischen Live/XCMate und allen fremden Reihen; zehnfache Navigation zwischen fremden Widgets ohne `Index out of range`, `GetDirectory`-Fehler oder verlorenem Fokus. Bei Provider-/Musik-Netzwerkausfall bleibt die Zeile bestehen und wartet mit eigenem nachvollziehbarem Status.
5. **Test-Suite mit realistischen nichttrivialen BINGIE-Konfigurationen**, keine Simulation, die lediglich drei XCMate-Widgets besitzt. Inventar/Diff vor/nach Update: **exakte externe Widgetanzahl, Namen, Reihenfolge, `plugin://`-Paths und erlaubte Sichtbarkeit unverändert**, dazu zusätzliche XCMate-Funktionen. Bei Verlust einer alten Reihe **P0-I FAIL und kein Release**, selbst wenn die XCMate-Hero-Screenshots schön aussehen.
6. Regressionen für **MP3 Streams Echoed, SHOUTcast, Im/Neu/Frisch im Kino, mehrere Serien- und freie Nutzerwidgets** aufnehmen. Auch vollständige normale Startseite (nicht nur direkt fokussierter Hero) und scrollbare Abschnitte mit dem Nutzer-Referenzlayout vergleichen. Testergebnisse im `ANDROID_ABNAHME_02987_DE.md` explizit als **P0-I** führen.

**Freigabe:** `.87` gilt **nur** dann als visuell korrekt und bestandsschutzsicher, wenn **BINGIE-Hero-Gestaltung UND sämtliche bestehenden Drittanbieter-Widgets gleichzeitig funktionieren**. Fehlende Original-Screenshotdateien sind klar als `REFERENZBILD_NICHT_VERFÜGBAR` zu markieren, nicht mit erfundenen Bildelementen auffüllen. Für die tatsächliche Android-Pixel-Abnahme die private Vorlage nur bei realer Zugänglichkeit heranziehen; alle bereits dokumentierten Layoutmaße bleiben auch ohne erneutes Bild verbindlich.
