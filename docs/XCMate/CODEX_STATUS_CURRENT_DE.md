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
