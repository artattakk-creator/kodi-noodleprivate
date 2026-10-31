# XCMate .64 – Issue-/Abnahmematrix

| Auftrag | Umsetzung / technischer Nachweis | Geräteergebnis |
|---|---|---|
| #295 P0-A Fokus | eigener lokaler Rahmen statt absolutem Globalrahmen bei eigenen Medien; native Reihenwechsel und Bounds/Pixels | ANDROID_NOT_TESTED |
| #295 P0-B Serien | gemeinsamer Provider-Assetrenderer auch bei Veröffentlichung, aktualisierte Signaturen; erste zehn Poster im nativen Fixture | ANDROID_NOT_TESTED |
| #295 P0-C / #291 | gültiger Zeilenfallback, unveränderte Quellenprüfung, begrenzter Fokus-Prefetch, keine GUI-IO | ANDROID_NOT_TESTED |
| #295 P0-D / #293 / #284 | Full-bleed, Langtitel, originales Space-Fallback, LiveRow erhalten, bekanntes Layout mit Diff/Backup/Restore | ANDROID_NOT_TESTED |
| #295 P0-E / #292 | stufenweiser privater Import, sicherer atomarer Commit, Readback/Syncwarnung, echte Authentifizierung getrennt | ANDROID_NOT_TESTED |
| #286 / #288 | vorhandene Menüs, sichere Zurück-Aktion und gespeicherte Quellen erhalten | ANDROID_NOT_TESTED |
| Live/.42, Filme, Serien/Autoplay/Resume, Portale, EPG, Icon, Daten | 638-Dateien-/2.593-Methoden-Bestandsschutz plus vollständige Regression | ANDROID_NOT_TESTED |

Historische .63-Fails B63-03/B63-11/B63-12 bleiben bestehen, bis die echten Geräteprüfungen sie widerlegen. Keine Issue-Schließung durch Host-PASS. Exakter HEAD, abschließende Testzahlen, Artefakte und SHA256 stehen im Abschlusskommentar von Draft-PR #296. Kein Merge/Release, kein Eingriff in Box A.
