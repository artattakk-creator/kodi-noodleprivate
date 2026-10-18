# XCMate – Fernbedienung, EPG, Kodi-Stabilität (Stand 18.10.2026)

## Beobachtungen aus dem Android-TV-Test
- Nach Installation von 0.1.18: EPG-Quellen-Menü öffnet nicht, XCMate-Startseite lädt endlos.
- Zeitweise auch andere Kodi-Add-ons (XVolt, Camination) und BINGIE MOD betroffen.
- Nach vollständigem Neustart: BINGIE-MOD-Startseite wieder erreichbar und Filmwiedergabe möglich. XCMate zu diesem Zeitpunkt **noch nicht erneut getestet**.
- Es gibt noch kein ausgewertetes `kodi.log` vom betroffenen Gerät; ursächliche Zuordnung deshalb offen.

## Verbindliche Reihenfolge
1. **Kodi-Stabilität/Isolation**: XCMate darf niemals andere Kodi-Add-ons blockieren.
2. **Fernbedienung und UI-Overlay**: OK, Links/Rechts, Hoch/Runter, Zurück, Menü, Fokus sichtbar; auch bei aktivem Live-Stream.
3. **EPG**: Provider-EPG zuerst, DE/AT/CH ergänzen, NL optional, konservatives Xtream-Kanal-Matching, persistente manuelle Zuordnung.
4. Cache und Hintergrundabläufe ressourcenschonend, ohne GUI-Thread-Blockaden.
5. Regressions- und reale Android-TV-Tests; große Änderungen nicht ohne Gerätelog als bewiesen ausgeben.

## 0.1.19 / 0.1.20
- Kodi-Verzeichnis bei EPG-Dialog schließen, Fehlerdialog statt endlosem Spinner.
- Cache-Ordner direkt per Kodi-Dateibrowser auswählbar, Fallback auf internen Cache.
- Große EPG-/Xtream-Hintergrunddownloads standardmäßig ausgeschaltet; keine automatische DACH-Massenaktualisierung beim Eintragen.

## 0.1.21: Sicherheits- und EPG-Speicherfix
- Der globale `FullscreenVideo`-Tastatur-/Fernbedienungs-Hook von XCMate wird **nicht mehr automatisch installiert**.
- Beim Dienststart wird eine eventuell vorhandene **von XCMate verwaltete** ältere Keymap entfernt, sofern der Nutzer keinen ausdrücklichen Fallback aktiviert hat. Fremde Keymaps bleiben unangetastet.
- Native `WindowDialog.onAction`-Navigation und Android-Anlernfunktion bleiben erhalten.
- Für Geräte, auf denen Kodi-native Tasten nicht funktionieren, bleibt die Alternative `Konfigurieren → alternative Vollbild-Keymap` als **bewusste Opt-in-Lösung** verfügbar. Diese ist Kodi-weit wirksam; beim Test BINGIE MOD und andere Videowiedergabe mitprüfen.
- XMLTV wird mit `ElementTree.iterparse` inkrementell gelesen, statt zusätzlich zu allen Programmeinträgen den gesamten XML-Baum im RAM zu halten. Das reduziert die Spitze der XML-Verarbeitung, beseitigt aber nicht den Speicherbedarf der EPG-Programmlisten.
- Vorhandene Xtream-Portale, Favoriten, EPG-Quellen und manuelle Mappings werden nicht überschrieben.

## Offene Diagnosefragen
- Ist der Fehler in XCMate-Startansicht, Einstellungen, Overlay bei laufendem Sender oder im globalen Kodi-Profil reproduzierbar?
- Kodi-Log auf `ERROR`, `XCMate`, `MemoryError`, `Timeout`, `WindowDialog`, `RunScript`, `epg` prüfen (vor Austausch Zugangsdaten schwärzen).
- Nach Gerätetest separat prüfen, ob native Fernbedienungstasten das Overlay erreichen, ob sichtbarer Fokus und Navigation funktionieren, ob 5 EPG-Quellen geladen und Sky-/RTLup-Kanäle korrekt gematcht werden.

## EPG-Quellen (opt-in)
- DE Master: https://kaimandura.github.io/epg-de/DE-MASTER.xml.gz
- DE alternativ: https://epgshare01.online/epgshare01/epg_ripper_DE1.xml.gz
- AT: https://epgshare01.online/epgshare01/epg_ripper_AT1.xml.gz
- CH: https://epgshare01.online/epgshare01/epg_ripper_CH1.xml.gz
- NL optional: https://epgshare01.online/epgshare01/epg_ripper_NL1.xml.gz

Erreichbarkeit, Rechte und Inhalte vor produktiver Übernahme prüfen.
