# XCMate 0.1.29.85 – Testbericht

**Entwicklungsstand, kein Release.** Dieser Bericht wird nach den laufenden vollständigen Prüfungen mit den endgültigen Ergebnissen, CI-Links und dem reproduzierten ZIP-Hash ergänzt. Android Box B: durchgehend `ANDROID_NOT_TESTED`.

## Getrennte Prüfumfänge

A: Neuer eigener begrenzter Tempcache, Objekt-/Byte-Limits, LRU/TTL, aktive Pins, Integrität, Journal-Wiederaufnahme, Symlinks, fremde Dateien, Reservesperre ohne Allokation, semantische Widgetgeneration, Ladezustände und begrenzte Revisionsbehandlung.

B: Ghosts UK/USA, Werkjahr/Land, drei Suchseiten, unvollständige Trefferlisten, offizielle Alternativtitel, M*A*S*H-Kanonisierung, Filmabgrenzung, korrigierbare dauerhafte Nutzerzuordnung, Profil-/Portal-/Quellenisolation, Persistenzfehler, Kontextmenü, Abbrechen/Bestätigen, nachträgliche Kandidatenposter.

## Bisherige ausgeführte Prüfungen

- Neue gezielte A/B-/Grenzfalltests und Schutzprüfungen: 59 PASS im Lauf vor der vollständigen Regression. Weitere endgültige Laufzahlen folgen unten.
- Zusätzliche bestehende Branding-Pytests: 11 PASS.
- PO-Validierung: alle 17 Kodi-Sprachkataloge PASS; neue Cache-/Vorschlagseinstellungen Deutsch/Englisch, bestehender Fallback unverändert.
- Python-Kompilierung: PASS.
- Vollständiger erster Hostlauf: Fehler gefunden, kein Gesamt-PASS. TVMaze-Sicherheits-/Legacy-Verhalten, präzisierte Revisionszustände, fehlender Readonly-Frame und Native-Dialog-Vertrag werden nachgeprüft. Der große 200.005-Titel-HTTP-Test stößt lokal auf `sqlite3.OperationalError: database or disk is full`; der betroffene Katalog-Lesecode ist gegenüber .84 unverändert. Ursache/CI-Ergebnis getrennt dokumentieren, keinen Test stillschweigend auslassen.
- Native Linux-Kodi-Prüfungen: vorbereitet für 1080p/720p, echte Textur-/Pixelprüfung mit synthetischem HTTPS-Ursprung, frischem Profil und zwei Offline-Neustarts. Zusätzlich .85-Kandidatendialog, Bestätigen/Back und sichtbare Vorschlagskennzeichnung. Ergebnisse erst nach echtem Lauf eintragen. Keine Aussage über Android-Pixel.

## Reproduzieren

```sh
python -m pip install 'Pillow>=11,<13' 'impacket==0.13.0' 'simpleeval==0.9.13' 'pytest>=8,<10'
python -m unittest discover -s tests -v
python -m pytest -q tests/test_xcmate_bingie_branding.py
python tools/validate_kodi_po.py
python tools/package_xcmate71.py /tmp/xcmate85-build
python tools/release_channel75.py
```

Native Disposable-Linux-Gates:

```sh
python tools/run_kodi_home85_contract.py --report-dir /tmp/native85 --resolution 1920x1080
python tools/run_kodi_home85_contract.py --report-dir /tmp/native85-720 --resolution 1280x720
python tools/run_kodi_home82_contract.py --report-dir /tmp/reg85-720 --resolution 1280x720 --fault-idle-seconds 1800
python tools/run_kodi_media77_contract.py --report-dir /tmp/media85
```

Keine dieser Anweisungen installiert etwas auf Box A oder Box B. Native Tests nutzen ausschließlich entbehrliche Linux-Container/Fixtures. Private Endpunkte, Providerzugänge und der reale TMDB-Token werden nicht benötigt.

## Offene Hardware-Gates

Siehe `ANDROID_ABNAHME_02985_DE.md`. Die echten 27-MiB-/FUSE-/Reservebedingungen, richtige Bilder konkreter echter Sendungen, reale Fernbedienung, Neustartpersistenz und Geschwindigkeit müssen auf Box B geprüft werden. Ein erfolgreicher Hosttest genügt dafür nicht.
