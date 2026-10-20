# XCMate 0.1.28.1 – instrumentierter Start-Hotfix / Issue #38

Stand: 20.10.2026. **Testkandidat, keine Android-Abnahme, kein Merge/Release.**
Basis: veröffentlichtes `main` `63b4cd6981351a398968a3795831cf024b07b2ba` (0.1.28),
Branch `fix/xcmate-028-startup-hang`. [Issue #38](https://github.com/artattakk-creator/kodi-noodleprivate/issues/38)
· [vollständiger Auftrag](CODEX_AUFTRAG_0281_STARTUP_HOTFIX_DE.md)
· [Android-Test, Installation und Rollback](ANDROID_TESTPLAN_0281_DE.md)
· [maschineller Prüfnachweis](TESTERGEBNISSE_0281.json).

## Ursache: Nachweis und Grenzen

**Der ursprüngliche intermittierende Android-Hänger ist nicht abschließend lokalisiert.**
Die ausgewerteten Protokollbefunde aus Issue #38 zeigen gestartete `default.py`-Aufrufe,
fehlendes Directory-Ergebnis und spätere Abbrüche, jedoch keinen Python-Traceback und
keinen SQLite-Lock-Nachweis. Die privaten Originalprotokolle liegen dieser Cloud-Arbeit
nicht vor; Grundlage sind der Auftrag und die vollständig gelesenen Issue-Kommentare.
Nach erzwungenem Kodi-Stopp plus Android-App-Cache-Leerung startete dieselbe 0.1.28
wieder. Das beweist keine Cache-Ursache und rechtfertigt keine Profil-/Cache-Löschung.

Nachträge in Issue #38 vom 20.10.2026, 11:26/11:27 UTC: Startkanal Bild/Ton,
erstes OK mit vollständiger Infoleiste, zweites OK mit Bedienleiste und schnelle
Links-Senderliste mit EPG sind für **produktive 0.1.28 nach Recovery** am Gerät bestätigt.
Diese Befunde sind keine Abnahme des neuen Hotfixes. Gruppenliste/Einzelfunktionen
bleiben nach dem dokumentierten Stand offen. Der Hotfix verändert die Remote-Logik nicht.

Im veröffentlichten Code sind folgende Schwächen nachgewiesen:

1. `default → main → utils` importiert schon `httpx` bzw. `urllib.request`, bevor die
   erste Router-Aktion protokolliert wird. Menü und Widgets brauchen keinen Transport.
   Ein absichtlich fehlgeschlagener Transportimport verhindert im alten Code den
   Menüaufbau; der neue Code erreicht denselben Menüaufbau ohne diesen Import.
   Das beweist die unnötige Abhängigkeit, keinen nativen Android-Importdeadlock.
2. Jeder Dispatch ruft `import_from_settings()` auf. Bei leerem Profil werden dabei
   Legacy-Einstellungen gelesen und gegebenenfalls Portale geschrieben; zusätzlich
   wird der Assistent beim Root-Aufruf modal geöffnet, bevor das Directory fertig ist.
   Vorhandene Portale lösen zwar keine Migration aus, werden aber mehrfach eingelesen.
3. `load_all()` prüft einen bereits lokalen Pfad zunächst über VFS und öffnet danach
   ohne Dateityp-/Größenprüfung. Eine FIFO anstelle einer Portaldatei lässt den alten
   Pfad tatsächlich hängen (isolierter Prozess/Timeout). Das ist ein defensiver
   Regressionstest, **kein Nachweis einer FIFO auf dem Android-Gerät**.
4. EPG-Worker warten in `with _REFRESH_LOCK` unbegrenzt aufeinander. Ein zweiter Worker
   bleibt im isolierten Altcode-Test nach vier Sekunden noch hängen. Die Xtream-
   Streaming-EPG-Funktion erhält außerdem keinen Kodi-Abbruch-Callback, obwohl sie ihn
   bereits unterstützt. Beide Probleme sind nachweisbar; eine Kausalität zum Root-Hänger
   wurde nicht belegt. Root hat selbst keinen direkten EPG-/Katalog-Aufruf.
5. Widgets lesen lokal, haben aber bisher keine Grenze für die Laufzeit einer einzelnen
   SQLite-Abfrage. Busy-Timeout ist endlich (zuvor zwei Sekunden pro Verbindung), kein
   Beweis eines unbegrenzten SQLite-Locks. Der Fehlerhandler kennt bereits abgeschlossene
   Menü-Directories nicht und kann nach einem späteren Fehler doppelt abschließen.

Vier gezielte Gegenproben gegen unverändertes `63b4cd6` schlagen erwartungsgemäß fehl:
Transport-Abhängigkeit, leeres Profil, FIFO (innerer 2-s-Timeout) und gesperrter EPG-
Worker (äußerer 4-s-Timeout). Die entsprechenden Hotfix-Tests bestehen. Dies reproduziert
konkrete Code-Schwächen; **nicht** den bislang ungeklärten Gerätezustand.

## Änderungen und betroffene Dateien

| Datei unter `src/plugin.video.xtreammate/` | Änderung / Zweck |
|---|---|
| `default.py` | INFO-Marker ENTRY, Main-Import, Router-Konstruktion, Dispatch; Fehlerkennung START_FAILED; kontrollierter Directory-Abschluss, nicht modale Benachrichtigung. Keine Traceback-Quellzeilen/Exception-Nachricht. |
| `resources/lib/boot_diagnostics.py` (neu) | Kleiner Tracer ohne Profil/DB/HTTP; monotone Phasenlaufzeiten und feste Phase-/Aktions-/Fehler-Positivlisten; aufrufbezogener, idempotenter Directory-Abschluss. Keine globale Kodi-Moduländerung. |
| `resources/lib/main.py` | Aktion vor Portalimport protokollieren; Migration aus Dispatch entfernen; Root sofort lokal aufbauen. Leeres Profil zeigt Assistent und explizite Legacy-Übernahme als Einträge. Setup-Directory vor Modalaufruf abschließen. Bestehende Aktionen erhalten. Unbenutzten globalen ThreadPool-Import entfernen. |
| `resources/lib/home_menu.py` | HOME_MENU-Phasen und aufrufbezogener Directory-Abschluss für Home/Settings. Sechs Bestandsmenüeinträge unverändert. |
| `resources/lib/app_routes.py` | Gemeinsamer Directory-Abschluss der additiven Routen; ausschließlich Widget-Reader mit 50 ms Busy-Timeout und 350 ms SQL-Zeitbudget pro Abfrage. |
| `resources/lib/library_index.py` | Optionale Reader-Budgets via SQLite-Progress-Handler; Fehler ist `IndexReadError`, kein stilles Ergebnis mit null Treffern. Andere Reader behalten ihre bisherige Laufzeitregelung. Keine Schema-/Datenmigration. |
| `resources/lib/portals.py` | PORTALS_LOAD-Phasen; lokale nicht blockierende Öffnung, reguläre Datei, maximal 4 MiB Konfiguration; Liste und Portal-Grundstruktur validieren. Nur tatsächlich fehlende Datei ergibt neues Profil. Defekt, Zugriffsfehler, Verzeichnis/FIFO/dangling Symlink ergeben Fehler und bleiben erhalten. |
| `resources/lib/utils.py` | HTTP-Backend erst bei echter HTTP-Anfrage importieren; Standardprofil lokal anlegen, nur wenn es fehlt, ohne wiederholtes VFS-mkdir. Cachewahl/Transportregeln bleiben bestehen. |
| `resources/lib/epg.py` | Importsperre höchstens 100 ms abwarten, zweiten Job mit REFRESH_BUSY beenden; Kodi-Abbruch an bestehenden Xtream-Importer weiterreichen. |
| `resources/lib/stream_epg.py` | Abbruch-Callback bis zum HTTP-Streaming weiterreichen. Keine neue EPG-Funktion/Quelle. |
| `addon.xml`, `changelog.txt` | Eindeutiger Kandidat 0.1.28.1 mit deutschem Changelog. Builder unterstützt bereits vierteilige Versionen. |

Tests: neue `tests/test_xcmate_0281_boot.py`; bestehende Branding-/Layout-Versionsprüfungen
auf 0.1.28.1, Branding-Fehlerprüfung auf credential-sichere Kennung umgestellt;
HTTP-Test löst das nun verzögerte Backend ausdrücklich auf; zwei XMLTV-Testtransporte
akzeptieren den zusätzlichen Abbruch-Parameter. Keine Prüfung deaktiviert oder übersprungen.
Dokumentations-/ZIP-Dateien sind im PR-Diff zusätzlich ausgewiesen.

## Datenintegrität und Freeze

Kein Cache-Reset, keine DB-Löschung, keine Profil-Neuanlage im Bestandsprofil, keine
neuen globalen Keymaps oder Skin-/BINGIE-Änderungen. Root liest nur die Portalliste und
UI-Einstellungen. Automatische Jobs und Widget-Aufrufe schreiben keine Portal-Migration.
Legacy-Übernahme ist bewusst vom Nutzer auszulösen; die bestehende Migration ist bei
vorhandener Portalliste weiterhin idempotent. Ein beschädigtes Profil führt zu einem
sichtbaren Startfehler, niemals still zum leeren Einrichtungsprofil.

Eingefrorene Dateien `live_overlay.py`, `live_recovery.py`, `remote_profiles.py`,
`remote_control.py`, `remote_bridge.py`, `player.py` bleiben bytegleich zur veröffentlichten
Basis. Sieben Start-/Playback-Methoden in `main.py` bleiben AST-gleich zu 0.1.28;
bestehende 0.1.26/0.1.27-Freeze-Regressionen bleiben aktiv. Auch `preplay.py`,
`play_intent.py`, Startpräferenzen, EPG-Konfiguration/Zuordnung, Favoriten und Resume-
Implementierung sind unverändert. Andere Add-ons und der produktive Index bleiben unangetastet.

Die 4-MiB-Grenze gilt nur für die kleine **Portal-Konfigurationsdatei**, nicht für
Sender-/Medien-/EPG-Kataloge. Überschreitung verändert keine Datei. Widget-SQL-Abbruch
ändert keine publizierte Datenbank und kann bei sehr großen Katalogen einen erneuten
Widget-Aufruf erfordern; er liefert keine irreführenden Erfolgstreffer.

## Tests, Paket und Freigabe

**399/399 vollständige Tests bestanden**, 0 Fehler, 0 übersprungen, **55,611 s** im
isolierten offiziellen Build. Darunter **18 neue Start-Regressionen**; separat 18/18 in
0,846 s. Zusätzlich **26/26 HTTP-/EPG-Tests in 1,095 s** mit installiertem httpx 0.28.1,
beide HTTP-Backends geprüft. Auch die großen vorhandenen Streamingfälle (200.005
Titel je Medienart, >80 MiB HTTP/XMLTV, >64 MiB SQLite) und Remote-Freeze-Tests bleiben aktiv.
Ein früher Zwischenlauf ergab 398/398 vor dem zusätzlichen Migrationsfall; maßgeblich
ist der abschließende Lauf mit 399. Kein behaupteter Android-Laufzeitwert.

Offizieller Builder einschließlich Bootstrap-/Upgrade-Noops, Python-Syntaxcheck,
drei ZIP-Manifeste/CRC, Repository-Installerkopien und Index-MD5 in einer **Wegwerfkopie**
geprüft. Nur das neue XCMate-ZIP und dessen SHA-Datei in den Arbeitsbranch übernommen.
**53 produktive Dateien** (Index, veröffentlichtes 0.1.28-Paket, andere Add-ons/Installer)
gegen `63b4cd6` bytegleich geprüft. Alle **107 Dateien** im Kandidaten-ZIP stimmen einzeln
mit dem aktuellen XCMate-Quellbaum überein.

[Test-ZIP 0.1.28.1](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.28.1.zip)
· [SHA-Datei](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.28.1.zip.sha256),
**338.115 Bytes**, SHA256:

```text
0d82fba50c26f4139126c2c4aff28b71d19f92dcd1bb547494afc9e3cc642036
```

[Draft-PR #39](https://github.com/artattakk-creator/kodi-noodleprivate/pull/39).
**[CI erfolgreich](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39416216202)** auf `fcf3fac`
(Anwendung/Tests unverändert gegenüber Codecommit `45d4eae`). Build, Syntax, Suite und
Artefakt-Upload erfolgreich; **Produktiv-Publish-Schritt übersprungen**. Auch der frühere
Code-Lauf `39416120636` ist erfolgreich. Nachweis über Run-/Job-/Schrittmetadaten;
kein separat aus CI-Logs extrahierter Testzähler behauptet.
[CI-Reviewartefakt `xcmate-review-39`](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39416216202/artifacts/12261762240), ID `12261762240`,
324.855 Bytes, Ablauf 03.11.2026 11:38 UTC. Download des CI-ZIP über die Cloud-API nicht
verfügbar; dessen Bytes daher nicht zusätzlich geprüft. Das dauerhaft im PR-Branch
liegende lokale Kandidaten-ZIP wurde vollständig gegen den Quellcode geprüft.
Die abschließende Dokumentationsänderung verändert keine Anwendung oder Tests;
aktuelle Checks des PR bleiben die maßgebliche Anzeige des letzten Commitstands.
CI erstellt eine eigene ZIP mit eigener SHA (ZIP-Zeitstempel können abweichen).
**Kein Main-Merge, kein Release, produktiver Index weiterhin 0.1.28.**

## Verbleibende Risiken

Der native Android-Hänger ist offen, bis ein instrumentierter Gerätetest den Stand
bestätigt oder eine konkrete blockierende Phase zeigt. Python kann einen blockierten
nativen Kodi-/OS-Dateiaufruf nicht sicher durch einen Thread-Timeout abbrechen. Dieser
Hotfix installiert absichtlich keinen Watchdog, der Kodi-GUI/Directory-Aufrufe aus einem
fremden Thread tätigt. Es gibt deshalb **keine behauptete harte Gesamtlaufzeitgarantie**
bei einem defekten Kodi-/Dateisystemaufruf. Phasenmarker grenzen solche Fälle ein.

350 ms begrenzen einzelne Widget-SQL-Abfragen, nicht den gesamten Widget-Aufruf oder
lokale Artwork-/EPG-Dateileser. Root greift darauf nicht zu. Bei gleichzeitigen Widgets
können INFO-Zeilen verschiedener Kodi-Interpreter ineinanderlaufen; anhand Kodis
Invoker-/Thread-Zeitstempeln korrelieren. Keine Zugangsdaten/Portalnamen/-IDs protokollieren.

EPG-Abbruch wird zwischen Parsing-/Transport-Chunks geprüft; ein bereits laufender
Socket-Read kann bis zum vorhandenen 15-s-Timeout warten. Bestehende M3U-/Stalker-
Downloads werden hier nicht umgebaut. Der normale Servicepfad bleibt unverändert,
Katalogjobs behalten ihre bestehenden Lease-/Abbruch-/Batch-Mechanismen.
Eine vollständige Worker-Shutdown-Garantie innerhalb fünf Sekunden wird nicht behauptet.

Darstellung, Theme-/Sprachinstaller und übrige Features aus [Issue #37](https://github.com/artattakk-creator/kodi-noodleprivate/issues/37)
bleiben zurückgestellt. Geräteabnahme muss ohne pauschale Cache-Leerung erfolgen.
