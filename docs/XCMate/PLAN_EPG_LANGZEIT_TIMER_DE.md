# XCMate – separate Ausbaustufen Langzeit-EPG und Timer

Stand 19.10.2026. **Analyse/Plan, keine fertige Implementierung.**
P0 kommt separat als [0.1.26-Kandidat](IMPLEMENTIERUNG_026_P0_REMOTE_OSD_DE.md).
Arbeitsgrundlage: [Geräteübergabe §§4–6](ANDROID_025_HANDOFF_REMOTE_3LEVEL_EPG_SCHEDULE_DE.md)
und [Issue #21](https://github.com/artattakk-creator/kodi-noodleprivate/issues/21).

## Tatsächliche Grenzen

- `epg_views.guide_for_channel()` erstellt höchstens **48** noch relevante Ereignisse;
  `resolve_guide()` begrenzt auch die Kombination aus Short-EPG und XMLTV wieder auf 48.
  Overlay und `programme_lines()` sehen deshalb nur diesen Ausschnitt. Bei 30-min-Sendungen
  sind das schon nach etwa einem Tag 48 Einträge; bloßes Entfernen von „48 Stunden“ reicht nicht.
- `epg_preview.status_lines()` zählt Programme bis **+48 h** für die Statusstatistik.
  **Dies ist kein XMLTV-Importfilter und kein eigener 48h-Filter in `programme_lines()`.**
  Die tatsächliche Quellenreichweite ist aus dieser Statistik nicht ableitbar.
- XMLTV wird mit Ereignis-Streaming gelesen, dann jedoch als Programmdictionaries im RAM und
  JSON-Cache gehalten. Obergrenzen bleiben 80 MiB, 150.000 Programme und 10.000 Kanal-IDs.
  Der Import kann vor der UI-Begrenzung scheitern. 50.000 Sender × 10 Tage dürfen nicht
  unkontrolliert materialisiert werden; Limits nicht blind erhöhen.
- `epg.py` prüft bei Commit, ob überhaupt noch ein gültiges Programm innerhalb der nächsten
  sieben Tage existiert. Das ist eine **Brauchbarkeitsprüfung**, keine Tagesnavigation oder
  vollständige Beschränkung aller gespeicherten Programme auf sieben Tage.
- Der aktuelle Kurz-EPG-Abruf nutzt `limit=4` und Cache-Fallback. Daraus lassen sich keine
  sieben/zehn Tage erzeugen. Ein Feed mit 24–48 h muss als solcher ausgewiesen werden.
- Der sieben Tage alte Fallback-Import darf noch gültige Sendungen liefern, bedeutet aber
  keine sieben Tage Programmhorizont. Importalter und letzte verfügbare Sendung trennen.

## Phase B – eigenständiger Branch und PR für P1

1. SQLite im privaten Add-on-Profil, neue separate Datei; bestehende Konten, Quellen,
   Favoriten, Gruppen und manuelle Zuordnungen unverändert übernehmen. UTC-Eventmodell mit
   Portal, Stream-/XMLTV-ID, Titel/Beschreibung, Start/Stop, Quellpriorität, Importzeit und
   optional stabiler Provider-Programm-ID. Kanalaliase separat indizieren; keine Kopie
   derselben Programme für jeden Xtream-Alias.
2. Indizes `(portal_id, epg_id, start_utc)` und Stream→EPG-Auflösung; stabiler Event-Key,
   explizite Quellenpriorität und manuelle Overrides wie im vorhandenen gemeinsamen Resolver.
   Quellimport in Staging-Transaktion, erfolgreicher Snapshot atomar freigeben. Bei Abbruch
   alten Snapshot behalten; keine teilweise geleerte produktive Guide-Datenbank.
3. Begrenzter Hintergrundimport: zeit-/senderbezogene Auswahl, bounded Batches, Disk-/RAM-
   Budget, SQLite-Version auf Kodi 21/Android prüfen. Bestehenden JSON-Cache einmal im Worker
   übernehmen, ohne Konfigurationsmigration. Netzwerk-/Entpack-/Parsegrenzen beibehalten.
4. Now/Next-Snapshot behält seinen kleinen RAM-Arbeitssatz für laufenden Sender und sichtbare
   Zeilen. Gleiche Prioritätsregeln für Browser und Infobar. Für Tag/Sender/Seite stellt ein
   Worker vorbereitete Ergebnisse bereit; kein HTTP/Import/DB-Vollscan beim D-Pad-Callback.
5. Browser standardmäßig sieben, optional zehn **lokale Kalendertage**. Lokale Mitternacht
   und nächste Mitternacht separat in UTC umrechnen, nicht pauschal +86400 bei DST. Tageswechsel,
   Such-/Programmauswahl, Titel/Zeiten/Beschreibung, kanalweise Seiten/Ergebnisgrenzen. Über
   Mitternacht laufende Programme per Intervallüberschneidung abfragen.
6. Je Quelle echte erste/letzte Sendung, letztes erfolgreiches Update, Alter und Anzahl
   zugeordneter Sender/Programme anzeigen. Fehlende Tage explizit leer erklären. EPG-Aktionen
   für noch nicht ausführbare Scheduler-Funktionen nicht als erfolgreich anbieten.
7. Tests: >48 Ereignisse, Tag +7/+9, 24h-Feed, Mitternacht/DST, Quellenüberlappung, Mappingwechsel,
   gescheiterter Import/Schreibfehler/Neustart, begrenzte Queries und 53.664-Sender-Katalog.
   APK/Kodi-SQLite und Reaktionszeiten auf echtem Android separat abnehmen.

## Phase C – eigenständige P2-Ausbaustufe

`reminders.py` speichert aktuell Benachrichtigungen; `_fire_reminder()` schaltet keinen Sender um.
`recordings.py` startet sofort einen FFmpeg-Prozess mit Laufzeit. Es gibt noch keine persistente
EPG-Start-/Stopp-Queue, Konfliktverwaltung oder nachgewiesene Android-Aufnahmeengine.

Vor Implementierung/Aktivierung von Aufnahmen **auf dem echten Android-Gerät** zuerst nur lesen/
prüfen: FFmpeg-Pfad und Ausführbarkeit/Version mit Timeout, alternative verfügbare PVR-Engine,
Schreibtest im gewünschten Ziel, freier Speicher und Provider-Parallelstream-Limit. Ein FFmpeg
in dieser Linux-Cloud beweist nichts über Android. Keine System-Binaries automatisch installieren.
Erst erfolgreicher kurzer kontrollierter Aufnahmeversuch mit prüfbarer Ausgabedatei bestätigt
eine verwendbare Engine. Ohne Engine Aufnahmeplanung deaktiviert und Grund anzeigen.

Reminder danach: UTC-Timer, konfigurierbarer Vorlauf, atomare Persistenz, Zustände pending/notified/
completed/missed/cancelled, doppelte Ausführung nach Restart verhindern. Auto-Tune separat mit
aktivem Opt-in, Konflikt bei anderem Video berücksichtigen. Aufnahmen anschließend mit Vor-/Nachlauf,
Start/Ende, Stream-/Speicher-Konflikten, Abbruch/Recovery und Ergebnisprüfung. Kein garantierter
Android-Wakeup, keine Funktionsbehauptung bei Standby/Aus. Bestehende Timerdaten niemals löschen.

Diese Schritte sind offene Arbeiten; Issue #21 bleibt offen. Neuer Branch jeweils ab dann
aktuellem `main`, eigene Tests/CI/PR und Geräteabnahme. Kein automatischer Merge oder Publish.
