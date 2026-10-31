# XCMate .63 – Issue-Abnahmematrix

Abschlussbelege: exakter HEAD, grüner Actions-Lauf, vollständiger Testlog und ZIP-SHA256 im Abschlusskommentar von [Draft-PR #294](https://github.com/artattakk-creator/kodi-noodleprivate/pull/294). Technische Umsetzung und reale Geräteabnahme sind getrennt. Kein Issue wird automatisch geschlossen.

| Auftrag | Technischer Umfang in .63 | Automatisierter Nachweis | Geräteabnahme |
|---|---|---|---|
| #293 / #284 Hero | Full-bleed mit Textoverlay/Gradient, reale Now/Next-Daten, keine rechte Infotabelle, akzeptierte LiveRow erhalten | echte native Kodi-Pixel, 88 Sender, Texte/Bilder/Neutralfall; aktueller CI-Nachweis im PR | ANDROID_NOT_TESTED |
| #291 lokales EPG | vorhandene guide_v1.sqlite, Quellen-/Alias-/Profil-/Revisionsprüfung, warme RAM-Übergabe vor Worker-Nachladung | echte SQLite-Identität, kein GUI-SQL/HTTP, Publikationswechsel, Source-/Profilkollision, native Warm-Messwerte | ANDROID_NOT_TESTED |
| #292 VFS-Import | ausgewählte USB/Downloads/SMB lesen, einmalig privat kopieren, Android-Profilanker schützen, Format-/Bytebudget und Fehlercodes | VFS-Mocks, echte synthetische lokale Dateien, Teilreads/EOF/Timeout, atomarer Vergleich und Schreibfehler | ANDROID_NOT_TESTED |
| #288 Zurück | sichtbare Position4/Remote-Back unverändert, Abschalten separat | bestehende und neue Menüregressionen | ANDROID_NOT_TESTED |
| #286 Menüzugang | sichtbare bestehende Widget-/TMDB-Menüs und passive Quellenrouten beibehalten | nativer Einstellungsweg, explizite Preview/Bestätigung, gespeicherte Bindings geschützt | ANDROID_NOT_TESTED |
| #293 TMDB-Aktivierung | Import allein unverändert; getrennte ausdrückliche Aktivierung, profilgebundener Hintergrundimpuls; maskierte Eingabe | UI-/Privatdatei-/Negativcache-/Neustartregressionen, sichere synthetische HTTP-Statusmatrix | ANDROID_NOT_TESTED |
| #293 echte TMDB-Authentifizierung | vorhandener echter HTTPS-Verbindungstest; kein gemeinsamer Schlüssel | Transport-/401/403/429/TLS/Timeout-Tests mit synthetischen Antworten sind kein Nutzertoken-Erfolg | ANDROID_NOT_TESTED |
| #293 Bilderpipeline | gleiche Ereignis-/Artworkidentität, Provider/XMLTV und verifizierte lokale Quellen vor optionalen Fallbacks; keine Fokus-Netzjobs | native dekodierte Testbilder, Ereigniswechsel und bestehende gemeinsame Cachetests | ANDROID_NOT_TESTED |
| .42 / .59 / .61 / .62 Bestandsschutz | keine Player-/Remote-/EPG-Import-/Widget-Routen-Neuschreibung, keine Resets, keine Boxänderung | 2.553 erhaltene Methoden und 624-Dateien-Inventar plus volle Regression | ANDROID_NOT_TESTED |

Vollständige technische Umsetzung wird durch Geräteabnahme bestätigt oder widerlegt; Host-PASS allein schließt die realen Fehlerberichte nicht.
