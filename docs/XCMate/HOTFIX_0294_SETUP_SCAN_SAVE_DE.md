# XCMate 0.1.29.4 – P0 Setup, lange Scans und Speichern

Stand **21.10.2026**. Neuer separater Branch `fix/xcmate-0294-setup-scan-save`, Grundlage **PR #52 / 0.1.29.3 / `32970a6688c17f0aebd6945873658e5b41a47c5a`**. PR #52 und seine Vergleichsversion bleiben erhalten. Unabhängig von Space-Premium-PR #50 und Repository-PR #51. **Kein Merge, Release oder produktives Repositoryupdate.**

[Vollständiger Nutzerauftrag](CODEX_AUFTRAG_0294_SETUP_SCAN_SAVE_DE.md) · [vor Implementierung dokumentierte Ursachen](HOTFIX_0294_ROOT_CAUSES_DE.md) · [Maschinenbericht](TESTERGEBNISSE_0294_SETUP_SCAN_SAVE.json) · [Android-/IR-/Installationsplan](ANDROID_TESTPLAN_0294_SETUP_SCAN_SAVE_DE.md).

## Belegte Ursachen und Änderungen

**Threadfehler:** Der alte Future-Callback lief im echten Executor-Thread und rief Controls, Ergebnisrenderer sowie `SetupWindow.saved()`/`WindowXML.close()` auf. Ein Python-RLock verschiebt diese Operationen nicht auf den Kodi-Window-eigenen Python-Thread. Alte Queue-Fixtures führten Jobs im Testthread aus und verdeckten dies. Jetzt liefern Worker Daten und höchstens einen koaleszierten Fortschrittswert. `WorkWindow.run()` nutzt öffentliche `Window.show()`- und `Monitor.waitForAbort(0.05)`-APIs; der Owner-Pump übernimmt Resultate auch ohne Tastendruck. Native onInit-/Action-/Click-Callbacks bleiben Kodi überlassen. Der einzige Future-Callback räumt nach bereits geschlossenem Fenster Daten auf, verändert keine GUI. Close/Cancel warten nicht auf den Worker; spätes Ergebnis wird verworfen, Staging genau einmal bereinigt.

**API-Nachweis:** Im gepinnten Kodi **21.3 Omega** (`a3a448d26b8d560a65655dab2cd122994dc4e146`) ruft Monitor.cpp während waitForAbort `MakePendingCalls()` auf; CallbackHandler prüft den ursprünglichen Python-ThreadState. Der öffentliche show+Monitor-Pump verwendet diese Dispatchfunktion und ergänzt die bisher fehlende Future-Verarbeitung im Owner. Control.cpp gibt bei `getListItem()` das ursprüngliche gemeinsame ListItem zurück; Property-/Art-Änderung benötigt kein Neubinden der Liste. Heruntergeladene Quellen und SHA-256 stehen im [SDK-Nachweis](KODI_213_SETUP_THREAD_API_0294.json). Das ist kein Nachweis realer Android-Renderleistung.

**Gruppenwahl:** Separate native Listen **100/101/102** für Live-TV/Filme/Serien, eigene Reiter oben, aktive Art über dauerhafte Markierung. Fünf kleine, reproduzierbare eigene PNGs für Checkbox an/aus, Fokus, Normal-/Auswahlgrund; keine skinabhängige `white.png`-Referenz im Assistenten und keine Unicode-Checkboxen. Fokusbalken über gesamte Zeile, dunkle Schrift auf Türkis, Checkboxen mit eigenem dunklem Innenfeld. Aktivierte Zeilen bleiben auch außerhalb des Fokus erkennbar. Reale ListItem-Properties/Art steuern die Darstellung. Zähler, Alle auswählen/Alle abwählen, Zurück/Weiter/Abbrechen sowie expliziter Leerzustand. Kein `reset/addItems/selectItem` beim Einzel-Toggle; bestehende Listen bleiben auch beim Bereichswechsel bestehen. Auswahl ist je Art getrennt. Nativen Links/Rechts/Hoch/Runter/OK nicht noch einmal in Python abspielen.

Der private M3U-Editor verwendet ebenfalls WorkWindow; sein Einstieg nutzt deshalb denselben sicheren Pump. Sein bisheriges Layout wurde als `XCMatePlaylistEditor.xml` bytegleich vom alten Layout getrennt, damit die neue Drei-Reiter-Anordnung nicht seine anderen Aktionen verschiebt. Kein Umbau seiner Bearbeitungsfunktionen.

