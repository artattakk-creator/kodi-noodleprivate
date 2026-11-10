# Android Box B – neue Kodi-Loganalyse für Folgeauftrag XCMate 0.1.29.86

**Stand:** 10.11.2026 · **Priorität:** P0 · **Ausgangsbasis auf dem Gerät:** XCMate 0.1.29.85; Kodi 21.3 Omega ARM32, RK3528, Titan BINGIE MOD 2.2.3; Setup 0.5.26, GS Media Pilot 1.9.12.  
**Evidenz:** zwei vom Nutzer am 10.11.2026 hochgeladene originale, **hier nicht in GitHub hinterlegte** Kodi-Logs: `kodi.old(20261110-134322).log` (07:55:28–08:24:11; 18.982 Zeilen) und `kodi(20261110-134323).log` (11:23:40–14:41:26; 42.177 Zeilen). Dateinamen sind nur die Herkunftsangabe, **keine Online-Quellen**. Die Zeitstempel sind Kodi-Gerätezeiten; ihre Synchronisierung mit externer Uhr ist hier nicht verifiziert. Beide Logbereiche sind zeitlich getrennt, verschiedene Neustarts.  
**Verknüpfung:** [P0 #409](https://github.com/artattakk-creator/kodi-noodleprivate/issues/409), [Entwicklungs-PR #410](https://github.com/artattakk-creator/kodi-noodleprivate/pull/410), [Codex-Folgeauftrag .86](CODEX_FOLGEAUFTRAG_02986_ANDROID85_LIVE_HERO_WIDGETS_BILDSUCHE_2026-11-10_DE.md), #401 Speichermount und #406 EPG/Artwork. **Noch kein .86-Android-PASS**.

## 1. Quantifizierte Evidenz – pro Datei, keine Quell- oder Nutzerkennungen

| Status / Ereignis | Ältere Sitzung 07:55–08:24 | Neuere Sitzung 11:23–14:41 | Bedeutung / Grenze |
|---|---:|---:|---|
| `EPG_CACHE_UNAVAILABLE` | 366 | 537 | 83 bzw. 86 **unterschiedliche pseudonymisierte Kanalreferenzen**; nicht 903 unterschiedliche reale Sender |
| `EPG_DATA_MISSING` | 301 | 1.485 | nur 10 bzw. 14 pseudonymisierte Kanalreferenzen: starke **Wiederholrate** |
| `EPG_DB_BUDGET` | 187 | 263 | wiederkehrendes Datenbank-/Zeitbudgetproblem |
| `EPG_READ_TIMEOUT` | 135 | 252 | EPG-Leseoperationen überschreiten Zeitbudget |
| `NO_SOURCE_FACTS` | 2.778 | 6.693 | 150 bzw. 342 pseudonymisierte Ereignis-Hashes; Meldung entsteht an mehreren Stufen pro Ereignis, **keine 9.471 verschiedenen Sendungen** |
| `RESERVE_BLOCKED` | 45 | 349 | Speicherreserve blockiert Image-/Metadatenpersistenz wiederholt |
| `RAM_ONLY` | 240 | 577 | Zwischenablage ohne sichere dauerhafte Archivkopie; Logereignisse nicht einzelne Bilddateien |
| `PROGRAMME_CACHE_BUDGET` | 61 | 192 | Artwork-/Metadaten-Cache wiederholt limitiert |
| `EXCEPTION: Index out of range` | 18 | 165 | **neu vorrangiger P0-Navigations-/GUI-/Servicefehler**, ohne Python-Stack im Kodi-Log |
| `IMAGE_DECODED` | 76 | 162 | einzelne Dekodierungen funktionieren; damit kein pauschaler TMDB-/Netzwerk-/Decoder-Ausfall |
| `NATIVE_HOME_EMPTY` | 8 | 8 | Home-Widget zu Sitzungsbeginn wiederholt leer |
| `widget_live_start_group`-Routeraufrufe | 41 | 23 | Kodi/Widget-Routen werden mehrfach erneut aufgerufen; **nicht** alle automatisch als Endlosschleife beweisen |

**Wichtige Interpretationsregel:** Ereigniszähler umfassen wiederholte Versuche, mehrere Logstufen und Meldungen derselben Sendung. Keine Roh-URLs, Zugangsdaten, IPv4-/IPv6-Adressen oder Portal-IDs in diese öffentliche Dokumentation übertragen.

## 2. P0-F – Neu: wiederholte Kodi-Indexfehler, Directory-Ausfälle, Python-Abbruch

**Zeitlicher Befund:**
- Älteres Log: 18-mal `error <general>: EXCEPTION: Index out of range` von 07:57 bis 08:21.
- Neueres Log: **165-mal**, konzentriert zwischen **14:23:30 und 14:41:22**; unmittelbar davor ab ca. **14:23:04**: `CPythonInvoker(... plugin.video.xtreammate/default.py): script didn't stop in 5 seconds - let's kill it`, `[XCMate][BOOT] DISPATCH_FAILED duration_ms=7186.4 error=OTHER`, `GetDirectory - Error getting plugin://plugin.video.xtreammate/...` (insgesamt sieben `GetDirectory`-Fehler), außerdem `CGUIMediaWindow::GetDirectory ... failed`.
- Der erste beobachtete Abbruch fällt auf einen **`media_detail`-/Home-Navigationspfad**, gefolgt von weiteren fehlgeschlagenen Menü-/Widget-Routen. Ein konkreter Python-Callstack für `Index out of range` fehlt. **Zeitliche Nähe ist keine beweisende Zuordnung der Ursache.**

**Verbindlicher Arbeitsauftrag an Codex:**
1. Im `.86`-Branch **alle Python-GUI-Indexzugriffe** in `series_manager85`, `programme_window46`, `home_runtime77`, `home_schedule75`, Skin-Renderer sowie Navigator/Player-Routen gegen Listenlänge, ungültigen Fokus, `-1`, abgehängte Controls, asynchrone Refresh-Generation und geschlossene Dialoge absichern. Zusätzlich prüfen, ob nativer Kodi-C++-Logtext `EXCEPTION: Index out of range` von Kodi-Kontroll-API statt Python erzeugt wird. **Nicht** ohne Beleg behaupten, dass `series_manager85` Verursacher ist.
2. Error-Instrumentierung nur mit **bereinigten** Informationen: Route, Kontroll-ID, Listenlänge, ausgewählter Index, Window-ID, Thread-/Generationsmarker, vor/nach Refresh, dazu echter Python-Traceback/exception-type sofern Python-Ursache. Keine Token/URLs/Benutzertitel im öffentlichen Log.
3. **Python-Invoker darf nicht nach 5s gewaltsam sterben:** langes `media_detail`/`xcmate_home` über asynchrone, abbrechbare Arbeit in Service/Worker aufteilen. In `default.py` nur sichere, zeitlich begrenzte Kodi-Directory-Navigation. Timeout und sichere Rückgabe ohne Window-/ListItem-Rennen; Abbruch darf keine noch laufenden GUI-Callbacks hinterlassen.
4. Regression auf echtem Kodi und Android: 100× Home→Live→Detail→Zurück→Filme→Serien→Detail→Zurück, wechselnder Senderfokus/Listenreload bei gleichzeitigem EPG-/Bild-Import; `Index out of range=0`, `DISPATCH_FAILED=0`, `GetDirectory=0`, 5s-Kill=0. Alle Nutzer-Fokuspositionen erhalten, keine Skin-Profilrücksetzung.

## 3. P0-A – Senderliste steht früh, aber Home verweilt 2–8 Minuten im Wartestatus

- Älterer Neustart: **88 Sender aus `HOME62 PAGE` um 07:55:50**, `HOME75 START_GROUP_KNOWN` um 07:55:58, `LIVE_HOME_READY` erst **08:03:42** mit `elapsed_ms=463372` (ca. 7:43 Minuten).
- Neuer Neustart: **88 Sender um 11:24:14**, `START_GROUP_KNOWN` um 11:24:20, `LIVE_HOME_READY` **11:26:48** mit `elapsed_ms=147811` (ca. 2:28 Minuten).
- **Kodipfad `WIDGET_FAST_DONE`:** 98 bzw. 75 Aufrufe; Median **14,70 s** / **13,20 s**, Maximum **98,52 s** / **97,05 s**. Der Modulname `FAST` garantiert offensichtlich keinen zeitkurzen Kodi-Directory-Call. Die Mehrheit dieser Aufrufe ist nicht nur initialer Start; getrennte Router-Lebenszyklen vergleichen.
- `HOME62 PAGE` tritt 62 bzw. 192 Mal auf; vorhandene Gruppendaten wiederholt angefordert. `NATIVE_HOME_EMPTY` je 8 Mal. Prüfung von `HOME62`/ `live_items62`/ `widget_home50` und `home_schedule75` muss die frühe **vollständige, logo-fähige** 88er-Rail von EPG- und Cover-Anreicherung strikt trennen.
- Aus `LIVE_HOME_READY`, `SKIN_CONTROL_ACTIVE` oder `IMAGE_REQUESTED` darf **nicht** auf physisch gerenderte Bildpixel geschlossen werden: `android_render_verified=false` in den HOME82-Statusbelegen.

**Zusätzlicher Testauftrag:** die beiden realen 2:28-/7:43-Startlinien als feste **Regressions-Fixtures** in `.86` aufnehmen: beim Home-Warmstart 88 Sender und gespeicherte Logos innerhalb der im Masterauftrag festgelegten Zeit auf echter Box sichtbar, kein Anwarten des EPG/Herobildes; keine 13–98s-Directory-Runtime im stationären Betrieb.

## 4. P0-B/C – Daten liegen teilweise vor, Darstellung/Persistenz bleibt instabil

**Positiver Gegenbeweis zu „alles kaputt“:** Auf beiden Neustarts 24 Film- und 24 Serien-Items; z. B. neuer Lauf nach wenigen Sekunden `HOME82 CACHED_ITEMS_READY kind=vod count=24 local_images=24` sowie `series count=24 local_images=21`. `IMAGE_DECODED` 76/162. Einzelne Art- und lokale Medienreferenzen funktionieren. Daten werden aber **unverhältnismäßig oft erneut als READY angekündigt**: `CACHED_ITEMS_READY` 101×/688×, und für dieselben 24 Medien im Hintergrund wiederholt vorbereitet.

**Problem:** `RESERVE_BLOCKED` 45/349 und `RAM_ONLY` 240/577 belegen, dass Bild-URL-/Texture-Referenzen oft nicht archiviert werden. Die beiden neuen Logs enthalten **keinen verifizierten `ART_STORAGE82`-`statvfs`-/Mount-Nachweis** für ein wirklich anderes ausreichend großes Zielvolume. Frühere getrennte Analyse belegt knappen FUSE-Speicher, aber **neue Messung nötig**. Kein Herabsetzen der Speicherreserve als stiller Fix.

**Codex .86 muss**:
1. Quell-/Event-/Bildänderungen getrennt als Revisionen führen; bereits zulässigen TMDB-Backdrop nicht durch leere XMLTV-Miniatur ersetzen. Große breite TMDB-Heros > hochwertiges fremdes echtes Szenenbild > separat ermitteltes offizielles Poster > Senderlogo; **niemals gewöhnliches Cover/Thumb/Icon groß im Hero**.
2. Atomaren Bild-/Bankwechsel testen, einschließlich RAM-only-Fallback ohne Schwarz-/Fokuswechsel. `SOURCE_CHANGED` (13/4 Ereignisse) und ablaufende Belege sind für Revalidierung zu berücksichtigen, nicht automatisch Grund zum Nullsetzen.
3. Logger `HOME82 READY` nur bei **relevanter semantischer Änderung** und tatsächlich sichtbarer/nativ bestätigter Generation; P50/P95 Neuerstellungsmessungen und Diagnose, warum `CACHED_ITEMS_READY` in einem drei Stunden langen Lauf **688-mal** loggt. Nicht jede Meldung als vollständigen Kodi-Refresh behaupten.
4. Bestehende Nutzerreihen „Frisch im Kino“/„Diese Woche aktuell“ unter Live-Hero beibehalten; EPG-Fehler dürfen VOD-/Serien-Widgets nicht leeren. Diese UI-Verlustbeobachtung ist **vom Nutzer**, kein direkter visueller Beweis im Log.
5. Getrennt belegte Freigabe von Android-/FUSE-/SMB-Speicherpfaden inklusive Schreib-/Lese-/Restore-Test und Ownership. Kein ungefragtes externes Netzlaufwerk.

## 5. P0-D – EPG-/Bildidentität und immer offene freie Suche

- Besonders `EPG_DATA_MISSING` nur **14 unterschiedliche pseudonymisierte Kanäle** trotz **1.485** Wiederholungen im neuen Log; das deutet auf häufige Re-Abfragen desselben nicht verfügbaren Zustands. `EPG_CACHE_UNAVAILABLE` betrifft dagegen bis zu 86 verschiedene Kanalreferenzen. `EPG_DB_BUDGET` und `EPG_READ_TIMEOUT` treten gleichzeitig auf.
- `NO_SOURCE_FACTS` wird bei `LOCAL_EVENT/MATCH/SOURCE` einer Sendung mehrfach geloggt. Nach Ursachenprüfung (EPG-Reader-Budget, Quellenrevisionen, DB-/WAL-/Lockstatus, Mapping-ID/Aliaße) **eine negative Retry-/TTL-Strategie pro echter Event-/Source-Revision**, kein 100facher Export und keine Erzeugung falscher Sendungsfakten.
- Userfälle **„Charmed – Zauberhafte Hexen“ und „Monk“**, sowie Film-Suche, weiter **P0 offen**, aber **aus den beiden Dateien keine eindeutige live gegen konkret diese Titel gerichtete Such-/HTTP-Anfrage nachgewiesen**. Daher bitte eigene redigierte Suchdialog-Logs mit Query-Variante, Quelltyp und `SOURCE_DISABLED`, `NO_RESULTS`, `NETWORK_ERROR`, `NO_SOURCE_FACTS`, `REVISION_CHANGED` erzeugen, ohne Suchbegriffe privater Werke öffentlich zu loggen. `series_requests85` benötigt einen robusten unabhängigen manuellen Recherchepfad auch ohne bestätigtes EPG-Event.
- Keine pauschale Cache-/EPG-DB-Bereinigung und kein erzwungener vollständiger XMLTV-Neuimport. Gültige alte EPG-Snapshots halten; Senderlogos und andere Widgets strikt unabhängig vom EPG bereitstellen.

## 6. P1/Nebenbefunde (nicht als P0-Ursache fehlklassifizieren)

- `repository.slyguy 0.0.9` und `script.module.slyguy 0.87.6` werden bei beiden Starts registriert; im älteren Log meldet der Shared Service **Started**. Damit liegt **kein Beweis für einen bleibenden SlyGuy-Installationsdefekt** vor. Der gemeldete kurze Installer-Stopp muss nur bei erneuter reproduzierter Fehlermeldung separat verfolgt werden (#407).
- BINGIE: `Could not load timers file ... Timers.xml` je einmal beim Start und `unsupported control type 7`/EGL-Hinweise; zurzeit keine Kausalität zu XCMate-Live-Latenz bewiesen. Optional Skin-Verträglichkeit/fehlende Datei gegen unverändertes BINGIE-Original prüfen.
- xVAULT: wiederholte `unable to read value of setting provider.*.check`; betrifft einen anderen Add-on-Einstellungsbereich, nicht automatisch XCMate-EPG.
- Kodi `CCurlFile` meldet einmal je Start eine ungültige kombinierte URL (Lokaldienst-Discovery). Separat auf veraltete Zeroconf-/Bonjour-Ankündigungen prüfen; keine Verbindung zum TMDB-Lookup beweisen.
- `ListItem.setInfo()` deprecated-Warnungen häufig; später sicher auf `InfoTagVideo` aktualisieren, aber nicht als unmittelbaren Grund für minutenlange Senderliste unterstellen.

## 7. Verbindliche .86-Akzeptanz und Releasegrenze

**Muss noch vor Review-/Merge-Freigabe aus PR #410 anhand neuer Tests und Gerät nachgewiesen werden:**
- Keine `Index out of range`-Flut, kein `CPythonInvoker`-Kill, keine XCMate-`GetDirectory`-Fehler bei Stressnavigation; freier manueller Film-/TV-Auswahldialog jederzeit nutzbar, unterbrechbar und dauerhaft korrekt speichernd.
- 88er-Live-Rail inklusive lokal bekannter Senderlogos in ≤2 s Warmstart bzw. ≤5 s Kaltstart **nach sichtbarem Home** auf der echten Testbox (oder ehrlich dokumentierte Abweichungen und Root Cause); EPG-/Artwork-Warmup parallel.
- EPG-Cache-Fehlzustände pro Kanal/Quelle begrenzen; bereits gültige Daten bleiben auf Cache-/DB-Timeout vorhanden. Kein log-storm mit denselben 10/14 Fehlkanälen.
- Keine schwarzen Hero-Zwischenbilder, kein XMLTV-Miniatur-Cover als Hero, kein Verlust alter Film-/Serienreihen.
- Speicherreserve bleibt geschützt, Zielmount wirklich verifiziert; keine unkontrollierte Speicher-/Datenlöschung; Box A, Installer und bestehende User-Profile unverändert.
- Neue `*.86`-Host-/Kodi-/Android-Gates getrennt dokumentieren. Der vorhandene PR #410 ist **Draft**; bestehende .85-Installation bleibt unverändert. **Ohne separate ausdrückliche Nutzerfreigabe kein Merge und keine Veröffentlichung.**

**Datenschutz:** Die beiden Logdateien wurden **nur lokal analytisch ausgewertet**; weder hier noch in den verlinkten GitHub-Issues sollen Rohlogs/Portalzugänge, Geräte-IP, Tokens oder private Medienadressen hochgeladen werden. Der Bericht enthält ausschließlich redigierte Zählwerte, Codes, Zeitfenster und interne Codenamen.
