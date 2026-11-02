# GS Media Setup 0.2.4 – Stand 02.11.2026 – nur Vorprüfung

**Wichtig:** Development Draft PR #318 / Master #317 / keine installierende Funktion.
Build basiert auf main XCMate .68; keine Änderungen am produktiven Repository.

## Verbindliches GS-Media-Standardprofil
Im Oktober-2026-Backup nachgewiesene Add-on-IDs, **alle elf zwingend**:
1. skin.titan.bingie.mod (Backup 2.2.3; 13 direkte Imports)
2. plugin.video.xtreammate (aktuell main .68; Hotfix .69 getrennt in #315)
3. plugin.video.cumination (Backup 1.1.204; 8 direkte Imports)
4. plugin.video.xvault (Backup 2026.10.20.1, 1 Pflicht-/12 optionale Manifestimports)
5. plugin.video.themoviedb.helper (Backup 5.4.16; 7 Imports)
6. slyguy.trailers (Backup 0.2.4, benötigt SlyGuy Common)
7. plugin.video.youtube (im Backup eine SlyGuy-YouTube-Repository-Variante; Quelle vergleichen)
8. plugin.audio.m3sr2019 (MP3 Streams Echoed 2026.1.0; 3 Module)
9. plugin.audio.shoutcast (Kodi offizielles Paket; xbmcswift2/xmltodict)

Alle elf gehören ins Standardprofil, nicht nur als Medien/Musik-Zusatzoption.

## Tatsächlich aus den addon.xml-Dateien des entpackten Backups
- **Cumination**: script.module.six, script.module.kodi-six, script.module.resolveurl >=5.0.00, script.module.resolveurl.xxx >=2.0.1, script.common.plugin.cache, script.module.websocket >=0.50.0, script.module.inputstreamhelper, script.module.requests.
- **SlyGuy Trailers**: script.module.slyguy >=0.86.96; Common benötigt slyguy.dependencies >=0.0.30 und repository.slyguy >=0.0.9; slyguy.dependencies setzt repository.slyguy voraus.
- **BINGIE**: 13 direkte Abhängigkeiten im setup_plan.py, darunter Skin Helper Service/Widgets/Backgrounds, TMDB Helper, YouTube und Skinshortcuts.
- **TMDB Helper**: xbmc.python, requests, PIL, addon.signals, jurialmunkey, infotagger, beautifulsoup4.
- **MP3 Echoed**: xbmc.python, beautifulsoup4, requests, routing.
- **xVAULT**: laut gesichertem addon.xml nur xbmc.python *zwingend deklariert*; 12 weitere Module/Player sind **optional deklarierte Imports**, nicht pauschal installpflichtig. Für benutzte Funktionen kann eine Laufzeitprüfung nötig sein; ResolveURL wird bereits über Cumination verpflichtend.
- **YouTube-Variante**: im Backup war ein Wrapper mit import auf repository.slyguy.youtube. Der offizielle Kodi-YouTube-Plugin-Stand kann andere Abhängigkeiten besitzen. Diese Paket-Variante nicht unbemerkt überschreiben.
- **SHOUTcast**: laut offiziellem Kodi-/PR#312-Plan benötigt script.module.xbmcswift2 und script.module.xmltodict.

**Die vollständige rekursive Dependency-Closure ist noch nicht für jedes Third-Party-Addon nachgewiesen.** Bei jedem Unknown oder unbestätigtem ZIP/SHA führt der Installer später FAIL-CLOSED aus.

## Andere im Backup gefundene Add-ons – vorerst NICHT Pflicht
EZ Maintenance+, Last Played, Global Search, TV Spielfilm, Stalker Mod,
xShip, Vavoo, SlyGuy Pluto Provider, weitere Dritt-Repository-IDs.
Sie sind eine Inventur, keine implizite Installationsfreigabe.

## Version 0.2.4 kann
- In Kodi ein Standardprofil mit allen elf Apps darstellen.
- Über read-only JSONRPC den Bestand und deaktivierte Add-ons erkennen.
- Bekannte Abhängigkeiten vor den konsumierenden Apps sortieren.
- Pflichtprogramme im Report kennzeichnen und optionale xVAULT-Imports benennen.
- Fehlende/veraltete/ungeprüfte Quellen sicher blockieren.
- Ein testbares Kodi-ZIP samt SHA256 per GitHub Actions bauen.

**Noch nicht implementiert**: Freigegebene Drittanbieter-ZIPs und deren Hash-/Lizenzliste, echte InstallAddon-Ausführung, automatische Skin-Patches, Kodi-Neustart/Resume und Android-Tests. Keine Downloads, Schreiboperationen, Profilveränderungen oder Auto-Installation.

Verbindlicher Folgeauftrag: #317, #315 sowie PR #312 und PR #318.


## Neues BINGIE-Layout: userbestätigter Entwicklungsauftrag
Aus dem archivierten 21.10.2026-Backup wurden folgende Daten rekonstruiert:
`skin.titan.bingie.mod-mainmenu.DATA.xml`,
`skin.titan.bingie.mod.properties`, `settings.xml`.
Dies belegt **historische** Menüs/Widgetverweise, nicht die gegenwärtige
Konfiguration der produktiven Box A. Die Sicherung enthält teils
Datei-Zeitstempel von Juni 2025.

**Zwingende zusätzliche Add-ons:**
`script.ezmaintenanceplus` (Backup 2026.04.05.0; requests >=1.0.0)
und `script.cabertoss` (offizielles Kodi-Omega-Repo; 1.0.2).
EZ Maintenance darf niemals selbsttätig Cache, Datenbanken oder Kodi-Profil
löschen. Caber Toss soll per Kodi-eigenen Addon eingerichtet werden, sein
Zielordner z.B. SMB/USB ist pro Gerät auszuwählen (keine Pfade mit Geheimnissen
aus altem Backup kopieren).

**Portable Vorschau in `setup_layout.py`:**
Live-TV/XCMate, Filme, Serien, Netflix (Provider 8), Amazon Prime (9),
Disney+ (337), Paramount+ (531), Apple TV (2), XXX/Cumination, Radio/
SHOUTcast, MP3 Streams Echoed, xVAULT, Wartung und Caber Toss.
TMDB Discover-Verknüpfungen aus deutschem `watch_region=DE`-Profil.
Echte Backup-Widgetpfade: Im Kino, Diese Woche im Trend, Disney Plus,
MP3 Streams Echoed Top World Albums (Musikroute muss aktuell geprüft werden).
Weitere historische Widgets (TV Spielfilm etc.) nur bei installierter
Zusatz-App und mit separater Zustimmung ergänzen.

**Noch NICHT angewendet:** Die BINGIE-Konfiguration wird aktuell ausschließlich
als read-only Vorschau angezeigt. Vor Installation/Geräteabnahme müssen
Skinshortcuts-Schema und existierende Userkonfiguration sicher migriert
werden. Neue Geräte dürfen nach Zustimmung GS-Media-Standardlayout erhalten.
Bestehende Geräte bekommen Diff/Backup/Merge statt ungefragtem Überschreiben.
Die Live-EPG-Hero-Quelle wird erst mit XCMate-Hotfix #315 stabil verfügbar;
keine erfundene Plugin-Route hinterlegen. Das Layout ist ohne echte
TMDB-API-/Widget-/Fernbedienungsprüfung nicht als Android-PASS zu markieren.


## Verbindliche Vorgabe: BINGIE zuerst XCMate + drei XCMate-Homewidgets
Die ersten drei Home-Widgets müssen lauten:
1. XCMate Live-TV: `plugin://plugin.video.xtreammate/?action=widget_live_start_group`
2. XCMate Filme: `plugin://plugin.video.xtreammate/?action=widget_recent_vod`
3. XCMate Serien: `plugin://plugin.video.xtreammate/?action=widget_recent_series`

Beleg aus aktuellem XCMate-main: `widget_entry46.py`, `app_routes.py`
und `setup_entry48.py`. Der erste Hauptmenüpunkt ist XCMate Live-TV.
Der Live-TV-Hero muss aus #315 URL-only korrekt mit der gewählten Sendung
versorgt werden; ohne echtes Artwork keinen generischen Platzhalter
einblenden. Die ursprünglichen TMDB-, Musik- und Anbieterwidgets kommen
erst nach den XCMate-Zeilen. Die Widget-Routen sind im Code geprüft, aber
noch nicht in BINGIE auf Android gerendert.

## Erst komplette GS-Media-Installation, dann Neustart und XCMate-Einrichtung
Zwingende Reihenfolge für die künftige Installer-Implementierung:
- Alle 11 Pflichtprogramme und deren echte rekursive Abhängigkeiten erfolgreich
  installieren/aktivieren; Quellen/Versionen/ZIP-Hashes verifizieren.
- BINGIE-MOD-Patches, Menüdefinitionen und sämtliche vorgesehenen Widgets
  auf dem neuen Gerät erfolgreich übernehmen und nachprüfen.
- Kodi-/Skin-Healthcheck vollständig bestanden; nur nach ausdrücklicher
  Setup-Bestätigung und neuer frischer GS-Media-Installation.
- Erst DANACH Abschlussmarker persistieren und Kodi kontrolliert neustarten.
- Nach verifiziertem neuem Kodi-Boot **erneut** den Add-on-/Dependency-
  Installationsstatus kontrollieren; bei Lücke, deaktivierten Add-ons oder
  gescheitertem Skin-/Widget-Apply nichts automatisch öffnen.
- Nur dann EINMAL `RunPlugin(plugin://plugin.video.xtreammate/?action=setup_wizard)`
  über die vorhandene XCMate-Wizardroute auslösen. Die später zuständige
  Kodi-Startkomponente muss den Handoff `attempted` *atomar vor* dem
  RunPlugin-Aufruf setzen, um Boot-Loops zu vermeiden.
- Bei abgebrochenem Wizard kein unendliches Autostart-Verhalten; Nutzer kann
  die XCMate-Einrichtung manuell fortsetzen. Bereits eingerichtete Kodi-
  Boxen niemals ungefragt in eine neue Ersteinrichtung schicken.

`setup_handoff.py` modelliert die reine read-only Gate-Entscheidung mit
Unit-Tests. **GS Media Setup 0.2.4 selbst ist weiterhin keine installierende
oder automatisch startende Service-Komponente**; es schreibt noch keinen
Handoff-Marker und startet XCMate beim Boot nicht tatsächlich. Erst beim
vollständigen Installer mit Bestandsdatensicherung und Android-Test aktivieren.


## TMDB Helper: xVAULT als voreingestellter Player (unverbindliche Preview)
Im Google-Drive-Kodi-Backup vom 21.10.2026 liegen bereits `plugin.video.themoviedb.helper/players/xvault_stable.json` und die TMDB-Helper-Einstellungen `default_player_movies=xvault_stable.json play_movie` sowie `default_player_episodes=xvault_stable.json play_episode`. Die xVAULT-Quelle enthält ihr eigenes `resources/tmdbhelper/xvault.json`; das `tmdbhelper_integration.py` aus dem gesicherten xVAULT-Stand kopiert bei Bedarf nach `xvault_stable.json`. Der Kodi-xVAULT-Router unterstützt `action=playTMDbHelper` für Filme und Serien. **Nicht blind an Player-Konfiguration anderer Geräte arbeiten.** Der künftige Installer soll bei *frischer, bestätigter GS-Media-Komplettinstallation* nach Installation/Aktivierung von TMDB Helper und xVAULT die Playerdatei aus dem geprüften Original xVAULT-Paket bereitstellen/verifizieren und beide TMDB-Helper-Standardwerte setzen; dabei vorherige Werte sichern und nach der Konfiguration einen echten Film-/Serien-Playbacktest ausführen. Auf eingerichteten Bestandsboxen keinerlei ungefragte Änderungen. Danach erst Installationsabschluss markieren, Kodi neu starten und XCMate-Wizard einmalig öffnen. Solange auch nur einer der Player-Gates nicht bestätigt ist, kein Setup-Handoff. Die neue Datei `setup_tmdb_player.py` beschreibt diese Prüfung bisher ausschließlich **read-only** und schreibt keine TMDB-Helper-Einstellungen.
