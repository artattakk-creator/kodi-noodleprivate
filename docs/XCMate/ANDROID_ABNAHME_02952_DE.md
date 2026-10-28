# XCMate .52 – Android-Abnahme Box A und Box B

**Alle 48 Gerätegates zunächst NOT_TESTED. Kein Host-PASS ist eine Android-Abnahme.**

Box A: Kodi 21.2, vorhandenes geschütztes Profil. Box B: Kodi 21.3, bestehendes Profil und Artworkmodus erhalten. Gerät/SoC/Androidversion tatsächlich notieren; nicht aus alten Logs erraten. An keiner Box wurde durch Codex etwas installiert oder geändert. Box A nur nach bewusster Freigabe/Handlung des Nutzers prüfen; bis dahin bleiben ihre Gates offen.

## Vorbereitung und Reihenfolge

1. Das ZIP im Draft-PR verwenden, SHA256 mit beiliegender Datei vergleichen und über Kodi **als Update** installieren, falls ausdrücklich zur Geräteprüfung vorgesehen. Keine Deinstallation, kein Downgrade, kein Löschen von Datenbanken, Portalen, Covers, Texturecache oder Profilen. Kein Skinadapter und keine Keymapänderung für diese Abnahme.
2. Version .52 und bestehende Einstellungen notieren. Bei vorhandener Guide-Backup-Blockade die bereits vorhandene manuelle EPG-Sicherung nutzen; nur bei BACKUP_VERIFIED einen schreibenden Refresh wiederholen. Kein manuelles SQL und kein Entfernen der Sperre. Ohne ausreichenden Platz als BLOCKED dokumentieren, kein Datenreset.
3. Erst REG52-01 kurz prüfen, dann EPG → Serien → Pixel → übrige Regression. Bei Hänger anhalten und Zeitpunkt/letzte Aktion notieren; keine Erfolgsmeldung aus Hosttests übernehmen.
4. Für EPG-Grenz-, Fehler- und kürzere-Feed-Tests eine kontrollierte nicht private Testquelle/Testumgebung verwenden. Ist das auf bestehendem Gerät nicht sicher möglich, NOT_TESTED mit Grund; keine vorhandene Quelle oder Zuordnung überschreiben. Sommer-/Winterzeit nicht am Gerät manipulieren (Hosttest vorhanden).
5. Eingangsbestand, tatsächlich letzte Feed-Sendung und Abdeckung notieren. Eine kurze Quelle kann 20 Tage nicht beweisen. Auflösung nur anhand verfügbarer echter Streams prüfen; Bezeichnungen HD/UHD reichen nicht.

Serien: vorhandene Gruppenauswahl → neue Seriengruppe → Speichern. Status/Retry/Abbruch: zusätzlicher Punkt **Serien-Nachimport** in diesem Menü. Widget-Refresh kann durch die bestehende native Reload-Drosselung bis zu 60 Sekunden dauern; fehlt ein Reload-Hook, Blockierstatus melden, keinen Skinpatch ausführen.

## Prüfliste