**Lange Scans:** Die Gesamtdeadlines aus `http_stream()`, Stalker-Gruppenimport und XMLTV-Parser sind standardmäßig entfernt; auch der explizite 300-s-Aufruf in stream_epg ist entfernt. Connect-/Read-Timeout bleibt **15 s**, zusätzlicher Decoder-Inaktivitätsschutz **30 s**. Zeit für den nachfolgenden SQLite-Verbrauch zählt nicht als Netzwerkinaktivität. Kleine HTTP-/Auth-/Metadata-/Short-EPG-Aufrufe und ausdrücklich gewählte Zeitbudgets bleiben begrenzt. GZIP-/JSON-/XML-Feld-/Chunk-/Nestinggrenzen, Speicherplatzreserve und Abbruch pro Chunk/Eintrag bleiben. Stalker erkennt zusätzlich A/B/A-Seitenzyklen über eine temporäre SQLite-Fingerprinttabelle statt einer unbegrenzt wachsenden Python-Menge. Ein Alias p=0/p=1 bleibt unterstützt.

Der Status meldet echte gelesene und per Batch gespeicherte Elemente samt Bereich/Gruppe; während unbekannter Gesamtdauer ist der Prozentbalken ausgeblendet. 100 Prozent erst nach abgeschlossenem Scan. Keine 300-s-Abschaltung bei weiterem Fortschritt, aber auch kein Abschalten der Verbindungs-/Sicherheitsgrenzen.

**Staging und Speichern:** Jeder erneute Scan beginnt mit frischen eigenen Staging-Index-/Guide-Dateien; M3U-Arbeitskopie bleibt erhalten. Auswahlsignatur und scanned-Status verhindern Speichern nach ungescannten Änderungen. Save-Lock verhindert gleichzeitigen/wiederholten Save. Große neue-ID-Batches werden vor dem Profil-Konfigurationslock kopiert; niemand sieht einen Account, bevor die Portalliste veröffentlicht ist. SQLite-Verbindungen entstehen und schließen im jeweils arbeitenden Thread, Transaktionen sind Batch-begrenzt. Konfiguration, Prüfung und Veröffentlichung stehen unter dem reentranten Profil-Schreiblock.

Frische permanente Reads prüfen Inhaltszahlen (2400/7/9 im Test), erlaubte Kategoriezuordnung, alle drei Gruppenmengen/known/auto_new=false, include-Flags, EPG-Quellen/Mappings, SQLite quick_check und bei optionalem Guide dessen persistente Tabellenzahlen. Nach Portalveröffentlichung werden vollständige Accountfelder und Konfiguration nochmals aus Disk geprüft; Erfolg erst danach. Readback-Fehler entfernen nur die neue ID und deren neue Konfigurations-/Index-/Guide-/Cache-/M3U-Dateien, keine alten Accounts, globalen Caches oder Quellen. Falls ein Profil/DB selbst nicht mehr lesbar ist, wird kein globaler Reset versucht: Fehlercode `XM-SETUP-ROLLBACK`, kein Erfolg behauptet.

Optionaler Now/Next-Kompatibilitätscache wird ohne Worker-GUI-Benachrichtigung geschrieben; bisherige Aufrufer von `_save_disk` behalten ihr Standardverhalten. Der schnelle Cache wird beim Save für höchstens 256 erste Sender vorgewärmt, mit Abbruchprüfung. **Alle** importierten Sendungen bleiben im vollständigen persistenten Guide; andere sichtbare Sender können daraus nachgeladen werden. Kein minutenlanges Cache-Vorwärmen für alle großen Gruppen. Nach Save wird derselbe gerade abgeschlossene Katalogscan nicht sofort erneut angefordert.

Neue sichere Codes `XM-SETUP-VERIFY`, `XM-SETUP-SAVE-BUSY`, `XM-SETUP-RESCAN`, `XM-SETUP-ROLLBACK` ergänzen vorhandene Auth-/Netz-/Eingabecodes. Status/Kodi-Log verwenden Phase, Typ und freigegebenen Code, keine Passwörter, Tokens oder kompletten Stream-URLs. Nutzerdaten gehören nicht in öffentliche Testberichte.

## Tests und Grenzen

