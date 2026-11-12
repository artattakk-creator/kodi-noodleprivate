# Prüffähiger Folgestatus – sechs Widgetreihen, EPG, Artwork und Exit

Stand 12.11.2026. Grundlage: gesamte operative Übergabe einschließlich Kapitel 7 und Nutzerkorrektur 14:42 Uhr. **„Diese Woche im Trend“**, kein Bewertungsranking. Kein Merge/Release, kein Zugriff auf Android-Geräte, keine Änderung bestehender SkinShortcuts oder Daten.

## Sechs Reihen: getrennte Fakten und Abnahme

| Soll-Reihe | Vorhandene Datenquelle / Consumer | Host-/Implementierungsstatus | Android / Spinner / Darstellung |
| --- | --- | --- | --- |
| Filme | `widget_recent_vod`, gemeldeter eigener Home-Container 1520 | PASS: Uhrpfad akzeptiert, aktive MediaRow; 24 native Einträge und sichtbare Cover im synthetischen Kodi nachgewiesen. Standardtitel Filme bleibt. | NOT_TESTED auf Box B; eigene begrenzte Originalanimation in Draft #438 |
| Serien | `widget_recent_series`, 1530 | PASS: aktive MediaRow, 24 native Einträge und sichtbare Cover; Standardtitel Serien bleibt. | NOT_TESTED auf Box B; eigener unabhängiger Spinner in #438 |
| Im Kino / Neu im Kino | Gesicherter Fremdpfad `plugin.video.themoviedb.helper/?info=now_playing`, anderes Filme-Menü, 2510 | NOT_TESTED: gespeicherter Fremdpfad identifiziert und geschützt. Keine eigene XCMate-Kinoroute behauptet. Helper ist laut Bestandsaufnahme installiert/aktiviert. | NOT_TESTED: Home-Platzierung, Endpoint-Authentifizierung, echte Poster und begrenzter Zeilenspin fehlen als Folgeabnahme |
| Disney | Bisher Disney Plus, fremdes Serien-Menü 3520, `tmdb_type=movie` | NOT_TESTED: Quellenidentität/Inhalt zu prüfen. Keine erfundene Disney-Lizenz oder automatische Kategoriezuordnung. Keine Umbenennung gespeicherter Shortcuts. | NOT_TESTED: Quelle, Home-Slot, getrennte Überschrift und Spinner |
| Diese Woche im Trend | Bisher fremdes Serien-Menü 3510, Helper `info=trending_week&tmdb_type=tv` | NOT_TESTED: Wochen-Trendsemantik bleibt erhalten, keine Bewertungssortierung. | NOT_TESTED: tatsächliche API-Ausführung, Home-Platzierung, Cover, Spinner und Timeout |
| MP3s | Installierten Audioanbieter/Katalog gesondert prüfen, Kandidat `plugin.audio.m3sr2019` nur bei tatsächlichem Vorhandensein | NOT_TESTED: Audioidentität/Widgetroute und echte Audio-Klickziele noch nicht verifiziert. Keine Umleitung zu Videos. | NOT_TESTED: eigener Audiocontainer, Wiedergabe, Fernbedienung, Spinner |

Die IDs der Fremdreihen sind **nicht** neue Home-Slots und nicht mit den eigenen 1510/1520/1530 zu verwechseln. Keine der vier Zusatzreihen ist durch den Uhrfix oder den Film-/Serienspinner vollständig hergestellt. Defaultreihenfolge und sechs dauerhaft sichtbare Überschriften bleiben Pflicht des separaten Zusatzwidget-Schritts; vorhandene Benutzeranpassungen dürfen dabei nicht pauschal ersetzt werden.

## EPG-/Artwork-Konsolidierung: bestehende Pfade, keine neue Parallelarchitektur

