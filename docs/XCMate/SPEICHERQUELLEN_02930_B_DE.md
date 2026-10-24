# .30-B – Speicherquellen und private Zwischenablage (#136)

Basis main 9ce385b / .29. Historische Android-Abnahme: 12 PASS / 16 FAIL;
die negativen ST-/CAP-/Download-Ergebnisse werden nicht umgewertet.

## Konkrete Änderung

Die Ordnerwahl für Aufnahme und Download beginnt jeweils mit **Kodi intern**,
**USB/externer Speicher** und **Kodi-SMB**. SMB zeigt vorhandene Kodi-Quellen
(Files.GetSources für files/video), USB vorhandene lokale Quellen/Mounts.
Danach startet der Kodi-Ordnerbrowser direkt an der ausgewählten Quelle.
Abbrechen, fehlende Berechtigung oder fehlendes Laufwerk ändern keine Einstellung.
Manuelles Browsen bleibt möglich; keine stille Auswahl des internen Speichers.
Quellenanzeigen und private Browserpfade werden nicht protokolliert.

Eindeutige Beschriftung: **Aufnahmeordner (Live-TV/TS)** gegenüber
**Downloadordner (Filme/Folgen)**. Bestehende getrennte Settings/Job-Ziele bleiben;
ein noch nie aktiviertes Downloadziel behält die bisherige anfängliche Vererbung
vom Aufnahmeordner. Eine explizite Auswahl wird nie durch diese Vererbung ersetzt.
Aufnahmepicker verwendet Capture-Native-Probe, Downloadpicker eigene
NATIVE/USB_STAGE/SMB2-Probe. SMB-Credentials/Signaturpflicht/Host-Freigabe unverändert.

## LINK:38 sauber zuordnen

Der vorhandene Befund betrifft CAPTURE_TARGET. Er beweist keinen Fehler des
SMB-Download-Protokolls. Neue STORAGE-Marker enthalten nur feste Klassen:
PICKER_ACTION, SOURCE_CATEGORY, TARGET_SELECTED, PROBE_BACKEND, TARGET_PROBE,
TARGET_BOUND, PERSIST_OK, STAGING_READY sowie bei Fehler code/step/errno.
Keine privaten Adressen, Freigabenamen, Nutzernamen, Passwörter oder Titel.

Die interne Zwischenablage versuchte zuvor ebenfalls Native-Publish/Hardlinks.
Wenn ausschließlich atomare Veröffentlichung/Directory-Sync dort nicht unterstützt
wird, darf eine **private .part-Zwischenablage** stattdessen exklusive O_NOFOLLOW-
Dateierstellung, verpflichtendes Datei-fsync, exaktes Readback und Kollisionsprüfung
verwenden. App-interne Android-Verzeichnisse werden bevorzugt; kein USB-Staging.
Die part-Datei wird niemals als fertig veröffentlicht/abgespielt. Checkpoint,
Prefix-Hash und vollständiger SHA256 prüfen spätere Wiederaufnahme/Übertragung.
Ein nach Stromausfall fehlender Directory-Eintrag führt zu Neustart/Fehler, niemals
zu einem falschen COMPLETE. Datei-fsync bleibt Pflicht; Fehler bleiben sichtbar.
Fertige Dateien behalten die bisherigen Backend-Verträge inklusive No-Replace,
Größe/Hash und Wiederherstellung. Die Capture-Atomic-Publish-Regel bleibt streng.

## Reproduzierbare Hostprüfung

```sh
PYTHONPATH=tests:src/plugin.video.xtreammate/resources/lib python -m unittest -v \
  test_xcmate_sources_02930 test_xcmate_download_targets_02929
```

Die SMB-Wire-Tests benötigen hostseitig impacket==0.13.0 und Loopback-Netzwerk.
27 Tests bestanden, darunter acht neue Fälle: Quellenwahl/Abbruch, getrennte
Aufnahmeroute, keine privaten Logwerte, LINK:38 nur im Staging, verpflichtendes
Datei-fsync und echter signierter SMB2-Transfer bei fehlendem Native-Link.
Die vorhandenen Übertragungs-/Disconnect-/Resume-/Kollisions-/Hash-Tests bestehen.
Host-SMB und simuliertes USB sind kein Nachweis physischer Android-Laufwerke.

## Android-Gates (jeweils NOT_TESTED)

1. Beide Picker öffnen; drei Quellenklassen, vorhandene Kodi-SMB-Verbindungen und
   tatsächlich angeschlossene USB-Geräte prüfen. Abbrechen unverändert.
2. Aufnahme auf intern, Download auf USB setzen; nach Neustart getrennt erhalten.
3. USB entfernen/ersetzen: verständlicher Fehler, kein Ordner auf intern erzeugt.
4. Kodi-SMB wählen, anmelden, Freigabe erlauben; Marker unterscheiden tatsächliche
   Zielprobe von INTERNAL_STAGE. Bei LINK:38 Phase und Backend festhalten.
5. Ganzen Film und ganze Folge auf intern/USB/SMB herunterladen, Größe/Hash,
   Pause/Resume und Wiedergabe testen. Keine COMPLETE-Meldung bei Abbruch.
6. Sofortaufnahme separat prüfen: Dateisystem/LINK:38 gegenüber HLS/MPEG-TS-Format.
   Poster-Retry bleibt eigener Test; keine Bilder/Jobs/Benutzerdaten löschen.

Kein main-Merge, Release, Repository-Index-Update oder OTA in diesem Draft.
