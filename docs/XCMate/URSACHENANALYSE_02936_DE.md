# XCMate 0.1.29.36 – Ursachen, Umsetzung und Messgrenzen

Stand: 25.10.2026 (Europe/Berlin). Kumulativer Draft auf `main` **46b4f9f**; dessen Add-on-Quellstand .35 entspricht **9c558c7**. Während der Arbeit aktualisierte Planungsdokumente wurden vollständig berücksichtigt und in den Entwicklungsbranch übernommen. Insbesondere ist #159 gemäß neuer verbindlicher Roadmap Bestandteil dieses Kandidaten. Kein Merge des Kandidaten nach main, Release oder OTA.

## Nachweis und verbleibende Unsicherheit

.35 bleibt **15/15 funktional Android-PASS**. Die private Logforensik dokumentiert trotzdem Programmtiteltreffer nach 28,070 s, Scanende nach 67,538 s und einen 16,767-s-Startdispatch. Letzterer war als OTHER protokolliert; OpenFile war kein erster Videoframe. Die neue Implementierung reproduziert konkrete Kosten und einen möglichen Stop-Race auf dem Host. Sie beweist noch nicht, welchen Anteil jeder Pfad an diesen Android-Latenzen hatte.

| Bereich | Reproduzierbarer Quellcodebefund | Änderung in .36 |
| --- | --- | --- |
| #140/#127 | Nach dem einmaligen XML-Now-Durchlauf fragt Short-Enrichment jeden fehlenden Sender ab: zwei Varianten, je frischer und stale Cache; viele nicht vorhandene Dateien und wiederholte Verzeichnisvorbereitung. Die weiteren EPG_PARTIAL-Slices sind keine bewiesenen neuen Vollscans. | Ein begrenztes Inventar vorhandener Cache-Dateinamen pro Suchgeneration. Nur vorhandene Kandidaten öffnen. Nicht lesbares/unterstütztes Inventar bedeutet UNKNOWN und erhält den alten Cache-only-Pfad. Revision/Abbruch/Mapping und Sofortausgabe der Namen bleiben erhalten. |
| #120/#35 | `home_start` validiert im vollständigen Live-JSON, `_startup_playable` liest denselben Katalog erneut. | Einzelzeile aus aktiviertem lokalem Index; Metadaten an denselben Router weitergeben. Bei vorhandenen, aber fehlenden/gesperrten Indexdaten kein Bypass. Fehlender alter Index darf genau einmal den bestehenden lokalen Cache streamen/lesen. Keine Provider-Authentifizierung/Neusynchronisation. |
| #17/#35 | Navigator bereitet den gesamten Provider-Live-JSON auf; GuideSnapshot und Startup-Preload laden wieder das gesamte EPG-JSON, obwohl nur wenige Sender sichtbar sind. Die Renderer selbst nutzen bereits RAM. | Vorbereitete Sender-Metadaten aus SQLite. Noch nicht indizierte neu aktivierte Gruppen behalten den bisherigen lokalen Katalog. Guide-Worker liest höchstens 16 Sender, je ID höchstens 48 Ereignisse, read-only mit Zeitbudget; ältere Profile behalten Legacy-Fallback. Native Renderer, Controls, Zapping und GUI-Owner unverändert. |
| #75 | `_exiting` gehörte nur einer Python-Fensterinstanz. Eine zweite Instanz derselben Session konnte Phasen/Deadline überschreiben und Stop/Home erneut anmelden. Home-URL wurde auch bei bereits vorhandener Home-Ansicht explizit erneut angefordert. | Globale Session-Latch vor jeder erneuten Anmeldung; committed phase bleibt bestehen. Exakt passende Home-Ansicht ohne erneute Plugin-URL zeigen; fremde Portal-Home nicht verwechseln. Vor Navigation complete setzen; fremde Player/Modals weiterhin schützen. Der Android-Doppelroute liegt möglicherweise zusätzlich Kodi-/Skin-Verhalten zugrunde: S36-07 bleibt Pflicht. |
| #159 | Vorhandenes `genre` liegt im Payload; bisher ausschließlich Titel-SQL. | Additive abgeleitete Genre-Tabellen und indexgestützte Mitgliedschaft; konservative Aliase, Titel exakt vor Titelteiltreffer vor Genre. Keine JSON-Extraktion pro Suchzeile. Nachindizierung im bestehenden Hintergrunddienst, kein neuer Threadpool. |

