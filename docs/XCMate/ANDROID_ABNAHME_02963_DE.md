# Android-Abnahme XCMate 0.1.29.63 – Box B

**Alle Prüfungen sind zunächst ANDROID_NOT_TESTED.** Gerät: Kodi 21.3, Android/RK3528 ARM32, Titan BINGIE MOD 2.2.3, Skinshortcuts 2.1.0. Box A nicht verändern. Kein Merge, kein Release, keine automatische Geräteinstallation.

## Vorbereitung

Das endgültige CI-Testpaket enthält plugin.video.xtreammate-0.1.29.63.zip und die zugehörige .sha256-Datei. Einen Actions-Artefaktcontainer zuerst entpacken; in Kodi anschließend ausschließlich das darin enthaltene Add-on-ZIP installieren. Die Versionsnummer unter XCMate prüfen. Bestehende .62 ohne Deinstallation, Downgrade, Profil-/EPG-/Cover-/Skinshortcuts-Reset aktualisieren.

Portale, Startgruppe, Favoriten, Film-/Serienwidgets und der bisher funktionierende .42-Kompatibilitätsmodus müssen erhalten bleiben. Keine neue Widgetquelle eintragen und bestehende Film-/Serienreihen nicht erneut verknüpfen.

Bei einem vorher ausdrücklich bestätigten und exakt bekannten Adapter erscheint einmal die .63-Upgradevorschau. Diff prüfen und nur bei gewünschtem Upgrade bestätigen; verifizierte Sicherung und nativer Skinshortcuts-Rebuild bleiben erhalten. Ein fehlender/abgelehnter Hinweis lässt die Skin-Dateien unverändert. Manuell: XCMate → Einstellungen → Aussehen und Darstellung → BINGIE-Startseiten-Widgets einrichten → BINGIE-Home-Layout prüfen/vorbereiten. Unbekannte Skin-Dateien nicht erzwingen.

Wiederherstellung über denselben Widgetmanager. Der jüngste .63-Plan stellt zunächst das zuvor installierte Layout wieder her; ein älterer bestätigter Plan kann danach separat zurückgenommen werden. Keine pauschale Skin-/Widget-Neuinitialisierung.

## Kurze erste Prüfreihenfolge

1. Home: WELT/NITRO oder einen anderen realen Sender mit importiertem EPG fokussieren. Großes Bild/Neutralmotiv und EPG-Texte liegen übereinander; kleine Senderbuttons darunter und Film-/Serienreihen bleiben sichtbar.
2. OK auf WELT: schneller bewährter Streamstart; warme lokale Jetzt/Danach-Texte in der ersten nutzbaren Live-Infoansicht, Ziel höchstens 1 Sekunde nach sichtbarer Oberfläche.
3. Einmal Zurück aus reinem Live-Vollbild: eigener Stream endet, bedienbare Home-/Vorgängeransicht. Offene Overlays schließen nur ihre Ebene.
4. Erst wenn diese drei Punkte bestehen, die restlichen Prüfungen ausführen. Bei Freeze abbrechen und Zeitpunkt/Version/Gerät notieren; keine weiteren Wiederholungszyklen erzwingen.

## Abnahmematrix

Je Zeile später PASS / FAIL / NOT_TESTED mit kurzer Beobachtung eintragen.

| ID | Ausführung und erwartetes Ergebnis | Status |
|---|---|---|
| B63-01 | .62→.63 als normales Add-on-Update; Version/Änderungshinweis korrekt; Einstellungen und Zugangsdaten erhalten | ANDROID_NOT_TESTED |
| B63-02 | Geprüftes Hero-Upgrade mit genau einer ausdrücklichen Zustimmung, Backup und Rebuild; unbekannte Dateien bleiben geschützt | ANDROID_NOT_TESTED |
| B63-03 | Vollflächiges 16:9-Ausgangsbild im Hero zugeschnitten, keine separate rechte Infotabelle; Logo/Name, großer Titel, Untertitel soweit real vorhanden, Jetzt/Danach, Zeiten, Fortschritt und Kurzbeschreibung als Overlay | ANDROID_NOT_TESTED |
| B63-04 | Bei vorhandenen lokalen Programmdaten stimmt Hero-Now/Next mit großem EPG, Mini-EPG und Live-Infobar überein; manuelle Quellenbindung hat Vorrang | ANDROID_NOT_TESTED |
| B63-05 | WELT OK bleibt schnell; Zeit ab sichtbarer Live-Oberfläche bis korrektem warmen Now/Next messen, Ziel ≤1 s; Programmtitel und Zeiten vergleichen | ANDROID_NOT_TESTED |
| B63-06 | Einmal Live-Zurück mit bestehendem .42-Modus; bei PASS fünf Wechsel/Wiederholungen, keine Doppelstarts oder Hänger | ANDROID_NOT_TESTED |
| B63-07 | Ganze Startgruppe bis mindestens Sender 88/letztem verfügbaren Sender; kleine 142×72-Layouts, genau ein Fokus; Fokus allein startet keinen Player | ANDROID_NOT_TESTED |
| B63-08 | Sender ohne Logo/EPG/Bild: Textfallback und bildfüllendes lokales Neutralmotiv, ehrlicher Hinweis statt falscher vorheriger Sendung oder Spinner | ANDROID_NOT_TESTED |
| B63-09 | Wechsel auf anderen Sender und echten Sendungswechsel beobachten: kein gemischter/alter Text, realer Fortschritt, Bild nur zum passenden Ereignis | ANDROID_NOT_TESTED |
| B63-10 | Drei Filmcover und zwei Seriencover, Scrollen, korrekte Klickziele, Resume/Autoplay und vorhandene automatische Aktualisierung unverändert | ANDROID_NOT_TESTED |
| B63-11 | Token-Datei von USB/Downloads über Kodi-Dateidialog importieren; private lokale Kopie, Quelle unverändert, keine automatische Bildaktivierung bei bloßem Import | ANDROID_NOT_TESTED |
| B63-12 | Dieselbe Prüfung mit vorhandener Kodi-SMB-Verbindung; danach SMB/USB entfernen und Tokenstatus erneut prüfen | ANDROID_NOT_TESTED |
| B63-13 | Separate Aktion „Token importieren und TMDB-Sendungsbilder aktivieren“ ausdrücklich bestätigen; beide vorhandenen Opt-ins nur im aktuellen Profil aktiviert | ANDROID_NOT_TESTED |
| B63-14 | Maskierte Direkteingabe als Alternative; ungültige vorhandene Privatdatei wird nur nach bestätigter Ersetzung geändert; sichtbares Zurück und Fernbedienungs-Zurück ändern nichts | ANDROID_NOT_TESTED |
| B63-15 | Eigener echter HTTPS-Verbindungstest meldet nur bei tatsächlichem Erfolg TMDB_OK; bei Fehlern den sicheren Code notieren, keinen Token/Screenshot davon weitergeben | ANDROID_NOT_TESTED |
| B63-16 | Eindeutig identifizierter Film/eine Seriepisode: gemeinsames korrektes Sendungsbild nach Hintergrundvorbereitung in Hero und großem EPG; bei Nachrichten/Mehrdeutigkeit kein falsches Cover; TMDB-Attribution nur bei angezeigtem TMDB-Bild | ANDROID_NOT_TESTED |
| B63-17 | Kodi-Neustart: Token privat weiterhin vorhanden, Hero/Now/Next aus gespeichertem EPG, sämtliche Widgetreihen/Einstellungen unverändert | ANDROID_NOT_TESTED |
| B63-18 | Falls mehrere Profile verwendet werden: kein Token, EPG-Snapshot oder Hero-Bild des anderen Profils; keine erzwungene Umstellung bestehender Daten | ANDROID_NOT_TESTED |
| B63-19 | .63-Layout gezielt wiederherstellen und erneut ausdrücklich vorbereiten; gespeicherte Widgetquellen/Film-/Serienzeilen unverändert | ANDROID_NOT_TESTED |

