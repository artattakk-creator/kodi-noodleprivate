# XCMate – Implementierungsplan: eigene Kodi-Popup-Oberflächen ab 0.1.15

**Stand:** 14.10.2026 · **Architekturentscheidung:** Kodi-eigene Python-`xbmcgui.WindowDialog`-Overlays und später erforderlichenfalls Skin/XML-Dialoge statt die Kodi-Standard-Player-OSD-Menüs global zu ändern. Die bestehenden XCMate-Portale, Add-on-ID `plugin.video.xtreammate`, EPG-Zuordnungen, gelernten Tasten und alle Benutzerdaten bleiben erhalten. Die TiviMate-Nutzerfotos sind nur Funktions-/Navigationsreferenz, keine kopierten TiviMate-Assets.

## Ausgangslage: durch echte Android-Aufnahmen belegt

- Startsender gibt TV-Bild aus, aber dessen OK/Links/Hoch/Runter/Menü wurden vom eigenen XCMate-Overlay bislang nicht zuverlässig abgefangen. Kodi-Standard-Menü und Lautstärke funktionieren.
- Service-Heartbeat zeigte **LÄUFT** und **2134 Dienstschleifen** mit **Video JA / XCMate-Sitzung NEIN**. Die Session-Wiederherstellung 0.1.14 wurde implementiert, aber noch **nicht** auf Android erfolgreich bestätigt.
- Ein modal gestartetes Dialogfenster aus einem normalen Kodi-Menü ist ein *separat* testbarer Eingabe-/Fokuspfad, auch wenn Live-TV nicht navigierbar ist. Ein Kodi-Overlay benötigt **keine Android-Draw-over-other-apps-Berechtigung**.

## Etappen

### Version 0.1.15 – P0 GUI-Smoketest und sichtbares TV-Overlay

**Lieferumfang (nach CI/Release):**

1. **„XCMate Popup- und Fernbedienungstest“** als Eintrag im Xtream-Portalmenü. Startet einen eigenen fokussierbaren `WindowDialog.doModal()` in der aktiven Kodi-Plugin-Ausführung – keine Stream-Wiedergabe erforderlich; kein Service- oder Xtream-Login erforderlich. Helle Schaltflächen „OK / Fokus testen“ und „Schließen“; Kodi-Tasten Links/Rechts/Hoch/Runter/OK/Zurück werden angezeigt, mit numerischer Action-ID und Count.
2. Zusätzliche Diagnose-Zeilen: letzter Popup-Status, letzter Key, Eingabeanzahl, Fokusstatus, automatischer TV-Popup-Status. Werte enthalten keinerlei Portal-URL, Benutzernamen oder Zugangsdaten.
3. Bestehender Live-`WindowDialog` initial **sichtbar als Sender-/EPG-Sidebar** über TV; die übrige Bildschirmfläche bleibt Livevideo. Nach 16 Sekunden **ohne** Tasteneingabe verschwindet die Sidebar, ohne das Video zu stoppen. Jede empfangene Taste unterbindet das automatische Ausblenden. Sender-/EPG-Daten stammen nur aus vorhandenem Cache. Keine Behauptung, das bereits gerenderte TV sei ein separat skaliertes Minivideo.
4. Kodi-Standard-Player-OSD bleibt technisch unverändert, soweit XCMate aktuell den Key-Event **nicht** erhält. Die Software darf nicht behaupten, sie könne die Android-Keyevents unabhängig von der tatsächlichen Fenster-Fokussierung ersetzen.
5. Keine zusätzlichen Benutzereinstellungen oder Portale werden automatisch geändert; 0.1.14-Session-Recovery bleibt vorhanden.

**Geräteabnahme auf Android / Kodi + Titan BINGIE MOD:**
- [ ] Nach Repository-Update Kodi vollständig neu starten.
- [ ] Ohne Sender: Portalmenü → **XCMate Popup- und Fernbedienungstest**. Ist das eigene große Popup sichtbar? Bild fotografieren.
- [ ] Im eigenen Fenster Links / Hoch / Runter / Rechts / OK auslösen. Wird die letzte Taste / Ereigniszahl aktualisiert? **Zurück** schließt. Ohne Stream müssen die Tests funktionieren.
- [ ] Portalmenü → „TV-Fernbedienung: Diagnose“: `Popup-Status`, `Popup-Ereignisse`, `Popup-Letzte Taste`, `Popup-Fokus` prüfen.
- [ ] Xtream-Startsender starten. Erscheint **automatisch** eine XCMate-Sender-/EPG-Sidebar für 16 Sekunden über dem TV-Stream? Foto machen, bevor sie verschwindet.
- [ ] Bei geöffnetem Live-Popup OK / Links drücken. Nach dem Stream erneut die Diagnose aufrufen: `Live-Sitzungswiederherstellung`, `Letzte TV-Einblendung`, `Auto-TV-Popup`, `Native Tastenereignisse`.
- [ ] Fehler nach Phase unterscheiden: **Popup ohne Video nicht sichtbar** = Kodi-GUI/Addon-Anbindung; **sichtbar, keine Tasten** = Kodi-Dialogfokus/Keymap; **Popup ohne Video funktioniert, Live-Popup fehlt** = Service/Session/Video-Fokus; **beide funktionieren** = Grundlage für die nächste UI-Stufe.