## Tatsächlich gemessene Hostwerte

Reproduktion: `python tools/benchmark_xcmate_02936.py --output /tmp/xcmate36-messwerte.json --samples 5` aus einem Quellcheckout mit Git-Historie. Rohmesswerte, Plattform und alle Samples: [HOST_MESSWERTE_02936.json](HOST_MESSWERTE_02936.json).

Gleiche synthetische Daten, tatsächliche SQLite-/JSON-/Dateisystemoperationen, Kodi-Bindings durch strikte Modelle ersetzt. Keine Sleeps oder injizierten Wartezeiten. Fünf neue temporäre Profile je Variante; OS-Pagecache nicht geleert. Kein Kodi-/Android-Cold-Boot-Benchmark und kein P95. Große Provider-JSONs enthalten bewusst ungenutzte Zusatzmetadaten; Original-Nutzerdaten wurden nicht verwendet.

| Test / 2.764 Sender | .35 Hostmedian | .36 Hostmedian | Arbeit vorher → nachher |
| --- | --- | --- | --- |
| Ein belegter Short-Now-Titel am Katalogende: erster Treffer | 161,76 ms | 57,27 ms | 2.764 → 1 geprüfter Sendercache; 22.110 → 6 VFS-exists-Aufrufe; 184 → 12 Slices |
| Menüroute bis vorbereiteter Startsender-ListItem | 46,93 ms | 1,62 ms | 2 → 0 Vollkatalog-Reads, 23.130.240 → 0 gelesene Vollkatalog-Bytes |
| Nur Navigator-Katalogvorbereitung | 23,14 ms | 15,04 ms | 1 → 0 Vollkatalog-Reads; Aufbau derselben 2.764 Sender |
| Nur Guide-Hintergrunditeration für einen Sender | 12,45 ms | 1,13 ms | 1 → 0 Portal-JSON-Reads, 6.006.716 → 0 Portal-JSON-Bytes |

Genre-Query nach fertigem Index: **2,45 ms** bei 1.000 Titeln und **45,82 ms** bei 50.000 Titeln, jeweils Median fünf Abfragen. Vorher nur ein Titelmatch, danach 100 bzw. 5.000 belegte Genre-/Titeltreffer. Das ist ein Funktionsausbau, kein identischer Vorher-/Nachher-Treffersatz. Materialisierung auf dem Host 10,69/533,30 ms reine Rechen-/DB-Zeit in 8/391 Transaktionen; längste Transaktion 1,60/2,05 ms, maximal 128 Payloads. **Service-Scheduling, Hintergrundkonkurrenz und ARM32-Laufzeit nicht enthalten.**

**Android .36: alle Messwerte NOT_TESTED.** Engineering-Ziel: belegter Now-Titel unter 10 s und deutlich schneller als .35; keine Umrechnung des Hostfaktors auf das Gerät.

## Messmarker und Datenschutz

- `SEARCH_PERF`: INDEX_QUERY_DONE, NOW_LOCAL_MATCH, ENRICHMENT_STARTED, CACHE_BATCH_DONE, NO_PROGRESS_STOP, VISIBLE_FIRST_PROGRAMME, FINAL; vorhandene Phasen bleiben. Zufällige Generation/Owner und Zahlen; keine Query, Titel, Kanal-/Portal-ID oder Adressen. CACHE_BATCH_DONE wird aggregiert, nicht pro Sender geloggt. VISIBLE_FIRST_PROGRAMME bedeutet übergeben an die native sichtbare Ergebnisliste, keine physische Displaymessung.
- `LIVE_TIMING`: IR_MENU_CLICK (**Plugin-Menürouteneingang**, kein Roh-IR), ROUTE_ACCEPTED, START_SID_RESOLVED, PORTAL_REQUEST_BEGIN/END (**network=0**, lokale Metadatenauflösung; Kodi-interne Stream-HTTP-Zeiten sind nicht zugänglich), PLAY_INVOKED, PLAYER_STARTED, FIRST_VIDEO_DETECTED. Letzteres prüft passende unveränderliche Item-Identität, Video und gültigen Player-Time-Zugriff; **kein behaupteter Decoder-First-Frame**.
- REMOTE_ACTION_RECEIVED/LIVE_NAV_READY/INFO_WINDOW_VISIBLE/MINI_CHANNELS_VISIBLE messen Handler-/Render-Rückkehr, cold/warm getrennt. Physischer Tastendruck bis gezeichnete Oberfläche muss auf Android zusätzlich gestoppt/gefilmt werden. Kein künstliches Verstecken von Kodi-Decoderfehlern.
- PLAYER_STATE_UNAVAILABLE erscheint höchstens einmal je Messgeneration. Keine privaten Exceptiontexte. Session-Nonce wird nur intern für Item-Zuordnung verwendet und nicht geloggt. Bestehende LIVE_EXIT-Sessions bleiben nur als Digest sichtbar.

