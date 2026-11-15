# XCMate 0.1.29.95 – Prüfstand

Draft-PR #465, Master #464. Installierbarer Testkandidat, keine Android-Abnahme, kein Merge und keine Repository-Veröffentlichung.

## Paket

- Datei: `../test-builds/02995/plugin.video.xtreammate-0.1.29.95.zip`
- SHA256: `1eed4d84c1317190f1936883eee2d9393368117f5a1e84516605c8ba141beb3b`
- Größe: 4.734.921 Bytes, 886 Dateien.
- Rebuild-Bytegleichheit, ZIP-CRC, vollständige Mitgliederliste, jeder Source-Bytevergleich und Manifest .95: PASS.
- .94-Pilot-ZIP und .90-Fallback unverändert; Veröffentlichungskanäle gegen `459817b4` geschützt.

## Bereits abgeschlossene Prüfungen

| Prüfung | Ergebnis / Beleg |
|---|---|
| Ursprüngliche .94-Reproduktion: >50 ms Zugriff und >128 Verzeichniseinträge | 2 reproduzierbare FAIL vor Reparatur; beide danach PASS |
| Neue .95-Funktionstests | 36 neue gezielte Tests, alle im abschließenden 146er-Prüflauf PASS |
| Release-/Delta-/historische Paket-/Sprach-/Boot-/neue .95-Tests | 146/146 PASS, 53,859 s; einschließlich Menüicons und bestehender EPG-Manager-Regressionen |
| Sprache | 17 PO-Kataloge PASS; neue Gate-/Profiltexte DE/EN mit vorhandenem Englisch-Fallback |
| Host-Zwei-Quellen-Pipeline | Echter Import, Sicherung, Gate READY, akzeptierter Folgeauftrag und unabhängiges Readback PASS; kein realer EPGShare-Endpunkttest |
| Abbruch / Offline / manipulierte Sicherung / veränderte DB | PASS, LastGood erhalten bzw. neue Freigabe korrekt verweigert |
| Guide-/WAL-/Backup-Erhalt bei lesender Prüfung | PASS; SQLite-SHM-Lesermarken sind kein unveränderlicher Dateisnapshot |
| Automatische Wartung .95 | Aktiver Guide und Backups geschützt, PASS |
| Physische Android-Box B, DE+AT | ANDROID_NOT_TESTED |

Vollständiger abschließender Host-/pytest-Lauf sowie native Kodi-Prüfungen des letzten Source-Commits laufen. Deren Ergebnisse und CI-Links werden vor der Übergabe ergänzt. Keine noch laufende Prüfung gilt als PASS.

## Zwischenläufe und korrigierte Prüfumgebung

- Ein erster Gesamtlauf ohne Sandbox-Netzfreigabe konnte lokale HTTP-/SMB-Testserver nicht öffnen (`PermissionError`). Diese Umgebungsfehler sind keine Reparaturen oder bestandenen Netzwerktests; der vollständige Lauf wird mit erlaubten lokalen Sockets wiederholt.
- Im anschließenden älteren Source-Lauf wurden vier tatsächliche Testvertragsabweichungen sichtbar: zwei eingefrorene Kanalschutztests mit Stand vor der separat veröffentlichten .94, ein neuer nicht lokalisierter Profilhinweis und eine neue private Proof-Sidecar im Boot-Dateierhaltstest. Kanalschutz bezieht sich jetzt auf die unveränderte aktuelle main-Basis; neue Hinweise stehen in den zentralen Sprachressourcen. Original-Profildateien bleiben bytegleich. Diese Punkte sind im abschließenden 146er-Prüflauf bestanden. Zusätzlich wurden der neue Sicherungsdialog auf den vorhandenen Icon-Select-Wrapper und die bestehende Manager-Abnahme auf den nun asynchronen Auftrag umgestellt (vor Workerstart kein Request; nach Drain exakt der ausdrücklich angeforderte Request).
- Ein nativer Widget-Prüfer verwendete noch den .94-Manifestprüfer für ein .95-ZIP; auf den tatsächlichen .95-Prüfer korrigiert. Kein Produktverhalten für diesen Harnessfehler geändert.

## Zusätzliche abgesicherte Randfälle

- Gate-Ablehnung vor dem ersten Importbericht: der automatische Scheduler prüft auch den dauerhaften Refresh-Status. Vorher reproduzierbar erneuter Vorschlag, nachher begrenztes Backoff ohne neue Sicherung. Manuelle Neuprüfung bleibt möglich.
- Die Importfreigabe erhält im vorhandenen GUI-Owner-Pool ein begrenztes 35-s-Jobbudget; andere Jobs bleiben bei 4 s. Gate-Abbruch prüft Fenstergeneration, Schließen und Kodi-Ende. Test: beim Schließen während der Prüfung entsteht kein verspäteter Importauftrag.
- Hostmessung auf synthetischem Guide: bei 80 ms lokaler Verzögerung .94 BACKUP_REQUIRED nach 80,864 ms, .95 READY nach 85,418 ms. 120.000 Quellzeilen: kalte Inventur 230,169 ms, gleiche unveränderte Generation 0,041 ms. Messung auf Linux am dokumentierten Zwischencommit, keine Android-Leistungszusage; siehe HOST_MESSWERTE.json.

## Offene Freigabepunkte

Alle Schritte der `ANDROID_ABNAHME_DE.md` bleiben ANDROID_NOT_TESTED. Öffentliche EPGShare-DE/AT-Erreichbarkeit, RK3528-Speicherlatenz, echte Guide-Größe und gleichzeitige Kodi-Menüs müssen auf Box B geprüft werden. P1-Artwork-/andere EPG-Lesebudgets und native MediaCodec-Probleme sind separat offen. Keine Datenlöschung oder Rückinstallation als Testmaßnahme.
