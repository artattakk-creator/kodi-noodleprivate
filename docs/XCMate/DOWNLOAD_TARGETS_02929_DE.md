# .29-B – separate Downloadziele, USB und SMB (#136)

Basis main c17cb4f (.28). Isolierter Draft; kein Release/OTA oder main-Merge.
Redirects #135 sind ein eigener Fehler und werden in diesem Branch nicht gelöst.
Für gemeinsame Android-Abnahme den kumulativen .29-C-Teststand verwenden.

## Auswahl ohne Datenmigration

XCMate → Einstellungen → Speicher: „Downloadziel wählen: intern / USB / SMB“.
Der Kodi-Quellenbrowser zeigt konfigurierte Dateiquellen und erreichbare Volumes.
Ziel prüfen, Fähigkeiten lesen, gegebenenfalls Staging ausdrücklich erlauben und
Übernahme bestätigen. Erst danach wird das Ziel für **neue** Downloads gespeichert.
Laufende/vorhandene Aufträge behalten ihren bei Erstellung gespeicherten Zielordner.
Keine bestehenden Dateien werden verschoben oder gelöscht. Aufnahmeziel bleibt
`recordings_folder`; die neue Auswahl ist unabhängig davon.

Ohne bestätigte neue Auswahl gilt weiter das bisherige gemeinsame Aufnahmeziel.
Ein eventuell aus älteren Prototypen vorhandener, bisher ignorierter
`downloads_folder` wird nicht von selbst aktiv: erst der neue Bestätigungsmarker
aktiviert ihn. Cancel, ungeeignetes Ziel oder Netzwerkfehler bewirken keinen
internen Rückfall. SAF-`content://` ohne zugreifbaren POSIX-Mount wird erklärt
abgelehnt; Android-/Kodi-Dateifreigaben können nicht vom Addon umgangen werden.

## Nachgewiesene Verträge

| Backend | Finalisierung / Schutz | Kapazität und Wiedergabe |
| --- | --- | --- |
| NATIVE, intern oder kompatibles USB | Bestehender NoFollow/O_EXCL/Datei- und Verzeichnis-fsync/atomarer No-Replace-Vertrag unverändert | Echter Freiraum und FAT32-Limit; ohne Netz, solange Medium angeschlossen |
| LOCAL_STAGE_VERIFY, kompatibles lokales USB ohne native Atomic-/Directory-fsync-Fähigkeit | Vollständige fsync-Zwischenkopie, frischer Zielname, kernelgestütztes O_EXCL/NoFollow, Datei-fsync, Größen-/SHA256-Rücklesung. Kein Atomic-/Directory-fsync-Versprechen | Zusätzlicher interner Platz für ganze Datei; Zielplatz/FAT32 prüfen. Unterbrochene Zieldatei kann sichtbar bleiben, XCMate gibt sie nicht frei |
| SMB2_STAGE_VERIFY | Vollständige lokale Zwischenkopie; authentifiziertes signiertes SMB2, exklusives FILE_CREATE, Write-Through, Rücklese-Hash, serverseitiges Rename mit ReplaceIfExists=False, erneute Zielprüfung | Ziel-Freiraum über dieses API unbekannt, nicht erfunden. Lokaler Staging-Platz geprüft. SMB-Wiedergabe benötigt erreichbaren Server |

SMB-Ziele werden im Kodi-Browser gewählt. Der Uploadadapter nutzt eine private,
reine Python-Implementierung, da Kodi-VFS `mkdir` bereits existierende Ordner als
Erfolg behandelt und Python-File „w“ mit Overwrite öffnet. Die verifizierte
Kodi-21.2-Quelle belegt, dass daraus keine exklusive Reservierung ableitbar ist:
`xbmc/platform/posix/filesystem/SMBDirectory.cpp::Create` und
`xbmc/interfaces/legacy/File.h::File` im Tag `21.2-Omega`.

SMB-Anmeldung explizit am Gerät für genau Server/Share speichern (0600-DB).
URL-Userinfo wird vor Speicherung des Downloadziels entfernt. Bei Bedarf fordert
der Picker Benutzer/Passwort an; keine öffentlich protokollierten Credentials.
Kodi benötigt für die spätere VFS-Wiedergabe zusätzlich seine gespeicherte
Freigabe-Anmeldung. Kein Zugriff auf private Kodi-Passwortdateien, kein SMB1-/Gast-
oder unsignierter Rückfall. Unterstützter Vertrag: SMB2.002/2.1 mit NTLMv2 und
Signierung. SMB3-Verschlüsselungspflicht/Kerberos-only erfordern ein anderes
geeignetes Ziel; Sicherheitseinstellungen des Servers nicht absenken.

