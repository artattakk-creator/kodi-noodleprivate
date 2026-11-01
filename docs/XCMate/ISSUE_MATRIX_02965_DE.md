# XCMate .65 – Abnahmematrix

| Referenz | Code / automatisierter Nachweis | Reales Gerät |
|---|---|---|
| #297 / #292 | Kodi-Profilanker, privater PRE_READ/Initialisierung, Subcodes, explizite konservierende Recovery; Syntaxfixtures/Negativtests | ANDROID_NOT_TESTED; .64-Zielfehler OPEN |
| #298 P0-B / #257 | Dauerhafte Queue, Lease/Crash/Retry, Kategorie-ID-Scope, Generation-/Legacy-Schutz, sichtbarer Gruppenstatus, gezielter Nachimport, Paging bis >1000 in Film/Serie | ANDROID_NOT_TESTED; echter Adult-Zone-Providercount unbekannt |
| #291 / #298 P0-C | RAM-first Home, gepinnter Textread vor Metadaten, kein Vollreload bei Master-Contention; SQL-/Timingvergleich | ANDROID_NOT_TESTED; sichtbares 1-s-Ziel OPEN |
| #295 / #293 / #284 | bisherige native Fokus-/Poster-/Hero-/Live-Strecken plus vollständiger Regressionstest | ANDROID_NOT_TESTED |
| Portale, Passwörter, Widgets, EPG/Mappings, .42-Live-Back, Autoplay, Resume, Cover und Box A | Schutzinventar, bestehende Methoden und Regression | Keine Fernänderung, Android-Bestandsschutz offen |

HOST_PASS wird erst nach endgültigem grünem CI eingetragen bzw. über PR/CI belegt. ANDROID_PASS darf ausschließlich nach realer Nutzerabnahme erscheinen. Technisch freigegebener Merge/Publish gemäß #298 schließt diese Fehler-Issues nicht automatisch.
