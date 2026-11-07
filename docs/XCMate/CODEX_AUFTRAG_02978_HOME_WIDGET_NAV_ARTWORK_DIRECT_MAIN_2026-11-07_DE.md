# Codex-Übergabe: XCMate 0.1.29.78 – BINGIE-Home/Widgets/Navigation/Artwork

**Datum:** 07.11.2026 · **Verbindlicher GitHub-Masterauftrag:** [Issue #385](https://github.com/artattakk-creator/kodi-noodleprivate/issues/385) · **Status:** **AUFTRAG**, weder Reparatur noch Build/Release durch diese Dokumentation erfolgt.

## Codex-Kurzauftrag – sofort ausführen

> Arbeite in `artattakk-creator/kodi-noodleprivate`. Lies **Issue #385 vollständig** einschließlich der neuen anonymisierten Android-Logbefunde und die älteren Fehlerissues [#366](https://github.com/artattakk-creator/kodi-noodleprivate/issues/366), [#367](https://github.com/artattakk-creator/kodi-noodleprivate/issues/367), [#368](https://github.com/artattakk-creator/kodi-noodleprivate/issues/368) und [#380](https://github.com/artattakk-creator/kodi-noodleprivate/issues/380). **Behebe jetzt die Regressionen der XCMate-Startseite kumulativ auf dem aktuellen Source-Stand 0.1.29.77. Erstelle 0.1.29.78, führe alle CI-Regressionstests durch, merge bei Erfolg den Source-PR direkt nach `main` und veröffentliche die neue .78 aus `main` unmittelbar im regulären GS-Media-Katalog, im GS Media Pilot sowie über den NeoDark3-Direktweg – ohne zusätzliche Rückfrage.** Bei roten Tests oder Versionskonflikten fail-closed; kein ungeprüfter Merge/Release. Damit ist eine unmittelbare Update-Verfügbarkeit genehmigt, **nicht** aber ein künstlicher Android-PASS.

## Ausgangslage

Die echten Kodi-Logs vom 07.11.2026 belegen **XCMate .77**, Kodi 21.3 Omega ARM32/RK3528, Titan BINGIE MOD 2.2.3 in 1920×1080, Installer 0.5.26 und Space-Blue-Manager 0.2.0. Quell-`main` = .77, Pilot-Katalog = .77, regulärer Katalog = .76. Die privaten Rohlogs sind NICHT auf GitHub zu veröffentlichen. Für .78 ist ein einziges kumulatives Update vorgesehen (keine Neuinstallation/Profilreset/Downgrade).

### P0-A – BINGIE-Hero/Controls & alte Widgets

Die Android-Logs zeigen `Non-Existent Control 296301/296751`, 14 fehlende `XCMate75.*`/`XCMate63.*`-Skin-`$VAR`, `RENDER_CONTROL_MISSING` und `NATIVE_HOME_UNVERIFIED` **trotz `SKIN_PATCH_VERIFIED`**. Repariere das falsche Patch-Gate, Skin-Includes/Variablen/Control-IDs und die Laufzeitbindung, einschließlich sicherer idempotenter Skin-Hook-Patches. Vorher die vorhandene Nutzer-/SkinShortcuts-Konfiguration und alte Widget-Pfade read-only inventarisieren und lokal sichern; **„Neu im Kino“ und alle zuvor eingerichteten Reihen** wieder sichtbar machen, ohne Default-Anordnung über Nutzeranordnung zu schreiben. Die Logs beweisen nicht, dass Widgets gelöscht wurden; auch defekte Datenquellen, Render-Controls und Kodi-Datenbank-Views als Ursachen prüfen.

Endlayout: **fester großer Hero** mit echtem Live-Bild, Senderlogo, Jetzt/Danach, Beschreibung, Fortschritt; darunter eine **jeweils aktiv sichtbare kompakte Leiste** bei Navigation, wobei alle weiteren Film-/Serien-/Kino-/Nutzer-Widget-Reihen **bestehen bleiben und erreichbar sind**. Fokusrahmen exakt an der gewählten Kachel; 1080p und 720p richtig; kein Hero-Schrumpfen oder Verschieben beim Scrollen. Space Blue nicht überschreiben.

### P0-B – Film-/Serien-Daten / Refresh

Beide Datenlisten sind am 07.11. im Log mit **24 VOD- und 24 Serien-Items (SQL READY)** vorhanden. Nicht voreilig Provider-/Index-Verlust behaupten. `BLOCKED_NO_RELOAD_HOOK`, `NATIVE_HOME_UNVERIFIED`, `REFERENCE_READY` ↔ `REFERENCE_PARTIAL`-Statusflackern und neue `HOME74 COMMIT`-Generationen beheben. Fehlende/doppelte Kodi-Refresh-Mechanik, Fehlertoleranz, unzulässige stale Generation und Fokussynchronisation prüfen. Vorhandene Provider-Poster/-Cover für VOD/Serien nutzen; die gezeigte URL allein beweist noch keine sichtbare Kodi-Textur.

### P0-C – EPG-/Artwork-Bilder bis zum Skin

`IMAGE77 EXACT_MATCH → URL_SECURITY BLOCKED`, `BLOCKED_IMAGE_HOST_OR_URL` und `RENDER_CONTROL SOURCE_MISSING control=110 visible=false` belegen getrennte Fehler in URL-Sicherheit und Texturanzeige. Sichere erlaubte XMLTV-/Provider-CDNs, TMDB-/TVMaze-Fallbacks, Match-Identität, lokalen Cache, Kodi-GUI-Property/Control/Texture nachvollziehen. Keine globale Host-Freigabe und keine falschen Bilder. Bereits importierten **TMDB-Token bytegenau erhalten**, dessen autorisierte Nutzung automatisch aktivieren, TVMaze für Serien als Fallback; bewusstes Nutzer-Opt-out respektieren. Beim `PROVIDER_ID EPG_DATA_MISSING` sichere verifizierte `STREAM_ALIAS`-Quellen/Zuordnungen verwenden.

### P0-D – Navigation / Kodi-Library / Player

- `NAV ANCHOR_TIMEOUT` und ungültiger `ActivateWindow(Videos,...)`-Aufruf (`unsupported protocol(activatewindow(videos,"plugin)`) müssen verschwinden. Navigation über Live-TV, Filme, Serien, alle alten Widgets, OK/Zurück und vertikalen Fokus testen; keine Keymaps oder Fernbedienungsprofile zurücksetzen.
- `MyVideos131.db` ohne `movie_view`, `tvshow_view`, `musicvideo_view`: Bibliotheks-Widget-Datenquellen und DB-Schema prüfen. **Niemals DB blind löschen, zurücksetzen oder ohne Sicherung verändern.** XCMate-Providerwidgets sind unabhängig von Kodi-Library-Views nutzbar zu halten.
- Native Stop-ACK kommt bei Live teilweise erst **nach 7,8 s**, während das Timeout schon nach 5 s feuert. Kein falsches Stop-Ergebnis, keine GUI-Blockade/Mehrfach-Stopps; Live- und Media/Serien-Exit getrennt prüfen.

## Test- und Freigabevertrag

1. Tests mit nichttrivialer vorhandener SkinShortcuts-Konfiguration incl. „Neu im Kino“, BINGIE 2.2.3, 1080p/720p, Space Blue, fehlenden Skin-Controls, falscher/fehlender $VAR, leeren bzw. fehlerhaften Kodi-Views, staler Widget-Generation und fehlendem Reload-Hook. Ein Add-on-/Skin-Patch-Gate gilt **nur PASS, wenn tatsächlich verwendete Window-Controls und Variablen im aktiven Skin verfügbar sind**.
2. Daten-/Bildtests: 24 Film- und 24 Serien-Einträge, Poster aus den tatsächlichen Provider-Daten, sichere Bild-URLs, EPG Event-ID/Cache und echte Texture-Bindung, EPG und Hero, Fokus/Refresh ohne Zurücksetzen. `IMAGE_URL_READY` != Bild sichtbar.
3. Navi-/Exit-Regression: Anker, Builtin-Quoting, mehrfaches Back, verschobener Fokus, Exit nach Serie/Film/Live, keine nicht bestätigten Stop-Erfolge.
4. **Keine Änderung** an `script.gsmedia.setup 0.5.26`, bestehendem TMDB-Token oder Benutzer-/Provider-/EPG-/Favoriten-/Skin-Daten. Keine privaten Rohlogs/IPs/Provider-URLs/Secrets hochladen.
5. Build reproduzierbar als `plugin.video.xtreammate-0.1.29.78.zip` inklusive SHA256; Source-ZIP-Parität, ZIP-CRC und Kodi-Addon-XML-Index/MD5 prüfen; Source-PR nach **grünem CI direkt nach main mergen**.
6. **Sofortige Veröffentlichung .78 nach dem Merge** im regulären GS-Media-Repository (`addons.xml` + ZIP), GS Media Pilot (`online-test/addons.xml` + ZIP) sowie NeoDark3 (gültiger Direktlink/Index). Drei ZIP-Pfade **byteidentisch**, Git SHA/Hashes/Versionen dokumentieren, ältere ZIPs bestehen lassen. **Nicht nur Source-Code mergen** und dann ohne installierbares Update stoppen.
7. Geräteabnahme ehrlich: automatische Host-CI = `HOST_PASS`, **Android bleibt `NOT_TESTED`**, bis Nutzer die .78 tatsächlich prüft. Erst dann `ANDROID_PASS`/FAIL je P0. Explizite Sofortveröffentlichungsfreigabe gilt **nur .78**; zukünftige Versionen erfordern separate Entscheidung.

## GitHub-Abgabe

Dokumentiere in [#385](https://github.com/artattakk-creator/kodi-noodleprivate/issues/385): Branch, PR, Merge-SHA, geänderte Module/Skin-Hooks, CI-Lauf mit Tests, drei Kanalstände/ZIP-Downloads/SHA256, zurückgehaltene Daten und offene Android-Befunde.

**Kurzdefinition von Erfolg:** Der Nutzer erhält **sofort ein updatefähiges .78-Paket** auf allen drei Kanälen; echte visuelle Fehler werden nach Geräteprüfung beurteilt. Die zuvor eingerichteten Widget-Reihen, darunter **„Neu im Kino“**, bleiben vorhanden, Film-/Serien-Widgets und Live-EPG sind korrekt mit dem großen Hero und der Navigation verbunden.
