# Android-Test 0.1.29.20 – Artwork – NOT_TESTED

Android 13 ARM32 / Kodi 21.2 / Titan BINGIE MOD / IR. .19-Tests 42–46 laut Nutzer PASS für die geprüften Abläufe. Neue .20-Schritte einzeln PASS/FAIL/NOT_TESTED bewerten, nicht ungeprüft übernehmen. Keine Cache-/Datenlöschung, Reimports oder Reparaturaktionen.

## Vorbereitung und Installation

- [ ] Kodi beenden und Profil privat sichern. Bestehenden Bildstatus (READY/SPACE_FULL/Bytes, Limit, freien Speicher) und eigene Einstellungen notieren. Keine Zugangsdaten/Bildadressen öffentlich teilen.
- [ ] ZIP/SHA prüfen, Test-ZIP manuell installieren, Kodi neu starten; Version **0.1.29.20**. Portale, EPG, Gruppen, Favoriten, Resume, Seen und bisherige Bilder vorhanden.
- [ ] Einstellungen → Speicher → Bildspeicherstatus: automatisches Limit „verfügbarer Speicher“ oder vorhandenes bewusstes Festlimit, Mindestreserve (Standard 1024 MiB), Downloads aktiv/pausiert nachvollziehbar. Ein explizites altes volles 512-Limit bleibt erhalten; für den Automatiktest selbst **Bildspeicherlimit=0** wählen. Eigene Werte vorher notieren.

## Poster und Ursachen

- [ ] Große Filmkategorie öffnen, normale Down-Navigation über 24, 48, 240 und möglichst **500 unterschiedliche Titel**. Gesamtzahl/Position/fokussiertes Cover bleiben stabil, keine Bedienblockade.
- [ ] Dasselbe in einer großen Serienkategorie. Nachladen neuer Poster beobachten; neue lokale Grafik erscheint ohne Neuöffnen, Fokus/Position bleiben bestehen.
- [ ] Repräsentatives Platzhalter-Cover fokussieren, kurz ruhen lassen und Fußzeile ablesen: keine Providerquelle / ungültige Quelle / ausstehend / lädt / Netzfehler / Cachefehler / Limit / physische Reserve / Datenbank belegt. Keine Provideradresse anzeigen oder veröffentlichen. NO_SOURCE ist kein Nachweis eines internen Downloadfehlers.
- [ ] Bildspeicherstatus erneut lesen: READY wächst, alte SPACE_FULL können in begrenzten Portionen abnehmen; Netz-/ungültige Bildfehler werden nicht unendlich neu versucht. Nicht alle 17k alten Jobs müssen sofort fertig sein.
- [ ] Weit zurückscrollen, Details/Back, Home/erneut öffnen: bereits heruntergeladene Cover sofort lokal, keine erneute Platzhalterwelle allein wegen Fensterung.
- [ ] Kodi vollständig neu starten, dieselben Titel erneut öffnen. Bereits gespeicherte Cover bleiben vorhanden. Optional bekannter Titel bei kurz fehlendem Netzwerk: vorhandene lokale Bilder bleiben; neue Downloads dürfen verständlich scheitern. Keine Profile entfernen.

## EPG und Speichersteuerung

- [ ] Bekanntes EPG öffnen: lokal vorhandene Logos sofort, fehlende mit gültiger Quelle priorisiert nachladen, nach Erfolg ohne Guide-Neustart sichtbar. Sender-/Zeitnavigation unverändert.
- [ ] Downloadpause einschalten: vorhandene Bilder weiter sichtbar; nach Ende eines gegebenenfalls schon laufenden begrenzten Downloads beginnen keine neuen. Fortsetzen setzt berechtigte Jobs fort, ohne READY neu herunterzuladen.
- [ ] Optional ein bewusst gewähltes kleines Festlimit setzen, ohne Dateien zu löschen: Status muss **eingestelltes Limit** anzeigen, nicht physisch vollen Speicher behaupten. Danach den notierten gewünschten Wert/0 wiederherstellen. Keine Massenausführung von „Erneut versuchen“ nötig.
- [ ] Echte ENOSPC-/Fast-voll-Tests **nicht durch Füllen des Android-Laufwerks erzwingen**. Hosttests decken diese Fälle ab; auf dem Gerät ohne geeignete separate Testumgebung NOT_TESTED lassen. Reserve und freien Platz nur ablesen.

## Regression und Herkunft

- [ ] .19-Medienlayout, sichtbarer Rahmen und Kategorie-/Cover-Back; Favoriten hinzufügen/entfernen, Resume, rote/grüne Augen und Continue-Ausblendung bleiben erhalten, einschließlich Neustart.
- [ ] Manuelle Next-Aktion: markierte Folge → Rechts → Next; richtige Folge/Staffel, Rückkehrfokus, Stop beendet Bild und Ton. Keine automatische Fortsetzung erwarten: #85 ist weiterhin NOT_IMPLEMENTED.
- [ ] Bekannter guter Live-TV-/EPG-Start und Stop/Back: keine Doppelstarts, kein Hintergrundton, keine neue Tastenbelegung.
- [ ] Add-on heißt XCMate, Anbieter **GS Media** ohne Fork-Suffix. Add-on-Information nennt die Herkunft. Einstellungen → Info → Lizenzen und Herkunft zeigt Upstream/Änderungshinweise und vollständige GPL; keine Copyrightentfernung.

Rückfall: unverändertes .19-ZIP mit bestehendem Profil. Die additive Queue-Metadatentabelle erfordert keine Rückmigration. Falls das Limit für .20 bewusst auf 0 geändert wurde, hat .19 dafür noch die alte Budgetsemantik; beim Rückfall den vorher notierten Wert manuell wiederherstellen. Bilddateien/Jobs nicht löschen. Bei Crash/Hänger/Hintergrundton abbrechen, Version/Schritt/Zeitpunkt und bereinigte private Diagnose sichern. Kein Merge/Release ohne ausdrückliche Freigabe.