## Genre-Vertrag und additive Migration

Nur Film/Serie, nur belegtes Provider-`genre`; keine Ableitung aus Kategorie-ID, Jahr, Plot oder unbekannten Kategorienamen. Aliase Sci-Fi/sci fi/Science Fiction/Science-Fiction; u. a. Western, Thriller, Krimi/Crime, Komödie/Comedy, Action. Vollständige Tokens, deshalb kein Western-Match für „Westernized“. Unbekannte Genrebezeichnungen werden nicht geraten.

Mehrere erkannte Genres gelten mit AND. Restwörter müssen im Titel stehen: `Sci-Fi 2024` findet Genre Sci-Fi plus Titel mit 2024; ein ausschließliches `year=2024` reicht nicht. Titelmatches nach bestehender Token-Semantik bleiben erhalten und priorisiert; gleiche Portal/Art/SID nur einmal; aktive Gruppen gelten weiterhin.

Im bestehenden `library_v1.sqlite` entstehen ausschließlich `xcmate_genre_state` und `xcmate_genre_terms` samt eigenem Primärindex. **Keine Änderung bestehender Spalten, Views oder gespeicherter Originalzeilen.** Kein EPG-/Artwork-/Resume-Schema betroffen. Der Worker liest maximal 128 Payloads je Transaktion über einen wiederaufnehmbaren SID/CID-Keyset-Cursor. Schreibverbindung je Batch; Zeitbudget, Abbruch-Rollback, BUSY-Backoff 30 s. Fertige Indizes benötigen beim periodischen Check keinen Writer-Lock.

Neue Katalogrevision blendet alte Genre-Resultate sofort aus; nur ein vollständiger, zur gelesenen Katalogrevision passender Index darf Ergebnisse liefern. Teilindizes werden niemals als vollständig dargestellt. Bei Neustart denselben Checkpoint fortsetzen; bei neuer Quellrevision ausschließlich den abgeleiteten Genre-Teil dieser Quelle neu bilden. Alte Reader können die zusätzliche Tabellen ignorieren und ihren ursprünglichen Titelkatalog lesen. **Keine Downgrade-/Reset-Anweisung.**

Während Vorbereitung funktionieren Titelmatches weiter. Das vorhandene Statusfeld zeigt „Lokaler Index wird geladen …“; aktuelle Suche wird höchstens alle zwei Sekunden per Worker ergänzt, ohne neuen Live-Scan und ohne Fokusreset. Nach maximal 120 s endet automatisches Nachfragen mit vorhandener Retry-Meldung; neue Suche darf erneut prüfen. Auf Live-Tab keine falsche Meldung über ausgefallenen Live-Index. Abbruch/Back beendet das Nachfragen.

## Bewusst offen

#111: aktuelles main hat bereits selektiven Retry, Kandidaten desselben Datensatzes, Statusklassen und dauerhafte Rate-Limits. Kein TMDb-Neulookup. Ohne belegte konkrete Retry-/Netzwerkphase und sichere Werk-/Quellidentität wäre ein Austausch der Artwork-Queue oder neuer Fremdposter-Lookup unbegründet. **Neue Reparatur BLOCKED**, Android S36-11 NOT_TESTED; nächste konkrete Untersuchung **.37** mit anonymem Einzelbild-Status, bei größerer Artwork-Migration Workstream .43. Keine Übernahme des historischen Draft #157 und kein READY-/Cache-Purge.

Wizard #43 bleibt unabhängige Preview-/Folgearbeit mit Integrationsziel .37 auf dann freigegebenem main; keine Wizard-Änderung in .36. Der aktualisierte Versionszug .38 Mini/Rail, .39 Live-OSD, .40 VOD-OSD bleibt erhalten. EPG-Hub/Mapping, Storage/Downloads/Aufnahmen und globale Artwork-Migration unverändert außerhalb dieses Pakets.
