# XCMate 0.1.29.6 – isolierter P0-Fensterstart-Hotfix

Stand 21.10.2026. Auftrag und Android-Regression: [Issue #67](https://github.com/artattakk-creator/kodi-noodleprivate/issues/67). 0.1.29.5 ist regulär veröffentlicht, auf der Box aber für EPG/Filme/Serien negativ getestet. Die gesicherte 0.1.29.4 bleibt die Rückfallbasis. Der Nutzer hat anschließend ausdrücklich den GitHub-Upload und die Bereitstellung als reguläres Kodi-Update freigegeben. Merge und Veröffentlichung erfolgen nach erfolgreicher CI; Android-Abnahme bleibt offen.

## Gemeinsame Fehlerursache und Gerätebeleg

Das bereitgestellte `kodi.log` bestätigt installierte **0.1.29.5**. Bei `guide_browser` und `movies_home` folgt auf `DIRECTORY_DONE` unmittelbar `GetDirectory - Error getting` / `CGUIMediaWindow::GetDirectory(...) failed`. Danach verweigert Kodi die Aktivierung von Fenster 13000/13001/13002: **`Activate of window '…' refused because there are active modal dialogs`**. Es gibt in diesem Ausschnitt keinen `XM-WINDOW-GUI-THREAD`-Nachweis und keinen entsprechenden Python-Traceback. Der Bericht des Nutzers umfasst zusätzlich Serien; deren Einstieg nutzt denselben MediaWindow-Pfad. Der genaue Typ des blockierenden modalen Dialogs ist im Log nicht benannt.

Der native Quellcode von **Kodi 21.3 Omega**, Commit `a3a448d26b8d560a65655dab2cd122994dc4e146`, erklärt auch den gehörten Ton:

- `PluginDirectory.cpp:195–215`: `EndOfDirectory` übernimmt den Erfolgswert und beendet die Directory-Anfrage.
- `ScriptRunner.cpp:176`: Das Ergebnis hängt an `IsSuccessful()`.
- `GUIMediaWindow.cpp:841–855`: Ein fehlgeschlagener Directory-Aufruf löst Previous-/Root-Fallback aus.
- `GUIWindowManager.cpp:866–873`: Bei einem aktiven modalen Dialog wird die Fensteraktivierung verweigert und **ACTION_ERROR** abgespielt. Genau diese Meldung steht im Geräte-Log.
- `Window.cpp:487–493`: `show()` aktiviert das Fenster. `doModal():658ff` verwendet ebenfalls `show()`. Ein reines Zurückwechseln zu `doModal()` beseitigt diese Aktivierungssperre nicht.
- `Monitor.cpp:39–62`: `waitForAbort` verarbeitet `MakePendingCalls`; `WindowXML.cpp:319–325` stellt natives `onInit` zu. Der sichere Owner-Pump ist grundsätzlich mit dieser API vereinbar.
- `GUIInfoManager.cpp:1926`: **`System.HasActiveModalDialog`** ist die in Kodi 21.3 registrierte Bedingung. Nicht die entfernte alte Bedingung `System.HasModalDialog` verwenden.

Die gemeinsame Regression ist damit am Fenster-Startübergang lokalisiert: 0.1.29.5 meldet die GUI-Menüroute vor Aktivierung als Directory-Fehler; Kodi fällt zurück und verweigert in diesem Zustand das Öffnen. Welcher native Dialog im Einzelfall aktiv war, bleibt offen. Hashes und Quelllinks stehen in [KODI_213_WINDOW_START_0296.json](KODI_213_WINDOW_START_0296.json). Das private Original-Log wird **nicht** ins Repository oder ZIP übernommen.

## Minimaler Verhaltensfix und Diagnose

1. Nur die beiden GUI-Routenblöcke in `app_routes.py` erhalten wie 0.1.29.4 wieder einen **erfolgreichen** Directory-Abschluss vor `open_guide/open_media`. Fehler-, Abbruch-, Player- und andere Routen bleiben unverändert. Der explizite Home-Rückweg aus 0.1.29.5 bleibt erhalten.
2. Der Owner wartet vor `show()` nicht blockierend in 50-ms-Schritten, solange `System.HasActiveModalDialog` wahr ist. Höchstens 15 Sekunden für diesen Aktivierungsübergang; Kodi-Abbruch wird beachtet. Keine zwangsweise Dialogschließung, kein `ActivateWindow(...,force)` und kein globaler Kodi-Eingriff.
3. Der bestehende Owner-Pump bleibt. Hintergrundjobs liefern ausschließlich Daten; keine Future-/Watcher-GUI-Updates werden wieder eingeführt. Vor dem nativen `onInit` werden keine Resultate oder Ticks angewendet. Bleibt `onInit` nach erfolgreichem `show()` 15 Sekunden aus, folgt ein diagnostizierter Startfehler. Diese Startgrenzen sind **keine Netzwerk-/Scan-Gesamtdeadline**.
4. Feste INFO-Marker **`[XCMate][WINDOW]`** mit `view=GUIDE/MOVIES/SERIES` zeigen Konstruktion, Konfiguration, modales Warten, Show, native Initialisierung, Abbruch und Schließen. Nur freigegebene Fehlerklassennamen; keine Exceptiontexte, Accounts, URLs, Titel oder Zugangsdaten.
5. Fehler aus nativem `onInit` werden gespeichert und am Owner sichtbar behandelt. Ein Close-Fehler ersetzt keinen vorangegangenen Startfehler. Ein noch nicht angezeigtes Fenster wird bei Abbruch/Fehler nur entsorgt: kein `Window.close()` und damit keine Navigation eines fremden Fensters.

Geändert: `addon.xml`, `changelog.txt`, `app_routes.py`, `owner_dispatch.py`, `guide_window.py`, `media_window.py`; Tests und dieser Bericht. Keine neue Funktion aus PR #50/0.1.30.1 übernommen. Kein Datenreset, keine Migration, keine Keymapänderung. Alle übrigen Add-on-Quellbytes, einschließlich `epg_events`, XMLTV-/Short-EPG-Resolver und Live-/Remote-Dateien, bleiben gegenüber 0.1.29.5 unverändert.

## Prüfungen

Die neuen Tests verwenden den tatsächlichen Python-`Router.dispatch` → `app_routes` → `GuideWindow/MediaWindow` mit echtem ThreadPoolExecutor und einem **Modell** verzögerter nativer Callbacks. Alle drei Menüpunkte, Directory-Erfolg vor Show, Back/Home genau einmal, Warten auf modalen Dialog, Modal-Timeout, Abbruch ohne Fremdfenster-Navigation, fehlendes/fehlerhaftes/spätes `onInit`, Konstruktion/Konfiguration, Thread-Guard und Originalfehler trotz Close-Fehler werden geprüft. Alle GUI-Updates bleiben am Owner. Keine Behauptung, dass das Python-Modell Kodis tatsächlichen Eventloop ausführt.

Gegenprobe mit unverändertem 0.1.29.5 scheitert an der erfolgreichen Directory-Vorbedingung in allen drei Menüpfaden. Zwei alte Tests hatten ausdrücklich `succeeded=False` gefordert; sie werden auf den korrigierten Vertrag umgestellt. Bestehende Dedup-/Matching-/Back-Tests bleiben bestehen. Ein Zwischenlauf deckte zusätzlich eine Testeinrückung auf; vor finaler Prüfung korrigiert. Drei lokale HTTP-Tests benötigen eine Loopback-Socketfreigabe; sie werden mit dieser Freigabe ausgeführt, nicht übersprungen oder durch Mocks ersetzt.

Finale Zähler, ZIP-Größe/SHA-256, Quellenvergleich und Status stehen in [TESTERGEBNISSE_0296_FENSTERSTART.json](TESTERGEBNISSE_0296_FENSTERSTART.json); vollständiger Lauf in [TESTLOG_0296_FENSTERSTART.txt](TESTLOG_0296_FENSTERSTART.txt). Der vollständige Repositorybuilder läuft in einer Scratch-Kopie. Nur das neue Core-ZIP und seine Prüfsumme werden in den Hotfixzweig übernommen. Produktive Archive, `addons.xml`, andere Add-ons und die lokale 0.1.30.1-Arbeit bleiben unberührt.

**Android 0.1.29.6 = NOT_RUN.** Der Gerätebeleg betrifft die Fehlerursache in 0.1.29.5, nicht die Abnahme des neuen Pakets.

## Installation und Android-Abnahme

1. Das vollständige EZ-Maintenance+-Backup von **0.1.29.4** behalten. Laufende Wiedergabe beenden.
2. Das **innere Add-on-ZIP `plugin.video.xtreammate-0.1.29.6.zip`** herunterladen. Nicht das GitHub-Quellcodearchiv installieren; ein Actions-Artefakt zuerst entpacken.
3. Kodi → Add-ons → Aus ZIP-Datei installieren. Über das bestehende XCMate installieren. Keine Deinstallation, kein Profil-/Cache-Löschen, kein neuer Portalimport und kein Vollscan als Voraussetzung.
4. Nach erfolgreicher Installation Kodi regulär beenden und neu starten. Add-on-Version 0.1.29.6 kontrollieren.
5. Zuerst **EPG, Filme und Serien jeweils einmal öffnen**. Falls eines weiterhin nicht öffnet, Test beenden und den Logabschnitt mit `[XCMate][WINDOW]` sowie den zugehörigen Kodi-Aktivierungsfehlern bereinigt bereitstellen. Nicht wiederholt Daten importieren.
6. Wenn alle drei öffnen: je **10 Öffnen-/Zurück-Zyklen**. EPG: Programme → Sender → XCMate-Home; Medien: Episode/Staffel/Details → Ausgangsansicht → Home. Kein leerer Bildschirm, keine erneute EPG-Startschleife. Auch schnelles Back während lokaler Datenarbeit prüfen.
7. Live-TV, OK/Links/Zurück, Senderwechsel, Startsender und vertraute Fernbedienungsbelegung prüfen. Die Live-Dateien wurden nicht verändert.
8. Dubletten am verfügbaren ProSieben-HEVC-Beispiel prüfen, unterschiedliche Episoden müssen getrennt bleiben. Manuelle Zuordnungen und HEVC-/Regional-Matching vergleichen.
9. Kodi erneut starten und Portale, aktivierte Gruppen, EPG-Quellen/Zuordnungen, Favoriten, Resume-/Serienfortschritt vergleichen. Titan BINGIE MOD und anschließend Estuary testen.

Alle neun Geräteprüfschritte sind für 0.1.29.6 zunächst **NOT_RUN**. Android-Freigabe bleibt beim Nutzer. Bei weiterhin gestörtem Fensterstart auf das vorhandene 0.1.29.4-Paket bzw. Backup zurückgreifen, ohne Add-on-Daten zu löschen; die reguläre 0.1.29.5 nicht blind erneut installieren. Keine Updates anderer Add-ons für diesen Test erforderlich.


## Abschließender lokaler Nachweis

**521/521 Tests bestanden**, 81,942 Sekunden, keine Fehler oder Skips. Zehn neue Starttests. Installierbares Core-ZIP: **389853 Bytes / 129 Dateien**, SHA-256 **`f8188f156b8d43d741706813ba6e9946d7f2be66b035e4977dadb32464afe40e`**. Syntax, CRC, Pfade, alle Quellbytes und unabhängiger zweiter kanonischer ZIP-Bau bestanden. Die unveränderten Live-/Remote-/Dedup-Module sind im Maschinenbericht gehasht.

**Historischer Zwischenstand vor ausdrücklicher Upload-/Updatefreigabe:** Die automatische Freigabeprüfung hat bereits das Erstellen des GitHub-Blobs für diese Test-ZIP abgelehnt, da sie den externen Artefaktupload unter die Vorgabe „keine automatische Veröffentlichung“ einordnet. Kein Remote-Branch oder Draft-PR erstellt, keine CI ausgelöst, kein Merge/Release/Produktivupdate. Lokales Paket und Anleitung sind fertig. Für die Bereitstellung in einem separaten GitHub-Testbranch/Draft-PR ist jetzt eine ausdrückliche Uploadfreigabe nötig; diese umfasst keinen Merge und kein Kodi-Repositoryupdate. Das private Kodi-Log wird nicht hochgeladen.


## Ausdrückliche Nutzerfreigabe zur Bereitstellung

Der Nutzer hat am 21.10.2026 ausdrücklich angewiesen: „Ja natürlich, lad den hoch. Der soll auf GitHub zu finden sein und auch per reguläres Update zu ziehen sein.“ Der zuvor abgelehnte Upload ist damit ausdrücklich genehmigt, einschließlich des für den regulären GS-Media-Updateweg erforderlichen Merges und Publish-Workflows. Keine erneute Rückfrage erforderlich. Die Geräteabnahme von 0.1.29.6 wird dadurch nicht als bestanden bezeichnet. Das private Original-Log bleibt lokal.
