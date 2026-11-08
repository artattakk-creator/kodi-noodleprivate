# XCMate 0.1.29.81 – Umsetzung und Prüfbericht

Stand: 08.11.2026, Europe/Berlin. Master #392, historische Befunde #389.
Basis: `9f5e5da705dc7be4044171debd273927998a4f27` / main .80.
Branch: `fix/xcmate-02981-artwork-stability`. Kein Merge, kein Release.

## Beleggrenzen

Die verbindliche Übergabe und die anonymisierte .80-Loganalyse wurden vollständig gelesen, einschließlich #392 sowie #389 mit Kommentaren. Die .80-Sitzung 16:38:36–17:06:50 wird von den überlappenden .79-Logs getrennt. Private Rohlogs und Gerätefotos wurden in diesem Lauf nicht erneut beschafft oder veröffentlicht. Die dokumentierte tatsächliche Filmwiedergabe aus .80 bleibt eine positive Android-Referenz. Sämtliche neuen Android-Gates sind **ANDROID_NOT_TESTED**. Synthetische API-Antworten und Linux-Kodi ersetzen weder den privaten TMDB-Zugang noch RK3528/GLES/Mali-Tests.

## Ursachen, Änderung und Grenzen

| Bereich | Nachweisbarer Codepfad / Korrektur | Regression / Restrisiko |
| --- | --- | --- |
| P0-A/B: Poster und Logos | Kurzlebige DNS-/URL-Leases und Kodi-Texture-Receipts waren keine dauerhafte Zusage lokaler Pixel. `render_cache81.py` übernimmt vollständig dekodierte PNG/JPEG-Dateien mit SHA256, Größen-/Dateistempel und atomarem Receipt in den bereits vorhandenen Bildcache. Profil, Zugang, Medienart, SID, Rolle und Quelle sind getrennt. Der bestehende Providerworker verarbeitet begrenzte Portionen, mit Backoff und vorhandener Speicherreserve. | 88 Logos sowie je 24 Filme/Serien über drei Zeitzyklen; Kaltlesen, Korruption, Kontowechsel und Rollen getrennt. Eine neue URL derselben Edition ersetzt die alte Datei erst nach vollständiger Prüfung; Titel-/Jahrwechsel, Removal oder Revocation dürfen sie nicht retten. Kein Löschen bestehender Dateien. Bei realem Reservemangel ist weiterer persistenter Erwerb weiterhin begrenzt. |
| P0-A: unnötige Generationen | `widget_policy74.py` bindet die tatsächliche Gruppenauswahl statt Änderungszeiten der gemeinsamen Datei. `home_publication74.py` entfernt minutenweise Fortschritts-/Receipt-Buchhaltung aus der Inhaltsignatur; der bestehende fokussierte Hero-Pump aktualisiert Fortschritt. Provider-Proofs behalten die ursprüngliche Quelle auch bei einem Edition-Fallback. | Tatsächlicher Publisher: identische Signaturen/Objekte über drei Cachezyklen; gültige Löschungen und Konto-/Gruppenwechsel weiterhin durch bestehende Tests. Manifest-Heartbeat ist keine neue Inhaltsgeneration. |
| P0-C: Quellwechsel / Schwarzbild | `event_art81.py` speichert bestätigte Bilder pro logischem Event und priorisiert passende TMDB-Backdrops vor XMLTV, Provider und generischen Postern. Ein niedrigerer Rang verdrängt keine bestätigte bessere Quelle. Neue Datei und Receipt werden unter vorhandenem Profillock atomar freigegeben. `hero_epg63.py` behält ein lokales altes Bild desselben Events hinter der neuen Textur; echte Event-/Mappingwechsel und Opt-out leeren diese Ebene. | Kein TMDB↔XMLTV-Rückschritt bei gleichem Event; separate Event-/Profil-/Freigabeschlüssel. Höherwertiger Erwerb bleibt bis zum vollständigen Decode ausstehend. Android-Texture-Upload und zehnminütiger Croods-Test offen. |
| P0-D: eigene TMDB-Suche | `art_trace81.py`, `media_sources43.py`, `tmdb_connection60.py`: anonymisierte Zustände, echte HTTP-Responsecodes und Latenz; keine erfundenen HTTP-Requests bei DNS-/Connectfehlern. Pro Event Inflight-Schutz, 60s Nichttreffer-/Fehlerbackoff, 300s bestätigter Metadaten-Cache; eigener Lieferant wird nicht zweimal pro Resolverdurchlauf aufgerufen. Token und bewusste Deaktivierungen bleiben unverändert. | Fünf dokumentierte Beispieltitel mit unabhängigen synthetischen Detailantworten, Alias nur mit bestätigter Alternativtitelantwort. HTTP 200/401/429/500, Netzfehler, Parallelaufrufe, Opt-out und Geheimnisfreiheit. Keine tatsächliche private API-/Android-Erfolgsbehauptung. |
| P1: Hero und Rails | `widget_skin81.py` ersetzt nur digest-geprüfte eigene .80-Knoten. 1620×400 Hero in 1080p-Designkoordinaten, proportionaler Hintergrund, großes vollständig erhaltenes Portrait vor gedimmtem passenden Hintergrund, transparente rechte Infotabelle. 268px Medienrow mit originalem transparenten blauen Fokusrahmen; beide Reihen initial sichtbar. Medien-Hero optional als eigener TMDB-Backdrop, Providerposter bleiben unverändert. Quelle korrekt gebunden. | Native 720p/1080p, Pixel-/Geometrieprüfungen, Fokus und gespeicherte persönliche Widgets. Unbekannte veränderte Adapter werden blockiert und nicht überschrieben. Keine globale Skin-Neugestaltung. |
| P1: Kataloganzeige | `catalog_progress73.py`: standardmäßig kein Fortschrittsdialog und kein Gruppenpopup. Optional kleine reservierte Statuszeile; optional ein Abschluss des gesamten Jobs. `catalog_jobs73.py` und `catalog_ui73.py`: persistente neue/geänderte/unveränderte/verarbeitete Zahlen, fehlgeschlagene Gruppen und echte API-/Vollsync-Zeit je Bereich. Leere Gruppen erhalten alte Daten und berechtigen keinen Vollsync-Zeitstempel. | Echte lokale HTTP-/SQLite-Tests für Null-Diff, Kaltlesen, Leerantwort, Fehler und unveränderte 3357 Live-Sender. Ältere Legacy-Imports liefern weiterhin nur ihre tatsächlich vorhandenen received/stored-Statuswerte; unbekannte neue/geänderte Zähler werden nicht erfunden. |
| P1: Kodi-DB/Player | Die read-only Diagnose fehlender MyVideos-Views bleibt erhalten; kein View-Neubau oder Datenbankreset. Die funktionierenden .80-Play-/Stop-/Exit-Routen werden nicht ersetzt. | Bestehende EPG-, Wiedergabe-, Autoplay-/Resume-/Exit-Suites und echte synthetische Kodi-Wiedergabe/ACKs. Android MediaCodec bleibt separat abzunehmen. |

