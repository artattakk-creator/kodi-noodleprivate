# .28-B – kumulativer P0-Test: Menü + Speicher-/Streamdiagnose

Enthält .28-A aus #132. Kein Android-PASS, kein vollständiger Releasekandidat,
kein automatischer Merge/Release. Die .27-Abnahme bleibt **13 PASS / 15 FAIL**.
Such-Live A01–A08 und Serienautoplay sind eingefroren.

## Sichere Dateistrategie

Hardlinks sind nicht mehr die einzige sichere Option. Ein neues gemeinsames,
Recorder-unabhängiges Modul prüft zuerst `renameat2(RENAME_NOREPLACE)` über die
exportierte native libc-Funktion, ohne architekturabhängige Syscallnummern. Ist
API oder Dateisystemfunktion nicht verfügbar, bleibt exklusives Hardlink-Publish
als Rückfall erhalten. Sind beide nicht unterstützt, wird vor Providerauflösung
abgelehnt. Kein einfacher rename-/replace-Fallback auf vorhandene Mediendateien.

O_EXCL/O_NOFOLLOW, geprüfter regulärer Quelldateityp, Verzeichnis-Handle,
Datei- und Verzeichnis-fsync sowie Reserve bleiben Pflicht. Die Probe publiziert
eine eigene Zufallsdatei, liest sie zurück und entfernt nur die anhand Inode/Device
nachweislich eigenen Probe-Dateien. Konkurrenztests müssen genau einen Gewinner
und unveränderte Dateien der anderen Aufträge zeigen. Endgültiges Publish
überschreibt weder fremde Dateien noch ein vorhandenes Symlink-Ziel.

Die TS-PES-Endfilterung bleibt unverändert; allein ihre abschließende
Veröffentlichung verwendet das neue Verfahren. Das ursprüngliche TS-Teilfile
bleibt bis zum erfolgreichen Abschluss erhalten. Bei Downloads bleibt die
bisherige Hash-/Validator-/Teilfile-Wiederaufnahme erhalten. Nach Absturz zwischen
Publish und DB-Abschluss wird eine vollständige eigene Datei anhand Größe/Hash
geprüft, bevor der Auftrag als fertig gilt. Keine DB-Schemaänderung/Migration.

Android-Fähigkeiten werden tatsächlich geprüft, nicht aufgrund von Pfadnamen
angenommen. Ein geprüfter dauerhafter App-Ordner wird nur nach Zustimmung als
gemeinsames `recordings_folder` übernommen. Kein Cache-Ordner als Dauerziel.
Insbesondere fehlende libc-Funktion, fehlende atomische FS-Funktion, Rechte,
fehlender Speicher und fehlendes fsync werden getrennt abgewiesen.

## Diagnose und getrennte Engines

Die UI zeigt feste technische Codes, bei Bedarf `CODE@SYSCALL:ERRNO` und einen
verständlichen Hinweis. Öffentliche Marker enthalten keine Pfade, URLs, Titel,
Sender-/Portal-IDs oder Exceptiontexte. Fehlgeschlagene Aufnahmezeilen sind
anwählbar und zeigen den Grund; auch kleine Datenmengen erscheinen als Bytes.
`recording` wird erst nach dem ersten tatsächlich geschriebenen und
synchronisierten Datenblock gesetzt.

HLS/DASH über URL, MIME oder Manifestanfang werden als
`UNSUPPORTED_MANIFEST@SOURCE_HLS:0` bzw. `...@SOURCE_DASH:0` gemeldet.
Nicht-TS und verschlüsselte TS haben eigene Source-Codes. Kein DRM-Umgehen,
kein Versprechen für HLS-/DASH-Aufnahmen. Speicher-READY bedeutet nicht
Streamformat-READY. Beide Engines prüfen ihren Speicher unabhängig vom
Aufnahmeformat: ein HLS-Aufnahmefehler verhindert keinen direkten MP4-/MKV-
Download. Downloads bleiben im gewählten Aufnahmeordner als `Download - …`.

## Android-Prüfung (jede Zeile PASS/FAIL/NOT_TESTED)

- [ ] P01 Film-/Seriendetails: Links und sichtbarer Aktionen-Button öffnen Menü;
  Rechts/Zurück erhält exakt Position/Fokus (siehe .28-A M01–M07).
- [ ] P02 Einstellungen → Speicher → Aufnahmeordner prüfen: vorhandenes Ziel
  zeigt READY oder einen konkreten Target-/Syscall-/errno-Grund.
- [ ] P03 Falls nötig geprüften persistenten internen Ordner ausdrücklich annehmen;
  alte Dateien bleiben unverändert. Kein automatischer geheimer Ordnerwechsel.
- [ ] P04 Erlaubten direkten TS-Sender aufnehmen: Status Aufnahme läuft,
  tatsächliche Bytes steigen; keine bloße Startbestätigung als Erfolg werten.
- [ ] P05 Nach etwa zwei Minuten manuell beenden: complete, lokale Datei Bild/Ton.
- [ ] P06 Kodi-Neustart und offline erneut abspielen.
- [ ] P07 Kontrollierter Abbruch: partial/failed, Teildaten und Bestandsdateien erhalten.
- [ ] P08 HLS-/DASH-Sender (falls vorhanden) ergibt Source-/Manifestgrund,
  keine falsche Speicherdiagnose und kein Umgehungsversuch.
- [ ] P09 Trotz solcher Formatbeschränkung direkten Film und genau eine echte
  Serienfolge herunterladen: Bytefortschritt und COMPLETE im gemeinsamen Ordner.
- [ ] P10 Downloads pausieren/abbrechen/fortsetzen/retry, vollständige Dateien lokal
  und nach Kodi-Neustart offline abspielen; keine Teildatei als fertig anbieten.
- [ ] P11 Freiplatz-/Rechte-/Zielverlust sauber anzeigen, kein Überschreiben,
  keine zusätzliche Verbindung bei abgelehntem Ziel, keine endlosen Retries.
- [ ] P12 .27-Such-Live A01–A08, EPG, Live-IR, Staffelautoplay/Stop, Portale,
  Favoriten, Resume und Originalicon weiter PASS.

Alle neuen Android-Punkte zunächst NOT_TESTED. Ein Host-/CI-PASS ersetzt diese
Prüfung nicht. Rohlogs bleiben privat. Neue Gerätespuren sind nun den Kategorien
DETAIL_MENU, CAPTURE_TARGET, CAPTURE und DOWNLOAD zuordenbar.
