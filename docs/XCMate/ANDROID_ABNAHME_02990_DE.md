# Android-Abnahme .90 – Box B, Kodi 21.3 / RK3528 ARM32

Stand: Entwicklung im Draft-PR [#431](https://github.com/artattakk-creator/kodi-noodleprivate/pull/431). **Alle folgenden Gerätefälle sind ANDROID_NOT_TESTED.** Die tatsächlichen .89-FAILs im historischen Protokoll bleiben erhalten. Native Linux-Kodi-Pixeltests und Hosttests sind keine Android-Abnahme.

## Installation und Schutz

Nur auf der vorgesehenen Testbox kumulativ über .89 aktualisieren: Kodi → Add-ons → Aus ZIP-Datei installieren → `plugin.video.xtreammate-0.1.29.90.zip`. Vorher die SHA256 mit der beiliegenden Datei vergleichen. Keine Deinstallation, kein Reset, keine Cache-Löschung. Die regulären/Pilot-/NeoDark3-Kataloge bleiben bei .89; .90 ist ausschließlich das Paket im Draft-PR. Box A nicht verändern. Installer 0.5.26 bleibt unverändert.

Vorher privat sichern bzw. erfassen: Kodi-Profil, Provider-/Senderzahlen, aktive Startgruppe und Startsender, Favoriten, EPG-Zuordnungen, manuelle Bildzuordnungen, TMDB-Konfiguration und alle eigenen/fremden Widgetnamen, Pfade, Reihenfolgen. Zugangsdaten und Rohlogs nicht veröffentlichen.

Die zwei nativen Fremdwidget-Fokuskorrekturen ändern **keine** persönliche Definition. Ein vorhandener BINGIE-Adapter wird nur über den vorhandenen, ausdrücklich bestätigten Vorschau-/Backup-/Prüfsummenablauf aktualisiert. Ohne diese Bestätigung bleibt die installierte Skin-Datei unangetastet. Keine eigenständige SkinShortcuts-Neugenerierung zum „Reparieren“ leerer Reihen auslösen.

## Reihenfolge und tatsächlich zu prüfende Ergebnisse

| ID | Ablauf und PASS-Kriterium | Android |
|---|---|---|
| T90-01 | Kodi neu starten, ohne Senderstart Home öffnen. Vorher bestätigte lokale Logos müssen spätestens 10 s nach bedienbarer Home-Ansicht sichtbar sein (Ziel). Teilbestand und fehlende Quellen getrennt zählen; fehlende Logos im Hintergrund. Richtige Senderidentität, kein globaler Manifest-/HTTP-Neustart. | ANDROID_NOT_TESTED |
| T90-02 | Nach einmaligem verifiziertem Erstaufbau 3 vollständige Kodi-Neustarts. Sichtbare Logos in Rail, Hero-Fallback und Details korrekt; 0 neue HTTP-Logo-Downloads/0 doppelte Commits für unveränderte gültige Dateien. Fehlende Providerquelle ausdrücklich ausweisen, kein erfundenes 88/88. | ANDROID_NOT_TESTED |
| T90-03 | Bei natürlich vorhandenem niedrigem Speicherstand Diagnose ablesen: Ziel, Volume, Gesamt/Frei, effektiver Floor und Quota. Vorhandene Logos bleiben sichtbar; neue Dateien nur oberhalb des Schutzfloors. **Keinen Speicher künstlich füllen**, keine Reserven abschalten. 115-MiB-Hostinjektion ist kein physischer Gerätebeweis. | ANDROID_NOT_TESTED |
| T90-04 | Verifiziert vorhandenes lokales EPG vor Neustart sicherstellen. Ohne Playerstart innerhalb 30 s (Ziel) Jetzt/Danach für die ersten fünf Sender prüfen: Titel, Beginn, Ende, Fortschritt. Kurzfristiger DB-Busy darf denselben gültigen Eintrag nicht leeren. Echte Programm-/Quellgrenze muss korrekt wechseln. | ANDROID_NOT_TESTED |
| T90-05 | 15 Minuten Home, mindestens 20 Fokus-/Senderwechsel. 0 `GUI86 CALLBACK_FAILED`, keine Eingabesperre, keine unbeabsichtigten Portalwechsel. Erreichbare Einstellungen und korrekte Back-Ebenen prüfen. | ANDROID_NOT_TESTED |
| T90-06 | Gleiche Sendung mindestens fünf Minuten stehen lassen, dann Live/Film/Serie wechseln. Hero und Cover bleiben ohne schwarze Zwischenzustände/Fremdbilder. Freigegebenes .88-Layout, Fokusrahmen, Quellenkennzeichnung und Bildproportionen erhalten. | ANDROID_NOT_TESTED |
| T90-07 | Redigierte Diagnose enthält Manifest-Ladezeit, lokale Treffer, Remote-Anfragen, Persistenzzeiten, LastGood-Alter und präzise Callback-Gründe. Pixelzeit per tatsächlicher Sichtprüfung erfassen; `READY` und Dateihash allein sind kein Bild-PASS. | ANDROID_NOT_TESTED |
| T90-08 | Live-TV, Film und Serie starten/beenden, Zurück-Navigation, Resume und staffelübergreifendes Autoplay prüfen. Merktimer weiterhin nur „Jetzt umschalten“ / „Verwerfen“, standardmäßig 5 Minuten vorher, kein automatisches Umschalten. | ANDROID_NOT_TESTED |
| T90-09 | Je mindestens fünf verschiedene reale Film- und Serienposter auf Home anzeigen. Nach drei Neustarts weiterhin dieselben gültigen lokalen Bilder/Titel. Während regulärem Hintergrundimport/EPG-Refresh keine Falschleere, keine Play-Symbole statt gültiger Cover, keine vollständige Neuladung unveränderter Reihen. | ANDROID_NOT_TESTED |
| T90-10 | Mindestens zwei unabhängige bestehende Fremdwidgets (z. B. MP3/SHOUTcast und Kino) mit IR-Fernbedienung erreichen, scrollen, öffnen und zurückkehren. Alle eigenen und fremden Namen, Pfade, Positionen und Reihenfolgen bleiben gleich. Fehlende Bindung/Sichtbarkeit und tatsächlich leere Anbieterantwort unterscheiden. | ANDROID_NOT_TESTED |
| T90-11 | Mini- und Groß-EPG → Details → manuelle Suche: TMDB-TV, TMDB-Movie und TVMaze getrennt prüfen. Mehrere Treffer, zweiten/anderen Treffer ausdrücklich wählen und speichern. Nach Schließen/Öffnen und Kodi-Neustart gleiche bestätigte Zuordnung. Abbruch, echte Programmänderung, Schreibsperre und Netzwerk-Timeout getrennt; keine fremde SID/Quelle zuordnen, keine Tokenänderung. | ANDROID_NOT_TESTED |
| T90-12 | Laufendes Live-TV: Links → Senderliste/Mini-EPG → Links → Gruppen → OK → richtige komplette Liste → OK → richtiger Sender. 20 Gruppen- und 20 Senderwechsel, mindestens eine Gruppe mit >128 Einträgen und einen Sender am Listenende. Reguläre EPG-/Importlast parallel. Ebenennavigation stoppt den Player nicht, Fokus/Gruppe bleiben nachvollziehbar. | ANDROID_NOT_TESTED |
| T90-13 | Private Vorher-/Nachher-Inventur bzw. Hashvergleich: Provider, Token, EPG, Gruppenfilter, Favoriten, Nutzerwidgets, SkinShortcuts und bestehende Bilder erhalten. Erwartete eigene neue Cache-/Mappingdateien getrennt von unzulässigen Veränderungen dokumentieren. Keine Rohdaten auf GitHub. | ANDROID_NOT_TESTED |
| T90-14 | BINGIE MOD → Shortcuts → Widget auswählen → Add-On → Video-Add-ons → XCMate: Live-TV-Startgruppe, neueste Filme und neueste Serien direkt als Quellen wählen, tatsächlich speichern, wieder öffnen und Kodi neu starten. WidgetPath und echte Home-Controls prüfen. Upgrade: mindestens zwei fremde Definitionen bleiben unverändert. Frische Installation mit/ohne Portal **nur in einem gesonderten Testprofil**, niemals durch Zurücksetzen bestehender Boxen; ohne Portal sichere Einrichtung ohne Fake-PID. | ANDROID_NOT_TESTED |

Pro Fall notieren: PASS / FAIL / ANDROID_NOT_TESTED, installierte Version, Gerät, Kodi-Version, Zeitpunkt (Europe/Berlin), Dauer ab Home-ready, sichtbare Sender-/Posterzahl, Diagnosecode und redigierte Beobachtung. Für das 10-/30-Sekunden-Ziel eine sichtbare Stoppuhr verwenden. Fehler nicht durch wiederholte Neuinstallation oder Löschen bestehender Daten überdecken.

## Abbruchkriterien

Bei Player-Hänger, verschwundenen Profil-/Widgetdaten, falscher dauerhafter Zuordnung oder wiederholten Callback-Ausnahmen stoppen und Befund sichern. Nicht auf Box A ausweichen und keine alte Version überinstallieren. Fehlgeschlagene Einzelprüfungen bleiben FAIL; übrige nicht ausgeführte Fälle bleiben ANDROID_NOT_TESTED. Merge und Veröffentlichung benötigen eine neue ausdrückliche Freigabe.
