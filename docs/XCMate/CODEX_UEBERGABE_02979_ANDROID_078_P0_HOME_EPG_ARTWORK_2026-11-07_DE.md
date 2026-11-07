# Codex-Übergabe: XCMate 0.1.29.79 – Android-.78-Folgefehler
Datum: 07.11.2026 | Master: https://github.com/artattakk-creator/kodi-noodleprivate/issues/387 | Vorgänger: #385 und PR #386.
Status: VERBINDLICHER AUFTRAG, **NOCH NICHT IMPLEMENTIERT, GEMERGT ODER VERÖFFENTLICHT**.

## Codex-Start

Arbeite im Repository artattakk-creator/kodi-noodleprivate auf aktuellem main. XCMate-Source, regulärer Kodi-Katalog und Pilot haben Version **0.1.29.78**. Ziel ist das kumulative Update **0.1.29.79**, keine Rückinstallation/kein Kodi-Reset. Lies zuerst Master-Issue #387 vollständig, danach #385 (BINGIE/Widgets) und #366/#367/#368/#380.

### 1. Die echten Android-.78-Belege (07.11.2026)

Vier vom Nutzer privat gelieferte Logs: kodi.old(20261107-160918).log, kodi(20261107-160918).log, kodi.old(20261107-161108).log und kodi(20261107-161108).log. Die beiden 17:05-Dateien überschneiden sich; **nicht doppelt zählen**. Start 16:49:50 ist XCMate .77, Starts 17:05:35 und 17:09:06 sind **.78**. Android ARM32, Kodi 21.3, RK3528, 1080p. BINGIE MOD 2.2.3 sowie Installer 0.5.26 sind installiert; das Fehlen des Skins wird in diesen Sessions nicht bestätigt. **Private Rohlogs/URLs/Tokens NICHT nach GitHub hochladen.**

- Runtime-Home: 17:06:45 zeigt WIDGET47 NATIVE_HOME_EMPTY mit directory_ok=0, items=0, decode_verified=-1 für live/vod/series. Um 17:07:53 SKIN_FILES_VERIFIED, um 17:08:02 trotzdem erneut NATIVE_HOME_EMPTY. 17:08:35 VOD ausnahmsweise NATIVE_HOME_ITEMS items=24, directory_ok=1, aber decode_verified=-1. Nach dem Neustart 17:09 erneut alle drei NATIVE_HOME_EMPTY. **Skin-Dateien vorhanden ist kein positiver Kodi-Runtime-/Pixel-Nachweis.**
- Datensatz/Poster: Film-/Serienabfragen selektieren jeweils 24 Einträge. Im ersten .78-Start teils 18 dynamische VOD- und 10 Serien-Bildreferenzen (restliche Placeholder), im zweiten kurzen .78-Start vorübergehend wieder je 24 Placeholder / null dynamische Referenzen. Das beweist keinen dauerhaften Verlust, ist aber ein belegter Cold-Start-/Cache-/Generation-Risikopfad.
- EPG im jüngsten kurzen .78-Start: 191 EPG_DATA_MISSING, 13 EPG_CACHE_UNAVAILABLE, 28 READY und 2 EPG_DB_BUDGET; es handelt sich um wiederholte Reads, nicht unterschiedliche Sender.
- Bilder: drei IMAGE77-Ketten von URL_SECURITY APPROVED über IMAGE_DECODED und IMAGE_LEASE BOUND bis LOCAL_CACHE PERSISTED. IMAGE77 ist der alte Diagnosepräfix, nicht die installierte Add-on-Version. Die echte Sichtbarkeit im BINGIE-Hero/EPG ist **nicht** nachgewiesen.
- Kodi-Bibliothek: MyVideos131.db meldet weiterhin missing movie_view, tvshow_view, musicvideo_view. Diese Views könnten klassische Zeilen wie „Neu im Kino“ beeinträchtigen, die genaue Ursache ist noch offen.
- Player-Exit: kein STOP_TIMEOUT im kurzen .78-Log reproduziert, daher **ANDROID_NOT_TESTED**, keinesfalls PASS.

### 2. P0-A: Native BINGIE-Home-Consumer / vollständige Benutzer-Widgets

- Prüfe dynamische Plugin-Directory-Routen, aktive Kodi-Window-IDs und Controls, BINGIE-SkinShortcuts, native Widget-Consumer, Property- und Texture-Binding, Skin-Reload-Hooks, Focus-Anker.
- Baue einen korrelierten Statuspfad: SOURCE_READY -> DIRECTORY_ITEMS -> SKIN_CONSUMER_READY -> RELOAD_ACK -> ACTIVE_CONTROL -> TEXTURE_VISIBLE. Kein positiver Erfolg auf Basis von SKIN_FILES_VERIFIED, ITEMS=24 oder Source-Property allein.
- Inventarisiere die bestehenden Skin-/SkinShortcuts-Widget-Pfade und Benutzeranordnung READ-ONLY vor jeder Änderung. „Neu im Kino“ sowie alle persönlichen Film-, Serien-, Live- und sonstigen Reihen erhalten. Nie ein Default-Layout über gespeicherte Benutzerdaten schreiben.
- Hero weiterhin groß/fest, Senderlogo, Bild, Jetzt/Danach, Beschreibung, Fortschritt. Darunter die kompakten horizontalen Logos sowie alle früheren zusätzlichen Widget-Reihen. Keine Fokusrahmen-Verschiebung und kein Abschneiden beim Scrollen. Skin-XML-Patch nur idempotent, gesichert, reversibel und kompatibel mit Space Blue.

