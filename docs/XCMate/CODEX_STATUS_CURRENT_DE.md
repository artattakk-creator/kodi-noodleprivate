# XCMate / Codex – aktueller Projekt- und Release-Status (verbindliche Übergabe)

**Stand:** 18.10.2026  
**Aktuelle Kodi-Version:** `0.1.22` (aus `main` des GS Media Kodi Repository veröffentlicht; Android-TV-Abnahme AUSSTEHEND)  
**Technische Kodi-ID:** `plugin.video.xtreammate` – nicht ändern  
**Repository:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Hauptbranch:** `main`  
**Codex-Entwicklungsbranch:** `fix/xcmate-kodi21-overlay-epg` (historischer Stand dieser Korrektur)  
**Übernahme:** [Pull Request #11](https://github.com/artattakk-creator/kodi-noodleprivate/pull/11), Merge-Commit `c14d7815bf0ca2e93dd3e1fa5225ca1df36c8f54`.  
**Veröffentlichung:** GitHub-Action [Publish GS Media Kodi updates](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39126897807) erfolgreich; `addons.xml` meldet XCMate `0.1.22`, ZIP `plugin.video.xtreammate/plugin.video.xtreammate-0.1.22.zip` vorhanden.  
**Letzter geprüfter Repository-Stand nach Auto-Publish (vor dieser Statusaktualisierung):** `9b590ea2dc0983fa75b084582431065211de1484`.

## Zuerst lesen – maßgebliche Unterlagen

1. [Zentrale Übersicht](README.md).
2. [Codex-Fehlerbericht, Ressourcenlimits, alle Geräte-Abnahmeschritte für 0.1.22](KODI21_FIX_022_DE.md) – stammt aus der Testkandidatenphase; deshalb ist die Aussage »nicht veröffentlicht« dort **historisch**, nicht aktueller Release-Status.
3. [Technischer Projektkontext](PROJECT_HANDOFF_DE.md) – enthält auch ältere Versionsangaben.
4. [Roadmap, offene Fehler und QA](ROADMAP_AND_QA_DE.md).
5. [Vorheriger 0.1.21-Zwischenstand](TV_REMOTE_EPG_RECOVERY_021_DE.md).

## Was Codex tatsächlich geändert hat (0.1.22)

- `live_overlay.py`: korrekter programmatischer Kodi-21-/Omega-`WindowDialog`-Lebenszyklus, Control-Konstruktion vor `show()`, `onControl` statt bisherigem unpassenden `onClick`, sichtbarer Fokus mit mitgelieferten Texturen und deduplizierte Tastenevents.
- `service.py`: stärkere Überprüfung der XCMate-eigenen Live-TV-Sitzung und Bereinigung bei fremder Wiedergabe.
- `utils.py`, `network_io.py`: Cache-Writable-Probe und Fallback; HTTP-Daten und Dekomprimierung begrenzt.
- `epg.py`, `epg_io.py`, `epg_sources.py`, `main.py`: ungültige XMLTV-Programme einzeln auslassen; bounded streaming; EPG-Refresh asynchron.
- Neue Tests: `tests/test_xcmate_kodi21_overlay.py`, `tests/test_xcmate_epg_limits.py` und Änderungen an Regressionstests.
- Noodle Private und fremde Add-ons wurden nicht verändert.

**Geprüft:** Pull-Request-GitHub-CI vom 18.10.2026: **180 Python-Tests erfolgreich**; Python-Syntax, Build und ZIP-Prüfungen erfolgreich. Der Release-Push-Workflow war erfolgreich. Das ist kein Ersatz für Gerätetests.

## Wichtige Einschränkung

Die neue XMLTV-Obergrenze beträgt **80 MiB entpackte XMLTV-Daten pro Quelle**, 150.000 Sendungen insgesamt und weitere dokumentierte Limits. Ein zuvor analysierter DE-MASTER-XMLTV-Datensatz war ca. 100 MiB unkomprimiert und kann dadurch bei dieser Version abgewiesen werden. Das ist ein **offenes Kompatibilitäts-/Abnahmethema**, nicht als funktionierendes EPG bewerten. Prüfe gegebenenfalls kleinere DE/AT/CH-Quellen und diskutiere später Streaming-Senderfilterung, ohne das Speicherlimit unkontrolliert zu erhöhen.

## BESTÄTIGTER Realgeräte-Test: XCMate 0.1.22 – Live-TV-Navigation schlägt fehl (18.10.2026)

**Versionsnummer 0.1.22 vom Nutzer bestätigt.** Die nachfolgenden Beobachtungen beziehen sich auf echtes Live-TV, nicht auf den separaten XML-Popup-Diagnosetest.

- **Positiv:** XCMate startet, reguläre Senderliste lässt sich öffnen, ein Xtream-Sender lässt sich starten und abspielen. Kurzes OK öffnet zügig und zuverlässig das **Kodi-Standard-Videoplayer-Menü**.
- **P0 offen:** Eigenes XCMate-Live-TV-Overlay / XCMate-OSD ist nicht erreichbar. Links öffnet keine XCMate-Senderliste; Hoch/Runter schaltet keine Sender; langes OK bzw. der gewünschte zusätzliche Bedienbereich mit Video-/Audio-/Untertitel- und Systemeinstellungen ist nicht erreichbar. **P0 nicht als behoben abschließen.**
- **P1 offen:** Reguläre XCMate-Senderliste zeigt **keine EPG-Jetzt/Danach-Angaben**. Ein zuvor gemeldeter Hintergrunddownload wurde nur gestartet, seine erfolgreiche Verarbeitung und Xtream-Senderzuordnung nicht bestätigt.
- Technischer Hypothesenpfad im Code: `main._play_live` meldet Xtream-LiveSession nur bei vorhandenem pid/sid; `service` startet Dialog nur für bestätigte Sessions, `LiveNavigator.owns_playback` gleicht laufende URL mit konfiguriertem Portal ab. **Ob eine bestimmte Prüfung fehlschlägt, muss mit Geräte-Diagnose und Kodi-Log geklärt werden**, nicht unbelegt behaupten.
- Mögliche weitere Ursache EPG: 80-MiB-Grenze für XMLTV verhindert großes deutsches DE-MASTER; andere Ursachen sind EPG-Downloadfehler, leerer Cache, unpassende Channel-IDs oder Zeitfenster.

**Nachverfolgung:** [GitHub-Issue #12 – Realgerät: XCMate-Fernbedienung greift nicht, Senderliste ohne EPG](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12). Codex soll auf einem neuen Fix-Branch arbeiten und mit Geräte-Logs testen; keine ungetestete direkte Veröffentlichung auf `main`.

**Nächster konkreter Geräteschritt:** Live-TV-Sender starten, dann ohne Kodi-Neustart Wiedergabe beenden und sofort `XCMate → TV-Fernbedienung: Diagnose` öffnen. Die Felder für letzte Live-Beobachtung, Sitzungswiederherstellung, Auto-TV-Popup, TV-Einblendung, Eingabepfad, native Tastenereignisse und letzte Fehler vollständig fotografieren. Bei weiterem Black Screen ggf. `kodi.log`/`kodi.old.log` anonymisieren und auswerten. Die getrennten VOD-Abbruchprobleme bleiben offen.

## Android-TV-Diagnose mit drei Fotos – 18.10.2026

**Installierte Add-on-Version bei diesen Screenshots weiterhin nicht verifiziert** (ggf. 0.1.21, nicht als erfolgreiche 0.1.22-Geräteabnahme interpretieren).

**Hintergrunddienst (Foto 1):**
- Dienststatus **LÄUFT**, letzte Lebenszeichen-Aktualisierung **0,1 Sekunden**.
- **533** Dienstschleifen, Dienstphase „läuft“, letzter Dienstfehler „keine gemeldet“.
- Letzte Live-Beobachtung „noch nicht geprüft“; Sitzungswiederherstellung „noch keine Prüfung“; TV-Einblendung „noch nicht gestartet“; Diensteingabe noch nicht verarbeitet.
- Autostart-Diagnosemodus **PAUSIERT**.

**Separater XML-Popup-Test (Fotos 1–2):**
- Darstellungsweg `WindowXMLDialog – Default/720p`.
- Popup-Status `XML: PER ZURÜCK GESCHLOSSEN`.
- **18** registrierte Popup-Eingabeereignisse.
- Letzte Taste `Zurück (Navigation)`, Kodi-Aktions-ID **92**.
- Zuletzt gespeicherter Fokusstatus **„Testfeld“**.
- Der Code `popup_probe.py` setzt bei Richtungstasten den internen `focus_index` abwechselnd auf Testfeld/Schließen. Der Diagnoseeintrag ist **kein Beweis für einen sichtbaren Fokuswechsel auf dem Display**. Nutzer konnte eine tatsächliche sichtbare Fokusbewegung nicht sicher erkennen.

**Reales Live-TV-Overlay (Fotos 2–3):**
- Auto-TV-Popup / TV-Einblendung **nicht gestartet**; XCMate-Stream erkannt **NEIN**; Video läuft **NEIN**.
- Globale Kodi-Tastenbelegung **INAKTIV**; Tastenübernahme nicht überprüft; Eingabepfad nicht aktiv; **0 native TV-Overlay-Tastenereignisse**.
- Diese Werte sind konsistent mit einem Popup-Test **ohne** Live-TV und **kein** fehlgeschlagener Live-TV-Fernbedienungstest. XML-Popup (`WindowXMLDialog`) und echtes Player-Overlay (`WindowDialog`) sind getrennte UIs.

**Bewertung:** GUI des unabhängigen XML-Testdialogs erfolgreich, Dienst aktiv; **noch kein Nachweis** für sichtbaren Fokus und Fernbedienung im tatsächlichen XCMate-Live-TV-Overlay. Zuletzt gemeldeter schwarzer Bildschirm nach VOD-Wiedergabe bleibt ein separater offener Fehler.

**Nächster kontrollierter Test:** Zuerst Version in Kodi-Add-on-Info feststellen. Falls `0.1.21`, normal über GS Media Repository auf `0.1.22` aktualisieren und Kodi neu starten. Ohne Aktivierung der globalen Keymap einen XCMate-Live-Sender manuell starten; Foto/Video des tatsächlichen Overlays mit Fokus und Verhalten bei Links/Hoch/Runter/OK/Zurück, danach sicher stoppen. Bei Fehlern anonymisiertes `kodi.log` und ggf. `kodi.old.log` sichern. Nicht aus dem bloßen Popup-Test auf funktionierende Live-TV-Steuerung schließen.

## Android-TV-Rückmeldung vom 18.10.2026 (Versionsstand noch NICHT bestätigt)

**Achtung: Der Nutzer vermutet, dass beim Test noch XCMate 0.1.21 installiert war.** Die untenstehenden Beobachtungen dürfen daher nicht als Erfolg oder Misserfolg der 0.1.22-Korrekturen gewertet werden, solange die auf dem Fernseher angezeigte Versionsnummer nicht geprüft ist.

- XCMate-Hauptmenü war wieder aufrufbar.
- In `Konfigurieren` öffnete sich die EPG-Verwaltung, und eine Meldung bestätigte den **Start** eines Hintergrunddownloads. Ob XMLTV-Dateien vollständig geladen und korrekt zugeordnet wurden, ist noch unbestätigt.
- `Neueste Filme` zeigte eine Liste; ein Film ließ sich starten und abspielen.
- Bei der Rückkehr bzw. beim Versuch, die VOD-Filmwiedergabe zu stoppen, erschien ein schwarzer Bildschirm und der Nutzer konnte nicht normal zurück navigieren. Ursache ungeklärt; **VOD/Player-Rückkehr als separaten offenen Fehler führen**, nicht vorschnell auf das Live-TV-Overlay zurückführen.
- Der separat gestartete XCMate-Popup-Diagnosetest zeigte ein Fenster. Tasteneingaben wurden durch wechselnde Kodi-Keycodes und akustisch wahrgenommen; **eine sichtbare Fokus-/Cursorbewegung war nicht eindeutig feststellbar**.
- Noch kein Diagnose-Screenshot bzw. Gerätelog zur Auswertung übermittelt. Ein Kodi-Neustart war wegen des schwarzen Bildschirms in Betracht gezogen worden.

**Diagnosedaten:** `popup_probe.py` schreibt Popup-Status, letzte Taste, Anzahl und Fokus in `xbmcgui.Window(10000)`-Properties. Diese **können beim vollständigen Kodi-Neustart verschwinden**. Bilder vor dem Neustart bevorzugen. Kodi-Protokoll und ggf. `kodi.old.log` nach dem Neustart prüfen; Logs vor einer Weitergabe von Zugangsdaten bereinigen.

**Nächster Test:** Zunächst Versionsnummer auf Android-TV kontrollieren. Falls noch 0.1.21, über das GS-Media-Kodi-Repository auf 0.1.22 aktualisieren, Kodi neu starten und Start/EPG/Popup/Fokus/VOD-Abbruch getrennt testen. Erst danach Folgereparatur auf einem Codex-Branch planen.

## Verbindliche Aufgaben für den Android-TV-Abnahmetest

1. Kodi aus dem GS-Media-Repository regulär auf XCMate `0.1.22` aktualisieren, Add-on- und Profildaten beibehalten und Kodi vollständig neu starten.
2. BINGIE MOD, Filmwiedergabe aus einem anderen Add-on, XCMate-Hauptmenü und XCMate-Konfiguration getrennt prüfen. Keine Endlos-Spinner.
3. XCMate-Live-Sender starten; sichtbare Senderliste, Fokus und Links/Rechts/Hoch/Runter/OK/Zurück/Menü prüfen; keine doppelten OK-Events.
4. Live-TV beenden und ein Video aus einem anderen Add-on öffnen; Tasten müssen normal reagieren, kein XCMate-Popup darf verbleiben.
5. EPG-Manager öffnen, kleine DE/AT/CH-Feeds einzeln laden und manuelle Senderzuordnungen nach Neustart wiederfinden. Große DE-Master-Datei wegen Limit gesondert bewerten.
6. Cache-Verzeichnis per Dateibrowser speichern und die Fallback-Funktion testen, ohne vorhandene Daten zu löschen.
7. Bei Problemen: `kodi.log` auf dem Android-TV auswerten, nur anonymisierte Fehlerstellen teilen, niemals Xtream-Credentials oder private Token ins Repository/Chat kopieren.

## Zusammenarbeit ChatGPT ↔ Codex – so bleibt alles nachvollziehbar

- **Codex arbeitet für künftige Korrekturen auf einem separaten Branch und erstellt einen Pull Request** mit Änderungszusammenfassung, Tests, tatsächlicher Version, Geräte-Risiken und Artefakten. Nicht unbemerkt `main` überschreiben.
- **Nach jedem Codex-Release** die aktuelle Version, Pull Request, Commit, GitHub-CI, öffentliches Paket, funktionale Änderungen, dokumentierte offene Gerätefehler und die nächste Aufgabe **in dieser Datei aktualisieren**. Den Überblick in `README.md` ebenfalls aktualisieren. Historische Berichte aufbewahren.
- **Für manuelle Statuskontrolle** GitHub-`main`, offene Pull Requests, CI-Runs, `addons.xml`, `addon.xml`, ZIP-Prüfsumme sowie diese Datei vergleichen. Erst danach von einer veröffentlichten Version sprechen.
- ChatGPT kann den fremden laufenden Codex-Chat **nicht direkt live mitlesen**. Sichtbar und überprüfbar sind hochgeladene Branches, PRs, Commits, Tests, Artefakte und Dokumentation. Nicht gepushte Arbeit und Android-TV-Funktionen können dadurch nicht bestätigt werden.
- **Kein ungeprüftes Weiterentwickeln parallel auf `main`**, solange Codex denselben Bereich bearbeitet. Laufende Android-Tests und echte Logs entscheiden die nächste Priorität.

## Geplante Prioritäten

- **P0:** Keine Kodi-weiten Hänger oder Eingriffe in BINGIE MOD, korrekter Add-on-Start.
- **P1:** Fernbedienung und sichtbarer Fokus/Popup im Kodi-Live-TV.
- **P2:** EPG-Quellen/EPG-ID-Matching und manuelle Zuordnung, speziell Sky und RTLup.
- **P3:** Cache-Sicherheit, Profilpersistenz, ressourcenschonende große XMLTV-Feeds.
- **P4:** Freigegebenes grafisches Design, Farben und Komfortfunktionen.

**Nächster Schritt:** Erstes reguläres GS-Media-Repository-Update auf `0.1.22` auf dem Fernseher und protokollierte Geräteabnahme, bevor ein P0/P1-Fehler als behoben geschlossen wird.
