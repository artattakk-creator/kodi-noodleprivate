# Testbericht XCMate 0.1.29.77

Status: Prüfung läuft. Source-Basis `2710431`, Installer 0.5.26 unverändert. Kein Android-PASS.

- 105 fokussierte Regressionen: PASS nach Korrektur der alten Stop-/Freigabeerwartungen.
- 39 .77-Tests einschließlich kumulativer Bestandsschutzprüfung: PASS.
- 11 vorhandene pytest-Brandingprüfungen: PASS (eine bestehende Drittanbieterwarnung).
- Vollständige unittest-Suite: läuft erneut mit benötigtem lokalem Netzwerkzugriff; frühere Entwicklungsdurchläufe mit veralteten Prüfvertragsdaten bzw. ohne Loopback-Freigabe sind keine Abschlussnachweise.
- Native Home 720p/1080p und native Medienzyklen: Prüfung läuft. Testumgebungsfehler werden nicht als Gerätefehler oder PASS ausgegeben.
- ZIP: 739 Dateien, CRC und vollständiger Bytevergleich zum Add-on-Quellbaum PASS; SHA256 siehe Paketdatei.
- Android .76 Sendungsbilder: FAIL laut Nutzer. Android .77 alle P0-Gates: ANDROID_NOT_TESTED.

| Issue | Implementierung | Geräteabnahme |
|---|---|---|
| #380/#366 Bilder | Quellenmigration, sicherer Full-Decode, Lease-/Negativcache, Render-/Texture-Diagnose implementiert | ANDROID_NOT_TESTED |
| #367 Home | gezielter Space-Blue-Adapter, feste vollflächige Darstellung, Controlfehler entkoppelt | ANDROID_NOT_TESTED |
| #368 Exit | Mediencheckpoint, Android-Fullscreen-Freigabe, einzelner nativer Stop/ACK, Quarantäne | ANDROID_NOT_TESTED |
| Kodi-Library/EPG-Polls | lesende Diagnose und begrenzte quellensichere Leseleases | ANDROID_NOT_TESTED |

Keines dieser P0-Issues wird aufgrund von Hosttests geschlossen. Abschlussergebnisse und Veröffentlichung werden nach erfolgreicher CI ergänzt.
