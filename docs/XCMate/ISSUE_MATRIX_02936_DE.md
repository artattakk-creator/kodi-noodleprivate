# XCMate .36 – Issue- und Restpunktmatrix

Stand 25.10.2026, kumulativer Draft. Vollständiger erneut über GitHub abgeglichener Snapshot aller **50 offenen Issues**: [ISSUE_MATRIX_02936.json](ISSUE_MATRIX_02936.json); 6 Teilumfänge hostverifiziert, 1 neue Funktion hostseitig implementiert, 1 neuer Reparaturansatz BLOCKED und 42 Issues außerhalb dieses Pakets weiterhin offen. Kein Issue geschlossen. **Vollständig nach Android-Abnahme behoben: noch kein Issue.** „Host verifiziert“ ist kein Android-PASS und schließt keine breit gefasste Anforderung. Historische .35-Abnahme bleibt 15/15 funktional PASS; alle .36-Gates zunächst NOT_TESTED.

| Issue | Art / .36-Unterumfang | Hoststand | Android-Gate | Gesamtstatus / nächster Schritt |
| --- | --- | --- | --- | --- |
| #140 | Vorversionsfix: lokale Now-/Short-Suche, fehlende Cache-Dateien überspringen, Phasen/Abbruch | Cache-/XML-/Alias-/50k- und UI-Regressionsfälle verifiziert | S36-01/02/03/06 | **Teilweise behoben, NOT_TESTED**: reale Latenz/Coverage nachweisen; umfassender Hub später .42 |
| #127 | Suchqualität/Cover/Fokus; kein Layoutumbau | UI-/Asset-Freeze, Mediennavigation und Suchdaten verifiziert | S36-01/03/08/10 | **Teilweise behoben, NOT_TESTED**, keine pauschale Gesamtschließung |
| #120 | Startsender aus lokalem Index, doppelte Kataloglesung entfernt | Index/Legacy/aktivierte Gruppe/Resolver vs Direct verifiziert | S36-04/09 | **Teilweise behoben, NOT_TESTED**: tatsächlicher Start/Video kalt/warm fehlt |
| #17 | Info-/Mini-Datenvorbereitung und Reaktionsmessung | Native Controls/Renderer/Zapping unverändert; begrenzte Hintergrunddaten | S36-05/06/09 | **Teilweise behoben, NOT_TESTED**; OSD-Neugestaltung .39 bleibt offen |
| #35 | Start/Pre-play und NowNext-Latenz | Bestehender Player-/Handshakevertrag und neue Zuordnungsmessung | S36-04/05/07 | **Teilweise behoben, NOT_TESTED**; keine behauptete physische First-Frame-Zeit |
| #75 | Sessionweite Stop/Home-Idempotenz, vorhandene Home wiederverwenden | Zwei Fensterinstanzen, 20 Zyklen, fremde Player/Modals, einmaliger Directory-Abschluss | S36-07, Baseline REG-03 | **Teilweise behoben, NOT_TESTED**: echter Kodi-/Skin-Doppelroute-Test und historische Popup-Gates bleiben offen |
| #97 | Geschlossene Vorgeschichte der Stop-Navigation | Bestehende Stop-Regression erweitert | S36-07 | **CLOSED bleibt CLOSED**; keine Wiedereröffnung/Schließaktion |
| #159 | **Neue Funktion enthalten:** echte Film-/Serien-Genresuche, Aliase, Titelranking, additive Nachindizierung | 23 gezielte Fälle, 1k/50k-Messung, Datenintegrität/Quellwechsel/IR-Modell | S36-10 / GENRE-01–07, S36-12 | **Implementierung hostseitig vollständig; Android NOT_TESTED**, Issue bleibt OPEN |
| #111 | Neuer Poster-/TMDb-Reparaturansatz | Bestehender selektiver Retry geprüft und unverändert geschützt; keine neue Quellenreparatur | S36-11 NOT_TESTED / nicht enthalten | **BLOCKED**: konkrete private Bildfehlerphase/Werkidentität fehlt; Untersuchung .37, Großmigration ggf. .43 |
| #91 | SQLite-/Cache-Sicherheit innerhalb der Pflichtpfade | Eigene kurzlebige Verbindungen, WAL-/Originaltabellen unverändert, Worker-Cancel/BUSY getestet | S36-12 | **Weiterhin offen** als breiter Hygieneauftrag; kein eigenständiger C4-Fix behauptet |
| #60/#58 | Quellen-/Coverage-Diagnostik | Bestehende Diagnose erhalten, keine neue Fusion | S36-02/09 | **Weiterhin offen** für geplanten EPG-Hub .41/.42 |
| #98/#161 | Manuelles Quellenmapping / EPG-Hub | Keine Migration/Implementierung dieses Workstreams | Nicht im .36-Paket | **Weiterhin offen** .41/.42, Preview-/Confirm-Vertrag bleibt bestehen |
| #43 | Wizard / zweite Box | Keine Änderung im .36-Paket | WIZ-01–12 separat NOT_TESTED | **Weiterhin offen**: eigener Preview-Branch/-Draft, kumulative Integration .37 nach .36-Freigabe |
| #94/#95/#150 | Rail und dauerhaft zweispaltiges Mini-EPG | Unveränderte heutige Links-Kette | Eigener UX-Testplan | **Weiterhin offen**, nach aktueller Roadmap .38 |
| #62/#63/#126/#135/#136 | Aufnahme/Download/USB/SMB | Quellen dieses Subsystems unverändert | Nicht im .36-Paket | **Weiterhin offen**, Storage-Workstream .44 |

Neue .36-Gerätebefunde werden mit PASS/FAIL/BLOCKED/NOT_TESTED und konkretem Repro in die .37-Restpunktliste übernommen; schwere Regressionen blockieren schon die aktuelle Freigabe. Keine Issues eigenmächtig schließen, main mergen oder Repository veröffentlichen.
