# Testbericht XCMate 0.1.29.77

Status: **Host / gesamte Source-CI / native Linux-Prüfungen PASS**. Source-PR #383 und Pilot-Release #384 gemergt; **PILOT_RELEASED**, öffentliche/native Update-Erkennung PASS. Source-Basis `2710431`, Installer 0.5.26 unverändert. Kein Android-PASS.

- 105 fokussierte Regressionen: PASS nach Korrektur der alten Stop-/Freigabeerwartungen.
- 39 .77-Tests einschließlich kumulativer Bestandsschutzprüfung: PASS.
- 11 vorhandene pytest-Brandingprüfungen: PASS (eine bestehende Drittanbieterwarnung).
- Vollständige unittest-Suite: **3.155/3.155 PASS, 616,738 Sekunden**. Nach der abschließenden Texturecache-Diagnoseänderung 13 frische betroffene Tests PASS. Finale CI auf `a2f8c29f9f1f6c2feb14ed302ba8a585709661e4`: **3.155 PASS in 532,673 Sekunden**, außerdem 11 pytest PASS; alle zehn Workflows grün. Frühere Entwicklungsdurchläufe mit veralteten Prüfvertragsdaten bzw. ohne Loopback-Freigabe sind keine Abschlussnachweise.
- Geerbtes Lite-CI-Gate erwartete noch Installer 0.5.21, obwohl main bereits 0.5.26 publiziert. Ausschließlich die Prüfversion und der fest gepinnte vorhandene ZIP-Hash wurden auf den unveränderten .5.26-Stand aktualisiert; kein Installer-Code/Paket verändert.
- Native Medienzyklen: **60/60 PASS**, je 20 Film, Episode und Live-TV in echtem Linux-Kodi; nativer Stop/ACK, GUI-RPC weiter bedienbar und echte Fortschrittswerte bei Film/Episode. Android-Rückkehr unverändert ANDROID_NOT_TESTED.
- Native Home: erster CI-Lauf zeigt korrekte Hero- und Detailpixel; nachgelagerte Texturecache-Abfrage lieferte PENDING. Cachezustand wird nun ehrlich getrennt vom bereits gemessenen sichtbaren Bild gewertet. Endgültiger lokaler und CI-Lauf **720p/1080p PASS**, je 31 Ansichten + 20 native Richtungsaktionen, 7 weitere Neustart-/Reload-Ansichten, Reihen 88/24/24 und 32 geschützte Dateien unverändert. Testumgebungsfehler werden nicht als Gerätefehler oder PASS ausgegeben.
- ZIP: 739 Dateien, CRC und vollständiger Bytevergleich zum Add-on-Quellbaum PASS; SHA256 siehe Paketdatei.
- Android .76 Sendungsbilder: FAIL laut Nutzer. Android .77 alle P0-Gates: ANDROID_NOT_TESTED.

| Issue | Implementierung | Geräteabnahme |
|---|---|---|
| #380/#366 Bilder | Quellenmigration, sicherer Full-Decode, Lease-/Negativcache, Render-/Texture-Diagnose implementiert | ANDROID_NOT_TESTED |
| #367 Home | gezielter Space-Blue-Adapter, feste vollflächige Darstellung, Controlfehler entkoppelt | ANDROID_NOT_TESTED |
| #368 Exit | Mediencheckpoint, Android-Fullscreen-Freigabe, einzelner nativer Stop/ACK, Quarantäne | ANDROID_NOT_TESTED |
| Kodi-Library/EPG-Polls | lesende Diagnose und begrenzte quellensichere Leseleases | ANDROID_NOT_TESTED |

Keines dieser P0-Issues wird aufgrund von Hosttests geschlossen. Source-Merge: `2a498044135d27b44b53d6d35d96cba7d59ce98b` (PR #383). Paket: 739 Dateien / 3.441.153 Bytes, SHA256 `8060b83e1b5153cb52cc7449bd4799d8b477517dcea84a6775cd3b63b4840bc8`. Evidenz: `test-builds/02977/evidence/`. Pilot-Freigabe und öffentliche Update-Erkennung siehe RELEASE_02977_PILOT_DE.md.

## Messwerte und Grenzen

- Modellierter wiederholter EPG-Miss: 10 gleiche Aufrufe → 1 DB-Fensterlesung innerhalb des begrenzten Leases, statt 10 unabhängiger Lesungen. Quellen-/Mappingwechsel und Ereignisgrenzen invalidieren; kein geräteseitiger Latenz-PASS behauptet.
- Native Bildfälle: vollständige HTTPS-PNG/JPEG-Dekodierung, identischer Event, korrekte Hero- und Detailpixel. Textur-Datenbank weiterhin PENDING; dies ist kein Nachweis dauerhafter Kodi-Texturecache-Persistenz. XCMate-URL-/EPG-Readback und Profile bleiben geprüft.
- Native Render-Settle-Messwerte enthalten absichtliche Fixture-Wartezeiten (lokal 720p Median ca. 2.821 ms), keine Produktions-Latenzmessung.
- Android: reale Folge + realer Film mit richtigen Bildern/Screenshots, XMLTV ohne Token, TVMaze, Fokus/Neustart sowie je 20 Exit-Zyklen weiter ANDROID_NOT_TESTED. Historische .76-Bilder bleiben Nutzer-FAIL.
- Vorhandene Token auf echten Geräten wurden nicht gelesen/übertragen. Integritätsnachweise beziehen sich auf synthetische Hostprofile; echter Vor-/Nachvergleich bleibt Android-Gate. Alte explizite Deaktivierung wird anhand der von Kodi gespeicherten Default-/Nichtdefault-Kennung erkannt; historische Absicht, die Kodi bereits als Default serialisiert hat, ist nachträglich nicht rekonstruierbar. Neue Opt-out-Marker verhindern spätere Reaktivierung.
- Unbekannte Skinänderungen sind bewusst BLOCKED. Beim ersten fokussierten eigenen Widget bietet der Service die gesicherte Home-Vorschau an; ohne Bestätigung keine Skinänderung. Manueller technischer Zugang über Einstellungen → Experimentell → Widget-Einrichtung, nicht über die unveränderten drei normalen Widgetquellen. Der verkürzte Pfad im Diagnosehinweis ersetzt diese Anleitung nicht.