**Gating:** Python-/Kodi-Mock-Tests und GitHub-CI können GUI-/Fokusfehler auf der realen Android-Box nicht nachweisen. **Keine Android-PASS-Aussage** ohne reale Fotobelege.

### Version 0.1.16 – P1 Senderübersicht / Gruppen-Overlay

Nach bestandener GUI-Eingabeabnahme:
- Links → fokussierbare Senderliste mit Senderlogo, Kanalnummer, EPG Jetzt/Danach und Fortschrittsbalken.
- Links erneut → Sendergruppen; Rechts → Sender; OK → abgestimmte Senderwahl; Zurück → Popup schließen.
- Fokusgedächtnis für Sender, Kategorie und scrollbare Listen; Filterung via vorhandene Portal-/Gruppen-ID.
- Als TV-Vorschau **weiterhin laufendes Hauptvideo sichtbar im nicht verdeckten Bereich**. Wirklich skaliertes, separates Video nur nach Kodi/Android-Renderingprüfung, nicht als Fake-Bild.
- Service muss auf Zappen ohne mehrfaches OSD-Initialisieren reagieren; keine blockierenden Xtream-Abfragen im GUI-Thread.

### Version 0.1.17 – P1 EPG-Zeitraster, Programmdetails und TV-Vorschau

- Vollständiges Guide-Raster mit horizontalen Zeitblöcken, Jetzt-Linie, Programm- und Senderfokus, Vorschau-/Info-Bereich und Catch-up-Metadaten.
- XMLTV/Xtream-Cache; Zeitzonen-/Lücken-/Stale-Daten sauber behandeln.
- Mini-TV im oberen Bereich als **Machbarkeitsthema**: Kodi XML-Skin-VideoControl/PVR/Host-Decodierung prüfen. Mögliches alternatives Layout: unverkleinertes Video in offen gelassenem Teil des Bildschirms. Kein zweiter laufender Decoder, keine Darstellung eines Standbildes als Livevideo.
- Prüfung D-Pad, Zurück, Guide, Favorit, Umschalten, Zeitachse.

### Version 0.1.18 – P1 Komfort und TV-Menüs

- Einheitliches XCMate-Quick-Panel auf OK mit Now/Next, EPG, Ton, Untertitel, Favoriten, Verlauf, Senderliste.
- Suche, Verlauf, zuletzt gesehener Sender, mögliche TiviMate-Tastenkontexte; Serienfortschritt und nächstes Episode-Autoplay getrennt, wie in `SERIES_PROGRESS_SPEC_DE.md`.
- Kennzeichnung nicht verfügbarer Android-/Kodi-Host-Funktionen statt funktionsloser Buttons.

### Version 0.1.19 – P2 Design / Optik

- Silver-Space-Logo, zurückhaltendes dunkles Slate-Grau als Standard, optionale Farben, Transparenz- und Schriftgrößenregelung; freigegebene Original-Grafiken von GS Media erst nach gesicherter Asset-Übernahme.
- Keine Übernahme geschützter TiviMate-Grafikassets; hohe Lesbarkeit/Focus-Rahmen auf Fernsehern.

## Gemeinsame technische Leitplanken

- Nur Add-on-eigene Kodi-Overlays, keine Android-System-Popups.
- Keine Änderungen an fremden Keymap-Dateien, Kodi-Globalsteuerung oder den Einstellungen anderer Add-ons.
- Sichere, opt-in/fail-closed Keymap; Benutzerdaten und Anbieter-Credentials nie in UI-Diagnose oder CI.
- Jede Stufe: Regressionstests, GitHub Actions, installierbares ZIP, `addons.xml` und Prüfsumme, danach echter Android-Gerätetest.
- Versionen nach 0.1.15 sind **Planungsmeilensteine**, keine zugesagten fertigen Installationspakete und können nach Gerätetestergebnissen umpriorisiert werden.
