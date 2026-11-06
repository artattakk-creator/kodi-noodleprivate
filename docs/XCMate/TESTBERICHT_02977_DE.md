# Testbericht XCMate 0.1.29.77

Status: Host-Gesamtlauf bestanden; finale CI-/Native-Home-Prüfung läuft. Source-Basis `2710431`, Installer 0.5.26 unverändert. Kein Android-PASS.

- 105 fokussierte Regressionen: PASS nach Korrektur der alten Stop-/Freigabeerwartungen.
- 39 .77-Tests einschließlich kumulativer Bestandsschutzprüfung: PASS.
- 11 vorhandene pytest-Brandingprüfungen: PASS (eine bestehende Drittanbieterwarnung).
- Vollständige unittest-Suite: **3.155/3.155 PASS, 616,738 Sekunden**. Nach der abschließenden Texturecache-Diagnoseänderung 13 frische betroffene Tests PASS. Finale CI prüft nochmals den exakten Commit. Frühere Entwicklungsdurchläufe mit veralteten Prüfvertragsdaten bzw. ohne Loopback-Freigabe sind keine Abschlussnachweise.
- Geerbtes Lite-CI-Gate erwartete noch Installer 0.5.21, obwohl main bereits 0.5.26 publiziert. Ausschließlich die Prüfversion und der fest gepinnte vorhandene ZIP-Hash wurden auf den unveränderten .5.26-Stand aktualisiert; kein Installer-Code/Paket verändert.
- Native Medienzyklen: **60/60 PASS**, je 20 Film, Episode und Live-TV in echtem Linux-Kodi; nativer Stop/ACK, GUI-RPC weiter bedienbar und echte Fortschrittswerte bei Film/Episode. Android-Rückkehr unverändert ANDROID_NOT_TESTED.
- Native Home: erster CI-Lauf zeigt korrekte Hero- und Detailpixel; nachgelagerte Texturecache-Abfrage lieferte PENDING. Cachezustand wird nun ehrlich getrennt vom bereits gemessenen sichtbaren Bild gewertet. Endgültiger 720p/1080p-Lauf läuft. Testumgebungsfehler werden nicht als Gerätefehler oder PASS ausgegeben.
- ZIP: 739 Dateien, CRC und vollständiger Bytevergleich zum Add-on-Quellbaum PASS; SHA256 siehe Paketdatei.
- Android .76 Sendungsbilder: FAIL laut Nutzer. Android .77 alle P0-Gates: ANDROID_NOT_TESTED.

| Issue | Implementierung | Geräteabnahme |
|---|---|---|
| #380/#366 Bilder | Quellenmigration, sicherer Full-Decode, Lease-/Negativcache, Render-/Texture-Diagnose implementiert | ANDROID_NOT_TESTED |
| #367 Home | gezielter Space-Blue-Adapter, feste vollflächige Darstellung, Controlfehler entkoppelt | ANDROID_NOT_TESTED |
| #368 Exit | Mediencheckpoint, Android-Fullscreen-Freigabe, einzelner nativer Stop/ACK, Quarantäne | ANDROID_NOT_TESTED |
| Kodi-Library/EPG-Polls | lesende Diagnose und begrenzte quellensichere Leseleases | ANDROID_NOT_TESTED |

Keines dieser P0-Issues wird aufgrund von Hosttests geschlossen. Abschlussergebnisse und Veröffentlichung werden nach erfolgreicher CI ergänzt.
