# XCMate 0.1.29.95 – Prüfstand

Draft-PR #465, Master #464. Installierbarer Testkandidat, keine Android-Abnahme, kein Merge und keine Repository-Veröffentlichung.

## Paket

- Datei: `../test-builds/02995/plugin.video.xtreammate-0.1.29.95.zip`
- SHA256: `7a4a1ed71ebff1d02c562983f2944104ea3d0d6402f7ce62c13fce243986a2d7`
- Größe: 4.734.625 Bytes, 886 Dateien.
- Rebuild-Bytegleichheit, ZIP-CRC, vollständige Mitgliederliste, jeder Source-Bytevergleich und Manifest .95: PASS.
- .94-Pilot-ZIP und .90-Fallback unverändert; Veröffentlichungskanäle gegen `459817b4` geschützt.

## Bereits abgeschlossene Prüfungen

| Prüfung | Ergebnis / Beleg |
|---|---|
| Ursprüngliche .94-Reproduktion: >50 ms Zugriff und >128 Verzeichniseinträge | 2 reproduzierbare FAIL vor Reparatur; beide danach PASS |
| Neue .95-Funktionstests | 34/34 PASS, echte synthetische SQLite-/WAL-/flock-Dateien, 3,613 s |
| Release-/Delta-/historische Paket-/Sprach-/Boot-/neue .95-Tests | 113/113 PASS, 44,423 s |
| Sprache | 17 PO-Kataloge PASS; neue Gate-/Profiltexte DE/EN mit vorhandenem Englisch-Fallback |
| Host-Zwei-Quellen-Pipeline | Echter Import, Sicherung, Gate READY, akzeptierter Folgeauftrag und unabhängiges Readback PASS; kein realer EPGShare-Endpunkttest |
| Abbruch / Offline / manipulierte Sicherung / veränderte DB | PASS, LastGood erhalten bzw. neue Freigabe korrekt verweigert |
| Guide-/WAL-/Backup-Erhalt bei lesender Prüfung | PASS; SQLite-SHM-Lesermarken sind kein unveränderlicher Dateisnapshot |
| Automatische Wartung .95 | Aktiver Guide und Backups geschützt, PASS |
| Physische Android-Box B, DE+AT | ANDROID_NOT_TESTED |

Vollständiger abschließender Host-/pytest-Lauf sowie native Kodi-Prüfungen des letzten Source-Commits laufen. Deren Ergebnisse und CI-Links werden vor der Übergabe ergänzt. Keine noch laufende Prüfung gilt als PASS.

## Zwischenläufe und korrigierte Prüfumgebung

- Ein erster Gesamtlauf ohne Sandbox-Netzfreigabe konnte lokale HTTP-/SMB-Testserver nicht öffnen (`PermissionError`). Diese Umgebungsfehler sind keine Reparaturen oder bestandenen Netzwerktests; der vollständige Lauf wird mit erlaubten lokalen Sockets wiederholt.
- Im anschließenden älteren Source-Lauf wurden vier tatsächliche Testvertragsabweichungen sichtbar: zwei eingefrorene Kanalschutztests mit Stand vor der separat veröffentlichten .94, ein neuer nicht lokalisierter Profilhinweis und eine neue private Proof-Sidecar im Boot-Dateierhaltstest. Kanalschutz bezieht sich jetzt auf die unveränderte aktuelle main-Basis; neue Hinweise stehen in den zentralen Sprachressourcen. Original-Profildateien bleiben bytegleich. Diese Punkte sind im 113er-Prüflauf bestanden.
- Ein nativer Widget-Prüfer verwendete noch den .94-Manifestprüfer für ein .95-ZIP; auf den tatsächlichen .95-Prüfer korrigiert. Kein Produktverhalten für diesen Harnessfehler geändert.

## Offene Freigabepunkte

Alle Schritte der `ANDROID_ABNAHME_DE.md` bleiben ANDROID_NOT_TESTED. Öffentliche EPGShare-DE/AT-Erreichbarkeit, RK3528-Speicherlatenz, echte Guide-Größe und gleichzeitige Kodi-Menüs müssen auf Box B geprüft werden. P1-Artwork-/andere EPG-Lesebudgets und native MediaCodec-Probleme sind separat offen. Keine Datenlöschung oder Rückinstallation als Testmaßnahme.
