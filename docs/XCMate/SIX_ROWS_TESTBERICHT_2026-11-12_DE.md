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

- PASS: 16 neue Sechs-Reihen-Tests: reale Quellsemantik, Strict-Allowlist, kein fremder Token, falsche Quelle/Mehrdeutigkeit, Audio-Browse-Schutz, exakte Reihenfolge, private generierte IDs, idempotente Ergänzung, Kollisions-/Manipulationsschutz, sequenzielle Arbeit, Timeout ohne Parallelstart, Leer-/Fehlerzustände, unveränderte Last-good-Inhalte und sechs gemeinsame Header.
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

`test-builds/media-spinner/plugin.video.xtreammate-0.1.29.90.zip` – 4.676.278 Bytes, 859 Dateien, CRC und alle Quellbytes geprüft. SHA256: `ec7884a27b498afc943bed8405475993562a1f89c49e8b72a4af7791286cb2f8`.
