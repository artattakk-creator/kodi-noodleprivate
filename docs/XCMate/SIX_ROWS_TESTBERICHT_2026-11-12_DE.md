# Sechs BINGIE-Reihen – Implementierung und Abnahme

Arbeitsstand auf dem vorhandenen Skin-Folge-Draft #438, abhängig von #437. Kein Merge, kein Release, keine Änderung eines Android-Geräts. Version bleibt 0.1.29.90; das Review-Paket ersetzt keinen veröffentlichten Updatekatalog.

## Quellen und Darstellung

Die private Sicherung wurde ausschließlich lesend untersucht; Rohkonfiguration und Zugangsdaten werden nicht eingecheckt. Die vorhandenen drei XCMate-Quellen bleiben unverändert. Die ergänzten Consumer stehen nach Serien und vor den unveränderten weiteren Benutzerreihen. Ihre IDs belegen keine gespeicherten BINGIE-Slots.

| Standardreihe | Tatsächliche Quelle | Nativer Consumer | Ziel |
| --- | --- | --- | --- |
| Filme | `widget_recent_vod` | vorhandener Container, im Referenzprofil 1520 | Videos |
| Serien | `widget_recent_series` | vorhanden, im Referenzprofil 1530 | Videos |
| Im Kino | optionaler TMDB-Helper, `now_playing/movie` | 297610 | Videos |
| Disney | gespeicherter Helper-Discover, Anbieter 337, Region DE, movie | 297620 | Videos |
| Diese Woche im Trend | gespeicherter Helper, `trending_week/tv` | 297630 | Videos |
| MP3s | vorhandener Audio-Browse-Pfad von `plugin.audio.m3sr2019` | 297640 | Music |

Disney bezeichnet die vorhandene Metadaten-/Verfügbarkeitsauswahl; daraus folgt keine Streamingberechtigung. Es gibt kein Bewertungsranking. Die Audioquelle wird nicht als VOD behandelt; automatisch ausführbare Play-/Shuffle-/Lösch-/Favoritenänderungsrouten sind als Widget-Datenquelle gesperrt. Ohne gespeicherten Audio-Widget-Pfad wird der tatsächlich vorhandene Music-Menüpfad übernommen. Seine Ordner öffnen im Musikfenster; echte Provider-Wiedergabe ist gesondert auf dem Gerät zu prüfen.

Der eigene XCMate-TMDB-Token wird weder gelesen noch weitergereicht. Fehlender/deaktivierter Helper, fehlende Quelle und mehrdeutige gespeicherte Quellen erhalten eigene Zustände; es wird kein Erfolg erfunden und keine willkürliche alternative Quelle gespeichert.

## Header, Laden, Navigation und Schutz

Alle sechs Reihen benutzen dieselbe gemessene Überschrift-/Original-BINGIE-Spinner-Komponente: 24×24, 85-ms-Frames, 12 Pixel rechts vom tatsächlichen Titel. Header bleiben auch ohne Einträge erhalten. Das neue private Reihen-Include unterstützt Poster, Thumb und Audio-Icon; feste vorhandene Film-/Seriengeometrie und Live-Hero bleiben erhalten.

Film-/Serienarbeit ist auf Profil/Provider/Reihe begrenzt. Die vier Zusatzquellen werden erst nach Freigabe der vorhandenen Live-/Film-/Serien-Ladereihenfolge zugelassen, nacheinander über Kodis native DirectoryProvider. Keine neuen Netzwerkthreads oder zusätzlichen Katalog-/SQLite-Scans. GUI-Polling liest nur RAM und native Labels. Kein erneuter Start bei Fokuswechsel oder unverändertem Inventar. Eine abgeschlossene Quelle behält Pfad und Last-good-Inhalte.

Maximal 60 Sekunden Ladeanzeige je Anfrage. Bei Timeout endet der Spinner. Falls Kodi den alten DirectoryProvider noch als aktiv meldet, wird die nächste Quelle nicht parallel gestartet. Kodi unterscheidet bei einem leeren nativen Container einen leeren Erfolg nicht zuverlässig von einem Quellfehler: deshalb explizit `EMPTY_OR_ERROR`, sichtbarer Prüfhinweis und kein behaupteter Quellen-PASS.

