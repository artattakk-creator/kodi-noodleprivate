# Native Direct-TS – separater Prototyp zu #62 / #113

**DRAFT. Nicht in XCMate eingebunden. Kein Merge und keine Veröffentlichung
dieser Engine ohne weitere Abnahme.** Die reguläre `.25` enthält ausschließlich
den Hotfix aus PR #116. Core-Version und Installations-ZIP werden durch diesen
Prototyp nicht verändert. `experiments/` wird nicht ins Kodi-Add-on gepackt.

## Implementiert

- Eigenständige Python-Engine ohne Kodi-Player-, FFmpeg-CLI- oder GUI-Aufruf;
  `run()` wird auf eigenem Worker ausgeführt, `stop()` betrifft nur diesen Job.
- Genau eine vom Aufrufer ausdrücklich freigegebene zusätzliche HTTP(S)-
  Verbindung; kein automatischer Reconnect. Keine URL oder privaten Header in
  Status/Logs. Keine Zugangsdaten in Dateinamen, ausschließlich zufällige Job-ID.
- 188-Byte-Synchronität, Paketheader/Adaptation, Transportfehler,
  PAT-/PMT-Sections mit MPEG-CRC und bekannte Audio-/Videostreamtypen.
  Scrambling und Conditional-Access-Descriptors werden abgelehnt. HTML,
  Playlist-/DASH-Adressen und entsprechende Response-Typen werden abgelehnt;
  Sync-Bytes allein reichen nicht als gültiger TS-Nachweis.
- Header-/Paketprüfung über die gesamte Aufnahme, bounded Probe (2 MiB / 10 s),
  Socket-Timeout 2 s. Redirects begrenzt durch urllib, HTTPS-Downgrade gesperrt.
- Nur ausdrücklich unterstütztes lokales POSIX-Ziel; Prüfung von Schreibbarkeit,
  Mindestfreiraum (64 MiB), Dateibudget (maximal 2 GiB im Prototyp) und sauberer
  Fehlerklasse. SMB/`special://`/VFS werden transparent abgelehnt.
- Eigene `.ts.part`, nur ganze TS-Pakete, JSON-Status `pending`, `recording`,
  `complete`, `failed`, `partial`. Fortschritts-Persistenz höchstens alle fünf
  Sekunden. fsync, exklusive Finalisierung ohne Überschreibung fremder Dateien.
  Vorzeitiges EOF, Stop, Netzwerk-/Speicherfehler werden nie als complete gemeldet.
  Nach erfolgreichem Abschluss wird nur die eigene zusätzliche Part-Verknüpfung
  entfernt; bestehende Medien bleiben unangetastet.

## Tests

Gezielte Tests aus dem Repository-Root:

```bash
python -m unittest discover -s tests -p test_xcmate_native_ts_prototype.py -v
```

Sie verwenden echte PSI-CRCs, fragmentierte Paketgrenzen, ungültige Quellen,
verschlüsselte Payload-/CA-Marker, echte lokale HTTP-Verbindungen, Abbruch,
begrenzten Speicher, vorzeitiges EOF, unveränderte fremde Datei und fehlende
Zustimmung zur zweiten Verbindung. Kein Bezug zu privaten Providerquellen.

Zusätzlich führt `smoke.py` einen tatsächlichen, zeitgesteuerten lokalen
HTTP-Mitschnitt aus einer echten MPEG-TS-Testquelle durch. Eine externe CLI
darf **nur zum Erzeugen/Prüfen der Testfixture auf dem Entwicklungshost**
verwendet werden; der Recorder selbst verwendet keine.

Beispiel für eine frei erzeugte, 180 Sekunden lange Testfixture:

```bash
ffmpeg -v error -f lavfi -i testsrc2=size=320x180:rate=10 \
  -f lavfi -i sine=frequency=440:sample_rate=48000 -t 180 \
  -c:v mpeg2video -b:v 250k -c:a mp2 -b:a 64k -muxrate 600000 \
  -f mpegts /tmp/fixture180.ts
python experiments/native_ts/smoke.py /tmp/fixture180.ts /tmp/native-capture
```

Host-Mitschnitt und Offline-Decoderprüfung werden mit ihren tatsächlichen
Ergebnissen getrennt dokumentiert. Sie sind **kein Kodi-Geräte-Playback**.

## Integrationsblocker – bleibt Draft

1. **Kodi-Offline-Playback der 2–5-Minuten-Aufnahme NOT_TESTED.** Kein Kodi-
   Prozess/Android-Gerät im Workspace. Auch ein erfolgreicher Host-Decoder
   erfüllt diese Freigabebedingung nicht.
2. Android-ARM32-POSIX-/USB-/Dateisystemtests fehlen. Exklusive Hardlinks sind
   auf FAT32/SMB nicht vorauszusetzen; dort wird diese Engine nicht freigegeben.
   Ein eigener geprüfter VFS-Publish-/Recovery-Pfad ist noch erforderlich.
3. Kein UI, Portalresolver, Provider-Verbindungslimit-Probe, authentifiziertes
   Kodi-URL-Suffix/Cookie-Handling, Aufnahmeindex oder Neustart-Reconciliation.
   Das Zustimmungsargument ersetzt keine verifizierte Provider-Capability.
4. PAT/PMT/Scrambling-Probe ist eine Formatprüfung, keine Freigabe für DRM.
   Zusätzliche verschlüsselte/proprietäre Formate müssen abgewiesen bleiben.
   Kontinuitätszähler/PCR-Verlauf und reale Provider-Unterbrechungen sind für
   die Produktionsreife weiter zu prüfen; keine Datenstrom-Reparatur erraten.
5. Zeitplaner #62, Vorabmeldung 3/5 Minuten und Senderwechsel erst nach OK
   sowie Meine Medien #113 bleiben getrennte nächste Schritte. Aufnahme muss
   unabhängig von einer Senderwechselbestätigung funktionieren, sobald sie
   ausdrücklich geplant und ihre Quelle freigegeben ist. B02 bleibt separat.

Erst wenn die fehlenden Geräte-/Format-/Speicher-/Playback-Gates bestanden sind,
darf eine neue installierbare XCMate-Version die Funktion aktivieren. Kein
scheinbar funktionierender Aufnahmebutton und keine ungeprüfte Migration alter
`recordings.json`-Daten in diesem Draft.
