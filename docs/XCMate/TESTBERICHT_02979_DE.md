# XCMate 0.1.29.79 – Testbericht und Issue-Matrix

Stand 08.11.2026. Draft-PR: https://github.com/artattakk-creator/kodi-noodleprivate/pull/388
Source-Basis main .78: `3b2a52859feda4d9413231bb4d3cf4121b1f1d67`.
Produktänderungen bis `e47479846a133a6252b2f9e4e644705bf7df8fc4` plus abschließende einheitliche Directory-Korrelation; native Testharness-Ergänzung: `4d9e8733db2caba8eb8b931197c3d81222736bf4`.

## Paket

`docs/XCMate/test-builds/02979/plugin.video.xtreammate-0.1.29.79.zip`

SHA256: `a44d60b226375beb85adffe2d8bea8f793a9f5cbe7724322146f1de11e0dabb1`

3.460.011 Bytes, 749 Source-Dateien. Deterministische ZIP-Metadaten, CRC und vollständige Source-Parität geprüft. Kein Profil, Token, Log oder SQLite-Datenbestand im ZIP. Build: `python tools/package_xcmate71.py <Ausgabeordner>`. Build aus finalem Source erneut mit kanonischem Paket vergleichen.

## Automatisierte Prüfung

- Vollständige lokale Suite vor der letzten reinen Korrelationscode-Korrektur: **3.213 Tests, 530,807 Sekunden, OK**; finaler Lauf mit zusätzlichem Korrelationsfall läuft. Vorhandene .78-Testmethoden/Skip-Inventar erhalten; 31 zusätzliche .79-Fälle.
- Finale .79-Fokusprüfung: 31 Tests, OK (Cache, Runtime, EPG, Schema, kumulativer Bestandsschutz).
- Bestehende Branding-pytests: 11 PASS. Eine externe pytest/anyio-Deprecation-Warnung, kein Produktfehler.
- Echte temporäre HTTP-/SMB-/SQLite-Dateisystemtests laufen getrennt von tatsächlichen Android-Gerätetests. Kodi-21.2-/21.3-API-Labels in Unit-Stubs sind keine nativen Android-Binärtests.

- Native Kodi 21.2 / BINGIE MOD 2.2.3: **720p und 1080p PASS**, je 31 Layout-/Fokusfälle, 20 native Navigationsaktionen, zwei tatsächliche Prozessneustarts bei abgeschalteter HTTPS-Bildquelle. Danach jeweils 88/24/24 Einträge; Film-/Serienbilder durch reale Screenshot-Pixel und SHA256 geprüft, 34 geschützte Profil-/Skin-Dateien unverändert.
- Kontrollierte Sendungsbilder: je zwei Ereignisse mit vollständigem Decode und tatsächlichen Hero-/Detailpixeln. Synthetische Bilder, keine Aussage über die passende echte Android-Sendung.
- Native Linux-Wiedergabe: **60 Stop-/ACK-Zyklen PASS**, 20 je Live-TV/Film/Serie; tatsächlicher Decoder und eigener Stream. Kein Nachweis für Rockchip-MediaCodec oder Android-Vollbild-Rückkehr.
- 17 Kodi-PO-Kataloge validiert; Python-Kompilierung bestanden.
- Paket aus unverändertem Produkt-Source erneut gebaut: **byteidentisch**, SHA256/ZIP-CRC/749-Dateien-Parität PASS.
- GitHub-CI: finaler Commit in Prüfung; Run-IDs und Ergebnisse nach Abschluss ergänzen. Ein vorheriger 1080p-CI-Zweitneustart schlug fehl, obwohl beide lokalen Auflösungen bestanden. Die genaue Ursache dieses einzelnen Fehllaufs ist nicht abschließend belegt; zusätzliche Zweitneustart-/Traceback-Artefakte sind ergänzt. Der erste Fehllauf wird ausdrücklich nicht als PASS gezählt.

Reproduktion der Hostsuite: `PYTHONPATH=<Pillow/impacket/simpleeval-Abhängigkeiten> SQLITE_TMPDIR=/tmp python -m unittest discover -s tests -v`. Native Tests: `python tools/run_kodi_home75_contract.py --report-dir <Ordner> --resolution 1280x720` beziehungsweise `1920x1080`; `python tools/run_kodi_media77_contract.py --report-dir <Ordner>`. Die Tests benötigen Docker, einen isolierten X11/Kodi-Prozess und die unveränderte, SHA-geprüfte Skin-Quelle; sie verbinden sich mit keinem Benutzergerät.

## Messwerte und Vergleichsgrenzen

| Prüfung | .78 Befund | .79 Host-/Native-Ergebnis |
|---|---|---|
| Neustart-Cover | Android-Read teils 24 Platzhalter; keine dauerhaft sichtbare Textur bestätigt | Zwei echte Linux-Neustarts je Auflösung, Quelle offline, beide Cover sichtbar und hashgleich |
| Native Home-Consumer | NATIVE_HOME_EMPTY trotz SKIN_FILES_VERIFIED; decode_verified=-1 | Tatsächliches Directory-Generation-ACK bei 88/24/24 Einträgen; Sichtbarkeit separat an Pixeln geprüft |
| Fehlendes EPG bei Fokuswechsel | Wiederholte Reads, keine eindeutige Zahl betroffener Sender | Kanalbezogene Backoff-Lease 15/30/60 Sekunden, Revision invalidiert; keine GUI-Netzwerkabfrage |
| Kontrollierter Screenshot 720p | Kein vergleichbarer .78-ARM32-Zeitwert | 31 Fälle: 1.966–3.117 ms, Median 2.799 ms |
| Kontrollierter Screenshot 1080p | Kein vergleichbarer .78-ARM32-Zeitwert | 31 Fälle: 1.977–3.342 ms, Median 3.148 ms |

