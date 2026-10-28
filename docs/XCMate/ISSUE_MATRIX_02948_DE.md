# .48 – Fehler-, Schutz- und Abnahmematrix

| Referenz | Umsetzung / Hostnachweis | Android-/Freigabestatus |
|---|---|---|
| #249 / #250 Startcrash | Prozess-Singleton, Startphasen, reduzierte Maintenance, LastGood, kein Netz auf Widget-Fokus, Erkennungsbudgets | **ROOT_CAUSE_UNCONFIRMED / NOT_TESTED**. Kein aktueller nativer Crash-Trace; Safeguards sind kein bestätigter Kodi-Fix. |
| Nutzer-Nachtrag Wizard träge | Doppel-Auth entfernt, Fast-Entry, kein Root-Wartekreis, verwaiste ACTIVE-Marker, Init-/Discoverylimits, Cancel/Retry | IMPLEMENTED / HOST_PASS; Gerät NOT_TESTED |
| #247 / #250 langfristiger Live-Back | Pending-Exit-Priorität, Herkunft Home/App, keine Root-Rekursion, Session-/ACK-Diagnose; `.42`-Engine unverändert | **PARTIAL / NOT_TESTED**. Nativer RK3528-Hänger ohne ACK nicht als repariert behauptet. |
| #239 / #242 / #244 / #247 Bilder und Infos | Tatsächliche Wizard-Verluste von Source-Archiv und Rich-Fakten repariert, korrekte Quellenränge, zentraler Quellenbeweis, revisionsgebundene Startdaten mit Jetzt/Danach-Fortschaltung, verifizierte Eventpropagation, Bildrotation/PIL/XMLTV-Icon-Schutz | IMPLEMENTED / HOST_PASS; reale Fotos, Decoder und Consumer NOT_TESTED. Fehlende alte Bildfakten nicht erfunden. |
| #245 / #247 Mini-EPG-Latenz | Lokaler Snapshot vor Legacy-Import, Quelle/Eventkey erhalten, kein unbewiesener Legacy-Fallback bei Quellbindung, atomare RAM-Aktualisierung, First-correct-Marker | IMPLEMENTED / HOST_PASS; Android-Cold/Warm/IR-p50/p95 NOT_TESTED |
| #250 Senderleiste/Hero | Native Live-only Vorschau + tatsächliches Layout, lokaler Fokus, 88 Sender / OK-Handoff geprüft | Native Ansicht NOT_TESTED; **bestehende BINGIE-Home BLOCKED_SKIN_INTEGRATION**. Reviewinclude ohne Installation. |
| #98 / #247 / #250 EPG zuweisen | Sichtbarer Button/Kontext, Quelle+Kanal, lokaler Namensindex, Vorschau im Raster, Save/Cancel, Legacy-Kompatibilität und Quellkollisionen | IMPLEMENTED / HOST_PASS; echte IR-/Android-Abnahme MAP48-01..08 NOT_TESTED |
| #228 / #240 / #247 Covermanager | Vorhandene Kandidaten sofort, Offlineauswahl, grafische Thumbnails, explicit Refresh/Save, sichere Bildredirects | IMPLEMENTED / HOST_PASS; F01-Ursache auf Gerät weiterhin unbestätigt; COVER48-01..05 NOT_TESTED |
| #247 C01–C05 + Movie Autorefresh | Geschützte Reader/Klick-/Reloadpfade und Mediendialog byteidentisch, alte Tests erhalten; abgeschlossener Live-Exit blockiert Refresh nicht | Historischer `.47` PASS bleibt. `.48`-REG48-01..06 NOT_TESTED. |
| #231 EPG-Schutz / Box A | Kein Reset/Cleanup/automatischer Reimport; bestehender gefüllter Guide erfordert verifizierte Sicherung; New-ID-Save separat geprüft | Schutz HOST_PASS; keine Box-A-Aktion; echtes BACKUP_VERIFIED nicht vorgetäuscht |
| D04 / #232 Historie | Bereits vorhandene -7 Tage / bis 20 Zukunft nur aus realen Feeds; kein Daten-/Zeitreset | **BLOCKED_REAL_TIME_WINDOW** bis sieben Tage tatsächlich vorhanden |
| #248 TV-Tipps | Nachrangige Referenz/Design, keine fremden redaktionellen Daten, kein Scraping/API-Aufruf | DEFERRED, keine Freigabe vorgetäuscht |
| Downloads / Aufnahmen / Space Premium | Nicht erweitert; bestehende Backends unverändert | OUT_OF_SCOPE, keine neuen Gerätespeichertests |

Lieferstatus und vollständige Zahlen im `TESTBERICHT_02948_DE.md`. Android ist ausdrücklich von Host/CI getrennt. Kein Issue wird automatisch geschlossen, kein PR automatisch gemergt, kein Repository-Release ausgelöst.
