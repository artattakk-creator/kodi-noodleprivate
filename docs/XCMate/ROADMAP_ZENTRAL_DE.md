# XCMate – zentrale Roadmap und Freigabeplanung

**Stand: 21.10.2026.** Dies ist der fortzuführende Einstieg für XCMate von GS Media, Add-on-ID `plugin.video.xtreammate`. Historische Übergaben bleiben erhalten. Ihre früheren Versionsstände, gemeldeten Fehler und damaligen Testzähler sind als zeitgebundene Nachweise zu lesen. Aktuellen Stand künftig hier, in der [vollständigen Issue-Matrix](ISSUE_INTEGRATIONSMATRIX_DE.md) und im [maschinellen Bestand](ISSUE_BESTAND_20261021.json) pflegen; keine weitere konkurrierende „aktuelle“ Roadmap anlegen.

## Verifizierter Bestand und Arbeitsgrenzen

- Live-GitHub-Erhebung: **36 offene Issues**, alle **60 Issue-Kommentare**, **vier offene Draft-PRs** mit insgesamt **acht PR-Kommentaren** gelesen. Die Vorgabe „drei Drafts“ ist durch den inzwischen erstellten Hotfix #70 überholt. Die eigene Dokumentations-PR erhöht den PR-Zähler erst nach dieser Momentaufnahme; sie ist kein Produktkandidat.
- Produktiv: **0.1.29.6**, `main` **b6383de5ec1763b10a012f90c47f8f220725544c**. [PR #68](https://github.com/artattakk-creator/kodi-noodleprivate/pull/68) ist gemergt; [Publish 39646892896](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39646892896) war erfolgreich. Die reguläre Installation ist laut Nutzer erfolgreich; Hauptmenü, Live-TV, EPG, Filme und Serien sind unter 0.1.29.6 real erreichbar. Das ist ein **Smoke-PASS**, keine pauschale Vollabnahme.
- Primäre Abnahme: **Kodi 21.2 Omega, Python 3.11.7, Android 13, RK3528/DQ08 ARM32, Titan BINGIE MOD 2.2.3**. Frühere Angaben „Kodi 21.3“ in Alt-Issues korrigieren die tatsächliche Box nicht. **Kodi 21.3** bleibt zusätzlich zu prüfen; Estuary sowie 720p/1080p, Darstellung bei 4K und ein kleiner Stick gehören in die Erweiterungsprüfung.
- Zuerst enger **0.1.29.7-Hotfix**, dann **0.1.30.1-Theme-Integration**. Beide Pakete sind gebaut und automatisiert geprüft, Android jeweils **NOT_RUN**. Es fehlt kein weiterer Featurebau zum Beginnen des Hotfix-Gerätetests. Bei einem neuen reproduzierten Fehler gezielt korrigieren und neu prüfen, keine spekulative Neuentwicklung.
- **Keine Merges, Releases oder produktiven Repositoryupdates durch diesen Auftrag.** Keine Issue-Schließung ohne vorgelegten Bereinigungsvorschlag und Nutzerfreigabe. Die bestehende Veröffentlichungserlaubnis für 0.1.29.6 ist keine Freigabe der neuen Kandidaten.
- Vollbackup/0.1.29.6-ZIP als Rückfall behalten. Keine Kodi-Neuinstallation, kein Daten-/Cache-Reset, keine Portale oder Gruppen neu anlegen müssen. Portale, Favoriten, manuelle EPG-Zuordnung, Quellen, Startsender und Resume schützen. Private Logs und DB-Backups bleiben außerhalb von Git, Paketen und CI-Artefakten.
- Die 35 lokalen uncommitteten Zukunftsdateien (Raster/TMDB usw.) sind bytegleich gesichert und bleiben außerhalb der gelieferten Kandidaten. Sie sind **Entwürfe**, weder gelieferter Code noch nachgewiesene Funktionen. Vor ihrer späteren Nutzung separat Diff, Provenienz, Tests und Integration prüfen.

## Statussystem und vollständige Konsolidierung

Die [Integrationsmatrix](ISSUE_INTEGRATIONSMATRIX_DE.md) enthält für **jedes der 36 Issues** Nummer/Titel, einen Status, vorhandene Komponenten, konkreten Rest, Abhängigkeiten, Priorität, Zielversion und Teststand. Code-/Testbelege verweisen auf konkrete unveränderliche Referenzcommits. Die ursprünglichen Kommentare sind einzeln verlinkt; nur ihre URLs/Hashes/Metadaten werden im Bestand gespeichert.

| Kategorie | Anzahl | Bedeutung |
|---|---:|---|
| DONE / VERIFIED | 1 | #42: Code, Tests und ausdrücklicher Android-PASS vorhanden |
| IMPLEMENTED / DEVICE TEST OPEN | 20 | Implementierung vorhanden; vollständige Abnahme des gesamten Tickets fehlt |
| PARTIAL | 10 | Konkrete funktionale Restarbeiten neben vorhandenen Bausteinen |
| OPEN | 1 | #63: eigentlicher Downloadmanager fehlt |
| SUPERSEDED / DUPLICATE | 2 | #12 und #21 als historische Sammeltickets zur Überführung vorgeschlagen |
| FUTURE | 2 | #14 eigener Kodi-Skin und #65 spätere Drittintegration |

„Im Code“, „automatisiert geprüft“, „Android bestätigt“ und „veröffentlicht“ sind getrennte Aussagen. Ein geschlossener/integrierter PR beweist weder die Abnahme eines gesamten Issues noch fehlende Funktionen. Insbesondere wurden PRs **#45–#48** ohne eigenen Merge geschlossen; deren Funktionen sind im Integrationsstand **#49** und im heutigen Code enthalten. [Integrationsnachweis 0.1.29.2](INTEGRATIONSPRUEFUNG_RC_0292_DE.md), [Phase B](PHASE_B_PERSISTENZ_FAVORITEN_029_DE.md), [Phase C](PHASE_C_LIVE_GRUPPEN_SCROLL_029_DE.md), [Phase D](PHASE_D_UNIVERSAL_SETUP_029_DE.md).

## Laufende Draft-PRs

| PR | Head bei Erhebung | Umfang / aktueller Beleg | Nächster Schritt und Gate |
|---|---|---|---|
| [#70 – 0.1.29.7](https://github.com/artattakk-creator/kodi-noodleprivate/pull/70) | `ed6c1a41e033cdc553d2e55f44731716fab5c986` | Artwork-Diagnose/Backup/Recovery und gültiger home_start-Abschluss, **540/540**, [CI grün](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39663982049) | Zuerst manueller Android-Test, echte DB-Klasse/Integrität/Prefetch; bleibt Draft |
| [#50 – 0.1.30.1 / Space Premium](https://github.com/artattakk-creator/kodi-noodleprivate/pull/50) | `0840f7ccfb99bafb8ade5fb18c79e85b202660cc` | Aktuelles main und #70 integriert; 98 Originalbilder; **589/589**, [Core-CI grün](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39664007139), [Theme-Bau grün](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39663999822), [Katalogprüfung grün](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39664007125) | Erst Hotfix-/Exit-/Fensterregression, dann Stock/Theme/Installer/IR-Abnahme; bleibt Draft |
| [#51 – GS Media Repository 1.8.0](https://github.com/artattakk-creator/kodi-noodleprivate/pull/51) | `62db8fea465d6ab8bf0a691937228f508aa92b14` | Separates Repositoryprojekt: TMDb Helper, Pluto.TV, SHOUTcast, MP3 Streams; TV-Spielfilm-Mediathek ist kein Guide und kein brauchbarer Python-3-Import | Eigene Upstream-/Lizenz-/Paket-/Android-Abnahme. Hier keine neue Suite ausgeführt, keine Freigabe aus altem PR-Text ableiten |
| [#3 – Tastenreferenz](https://github.com/artattakk-creator/kodi-noodleprivate/pull/3) | `0162b24e696807525b665f579524e2870c875f3e` | Historischer TiviMate-Funktions-/Kurz-/Langdruckkatalog, **keine universelle Remoteimplementierung** | Als Referenz für #64 nutzen; keinen alten Branch als fertigen Remoteersatz mergen. Historische Tests nicht als aktuelle Android-Prüfung ausgeben |

Die frühere Aussage „#50 ist 49 Commits hinter main“ gilt für dessen alten Head. Der oben genannte integrierte Head enthält main und Hotfix. Vor jeder späteren Weiterarbeit Heads/Abstammung/CI erneut live prüfen.

## Phase A – aktuelle Fehler, Datenintegrität und Abnahme

**P0: [#69](https://github.com/artattakk-creator/kodi-noodleprivate/issues/69) und home_start.** Das neueste Log stammt tatsächlich von 0.1.29.6: **22** generische `MIGRATION_FAILED`-Warnungen; gültiger Startsender erzeugt einen Directory-Fehler und spielt danach. Nicht mit dem älteren 0.1.29.5-Log mit 37 Warnungen verwechseln.

- **Belegte Codeursache der Warnflut:** wiederholte mehrteilige Schemainitialisierung, generischer Exceptionhandler ohne SQLite-Klasse/Phase und ohne persistente Wiederholungsbremse. Die aktive Gerätedatenbank wurde nicht geliefert. Ein historischer `art_pending`-Backupbefund beweist daher **keinen aktuellen aktiven Indexschaden**.
- **0.1.29.7 vorhanden:** atomare DDL, Dateisperren und SQLite-Schreibbarriere, Fehlercodes/BUSY-/Storage-Backoff, konsistentes Onlinebackup einschließlich committed WAL, Prüfung auf Arbeitskopie. Automatischer REINDEX nur bei eindeutigem Index-only-Nachweis und unveränderten Tabellen; unklare/Tabellenschäden verlangen bestätigten Queue-Neuaufbau. Ohne vollständiges Backup keine Ersetzung. Bilder und andere Profildaten bleiben erhalten; nach Neuaufbau Hintergrundprefetch bis bewusster Retry pausiert.
- **Belegte home_start-Ursache:** gültige direkte Wiedergabe wurde mit `endOfDirectory(..., succeeded=False)` eingeleitet. Jetzt nur für verifizierte gültige Direktstarts erfolgreich abschließen. Kein Player-/Zapping-Neubau und kein zusätzlicher Provider-/Containeraufruf.
- **[#67](https://github.com/artattakk-creator/kodi-noodleprivate/issues/67):** Fensterstart 0.1.29.6 im realen Smoke-Test behoben; Owner-Pump/Modal-Wartepfad bewahren. EPG/Film/Serie 10× öffnen/Back/Fokus/Resume/Neustart vor Schließung.
- **[#40](https://github.com/artattakk-creator/kodi-noodleprivate/issues/40) / [#59](https://github.com/artattakk-creator/kodi-noodleprivate/issues/59):** Stop-/Ownership-/Fortschritts- und Back-Code existiert. Reale Live-Back-Hängermeldung und Film/Episode-Bild+Ton-Stop prüfen; 20 Back-Zyklen für #59. Bleibt Releasegate vor Themefreigabe, kein unbelegter Erfolg aus CI.
- **[#58](https://github.com/artattakk-creator/kodi-noodleprivate/issues/58):** 0.1.29.5-Dedup ist in 0.1.29.6/7 erhalten. ProSieben-15:06/15:07/15:36 real vergleichen, echte aufeinanderfolgende Folgen behalten. Keine EPG-Quelle automatisch deaktivieren.
- **[#32](https://github.com/artattakk-creator/kodi-noodleprivate/issues/32) / [#33](https://github.com/artattakk-creator/kodi-noodleprivate/issues/33):** neue SAX-/Streaming-/Katalogpfade sind im Code und getestet; zwei DE-Feeds waren real READY, Medien öffnen wieder. Vollständigen aktuellen Refresh bzw. großen aktiven Katalog und Fehlerpfade noch abnehmen; historische Exception ohne Traceback nicht nachträglich behaupten.
- **[#38](https://github.com/artattakk-creator/kodi-noodleprivate/issues/38):** 17-s-Kaltstart ist ein historischer subjektiver Einzelmesspunkt, kein aktueller Benchmark und keine bestätigte EPG-/DB-Ursache. BOOT-Phasen, Kodi-Host/Widget-/Rootzeiten mehrfach kalt/warm messen. 3–5s ist ein Optimierungsziel, keine Garantie.

Trakt/TMDb-Helper-401, externer xVAULT/InputStream-403 und fremde Repositorywarnungen bleiben außerhalb dieser XCMate-Fehlerursachen.

## Phase B – EPG und Programmzeitschrift, zentrales Ticket #57

Abhängigkeiten: [#13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13), [#21](https://github.com/artattakk-creator/kodi-noodleprivate/issues/21), [#34](https://github.com/artattakk-creator/kodi-noodleprivate/issues/34), [#58](https://github.com/artattakk-creator/kodi-noodleprivate/issues/58), [#60](https://github.com/artattakk-creator/kodi-noodleprivate/issues/60). **[#57](https://github.com/artattakk-creator/kodi-noodleprivate/issues/57) bleibt das einzige zentrale Umsetzungsticket.**

1. **Kurz-EPG während Live-TV:** lokale Jetzt/Danach-Daten, Logo, Start/Ende, Fortschritt/Restdauer; keine Netzwerkarbeit beim Tastendruck. Startsender, sichtbare Startgruppen-Sender und aktuelle Gruppe zuerst; fehlendes XMLTV nur über begrenzten asynchronen Short-EPG-Fallback. Keine 2700 Einzelaufrufe und kein Guide-Rebuild bei Back.
2. **Datenqualität zuerst:** konservatives Stream→EPG-Mapping, manuelle Overrides, Codec-/DACH-/Regionalvarianten und Mehrdeutigkeiten. Echte XMLTV-/Short-EPG-/Zeitfensterabdeckung getrennt messen. Letzte reale Quote **288/2764 =10,4%**; kein nachgewiesener neuer Wert. READY-Feed und WAITING-Anbieter unterscheiden; WAITING bedeutet nicht „nicht verfügbar“. Ein Gesamtfeed muss unter Umständen vollständig übertragen werden, obwohl nur aktive Programme gespeichert werden.
3. **Raster als eigene Oberfläche:** Hauptmenü EPG, feste linke Senderlogos/-namen, gemeinsame horizontale proportionale Zeitachse, Now-Linie, synchroner Vertikal-/Horizontalscroll und virtuelle sichtbare Fenster. 7–10 Tage nur bei wirklicher Feedreichweite; optional 14 erst bei Daten-/Retentionnachweis. Startgruppe/Favoriten, Jetzt/20:15/Heute Abend/Morgen/Kalender, D-Pad/OK/Back und unveränderter Fokus/Zeitausschnitt. Aktuell existiert ein Tageslisten-Guide, **noch kein gelieferter horizontaler Raster**.
4. **Kanonische Events und Detaildaten:** bestehende `guide_store` nichtdestruktiv erweitern, UTC und DST, event-/portal-/stream-/EPG-ID, Titel/Untertitel/Episode/Beschreibung, Genre/Bild/Quelle/Confidence/Freshness. XMLTV-Felder (u.a. episode, category, screenshot, credits/rating) nicht im Persistenzpfad verwerfen. Konsistente Backups bei Schemaänderungen. Ein Matcher/NowNext-Snapshot für beide Oberflächen, kleine schnelle Overlayqueries.
5. **Zwei Kontexte:** kurzes OK auf Sendung → Details/Jetzt ansehen/Erinnern/Merken; Senderzeile lang OK oder Kontexttaste 117 → EPG zuweisen/automatisch zurücksetzen/Quellenstatus/selektiv aktualisieren/Favorit/Guide-Sichtbarkeit/Diagnose. Nur tatsächlich verfügbare Aufnahme-/Archivaktionen anbieten. Vorhandenes Settings-Mapping wiederverwenden und bisherige Suche anderweitig erreichbar halten.
6. **Metadaten in eigener Stufe:** TMDB als gewünschte primäre Quelle für nichtkommerzielle Film-/Serienanreicherung, eigene lokal gespeicherte Zugangsdaten, offizielle Attribution/Logo und konservatives Titel/Jahr/Staffel/Folgenmatching. Episodenstill/Filmstill bzw. Poster, Backdrop, Beschreibung/Besetzung/Regie/Genre/Jahr/Rating/Trailer, Quellennachweis und neutraler Fallback. TMDB liefert keine linearen Sendezeiten. Optional TVmaze nach konkretem Lizenzreview; keine ungeprüfte TV-Spielfilm-Übernahme. Ein hypothetisches kommerzielles Modell blockiert diesen nichtkommerziellen Auftrag nicht.
7. **Suche/Filter/Highlights:** Titel/Besetzung, Genre/Gruppe/Favoriten/HD, Prime-Time/Heute-Abend, Merkliste und Erinnerungsverwaltung aus echten Metadaten, keine kopierte Redaktion. Netz/APIs bleiben optional; Guide muss ohne Enrichment benutzbar bleiben.
8. **Catch-up getrennt:** `tv_archive` und `tv_archive_duration` gehen derzeit in `library_index.FIELDS` verloren; vorhandene `xtream.catchup_url()` allein ist keine Integration. Xtream/M3U-Capabilities pro Stream persistent normalisieren, true/false/unknown sauber darstellen, Rücklaufzeichen/Archivtage/Filter, historischen EPG erhalten. Nur innerhalb echten Archivfensters „Aus Archiv ansehen“, UTC/DST/Providerformate und reale Wiedergabe prüfen. Ohne historische Daten ehrlich erklären. Serverarchiv benötigt keinen lokalen Recorder.

## Phase C – Fernbedienung und Live-TV

[#12](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12), [#17](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17), [#20](https://github.com/artattakk-creator/kodi-noodleprivate/issues/20), [#35](https://github.com/artattakk-creator/kodi-noodleprivate/issues/35), [#42](https://github.com/artattakk-creator/kodi-noodleprivate/issues/42), [#64](https://github.com/artattakk-creator/kodi-noodleprivate/issues/64).

Bestehender Freeze: OK Info → weiteres OK/Down Transport → Optionen; Links Sender → Links Gruppen; Up/Down zappen; Back kontextgerecht. Warme lokale Snapshots, vorbereitete Logos/EPG und Pre-play-Handshake erhalten. Native Sichtbarkeit **vor** Videoaufbau separat messen; ACK-Timeout ist kein Anzeigeerfolg. Kontinuierliches Scrollen ist real bestätigt, nicht neu entwickeln. Kleiner lokaler Gruppenzähler aus #37 ist eine isolierte Ergänzung.

**#64 ist weiterhin Teilimplementierung.** Der Nutzer hat die alte offene Rückfrage geklärt: verschiedene Boxen/Fernbedienungen, Rot/Grün/Gelb/Blau und weitere wirklich erkannte Tasten frei einem Aktionskatalog zuweisen. Taste wählen/lernen → Aktion → Konfliktvorschau → Speichern/Testen, nicht belegt/Reset, Box-/Remoteprofile und Import/Export, optional Kontext/Kurz-Langdruck bei unterscheidbarer Hardware. Kein blindes Autoerkennen einer Hersteller-ID. Sichere Standardnavigation und Countdown-Revert; Home/Volume/Systemtasten, fremde Add-ons und globale Kodi-Keymaps schützen. Nur implementierte Funktionen anbieten, keine freien Shellbefehle. PR #3 ist Referenz, kein fertiges neues Inputsystem. Zwei unterschiedliche Boxen/Remotes mit/ohne Farben praktisch testen.

## Phase D – Medien, Suche, Bilder und Widgets

[#24](https://github.com/artattakk-creator/kodi-noodleprivate/issues/24), [#25](https://github.com/artattakk-creator/kodi-noodleprivate/issues/25), [#26](https://github.com/artattakk-creator/kodi-noodleprivate/issues/26), [#40](https://github.com/artattakk-creator/kodi-noodleprivate/issues/40), [#41](https://github.com/artattakk-creator/kodi-noodleprivate/issues/41), [#44](https://github.com/artattakk-creator/kodi-noodleprivate/issues/44).

Vorhanden und vor weiterer Entwicklung abzunehmen: BINGIE-artige Landingpages/Neuheiten-Posterrails, Gruppen-/Posterwand, echte Backdrops/Details/Trailer, Staffel-/Folgenübersichten, Favoriten-/Weitersehen-Reihen, manuelles Gesehen/Ungesehen, Film-/Episodenresume und nächste ungesehene Folge. IDs portalgetrennt, lokale Metadaten-/Fortschrittspersistenz, Medienende entfernt keine Favoriten. Fotos/Beobachtungen zu bloßem Favoritentoggle sind keine Vollabnahme.

Dauerhafte Poster/Fanart mit Budget und Jobqueue sind vorhanden; die alte 64-Dateien-Eviction wurde entfernt. #69 blockiert die reale zuverlässige Bildnachladung. Nach Reparatur 130+ echte Bilder, nicht fokussierte Kacheln, Film↔Serie↔Back, Neustart/offline und Speichergrenzen prüfen. Keine aktive Bildsammlung still löschen. Komfortable selektive Bereinigung ist separater Rest.

Suche: LIVE-TV/FILME/SERIEN mit tatsächlichen lokalen Gesamtzahlen, Pagination und klaren unindiziert/indexiert/Fehler/Null-Zuständen. Große aktive Gruppen, Unicode und Portaltrennung real prüfen. Drei stabile BINGIE-Reihen: Startsendergruppe (Startsender zuerst, NowNext), neueste Filme, neueste Serien; Einrichtung über Skin-Widgets dokumentiert, keine automatische Änderung bestehender Widgets.

**Nicht vergessen:** Aus der [Serienfortschrittsspezifikation](SERIES_PROGRESS_SPEC_DE.md) bleiben **Auto-Next mit Opt-in/Countdown (Default aus)** und **Staffel-/Serienreset mit Bestätigung** offen; die Weitersehen-Rail ist inzwischen vorhanden. Manuelle nächste Folge ist kein automatischer Folgestart. Diese Restpunkte unter #24/#44 weiterführen, keine zweite Fortschrittsdatenbank anlegen.

## Phase E – Setup, Darstellung, Themes und Sprache

[#23](https://github.com/artattakk-creator/kodi-noodleprivate/issues/23), [#27](https://github.com/artattakk-creator/kodi-noodleprivate/issues/27), [#29](https://github.com/artattakk-creator/kodi-noodleprivate/issues/29), [#30](https://github.com/artattakk-creator/kodi-noodleprivate/issues/30), [#31](https://github.com/artattakk-creator/kodi-noodleprivate/issues/31), [#37](https://github.com/artattakk-creator/kodi-noodleprivate/issues/37), [#43](https://github.com/artattakk-creator/kodi-noodleprivate/issues/43).

- **Universeller Assistent vorhanden:** Xtream, M3U/M3U8 URL, privater Dateiimport über Kodi-VFS/USB/SMB, Stalker/MAG. Metadaten/Kategorien vor teurem Import, getrennte Checkboxen für Live/VOD/Serien und explizite Quellenwahl, selektiver Scan/Counts → Ergebnis → Save mit Readback; bis Save abbrechbar. Hintergrundbilder/EPG nach Save unabhängig vom Dialog. Private M3U-Arbeitskopie/Overrides, Titel/Gruppe/Logo/tvg-id/Enable/Sortierung/Dubletten/eigene Ergänzungen und Export; Originale nicht überschreiben. Fehlende Providerstaffeln ehrlich behandeln. Neue Provider-/Datei-/Speicherwege auf zweiter Box prüfen; bestehende Konten bleiben erhalten.
- **Space Premium nur in PR #50 fortsetzen:** generischer deklarativer Installer/Katalog, 98 Originalgrafiken, getrennte Theme-/Core-ZIPs. GitHub ist offizielle Onlinequelle, Drive bleibt Quellenarchiv. Manifest/Hash/Allowlist/ZIP-/Bild-/Größen-/Kompatibilitätsprüfung, explizites Opt-in, atomare Installation/Revision/Entfernen, Cachebudget und Stock-Fallback. Kein globaler Kodi-Skinwechsel. Zwölf Reservebilder implementieren keine Aufnahmen/Downloads.
- **Onlineverfügbarkeit:** unveröffentlichter Katalogpfad zeigt nach main; vor Freigabe dort ggf. 404. Für jetzigen Test lokales Theme-ZIP **innerhalb XCMates** importieren. Nach ausdrücklich freigegebenem Merge erst HTTP200 und exakte ZIP-/Katalogbytes auf Android nachweisen. Kein Ausweichen auf fremde Quellen und kein neues Theme erfinden.
- **Darstellung teilweise vorhanden:** Grundfarben, Fontstufen, getrennte Hintergrund-/Panel-/Icondeckkraft, Vorschau/Cancel/Reset. Vollständige getrennte Schrift-/Statusfarben, sehr große Layouts, Persistenz pro Theme und Leistungsprofile sowie native Darstellung nach #31 weiterentwickeln/prüfen. Icon im Core unabhängig vom gewählten Theme; dezenter Standardhintergrund braucht visuelle Abnahme. Lokaler Gruppenzähler #37 separat, keine Netzabfrage beim Scrollen.
- **Sprache:** eigene Deutsch/Englisch/Kodi-Auswahl ist vorhanden, English-Fallback bleibt. Eigenen Dialog am Gerät prüfen, deutsche Bestandsprofile erhalten, globale Kodi-Sprache und IPTV-Filter unverändert. **Optionale weitere Sprachpakete fehlen**: deklarativer separater Katalog/Installer/Loader mit SHA/Placeholder-/ID-/Pfadprüfung, Aktivieren/Entfernen, offline/Fallback. Dieser Rest darf nicht die schon vorhandene DE/EN-Auswahl wieder zur Neuentwicklung machen.

## Phase F – Scheduler, Aufnahme A bei Wiedergabe B, Downloads

**[#62](https://github.com/artattakk-creator/kodi-noodleprivate/issues/62):** Reminder sind vorhanden. Auto-Tune und geplanter Recorder fehlen als durchgängige Funktion. Zuerst persistente UTC-/DST-sichere Zeitplanung, Dedupe, Änderungen/Storno, Neustart/missed, Vor-/Nachlauf, Status/Konflikte; Auto-Tune pro Sendung explizit aktivieren, Vorwarnung/Cancel, fremde Wiedergabe sicher behandeln. Kein garantiertes Aufwecken ausgeschalteter/schlafender Boxen.

Android-Recorder als gesonderte Machbarkeit/Backend-Abnahme: `probe/start/stop/status/recover`, USB/HDD/SMB-Schreibprobe, freier Platz/Dateigrenzen/Fehler. Vorhandenes FFmpeg-CLI in der Linux-Cloud ist kein Android-Beleg; VLC liefert keine garantierte Kodi-CLI. Keinen heruntergeladenen FFmpeg-Binary-Start versprechen. Nur verifizierten kompatiblen Helper/API/Storeweg anbieten, oder korrekt unterstützten DRM-freien Direktstreamwriter prüfen; fehlendes Backend ehrlich melden.

**Verbindlicher Gerätetest:** A 10+ Minuten aufnehmen, B im einzigen Kodi-Player schauen und B→C zappen/Guide/Medien besuchen, ohne Recorder A zu stoppen; danach gespeicherte Datei mit Bild/Ton/Vollständigkeit prüfen. Getrennte Recorder-/Player-Sessions und explizite Aufnahme-Stopaktion. Provider unterstützt laut Nutzer parallele Streams; Backend und reale Datei sind dennoch offen.

**[#63](https://github.com/artattakk-creator/kodi-noodleprivate/issues/63) Downloads:** eigener persistenter Manager für Filme/Episoden/optionale Staffeln, wählbares dauerhaftes Ziel, Größen-/Kapazitäts-/VFS-Prüfung, begrenzte Queue, Bytes/Tempo, Pause/Cancel/Retry, HTTP-Range/ETag/Content-Range-Resume oder sauberer Neustart, eigene `.part`-Dateien/atomare Veröffentlichung, Kollisionen, Offline-Playback nach Kodi-Neustart. USB-Abzug, Speicher voll, SMB-Semantik testen. Datei löschen getrennt bestätigen. Nur unterstützte berechtigt speicherbare Quellen, keine DRM-Umgehung. Recorder ist keine notwendige Abhängigkeit für direkten HTTP-Dateidownload; gemeinsame Storage-Erkenntnisse wiederverwenden, keinen Monolithen bauen.

## Phase G – bewusst getrennt und historische Restanforderungen

- **[#19](https://github.com/artattakk-creator/kodi-noodleprivate/issues/19)**: technisches Audit vorhanden, tatsächliche Rechtekette/Notices und Drittasset-/Datenrechte offen. Begleitend vor neuer öffentlicher Distribution klären, weder pauschalen Closed-Source-Freibrief noch neue hypothetische kommerzielle Freigabeanforderung erfinden. Kein eigenmächtiger Lizenzwechsel oder V2-Neubau.
- **[#14](https://github.com/artattakk-creator/kodi-noodleprivate/issues/14)** eigener Kodi-Skin: Zukunftskonzept mit separater ID/Rückfallweg, nicht optionales XCMate-Theme. **[#65](https://github.com/artattakk-creator/kodi-noodleprivate/issues/65)** X-Wall/Drittoberflächen: Parkplatz, Add-on-ID noch ungeklärt, derzeit kein Implementierungsauftrag. **PR #51** bleibt separates Repositoryprojekt.
- **[#66](https://github.com/artattakk-creator/kodi-noodleprivate/issues/66)** bleibt **closed / not planned**: Multiview, Split-Screen, PiP und Mehrfach-Videodecoder sind ausdrücklich gestrichen, auch wenn ältere Referenzfotos/JSON diese nennen. Nur Aufnahme A + normale Wiedergabe B bleibt.
- Historische [Foto-/Settingsreferenz](TIVIMATE_SETTINGS_CONTRACT_2026-10-14.json) und [vierter Referenzbericht](TIVIMATE_SETTINGS_FOURTH_SERIES_2026-10-14_DE.md) bewahren zusätzliche Wünsche: Backup/Restore, Kindersicherung/PIN mit Zugriffsregeln/Throttling, Sleep-/Start-/Hostoptionen, Player-/Audio-/Subtitle-/AFR-/Decoderpräferenzen, Opt-in-Telemetrie sowie Über-/Lizenzinformationen. Das sind keine pauschal erledigten Funktionen und keine Freigabe, Kodi-globales Verhalten zu ändern. Vor späterer Umsetzung jeden noch gewünschten Punkt aus der Referenz in ein eigenes Ticket mit Istcode-/Testnachweis überführen; **Future / Version offen**, keine automatische Vollkopie von TiviMate-Fotowerten. Bestehende Teilfunktionen zunächst prüfen. Auto-Next/Staffelreset sind oben konkret #24/#44 zugeordnet.

## Bereits gelieferte Arbeit und tatsächlich fehlende Funktionen

**Keine neue Implementierung planen für:** kontinuierliches Scrollen #42 (voll bestätigt), den wieder funktionierenden Fensterstart #67 (Smoke-PASS), aktive Gruppen #37 (Teil-PASS), Bestandsaccount/Aktivwahl #43 (Teil-PASS), bestehende Live-Remote-State-Machine #17/#20, eigene DE/EN-Wahl, Streaming-/Gruppenimport, Medienrails/Favoriten/Resume und lokale Bilderhaltung. Bei den zuletzt genannten Funktionen fehlen überwiegend spezifische Android-Abnahmen; #69 ist ein tatsächlicher aktueller Fehlerpfad. Automatisierte Belege und engere reale PASS-Umfänge stehen in der Matrix.

**Funktional noch zu entwickeln:** horizontaler #57-Raster mit vollständiger Kontext-/Metadatenpersistenz, durchgängiges Catch-up mit Archivwiedergabe, TMDB-Anreicherung, universeller #64-Tasten-Aktionsdialog/Profile, #62 Auto-Tune/Scheduler und bewiesenes Android-Recorderbackend, #63 Downloadmanager, optionale #29-Sprachpakete, vollständige #31-Personalisierung, #37-Gruppenzähler sowie Auto-Next/Staffel-/Serienreset. #38 benötigt zunächst messbare Ursachenanalyse statt eines angenommenen neuen Features. #14/#65 bleiben bewusst zurückgestellt; Lizenz-/Provenienzreste #19 sind getrennte Prüfarbeit.

## Vorgeschlagene Versionen und Abhängigkeiten

| Version / Phase | Enger Lieferumfang | Freigabevoraussetzung / Abgrenzung |
|---|---|---|
| **0.1.29.7** | Nur Artwork-DB-/Diagnose/Recovery und gültiger Startsenderabschluss, vorhandener Freeze erhalten | Echte DB-/Prefetch-/home_start-Abnahme und Regressionen. Keine neue Raster-/TMDB-/Remote-/Recording-/Downloadfunktion |
| **0.1.30.1** | Bereits integrierter Core + optionaler generischer Themeinstaller + Space Premium 1.0.0 | #70-Basis, #40/#59/#67-Abnahme, Stock/Theme/Installer/Fokus/Offline/Persistenz. Eindeutige neue Version, altes 0.1.30-ZIP bleibt unverändert |
| **0.1.30.2** | Kleine gemessene UX-/Performance-Reste: #37 Gruppenzähler, #38 Kaltstart, #31 Darstellung, Auto-Next/Staffel-/Serienreset separat reviewbar | Jeweils eigene Änderungen/Tests; bei größerem Umfang aufteilen. Keine Scope-Erweiterung von #70/#50. Bestehende Sprache/Suche/Widgets erst abnehmen |
| **0.1.30.3** | Optionale Sprachpakete #29/#30, unabhängig von vorhandener DE/EN-Wahl | Eigener Installer-/Fallback-/Migrations- und Android-Test; blockiert nicht den EPG-Datenentwurf |
| **0.1.31** | #60 Coverage/Quellenqualität und #57 Raster-Grundfunktion mit bestehenden Remindern | #58/#59 bestanden, echte UTC-/DST-/7–10-Tage-Daten, große virtuelle Fenster, IR/Back, Stock/Theme. Kein Recorderzwang |
| **0.1.31.1 / .2** | Getrennte #57-Stufen: TMDB/Detail-/Filteranreicherung; danach Catch-up-Persistenz/Archiv | Attribution/sicheres Matching; echte Archiv-Capabilities/historischer EPG/Playback. Metadaten sind keine Sendezeiten |
| **0.1.32** | #64 universelle Tasten-/Box-/Remoteprofile | Alter Freeze unverändert, zwei verschiedene Geräte/Remotes, kein System-Key-Hijacking |
| **0.1.33** | #62 Reminder-Verwaltung + Opt-in Auto-Tune/Scheduler | Konflikt-/Neustart-/DST-/Cancel-Nachweis; Recorderbuttons nicht ohne Engine freischalten |
| **0.1.34** | #62 Android-Aufnahmebackend und Sofort-/EPG-Aufnahmen | Tatsächliche Datei, USB/HDD/SMB und A aufnehmen + B/C schauen; kein Multiview |
| **0.1.35** | #63 direkter VOD-/Episoden-/Staffeldownloadmanager | Storage-/Resume-/Cancel-/Offline-Abnahme. Kann technisch separat nach Storagekonzept entwickelt werden |
| **Future** | #14, #65 und bestätigte historische Restwünsche | Eigener späterer Auftrag, keine Version zugesagt; #19 begleitend statt vergessen |

Nummern nach 0.1.30.1 sind **Planungsvorschläge**, keine begonnenen Implementierungen oder Zeitversprechen. Abhängigkeiten bestimmen die Reihenfolge, nicht eine Pflicht, unverbundene Module in einen Branch zu packen. Für jede Stufe vom dann aktuellen bestätigten Stand ausgehen.

## Bestätigte Android-Teiltests und gezielt offene Abnahme

| Version / Nachweis | Real bestätigt | Nicht daraus ableiten |
|---|---|---|
| 0.1.25 / #13/#17 | Erste OK-Now/Next-Infoleiste | Kein funktionaler Langzeitguide/Timer |
| 0.1.27 / #17 | Live-TV-/Remoteverhalten wie 0.1.26 einwandfrei | Kein vollständiges 10×-Protokoll oder Medien-PASS |
| 0.1.28 / #38-Kommentare | Startsender Bild/Ton; OK-Info/zweite OK-Leiste; Links schnell mit EPG; Up/Down-Zapping | Keine bewiesene Ursache des intermittierenden Start-Hängers, kein Pre-play-Frame-Timing |
| 0.1.29.2 / #38/#43/#37/#42 | Kaltstart funktional ca.17s; Bestandsaccount/Aktivwahl; nur aktive Gruppen; kontinuierliches Scrollen | Keine komplette neue Assistenten-/Gruppenverwaltung-/Exit-Abnahme |
| 0.1.29.4 / #58/#60 | Zwei DE-Feeds READY, echte Programme, EPG/Medien zugänglich; reale Doppler und schwaches Matching belegt | Kein bereits sauberer Dedup/Back-/Setup-Save-PASS |
| 0.1.29.5 / #67 | Installation erfolgreich, **Fenster-Gerätetest FAIL**, Live-TV funktionierte | Kein stabiler Rückfallstand trotz grüner damaliger CI |
| 0.1.29.6 / #67 und Nutzerauftrag | Hauptmenü, EPG, Filme, Serien und Live-TV erreichbar / Smoke-PASS | Keine vollständige Back-/Stop-/Resume-/Theme-/DB-Abnahme |
| 0.1.29.7 / 0.1.30.1 | **NOT_RUN auf Android** | CI-/SDK-Erfolg ist keine Geräteausführung |

Nächster Testlauf: (1) 0.1.29.7 manuell installieren, Neustart; (2) Einstellungen→Speicher→Artwork-Jobdatenbank prüfen, Diagnosecode teilen, keine privaten DB/Backups hochladen; (3) Startsender wiederholen ohne Directoryfehler; (4) #67 10× und #59 20× plus #40 Bild/Ton/Resume/kein fremder Stop; (5) echte EPG-Dubletten/Cover/Persistenz prüfen; (6) erst danach 0.1.30.1 Core, Stock, lokales Theme, Back/Fokus/IR/offline prüfen. Neueinrichtungs-/Stalker-/USB-/SMB-Tests getrennt auf geeigneter zweiter Box. [Detaillierte Hotfix-/Theme-Anleitung](https://github.com/artattakk-creator/kodi-noodleprivate/blob/0840f7ccfb99bafb8ade5fb18c79e85b202660cc/docs/XCMate/STABILISIERUNG_0297_0301_20261021_DE.md).

## Vorhandene Pakete und automatisierte Nachweise

| Paket | Größe | SHA-256 |
|---|---:|---|
| [0.1.29.6 produktiv / Rückfall](https://github.com/artattakk-creator/kodi-noodleprivate/blob/b6383de5ec1763b10a012f90c47f8f220725544c/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.6.zip?raw=true) | 389853 Bytes | `f8188f156b8d43d741706813ba6e9946d7f2be66b035e4977dadb32464afe40e` |
| [0.1.29.7 Test-Core](https://github.com/artattakk-creator/kodi-noodleprivate/blob/ed6c1a41e033cdc553d2e55f44731716fab5c986/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.7.zip?raw=true) | 397264 Bytes | `4c45c573f2adaf977e37ae6d5ca5e5f67f1e797d9d976aa2ea28e20df2890128` |
| [0.1.30.1 Test-Core](https://github.com/artattakk-creator/kodi-noodleprivate/blob/0840f7ccfb99bafb8ade5fb18c79e85b202660cc/plugin.video.xtreammate/plugin.video.xtreammate-0.1.30.1.zip?raw=true) | 807271 Bytes | `72fe39e5ef9d01bb48d0b8c13e6961894587fdfc4e9a96125604ee35aa4f44fc` |
| [Space Premium 1.0.0](https://github.com/artattakk-creator/kodi-noodleprivate/blob/0840f7ccfb99bafb8ade5fb18c79e85b202660cc/themes/xcmate/space-premium/XCMate-Space-Premium-1.0.0.zip?raw=true) | 19772084 Bytes | `8fc7f312a65fa5ecdbe68d3487939a25d685de29717896a0a1113c8d41176ae2` |

**0.1.29.7:** 540/540 lokal und CI bestanden; 19 neue SQLite/WAL/Corruption/Lock/Recovery/UI-/Routingfälle. **0.1.30.1:** 589/589 lokal und CI bestanden; zusätzlich zwei Hotfix-/Lifecycle-Integrationsprüfungen. Keine Fehler/Skips in diesen finalen Läufen. Reproduzierbare ZIPs, CRC/Pfade/Quellbytes/Python-3.11-Syntax, 98 Originalbildhashes/Decoder und Kodi-21.2/21.3-SDK-Verträge geprüft. Das sind Host-/SDK-/Modelltests; keine native Androidausführung. CI-Paketprüfsummen entsprechen den bereitgestellten ZIPs; produktiver Publish-Schritt wurde übersprungen.

[Hotfix-Maschinenbericht](https://github.com/artattakk-creator/kodi-noodleprivate/blob/ed6c1a41e033cdc553d2e55f44731716fab5c986/docs/XCMate/TESTERGEBNISSE_0297_ARTWORK_START.json) · [Integrationsbericht](https://github.com/artattakk-creator/kodi-noodleprivate/blob/0840f7ccfb99bafb8ade5fb18c79e85b202660cc/docs/XCMate/TESTERGEBNISSE_0301_ARTWORK_START.json) · [Renderer-Matrix](https://github.com/artattakk-creator/kodi-noodleprivate/blob/0840f7ccfb99bafb8ade5fb18c79e85b202660cc/docs/XCMate/SPACE_PREMIUM_RENDERER_MATRIX_030.json).

Dieser Ergänzungsauftrag ändert ausschließlich Dokumentation. Keine neue Add-on-Version, kein neuer Paketbau, keine erneute Behauptung von Android-PASS und keine Änderung der Hotfix-/Theme-Quellstände. Dokumentationsprüfung: vollständige 36/36-Zuordnung, Kommentare/Pagination, Statuszählung, lokale und gepinnte Codelinks, vorhandene Belege, ausschließlich docs-Diff und Erhalt der historischen Inhalte. Ergebnis separat in der Dokumentations-PR festhalten.

## Pflege und nächste freigabefähige Schritte

1. **Jetzt:** 0.1.29.7-Gerätetest beginnen; bei Befund minimal im Hotfix nacharbeiten, mit passender Regression neu paketieren. Ohne Gerätebefund ist kein weiterer Produktcode in dieser Roadmap-Aufgabe erforderlich.
2. **Danach:** #40/#59/#67-Abnahme, 0.1.30.1/Space Premium testen. Erst konkrete Testergebnisse/Blocker dem Nutzer zur Releaseentscheidung vorlegen; keine automatische Veröffentlichung.
3. **Issue-Bereinigung:** #42 als erledigt, #12 und #21 nach vollständiger Restüberführung zur Schließung vorschlagen. Alle übrigen differenziert offen lassen. [Detaillierter Bereinigungsvorschlag](ISSUE_INTEGRATIONSMATRIX_DE.md#konsolidierung-zur-freigabe).
4. **Folgeentwicklung:** #60-Datenqualität/#57-Raster als nächstes eigenständiges Featurepaket spezifizieren, vorhandene lokale Entwürfe erst prüfen. Kleinere #37/#38/#31-Arbeiten separat reviewen. Keine gleichzeitige Vollimplementierung der Roadmap.
5. **Bei jedem neuen Beleg:** Datum, installierte Version, Commit/CI, Testumgebung, genauer PASS-Umfang und Rest ergänzen. Issue-Kommentar und Codebefund bei Widerspruch zeitlich trennen. Ticketzählung live neu erheben; Snapshot nicht als dauerhaften Zähler ausgeben.
6. **Beim Schließen eines Tickets:** erst nach Nutzerfreigabe Zusammenfassung mit Code-/Test-/Gerätebeleg und verbleibenden Nachfolgetickets veröffentlichen. Dauerhaft gepflegte Matrix/Roadmap im selben Änderungsumfang anpassen. Alte Dokumente/Logs bleiben historische Nachweise, private Daten niemals übernehmen.
