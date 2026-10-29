# XCMate .55 – Issue- und Abnahmematrix

Keine Issues schließen. Code-/Host-PASS ist keine Android-Abnahme; alle 24 neuen Gerätegates sind NOT_TESTED.

| Referenz | Umsetzung | Status / offene Abnahme |
|---|---|---|
| #266 Master / aktueller Chat-P0 | gleiche .55: verwaisten Live-Handoff lösen, Settings erneut ermöglichen, eigenes Queuing per Back abbrechbar, feste Diagnosegründe; Stop-Kern erhalten | TEILWEISE: Host-Reproduktion korrigiert, konkreter Geräteauslöser/20 Zyklen NOT_TESTED |
| #267 Quellnavigation | passiver nativer Widgets-Ordner mit genau drei Quellen, keine neue Verwaltung; vollständige gespeicherte Startgruppe, Reload-Hooks | TEILWEISE: originaler Picker-/Reader-/150-Sender-Hostnachweis PASS; echtes Speichern/Neustart auf BINGIE NOT_TESTED |
| #239 gemeinsame Sendungsbilder | vorab persistierte HTTPS-URL im vorhandenen Eventindex, starke Quellenbindung, readonly Hero/EPG-Detail; keine Fokus-/Detailrecherche; Hintergrundpflege | TEILWEISE: automatische Tests PASS, echte Film-/Episode-/Eventbilder und URLgleichheit sichtbar NOT_TESTED |
| #252 Widget-/BINGIE-UX | bestehende Live-/Recent-Routen, Poster-/Detailziele, Legacy-URLs, Medien und Refresh erhalten | TEILWEISE: Hostregressionen PASS, drei echte Home-Reihen und Autorefresh NOT_TESTED |
| #254 BINGIE-Adapter | tatsächliche Home-Includes nach Vorlage, vier-Dateien-Diff/Hash-Guards, privates Backup/Restore, bekannter .50-Upgrade; keine Anwendung | HOST PASS / GERÄT NOT_TESTED; konkrete Skinanwendung weiterhin gesonderte Freigabe erforderlich |
| #265 .54-Abnahme | historisch 17 PASS / 0 FAIL / 7 NOT_TESTED bleibt erhalten; keine Umdeutung zu .55-PASS | ERHALTEN: Wizard-/Import-/Stop-Rohhashschutz, .55-Regression NOT_TESTED |
| #263 Wizard | Feature-Freeze; kein Umbau, keine Änderungen an Login, Passwort, Portal, Gruppen, Checkpoints, Import oder Slideshow | UNVERÄNDERT; nicht erneut als neuer .55-Fix beansprucht |
| TV Spielfilm | keine lizenzierte/zugelassene API nachgewiesen | BLOCKED_NO_AUTHORIZED_API / Bildrechte nicht belegt; kein Scraping/Hotlinking |
| Weitere Bildhosts | exakte HTTPS-Hostfreigabe und positive öffentliche DNS-/Bildheader-Vorprüfung, keine Credentials/Querytokens | Ohne Freigabe BLOCKED_IMAGE_HOST_OR_URL; neutraler Fallback, kein Bild-PASS |
| Box A / produktives main | kein Gerätezugriff, keine Skin-/Profiländerungen, kein Merge/Release | UNVERÄNDERT |
