# XCMate 0.1.29.33 – Busy-Handoff, Fokus und typisierte Suchtreffer

24.10.2026 · Basis main `6c1b9c34b547764523fba295e449821513c8f647`, Add-on .32. Vollständig gelesen: .32-Logforensik, .32-Nutzerabnahme, .33-Startauftrag, ursprüngliche .31-Forensik und .32-Testplan; #140/#143; separater Folgeauftrag #98; ergänzender Suchdarstellungsauftrag des Nutzers. **Dieser Kandidat erweitert ausschließlich die Suche. #98 ist noch nicht implementiert.**

## Beleg und Architektur

.32-Gerätetraces zeigen dreimal `GUIDE_CLOSED → WAIT_RELEASE → RELEASE_TIMEOUT`, Fenster 10025/Dialog **10138**, ohne SEARCH_OPEN. Die Modal-Abfrage blockiert somit nachweislich den Öffnungspfad. Nicht abschließend bewiesen ist, welcher Kodi-Aufruf den Busy-Dialog hält. Drei vorab geschriebene Hosttests scheitern auf unveränderter .32: fehlende Fortsetzung im Busy-Fall, unsichtbares XML-Medienstandardziel 120 sowie alte Suchbutton-Navigation 400→120 während Visibility-Lag.

Kodi-21.2-API-Abgleich, Tag `21.2-Omega`:

