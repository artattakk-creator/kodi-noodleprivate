# .27-B – Aufnahmeziel (#126), auf Testschritt A aufgebaut

Draft-Test, keine Releasefreigabe. Noch kein Android-PASS.
Die .26-Baseline bleibt 15 PASS / 6 FAIL. Konkreter alter Mount/Syscall unbekannt.

Der Picker, die Startaktion, der Service vor `resolve()` und der Recorder selbst
verwenden jetzt denselben POSIX-/Hardlink-Vertrag: eindeutige Probe-Datei,
Schreiben/Lesen, Hardlink, File-/Directory-fsync und mindestens 64 MiB Reserve.
Die bestehende PES-Endfinalisierung bleibt unverändert. Kein unsicherer Rename-
Fallback. Nicht geeignete Ziele erzeugen getrennte feste Reason-Codes,
Syscall-Kategorie und numerisches errno, keine privaten Pfade im Log.

Bei inkompatiblem Ziel wird ein tatsächlich erfolgreich geprüfter persistenter
App-Ordner angeboten. Android-Private-Kandidaten werden nur geprüft, wenn sie
erreichbar sind; kein temporärer Cache, kein Root-/Berechtigungseingriff und
keine Garantie für jeden Kodi-Fork. Nur nach Zustimmung wird recordings_folder
geändert; vorhandene Dateien bleiben unverändert am bisherigen Ort. Ist kein
kompatibles Ziel erreichbar, wird abgelehnt, keine Providerverbindung aufgebaut.

- [ ] B01 Einstellungen → Speicher → Aufnahmeordner: auswählen, prüfen, abbrechen.
- [ ] B02 Nicht kompatibles Ziel: klarer Grund; Start erzeugt keine zusätzliche
  Providerverbindung. Geprüften App-Ordner bewusst annehmen, falls angeboten.
- [ ] B03 Sofortaufnahme starten, zusätzliche Verbindung erlauben; Status wird
  von pending/starting zu recording, Datenmenge steigt. Auftrag ≠ laufende Aufnahme.
- [ ] B04 Nach etwa zwei Minuten gezielt beenden; Status complete, Bytes >0.
- [ ] B05 Fertige Datei aus Aufnahmeverwaltung abspielen: Bild und Ton.
- [ ] B06 Offline erneut abspielen; Kodi-Neustart erhält Datei und Eintrag.
- [ ] B07 Echte Unterbrechung: partial/failed und Diagnose, kein Datenverlust.
- [ ] B08 Vorhandene EPG-/Live-/Medien-/Autoplay-/Icon-PASS prüfen.

SMB/SAF/FAT32 und emulierter Android-Speicher werden nicht pauschal freigegeben;
die reale Fähigkeitsprobe entscheidet. Der spätere Download nutzt auf expliziten
Nutzerwunsch dieselbe Einstellung, eigene Kennzeichnung und Verwaltung.
