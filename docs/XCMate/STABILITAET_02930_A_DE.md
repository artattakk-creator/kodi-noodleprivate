# .30-A – Portal-Snapshots, Hintergrundlast und Shutdown (#141)

Basis main 9ce385b / .29. Private Rohlogs nicht angefasst/hochgeladen.
Historische .29-Abnahme unverändert **12 PASS / 16 FAIL / 0 NOT_TESTED**.
16.981 MemoryErrors stammen aus .28; .29 hat bislang nur ~37 Minuten ohne
erneuten nachgewiesenen OOM. Keine bestätigte primäre Leckquelle, keine Tombstones.

## Nachweisbare unnötige Arbeit und Reparatur

`app_services._run` rief Wartung, refresh_local, Artwork-Scan und Startvorbereitung
auch nach jedem erfolgreichen Katalogjob erneut auf (Wartezeit nur 0.1 s).
Mehrere dieser Stufen fragen `get_active()` ab; `portals.load_all()` las/parste
zuvor jedes Mal bis zu 4 MiB JSON. Zusätzlich Service-Recovery, Provider-, UI- und
Widgetpfade. Diese Aufrufquellen sind im Code nachvollziehbar; daraus folgt noch
nicht, dass sie die alleinige Ursache der Android-MemoryErrors waren.

Eine Snapshot-Version pro Interpreter: lokaler Pfad, Device/Inode, Größe,
mtime_ns und ctime_ns. Vor jedem Zugriff Version prüfen. Nur Änderung führt zu
neuem begrenztem Datei-/JSON-Read. Cache nicht dauerhaft nach Read-Fehler negativ
speichern. Änderungen via save/update, Profiltransaction, externe atomare Ersetzung
oder spätere Anlage einer fehlenden Datei werden erkannt. Gemeinsame Lesesperre
bei vorhandener Profiltransaktions-Lockdatei; Verifikation im eigenen Writer ist
reentrant. Keine neue Lockdatei bei reinem Lesen älterer Profile.

Öffentliche APIs liefern entkoppelte Kopien; `get_by_id` kopiert nur den Treffer.
Kein Caller kann gecachte Credentials/Gruppen durch Änderungen an einem Resultat
verändern. Ein Snapshot, keine Versionshistorie mit alten Credentials.
MemoryError: Snapshot freigeben, begrenztes 2–30-s-Backoff, feste Nutzermeldung,
niemals leere Portalliste als Reparatur. Erfolgreiche oder geänderte Datei erholt
sich; Daten werden nicht geleert/geschrieben. Echte JSON-Reads loggen die vorhandenen
BOOT-Phasen, Treffer nicht mehr pro Zugriff. Numerische Zähler trennen Call/Read/OOM
und feste Callsite-Klassen. Keine Stacktexte, IDs, Titel, URL oder Profilinhalte.

Vorbereitungsstufen maximal alle fünf Sekunden, unabhängig von schneller
Katalogarbeit. Unter realem OOM bzw. MemAvailable <64 MiB pausiert optionale
Bibliotheksarbeit; Live-/IR-/EPG-Playercode und Autoplay-Logik unverändert.
Prozess-RSS/PSS ist nicht mit Python-Heap identisch; keine Leakdiagnose allein
aus einer steigenden Gesamtkurve während Wiedergabe ableiten.

## Shutdown

Stop-Signale vor den begrenzten Joins, sofortige Sperre neuer optionaler Starts,
Artwork-Enrol/Download und Mess-Worker werden berücksichtigt. Optionales HTTP in
expliziten Hintergrund-Scopes erhält einen endlichen 2-s-Socket-Timeout; bestehende
Autoplay-/Vordergrund-Timeouts bleiben erhalten. Stop/MemoryError werden nicht erneut retried.
Streaming-Reads prüfen Abbruch und Retry-Wartezeiten sind unterbrechbar.
Native Download-/SMB-Sockets werden bei Service-Stop per shutdown geweckt; ihre
IO-Eigentümer schließen die eigenen Deskriptoren. TLS behält Zertifikatsprüfung
und SNI, der Handshake findet vor HTTP statt. Unterbrochene Downloads werden PAUSED
mit SERVICE_INTERRUPTED; keine falsche COMPLETE-/Auto-Retry-Meldung.