| ID | Aktion | PASS-Kriterium | Box A | Box B |
|---|---|---|---|---|
| EP52-01 | Vorhandenen Datenbestand und manuelle Mappings dokumentieren; Guide-Diagnose nur lesen. | Keine Änderung bestehender Zuordnungen oder Konfiguration. | NOT_TESTED | NOT_TESTED |
| EP52-02 | Manuellen EPG-Refresh mit allen aktivierten Quellen ausführen. Falls BACKUP_REQUIRED: vorhandene verifizierte EPG-Sicherungsfunktion bewusst verwenden und Erfolg abwarten. | Jede Quelle separat READY/Fehler/READY_NO_NOW; Blockade nie als PASS werten. | NOT_TESTED | NOT_TESTED |
| EP52-03 | Großes EPG bis zum Beginn des lokalen Tages −7 zurücknavigieren. | Zuvor empfangene Programme bleiben verfügbar; nicht gelieferte Historie als solche dokumentieren. | NOT_TESTED | NOT_TESTED |
| EP52-04 | Bis Tag +20 navigieren und Quellen-/Tagesdiagnose prüfen. | Tatsächlich gelieferte Daten sichtbar; +21 wird nicht neu importiert. Bei kurzer Quelle NOT_TESTED statt erfundener Vollständigkeit. | NOT_TESTED | NOT_TESTED |
| EP52-05 | Auf Testdatenquelle nach langem Feed einen kürzeren gültigen Feed aktualisieren. | Gültige bestehende Vergangenheit/Zukunft bleibt; keine Quelle oder DB löschen. | NOT_TESTED | NOT_TESTED |
| EP52-06 | Zwei aktivierte Quellen mit Lücken und derselben Sendung mit mehr Details vergleichen. | Lücken ergänzt, keine Dubletten, Beschreibung/Genre/Episode/Bildherkunft passend. | NOT_TESTED | NOT_TESTED |
| EP52-07 | Manuelle quellqualifizierte Zuordnung bei gleicher Kanal-ID in zwei Quellen vergleichen; Vorschau abbrechen. | Gewählte Quelle hat Vorrang; Abbrechen stellt Mapping/Ansicht wieder her. | NOT_TESTED | NOT_TESTED |
| EP52-08 | Denselben laufenden Sender im großen EPG, Mini-EPG, erster Infobar und bestehendem Livewidget prüfen. | Gleiche Jetzt-/Danach-Sendung, Zeiten, Beschreibung/Bild passend; fehlendes Bild neutral. | NOT_TESTED | NOT_TESTED |
| EP52-09 | Kodi regulär beenden/neustarten, anschließend Netzwerk kurz trennen und lokal navigieren. | Gespeicherte gültige Programmdaten und Bilderreferenzen bleiben lesbar; keine Fokus-Netzwerkhänger. | NOT_TESTED | NOT_TESTED |
| EP52-10 | Automatischen Refresh regulär abwarten; einen Quellfehler nur kontrolliert in Testquelle simulieren. | Andere Quellen laufen weiter, LastGood bleibt; keine Zugangsdaten/URLs im Diagnoseauszug. | NOT_TESTED | NOT_TESTED |
| SER52-01 | Nach Einrichtung in vorhandener Serien-Gruppenauswahl eine bisher inaktive Gruppe aktivieren und speichern. | Ohne Wizard/Portal-Neuanlage sichtbarer Nachimport; gespeicherte/empfangene Anzahl wächst. | NOT_TESTED | NOT_TESTED |
| SER52-02 | Import einer großen Gruppe (>1.200 Serien falls verfügbar) vollständig abwarten. | Keine Seitengrenze; gespeicherte Anzahl mit tatsächlich gelieferten Serien vergleichen. | NOT_TESTED | NOT_TESTED |
| SER52-03 | Serienübersicht und vorhandenes BINGIE-Serienwidget öffnen, reguläre Reload-Frist bis 60 s abwarten. | Dieselben neuen Serien/Cover, vorhandene Widgetverknüpfung ohne Neubindung nutzbar. | NOT_TESTED | NOT_TESTED |
| SER52-04 | Im Menü Serien-Nachimport abbrechen, danach gezielt Wiederholen; bei Bedarf Test-Netzfehler. | Keine Teilveröffentlichung; FAILED/CANCELLED sichtbar und sicher wiederholbar. | NOT_TESTED | NOT_TESTED |
| SER52-05 | Kodi nach ausgewählter, noch nicht indexierter Gruppe regulär neu starten. | Fehlender Gruppen-Head wird wieder eingereiht; keine doppelten laufenden Importe. | NOT_TESTED | NOT_TESTED |
| SER52-06 | Filmkatalog, Livegruppen, alte Serien, Resume und Gesehen-Status vor/nach Import vergleichen. | Bestand bleibt unverändert; abgewählte Gruppe startet keinen Nachimport. | NOT_TESTED | NOT_TESTED |
| PIX52-01 | Echten 720p- und 1080p-Stream jeweils in erster Infobar prüfen. | Gerahmt 1280 × 720 bzw. 1920 × 1080, anhand tatsächlich dekodierter Quelle prüfen. | NOT_TESTED | NOT_TESTED |
| PIX52-02 | Echten 1440p-/UHD-Stream prüfen, soweit vorhanden. | 2560 × 1440 bzw. 3840 × 2160; fehlender Teststream bleibt NOT_TESTED. | NOT_TESTED | NOT_TESTED |
| PIX52-03 | Zwischen Sendern unterschiedlicher Auflösung wechseln; Infobar sofort und nach zwei Samples ansehen. | Kein stehenbleibender alter Wert, kurz neutral, danach stabiles aktuelles Paar. | NOT_TESTED | NOT_TESTED |
| PIX52-04 | Stream ohne zuverlässige Kodi-Pixelwerte und nach Stop prüfen. | Neutral/verborgener Rahmen; Audio, Jetzt/Danach, Fortschritt und Bedienung bleiben intakt. | NOT_TESTED | NOT_TESTED |
| REG52-01 | Startsender, Mini-EPG, Gruppen, großer Guide, OK/Back und .42-Kompatibilitätsmodus prüfen. | Keine Rückkehrhänger; gespeicherte Kompatibilitätseinstellung unverändert. | NOT_TESTED | NOT_TESTED |
| REG52-02 | Film/Serie/Suche mit Covern und Resume, Serien-Autoplay über Staffelgrenze prüfen. | Bestehende Abläufe und Fernbedienung funktionsfähig. | NOT_TESTED | NOT_TESTED |
| REG52-03 | Vorhandene Film-/Serien-/Livewidget-Verknüpfungen nach Kodi-Neustart verwenden. | Links, Cover und automatische Aktualisierung erhalten; keine Skinmodifikation. | NOT_TESTED | NOT_TESTED |
| REG52-04 | Wizard in bestehendem Profil nur öffnen/abbrechen; Settings/Portale/Favoriten/Artworkmodus vergleichen. | .51-Wizard/Bestandsprofil erhalten; keine Neuinstallation, Migration oder Löschung. | NOT_TESTED | NOT_TESTED |

## Ergebnisprotokoll

Pro Box: Datum/Uhrzeit, Kodi-Version, XCMate-Version, ZIP-SHA, reale Hardware, Gate, PASS/FAIL/NOT_TESTED/BLOCKED, erwartetes und beobachtetes Verhalten. Bei Serien auch Gruppe (anonymisiert), vorher/nachher gespeicherte Anzahl und Widgetanzahl; bei EPG Tage/Quelle/Zeitraum und Abdeckung; bei Pixeln tatsächliches Paar und Umschaltverhalten. Keine privaten Provider-/SMB-Adressen, Tokens oder Passwörter in GitHub. Nur redigierte Diagnoseauszüge, keine Kodi-Rohlogs.

Freigabe erst nach ausgewerteter Geräteprüfung und ausdrücklichem Nutzerentscheid. Kein automatischer Merge und kein produktiver Release. Issues bleiben offen.
