# .93 – Android-Abnahme, zunächst ANDROID_NOT_TESTED

Nur freigegebene Testbox, kumulativ aus ZIP; Box A unangetastet. Profil/Quellen/Token/Widgets sichern, keine Neuinstallation und keinen 48-Komponenten-Installer starten. Regulär/Pilot/NeoDark3 nicht aktualisiert. Version, SHA, Gerät, Kodi-Version und Uhrzeit notieren. Private Rohlogs niemals öffentlich hochladen.

| ID | Ablauf und prüfbares Soll | Status |
|---|---|---|
| PLAY93-01 | Startsender → einmal Back/Stop aus reinem Live-Vollbild. Genau ein Stop, echte native Queue-ACK, bedienbare Rückkehr. Bei Standbild abbrechen und Uhrzeit notieren; Android-HOME als Nutzereingriff separat vermerken. | ANDROID_NOT_TESTED |
| PLAY93-02 | Nur nach PASS: 30/60/120 Live-/VOD-/Serienwechsel; späte/verlorene ACK, fremde Wiedergabe und .42-Kompatibilität schützen. Kein Auto-Neustart nach bewusstem Stop. | ANDROID_NOT_TESTED |
| PLAY93-03 | Live und VOD 30–90 min; MediaCodec/Audiotrack, Gruppen-/HD/4K-Wechsel, Streamverlust. Echten Prozessabbruch mit Android Exit-Reason/logcat getrennt erfassen; keine LMKD-/SIGSEGV-Vermutung als Tatsache. | ANDROID_NOT_TESTED |
| EPG93-01 | Vor Upgrade Inventur pro Volume und Dateiklasse. Nach Upgrade Backup-Retention: gültige letzte Recovery vorhanden, entfernte/übersprungene Sets und freie interne Bytes vorher/nachher erfassen. Gleicher Mount zwingend. | ANDROID_NOT_TESTED |
| EPG93-02 | Drei Quellen inkl. Provider/EPGShare/Kaimandura, gültiger Commit und kalter Readback, Bildermetadaten erhalten. Raw nicht persistiert → 0 Bytes Raw-Delete korrekt. Lokale Benutzer-XMLTV-Datei bleibt erhalten. | ANDROID_NOT_TESTED |
| EPG93-03 | Offline/kaputter Feed/verkürzter Feed/SQLite Busy: LastGood bleibt; 7d Vergangenheit/20d Zukunft soweit vorhanden. Reboot und Quelle deaktiviert, Recovery wirklich nutzbar. Keine Behauptung physischer Freigabe aus DELETE-Zeilen. | ANDROID_NOT_TESTED |
| EPG93-04 | Backup-Keeper korrupt, unbekannte Datei, offene Sicherung, Stromausfall/Abbruch: keine Löschung unbewiesener Daten; Journal/Fortsetzung; mindestens ein validierter Recovery-Satz. | ANDROID_NOT_TESTED |
| ST93-01 | Einstellungen → Speicher → Übersicht: eigener Titel XCMate-Speicheranalyse, lesbare Werte, kein Plot/JSON. Pro Klasse vollständig/teilweise/nicht lesbar; 0 unvollständig darf nicht leer bedeuten. Scrollen/Back/Expertenaktion. | ANDROID_NOT_TESTED |
| ST93-02 | Längere Inventur erneut öffnen, Fortschritt/Cancel, Kategorien überlappen nicht addieren. Android tatsächlich erkannt, QA bleibt NOT_TESTED; Quota unbekannt klar sichtbar. | ANDROID_NOT_TESTED |
| USB93-01 | Bestehender USB-Pilot: anderes verifiziertes Volume, Probe, Kopie/SHA, sichtbare Bilder, echter Neustart, Offline/Abziehen und Rückkehr. Originale nur gesondert bestätigt; tatsächlichen internen Platzgewinn messen. | ANDROID_NOT_TESTED |
| ART93-01 | ProSieben/Galileo: Mini-EPG-Bild → Details mit gleichem Event/Quelle/Revision. Kleines gültiges XMLTV-Bild bleibt im Detail, ohne Hero-Mindestgrößen zu lockern. | ANDROID_NOT_TESTED |
| ART93-02 | Galileo/Ghosts TMDB und TVMaze: manuell wählen, persistenter Readback, Bildstatus separat, Schließen/Reopen/Reboot; fehlerhafte Bildabfrage behält korrekten Event-Fallback. Token unverändert. | ANDROID_NOT_TESTED |
| ART93-03 | Ereignis-/Quellen-/Portal-/Revisions-/Mappingwechsel: niemals altes/fremdes Bild als neues freigeben. Bestehende Home-TMDB-Backdrops und Logos mindestens fünf Minuten sichtbar. | ANDROID_NOT_TESTED |
| LIVE93-01 | Gespeicherter Startsender während Index-Busy/Teilkatalog: keine Neueinrichtungsfrage und keine geänderten IDs. Nach Datenbereitschaft erneut starten. | ANDROID_NOT_TESTED |
| LIVE93-02 | Mini-EPG vor Komplettkatalog öffnen; 4K/andere aktivierte Gruppen wählen. Lokale Sender kommen automatisch, auch ohne EPG; >100/137 Sender blättern, Gruppe/Back/OK. Keine falsche Leeranzeige bei Pending. | ANDROID_NOT_TESTED |
| REG93-01 | Schnelle Home-Logos/Hero, sechs Reihen, persönliche fremde Widgets, Überschriften/Spinner, Fokus/IR, Film/Serie/Resume/Autoplay, EPG-Mapping/Favoriten erhalten. | ANDROID_NOT_TESTED |

Bei FAIL erste Abweichung, feste Diagnosecodes und Zeitpunkt notieren; keine Reset-/Löschversuche. Unvollständige Inventur, gespeichertes Mapping oder erreichbare Bild-URL allein sind kein Geräte-PASS.
