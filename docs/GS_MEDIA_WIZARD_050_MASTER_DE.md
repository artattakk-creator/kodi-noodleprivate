# GS Media Setup 0.5.x – verbindlicher Komplett-Neuaufbau (03.11.2026)

## Ziel
Einmalig das eigene Online-Repository auf frisch installiertem Kodi 21.3 ARM32 einbinden. Danach **einen Knopf** im GS Media Setup betätigen und alle elf vereinbarten Apps, Abhängigkeiten, Original-Repositories, BINGIE-Skinpatch, Menüs/Widgets und TMDB-xVAULT-Player mit nachvollziehbarem Status installieren. Kein PC, keine USB-Dateien, kein manuelles Suchen nach Upstream-ZIPs. Kodi-eigene Sicherheitszustimmungen bleiben erhalten.

## Aktueller Android-Befund
Das öffentliche Online-Test-Repository 1.8.2 und Setup 0.4.0 wurden erfolgreich direkt über Kodi installiert (Issue #323). Der Installer blieb bei script.bingie.helper hängen, da repository.titan.bingie.mod nicht selbst installiert wurde. Nutzer installierte BINGIE-Repository und Helper manuell. **Dieses Teilsystem ist vorhanden und darf nicht neu installiert, gelöscht oder zurückgesetzt werden.**

## Installationssequenz
1. Kodi 21.3/ARM32, freier Speicher, Internet, Add-on-Inventur, vorhandene Konfigurationen und Backup/Estuary-Recovery.
2. Verifiziertes Original-BINGIE-Repository 2.0.1 **aus dem GS Media Katalog per Kodi InstallAddon**, aktiv bestätigen, danach script.bingie.helper und Helper/Resource-/Skinshortcuts-Abhängigkeiten in tatsächlicher Manifest-Reihenfolge.
3. Erst nach allen BINGIE-Abhängigkeiten Titan BINGIE MOD 2.2.3; Version und originale XML-Hashes sichern, bei Fehler Rollback. Skin nicht vor erfolgreichem Setup blind aktivieren.
4. XCMate und restliche Pflichtprogramme: Cumination, xVAULT, TMDB Helper, SlyGuy Trailers, YouTube, MP3 Streams Echoed, SHOUTcast, EZ Maintenance+, Caber Toss sowie alle transitive Dependencies und jeweiligen Original-Repositories.
5. BINGIE-Menü und Widgets: Live-TV XCMate, Filme XCMate, Serien XCMate zuerst, anschließend restliche bestätigte Einträge. Live-Hero, EPG-Now/Next, Fokus prüfen.
6. Für TMDB Helper xVAULT als Default für **Filme und Episoden** einstellen. XCMate nutzt eigene TMDB-EPG-Artwork-API, keine TMDB-Helper-Abhängigkeit für TV-Bilder; optional TVMaze.
7. Vollständigen Healthcheck (Alle Apps+Dependencies aktiviert, gepinnte Quellen, BINGIE, TMDB, Live-TV/VOD/Serien, Medienplayer, EPG, Neustart). Erst bei belegtem PASS Kodi neu starten und XCMate-Wizard **einmalig** öffnen. Sonst FAIL/BLOCKED.

## Quellen-/Lizenzvertrag
- Der bisherige produktive GS-Media-Katalog bleibt unverändert. Nur isolierter Entwicklungszweig und Online-Testkanal.
- Drittanbieter nur mit gültigem Autorisierungsnachweis spiegeln: Originalquelle, Paket-ID, Version, SHA256, Nutzungs-/Weitergaberechte, vollständige Lizenzhinweise und GPL-Quellcode-/Änderungsnachweise. Keine willkürlichen ZIPs und keine Aneignung fremder Urheberschaft. Wenn Mirror nicht zulässig: verifizierter legitimer Upstream-Feed.
- Kodis InstallAddon(id) installiert aus einem vorhandenen Repository. InstallFromZip öffnet nur die manuelle Dateiauswahl. Also **alle benötigten Bootstrap-Repositories und Anwendungen** vor dem Installationslauf im eigenen geprüften Online-Katalog referenzieren beziehungsweise zulässig bereitstellen; sonst keine ehrliche Ein-Knopf-Installation.
- Der Fortschritt zeigt bestätigte Installationsschritte (Komponente, Phase, Quelle, Anzahl, Erfolg, Fehler/Retry). Native Kodi-Downloadanzeige für Pakettransfer. Nicht unüberprüft Netz-Byte-Prozentwerte behaupten.
- Bereits installierte BINGIE Repo/Helper und GS-Media-Pilot-Repo korrekt erkennen; Pilotrepo-ID repository.gsmedia.pilot für XCMate akzeptieren.
- Eigenes atomisches secretfreies Journal, Cancel/Pause/Resume nach Neustart, keine Bootloops, keine bereinigenden Add-ons ohne Zustimmung, keine Kodi-App-Daten-Löschung.

## Im neuen Branch bereits implementiert
Branch feat/gsmedia-wizard-050-oneclick-20261103 (auf PR #320 / XCMate .70):
- setup_auto50.py: automatische Sequenz, Repo vor Helper/Skin, Sicherheitsschritte, Pilot-Repo-Unterstützung, Retry/Resume.
- setup_auto_store50.py: secretfreies atomar gespeichertes Journal.
- setup_auto_ui50.py: ein Startknopf, nichtmodale Fortschrittsanzeige, Kodi InstallAddon und JSON-RPC-Verifikation, kontrollierter BINGIE-Skinpatch mit Backup, TMDB-xVAULT-Player, STOP bei nicht belegter Paketfreigabe.
- Default-Menü mit automatischer Einrichtung und Stop-Steuerung; Setup-ZIP auf 0.5.0 umgestellt.
- tests/test_gsmedia_setup_auto50.py; CI testet reine Steuerlogik, Syntax, Paketbau, SHA.
- Entwicklungsstand **NICHT PRODUKTIONSREIF**: BINGIE Repo ist noch nicht im Online-Testkatalog gepinnt und freigegeben; restliche Fremd-Repositories ebenfalls nicht. Android-End-to-End noch nicht nachgewiesen. Das darf nicht als Komplettinstallation ausgewiesen oder als Update an Box A ausgerollt werden.

## Fortsetzungsauftrag für Codex – zwingend
A. Alle elf Apps und rekursiv erforderlichen aktuellen addon.xml-Imports aus echten Upstream-ZIPs mit Kodi 21.3/ARM32, SHA, Originalquelle, Lizenz, Erlaubnis zur Weitergabe prüfen; maschinenlesbare BOM/Lockdatei.
B. Original-Repositories und erlaubte Pakete dem isolierten Kodi-Online-Katalog hinzufügen; zuerst BINGIE Repo 2.0.1 -> BINGIE Helper -> Skin 2.2.3 als lückenlosen Ein-Knopf-PASS beweisen.
C. Automatische sequenzielle Installationen ohne erneuten Wizard-Start; Fortschritt/Downloadstatus/Fehler/Retry/Resume und ständiges Validieren anhand Kodi.
D. Tests für frisches Kodi und den aktuellen teilinstallierten Zustand; schlechte Quelle, 404, Hash-Fehler, kein Speicher, Stromverlust, Skin-Hänger, Rollback, Produktiv-Katalog unverändert.
E. Online-Test-Update über repository.gsmedia.pilot erst nach Quell-/Android-Gates. Kein voreiliger Merge nach main; XCMate .70 Speicher-/Artwork-Bugs (#315/#322) separat beheben.

Verknüpfungen: #317, #323, #315, #322 und PR #320.