### 3. P0-B: Cover und Cache stabilisieren

- Provider-Poster/-Cover für Filme und Serien primär verwenden; kein erzwungener TMDB-Helper für VOD.
- Unterbinde das Überschreiben eines gültigen last-good-Snapshots durch alte oder unvollständige Widget-Generationen. Unterscheide POSITIVE, PARTIAL und PLACEHOLDER samt Etag/Revision, Event-/Item-ID, Dateigültigkeit, Scope und TTL.
- Überprüfe reale Kodi-Directory-Item-Artwerte (poster/thumb/fanart), nicht nur Hintergrund-Publisher. Bei Kaltstart vorhandene sichere Cache-Einträge behalten, danach asynchron und ohne GUI-Blockade verfeinern.
- Teste zwei Neustarts, Skin-Reload, Fokuswechsel und temporär nicht erreichbaren Bildserver; erst nach tatsächlicher Darstellung PASS.

### 4. P0-C: EPG / Programmbilder

- EPG-Provider-ID, sichere Stream-Aliase und manuelle Zuweisungen konservativ matchen. Verfügbare Provider/XMLTV-Einträge im lokalen Cache konsistent zusammenführen, Startgruppe priorisieren, tägliche EPG-Aktualisierung und rechtzeitige Persistenz. Nie Programme bloß wegen ähnlichem Sendernamen vermischen.
- Begrenze häufige Datenbank-Polls bei EPG_DATA_MISSING / DB_BUDGET und schiebe HTTP/SQLite-Schwerarbeit aus dem Kodi-GUI-Thread.
- Programmbild End-to-End: EVENT -> verifizierte Quelle -> URL-Security -> Download/Decode -> Persisted Local File -> Lease -> aktive Skin-Property -> existierendes Control -> sichtbare Texture. Mini-/Groß-EPG und Live-Hero verwenden für dieselbe Sendung dieselbe gültige Bildreferenz.
- XMLTV-/Provider-Bild zuerst, TVMaze als Serien-Fallback, TMDB nur bei vorhandenem gültigem bereits importiertem Read-Token. Bestehenden Token **byteidentisch erhalten**, kein Reimport, Löschen, Überschreiben oder Logging. Ausdrückliche Opt-outs respektieren. Keine Host-Wildcard und keine falschen Bildzuordnungen.

### 5. P0-D: Kodi-DB und Kino-/Library-Widgets ohne Datenverlust

- Nur lesend Schema, sqlite_master, PRAGMA integrity_check, DB-Version und aufrufende Queries für MyVideos131.db untersuchen. Datenbank-Problem und benutzerspezifische Widget-Bindings getrennt analysieren.
- **DB weder löschen noch blind reparieren/migrieren**, keine frei erfundenen SQL-Views. Vor einer später nötigen gezielten Migration Backup, nachvollziehbare Ursache und explizite Freigabe.
- XCMate-Providerwidgets dürfen nicht von einer defekten Kodi-Videolibrary abhängen; vorhandene klassische Kodi-Widget-Reihen nicht entfernen.

### 6. Regression, Umsetzung, Veröffentlichung

- Nutze kumulativ main .78, erstelle Branch/PR für **0.1.29.79**. Unit-/Integrations-/CI-Tests für Native-Runtime-Consumer, fehlende Controls, Revisions-/Kaltstartcache, Poster, EPG-Matching, URL-Security, Texture-Zuordnung, kaputte Kodi-Views, alte Benutzerwidgets, Fokus/Navigation und Serien-/Film-/Live-Exit. CI PASS ist kein Android PASS.
- Paketprüfung: reproduzierbares plugin.video.xtreammate-0.1.29.79.zip, SHA256, ZIP-CRC, addon.xml-Version, Source-ZIP-Parität, kein Daten-/Tokenverlust.
- Nach grünen Tests PR für main bereitstellen und den Release-Kanalstand dokumentieren. Die ausdrückliche Freigabe, eine **ungeprüfte** Version sofort auf allen Kanälen zu veröffentlichen, galt in #385 ausschließlich für **.78**. Für .79 einen neuen konkreten Veröffentlichungsauftrag beachten: ohne diesen keine stillschweigende gleichzeitige Umstellung aller Kanäle. Wenn freigegeben, Source-Merge + Kataloge/MD5/ZIPs nachweisbar umsetzen.
- **Installer 0.5.26 ist eingefroren.** Keine Kodi-Neuinstallation, kein SkinShortcuts-Reset, kein Entfernen von Space Blue, keine Änderung von Favoriten, Portalzugängen, EPG-Mappings, Token und Kodi-Userdata.
- Abnahme an realer Android-Kodi-21.3-Box: Film-/Seriencover bleiben nach zwei Starts sichtbar; „Neu im Kino“ und alle anderen gespeicherten Reihen vorhanden; großer Hero und EPG mit passenden Bildern und Now/Next sichtbar; Navigation/Fokus/Exit stabil. Bis dahin je P0 ANDROID_FAIL oder ANDROID_NOT_TESTED, nie künstlich PASS.

## Rückmeldung von Codex

In #387 dokumentieren: Branch/PR, Änderungen pro P0, CI/Testergebnis, Android-Abnahmestand, gegebenenfalls Merge-Commit, ZIP/SHA256 und **tatsächlich aktualisierte** Repository-Kataloge; offene Fehler klar kennzeichnen. Privaten Gerätelog nur lokal für Reproduktion, niemals vollständig öffentlich committen.

**Ziel:** Vorhandene Daten und echte Bildreferenzen endlich zuverlässig sichtbar machen, statt die Startseite erneut umzubauen.
