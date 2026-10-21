# XCMate 0.1.29.8 – Fokus, Back und Kodi-Aktionsrouting

21.10.2026. Basis: regulär veröffentlichtes 0.1.29.7, main `bf6c88883428a97f53818ac7b9f95c41ea9f81ba`. Neuer **isolierter Testkandidat**, keine Merge-/Release-/Repositoryupdate-Freigabe. Primär Kodi 21.2 / Android 13 / RK3528 ARM32 / Titan BINGIE MOD 2.2.3, zusätzlich Kodi 21.3 / Estuary.

## Befund und korrigierte Interpretation

[#73](https://github.com/artattakk-creator/kodi-noodleprivate/issues/73) dokumentiert die reale 0.1.29.7-Regression: Kategorien→Landing funktioniert, Landing→Home ist unzuverlässig; Serien-Neuöffnung endet teils mit schwarzem Bild/drei Punkten. Nachgelieferte private Logs wurden in den öffentlichen Issue-Kommentaren ausgewertet: acht ungültige Fokusversuche auf Control 120, Home-Directoryfehler und SERIES `WAIT_MODAL → MODAL_TIMEOUT → WindowStartError/START_FAILED` nach 15 Sekunden. Die Originaldateien wurden in diesem Auftrag nicht erneut bereitgestellt und werden nicht veröffentlicht.

**Verbindliche Nutzerkorrektur:** Die zwei Home-Aufrufe um 22:50:04 folgten **zwei bewussten Back-Tastendrücken**. Sie beweisen keinen selbständig erzeugten Doppelaufruf. Der Fehler ist der unzuverlässige erste Rückschritt und der unsichere Zustand bei weiteren echten Eingaben. Neue Diagnose trennt deshalb Key-ID, monotone Zeit, Ansichtsmodus, kurzlebige Dispatch-ID und Owner-Thread.

### Belegte Codefehler und Grenzen der Root-Cause

1. `XCMateMedia.xml` erzwang den Landing-Kategorienbutton 120 als Default; `_show()` verbarg ihn außerhalb der Landingpage. Python leitete Fokusziele ungeprüft weiter. Zusätzlich konnten leere Datenlisten/Favoriten oder die native Headernavigation auf einen nicht verfügbaren Control führen. Das ist ein konkreter Fokusvertragsfehler und passt zu den acht Logmeldungen.
2. Home verlinkte Medien-/Guidefenster als **Verzeichnisse**. Diese Route schloss eine neue leere Directory ab und aktivierte dann WindowXML. Native `Window.close()` navigiert zum zuvor aktiven Kodi-Fenster; dieses besaß weiterhin den Medien-Routenpfad. Danach folgte ein weiterer `Container.Update(Home,replace)`. Diese Kombination macht den gewünschten Home-Rückweg von einer zweiten, asynchronen Containeroperation abhängig und lässt Navigation und Fensterende überlappen. Sie wird durch eine explizite Aktion-/Directory-Trennung ersetzt.
3. Die vier Popup-Routen [#75](https://github.com/artattakk-creator/kodi-noodleprivate/issues/75) meldeten einen erfolgreichen Dialog mit `succeeded=False` als Directoryfehler. Dies ist unabhängig von SQLite-Integrität und vom Recorderbackend.
4. **Unbekannt bleibt die Identität des damals blockierenden Modal-Dialogs.** Ein 15-s-Timeout beweist einen aktiven Dialog, nicht seine Herkunft oder eine monokausale Erklärung des gesamten Geräte-Freezes. Native Android-Wirkung des neuen Kandidaten muss geprüft werden; Hosttests sind kein Nachweis dafür.

## Änderung 0.1.29.8

- Medien-/Guideeinträge und reine Diagnose-/Settingsaktionen sind **nicht-folder, nicht-playable Pluginitems**. Kodi `CGUIMediaWindow::OnClick()` ruft hierfür `CPluginDirectory::RunScriptWithParams()` auf (RunPlugin-Kontext, Handle -1). Die bisherige Home-Directory bleibt darunter erhalten. Bestehende Live-/Player-Routen werden nicht verändert.
- **Kein Home-Container.Update beim Schließen** von MediaWindow/GuideWindow. Landing-Back schließt zur bereits vorhandenen Home-Ansicht. Suchwechsel werden erst nach dem vollständigen Window-Lauf ausgelöst, nicht aus dem Close-Callback heraus.
- Alte Verzeichnislinks/Bookmarks bleiben kompatibel: Directory genau einmal erfolgreich fertigstellen und **vor** Aktivierung einmal auf eine Home-Route mit kurzlebiger Navigationskennung wechseln. Erst nach passendem `Container.FolderPath` aktivieren; nach höchstens fünf Sekunden/bei Kodi-Abbruch ohne Windowstart zurückkehren. Externe Aktionseinstiege außerhalb des XCMate-Home werden entsprechend vorab auf Home verankert. Home selbst öffnet dabei kein weiteres WindowXML; keine Rekursion.
- Eine **nichtblockierende prozessübergreifende Dateisperre** schützt den gesamten nativen Fensterlebenszyklus. Ein konkurrierender Aufruf startet kein zweites Fenster und wartet nicht hinter einem vorhandenen Owner. Android/Linux `flock` ist Voraussetzung dieses sicheren Fensterstarts.
- Der stets vorhandene Suchheader 400 ist der sichere native XML-Default. Python bestimmt danach den tatsächlich gültigen Fokus je Ansicht, Datenstand und letzter Position. Versteckte, leere oder deaktivierte Ziele werden übersprungen. Native Navigationsverbindungen führen nur zu gültigen Controls. Für Enabled wird **Kodis `Control.IsEnabled(id)`-Bedingung** verwendet; einen Python-`Control.isEnabled()`-Getter gibt es in den geprüften Omega-Headern nicht.
- Gruppen-/Posterwand-/Detail-/Staffel-/Episoden-Back führt jeweils eine Ebene zurück. Aus der maximierten Posterwand geht es zuerst zur Gruppenansicht. Kategorieheader, Favoritenrail, Gridposition und gewählte Staffel werden bei Rückkehr bewahrt. Keine Katalog-Neuindizierung beim Back.
- Beim Home-Übergang behält das laufende WindowXML **150 ms (drei reguläre Pumpintervalle)** die Eingabehoheit. Weitere echte Eingaben in diesem Übergang werden kontrolliert verworfen, bevor der native Close Home freigibt. Kein erneuter Fensterstart und kein zweiter Containerwechsel. Es ist keine Behauptung, zwei bewusste Tastendrücke seien ein automatisch dupliziertes Event. Ein späterer bewusster Back auf sichtbarem Home darf Kodi verlassen.
- Nach Close oder während des Home-Übergangs werden keine neuen Control-/Click-/Back-Operationen mehr ausgeführt. Späte Workerresultate bleiben generationgebunden; bestehende Owner-Pump bleibt erhalten.
- Modal-/Init-Warten bleibt endlich. Bei WindowStartError bleibt Home verfügbar und es gibt eine nichtmodale Erklärung statt eines neuen rekursiven Startversuchs. WINDOW_STATE protokolliert numerische aktive Fenster-/Dialog-ID und Thread; keine fremden Dialoge schließen. Vor erfolgreicher nativer Aktivierung erfolgt kein fremdes `PreviousWindow` durch Fehlerbereinigung.
- Popup-Routen schließen bei einem tatsächlichen Directory-Aufruf korrekt und höchstens einmal ab; im RunPlugin-Kontext gibt es keine Directory abzuschließen. Ungültige Portal-/Medientyp-/Startsenderpfade und nicht unterstützter Playlisteditor bleiben echte Fehlerfälle. Kein pauschales Ersetzen sämtlicher `_end(False)`.

Geänderte Runtime-Komponenten: `window_navigation.py` neu, `home_menu.py`, `app_routes.py`, `media_window.py`, `guide_window.py`, `owner_dispatch.py`, `boot_diagnostics.py`, Media-XML, EN/DE-Erklärung und Manifest/Changelog. **Keine Änderung** an Settingsdefinition/Standardbudgets, Artwork-/EPG-Datenhaltung/Dedup, Player-/Live-/Remote-Modulen, Portalen, Profilen oder Keymaps. Vorhandene Bilder werden weder migriert noch gelöscht.

## Automatisierte Prüfung und Kodi-Vertrag

Neue Fälle prüfen native Default-/sichtbare-/deaktivierte Controls, leere Rails, zwei bewusste Back-Eingaben einschließlich des Pump-Übergangs, 10× Film- und 10× Serienzyklen, Staffelfokus, prozessgetrennte Fensterbesitzer, Legacy-Anchor vor Show, Abbruch/Modalfehler-Fallback, jede Popup-Route mit positivem und negativem Handle, echte Fehlerpfade und Suchwechsel erst nach Close. Bestehende Tests für Stop/Resume/Ownership, EPG-Dedup/Back, Fensterstart, Quellen/Setup, große Kataloge und Datenpersistenz bleiben aktiv.

Native Referenzen: [Kodi 21.2 CGUIMediaWindow](https://github.com/xbmc/xbmc/blob/21.2-Omega/xbmc/windows/GUIMediaWindow.cpp), [Window.show/close](https://github.com/xbmc/xbmc/blob/21.2-Omega/xbmc/interfaces/legacy/Window.cpp), [Control](https://github.com/xbmc/xbmc/blob/21.2-Omega/xbmc/interfaces/legacy/Control.h), [Control.IsEnabled](https://github.com/xbmc/xbmc/blob/21.2-Omega/xbmc/GUIInfoManager.cpp). Control.h ist zwischen 21.2 und 21.3 byteidentisch. Vollständige finale Suite, ZIP/SHA und Source-/Syntax-/Reproduktionsnachweise werden im [Maschinenbericht](TESTERGEBNISSE_0298_NAVIGATION.json) festgehalten. **Android des Kandidaten: NOT_RUN.**

## Android-Abnahme – zuerst genau dieser Hotfix

1. Funktionierendes Vollbackup und 0.1.29.6-Rückfall-ZIP behalten. 0.1.29.8-Test-ZIP über bestehende Add-on-ID installieren, Kodi regulär neu starten. Keine Neuinstallation, keine Quellen-/Portal-/Daten-/Cachelöschung.
2. Filme: Home→Landing→Kategorien→Gruppe/Poster→Details. Mit einzelnen Back-Eingaben jeweils eine Ebene zurück, schließlich **einmal** Landing→Home. Zehnmal wiederholen; Fokus und Scrollposition prüfen. Kategorienheader soll bei Rückkehr wieder erreichbar sein.
3. Serien: analog, zusätzlich Staffeln/Folgen, zweite Staffel auswählen→Folgen→Back stellt zweite Staffel wieder her. Zehnmal wiederholen, Serien sofort erneut öffnen. Bei leerem Favoriten-/Weitersehenbereich und fehlenden Postern weiter bedienbar.
4. **Zwei bewusste schnelle Back-Eingaben** aus Landing getrennt vom Einzel-Back-Test prüfen. Während des Übergangs kein Kodi-Exit/Reload/zweites Fenster; danach sichtbares Home. Erst ein weiterer bewusster Back auf Home darf Kodi verlassen. Nicht nachträglich als internen Doppelaufruf interpretieren.
5. EPG wiederholt öffnen/Details/Back→Home. Film und Episode starten→Playback verlassen: Bild und Ton stoppen, Resume bleibt. Bloßes Schließen eines Live-Overlays stoppt Live-TV weiterhin nicht pauschal. Live-Senderwechsel, OK/OK/Down/Links/Links, fremde Add-ons prüfen.
6. Unter Einstellungen art_status/art_retry/DB-Prüfung/Recorderprüfung/Darstellung/Sprache/EPG-Timer/Quellenstatus/Über/Widget-Hilfe jeweils öffnen und mit Back schließen. Keine neuen GetDirectory-Fehler. **Keinen 17k-Artwork-Retry zum Test erzwingen:** Budgetproblem ist separat; eine Ansicht prüfen genügt.
7. Mindestens 20 Minuten gemischte Navigation, Kodi-Neustart, BINGIE/Estuary und 720p/1080p; 21.3 zusätzlich. Keine Control-120-Fokuswarnungen, normalen Modal-Timeouts/START_FAILED, schwarzen Fenster oder endlosen Spinner. Ein absichtlich offener fremder Dialog muss erhalten bleiben, sein Abbruch/Fallback darf Kodi nicht blockieren.
8. Bei Befund nur feste NAV/WINDOW/BOOT-Codes, Modus, Key-ID, Dispatch-ID, numerische Fenster-ID und Zeitfolge teilen. Private Original-Logs/Trakt-Bearer/Portal-/SMB-URLs nicht auf GitHub. Der damalige unbekannte Dialog lässt sich erst anhand neuer WINDOW_STATE-Marker genauer zuordnen.

## Folgeschritte und Freigabegrenze

**#74 UI:** eigener Folgebranch nach dieser Hotfixbasis. Kategorien/Suche oben, Reihenfolge Weitersehen→Favoriten→Neu, größere echte 2:3-Poster mit zweizeiligen Titeln und vertikalem Rail-Scrolling. Vorhandene Theme-IDs/-Hooks beibehalten. Kein ungeprüfter Großlayoutumbau im Hotfix.

**#41 Artwork:** eigener Featureentwurf/-branch, siehe [konkreter Implementierungsplan](ARTWORK_SPEICHER_AUSBAU_DE.md). Vorhandenes 512-MiB-Budget bleibt in 0.1.29.8 unverändert. 514/512 MiB ist eine interne Quotaüberschreitung, kein Nachweis physisch vollen Flashs oder neuer DB-Korruption.

**#50 Integration:** erst nach positiver Android-Abnahme der Navigation neue Hotfix-/UI-/Artwork-Änderungen einzeln mit PR #50 abgleichen. Native Lifecycle-/Back-/Action-Einstiege und Themepräsentation sauber kombinieren; 98 Originalgrafiken/106 Keys erhalten. Neue vollständige Core-/Theme-Builds/Tests und Stock/Theme-Geräteabnahme vor Freigabe. Der bestehende 0.1.30.1-Head wird in diesem Hotfix nicht ungefragt weitergemergt.

Kein Issue geschlossen, kein produktiver Index verändert. 0.1.29.7 bleibt unveränderte veröffentlichte Basis mit negativem P0-Gerätebefund, 0.1.29.6 als Rückfall. Testkandidat ≠ Android-abgenommen ≠ Release.