Die generierte eigene Serien-Abwärtsverbindung führt zu den gefüllten Zusatzreihen und danach zum bisherigen Benutzerwidget. Leere Quellen werden übersprungen. Die bisherigen Fremd-Widget-Pfade, Einstellungen, Namen, Reihenfolge, SkinShortcuts und globalen Reload-Hooks bleiben unverändert. Rückwärtsnavigation aus alten Fremdreihen behält deren ursprüngliche Verbindung zur Serienreihe. Geänderte eigene IDs/Includes oder eine mehrdeutige Home-Gruppe blockieren die Ergänzung, statt fremde Reihen zu überschreiben.

Definitionen werden ausschließlich über den vorhandenen gesicherten Skin-Transaktionsweg mit Vorschau/Bestätigung/Backup/Hash/Rollback angewendet. Der generierte Cache wird wie zuvor privat gesichert und atomar ersetzt; gespeicherte Shortcuts werden nicht geschrieben. Es wurde kein Skin auf einer Benutzerbox modifiziert.

## Prüfstand dieses Commits

- PASS: 18 neue Sechs-Reihen-Tests: reale Quellsemantik, Strict-Allowlist, kein fremder Token, falsche Quelle/Mehrdeutigkeit, Audio-Browse-Schutz, exakte Reihenfolge, private generierte IDs, idempotente Ergänzung, Kollisions-/Manipulationsschutz, sequenzielle Arbeit, Timeout ohne Parallelstart, Leer-/Fehlerzustände, unveränderte Last-good-Inhalte und sechs gemeinsame Header.
- PASS: 12 Spinner-/Geometrie-/Pending-/Originaldatei-/ZIP-Tests.
- PASS: 196 kombinierte Quellen-, clock50-, historische Scope- und Veröffentlichungs-Schutztests, 95,835 Sekunden. Bestehende Testmethoden/Skipbedingungen bleiben erhalten. Historische ZIPs werden gegen ihren exakten historischen Quellbaum geprüft, der neue ZIP gegen sämtliche aktuellen Quellen.
- Neuer vollständiger CI- und nativer Kodi-Lauf wird für diesen Stand gestartet; Ergebnis nachtragen. Frühere vollständige Host-CI ist grün, ersetzt den neuen Lauf nicht.
- Native Sechs-Reihen-Testquellen sind ausdrücklich synthetische lokale DirectoryProvider mit Postern und WAV. Sie prüfen tatsächliche Kodi-Container, Texturen, IR-Fokus, Spinner und Audio-Auflösung, nicht den externen TMDB-/MP3-Dienst.
- Früherer Zwei-Reihen-Stand: native echte Spinner-Pixel in 720p PASS; 1080p verlor beim ersten Kaltneustart den Live-Fokus. Der Observer wartet nun auf die tatsächliche bestehende Consumer-Aktivierungsbarriere, statt gleichzeitig mit einem legitimen Reload den Testfokus zu setzen. Der Fokus-Guard selbst bleibt bestehen; neues Ergebnis erforderlich.

## Android-Abnahme – jede Zeile zunächst NOT_TESTED

| Reihe | Überschrift | Spinner/Timeout | Einträge/Cover | IR/Fokus | Klickziel | Neustart |
| --- | --- | --- | --- | --- | --- | --- |
| Filme | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| Serien | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| Im Kino | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| Disney | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| Diese Woche im Trend | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| MP3s | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |

Auf Kodi21.3/BINGIE2.2.3 die bestehende Installation verwenden, keinen Reset: vorhandene Widgets/Positionen vorab dokumentieren; Review-Update und vorhandene gesicherte Skin-Vorschau prüfen. Live-Hero/Logo-Leiste zuerst, darunter die sechs Titel und weitere persönliche Reihen. Jede Quelle langsam/erfolgreich/leer/offline prüfen; Spinner endet bei Abschluss oder Timeout, kein künstlicher Fortschritt. Pro Reihe horizontal navigieren und klicken, bei MP3 echte Audioauflösung prüfen. Kodi neu starten und alle Quellen/Widgets/Positionen erneut prüfen. Keine echten Zugangsdaten/URLs in öffentliche Logs übernehmen.

## Weiterhin offene Masteraufgaben