Die Screenshotzeiten enthalten absichtliches Warten auf stabile Fades; dies sind **keine Android-Startzeiten** und kein belastbarer .78/.79-Geschwindigkeitsvergleich. Rohbelege: `test-builds/02979/evidence/`, inklusive vollständiger Host-Ausgabe und beider Neustartberichte.

## Ursachen und Grenzen der Nachweise

Die erste native Cacheprüfung fand den realen Kodi-URL-Schlüssel mit kleingeschriebener Prozentkodierung einschließlich HTTP-Optionen. Dafür besteht ein neuer Regressionstest. Ein früher Testaufbau wartete ausschließlich auf eine entfernte URL, obwohl der Hintergrundworker sie bereits erfolgreich durch die überprüfte lokale Textur ersetzt hatte; die Prüfung akzeptiert nun genau diese quellengleiche lokale Datei und verlangt weiterhin passende tatsächliche Pixel. Für echte Kaltstarts stoppt der isolierte Skript-Worker wie der Produktdienst. Ein weiterer früher Screenshot traf den abblendenden BINGIE-Start-Splash; der endgültige Test wartet auf dessen Schließen und prüft danach die unveränderten erwarteten Farbwerte. Diese vorläufigen Fehlläufe werden nicht als erfolgreiche Neustartprüfungen gezählt.

Die neuen GUI-Diagnosen unterscheiden SOURCE/DIRECTORY/CONSUMER/ACK/ACTIVE/TEXTURE_REQUESTED. `TEXTURE_VISIBLE` wird durch Bindings oder Zählwerte niemals künstlich bestätigt. Tatsächliche Linux-Pixel sind ein eigener Nachweis; das gleiche gilt auf Android erst nach Geräteprüfung. Öffentliche Bildadressen allein sind kein Bild-PASS.

## Issue-Abnahmematrix

| Bereich / Referenz | .79 Implementierung | Nachweis / verbleibend |
|---|---|---|
| Native Home-Consumer, #387/#385/#367 | Erneute Bekanntmachung unveränderter normaler und paginierter Frames, kontrollierte Hook-Aktivierung, korrelierte Directory-Generation, begrenzte Wiederholungen | Hosttests; echte Android-Controls und Darstellung ANDROID_NOT_TESTED |
| Persönliche Reihen / „Neu im Kino“ | Gespeicherte SkinShortcuts/Pfade read-only inventarisiert; keine Defaults/Reihen ersetzt | Host-Dateihashes und native Fremdreihen; konkrete Android-Kinoquelle weiterhin zu prüfen |
| Film-/Seriencover, #387 | Exakte Wiederauffindung vorhandener Kodi-Thumbnails; positive Decode-/Hash-/Dateistempel-Belege, private begrenzte Journaldatei, keine globale Löschung | Native Neustart-/Offline-Pixelprüfung; Android zwei Neustarts ANDROID_NOT_TESTED |
| EPG-Mapping / Polls | Explizite Provider/XMLTV-IDs; manuelle Mappings exklusiv; senderbezogene negative Backoff-Leases | Hosttests; tatsächliche Providerzuordnung und Latenz auf Android ANDROID_NOT_TESTED |
| Programmbilder, #366/#380 | Bestehende gemeinsame Ereignis-/Sicherheits-/Decode-/Lease-Kette erhalten und regressionsgeprüft | Synthetische reale Kodi-Hero-/Detailpixel; passende echte Sendungsbilder in Mini-/Groß-EPG ANDROID_NOT_TESTED |
| MyVideos131.db | Lesende Schema-/Integritäts-/Query-Diagnose erweitert | Fehlende Views und genaue Android-Ursache **OFFEN**; keine Migration oder DB-Schreiboperation |
| Navigation und Player-Exit, #368 | Produktpfade aus .78 erhalten; Regressionen erneut geprüft | Synthetische native Stop-ACK-Zyklen; RK3528/MediaCodec/Autoplay/Back ANDROID_NOT_TESTED |
| TMDB-Token / Installer | Tokenverwaltung unverändert; Installer 0.5.26 byteidentisch | Baseline-/Datenschutz-/Bestandsschutztests; Gerätebestand zusätzlich prüfen |

Keines der referenzierten P0-Issues wird auf Basis der Hosttests geschlossen. Historische .78-Android-Fehler bleiben FAIL; alle neuen .79-Android-Gates sind ANDROID_NOT_TESTED.

## Auslieferungsstand

Nur Source-Branch/Draft-PR und manuelles Test-ZIP. Kein Merge-Commit, keine reguläre/Pilot-/NeoDark3-Veröffentlichung. Veröffentlicht bleibt .78. Installer 0.5.26 unverändert. Weitere Schritte: Android-Abnahme gemäß `ANDROID_ABNAHME_02979_DE.md`, danach ausdrückliche Merge-/Veröffentlichungsfreigabe.