APP_WORKER_STOP_PENDING berücksichtigt laufende bekannte Unterworker, nicht nur
den Bibliotheks-Thread. Betriebssystem-IO/DNS/Dateisysteme können dennoch länger
blockieren; kein erzwungenes Töten und keine Freigabe einer noch aktiven
Capture-/Download-Lease. Der erste .29→.30-Upgrade kann das Verhalten des alten
.29-Interpreters nicht rückwirkend ändern. Für .30 separat Kaltstart und späteren
Service-Neustart/Upgrade prüfen.

## Ausführbarer Android-ARM32-Langzeittest

1. Kumulatives .30-ZIP installieren; Kodi neu starten, Profile unverändert lassen.
2. XCMate → Einstellungen → Wartung → **Stabilität / Langzeittest** → vier Stunden
   starten (optional acht). SDK-Service muss laufen. Nach fünf Sekunden Messwerte
   anzeigen; Python-Pointerbreite auf der Box muss **32** melden.
3. 30 min IDLE, 30 min Live mit IR-/Senderwechsel, 30 min Film inkl. Stop/Resume,
   30 min Serie inkl. natürlichem Folgen-/Staffelwechsel, 30 min großes EPG/Suche,
   30 min genehmigte USB-/SMB-Downloads/Unterbrechung, 30 min erneutes IDLE,
   30 min Neustart-/Service-Updateprüfung. Phasen im gleichen Menü markieren.
4. Numerische private `stability_samples.jsonl` (zwei Dateien à ~512 KiB maximal)
   auswerten: RSS/PSS falls erlaubt, Python-/OS-Threads, FD-Anzahl, GC-Generations-
   Zähler (keine vollständige Objektliste), Artwork-Inbox, Portal-Calls/Reads/OOM,
   Caller-Klassen. Zähler sind pro Interpreter, Prozess-Speicher gilt für Kodi
   insgesamt. Ein Neustart beginnt neue Zähler; fehlendes PSS ist UNAVAILABLE.
5. Menüs zwischen Phasen öffnen: kein MemoryError, kein ROOT_MENU_FAILED,
   keine ungebremste echte Portal-Read-/Parseflut; ohne Profiländerung Reads
   begrenzt, Calls können weiterhin bestehen. Profil-/Credentials-/Gruppenänderung
   einmal bewusst prüfen und sofortige Sichtbarkeit sicherstellen.
6. Alte Rohlogs, private Pfade, Titel und URLs nicht veröffentlichen. Nur numerische
   Messwerte und feste Fehlerklassen teilen. Nativer Heap/Android-OOM-Killer und
   Tombstones bleiben ohne gesonderte Gerätedaten eine Diagnosegrenze.

Optionaler ADB-Begleiter auf einem Host mit ADB:

```sh
python tools/android_stability_02930.py --hours 4 --interval 60 --output kodi-memory.jsonl
```

Er speichert ausschließlich numerische PSS/RSS aus dumpsys, kein logcat/Rohdump,
keine Seriennummer. Die tatsächliche Python-ARM32-Breite stammt aus dem Addon.
Das Tool meldet COLLECTED oder UNAVAILABLE, niemals allein Geräte-PASS.

| Gate | Status |
| --- | --- |
| Mehrstündiger echter ARM32-Lauf mit allen Phasen | NOT_TESTED |
| Erneute MemoryError-/Root-Menü-Freiheit | NOT_TESTED |
| .30-Service-Neustart/Update ohne Invoker-Kill | NOT_TESTED |
| Neun bestehende Such-/Player-/EPG-Regressions-PASS erhalten | NOT_TESTED |

Hosttests: 20.000 Portalaufrufe bei unveränderter Datei ergeben genau einen
JSON-Read; Aliasfreiheit, sofortige Version-/Writer-Invalidierung, parallele Leser,
OOM-Backoff/Recovery, Prep-Debounce, Socket-Abbruch und begrenzte anonyme Messdaten.
Das ist kein Nachweis einer reparierten alleinigen Android-Leckursache.