Vor Aktivierung: echte Testdateien erzeugen, lesen/hashen, exklusives Erzeugen
gegen Kollision und No-Replace-Rename gegen ein eigenes vorhandenes Testziel
prüfen. Das ist kein bloßer Browser-/Write-PASS. SMB-Fehler nennen technische
Kategorie und gegebenenfalls NTSTATUS im Stage-Code, keine Netzpfade oder Titel.

## Unterbrechung / Integrität

HTTP-Download und externe Übertragung sind zwei Phasen. TRANSFERRING zeigt die
kopierten Bytes separat; Pause/Cancel sind während der Kopie möglich. Vor dem
abschließenden No-Replace-Schritt erfolgt ein geschützter Zustandswechsel.
Verschwundener Worker wird PAUSED, nicht unkontrolliert neu gestartet.

Vollständige, gehashte lokale Zwischenkopie bleibt erhalten. Nach Trennung oder
Pause wird beim ausdrücklichen Retry die Kopie zum Ziel neu begonnen; es gibt kein
ungeprüftes Anhängen an fremde/unterbrochene SMB-Dateien und keinen erneuten
HTTP-Download, solange der vollständige eigene lokale Hash stimmt. Neue Zielkopien
bekommen exklusive frische Teilnamen. Teil-/Fehldateien und vorherige Zielkopien
werden nicht automatisch gelöscht. Der private Transfernachweis verfolgt ihre
Zugehörigkeit. COMPLETE erst nach passender Größe und SHA256 des wirklichen Ziels;
eigene, nachweislich abgeschlossene Rename-Fälle lassen sich nach Crash prüfen.

Lokale Zwischenkopien bleiben auch nach Abschluss zur Wiederherstellung erhalten;
vor jedem neuen Auftrag/Schreibblock werden Freiraum und Reserve geprüft. Daraus
entsteht zusätzlicher Platzbedarf, kein unbegrenztes Weiterladen bei vollem Speicher.
Die Aufnahmeengine verwendet diese Backends nicht automatisch.

Nur additive Schemaerweiterung `copy_bytes` an der bestehenden Downloadqueue;
bestehende Aufträge bleiben erhalten. Weitere kleine private Tabellen für
Staging-Freigaben, Transfernachweise und SMB-Account. Keine Portal-/EPG-/Resume-
oder Artwork-Migration. Drittanbieterherkunft und Änderungen unter
`THIRD_PARTY_SMB.txt`, auch im Lizenzdialog sichtbar. Keine Runtime-pip-Installation,
kein externer Aufnahme-/Downloadprozess im Kodi-Addon. Impacket ist ausschließlich
die isolierte Host-/CI-Testserver-Abhängigkeit und nicht im Installations-ZIP.

## Android-Abnahme – alle neuen Felder NOT_TESTED

| ID | Prüfung | Status |
| --- | --- | --- |
| ST01 | Bisheriger gemeinsamer Ordner bleibt Standard; alte Daten intakt | NOT_TESTED |
| ST02 | USB wählen, bestätigen, Neustart; Film COMPLETE und ohne Netz abspielen | NOT_TESTED |
| ST03 | SMB wählen, bestätigen, Neustart; COMPLETE und Wiedergabe über Kodi-VFS | NOT_TESTED |
| ST04 | Separates Downloadziel bei unverändertem Aufnahmeziel | NOT_TESTED |
| ST05 | FAT32 >4GiB, voll, read-only, USB entfernt, SMB offline, Kollision, SAF | NOT_TESTED |
| ST06 | Externe Kopie pausieren/fortsetzen/abbrechen und explizit Retry | NOT_TESTED |
| ST07 | SMB-Netzunterbrechung: kein falsches COMPLETE; lokaler Stage bleibt | NOT_TESTED |
| ST08 | Film und genau eine Folge im gewählten Ziel vollständig/korrekt | NOT_TESTED |

Host-/CI-Fixtures prüfen lokale Dateisysteme (USB-Eigenschaften simuliert) und
einen echten isolierten signierten SMB2-Server auf Loopback, einschließlich
Server-Abbruch/Neustart, korrupter Zielkopie und parallelen exklusiven Erzeugens.
Das ersetzt weder echten Android-USB-/FAT32-Mount noch Kodi-VFS-Gerätewiedergabe.

#131 Menü nur Teil-PASS aus .28, Gesamtprüfung offen. #126 Aufnahme, #111 Poster
und #63 komplette Downloads weiterhin echte Geräte-Gates. #43 vollständiger
Wizard und #127 Suchdarstellung bleiben Pflicht vor vollständigem RC; #120/#122/
#123/#98/#115 bleiben getrennte Folgearbeiten.
