# XCMate – Verbindliche Spezifikation: Native TS-Aufnahme, EPG-Timer und Medienmanager

**Nutzerentscheidung:** 23.10.2026. **Basis:** `plugin.video.xtreammate` v0.1.29.22, Kodi 21.2 Omega, Android 13/RK3528 ARM32, Titan BINGIE MOD, IR. **Status:** Spezifikation / Entwicklungsauftrag, **noch nicht implementiert oder auf Android abgenommen**.

**Referenzen:** [Aufnahmen #62](https://github.com/artattakk-creator/kodi-noodleprivate/issues/62), [Filme/Serien-Downloads #63](https://github.com/artattakk-creator/kodi-noodleprivate/issues/63), [Medienmanager #113](https://github.com/artattakk-creator/kodi-noodleprivate/issues/113), [Design/Icon #37](https://github.com/artattakk-creator/kodi-noodleprivate/issues/37), [Player #79](https://github.com/artattakk-creator/kodi-noodleprivate/issues/79).

## A. Nutzungsablauf: Sendung im EPG aufnehmen

1. Nutzer fokussiert im **bereits funktionierenden großen EPG** eine Sendung, drückt OK (ggf. Kontextmenü). Neben Wiedergabe/Details/Erinnerung sind die Aktionen **„Aufnahme planen“**, **„Jetzt aufnehmen“** für laufende, wirklich unterstützte Streams, **„Zum Sendungsbeginn umschalten“** und **„Timer verwalten“** erreichbar. Bestehende Navigations- und Fokuslogik aus Android-Test 50 (E01–E10 PASS) unverändert.
2. Bei **„Aufnahme planen“** wird die tatsächliche Verfügbarkeit einer nativen TS-Aufnahme für diese Quelle vor Freigabe geprüft (Streamtyp, Quelle/Portal, Rechte, Speicherziel, Platz/Permission, ggf. Provider-Sessionlimits). Unbekannte Fähigkeiten als UNKNOWN statt gesichert verfügbar kennzeichnen; bei unsupported nicht als Aufnahme planbar vortäuschen. Falls eine spätere Laufzeitprüfung nötig ist, `unverified` markieren und konkretes Risiko anzeigen.
3. Bestätigungsdialog mit **Sendungstitel, Sender, Datum/Start/Endzeit, gewähltem Ziel, optionalem Aufnahmevorlauf/Nachlauf**, Warnung bei Kollision/limitierter Mehrfachverbindung; **Vorabmeldung 3 oder 5 Minuten** vor Start wählbar, konfigurierbar auch 0/1/10/15 sowie individuelle Minuten innerhalb sicherer Grenzen. **Beispiel-Default: 5 Minuten**. Unterscheide: (a) Aufnahmevorlauf, (b) Zeitpunkt des Hinweises, (c) Zeitpunkt tatsächlicher Wiedergabe-Umschaltung.
4. Nach Bestätigung Timer in persistenter SQLite-DB speichern. **`Meine Medien → Aufnahmen → Geplant`** listet den neuen Timer sofort. Timer ändern, löschen, Hinweis konfigurieren, Vor-/Nachlauf, Speicherziel und Wiederhol-/Konfliktstatus anzeigen. Alle Zeitpunkte intern UTC, lokale Anzeige mit Zeitzone, DST-Sonderfälle behandeln.
5. **N Minuten vor Beginn** bei aktivem Kodi: sichtbarer, IR-bedienbarer Dialog/Overlay in Kodi (kein behauptetes Android-System-Push): **„[Sendung] auf [Sender] beginnt in [N] Minuten. Jetzt zum Sender umschalten?“** Aktionen **„Ja, umschalten“** / **„Nein, weitersehen“**, ggf. „Details/Timer“. Kein implizites Timeout als Ja. Ein freigegebener Wechsel darf erst durch ausdrückliches OK des Nutzers eine bestehende Wiedergabe unterbrechen. Bei Annahme wird über den verifizierten XCMate-Live-Pfad derselbe `portal_id+stream_id` geöffnet; Startsender-Einstellung bleibt dauerhaft unverändert. Fremde Kodi-Sessions niemals automatisch stoppen.
6. **Wichtige Entkopplung (Empfehlung/Default):** Wenn der Nutzer „Aufnahme planen“ ausdrücklich bestätigt hat, wird die Aufnahme **zur programmierten Startzeit (ggf. mit eingestelltem Vorlauf) auch ohne Annahme des Senderwechsel-Dialogs** gestartet, sofern eine unabhängige zulässige Direct-TS-Streamverbindung technisch möglich ist und Kodi läuft. Der Dialog steuert **nur den Live-TV-Senderwechsel**, nicht die bereits zugesagte Aufnahme. Das verhindert versäumte Aufnahmen, wenn der Nutzer nicht am TV ist. Besteht eine Provider-Beschränkung auf nur eine Sitzung und kann die Aufnahme nicht zusätzlich gestartet werden, **vorher warnen**, zur Laufzeit sauber `failed`/Konflikt melden und niemals heimlich umschalten oder fremde Wiedergabe unterbrechen. Bei ausdrücklichem Wunsch des Nutzers kann Codex einen separaten Modus „Aufnahme nur nach Bestätigung“ anbieten, aber nicht als unbemerkten Default.
7. Aufnahme unabhängig von der aktuellen Live-TV-Wiedergabe über **nativen Direct-TS-Worker**: HTTP(S)-Stream öffnen und empfangene **echte MPEG-TS-Payloadbytes** in `.ts.part` speichern; Transportstream ohne Neu-Encoding, **keine separate FFmpeg-Installation**. Kein Abgriff des dekodierten Kodi-Bildschirms. Unterscheidung echter MPEG-TS-Bytefolge (`0x47` Sync in 188-Byte-Paketen, Header/Content-Type und sichere Laufzeitprobe) vs HLS-Playlist `.m3u8`, DASH, JSON-/HTML-Fehlermeldung. Unsupported-Typen ausdrücklich ablehnen oder gesonderte Engine später vorsehen. HTTP-Fehler, Reconnect, Timeouts, Stop/Abort, TS-Paketgrenzen, kurzer Prebuffer, Datenintegrität/Dateigröße/Endemarkierung behandeln. Dauerhafter Erwerb nur mit Nutzungsrecht, ohne DRM-Umgehung.
8. Während Aufnahme `recording`/rote Statusanzeige, Titel, Sender, verstrichene Zeit, Datei-/Restplatz, Ende/Stop/Verlängern. **Recorder-Stop darf keine laufende Kodi-Wiedergabe stoppen**; Live-Player-Stop darf wiederum einen unabhängigen Recorder nicht automatisch abbrechen. Nebenläufigkeit und HTTP-Verbindungen begrenzen.
9. Bei regulärem Aufnahmeschluss Daten sauber flushen und Datei in den gewählten Aufnahmen-Ordner finalisieren, Metadaten atomar speichern, als `complete` kennzeichnen; defekte/abgebrochene Dateien als `partial`/ `failed` deutlich sichtbar, niemals als erfolgreich ausgeben. **Fertig aufgenommene Datei in `Meine Medien → Aufnahmen → Abgeschlossen`** zeigen; über Kodi direkt abspielbar (auch offline), Resume verfügbar.
10. Bei Kodi-Neustart: Timer persistent und wieder aktiv, laufende Prozesse/Leases und `.part`-Files sicher prüfen (nicht blind verschieben oder löschen), versäumte Termine und Nichtverfügbarkeit der Box als `missed`/ `failed` anzeigen. **Kodi muss während der Aufnahme aktiv sein**; Android-Standby/TV-Aufwecken ausdrücklich nicht garantieren.

## B. Medienmanager `Meine Medien`

### Oberfläche

**Ein eigener XCMate-Hauptmenüpunkt**, nicht ein neuer globaler Kodi-Skin. Oberhalb der Inhalte drei mit IR erreichbare **Reiter in Reihenfolge `Serien | Filme | Aufnahmen`**. Standard-Startreiter **Aufnahmen**. Links/Rechts wechselt bei Reiterfokus den Reiter, Down in dessen Inhalte, Up zurück zum Reiter, OK öffnet Auswahl, Back schließt Detail/Unterordner und führt zurück zu XCMate-Home. Lesbarkeit/Fokus in Standarddesign und Space Premium; unverändertes Original-XCMate-Icon aus #37.

**Aufnahmen**:
- Unterbereiche **Geplant** (Timer, Vorabmeldung, geplante Senderwechsel, ändern/entfernen), **Laufend**, **Abgeschlossen**, **Fehler/Teilaufnahmen**.
- Sortierung Geplant nach nächstem Start, Fertig neueste zuerst. Datums-/Uhrzeitanzeige lokal, Dauer, Größe, Senderlogo soweit vorhanden; fehlendes Poster darf Ansicht nicht blockieren.
- Aktionen **Abspielen**, **Fortsetzen**, **Info**, **Speicherort öffnen**, **Timer bearbeiten**, **Aufnahme stoppen**, **Eintrag aus Liste entfernen**; **Datei physisch löschen** ist separat und bestätigt, niemals still.
- Kodi-Offline-Wiedergabe ohne Providerzugriff; Datei-Entfernung/USB fehlt → erklärter `missing_destination`-Zustand, keine Löschung der Kataloghistorie.

**Filme**:
- Ausschließlich tatsächlich fertig **lokal heruntergeladene Filme** aus #63. Poster, Titel, Jahr, Laufzeit, Wiedergabe-/Resume-Status, Speicherort, Größe. Abgebrochene Downloads nicht als fertigen Film anbieten; ein optionaler separater Downloadstatus ist erlaubt.

**Serien**:
- Hierarchie **Serienname → Staffel 01 / Staffel 02 / ... → Episode 01, 02 ...**, aus persistenter Medienidentität (portal/series/season/episode), mit logischem physischen Ablagekonzept `Serien/<Serie>/Staffel 01/S01E01 - Titel.ext` (Namen bereinigen, IDs/Kollisionen absichern). Episodenstatus, Länge, Resume/Gesehen, Offline-Playback. Mehrere Anbieter nicht aufgrund gleicher Titel/Jahre vermischen. Inaktive/abgezogene Datenträger sicher darstellen.

**Medienquellen und Speicherung**:
- Aufnahmen und Downloads dürfen getrennte Zielordner haben. Lokale Android-Dateien, USB/HDD und **nur tatsächlich schreibbare** SMB-Ziele; Kodi-`xbmcvfs` und POSIX-Pfade sind nicht austauschbar. Sicherer Write-/Read-/Rename-Test, Platzprüfung und FAT32-Limit; kein blindes Schreiben eines `smb://`-Ziels mit Python `open()`.
- SQLite/Jobs/Datei-Metadaten persistent in Add-on-`userdata`, eigentliche Medien im vom Nutzer gewählten externen Archivpfad. Kein vollständiger Medien-Scan auf GUI-/IR-Tastenpfad. Kein Umzug fremder Dateien. Keine pauschale Cache- oder Datenbankbereinigung.
- Fehlendes Artwork darf **nicht** Offline-Medien blockieren und durchläuft separaten #41/#111-Fehlerpfad.

## C. Technische Umsetzungsschiene und Grenzen

Bestehende Module in `main` .22:
- `recordings.py`: Altimplementierung `ffmpeg`/Subprocess + `recordings.json`; **nicht** als bereits native TS-Aufnahme verkaufen. Nicht blind voraussetzen, dass FFmpeg auf Kodi Android ausführbar ist. Historische Einträge konservativ read-only importieren, keine destruktive Migration.
- `guide_timers.py`: SQLite-Erinnerungen (explizit **kein** Recording/Auto-Tune), vorhandene Timer und Erinnerungen unverändert erhalten; neue Recording-/Tune-Timertypen separat erweitern oder versionierte Tabellen/DB.
- `home_menu.py::recording_folder/probe_directory`: Verzeichniswahl/Schreibprobe als Ausgangspunkt; VFS-File-Roundtrip nutzen, aber Schreibsemantik für große Dateien und TS/SMB gesondert testen.
- `service.py`: bestehender Kodi-Hintergrunddienst; Timer-Polling nicht im GUI-Thread, EPG-Callbacks/Kodi-UI nur korrekt marshalled; genau-einmal-Claim mit DB-Lease, zukunftssichere Prozessbeendigung, Schlafzustand, Abbruch.
- `media_window.py` und `media_progress.py`: Film-/Episodenmodell und Resume. Downloads #63 als eigene Queues, lokale Dateipfade für Offline-Wiedergabe.

**Ausführungsreihenfolge:** vorbereitende technische Capability-/Risk-Gates (Direct-TS/Multi-Session/Dateiziel), **eigener Draft-PR für Recorder+Scheduler**, weiterer kumulativer Draft-PR für Medienmanager-/Downloads-Integration oder ein klar gegliederter zusammenhängender Draft auf aktueller main-Basis; Versionsnummern mit offenen PRs abgleichen. Space Premium #37 selektiv integrieren, ohne veralteten Core aus PR #50 zu mergen. **Keine eigenmächtige Veröffentlichung oder Merge.**

## D. Prüfliste / Definition of Done

- [ ] EPG: Aufnahme planen, Details/Start-End/Vorlauf/Nachlauf/Hinweis 3 oder 5 min, Speichern und im Manager sofort sichtbar.
- [ ] Timer nach Kodi-Neustart unverändert erhalten; Sommerzeit/Zeitzone korrekt.
- [ ] Vorabmeldung tatsächlich sichtbar und mit IR auswählbar; „Ja“ schaltet zum richtigen Sender, „Nein“ lässt aktuelle Wiedergabe und Einstellungen unverändert.
- [ ] Aufzeichnungsstart autonom ohne Dialogbestätigung, wenn programmierte Aufnahme + unabhängiger zulässiger Direct-TS möglich; keine heimliche Umschaltung. Single-Session-Provider: eindeutiger Konflikt statt falschem PASS.
- [ ] Echte MPEG-TS-Daten mindestens 2–5 min ohne FFmpeg aufnehmen und erfolgreich lokal mit Kodi abspielen; kein HLS-/HTML-Fehlstream als fertige TS-Datei.
- [ ] Aufnahme-/Dateispeicher nach tatsächlichem ausgewähltem Ziel, USB-Schutz, kontrollierter Stop, ENOSPC, HTTP-Abbruch, Kodi-Ende, Daten-/Metadatenpersistenz und partielle Datei.
- [ ] Medienmanager: Reiter `Serien | Filme | Aufnahmen` per IR, korrekte Liste und Navigation, nach Neustart vorhanden.
- [ ] Aufnahmen: Geplant/Laufend/Fertig/Fehler unterscheidbar, echten Timer löschen/ändern, fertige Datei offline abspielen, physische Dateilöschung nur bestätigt.
- [ ] Downloads #63: DRM-freien, berechtigt direkt herunterladbaren Film und Episode vollständig speichern; Film nur in Filme, Serie/Staffel/Episode nur in Serien, kein Duplicate/Overwrite, Offline-Wiedergabe und Resume.
- [ ] Beide Designs Standard/Space Premium, Original-Icon gleich, 720p/1080p, BINGIE MOD und möglichst Estuary; Test-50-E01–E10 und alle Playback-/Autoplay-Regressionsfälle PASS, B02 Staffelwechsel **vertagt**, nicht zu Testpflicht zurücksetzen.
- [ ] An Android 13 ARM32 mit echten Sender-/Medien-Testfällen geprüft. Hosttests, CI, Test-ZIP, SHA256 und deutsche Android-Testanleitung. Keine Merges/OTA ohne Freigabe.

**Diese Spezifikation ist ein verbindlicher Codex-Auftrag, kein Nachweis einer Implementierung.** Freigegebene fremde/DRM-geschützte Streaminhalte niemals umgehen. Keine Provider-URLs, Zugangsdaten, Token oder Nutzerdaten öffentlich loggen.