## Token-Dateiformat und Bedienung

Menü: XCMate → Einstellungen → EPG → TMDB-Zugang.

Standardname tmdb_read_access_token.txt; andere ausgewählte Dateinamen sind ebenfalls zulässig. Inhalt: eigener vollständiger TMDB API Read Access Token als eine physische UTF-8-Zeile mit drei Base64URL-Blöcken und zwei Punkten. Optional genau ein abschließender LF oder CRLF. Kein Bearer, keine Anführungszeichen, kein JSON, kein BOM, keine Leerzeichen/Kommentare oder zweite physische Zeile. Ein ausschließlich visueller Editor-Umbruch ist in Ordnung.

„Token-Datei importieren“ speichert nur privat. „Token importieren und TMDB-Sendungsbilder aktivieren“ ist eine getrennte, zusätzliche Zustimmung. „Token geschützt eingeben/ändern“ nutzt das bestehende maskierte Setting, wenn keine Privatdatei vorhanden ist; eine vorhandene Datei hat weiterhin Vorrang und wird geführt ersetzt.

Die Quelle wird nicht verändert/gelöscht und später nicht mehr benötigt. Das Ziel liegt ausschließlich im privaten aktuellen Kodi-Profil. Nie Token, Fragmente, Tokenhashes oder private SMB-Pfade in Chat/GitHub/Screenshots/Rohlogs weitergeben.

Sichere Fehlercodes: TOKEN_PATH = unzulässige Quelle; TOKEN_UNREADABLE = nicht lesbar/Berechtigung/VFS-Zeitbudget; TOKEN_FORMAT = tatsächliches Inhaltsformat; TOKEN_SIZE = Bytebudget; TOKEN_WRITE = privates Ziel nicht sicher schreibbar; TOKEN_CHANGED = Ziel/Profil seit Bestätigung verändert. Ein VFS-Timeout erlaubt keinen nachträglichen Import: ein eventuell noch laufender nativer Leseaufruf darf nur auslaufen, ohne Dateiübernahme.

## EPG-Diagnose ohne zusätzliche Datei

XCMate verwendet weiter die vorhandene guide_v1.sqlite und die bestehenden Quellen-/SID-/Alias-/manuellen Zuordnungen. Keine zusätzliche EPG-Datei anlegen oder kopieren, keine Datenbank löschen. Sind tatsächlich keine aktuellen Daten vorhanden, muss die Oberfläche sofort den Sender und „Keine Programminformationen“ anzeigen.

Relevante sichere Ereignisse: HOME_FOCUS, HOME_NOW_NEXT_READY, OK_CLICK, FIRST_VIDEO, INFO_VISIBLE, PLAYER_NOW_NEXT_READY, DB_READ, SNAPSHOT_SEEDED. FIRST_VIDEO bezeichnet die beobachtbare native Kodi-Player-Zeit-/Videozustandsprobe und keinen Nachweis des ersten dekodierten Bildes. Die echte sichtbare 1-Sekunden-Grenze auf Box B separat messen.

Missing- und Fehlerzustände unterscheiden: EPG_DATA_MISSING, EPG_MAPPING_MISSING, EPG_CACHE_UNAVAILABLE, EPG_CACHE_STALE, EPG_SNAPSHOT_SCHEDULE_DELAY, EPG_DB_BUDGET, EPG_UI_UPDATE_DELAY. Keine privaten Rohlogs öffentlich hochladen. Host-Pixel und synthetische/Mock-Authentifizierung sind ausdrücklich kein Android-PASS.
