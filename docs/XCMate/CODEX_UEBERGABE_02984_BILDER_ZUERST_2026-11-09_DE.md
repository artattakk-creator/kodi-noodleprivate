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