## Tests

Die verbindlichen Gatefälle A1–A9 und die reproduzierbaren Befehle stehen in `ANDROID_ABNAHME_02981_DE.md`. Endgültige Zähler, CI-Links und native Receipts werden vor Fertigmeldung im folgenden Ergebnisblock ergänzt. Frühere Fehlversuche (unter anderem falscher opaker Fokusrahmen, veraltete Remote-only-Testannahme und Fixture-Teardown) gelten nicht als bestandene Abnahme.

### Ergebnisblock

- Vollständige Host-Suite: läuft; endgültiges Ergebnis vor Übergabe ergänzen.
- Neue gezielte Tests: Render-Cache, echter Publisher, TMDB-Protokoll, Katalog-Readback, UI-Digests und Bestandsschutz.
- Native Kodi 720p/1080p mit künstlichem Portal, TLS-Bildquelle, EPG und H.264/AAC-Stream: läuft; endgültige Receipts ergänzen.
- Alle Android-Gates: **ANDROID_NOT_TESTED**.
- Prüfpaket: `test-builds/02981/plugin.video.xtreammate-0.1.29.81.zip`, zugehörige `.sha256`.

## Bestandsschutz

Keine Löschung, Deinstallation, Token-/Provider-Änderung, Profilmigration oder automatische Android-Installation. Regulärer, Pilot- und NeoDark3-Katalog verbleiben bei .80. Installer 0.5.26 bleibt byteidentisch. Die Schutztests halten alle 762 bisherigen XCMate-Quelldateien und bisherigen Testmethoden/Skipbedingungen fest; bewusste Änderungen sind als exakte Deltas nachvollziehbar. Neue validierte Bilddateien werden additiv unter dem vorhandenen Budget gespeichert, ohne Kodi-Texturecache oder Datenbanken zu löschen. Box A bleibt unangetastet.