- [AddonBuiltins.cpp, RunScript](https://github.com/xbmc/xbmc/blob/21.2-Omega/xbmc/interfaces/builtins/AddonBuiltins.cpp): verwendet `CScriptInvocationManager::ExecuteAsync` (Zeile 281). Das ist eine eigene Kodi-Skriptinvokation, kein Python-Timer und keine GUI-Arbeit auf einem Datenworker.
- [WindowXML.cpp](https://github.com/xbmc/xbmc/blob/21.2-Omega/xbmc/interfaces/legacy/WindowXML.cpp): native Window-Initialisierung läuft vor dem Python-onInit-Callback (Zeilen 319 ff.); sichere XML-Standardziele sind daher zusätzlich zu Python-Fokusprüfungen erforderlich.
- [PluginDirectory.cpp](https://github.com/xbmc/xbmc/blob/21.2-Omega/xbmc/filesystem/PluginDirectory.cpp) / [ScriptRunner.cpp](https://github.com/xbmc/xbmc/blob/21.2-Omega/xbmc/interfaces/generic/ScriptRunner.cpp): Plugin-/Skript- und Busy-Warteverträge getrennt betrachten. Nicht behaupten, jeder Action-Handle erzeuge synchron denselben Busy-Zyklus.

**Neuer Busy-Pfad:** Wenn das eigene alte Guide-Fenster tatsächlich geschlossen ist und Kodi exakt den modalen Busy-Dialog 10138 meldet, gibt der aktuelle Owner nur einen `SearchTransfer` zurück. Die äußere Navigation-Lease endet. Erst `after_close` plant `RunScript` mit festem Skriptpfad und zufälligem Einmaltoken; die ursprüngliche Ausführung kann enden. Die neue Invokation nimmt eine eigene Navigation-Lease und wartet weiterhin auf echte Freigabe, bevor sie das unveränderte native SearchWindow öffnet. Der Timeout wurde nicht erhöht; die Modalprüfung und der Owner-Pump bleiben bestehen. **Keine Dialog.Close-/erzwungene Home-/ActivateWindow-Kette, kein pauschaler Modal-Bypass.**

Token und UI-Snapshot liegen nur in Window(10000)-Properties, nicht in Dateien/DB. 15-s-TTL, Größenlimit, Einmalverbrauch und „neueste Anforderung gewinnt“; Quelle/Portal/Spielersession und aktueller Unterbau werden vor Öffnung erneut geprüft. Fremder Owner, anderer Player/Ordner/Portal, Shutdown, echte fremde Modals oder abgelaufene Requests werden verworfen und als feste BLOCK-Phase erfasst. Beim regulären Pfad ohne Busy bleibt die direkte Owner-Übergabe erhalten. Guide-Back stellt weiterhin Gruppe/Tag/Zeile/Zeit/Fokus aus demselben UI-Snapshot wieder her. Playback läuft ausschließlich über den bisherigen Handoff nach Freigabe der neuen Lease.

Root-global_search erhält denselben Busy-Ausweg, auch bei positivem Directory-Handle: Directory einmal vollständig beenden, im neuen Owner den tatsächlich fertigen sichtbaren global_search-Container prüfen. Keine zusätzliche Verzeichnis-Suchoberfläche.

## Fokus und Ergebnisdarstellung

- Medien-XML nutzt den stets sichtbaren Suchbutton **400** als nativen Standard; großer Guide **314**, auch in Gruppen sichtbar/bedienbar. Die alten Defaults 120/312 können in Such-/Gruppenansichten unsichtbar sein. Python stellt danach den semantischen Modusfokus wieder her.
- Im Suchmodus werden alle Such-Navigation-Edges vor einer deferrierten Fokussetzung zunächst auf sichere Selbstverweise gestellt. Damit bleibt bei einem Visibility-Lag kein alter Button-400→Landing-120-Pfad aktiv. Vorhandene visible/enabled-Prüfungen und begrenztes Deferring bleiben. Neue redigierte `[FOCUS]`-Events enthalten Ziel, semantische Zulässigkeit, native Visibility/Enabled und tatsächlichen Fokus; nur Zustandsänderungen loggen.
- Neue 100-Pixel-Zeilen im 720p-Koordinatensystem: Senderlogo links im Querformat, Film-/Serienposter im Hochformat, klarer Titel und separate Typ-/Metadatenzeile, vorhandener Neonfokus. Ausschließlich bestehende Grafikdateien; Originalicon/Splash/Themebilder unverändert.
- Live-Namensmatches können jetzt den ohnehin lokal ermittelten Jetzt-Titel anzeigen. **Matching, Trefferzählung und `_now_match` ändern sich nicht.** „Läuft jetzt“ ist Anzeige einer vorhandenen Sendung, kein zusätzlicher Programmtitel-Match. Jahr/Genre nur aus vorhandenen Katalogdaten; keine erfundenen Angaben.
- `search_results` enthält nur Darstellung. `local_art` liefert lokale Cachepfade oder typgerechte lokale Platzhalter; der vorhandene Artwork-Worker kann im Hintergrund arbeiten. Keine HTTP-/SQL-Aufrufe beim D-Pad. Bilder werden bei Cache-Revision auf bestehenden ListItems aktualisiert, ohne Listenreset/Fokusänderung. Unveränderte Partial-Ergebniszeilen werden nicht ständig neu aufgebaut.
- Renderer-Revision erzeugt neue abgeleitete XML-Pfade für bestehende Appearance-/Premium-Varianten, ohne alte Dateien/Bilder zu löschen. Keine Änderung am Kodi-/BINGIE-Skin oder Keymaps.

## Tests und Grenzen

**18 neue Busy-/Fokus-Tests plus 6 neue Suchdarstellungs-Tests.** Darunter Dreifach-Busy-Fall, realer Such-/Guide-Restore im Modell, Modal/Owner-/Player-/Portalwechsel, TTL/Replay, beide Handles, native Keyboard-Reinit, unveränderte Partial-Liste, lokale Logos/Cover/Placeholder und Bildaktualisierung ohne Fokusverlust. Historische Tests bleiben, nur explizite aktuelle Versions-/XML-Standardverträge werden angepasst. Keine Daten-/Player-Sicherheitsassertion entfernt.

Vollständiger Lauf/ZIP/SHA und Bestandsschutz werden im finalen Testbericht dokumentiert. **Hostsimulation ist kein Kodi-/Android-PASS.** Eine reale Entkopplung vom beobachteten Busy-Besitzer und Skin-/IR-Bedienbarkeit muss der Nutzer am Gerät prüfen.

[Android-Checkliste](ANDROID_ABNAHME_02933_DE.md): zunächst **nur A1–A3**, erst bei PASS die Darstellung **SEARCHUI-01–06** und gegebenenfalls erweitertes NAVSEARCH/REG. Alle neuen Felder NOT_TESTED. Historische .32-Werte 7 PASS/10 FAIL, .31/.30 und vierstündige MEM-PASS bleiben unverändert. Keine Downloads-/Recorder-Reparaturen.

## Separater Folgeauftrag #98 bleibt verbindlich

Vollständig übernommener Auftrag: `CODEX_UEBERGABE_EPG_ZUWEISEN_IM_GUIDE_20261024_DE.md`. Nach Android-Abnahme dieses Suchfixes und ausdrücklicher Main-Freigabe: eigener kumulativer Draft mit Sender-Kontextmenü auch bei leerem EPG, vollständiger paginierter Quell-/Kanalsuche, **stabiler source_id + channel_id** statt Quellenreihenfolge, echter schreibfreier Rastervorschau nur der markierten Zeile, Save/Cancel/Reset mit exaktem Restore, Legacy-Kompatibilität und MAP-01–11. Bestehende Merge-/Index-ID-Kollisionen müssen dabei tatsächlich behoben werden, nicht allein ein Menüpunkt ergänzt. Keine Version für #98 vorab reserviert und keine EPG-Quelle/Zuordnung in .33 geändert.

**Kein Merge, Release, Tag, Index-Publish oder Schließen von #140/#98. Private Kodi-Rohlogs bleiben privat.**