- `local_epg` / `guide_store` liefern gespeicherte Zeitintervalle; `epg_merge52` vereinigt verifizierte Quellen und übernimmt nur belegte, fehlende Metadaten desselben Ereignisses. Quellen-/Kanalbindung in `epg_binding48`; bestätigte manuelle Auswahl darf nicht durch Providerfallback überschrieben werden.
- `epg_handoff63` enthält profil-/sendergebundene Now/Next-Snapshots; `programme_events46` konstruiert die gemeinsame Ereignisidentität, `programme_index46` hält reiche Ereignisfakten. Detailfenster laden auf ihrem vorhandenen Worker, nicht im GUI-Callback.
- Die selektiven vorhandenen EPG-/Mapping-/Details-/Retentiontests wurden ausgeführt: **88 PASS, 28,271 s**. Das ist kein Nachweis der realen vier Ansichten auf dem Android-Datenbestand und kein Beweis, dass Galileo #433 behoben ist.
- #433 bleibt offen: Bildübergabe vom Mini-EPG zum Detail und `SAVE_BLOCKED` benötigen korrelierte Ereignis-/Quellen-/Operationsdiagnose. Die drei protokollierten Speicherfehler dürfen nicht ohne Korrelation als Galileo-Ursache erklärt werden. Aktuelle Save-Pfade unterscheiden bereits SourceError, Persistenzblockade und Readback; generische Restfehler bleiben zu prüfen.
- #108 bleibt offen: temporärer Cache besitzt TTL/Pin-Schutz und räumt bei Aufnahme neuer Dateien auf; der 24-MiB-Providerposterstore hat noch keine vollständige referenzsichere Idle-Eviction. Keine blinde Löschung, keine neue Datenbank, kein pauschaler Reserve-Bypass. Persistente Logos und aktive/Hero/Detail-/manuelle/Favoritenreferenzen bleiben geschützt.

Die Übergabe verlangt ausdrücklich: **„Keine neuen großen Architekturbaustellen vor der Widget-/Android-P0-Abnahme.“** Der zentrale Snapshot-/GC-Ausbau wird deshalb als separater Folgeschritt geführt. Diesen offenen Stand nicht als vollständig implementierten EPG-Hub oder GC-PASS ausgeben.

## Exit und Bereinigung

- #174 bleibt FAIL im dokumentierten Android-Lauf: nativer Stop ohne bestätigtes ACK bis zum Neustart. Kein zusätzlicher Stop-Thread und keine Timeout-Verlängerung als Reparatur. Bestehende Player- und Fernbedienungspfade wurden im Uhr-/Spinnerfix nicht umgeschrieben.
- Gruppenwechsel war vom Nutzer beobachtet funktionsfähig. Der synthetische .90-Gesamttest `GROUP90_NATIVE_VIDEO_NOT_OWNED` bleibt separat als FAIL zu untersuchen; er beweist keinen neuen Android-Gruppenfehler.
- Native geerbte Prüfung `NATIVE_ONE_RAIL` bleibt FAIL im Gesamtlauf. Nicht entfernen oder als Bildbeweis werten; sie steht neben den aktuellen präzisen 1510/1520/1530-Pixelprüfungen.
- Keine Bereinigung auf einem Geräteprofil oder im privaten Backup ausgeführt. Aktive SQLite-/WAL-Dateien, Wizard-ACTIVE-Staging, letzte gültige Sicherungsgruppe, Senderlogos und aktive Bilder bleiben erhalten. PR #436/#434/#435 sind getrennte Nebenstränge. Ältere Backupstände nicht ohne vollständigen Restore-/Hashnachweis entfernen.

## Nächste echte Abnahme

Box B: Native 1510/1520/1530, Überschriften und reale Cover, Fokus und Klick, je Reihe Laden/leer/Fehler/Timeout, drei Kaltstarts, Skinreload und Player-Rückkehr. Danach separat sechs Reihen mit bestätigten Quellen, Defaultanordnung und geschützten Benutzeranpassungen abnehmen. Alle Gerätefälle sind bis dahin NOT_TESTED. Box A bleibt unangetastet.
