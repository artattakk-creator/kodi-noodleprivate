# XCMate 0.1.29.68 – Android-Abnahme Box B

Alle unten stehenden .68-Geräteprüfungen: **NOT_TESTED**. Die realen .67-FAIL aus #313 bleiben historisch erhalten. Linux-/Host-/Pixeltests bestätigen kein Android-PASS. Box A nicht verändern.

Installation als kumulatives Update des bestehenden Add-ons, ohne Deinstallation, Daten-/Cachelöschung, Neuimport oder Reset. Test-ZIP und SHA256 müssen aus demselben abgeschlossenen CI-Lauf stammen. Das Update-Popup zeigt Version und Changelog; vorhandene Einstellungen bleiben bestehen.

Vorher Gerät, Kodi-Version, Add-on-Version, aktive Startgruppe und unverändert vorhandene Portale/Favoriten notieren. Keine Zugangsdaten/URLs oder privaten Rohlogs öffentlich hochladen. Änderungen der Test-Startgruppe nach dem Test ausdrücklich auf den bisherigen Wert zurückstellen.

| ID | Ausführung | Erwartung | Status |
| --- | --- | --- | --- |
| 68-ART-01 | Großen EPG öffnen, acht Zeilen mit aktuell laufenden Sendungen ansehen; dann Sender außerhalb der Home-Startgruppe wählen | Begrenzte priorisierte Aufträge, Bild erscheint ohne Guide-Neustart; keine alte Sendung sichtbar | NOT_TESTED |
| 68-ART-02 | Im Guide verschiedene Sendungen fokussieren und Details öffnen | Details zeigen QUEUED/RUNNING oder zutreffenden Fehler; bei Erfolg dasselbe lokale Bild mit korrekter Quelle | NOT_TESTED |
| 68-ART-03 | Eine eindeutig belegte Serie/Film mit Jahr oder Staffel/Folge auswählen | Passende TMDB-Sendung, keine ungeprüfte Bildverwechslung; generisches Serienbild entsprechend bezeichnet | NOT_TESTED |
| 68-ART-04 | Bei realem TMDB-Bild Guide-/Mini-/Hero-/Detailanzeige prüfen | Unverändertes offizielles TMDB-Logo rechts unten, Credits erreichbar | NOT_TESTED |
| 68-ART-05 | Nachricht/Sport/mehrdeutigen oder bildlosen Titel auswählen | Kein geratenes Poster, zutreffender negativer Zustand, bedienbarer Text | NOT_TESTED |
| 68-ART-06 | Dieselbe Sendung erneut fokussieren, später Kodi neu starten | Vorhandene Bilddatei erneut nutzbar; keine Abfragestürme | NOT_TESTED |
| 68-TMDB-01 | Zentrales EPG-/Sendungsbildmenü öffnen | Token-/Lookupstatus getrennt; bestehenden funktionierenden Token nicht erneut importieren | NOT_TESTED |
| 68-TMDB-02 | Bestehende Zustimmung und Quellen prüfen | Keine automatische Freigabeänderung; vorhandene Werte/Token erhalten | NOT_TESTED |
| 68-SPACE-01 | Reine Speicherdiagnose anzeigen, Werte redigiert notieren | DB-/WAL-/Seiten-/Freelist-/Freiraum-/Reservewerte; echter Platzmangel, interne Grenze und Reserve getrennt | NOT_TESTED |
| 68-SPACE-02 | Bei Bildblockade konkreten Detailcode prüfen | Kein erfundener Erfolg; keine Budgets blind erhöhen, keine Dateien löschen | NOT_TESTED |
| 68-MINI-01 | Kodi normal starten, ersten Live-Sender öffnen, erstmalig Links; Zeit stoppen | Sender-/Ladeanzeige unmittelbar bedienbar; EPG ergänzt sich; Kaltzeit separat notiert | NOT_TESTED |
| 68-MINI-02 | Mini schließen, nochmals Links; 10 Wiederholungen | Warme Senderliste/Jetzt/Danach möglichst <1 s; echte Zeiten notieren | NOT_TESTED |
| 68-MINI-03 | Sender ohne Programmdaten fokussieren | Sendername/Logo bleiben sichtbar; „lädt“ und tatsächlich fehlendes EPG unterscheiden | NOT_TESTED |
| 68-MINI-04 | Mehrfach schnell Links/Zurück/Senderfokus wechseln | Kein Blank-Frame, kein Hänger, kein fremdes Ereignis/Mehrfachrahmen | NOT_TESTED |
| 68-HOME-01 | Bisherige Startgruppe unverändert öffnen und bis zum letzten Sender scrollen | Vollständige dynamische Liste, EPG/Logo/Hero für jeweils exakt gewählten Sender | NOT_TESTED |
| 68-HOME-02 | Kontrolliert andere bestehende Startgruppe wählen, danach zurückstellen | Alte Snapshotdaten werden nicht übernommen; richtige Anzahl und Reihenfolge | NOT_TESTED |
| 68-HOME-03 | Alle aktivierten Gruppen (*) wählen, danach zurückstellen | Nur freigegebene Gruppen, keine doppelten Sender, kein fremdes Portal | NOT_TESTED |
| 68-HOME-04 | Vorhandenes zweites Portal/Profil nur falls bereits verfügbar auswählen | Keine Daten der vorherigen Auswahl; sonst NOT_TESTED, keine neue Konfiguration erzwingen | NOT_TESTED |
| 68-HOME-05 | Änderungen der aktiven Gruppen/Indexgeneration prüfen, falls ohne Datenverlust möglich | Neue Policy aktualisiert Widget; bisher gespeicherte Widgetquelle unverändert | NOT_TESTED |
| 68-COMPAT-01 | Bisherige BINGIE-Live-Texte und Senderlogos prüfen | Bestehende .67-PASS bleiben funktional | NOT_TESTED |
| 68-COMPAT-02 | Filme/Serien und Widgets, Suche, Cover und Serien-Resume/Autoplay stichprobenartig bedienen | Keine Regression | NOT_TESTED |
| 68-LIVE-01 | Startsender → einmal Zurück mit bestehendem .42-Modus | Bedienbare Rückkehr; bei FAIL stoppen und redigierten Befund erfassen | NOT_TESTED |
| 68-LIVE-02 | Erst nach LIVE-01 PASS fünf, anschließend 20 Live-Zyklen | Kein Hänger/Player-Race; separates Live-Gate bleibt offen bis Bestätigung | NOT_TESTED |
| 68-REG-01 | Favoriten, Gruppen, manuelle EPG-Zuordnungen und Einstellungen vergleichen | Unverändert vorhanden | NOT_TESTED |
| 68-EXT-01 | Externe Komponenten-Diagnose öffnen | Versionsnummern sichtbar, keine automatische Skin-/Helpermodifikation | NOT_TESTED |

Die Größen 0/1/5/17/88/120/256 und Seitengrenzen 16/64/128 werden automatisiert mit synthetischen SQLite-Beständen geprüft. Auf Box B nur tatsächlich vorhandene Gruppen testen; keine Portale/Benutzerdaten für künstliche Größen umbauen.

Abnahmebericht je ID mit PASS/FAIL/NOT_TESTED, gemessenen Kalt-/Warmzeiten und zutreffenden festen Diagnosecodes. LOCAL_IMAGE_READY ist kein Ersatz für das tatsächlich sichtbare Bild. Wenn eine lokale Datei bereit ist und Android keine Texture zeigt, als KODI_TEXTURE_NOT_SHOWN erfassen, nicht als Netzwerkfehler.

Kein automatischer Merge oder Release. Nach Nutzerprüfung bleiben erforderliche Korrekturen im Draft; Veröffentlichung erst nach ausdrücklicher Freigabe.
