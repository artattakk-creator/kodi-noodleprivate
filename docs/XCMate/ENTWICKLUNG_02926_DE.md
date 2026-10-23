# XCMate .26 – Suchstabilisierung und ausdrücklich gewünschte einfache Aufnahme

23.10.2026; Branch `fix/xcmate-02926-search-record-now`, Basis `main`
`5bd7349eae89db85a5b0deac8362478d559d5007`, veröffentlichte Version `.25`.
**Draft/Test-ZIP; keine Produktionsveröffentlichung.**

## Befund und Umfang

Die übergebene [Suchabsturz-Analyse](https://github.com/artattakk-creator/kodi-noodleprivate/issues/118)
belegt laut ihren ausgewerteten Logs fast gleichzeitige Home-/Search-Aufrufe und
anschließenden Kodi-Neustart. Die Originale liegen diesem Entwicklungsstand
nicht vor; kein nativer Crashstack/Tombstone wurde daraus übernommen oder
nachträglich behauptet. Die genaue native Crashursache bleibt unbewiesen.
Arbeitsanweisungen im Anhang sind als Dokumentinhalt getrennt von der direkten
Nutzerergänzung behandelt: einfache Aufnahme aktivieren, ohne Timer/Medienmanager.
Der Android-Testkandidat folgt diesem eng begrenzten Start/Stop-Wunsch.

`.25` schloss in `_search()` das Medienfenster und rief in `open_media()`
anschließend `Container.Update(global_search)` auf. Dieser Aufruf geschah
innerhalb des von `open_route()` gehaltenen Navigationseigentums. Das war keine
bewiesene Root Cause, aber eine unnötige zweite native Containertransition.
`.26` entfernt diesen Pfad vollständig für die Medien-Suche: Eingabe,
Suchergebnis, Medien-Detail und Back bleiben im **selben WindowXML/Owner**.
Es entsteht kein Thread-übergreifendes GUI-Rendering und kein Home-Aufruf nach
Sucheingabe. Die bestehende Directory-/Legacy-Suche mit positivem Handle bleibt
zur Kompatibilität erhalten. Die Suchaktion aus Einstellungen verwendet einen
einmaligen Root-Suchnavigator; sein Back schließt im Owner-Pump. Live-Ergebnisse
nutzen das bestehende geprüfte Grid-Live-Handoff erst nach Owner-Release.

Lokale Datenworker liefern getrennte echte Counts für Sender/Filme/Serien,
48er-Seiten und explizite Indexfehler-/Ladezustände. Nur aktive Gruppen des
ausgewählten Portals; kein ungefragter Multi-Portal-Fanout. Sendernamensuche
wird mit echten Jetzt-Titeln der vorhandenen Guide-DB kombiniert. Manuelle
Zuordnung hat dieselbe Priorität wie im Grid; keine Änderung der Guide-Daten,
keine Netzwerkabfrage im IR-Callback, keine erfundenen Jetzt-Sendungen.
Der Query wird nicht geloggt. Die bekannten 23 Lightweight-PASS werden nicht
allein durch CI als erneute Android-PASS ausgegeben.

## Manuelle Recorderfunktion

Die zusätzliche Start/Stop-Steuerung steht unter Speicher & Aufnahmen.
Eine private neue `manual_capture_v1.sqlite` transportiert nur Kanal-/Portal-ID,
Ziel, Dauer, Zustand und Dateibasename. Streamadressen entstehen ausschließlich
im Service-Worker und werden weder geloggt noch in die Auftrags-DB geschrieben.
Der vorhandene Service startet den Supervisor erst nach einer manuellen Anfrage.
Dateisperre und globale Ein-Auftrag-Grenze schützen gegen zweite Interpreter;
die Aufnahme ist von Kodi-Player-Start/Stop unabhängig. Ein ausdrücklich
bestätigter zweiter Providerstream ist Voraussetzung, keine Capability-Garantie.

Die Engine aus Draft #117 ist selektiv übernommen und ihre bekannte
Endfinalisierung korrigiert. Ein Zeit-/Paketcut allein kann ein Codecframe
anschneiden. Die Finalisierung verwirft daher **pro Audio-/Video-PID** dessen
letzte nicht durch einen folgenden Start verifizierte PES-Einheit. Ein globaler
Byte-Truncate würde bei interleavten Spuren eine andere Spur anschneiden;
dieser Fall ist gezielt getestet. Die beiden Durchläufe brauchen begrenzten
RAM; zusätzlicher Plattenplatz bleibt beim Schreiben reserviert.

Nach fsync wird ein fertiger UUID-Dateiname exklusiv veröffentlicht, ohne
bestehende Medien zu überschreiben. Ein bewusster Benutzerabschluss kann eine
fertige Aufnahme ergeben; Service-Abbruch/EOF/Netzwerkfehler bleiben partial
oder failed. Nur eigene temporäre Verknüpfungen werden nach gesichertem
Abschluss entfernt; alte Bilder/Dateien/recordings.json bleiben unverändert.
Kein Recorder-CLI-Prozess, Timer, Downloader oder Medienmanager wird aktiviert.

**Hostnachweis:** echte kontinuierliche HTTP-Aufnahme 120,390 s Wandzeit,
9.057.088 Bytes, Media-Dauer 120,810022 s. Vollständiger strenger Decoderlauf
mit MPEG2/MP2: Exit 0, leeres Fehlerlog. Zusätzlich H264/AAC mit absichtlich
angeschnittenem Paketende finalisiert: strenger Decoder Exit 0, leeres Fehlerlog.
[Maschinenlesbarer Bericht](RECORDER_HOST_02926.json).
Die Entwicklungshost-CLI erzeugt/prüft nur Testquellen; sie wird von der Engine
nicht aufgerufen. **Kodi-/Android-Offline-Wiedergabe bleibt NOT_TESTED.**

Nur lokale POSIX-/Hardlink-Ziele werden in diesem Kandidaten angeboten.
SMB/VFS/FAT32/Android-SAF, Header-/Cookie-Pflicht, Stalker und adaptive oder
verschlüsselte Quellen sind nicht freigegeben. Maximal eine Aufnahme, 2 GiB
Dateibudget, Socket-/Probelimits, kein automatischer Reconnect. Ein im OS noch
blockierter Worker hält seine Dateisperre bis zum tatsächlichen Exit;
Shutdown behauptet keine garantierte Beendigung fremder OS-I/O.

## Verifikation und Lieferung

Gezielte neue Tests decken Such-OK/Cancel/Back/Wiederholung/5.105 Treffer,
EPG-Zuordnung, Indexfehler, Detail-/Playerdelegation, Owner-Release,
Single-Recorder, private Persistenz, echte lokale HTTP-Aufnahme mit manuellem
Abschluss, PES-Interleaving, Überschreibschutz, Abbruch und sichere lokale
Wiedergabeauswahl ab. Die gezielt ersetzte Suchmethode und drei klar benannte
Polling-/Trace-Hooks werden beim historischen Freeze einzeln geprüft;
keine alten Referenzdigests werden ersetzt. Live-/Guide-/Player-/Autoplay-
Module und Premium-Bilddaten bleiben unverändert.

Gesamtergebnis: [TESTERGEBNISSE_02926.json](TESTERGEBNISSE_02926.json),
[vollständiges Log](TESTLOG_02926.txt),
[Android-Testanleitung](ANDROID_TEST_02926_DE.md).
Ein erfolgreicher Host-/CI-Test ist keine Android-Crashabnahme. #118 bleibt
offen; Produktionsmerge/-Update erst nach Geräteabnahme und Freigabe für diesen
neuen Such-/Aufnahmekandidaten.
