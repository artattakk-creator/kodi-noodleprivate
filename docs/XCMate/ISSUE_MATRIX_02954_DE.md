# XCMate .54 – Issue-/Freigabematrix

| Issue / Anforderung | Code und Host | Android / Freigabe |
|---|---|---|
| #263 Portal vor EPG | GETRENNTE PHASEN, geprüfter Katalog, idempotentes Save, EPG-Fehler löscht kein Portal; Host PASS | CAT54-05/06, EPG54-01–04 NOT_TESTED |
| #263 Gruppencheckpoint | 45/883, PARTIAL/COMPLETE, echte Generation/Count/SHA, Integritäts-/Altersprüfung, keine DB-Neulöschung; eigene .53-Heads geprüft übernehmbar | CAT54-01–04 NOT_TESTED |
| #263 Quellencheckpoint | einzelne vollständige Publishs/Belege, Resume nur fehlender Quellen, Source-/Mapping-/Katalogfingerprint, eigene Crashgeneration und native Lease | EPG54-01/03/04/06 NOT_TESTED |
| #263 Laufzeit | keine feste aktive Gesamtdauer; Requesttimeout/Cancel/Cleanup erhalten; echte virtuelle >5-/20-min-Nachweise | EPG54-02 NOT_TESTED, reale ARM32-Langlaufabnahme offen |
| #255 Verbindung/Passwort | echter Auth-Erfolg, automatische Kategorien, DNS/TLS/HTTP/Auth/Timeout unterschieden; RAM-Passwort neu anzeigen/editieren, vorhandenes nie offen; keine ungeschützte Secret-Recovery | AUTH54-01–04 NOT_TESTED; Interpretergrenze dokumentiert |
| #262 Fortschritt/Layout | reale Bytes/Events/Groups/Quellen, coalesced Owner-Pump, größere Schrift und disjunkte Reiter/Zähler/Liste | UI54-01 / EPG54-01 NOT_TESTED |
| #262 Slideshow | separat spezifiziert, keine genehmigten echten Assets vorhanden | BLOCKED_APPROVED_ASSETS, kein behaupteter fertiger Bildwechsel |
| #261 Fanart | Metadaten auf vorhandenen Lightweight-Splash, Original-Icon/Grafikbytes erhalten | UI54-02 NOT_TESTED, kein Texturecache-Reset |
| #259 EPG-Manager/Bestand | Manager-Resume über kontrollierte native Freigabe; kein falsches READY bei leerem/unklarem Bestand; 7/+20/LastGood/Mappings/Backup erhalten | EPG54-03–06, REG54-02 NOT_TESTED |
| #249 / #259 nativer Startcrash | Ursache mangels neuer Log-/ANR-Evidenz ungeklärt, keine spekulative Reparatur. Start-/Helper-/Ownership-Regressionsschutz im Hostlauf | BLOCKED_LOG_EVIDENCE, ST54-01 zuerst, bei FAIL andere Gates blockieren |
| Nutzer: Installationspopup | Erstinstallation und Update: Installation erfolgreich, tatsächliche Version und konkrete Änderungen; genau einmal/sicher verschoben, de/en | UPD54-01/02 NOT_TESTED |
| .53 Live/Medien/Autoplay/Suche/Widgets/Profiles | volle Regression PASS, betreffende Kerne/Grafiken/BINGIE-Writer byteidentisch, keine Geräte-/Skinaktion | REG54-01–03 NOT_TESTED, BINGIE später separat |

**Keine Issue-Schließung und kein automatischer Merge/Release.** Hostgrün ist keine Gerätefreigabe. Kein Downgrade, Reset, Neuinstallation oder Datenverlust auf Benutzergeräten. Box A unangetastet. Downloads, Aufnahme, neue BINGIE-/Hero-Skinintegration und externe Speichermigration nicht in diesem Auftrag.
