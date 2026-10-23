# Android-Test – XCMate 0.1.29.24 / Space Premium 1.0.0

Separater kumulativer Draft einschließlich .23, keine Veröffentlichung. Erst .23-Grafikbefunde dokumentieren, dann direkt über vorhandenes XCMate installieren; keine Deinstallation und kein Cache-/Datenreset. ZIP mit SHA256 prüfen. Ziel: Android 13 RK3528 ARM32, Kodi 21.2, Titan BINGIE MOD, IR. Alle neuen Zeilen hier NOT_TESTED; einzeln PASS / FAIL / NOT_TESTED melden.

- [ ] T01 .24 installiert, Portale, Gruppen, Startsender, Favoriten, EPG-Zuordnungen, Resume/Gesehen und gespeicherte Cover erhalten.
- [ ] T02 Ohne Paket: Standard – XCMate Lightweight öffnet Home, Live, EPG, Filme/Serien; Original-Icon auf Kodi-Kachel, Info und Home sichtbar, auch nach Neustart.
- [ ] T03 Einstellungen → Darstellung & Sprache → XCMate-Designs → Designs verwalten: beide Designs und korrekter Status sichtbar; Vorschau öffnet/schließt mit IR ohne Download.
- [ ] T04 Space Premium → Herunterladen und installieren: genau ein bewusster Abruf, SHA256/Installation erfolgreich; Status Installiert. Abbruch während Download hinterlässt Standard und vorhandene Daten unverändert.
- [ ] T05 Premium aktivieren, XCMate neu öffnen: Home, Einstellungen, Live-Senderleiste/Infobar/Transport, EPG-Hintergrund/Kopficons, Film-/Serienaktionen, Platzhalter und eigenes Player-OSD verwenden Premiumgrafiken. Providerposter haben Vorrang.
- [ ] T06 Dasselbe Original-XCMate-Icon bleibt sichtbar; Original-Icon prüfen meldet ORIGINAL/CONTENT_ADDRESSED.
- [ ] T07 EPG E01–E10 aus Test 50: Startgruppe/-sender, Originalreihenfolge, Links-Gruppenwahl, Zurück/Position, sechs Kopfbuttons, weiße lesbare Beschriftung/transparent sichtbarer Fokus, Zeitnavigation/Refresh.
- [ ] T08 IR-Back, Detail-/Rail-Navigation und Fokus bleiben in Standard und Premium bedienbar; EPG-Play/Live-Overlay/Senderwechsel/Stop ohne Absturz oder unerwünschten Neustart.
- [ ] T09 Premium nach Kodi-Neustart aktiv. Internet deaktivieren: installierter Premium-/Standard-Wechsel funktioniert ohne erneuten Download.
- [ ] T10 Standard wiederherstellen und XCMate neu öffnen; anschließend Premium erneut aktivieren. Auswahl bleibt gespeichert. Wechsel während Wiedergabe verändert/stört den laufenden Player nicht und gilt nach Wiedergabe beim nächsten Öffnen.
- [ ] T11 Paket ausdrücklich entfernen: nur Theme verschwindet, Core bleibt nutzbar; keine Bilder/Portale/EPG/Resume verloren. Fehlendes oder fehlerhaftes Paket fällt auf Core zurück, Fehler wird ohne privaten Pfad/Adresse angezeigt.
- [ ] T12 Bereits geladene Poster, Einzelposterstatus/-Retry aus .23, normales Serien-Autoplay und manuelles Next/Resume/Gesehen funktionieren weiter.

Keinen absichtlichen Stromverlust oder Dateimanipulation im produktiven Profil für Rollbacktests durchführen; beschädigte ZIP-/Prüfsummen-/Pfadfälle sind automatisiert geprüft. Gerätetest eines fehlerhaften Pakets nur mit eigener Kopie über den XCMate-Import, niemals über Kodis globalen ZIP-Installer für Themes. Kodi-Skin und Keymaps bleiben unverändert. B02 automatischer Staffelwechsel ist ausdrücklich ausgenommen, #85 bleibt offen.
