# GS Media – Kerninstallationspaket 1.8.2 und späterer Komplett-Backup-Manager

**Stand: 02.11.2026. Verbindliche Produktanforderung, keine bereits erfolgte Veröffentlichung.**

## Zielbild für eine frische Kodi-Box

Der Nutzer will nach Installation von Kodi 21.3 und GS Media Repository die **vier prioritären Apps samt funktionsnotwendigen Abhängigkeiten** über einen geprüften Installationsplan beziehen:

1. XCMate (`plugin.video.xtreammate`), aktueller veröffentlichter Stand .66; Playback-/EPG-Hotfix .67 getrennt (#307).
2. xVAULT (`plugin.video.xvault`) und erforderliche Kodi-Python-Module/ResolveURL; offizielle xVAULT-Pakete/Updatequellen und native Android-ARM32-Binärkomponenten passend zur Plattform.
3. MP3 Streams (`plugin.audio.m3sr2019` **Echoed** bevorzugt, wenn die Quelle wiederhergestellt und Kodi-21-Playback verifiziert wurde). Das separat installierte Legacy-`plugin.audio.mp3streams` darf nicht unbemerkt ersetzt oder heruntergestuft werden.
4. SHOUTcast (`plugin.audio.shoutcast`) aus der offiziellen Kodi-21-Omega-Quelle, mit `xbmcswift2` und `xmltodict`.

Die tatsächlich vom Upstream bestätigten Komponenten und die Herkunft stehen maschinenlesbar in `docs/GS_MEDIA_CORE_182_RELEASE_MATRIX.json`. Der Gate `tools/gsmedia_core_release_gate.py` gibt **Exit-Code 2**, solange auch nur ein Pflichtpaket ohne geprüfte, erreichbare Quelle und erfolgreich getesteten ZIP-Installationspfad bleibt.

## Was derzeit bestätigt ist und was NICHT

- GS Media 1.8.1 ist auf `main` publiziert; nur XCMate .66, Noodle Private .4.2 und das Repository selbst sind im eigenen Index.
- Kodi 21 liefert SHOUTcast 2.5.2+matrix.1 über die **offizielle Kodi-Repositorystruktur**. SHOUTcast-Manifest aus `xbmc/repo-plugins` Branch `matrix`: `xbmc.python >=3.0.0`, `script.module.xbmcswift2 >=19.0.0`, `script.module.xmltodict >=0.12.0`.
- xVAULT `2026.11.01.1` ist als offizielles Paket unter `mojomedia1812/xVAULT` / `docs/plugin.video.xvault/` gelistet. Seine eigenen Dokumente verlangen mindestens die Runtime-Komponenten `requests`, `six`, `pyaes`, `infotagger`, `resolveurl`; weitere Module/ARM32-Visuals sind optional. **Der Hersteller weist ausdrücklich darauf hin, dass Drittanbieter-Reuploads nicht als originale, unterstützte Installationen überprüft werden können.** Deshalb bevorzugt die Integration das originalsignierte Release und das offizielle xVAULT-Repository; kein umgebautes xVAULT-ZIP als scheinbar offizielles Update verteilen.
- Die zuletzt in PR #303 verwendete Quelle `Echo-Storm/MP3-Streams-2026-Kodi` für `2026.1.0` liefert HTTP 404. Ältere Forks (`L2501` Version 0.0.7) sind **kein** gleichwertiger Ersatz und dürfen bestehende .2026-Versionen nicht downgraden. Source Recovery/autorisiertes ZIP/prüfbare Lizenz ist P0-Baustein dieses Integrationszweiges.
- Das Backup vom 21.10.2026 enthält historische Add-on-Verzeichnisse (109), aber **keinen bestätigten vollständigen aktuellen Boxzustand vom 02.11.** Historische Existenz eines Moduls ist kein Test einer Neuinstallation.

## Codex-Auftrag – Release 1.8.2 (erst nach allen Gates)

1. Eigene, überprüfbare Download-Pins (Original-URL, SHA256 und Upstream-Metadaten, Version, Lizenz) je Zielpaket ermitteln. Für MP3 Echoed 404 **keinen Hash erfinden** und keine unerlaubte Quelle ersetzen.
2. Für jede der vier Apps die **vollständige rekursive** Manifest-Dependency-Closure auf Kodi 21.3 Android ARM32 erstellen; unterscheiden: `xbmc.python`/System, offizielle Kodi-Module, externes ResolveURL, optionale InputStream-/native Visualizer-Komponenten.
3. Versandmodell wählen: geprüfte Pakete in GS Media selbst **oder** vom Nutzer ausdrücklich bestätigte Installation über das offizielle Original-Repository. Die UI muss transparent angeben, aus welchem Repo installiert wird. Keine ungeprüften Fremd-Sammelkataloge wieder in `repository.gsmedia/addon.xml` einhängen.
4. Nach Quelle/Lizenz-/ABI-Check die betreffenden Add-on-IDs einzeln in `APPROVED_ADDON_IDS` aufnehmen und den Indexbuilder um sichere, explizit gepinnte Paketimporte ergänzen. Jedes Paket: ZIP-Pfade/CRC/Manifest-ID/Version, Hash, Lizenz, kein Traversal/Symlink/Zipbomb, transitive Abhängigkeiten, keine Geheimnisse.
5. Autoupdate darf keinen stabilen Bestand durch Nightly/downgrade ersetzen; xVAULT-Stable-Channel und MP3-Version exakt prüfen; bei fehlender Quelle Fail-CLOSED, nicht eine Null-Datei oder Placeholder publizieren.
6. Test auf sauberem Kodi-21.3-Android-ARM32 sowie Update-Installationen bestehender Boxen: Installierbarkeit, Start/Playback, Dependency-Status, Coldboot, BINGIE, XCMate, getrennte Datenbereiche.
7. ZIP/SHA und `addons.xml` erst nach grünen CI-Tests + erforderlicher Nutzerfreigabe nach `main`. Bis dahin bleibt **1.8.1 stabil** und dieses Vorhaben Draft.

## Anschließend: GS Media Backup & Restore (privat, kein öffentlicher GitHub-Upload)

**Backup-Komplettmodus, später implementieren:**

- Add-on-Inventur mit IDs, Versionen, Quellen, aktiviert/deaktiviert und Prüfsummen;
- `userdata/addon_data` und Einstellungen inkl. XCMate-Portalen, TMDB-Zugang, Favoriten, Wiedergabestatus, Quellenmapping, EPG-Konfiguration;
- Kodi-Datenbanken, inklusive lokalem EPG, Video/Resume sowie relevante Textures/Thumbnail-Metadaten;
- Skin Titan BINGIE MOD: eigene XML-/Widget-Shortcuts und gesicherte aktiv benutzte Skin-Helfer-Konfigurationen;
- Benutzerdateien wie `guisettings.xml`, `sources.xml`, `advancedsettings.xml`, Keymaps, Profile; geplante Ausnahmen für Cache/Temp/Logs bzw. optionale Thumbnails nach Größe;
- SMB/USB-Ziele nur als Pfad-/Mapping-Einträge mit Zielprüfung; Android-spezifische Berechtigungen, APK und OS-Zustand gesondert dokumentieren;
- Atomarer Snapshot nach datenbankkonsistentem Export, SHA256-Manifest, vollständige Dateiliste, Wiederherstellungsvorschau, Schutz vorhandener Daten, optional passwortverschlüsselt und mit Offline-/NAS-/USB-Kopie.

**Restore-Betrieb:** kontrollierter Offline- oder Pausenmodus; keine Wiedergabe / DB-Writes während Rücksicherung; vor jeder Änderung Backup des Zielgeräts; Komponenten gezielt auswählbar; Versions-/Architekturprüfung; Nutzerfreigabe; sichere reversible Umbenennung/Kopie; anschließend Start-/Integritätsprüfung und Rückrollplan. Keine Portal-Secrets, Tokens oder privaten Backups in öffentliche Releases/CI/GitHub.

**Wichtig:** Das am 21.10.2026 gesicherte Masterbackup ist ein historischer Referenzstand. Ein vollständiges Recovery **des aktuellen** Zustands braucht ein frisches Backup **nach** der Kerninstallation und den Hotfix-Abnahmen.

Referenzen: #305 Repository/Wizard, #307 Live-P0, PR #306 Setup-Wizard, PR #309 Repo 1.8.0, PR #310 1.8.1 Lite.