**496/496 Gesamttests bestanden, 68,994 s**, keine Fehler/Failures/Skips. **20 neue Hotfix-Tests**, zusätzlich fokussierter Lauf **49/49**, 5,034 s. Vollständiger Repositorybau und compileall in isolierter Kopie erfolgreich. Produktivindex und fremde Add-on-Dateien nicht zurückkopiert.

Drei Tests auf unveränderter Baseline 0.1.29.3 scheitern nachweislich: echter Worker-GUI-Zugriff, fortlaufender HTTP-Import über 300 s und falsche Speicheranzahl trotzdem Erfolg. Dieselben Fälle bestehen jetzt. Neue Tests nutzen echte Executor-Threads mit Owner-Guards, native WindowXML-Ereignisse, keinen künstlichen WindowDialog-onInit-Aufruf, Completion ohne Tastendruck, Cancel/späte Ergebnisse und Cleanup genau einmal.

2400 Sender plus 7 Filme/9 Serien werden tatsächlich in SQLite importiert, gespeichert und über neu geladene Module/frische Verbindungen eingelesen. Dies simuliert den Interpreter-Neustart, **kein realer Kodi-/Android-Neustart**. Separate Gruppen, Rescan nach Abwahl, Counts/Integrität, Fehler vor/nach Veröffentlichung, Save-Wiederholung sowie optionaler EPG-/Cache-Rollback sind geprüft. Fortlaufendes HTTP-Streaming/JSON-Parsing über simulierte **20 Minuten**, Stalker und XMLTV über 300 s, Read-Inaktivität/Timeout/Cancel und Seitenzyklen ebenfalls geprüft. Die vorhandene Gesamtsuite enthält weiterhin echte lokale HTTP-/SQLite-Großtests mit 200005 Filmen und Serien sowie großem XMLTV; keine abgeschwächten Freeze-Referenzen.

Der erste Gesamtlauf meldete zwei erwartete alte Versionsassertionen (0.1.29.3); beide wurden auf das tatsächlich gelieferte Ziel 0.1.29.4 aktualisiert. Historische GUI-Fixtures erhielten die tatsächlichen ListItem-/Window-Properties und einen expliziten Owner-Pump nach Job-Ende. Keine Callback-Ausnahme wird als Testerfolg verschluckt.

**Der Android-Speichern-Absturz ist ohne Crashlog nicht abschließend kausal erklärt.** Unsichere Worker-GUI-Aufrufe und die drei Regressionen sind belegt und korrigiert. Echter Kodi-21.3-/ARM32-/IR-/BINGIE-/Estuary-Test, natives Rendering, Audio/Video und kompletter Kodi-Neustart bleiben **NOT_RUN**.

## Geprüfte manuelle Installationsdateien

| Version | Bytes / Dateien | SHA-256 |
|---|---|---|
| [0.1.29.4 Test-ZIP](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.4.zip) | 382936 / 126 | `7b914eb02756751978df5b80f0cf574760fc9d2215cb06ed4b7fe9123534f69f` |
| [0.1.29.3 Vergleich](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.3.zip) | 376662 / 120 | `3c1f54a6d4ffdf6c069c483ade06867c18ff528414724a13656011f3d30189af` |

CRC, Pfade, keine Duplikate/Symlinks/Profil-/DB-/Log-/Bytecode-Dateien, komplette Dateiliste und **jeder ZIP-Bytevergleich mit aktuellem Quellcode** bestanden. Zweiter kanonischer Bau ist bytegleich. Alle fünf PNGs vollständig decodiert. 0.1.29.3 wurde aus dem unveränderten PR-52-Commit reproduziert und stimmt mit dessen veröffentlichtem **CI-Prüfsummenwert** überein; kein veränderter Inhalt unter derselben Version.

Für GS Media/Neo Dark ist die 0.1.29.4-ZIP ausschließlich als manuell ausgewählte Testdatei im Entwicklungsbranch vorbereitet. Kein produktiver addons.xml-Eintrag und keine automatische Updateveröffentlichung. CI-Artefakt zuerst entpacken; nur die innere `plugin.video.xtreammate-0.1.29.4.zip` in Kodis Add-on-ZIP-Installer wählen. Nicht den Quellcode-ZIP oder äußeren Actions-Container installieren.

**CI und Draft-PR:** Nach Push im [Maschinenbericht](TESTERGEBNISSE_0294_SETUP_SCAN_SAVE.json) zu ergänzen. CI-Publish muss SKIPPED bleiben. Baseline/main/PR #50 werden nicht verändert. Alle Freigaben bleiben beim Benutzer.
