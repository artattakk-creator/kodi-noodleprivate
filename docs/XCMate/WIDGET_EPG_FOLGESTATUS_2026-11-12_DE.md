# Fortsetzungsstatus – Widget-, EPG- und Artwork-Master

Aktuelle verbindliche Folge: großer Hero, Senderlogo-Leiste, **Filme → Serien → Im Kino → Disney → Diese Woche im Trend → MP3s**, danach persönliche BINGIE-Widgets. Kein Bewertungsranking, keine Änderung gespeicherter Quellenordner.

| Block | Umsetzung / Abnahme |
| --- | --- |
| Uhr-Token / MediaRow-Zulassung | kleiner eigenständig geprüfter Draft #437; reale 1510/1520/1530-Consumer im Referenzprofil, keine Änderung der echten URL |
| Gemeinsame Header/Spinner | im vorhandenen auf #437 gestapelten Draft #438 für alle sechs Reihen implementiert; Deadline, Leer-/Fehlerzustände, Originalanimation |
| Zusatzquellen | tatsächliche gespeicherte Quellen privat read-only verifiziert; vier zusätzliche private Consumer, keine belegten Benutzer-Slots überschrieben |
| Wiederaufbau / Navigation / Klickziele | native Linux-720p-/1080p-Belege einschließlich aller sechs Reihen und drei Prozessneustarts; aktueller finaler Stand im Hauptbericht |
| Echte Anbieter / Android21.3 | NOT_TESTED für jede Reihe; keine Hostsimulation als Geräte-PASS |
| EPG Home/Mini/Groß/Details | vorhandene gemeinsame lokale Komponenten erhalten; konkrete Geräte-Synchronität und Galileo-Fallback #433 weiterhin offen |
| Speicherung der manuellen TMDB-/TVMaze-Zuordnung | historischer Nutzer-FAIL #433 offen; keine unbelegte Festlegung auf Dateirechte |
| Speicher / SQLITE_BUSY / Artwork-Vollständigkeit | Schutz und Bestandsregressionen erhalten; reale Quellen-/Reserve-/Mount-/Pixelabnahme #430 offen |
| Rolling-Cache / sichere Altlastenbereinigung | #108 weiterer Arbeitsschritt; keine blinde Löschung, aktives Staging/WAL/letzte gültige Sicherung geschützt |
| Player-Exit | #174 Android-FAIL bleibt offen; synthetischer Audio-Stop bestätigt keinen Rockchip-Live-/Film-/Serien-Fix |

[Implementierung, Ursachen, vollständige Tests und Paket](SIX_ROWS_TESTBERICHT_2026-11-12_DE.md) · [Android-Abnahme](ANDROID_ABNAHME_PR438_DE.md).

Die frühere Einschränkung auf nur zwei implementierte Reihen ist überholt. Der gesamte Master ist dennoch nicht als abgeschlossen geschlossen: zuerst konkrete Widget-Geräteabnahme, danach größerer EPG-/Artwork-/Cache-Umbau in getrennt prüfbaren Schritten.

Main, regulär, Pilot, NeoDark3 und Installer 0.5.26 wurden durch diese Arbeit nicht verändert. Kein automatischer Merge/Release.
