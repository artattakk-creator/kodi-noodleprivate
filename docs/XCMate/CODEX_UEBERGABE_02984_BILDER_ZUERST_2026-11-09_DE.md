# Codex-Übergabe – XCMate 0.1.29.84: BILDER ZUERST
Stand: 09.11.2026. **P0**. **Verbindlich:** nicht die Migration allein als Erfolg werten; der Nutzer sieht zurzeit **keine Senderlogos, keine Live-/EPG-Programmbilder auf BINGIE und keine Film-/Seriencover**.

**Maßgebliche GitHub-Vorgänge:** [#403 – sichtbare Bilder zuerst](https://github.com/artattakk-creator/kodi-noodleprivate/issues/403), [#401 – Speicher/Journal](https://github.com/artattakk-creator/kodi-noodleprivate/issues/401), [#398 – Android-Kapazität](https://github.com/artattakk-creator/kodi-noodleprivate/issues/398), [#395 – Startseitenmaster](https://github.com/artattakk-creator/kodi-noodleprivate/issues/395), [#106 – Migration intern/USB/SMB](https://github.com/artattakk-creator/kodi-noodleprivate/issues/106).

## 1. Kurzdiagnose / echte Logs

Nutzer-Logs: kodi.old(20261109-115006).log, kodi(20261109-115004).log. Beide sind privat, nicht committen: altes Log enthält eine SMB-URL mit Benutzername/Passwort. Nur redigierte Zeit-/Zeilenverweise.

| Beobachtung | Beweis aus altem Log |
|---|---|
| VOD/Serie-Daten vorhanden, Artwork fehlt | WIDGET47 Zeile 660 (Serie) / 667, 711 (VOD) / 795 (Serie): 24 Items, 0 local/matched images, 24 placeholders |
| Live-Widgets ohne anzeigbare Bilder | WIDGET47 Zeile 1019: NO_RENDERABLE_REFERENCE trotz 36 logo_sources/36 poster_sources; anderes Mal 88 selected |
| Startseite publiziert Referenz, nicht Bild | HOME82 121× CACHED_ITEMS_READY mit local_images=0, approved_refs=0, android_render_verified=false; HOME74 REFERENCE_PENDING |
| EPG-Quelle ist nicht grundsätzlich tot | IMAGE77 18× HTTP_RESPONSE IMAGE_DECODED; 95× LOCAL_CACHE RAM_ONLY; 62× MATCHED_EVENT_FACTS SOURCE_MISSING (Pipeline-Stufen/Events nicht 1:1) |
| Speicherdruck | ART_STORAGE82 13× FUSE 4,034,297,856 Byte total, rund 28 MiB nutzbar; ARTWORK 22× enroll DISK_FULL; Programme-DB 50× PROGRAMME_DB_IO und 5× DISK_FULL |
| Migrator nicht gestartet | ART_STORAGE83 12:20:44 und 12:37:24 JOURNAL_RESERVE_BLOCKED (USB, SMB); 12:42:51 TARGET_SAME_CAPACITY_POOL (Android Movies) |

Kodi-Systeminfo zugleich /storage/emulated/0 angeblich 256 GB total/144 GB frei; XCMate-Dateipfadstatvfs ca. 3,76 GiB total, nur 27 MiB available. Unterschied offen, niemals ignorieren, Quell-/Zielpool nicht frei erfinden. Nutzer hat leere Movies/XCMate/Artwork/{media,logos,fanart}/<Profil> gesehen. Nutzer bestätigt, dass Caber Toss Logdateien auf SMB speichern **kann**. Das ist ein Schreibnachweis für eine Anwendung/einen Pfad, nicht automatisch XCMate-Render-PASS.

## 2. Entscheidung: .84 hat Bildanzeige als harte Abnahme

**Priorität 1 – LIVE STARTBILD:** Startsender/aktuelle Sendung und Startgruppe. Sofort Senderlogos aus geprüften Quellen bzw. verifizierten lokalen Dateien anzeigen; erst Startsender + die ersten fünf Logos/EPG-Bilder, dann die restliche Gruppe. Bei passender verifizierter Sendungsquelle (TVMaze/TMDB/Provider-EPG) echtes Hero; falls keine Quelle, station logo oder eindeutiger neutraler Platzhalter. Keine Bildverwechslung zwischen Sendungen. Jetzt/Nachher und Sendernamen, Senderfortschritt und Fokusrahmen stabil lassen. Keine Generik-Icons, wenn echte Logos zulässig vorliegen; keine leeren Statusfelder.

**Priorität 2 – FILM UND SERIE:** Die vorhandenen 24 Items je Widget müssen Bildreferenzen erhalten. Providerposter/-fanart als Primärquelle; kein TMDB Helper als Pflicht. Bestehende katalogisierten Inhalte/Providerdaten nicht grundlos neu indexieren. Prüfe Sicherheitsfilter und Statuspfade genau: Quelle existiert, URI erlaubt, DNS-/HTTPS-Approval, Darstellung im Kodi ListItem, Texture-Cache, tatsächliche Anzeige. Unter reserviertem Speicher darf optionaler JSON-/SQLite-Artwork-Status nicht sämtliche bereits zulässigen *Anzeigereferenzen* verschwinden lassen.

**Priorität 3 – EPG/PROGRAMME:** IMAGE_DECODED bedeutet nicht Bild im GUI. RAM_ONLY ist gerade kein persistiertes Bild; nur sichere explizit zeitlich und eventgebundene HTTPS-Referenz nach existierenden Credential/URL/DNS/Redirect/SSRF-Prüfungen als display-only Fallback bereitstellen, wenn das Kodi-Backend sie real rendern kann. Sonst ehrlicher Platzhalter und Diagnosecode. Richtige Sendung/Staffel/Titel-Jahr-Abgleich; Attribution und Programmdetails unverändert.

**Priorität 4 – RECOVERY/STORAGE:** Wo Last-Good-Bild/erlaubte externe URI existiert, nicht durch neue fehlgeschlagene Metadatenwrites auf 0/Platzhalter zurückfallen. Programme- und Artwork-Worker bei DISK_FULL/SAFE_RESERVE_BLOCKED budgetieren/backoff, nicht auf jedem Widgetrefresh neue Persistenzversuche. Keine Datenbanklöschung, kein blindes Lock-Brechen, Reserve niemals pauschal abschalten. #401-Journal-Bootstrap nur wenn ohne Risiko möglich und für Bild-DoD erforderlich; ansonsten eigenständiger, nachgelagerter Fix. Aktuelle Artwork-Moduswahl und alle bestehenden Nutzerkonfigurationen beibehalten.

## 3. Verdächtige Codepunkte, systematisch testen

- src/plugin.video.xtreammate/resources/lib/widget_art44.py: prepare() schreibt referenzierte JSON-Metadaten via tempfile, art() findet bei Nicht-Dynamic sonst nur lokale Bilder. Bei knapper Reserve sind diese Schritte getrennt zu behandeln; keinerlei ungeprüfte URL-Adoption.
- artwork_config.py: persistent() anhand mode; Nutzerprofil nicht still von internal auf dynamic ändern.
- artwork_visible.py: bounded worker DNS/Public-IP-Approval, kurze TTL, Kodi URL-Optionen, retention; darf nicht zu SSRF/Credential-Bypass werden.
- widget_assets69.py: Quellenprüfung samt Login-Secrets, image lease, Window-Referenzen, recovery/caching; prüfen, warum widget refs/count=0 und warum valid provider source nicht zu Renderquelle wurde.
- media_art.py, widget_items45.py, widget_render47.py, widget_live47.py, widget_cache82.py, widget_skin*.py: tatsächlicher Übergang bis Kodi ListItem.setArt und Home/Timer, nicht nur Quelle/JSON.
- programme_pipeline77.py, programme_transport77.py, programme_art46.py, programme_image69.py, programme_widgets46.py, programme_assets47.py: EPG-Foto decodiert→RAM_ONLY→scoped display/texture; separate, überprüfte Fallback-Möglichkeit ohne persistente DB. Keine Bildfalscherkennung/Token-Leaks.
- home_lkg82.py, home_publication74.py/80.py: last-good bei unveränderter Source-Revision nicht auf REFERENCE_PENDING/PARTIAL zurückfallen.

## 4. Sichtbarkeits-Testplan

- Host: 27 MiB intern verfügbar, EPG image decoded but no persisted file, verified URL lease valid/expired, provider logo/source vorhanden aber blocked, 24 Filme + 24 Serien, view refresh, temporär Offline/Netzwerkabbruch, Crash/restart, 30-sec-DNS-Lease/redirect, wrong EPG event, Kodi texture fail, repeated missing DB writes, FUSE same pool.
- Hardware Box B (Kodi 21.3 ARM32/RK3528 BINGIE MOD): Startgruppe sichtbar; echte Senderlogos und Startsender; mindestens ein *wirklich verfügbares und zum EPG passendes* Live-Hero-/Programmbild, sowie sichtbares Film- und Serienposter. Dazu Screenshot+redigierte Kodi-Texture-Prüfung, Quellen-/Match-/Render-Zahlen, Fokus-/Zurück-/Neustart-Test. Ein Event ohne Bildquelle darf neutrale Fallbackgrafik zeigen, zählt **nicht** als Eventbild-PASS.
- In UI angeben: Quelle fehlt vs URL aus Sicherheitsgründen blockiert vs Bilddekodierung gelungen vs Dateireserve blockiert vs Bild wird aktuell geladen vs Kodi-Textur nachgewiesen. Keine falschen PASS-Zähler.
- Bestandsschutz: Box A, Provider-, TMDB-Zugänge, EPG-Quellen/Mapping, Kodi MyVideos131 DB, Favoriten, SkinShortcuts/Branding und Setup Wizard 0.5.26 unangetastet. Keine Raw-Logs/SMB-URI-Credentials öffentlich.

## 5. Liefervertrag

**Ein** .84-Branch: fix/xcmate-02984-artwork-visible-first, vom aktuellen main. Testen, CI, Changelog, ZIP+SHA256, PR gegen main, Bewertung PASS/FAIL/NOT_TESTED im Issue #403. Den alten exklusiven .84-Branchvorschlag aus #401 NICHT zusätzlich starten. **KEIN automatischer Merge, KEIN Release in regulär/Pilot/NeoDark3 ohne Freigabe.** Google Drive nicht entwickeln. WebDAV ist höchstens späteres P2 und kein Release-Blocker. Dokumentationslink zu diesem Auftrag im Issue #401/#395 hinterlegen.

## 6. Verbindliche zusätzliche Nutzerpräzisierung: REFERENCE-FIRST statt Archiv (09.11.2026, nachträglich)

**Konkrete Nutzeranforderung:** XCMate soll idealerweise **nur einen geprüften TMDB-/TVMaze-/Provider-Bildverweis** zusammen mit einer eindeutigen Sendungs-/Medienzuordnung speichern. Beim Anzeigen der Startseite werden **Startsender und höchstens die ersten fünf tatsächlich sichtbaren Sender-/Sendungsbilder priorisiert**. Alles Weitere folgt bedarfsgesteuert. Heruntergeladene Sendungsbilder werden nach Ende ihrer Sendung plus kurzer sinnvoller Übergangsfrist zu Löschkandidaten, falls sie nicht von der aktuellen/folgenden Ansicht referenziert werden. Film-/Serienbilder benötigen andere, LRU-basierte Regeln. **Keine wachsende dauerhafte Artwork-Bildsammlung.** Google Drive ist verworfen; WebDAV später, kein .84-Scope.

**Klarstellung zur missverstandenen Größe:** Der bisherige Read-only-Befund `total=4,034,297,856 B` bedeutet **3,76 GiB GESAMTKAPAZITÄT des von XCMate gemessenen FUSE-Speicherpools**, **keine** 3,76 GiB oder „37 GB“ nachgewiesene Artwork-Daten. Ein Gesamt-Arbeitsverzeichnis-Speicherinventar fehlt. Kodi-Anzeige `/storage/emulated/0` 256 GB/144 GB frei ist widersprüchlich, #398 weiter untersuchen. Niemals behaupten, 37 GB Bilder seien installiert.

### Codefakten, die geändert/abgegrenzt werden müssen

- `art_store.py` sagt wörtlich: **Completed files are never automatically evicted**, bei vollem Budget werden Jobs gestoppt. Dieser historische Archiv-Vertrag ist **nicht** die gewünschte generelle Cachepolitik. Bestehende persistierte Bilder *nicht* ohne geprüften Nutzerauftrag auf neue Löschregeln umstellen.
- `art_storage.py:budget()`: Grundeinstellung `media_art_budget_mb=0` = **unbegrenzt**. `reserve()` hat Standard 1024 MiB (min 32 MiB); nur diese Obergrenze und Reserve garantieren keine kleine Bilddateimenge oder LRU. `import_budget.RESERVE=32 MiB` ist getrennte SQLite/Metadatenreserve.
- `programme_art46.py:limit()`: EPGBild-Cache 32/64/128/256 MiB, Standard **64 MiB**, `MAX_DISK=64 MiB`; kontrollierte Weiterentwicklung zu TTL/LRU, keine Annahme dass aktuelle Dateien automatisch bei Sendungsende verschwinden.
- `artwork_config.py`: Modi `dynamic/internal/external`, `persistent()` ist in internal/external wahr. Fresh profiles werden ggf. dynamic, Bestandsprofile internal. **Bestehende Profile nicht still umstellen.** `artwork_visible.py` und `widget_art44.py` haben bereits temporäre, validierte Dynamikreferenzen; bei persistentem Profil laufen sie nicht automatisch. Kodi kann empfangene Bild-URLs in seinem **eigenen** Texture-Cache speichern; ein abgeschaltetes XCMate-Archiv beweist noch keinen dauerhaft begrenzten gesamten Bild-Footprint.

### Implementierungsauftrag innerhalb #403 („Bilder zuerst“)

1. **Reference-first für EPG:** Kleine Metadaten `channel/event_id + exact title/time/source + source ID + normalized safe image reference + verified match/URL lease + expiry` statt programmlanger Vollbildarchive. Quell-URLs nach Ablauf neu auflösen, wenn sie kurzlebig sind; Profile-/Event-Scoped, keine Xtream-Passwörter in GUI/Kodi-/XCMate-Logs oder ungeschützten Dateien.
2. **Kritische Anzeige ohne Archivpflicht:** Bei Speicherreserve-blockiertem Kodi-Profil erlaubte, tatsächlich renderbare, geprüfte öffentliche Bildreferenzen in die UI geben, **ohne unsichere URL-/SSRF-/Redirect-/Token-Checks zu umgehen**. Bei Kodi-Texture-Schreibfehler klar `TEXTURE_WRITE_BLOCKED` melden; nicht behaupten, dass reine URL-Referenzen automatisch auf der Box ein Bild erzeugen. Bei Private-/Credential-bearing Providerquellen nur sichere Transfer-/Proxy-Strategie, nie direkt dem Kodi-Renderer ausliefern.
3. **Vorabruf klein:** Zuerst das Senderlogo des Startsenders und aktuelle Programm/Hero; maximal 5 weitere sichtbare Sender mit aktuellen EPG-Infos und konkreten benötigten Bildern. Nachfassen nur bei Scrolling/Fokus/Sendungswechsel; keine Anfrage auf sämtliche 88 Sender samt EPG-Bildern beim Startup, erst recht keine gleichzeitigen Downloads aller Film-/Serienposter.
4. **Zwei Cache-Ebenen bewusst trennen:** (a) kleines, konfigurierbares XCMate-eigenes **temporäres** Artwork mit harter Größen-/Dateianzahlgrenze, LRU, Refcount/Pins, atomarem Status und sicherem Crash-Recovery; (b) Kodi Texture-Cache, der durch `ListItem.setArt`/URL-Laden eigenständig wächst, **separat messen** und nur über explizit unterstützte, geprüfte Kodi-APIs verwalten. Kodi-`Thumbnails`/Textures13.db **nicht** ungeprüft oder per Dateimanager löschen. Kein Gesamtlimit behaupten, wenn nur XCMate-Caches limitiert werden.
5. **Lebenszyklus:** Live-Event-Image nach `event.stop + Grace` zur Freigabe markieren, aber nur wenn keine laufende Anzeige, nächster Event, Last-Good/Referenz oder aktive Übertragung es nutzt; Senderlogos länger pinnen, bis sichere Quelle/kleines Budget bestätigt; VOD-/Serienposter bedarfsbezogen LRU/TTL mit späterem Abruf. Bei beschränktem Speicher müssen maximal zulässige Cachegrößen an **tatsächlich verfügbare** Bytes und Reserven angepasst werden; derzeit 27 MiB available darf **kein** 64/128-MiB-Vorabruf starten.
6. **Migration/Altlasten:** Vor jeder Bereinigung **read-only Inventur** (XCMate media_art_v1, tv_logos, programme_images46, Kodi Thumbnails/Textures13; außerdem andere Kodi-/Systemdateien nur Größen/Counts), Quell-/Ziel-/Mount-Klassen und bytes. **Alte Bestandsdateien nie ungefragt automatisch entfernen.** Separaten, verständlichen, doppelbestätigten Cleanup nach Backup/Abnahme anbieten; niemals Favoriten, Tokens, EPG-DB, Kodi-Datenbanken entfernen. Cache-Lifecycle nur für klar als **neu verwaltete temporäre** Dateien nach Opt-in/erfolgreicher Umstellung.
7. **Abnahme:** Gemessenes Startbild-Load (Startsender + erste 5), keine unkontrollierten Job-/Datei-Anwüchse nach 24h Test-EPG, Refresh über 3 aufeinanderfolgende Sendungen zeigt korrekte Bilder und released alte temporäre Dateien nach Grace; VOD/Serie 24 Widgets → sichtbares Poster bei Fokus; sichere Kodi-Render-Nachweise und reale XCMate/Kodi-Cache-Bytezahlen. „nur 37 GB artwork“ als falsche Behauptung in Diagnose verhindern.

**Priorisierung:** Sichtbare Bilder auf Box B innerhalb .84 (#403); bei notwendiger tiefer Cache-Lifecycle-Änderung Codex Scope und Risiken explizit als eigene inkrementelle Umsetzung auf demselben Branch oder nachgelagert melden. Keine Releasefreigabe, bevor echte Bilder sichtbar sind. Bestandschutz immer P0.

## 7. Präzise Pipeline-Vorgabe – EPG-Registrierung → Bildreferenz → Viewport-Fenster (09.11.2026)

**Nutzerdefinition:** Sobald eine Sendung im EPG registriert wird, soll XCMate die zugehörige TMDB-Bildreferenz ermitteln und bei Bestätigung zusammen mit der Sendung speichern. Wenn TMDB keine **sicher zuordenbare** Referenz liefert: TVMaze/weitere erlaubte Quellen und XMLTV (ggf. direkte Event-Icon-URL) prüfen. **Keine Bildbytes beim EPG-Import herunterladen!** Bilder erst beim Sichtbarwerden in BINGIE/EPG/Details laden. Initial auf Home **maximal die fünf sichtbaren Sendungsbilder** vorladen, bei horizontalem Fokuswechsel um einen Sender das nächste Bild nachladen; nicht 88 Sender auf einmal. Stream/EPG-Werte bleiben separat.

### Semantik beim EPG-Import

- XMLTV-/Provider-EPG auswerten und autoritativ speichern, anschließend **asynchron einen begrenzten Resolve-Auftrag** je eindeutigem Event/Medientitel anstoßen. Keinen API-Aufruf synchron im EPG-Parser und **kein blindes TMDB-Search für jede Zeile ohne Deduplizierung**: dieselbe Serie/Sendung auf verschiedenen Sendern oder an verschiedenen Tagen nur einmal suchen, soweit fachlich dieselbe Produktion/Episode; getrennte Episode benötigt korrekte Staffel-/Folgenzuordnung.
- **Quelle priorisieren nach belegter Genauigkeit, nicht bloß Anbieterreihenfolge:** Eine exakte XMLTV-Ereignisbildreferenz ist bereits präzise und darf genutzt werden, ohne eine ungenaue TMDB-Serienillustration vorzuziehen. Sonst TMDB (eigener Nutzer-Token, kein TMDB Helper), TVMaze-Fallback, XMLTV/Provider-Daten soweit passend. Ambiguous Match, Falschepisode oder fehlendes Bild ⇒ `NO_MATCH`/Quellfehler mit zeitlich begrenzter Negativ-Cache-TTL; nie falsches Titelbild.
- Gespeichert werden **nur kompakte Bildmetadaten**: stabile Event-/Werk-ID, Kanal-/Zeitfenster, eindeutig gematchter Titel/Staffel/Episode/Jahr, Provider-Typ, externe ID bzw. freigegebener Bildpfad/URL, Bildrolle (Logo/Still/Backdrop/Poster), Quellen-/Verifikationsstatus, `checked_at`, `expires_at` und Quellenrevision. Keine API-Antworten/Frames/Bilder in der EPG-DB, keine Passwörter in URL. URL-Lebensdauer getrennt von Sendungsdauer: wenn Bildlink abgelaufen oder verändert ist, bei Bedarf neu auflösen.
- Rate-Limit/429, intermittierende Netzwerkfehler und manuelle EPG-Neuzuordnung mit begrenzten Hintergrundjobs/Backoff behandeln. EPG-Text funktioniert auch bei Bildresolver-Offlinen; keine langen Ladeblockaden, kein vollständiges Neuscannen bei jedem Kodi-Start.

### Viewport-gesteuertes Nachladen

- Beim Öffnen: Fünf **sichtbare** Live-Programme (nicht sämtliche EPG-Einträge) bzw. Startsender zuerst; Logos schnell aus kleinem separaten Logo-Cache. Optional *ein* nächster Kandidat nur wenn tatsächlich Fokusbewegung/Scrollrichtung erkennbar, Gesamtzahl gleichzeitig gehaltener Bilder streng begrenzen.
- Bei Schritt nach rechts verschiebt sich sichtbares Fenster `[1..5] → [2..6]`: `6` anfordern, `2..5` weiterverwenden, `1` nicht löschen, solange sichtbar/als Last-Good gebunden; danach eligible für LRU. Bei Schritt nach links symmetrisch. Auf EPG-Detailseite nur betreffenden Event nachladen. Für VOD/Serie ebenfalls dynamisch anhand sichtbarer Widgetzeilen; nicht alle 24 Poster sofort herunterladen, wenn nur Teil sichtbar.
- Bilddownload in BOUNDED Worker statt UI-Thread, nur durch bestehenden sicheren HTTPS/SSRF/Redirect-Resolver (für Provider-URLs mit Zugangsdaten **keine direkten Kodi-Renderer-URLs**); Hash/Decode-Validierung vor Dateiverwendung. Zeilen-/Eventrevision prüfen, damit ein spät eintreffender Download nicht auf inzwischen neu fokussierte Sendung gemappt wird.
- Kodi speichert selbst intern gerenderte Texturen, auch bei URL-only XCMate. **Separaten Kodi-Texture-Cache lesen/messen**; nicht versprechen, dass ein XCMate-Cachelöschjob Kodi-Thumbnails ebenfalls freigibt. Kein direktes Löschen von Kodi Textures13.db/Thumbnails. Bei fehlendem internem Platz könnte auch Kodi-Rendering scheitern; fehlende UI-Bilder nicht allein als XCMate-Datenbankproblem behandeln.

### Cache-Grenzen und Aufräumsemantik

- Eigenen **temporären** XCMate-Cache mit hartem Byte-/Objektlimit und LRU priorisieren (keine unlimitierte `media_art_budget_mb=0`-Archiv-Neuproduktion). Sichere `pinned` Referenzen für aktuell sichtbare Bilder, Startsenderlogo, aktiv verwendetes Hero und laufende Bildtransfer; keine Datei löschen, solange UI/Worker sie verwenden oder ein gültiger Last-Good-Fallback darauf zeigt.
- Nach `event.end + grace` (z. B. konfigurierbare 10 Minuten) nur **Löschkandidat**; tatsächliche Entfernung durch Worker unter Lock/Refcount wenn unreferenziert, nicht bei jedes EPG-Event zwanghaft löschen (wiederholte Sendungen können dieselbe Bilddatei nutzen). Schon vor der TTL bei Cache-Limit älteste unpinned Dateien verdrängen. Senderlogo lange halten; VOD/Serie LRU.
- Bestehende **Archivdateien/alte Kodi-Texturen** nicht ohne separate Inventur/Einwilligung automatisch bereinigen; laufender Laufzeit-Cache nur für eindeutig neu angelegte temporäre Artefakte automatisch verwalten. Bei hoher /data-Auslastung in-memory + verifizierte URL-Referenzen bevorzugen, Renderbedingungen auf echter Box prüfen.

### Testbeispiel für Codex (unverfänglich, keine Providerdaten)

Gleiche Quelle und EPG-Events 1..8, sichtbar 1..5 ⇒ genau diese fünf Bild-IDs als initiale anstehende Requests (dedupliziert). Einmal rechts ⇒ nur neuer Auftrag für 6; zurück links ⇒ Bild 1 aus Cache/Last-Good, kein doppelter Download. Drei parallele Hintergrund-Updates (EPG-Revision, Focus, fehlende Quelle) dürfen kein altes Eventbild in neues Widget einbauen. Beim Sendungswechsel `t=end` und `t=end+grace` wird alter *unreferenzierter* Download entfernt, Pin verhindert vorzeitige Entfernung. Cache misst tatsächliche Bytes, niemals über Hardlimit; keine APK/Kodi-DB/EPG- oder bereits bestehenden Dateien löschen. Echte Bilder auf Box B nachweisen, `IMAGE_DECODED` reicht nicht.

**Wichtige Codekorrelation:** In `programme_art46.py` werden zwar source/URL im Ergebnis gespeichert, doch der aktuelle lokale Persistenzweg ruft `space(3 MiB)` **vor dem Download** und schreibt danach Bildbytes; somit nicht die gewünschte Reference-first-Architektur. `programme_sources57.py` bietet bereits TMDB/TVMaze-Resolver, `tmdb_epg60.py` Staffel-/Episoden-Matching, `programme_art46.py` verarbeitet vorhandene XMLTV-/Provider-Event-Icons. Die ref-first-Phase vom Bilddownload und vom lokal gespeicherten Dateibeleg sauber trennen.

## 8. Aktuelles reales TV-Foto zeigt zusätzlich eine BINGIE-Home-Layoutregression (09.11.2026)

**P0-Unterticket [#404](https://github.com/artattakk-creator/kodi-noodleprivate/issues/404)** ist **Abnahme-Blocker** für Hauptfix #403 und muss auf dem **selben** .84-Branch behandelt werden. Privates Benutzerfoto liegt im Chat vor, nicht ungefragt in ein öffentliches GitHub-Issue kopieren.

### Sichtbar beobachtet

- Hero ist nur ein schmaler oberer Streifen; großflächige schwarze leere Bildschirmmitte.
- XMLTV-Hero zeigt nur zentralen/unteren Teil eines Gesichts, Motiv wirkt unpassend beschnitten. Der Text rechts sagt explizit **„Bild: XMLTV“**, das ist **keine** Bestätigung, dass TMDB funktioniert.
- Rechte EPG-Anzeige `DE| DELUXE MUSIC HEVC / TOP 25`, Jetzt 14–16, Danach 16–17, Beschreibung/Plot drängen sich übereinander; Lesbarkeit und Safe-Area schlecht.
- Horizontale Senderleiste enthält **einige echte Logos**, u. a. Welt, Nitro, Discovery; Fokusmarker vorhanden. Daraus gerade **nicht** „alle Logos generell defekt“ ableiten.
- **Filmwidget fehlt** sichtbar vollständig; große Lücke zwischen Senderreihe und unterer Reihe.
- **Serienwidget erscheint am unteren Bildrand abgeschnitten**, nur Teile generischer runder Platzhalter zu sehen. Item- und Bildquelle separat prüfen.

### Konkrete Quellcode-Korrelation

- `widget_skin80.py` setzt `XCMate50.Hero` control 296751 auf Höhe `480`, `aspectratio=scale`, Home-Container `77777` `top=500,height=560`.
- `widget_skin81.py` setzt denselben Hero auf **`400`**, Gesamt-Herogruppe auf `420`, Text-/Bildpanel auf `400`, `XCMate50.LiveRow` auf `80`, Medienreihe `XCMate80.MediaRow` auf `268`, Poster-layout `140×208`, Scroll-Container `77777` `top=420,height=640`. Das ist ein **konkreter Regression-Verdacht**, nicht endgültig bewiesene Laufzeitursache ohne Prüfung der installierten XML-Dateien und `XCMate81.Contract`.
- `home_activation78.py`, `widget_skin78.py:runtime` und SkinShortcuts-Generator/Native-Home-Bindings prüfen, ob der Build tatsächlich aktiv ist; keine globale, ungesicherte Repatch-/Reset-Aktion.

### Verbindlicher Fix/Abnahme

- Hero auf dem realen 1920×1080-Gerät deutlich größer und breit, ungefähr 500–560 Kodi-Koordinaten als **Startentwurf**; mit vollständig sichtbaren, lesbaren Sendungsinformationen rechts. Original-Image-Aspekt/Szenenmotiv prüfen und Portrait/gering aufgelöste XMLTV-Vorlagen ohne verzerrte Gesichter oder aggressive Crops sinnvoll letterboxen/contain; nicht Qualitätsgewinn vortäuschen. Quelle und Titel korrekt attribuieren.
- **Senderlogos → Neueste Filme → Neueste Serien** ohne Hunderte Pixel Leerstelle. Sowohl real vorhandene Katalogdaten als auch tatsächlich gerenderte Poster und bedienbare horizontale Fokusnavigation. Die Reihen dürfen nicht aus dem Scrollcontainer verschwinden oder am Screen-Ende unerreichbar abgeschnitten sein. Evtl. notwendige vertikale Navigation ausdrücklich testen und sinnvoll auf den verfügbaren Platz abstimmen.
- Overlay-Bounds, Content-Padding, Long-Title, Now/Next, Progress, Quellencredit und Zeichensatz sauber prüfen. Keine Texte überlagern.
- Spaltenbreiten/Row- und Viewport-Koordinaten/Content-Quelle differenzieren; Daten da (24 VOD + 24 Series aus Logs) ≠ Reihe sichtbar ≠ Bild gerendert. Auf Box B Beleg durch Start-, Fokus-, Film- und Serien-Screenshot bei 1080p; wenn möglich 720p/4K Layout-Regressionschecks. Keine globalen Skin-/Kodi-DB-Resets. Box A bleibt unverändert.
- **Abnahme von .84 nur** wenn #403 **und** #404 für sichtbares Live/Filme/Serien + EPG-Hero erfolgreich verifiziert sind; #401 Speicher/Journalarbeit koordiniert ohne neue unnötige Blockade.

**Status:** Dokumentationsauftrag, **kein** implementierter Layoutfix und **keine** Veröffentlichung.

## 8. Neue verifizierte Logauswertung vom 09.11.2026 – TMDB funktioniert partiell, Widget-Render nicht

Zwei **weitere** private Kodi-Logs wurden ausgewertet: `kodi.old(20261109-132710).log` (31.604 Zeilen; Kodi-Protokollzeit 12:48:24–13:42:47) und `kodi(20261109-132711).log` (28.024 Zeilen; 13:43:14–14:26:44). Kodi 21.3, XCMate .83, Titan BINGIE MOD 2.2.3. **Keine Rohlogs/Geheimnisse ins GitHub übernehmen.** Die Zeit-/Zeilenreferenzen beziehen sich ausschließlich auf diese zwei hochgeladenen Originaldateien.

| Prüfung | Altes Log | Neues Log | Schluss |
|---|---:|---:|---|
| `ART81 TOKEN_PRESENT=YES` / `ENABLED=YES` | 396 / 396 | 293 / 293 | TMDB-EPG-Recherche ist **aktiv und Token verfügbar** bei diesen Versuchen; nicht mehr pauschal «TMDB deaktiviert» diagnostizieren |
| `ART81 HTTP_STATUS=OK` mit `status:200` | 103 | 90 | API antwortet. Kein Beweis für GUI-Bilddarstellung |
| `ART81 MATCH_CONFIRMED=EXACT` / `IMAGE_BACKDROP_READY=OK` | 8 / 8 | 6 / 6 | Mindestens einzelne **exakte** TMDB-Bildreferenzen werden gefunden |
| `ART81 MATCH_REJECTED=NO_MATCH` | 385 | 282 | Die meisten Versuche scheitern an genauer Zuordnung; welche Match-Regel je Event ist damit **noch nicht eindeutig bewiesen** |
| `IMAGE77 HTTP_RESPONSE=IMAGE_DECODED` | 104 | 121 | Zumindest einzelne Bilddownloads/-decodes funktionieren, nicht nur URL-Facts |
| `IMAGE77 LOCAL_CACHE=PERSISTED` | 54 | 152 | Neu im zweiten Lauf viel mehr persistierte Bildereignisse; nicht notwendigerweise TMDB-Bilder |
| `IMAGE77 LOCAL_CACHE=RAM_ONLY` | 236 | 119 | Viele Bildvorgänge bleiben temporär; nicht automatisch Renderer-tauglich |
| `IMAGE77 BINGIE_SKIN_PROPERTY=BOUND` / `RENDER_CONTROL=IMAGE_REQUESTED` | 0 / 0 | 29 / 29 | BINGIE-Property und Renderanforderung im zweiten Lauf erstmals sichtbar; **kein bestätigtes Texture-PASS** |
| `IMAGE77 BINGIE_SKIN_PROPERTY=SOURCE_MISSING` | 3 | 17 | Wechselnder Quellstatus mit sichtbaren Controls |
| `WIDGET47 live/ASSETS REFERENCES_READY` | 3 / 53 | 31 / 33 | Live-Bildreferenzen **intermittierend**, nach Restart deutlich häufiger |
| `WIDGET47 live/ASSETS NO_RENDERABLE_REFERENCE` | 49 / 53 | 2 / 33 | Live-Logoquellen können je nach Widget-Lauf wegfallen; schlüssiger Reload-/Life-Cycle-Test erforderlich |
| `WIDGET47 vod/series ASSETS NO_RENDERABLE_REFERENCE` | 38/38 und 38/38 | 28/28 und 29/29 | **Alle** ausgewerteten VOD- und Serien-Asset-Läufe haben 0 renderbare Bildreferenzen! |
| `HOME82 CACHED_ITEMS_READY` | 106 VOD +106 Serie | 84 VOD +84 Serie | **Ausnahmslos** `local_images=0, approved_refs=0, android_render_verified=false` in beiden Läufen |
| `ART_STORAGE82` verfügbar | min 24.506.368 B, max 132.124.672 B | 31.928.320–44.322.816 B | Messwerte variieren, `budget=0` (**unbegrenzt**), Reserve 80.685.957 B und im alten Lauf zeitweise 1.073.741.824 B; neue Freiplatzmessung bleibt unter 80,7 MB |
| `PROGRAMME_DB46` I/O | 93× PROGRAMME_DB_IO, 6× DISK_FULL | 46× PROGRAMME_DB_IO, 5× DISK_FULL | Lokaler Datenträger-/SQLite-Druck besteht fort |
| Kodi `MyVideos131.db`: fehlende movie/tvshow/musicvideo views | 12 Fehlzeilen | 12 Fehlzeilen | Weiterhin getrennte native Kodi-Schema-Anomalie, read-only prüfen, keinesfalls DB löschen |

Beispiel einer exakten TMDB-Sequenz im alten Log, Z. 11630–11639, 13:02:29–13:02:30: `TOKEN_PRESENT YES → ENABLED YES → OPT_OUT NO → TITLE_NORMALIZED OK → HTTP_REQUEST_SENT OK → HTTP_STATUS 200 → MATCH_CONFIRMED EXACT → IMAGE_BACKDROP_READY OK`. Im neuen Log erneut um 13:51:44 (Z. 6575–6590). **Verbindung und Trefferauswahl funktionieren im Einzelfall tatsächlich**; reiner Token-Reset und globales Abschalten der strikten Matching-Sicherheit wären falsche Reparaturen.

### Priorisierte neue .84-Testfälle

1. **TMDB Match-Transparenz:** nach `HTTP 200` exakten Ablehnungsgrund als festen Code melden (mehrdeutig, kein Jahr/Staffel/Genre, fehlende Bilddatei, Limit, Title-Mismatch). Kein raw Titel/token/URL in Diagnose. Bei bestätigtem `IMAGE_BACKDROP_READY` dieselbe durch Hash/ID gebundene Sendung bis `IMAGE77`/Widget/Skin verfolgen, auch nach EPG-Revision. Die Codes `MATCH_REJECTED NO_MATCH` und `IMAGE_BACKDROP_READY OK` gelten nicht als Renderbeweis.
2. **VOD/Serien eigenständiger P0:** In beiden neuen Logs *sämtliche* überprüften Asset-Durchläufe `NO_RENDERABLE_REFERENCE` und Home-Cache `0 refs/0 images`. Provider-Posterquelle → Credential-/URL-Policy → begrenzt geprüfter Art-URI → `ListItem.setArt` → Skin `thumb/poster/fanart` → Kodi Texture miss/hit → Screenshot getrennt diagnostizieren. Keine unzulässige Freigabe von Provider-URLs, keine TMDB-Helper-Abhängigkeit.
3. **Live BINGIE Focus/Refresh:** Im neuen Log 31/33 Live-ASSETS `REFERENCES_READY` und bis zu 48 lokale Bilder, aber BINGIE zeitweise SOURCE_MISSING und 29 `IMAGE_REQUESTED`. Vorhandene Valid-Referenzen beim Fokus-/Refresh-/Senderwechsel schützen; positive Visibility erst bei nachgewiesener GUI-Textur und Screenshot. Verschiedene Programmtitel/Fokus, Kodi-Widget-Reload und Dateimutation testen.
4. **Persistierung vs. Sichtbarkeit:** `LOCAL_CACHE=PERSISTED` (152) ist Bildspeicherschritt, kann trotzdem alter Event, EPG-Stelle oder ungenutzte Quelle sein. Gesondert messen, welche Bildquellen/IDs zur **gerade auf BINGIE angezeigten** Sendung gehören. `BINGIE_SKIN_PROPERTY BOUND` ist nicht Pixel-/Texture-PASS.
5. **Begrenzter dynamischer Cache:** sichtbare fünf Programme, nach rechts +1 genau neuer Fetch, LRU-/Grace-Lifecycle. Da `budget=0` weiterhin XCMate-Archiv unbegrenzt macht, vor Umstellung Sicherung/Inventur; keine unautorisierte Löschung historischer Bilder oder Kodi Textures13.db. Die Speichergröße 3,76 GiB ist FUSE-Pool, **nicht** gemessene Bilddaten.
6. **XMLTV-Qualität:** Nutzer berichtet gelegentliche, optisch eingeschränkte XMLTV-Programmbilder, aber bislang **kein Bild-Screenshot** in diesen beiden Log-Uploads. Nicht bereits Crop/Aspect/Pixelauflösung als Ursache behaupten. Nach visuellem Beleg gesondert bewerten.

**Kein zweiter .84-Branch**, kein automatischer Release, alle bisher gültigen Nicht-Lösch-/Datenschutzbedingungen gelten weiterhin. Die hochgeladenen Original-Logs gehören **nicht** in Issues oder ZIPs.
