# XCMate – Roadmap, Bugliste und Release-Checkliste

**Statusdatum:** 14.10.2026 · letzter geprüfter veröffentlichter Stand: 0.1.9.  
Labels: [RELEASED] in GitHub gebaut; [ON-DEVICE OPEN] Nutzergerätetest fehlt/negativ; [PLANNED] nur spezifiziert.

## Priorisierung

| Prio | Thema | Status | Nächster konkreter Schritt |
| --- | --- | --- | --- |
| P0 | Startsender aus Portalstartseite | [ON-DEVICE OPEN] | Android: direkt WELT starten; leere Verzeichnisansicht darf nicht erscheinen; Kodi-Log analysieren |
| P0 | Android TV-Fernbedienung Links/Hoch/Runter/OK und Zusatzmenü | [ON-DEVICE OPEN] | Native Action-ID per Diagnose/Anlernmodus prüfen; LiveNavigator-Fokus und BINGIE MOD testen |
| P0 | Senderliste sofort öffnen | [ON-DEVICE OPEN] | Warmcache messen; wiederholter Aufruf aus Vollbild ohne Serverwartezeit |
| P1 | Serien-Fortschritt, gesehen, fortsetzen, Auto-Next | [PLANNED] | Implementieren gemäß SERIES_PROGRESS_SPEC_DE.md und Android-Tests |
| P1 | EPG in Senderliste, Jetzt/Danach und manuelle XMLTV-Zuordnung | [RELEASED, ON-DEVICE OPEN] | Mit echten Daten Sender-ID-Mapping und Sichtbarkeit prüfen |
| P1 | Freigegebenes Bildpaket in Kodi integrieren | [DESIGN APPROVED / INTEGRATION OPEN] | Originale ins Repo, Assets referenzieren, ZIP und Anzeige prüfen |
| P1 | Frei wählbare XCMate-UI-Farben; Default edles Grau | [PLANNED] | Persistente Einstellung + TV-OSD-Theme + Kontrasttests |
| P2 | BINGIE MOD Sendergruppen-Widgets und Programminfo-Hover | [RELEASED, ON-DEVICE OPEN] | Skin-Widget-Typ prüfen, Fokus-Infopanel testen |
| P2 | Neueste Filme/Serien, Beschreibungen/YouTube-Trailer | [RELEASED, ON-DEVICE OPEN] | Providerfelder, Metadaten & Kodi-YouTube-Erreichbarkeit prüfen |

## Vor jedem Release

1. `addon.xml`-Version erhöhen, Ziel-ID `plugin.video.xtreammate` beibehalten, Name **XCMate**; Installer- und XML-Katalogversion müssen übereinstimmen.
2. Keine aktiven Zugangsdaten, privaten URLs, Tokens, Portalprofile oder realen Logs in Commit, Testdaten oder ZIP.
3. Python `compileall` + `python -m unittest discover -s tests -v` (CI), neue Tests für die Änderung; nicht nur String-/Mock-Tests als Android-End-to-End-Nachweis werten.
4. `.github/workflows/publish.yml` muss erfolgreich durchlaufen; danach existieren tatsächlich `plugin.video.xtreammate/plugin.video.xtreammate-VERSION.zip`, `addons.xml`, `addons.xml.md5`.
5. Beim Upgrade aus der Vorversion unveränderte Portale/Gruppen/Tasten/EPG/Startsender belegen; Kodi nicht deinstallieren und Profile nicht löschen.
6. Android-Test: WELT/anderen gespeicherten Sender starten, Links/Links, Up/Down, OK/OK, Guide, Zurück, Audio/Video, Streaming-Stop, wiederholter Cache-Aufruf.
7. Serien-Funktion zusätzlich: bookmark, resume, watched, next, Ende vs manuelles Stop, Doppelereignisse, Offline/Kodi-Neustart.
8. UI: echtes Kodi/Titan BINGIE MOD, 10-Foot-View, Standardgrau, Fokusrahmen, lesbare EPG-Infos.
9. Erfolgsbericht trennt **CI-Grün**, **GitHub-ZIP vorhanden** und **Android-Gerätetest bestanden** ausdrücklich.

## Diagnostik und Mindestdaten vom Testgerät

Kodi-Version und Android-Version erfragen, aber keine Zugangsdaten. Menü `TV-Fernbedienung: Diagnose` verwenden: Tastenbelegung, Xtream-Session, Overlay-Status, letzte Kodi-Taste, zuletzt verarbeitet, Startsender-Status. Fehlerzeilen aus `kodi.log` anonymisieren. Nicht ungefragt ein neues Kodi-Repository oder eine vollständige Neuinstallation verlangen.

## Pflege dieses Projekts

Bei jeder Änderung: Bug und verifizierte Ursache, Dateien, Tests, GitHub Commit-SHA, Action-Run-ID, installierbares ZIP, noch offene Gerätetests und neues nächstes To-do hier nachtragen. Einen neuen Chat stets mit `NEW_CHAT_COPY_BLOCK_DE.md` beginnen.
