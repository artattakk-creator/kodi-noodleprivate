# XCMate .64 – Testbericht

Verbindlicher Abschlussnachweis: grüner CI-Lauf am exakten aktuellen HEAD von Draft-PR #296, vollständiger Testlog, Build-Verifikation, ZIP/SHA256 und native JSON-/PNG-Artefakte. Ein früherer Zwischenlauf ist kein fertiger Kandidat.

- Baseline: alle 638 .63-Quelldateien und alle 2.593 vorhandenen Methoden samt Skip-Bedingungen erhalten. Nur vollständige exakt hinterlegte .64-Deltas dürfen normalisiert werden. Keine Grenzwerte alter Tests erhöht.
- Neue Tokenfälle: reale synthetische private Datei, 0600, EROFS/EACCES/EINVAL/ENOTSUP/EIO, file-fsync, rename, Directory-fsync nach Commit, fehlerhafter Readback, Symlink, Profilwechsel, sichere UI und Log-Redaktion.
- EPG: echte gespeicherte DMAX-Testzeile, RAM-Verdrängung ohne GUI-SQL/HTTP, Profil-/Revisions-/Zeitprüfung, Fokuspriorität ohne Verhungern der Startgruppe.
- Serien: getrennte freigegebene Provider-Assetdatei im gemeinsamen Index, leerer Altcache, Signatur-/Referenzwechsel ohne Metadatenänderung, keine TTL-Verlängerung, getrennte Diagnosen. Kein TMDB/TVmaze.
- Layout: bekannte .63→.64-Transaktion nur mit Bestätigung, exakt reversible Sicherungen, unbekannte Skins blockiert, LiveRow mit unveränderter Geometrie; ausschließlich der inaktive Fokusrahmen wird ausgeblendet, originale Grafik unverändert.
- Native Kodi21.2/Linux+BINGIE2.2.3: alle bisherigen sechs Strecken plus neue .64-Strecke mit EnableFixedFrameWidgets und LockHubWidgets, echte eigene Fokus-/Selected-IDs, aktive Rahmenbounds/Pixels, erste zehn Serienposter, erste/mittlere Filmkachel, Rückkehr zu Live. Synthetische Providerbilder, keine Userdaten.
- Paket: vollständige Quell-/Assetdateien, ZIP-CRC, eindeutige sichere Pfade, Manifest/Version, PO/Icon/Python und SHA256 geprüft. Produktionspublish im PR SKIPPED.

Die verwaltete Umgebung scheiterte beim Start; Tests laufen in Actions. Externe Native-Helfer sind isoliert. Keine Android-/Nutzertoken-Abnahme; B64-01 bis B64-12 bleiben ANDROID_NOT_TESTED. Die Originalfotos sind in diesem Ausführungskontext nicht vorhanden. Geräteursache und technische Reproduktion werden nicht gleichgesetzt.

[Ursachen](URSACHEN_02964_DE.md) · [Android-Plan](ANDROID_ABNAHME_02964_DE.md) · [Issue-Matrix](ISSUE_MATRIX_02964_DE.md)
