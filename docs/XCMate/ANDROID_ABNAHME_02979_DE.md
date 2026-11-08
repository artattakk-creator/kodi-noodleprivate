# XCMate 0.1.29.79 – Android-Abnahme

Stand 08.11.2026. Alle folgenden Gates: **ANDROID_NOT_TESTED**.
Auf vorhandener Kodi-21.3-ARM32-Testbox prüfen; ältere Kodi-21.2-Box erst nach eigener Freigabe. Keine Neuinstallation, kein Reset, keine Skin-/Keymap-Änderung. Der Download ist ein manuelles Test-Update; die regulären Kanäle bleiben .78.

Vorher installierte Version und Gerät notieren, bestehende Sicherung verwenden, persönliche Widget-Reihen/Pfade und Startgruppe dokumentieren. ZIP-Prüfsumme vergleichen. Keine Zugangsdaten, Bild-/Stream-URLs oder private Rohlogs öffentlich hochladen.

| Gate | Durchführung | Erwartung | Ergebnis |
|---|---|---|---|
| HOME79-01 | .78 mit .79-Test-ZIP aktualisieren | Portale, Token, Favoriten, EPG-Mappings, Space Blue, Installer 0.5.26 unverändert | ANDROID_NOT_TESTED |
| HOME79-02 | Kodi ohne vorherigen Senderstart öffnen | Startgruppe, Logos, lokales Jetzt/Danach und großer fester Hero vorhanden | ANDROID_NOT_TESTED |
| HOME79-03 | Live-TV, Filme, Serien fokussieren; vorhandene zusätzliche Reihen prüfen | Wirkliche Einträge in BINGIE-Controls; persönliche Reihen einschließlich „Neu im Kino“/Pfade/Positionen erhalten | ANDROID_NOT_TESTED |
| HOME79-04 | Film-/Seriencover laden lassen, Kodi vollständig beenden und zweimal neu starten | Bereits dargestellte Cover bleiben erhalten; keine dauerhafte Rückkehr zu Platzhaltern | ANDROID_NOT_TESTED |
| HOME79-05 | Nach erfolgreichem Laden vorübergehend Netzwerk trennen | Vorhandene Cache-Cover bleiben sichtbar; EPG-Texte bleiben von Bildsuche unabhängig | ANDROID_NOT_TESTED |
| HOME79-06 | Skin regulär neu laden, Reihen wechseln und zurückscrollen | Keine leeren alten Generationen, Fokusrahmen korrekt, Hero unverändert groß | ANDROID_NOT_TESTED |
| EPG79-01 | Sender mit Provider-/XMLTV-ID und manuell zugewiesenen Sender vergleichen | Richtige Programme; manuelle Zuordnung bleibt vorrangig; keine Vermischung ähnlich benannter Sender | ANDROID_NOT_TESTED |
| EPG79-02 | Sender ohne EPG mehrfach fokussieren und anschließend Daten aktualisieren | Keine Poll-Flut; neue gespeicherte Daten werden nach Commit berücksichtigt | ANDROID_NOT_TESTED |
| IMAGE79-01 | Dieselbe laufende Sendung in Home, Mini- und Groß-EPG öffnen | Passendes tatsächlich sichtbares Bild und identische Sendungszuordnung; URL/Decode allein kein PASS | ANDROID_NOT_TESTED |
| IMAGE79-02 | Mini-/Groß-EPG-Details mehrfach öffnen, schließen, Zeitfenster wechseln | Keine Helper-Hänger, keine veralteten Sendungsbilder, bedienbarer Rückweg | ANDROID_NOT_TESTED |
| NAV79-01 | Linksnavigation, Kategorien, Suche, alle Widget-Ebenen und Back testen | Keine Timeout-/Focus-Schleifen; gespeicherte Navigation erhalten | ANDROID_NOT_TESTED |
| EXIT79-01 | Live-TV starten → einmal Zurück | Eigener Stream stoppt, ACK, bedienbare vorherige Ansicht; bei FAIL weitere Zyklen abbrechen | ANDROID_NOT_TESTED |
| EXIT79-02 | Film und Serie jeweils starten → Zurück; danach fünf/20 Zyklen | Keine Hänger; Resume, Gesehen-Status, manuelles Next und Autoplay samt Staffelwechsel erhalten | ANDROID_NOT_TESTED |
| DB79-01 | Vorhandene Diagnose für Kodi-Videobibliothek ausführen | Fehlende/defekte Views klar gemeldet; DB unverändert; Providerwidgets funktionieren unabhängig | ANDROID_NOT_TESTED |
| REG79-01 | Kodi-Neustart, Katalogaktualisierung, Startgruppe, Favoriten, Suche | Keine Nutzerdatenverluste oder Änderung persönlicher Einstellungen | ANDROID_NOT_TESTED |

Für jedes Gate PASS/FAIL/NOT_TESTED mit Gerät, Kodi-Version, Uhrzeit und beobachteter Darstellung notieren. Screenshots von realen Geräten von synthetischen Linux-Belegen unterscheiden. Bildfehler erst nach Sichtkontrolle als behoben markieren. Falls „Neu im Kino“ wegen fehlender Kodi-Views leer bleibt: separat als DB-Problem erfassen, keine Datenbankreparatur ohne gesicherte Analyse/Freigabe.
