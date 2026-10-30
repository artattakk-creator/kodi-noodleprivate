# XCMate .61 – Box B, zuerst nur die Senderleiste

Alle Geräteprüfungen: **ANDROID_NOT_TESTED**. Ergebnisse: PASS / FAIL / ÜBERSPRINGEN. Box A unverändert lassen. Installation als normales ZIP-Update; keine Deinstallation, kein Reset.

1. **B-61-01:** XCMate → Einstellungen → Aussehen und Darstellung → **BINGIE-Startseiten-Widgets einrichten** → **BINGIE-Home-Layout prüfen/vorbereiten**. Vorschau mit vier Dateien und SHA256 ansehen. Nur nach eigener Prüfung ausdrücklich zustimmen. Vorhandene Widgetverknüpfungen behalten. Bei bereits vorhandenem Adapter die angebotene einmalige Neugenerierung bestätigen. Auf BINGIE Home mindestens eine Senderkachel und sichtbaren Fernbedienungsfokus prüfen, dann bis zum letzten Sender der Startgruppe scrollen. Kein Token/EPG erforderlich.
2. **B-61-02:** Senderfokus ändert Hero, startet keine Wiedergabe. Ohne EPG Sendername und neutrales Bild; mit EPG Jetzt/Danach, Zeiten, Beschreibung und Fortschritt. OK startet bestehenden Player; Zurück wie bisher. Bei FAIL abbrechen und genaue Menü-/Bildschirmstufe melden.
3. **B-61-03:** Token-Dateiimport folgt im zweiten Commit. Im frühen P0-Zwischenpaket **ÜBERSPRINGEN**, kein TMDB-Token erforderlich.
4. **B-61-04:** Filme/Serien scrollbar, Cover und Aktualisierung erhalten. Neustart: Portale, Gruppen, Startsender, Favoriten, EPG-Zuweisungen und Widgetverknüpfungen erhalten.

## Wiederherstellung

Im selben Manager normal mit OK **Widget-Verknüpfung oder Layout wiederherstellen** wählen, passende Layoutsicherung auswählen und ausdrücklich bestätigen. Nur unverändert verifizierbare Ziele werden zurückgeschrieben; zwischenzeitliche fremde Änderungen werden blockiert. Danach einmalige native Skinshortcuts-Neugenerierung. Keine Cache-/Datenbanklöschung. Kein automatisches Zurücksetzen.