EPG-Vergleich Home/Mini/Groß/Details, Galileo-Bildverlust und manuelle `SAVE_BLOCKED`-Reproduktion (#433), SQLITE_BUSY/Reserve (#430/#161), referenzgesicherte Rolling-GC (#108), nativer Player-Stop/ACK (#174) sowie vollständige Android-Abnahme sind nicht durch diese Reihenänderung behoben. Keine Datenbanken, WALs, Bilder, Wiederaufnahme-Journale, Backups oder Upgrade-Skripte gelöscht. Keine unbelegte Sammel-PASS-Meldung.

## Aktuelles Review-Paket

`test-builds/media-spinner/plugin.video.xtreammate-0.1.29.90.zip` – 4.676.831 Bytes, 859 Dateien, CRC und alle Quellbytes geprüft. SHA256: `91f39a626b3742d76d2f02234e123a71bfbdfeb46926be661db0b6c3e2f87c47`.

## Nachprüfung mit echten gespeicherten Pfaden und nativen Pixeln

Der Produktions-Discovery wurde zusätzlich mit einer privaten, nur temporär angelegten Arbeitskopie der tatsächlichen beiden Konfigurationsdateien ausgeführt. Zunächst FAIL für die drei Helper-Quellen: deren reale Reload-Variable heißt `TMDbHelper.Widgets.Reload`. Der Validator akzeptiert nun ausschließlich diese zusätzliche exakte, deklarierte Home-Eigenschaft. Alle vier Zusatzquellen werden danach eindeutig erkannt: PASS für Discovery, ausdrücklich keine Behauptung eines erfolgreichen API-/Audiostream-Aufrufs. Vorhandene Reload-Signale werden read-only übernommen; XCMate pulst den gemeinsamen Hook nicht und verändert keine gespeicherte URL. Eine zusätzliche Regression schützt die echte Macro-Variante.

Nativer Lauf 43249630477 fand in beiden Auflösungen eine reale Layoutregression: Serien hatte 24 Einträge, aber 0 passende Coverpixel, weil vier noch ungefüllte Zusatzreihen jeweils 244 Pixel Höhe beanspruchten und die letzte gefüllte Reihe aus dem Viewport schoben. Diese fehlgeschlagenen Prüfungen bleiben dokumentiert. Die Zusatzreihen zeigen jetzt einen kompakten 26-Pixel-Header bei Wartet/Leer/Fehler. Der volle native Coverbereich wird vor Beginn der konkreten Anfrage freigegeben und bei vorhandenen Einträgen beibehalten. Die Freigabe hängt ausdrücklich nicht an `NumItems`, damit kein neuer Cold-Load-Deadlock entsteht. Alle Header/Spinner verwenden weiterhin dieselbe Komponente. Neue native Prüfung erforderlich; kein Pixel-PASS aus einem XML-Test ableiten.

## Weitere native und vollständige Regressionen

Nach der kompakten Header-Korrektur waren die eigentlichen Live-/Film-/Serien-Pixel in beiden Auflösungen wieder vorhanden. Lauf 43251229556 fand zwei Folgeprobleme: Bei 1080p waren alle vier synthetischen Zusatzquellen bereits gefüllt, aber die Fernbedienung blieb vor der Kinoreihe stehen. Dynamische Navigation wird deshalb nun als regulärer Kodi-Builtin `SetFocus($INFO[…])` übergeben; ein bloßes dynamisches Label ist kein gültiges numerisches Navigationsziel. Die ursprünglichen Fremdreihen-Verbindungen bleiben erhalten. Bei 720p wurde eine reale rotierende Textur im vergrößerten Screenshot als 26×27 statt 24×24 gemessen. Die Prüfung misst jetzt direkt die unvergrößerten nativen Pixel mit der tatsächlichen Auflösung (24 logische Pixel und höchstens ein Raster-Randpixel); die produktive Textur bleibt 24×24. Der Fehlerguard für fehlende Animation/Fokus bleibt bestehen.

Ein lokaler vollständiger Zwischenlauf führte 3.843 Tests aus (894,264 s), davon sieben Fehler durch einen überlebenden Test-Dummy `epg_status` ohne `update/changed`. Die zwei neu manuell angelegten verschachtelten Fixture-Instanzen hatten ihre `addCleanup`-Rücknahmen nicht ausgeführt. Sie führen jetzt auch `doCleanups()` aus. Es wurde keine produktive EPG-Funktion verändert oder ein Test übersprungen; vollständigen Wiederholungslauf abwarten. 11 Brandingtests sowie alle 17 PO-Kataloge sind PASS.
