# Codex-Übergabe – XCMate 0.1.29.77 (kumulatives P0-Update)

**Stand:** 06.11.2026 · **Status:** ARBEITSAUFTRAG, NOCH KEIN BUILD/RELEASE · **Master:** [Issue #380](https://github.com/artattakk-creator/kodi-noodleprivate/issues/380)

> **Codex-Start:** Lade dieses Dokument, den [ausführlichen Masterauftrag](./AUFTRAG_02977_MEDIEN_EXIT_TMDB_TVMAZE_EPGBILDER_DE.md) und die Issues [#366](https://github.com/artattakk-creator/kodi-noodleprivate/issues/366), [#367](https://github.com/artattakk-creator/kodi-noodleprivate/issues/367), [#368](https://github.com/artattakk-creator/kodi-noodleprivate/issues/368), [#380](https://github.com/artattakk-creator/kodi-noodleprivate/issues/380). Behebe sämtliche P0-Befunde in einem kumulativen XCMate-Release **0.1.29.77**; keine Zwischenveröffentlichung .76 erforderlich, kein Downgrade/Deinstallieren. Führe Tests und Source-Merge nach \`main\` erst nach bestandenen CI-Prüfungen aus; veröffentliche das Add-on zunächst nur auf **GS Media Pilot**. **Nicht** eigenmächtig regulär freigeben.

## 1. Bestätigter Versions- und Veröffentlichungsstand

- GitHub: \`artattakk-creator/kodi-noodleprivate\` (default branch \`main\`).
- XCMate-Quellcode \`src/plugin.video.xtreammate/addon.xml\`: **0.1.29.76**, kumulativer Bestand; [PR #370](https://github.com/artattakk-creator/kodi-noodleprivate/pull/370) ist bereits nach \`main\` gemergt.
- GS-Media-Pilot \`online-test/addons.xml\`: **0.1.29.75**; regulärer Kodi-Katalog \`addons.xml\`: **0.1.29.74**.
- Echtes Kodi-Android-Gerät laut Logs vom 06.11.2026: **XCMate 0.1.29.75**, Kodi 21.3 Omega, Android ARM32, Rockchip RK3528, Titan BINGIE MOD 2.2.3, Space Blue Manager 0.2.0.
- **Sollpfad auf der Testbox: 0.1.29.75 → 0.1.29.77 direkt**. Alle .76-Änderungen (einschließlich Widgets/Startseiten- und Ladeprioritäts-Code) bleiben enthalten. **0.1.29.76 nicht separat installieren**; ein einziger Pilot-Testlauf der vollständigen .77.
- **GS Media Installer 0.5.26 bleibt eingefroren.** Es ist ein getrenntes Projektartefakt. Keine Installer-Neufassung, kein Neuaufsetzen von Kodi und kein Android-Systemimage.

## 2. P0-A – Hänger beim Verlassen von Serien, Filmen und Live-TV

**Belegte Android-Fehlerkette am 06.11., ca. 21:24:34:**
\`[PLAYER_EXIT] EXIT_INTENT reason=USER_BACK kind=media\` → \`PROGRESS_SNAPSHOT_DONE\` → \`PLAYER_STOP_START\` → Kodi \`VideoPlayer: waiting for threads to exit\`; Audio-/Videothreads melden Ende, jedoch **kein** \`VideoPlayer: finished waiting\`, kein \`PLAYER_STOP_DONE\`, keine bestätigte Rückkehr. Danach Server-/Socketfehler und neuer Kodi-Start um 21:28. **Die genaue Native-Thread-Ursache ist nicht bewiesen**; kein blindes Zusammentreffen von Live- und Media-Routen behaupten. Ein Live-Stop gelang im selben älteren Log mit \`STOP75 ACK\` und \`HOME_VISIBLE\`.

**Implementieren:**
1. Reale Callgraphs \`native_stop41.py\`, \`live_exit.py\`, \`playback_exit.py\`, \`exit_jobs.py\`, Serien-Autoplay, Player/Window-Navigation nachverfolgen; Media/Series/VOD/Live getrennt instrumentieren.
2. Pro aktiver Session ein eindeutig identifizierter Player-Owner, ein idempotenter Stop-Intent, kontrollierte Native-Kodi-Stop-/ACK-/OnStop-Behandlung ohne blockierenden GUI-Thread und ohne mehrfachen Stop desselben Players.
3. Sichere Timeout-/Fehlerbehandlung: keine Endlosschleife, kein fälschliches \`COMPLETE\` bei fehlender Bestätigung, kein Stop fremder Player. Episodenfortschritt und gewählte Staffel erhalten. Nach tatsächlichem Stop zuverlässig zur vorherigen XCMate-Ansicht zurückkehren.
4. Host-/State-Machine-Tests plus auf Android **mindestens 20** reproduzierbare Stop-/Back-Zyklen je **Serie, Film/VOD, Live-TV**, einschließlich Autoplay/EOF, schneller Back-Wiederholung, aktiver OSD, Netzwerkstörung und Kodi-Neustart.

## 3. P0-B – EPG stabilisieren und tatsächliche Sendungsbilder liefern

**Belegte alte Android-.75-Logzähler** (mehrfache Abfragen, keine Anzahl unterschiedlicher Sendungen): \`EPG63 DB_READ=18.145\`, davon \`EPG_DATA_MISSING=16.935\`, \`READY=729\`, \`EPG_CACHE_UNAVAILABLE=444\`, \`EPG_DB_BUDGET=37\`. Viele Missing-Fälle bei \`PROVIDER_ID\`, andere \`STREAM_ALIAS\` dagegen READY. Artwork: \`BLOCKED_IMAGE_HOST_OR_URL=636\`, \`AWAITING_BACKGROUND_REFRESH=1.064\`, \`FETCH_FAILED=79\`, aber nur \`IMAGE_URL_READY=22\`; ein Film-Widget hatte 24/24 Platzhalter, null gematchte Bilder.

**Verbindliche Bildquellenlogik (einheitlicher Modus, keine drei manuellen Schalter):**
1. Bestehende **XMLTV- und Provider-Bilder** zuerst anhand des **genau passenden EPG-Events** verwenden. Kanal-/ID-/Zeit-/Titel-Matching sauber mit Fallback \`PROVIDER_ID\` → \`STREAM_ALIAS\` → explizite gültige manuelle Zuordnung; keinen falschen Sender/Text vermischen.
2. **Filme:** den bereits vorhandenen **eigenen TMDB-Token** bei gültiger Read-only-Prüfung für TMDB-Artwork verwenden. **Serien/Episoden:** TMDB, dann **TVMaze standardmäßig als Fallback**, mit exakter Serien-/Episodenidentität. TVMaze ist kein garantierter Film-Bildanbieter.
3. Nutzer hat die automatische Nutzung dieser Dienste für seine Installation ausdrücklich gewünscht. Datenschutz-/Netzwerkhinweis im einmaligen Einrichtungs- bzw. Migrationsprozess; verständlicher zentraler Bildquellenstatus. **Explizite Opt-outs erhalten**, nicht bei jedem Start zurücksetzen.
4. **TMDB-Bestandsschutz: absolut**. Bereits importierte Token-Datei, Legacy-Setting und Zugangsinformationen nicht löschen/überschreiben/umbenennen/neu importieren. Nur read-only prüfen, Vorher-/Nachher-Fingerprint ohne Tokeninhalt; **keine Tokenwerte in CI, Kodi-Logs oder GitHub**. Alle erfolgreichen Importvarianten müssen bei gültigem Token die verknüpften Schalter \`programme_tmdb46\` und \`tmdb_research43\` aktivieren. Bestehenden gültigen Import nach dieser Nutzergenehmigung einmalig migrieren, nicht bei jedem Start neu freischalten. \`programme_tvmaze67\` als aktivierter Serien-Fallback, bewusste spätere Deaktivierung respektieren.
5. Die \`NO_IMAGE\`-Negativcache-Logik (\`programme_art46.py\`, sechs Stunden) darf erlaubtes TVMaze/XMLTV/Provider-Fallback nicht verhindern. Bei berechtigtem Quellenwechsel gezielt neu bewerten.
6. Sicherheitsprüfung für Bild-URLs/HTTPS/Content-Type/Redirects in \`programme_urls55.py\` und \`programme_origin75.py\` korrekt für vertrauenswürdige Provider-/XMLTV-CDNs, TMDB, TVMaze; **keine globale Wildcard**. Weder Provider-URLs noch Token in Telemetrie.
7. Ein und derselbe Event-Key muss dieselbe gültige Bildreferenz im **Mini-EPG, großen EPG und BINGIE-Hero** liefern. Fest gespeicherte Daten aus lokalem Cache laden, kein HTTP im Fokus-/GUI-Thread. Nicht nur \`IMAGE_URL_READY\`, sondern **tatsächlich gerenderte Kodi-Textur** auf Android nachweisen.

**Ladepriorität:** EPG-DB/Startgruppe → Senderlogos + Jetzt/Danach + Hero + erste sichtbare Sender → Filme → Serien → übrige Hintergrundbilder. Keine fortwährenden 88-Sender-Vollscans beim Fokuswechsel. Cache regelmäßig aktualisieren, dokumentierte 24-h-EPG-Aktualisierung und verfügbare Vergangenheit/Zukunft erhalten.

## 4. P0-C – Native BINGIE-Home-Geometrie und Fokus

Aus Android-.75-Log: **24× \`HOME75 RENDER_CONTROL_MISSING\`**, **3× \`FOCUS_OVERRIDE\`**. Ein installierter Space Blue Manager beweist **nicht**, dass XCMate-eigene Hero-Render-Controls korrekt integriert sind.

**Verbindliches Layout der früheren Nutzervorgaben:**
- **Vergrößerter, dauerhafter Hero**, großflächiges Programmbild über die komplette vorgesehene Fläche; beim vertikalen Scrollen **weder schrumpfen noch abschneiden**.
- Senderlogo plus **Jetzt/Danach**, Zeiten, Beschreibung und Fortschrittsbalken als lesbares Overlay; korrekte Bild-Event-Zuordnung und Fallback.
- Unter dem Hero **genau eine aktive schmale horizontale Sender-/Coverleiste**, Live-TV mit kleinen Senderlogos, navigierbar über die gesamte Startgruppe; dann eigenständige Filme-/Serienleisten.
- **Fokusrahmen exakt an der ausgewählten Kachel**, keine Verschiebung bis in die nächste Reihe, keine Fokus-/Hero-Geometrie-Regression; bei Fokusänderung sofort gültige Informationen ohne Streamstart anzeigen.
- Native Skin-XML-Control-/Property-IDs, Hook-Installationsstatus und aktuelle 1080p-Koordinaten gezielt auf echter BINGIE-2.2.3-Installation prüfen. Original-Dateien vor eventuellem Skin-Patch sichern, idempotentes Rücksetzen, Benutzerprofile/Space-Blue-Patch schützen. Kein alleiniger Erfolg aufgrund synthetischer 720p-Mockups.

## 5. P0-D – Unabhängiger Kodi-MyVideos-Datenbankbefund

Das Gerät protokolliert \`MyVideos131.db: no such table: movie_view\` (20× im langen und 8× im kurzen Log). Unabhängig von XCMate-Hero und Artwork untersuchen, ob eine fehlende View, falsche DB-Migration oder inkompatible Datenbankabfrage vorliegt. **Keine Datenbank löschen, leeren oder automatisch neu initialisieren**; zunächst Snapshot, Schema- und Query-Vergleich und rückbaubare Korrektur.

## 6. Regression, Zustands-/Geheimnisschutz und Release-Gates

**Strikte Unveränderlichkeits-Gates:**
- TMDB-Tokenbytes unverändert, keine Logs/Commits mit Zugangsdaten.
- EPG-Quellen, Sender-Mappings, Favoriten, Playerpräferenzen, Skin- und Space-Blue-Bestand, Serienfortschritt, Kodi-Userdata und bestehende Datenbanken erhalten.
- Installer 0.5.26, dessen ZIP, Katalogeinträge und Konfiguration vollständig unberührt; keine anderen Add-ons deinstallieren.
- Alle Änderungen von 0.1.29.76 plus frühere kumulative Fixes in .77 weiterhin vorhanden; **kein Neubau auf .75**, der .76-Funktionen verliert.

**Automatisierte Abnahme:** Lint/Python-Syntax, Host-/Unit-/Integrations-/negative Tests der Exit-Session-FSM, TMDB-Migration/Opt-out, XMLTV/Provider ohne Token, Serien-Fallback TVMaze, Film mit TMDB, Bildhost-Sicherheit, Event-/Cache-/Kodi-Binding, Home-Patch-Kontrollstruktur/Fokus; ZIP-CRC, \`addon.xml=0.1.29.77\`, SHA256, Repository-Index & MD5, keine anderen Add-on-IDs/Versionen berühren.

**Veröffentlichungsreihenfolge:**
1. Codex implementiert auf neuem Branch, führt CI/Regressionen aus, dokumentiert Ergebnisse und erstellt prüfbaren Pull Request für die kumulative .77.
2. Bei grünem CI **Source-PR nach \`main\` mergen**. Geprüftes **0.1.29.77-ZIP ausschließlich GS Media Pilot** verfügbar machen, Pilot-\`addons.xml\`/MD5/Index konsistent aktualisieren. Versionsgleichheit/Unverändertheit und bestehende .75/.76-Artefakte beachten. **Reguläres \`addons.xml\` bleibt auf .74**, bis der Nutzer Android-PASS ausdrücklich bestätigt und produktive Veröffentlichung autorisiert. **NeoDark3 nicht unbemerkt auf dieselbe experimentelle XCMate-Fassung umstellen**, sofern es dadurch einen produktiven Kanal verändern würde.
3. Android-Kodi-21.3-ARM32-Geräteabnahme mit echten Provider-/EPG-Daten: stabiler Medien-Exit (20× je Typ), tatsächliche Live-Hero-Bilder und Mini-/Groß-EPG-Bilder, passende Jetzt/Danach-Daten, voller feststehender Hero und stimmiger Fokusrahmen.
4. Statuswerte korrekt als \`HOST_PASS\`, \`ANDROID_NOT_TESTED\`, \`ANDROID_FAIL\` bzw. \`ANDROID_PASS\` protokollieren. Nie einen erfolgreichen CI-Lauf als erfolgreichen Android-Bild- oder Player-Test ausgeben. Rollback sicher und nicht destruktiv.

## 7. Übergabe-Rückmeldung von Codex

Am Ende in GitHub dokumentieren: Branch, PR, Source-Merge-SHA, exakte .77-ZIP/SHA256, Dateiliste und Unterschiede gegenüber .76, Testbefunde pro P0-Punkt, Pilot-\`addons.xml\`-Version/Downloadlink, **regulärer Kanal unverändert**, Android-Testplan, offene Probleme; die Aussagen mit überprüfbaren Logs/CI-Artefakten belegen. Rohlogs nicht veröffentlichen.

**Ein Satz als Freigabekriterium:** *Die Testbox aktualisiert XCMate direkt von 0.1.29.75 auf die vollständig kumulative 0.1.29.77, ohne jemals 0.1.29.76 einzeln installieren zu müssen, ohne den TMDB-Token oder Kodi-Daten anzutasten, und zeigt erst nach Geräteabnahme einen fehlerfrei beendbaren Player sowie richtige Bilder und die vereinbarte große BINGIE-Startseite.*
