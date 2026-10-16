# XCMate 0.1.18 – regionale XMLTV-EPG-Pakete

## Fest hinterlegte, frei auswählbare EPG-Quellen

| Kürzel | Quelle | XMLTV-URL |
| --- | --- | --- |
| DE Master | Kaimandura | https://kaimandura.github.io/epg-de/DE-MASTER.xml.gz |
| DE Alternativ | EPGShare01 | https://epgshare01.online/epgshare01/epg_ripper_DE1.xml.gz |
| AT | EPGShare01 | https://epgshare01.online/epgshare01/epg_ripper_AT1.xml.gz |
| CH | EPGShare01 | https://epgshare01.online/epgshare01/epg_ripper_CH1.xml.gz |
| NL optional | EPGShare01 | https://epgshare01.online/epgshare01/epg_ripper_NL1.xml.gz |

Stand der Quellenrecherche: 16.10.2026. Diese Daten werden von Dritten
bereitgestellt und sind weder Teil der Add-on-Datei noch garantiert verfügbar.
Senderabdeckung (insbesondere Sky-Eventkanäle) kann wechseln. Rechte und
Nutzungsbedingungen des jeweiligen EPG-Anbieters sind zu beachten.

## Bedienung auf Kodi / Android-TV

1. XCMate → EPG verwalten / Einstellungen → EPG-Quellen und Senderzuordnung.
2. „EPG-Paket Deutschland / Österreich / Schweiz / NL“ wählen.
3. Einzelne regionale Quelle oder „DACH-Paket“ hinzufügen. Niederlande
   ist nur einzeln wählbar. Bereits vorhandene URLs werden nicht verdoppelt.
4. Nach automatischem EPG-Refresh ggf. „Xtream-Sender einem XMLTV-Kanal
   zuordnen“ für noch fehlende Sender auswählen.
5. In der Quellenliste lassen sich Quellen deaktivieren, verschieben oder löschen.

Der Anbieter-EPG hat Vorrang; die zuerst konfigurierte XMLTV-Quelle ergänzt
fehlende IDs, weitere Feeds füllen weitere Lücken. Bei eindeutig passendem
Sendernamen kann XCMate anhand des lokal gecachten Xtream-Senderkatalogs
automatisch verbinden. Bei mehrfach vorkommenden Namen über mehrere
Länder oder unsicherer Senderidentität wird *nicht* geraten.
Eine ausdrücklich manuell gespeicherte Zuordnung hat Vorrang.

Konfiguration und manuelle Mappings liegen getrennt im persistenten Kodi-
Benutzerdatenbereich; der eigentliche Programmführer wird im Cache gehalten.
Beim ersten Start des EPG-Managers werden nicht ungefragt alle Länder
heruntergeladen, um Android-TV-Speicher und Laufzeit zu schonen.

**Hinweis:** Die derzeitige Fernbedienungs-/TV-Overlay-Diagnose wird durch
diese Änderung nicht verändert; diese bleibt ein separates offenes Thema.
