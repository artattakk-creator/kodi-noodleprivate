# XCMate .61 – Ursachen und Beweisgrenzen

Basis main f0e29c1ac758e5eb48083fa2d8e70f07d185bb43 (.60), erneut abgefragt. Issue #286 und beide Nachträge vollständig gelesen; Android-FAIL hat Vorrang vor synthetischen .60-Ergebnissen.

**Bestätigter Codefehler:** home_menu Widgets öffnet absichtlich nur widget_sources49. Die echte Verwaltung widget_setup war nicht in appearance verlinkt; die Layoutvorbereitung war ausschließlich ein Kontextmenü. Deshalb war der in .60 dokumentierte Installationsweg nicht durchführbar. .61 ergänzt sichtbaren Settings-Zugang, getrennte Widget-Einrichtung im Hauptmenü und normale OK-Aktionen für Vorschau und Restore. Vorhandener Adapter: ausdrücklich bestätigbarer einmaliger Builder-Aufruf statt Sackgasse. Keine Anwendung beim Update, keine Schleife.

Vier-Dateien-Adapter, native LiveRow/Hero, Senderquelle, ursprüngliche Reihenfolge, komplette Gruppe, gespeicherte Quellen-URLs, Film-/Serienbindings und .42-Kompatibilitätsmodus bleiben unverändert. Das Fehlen von EPG/Bildern/Token darf keine Datenzeilen filtern. Nicht belegt ist, ob auf der realen Box zusätzlich eine fremde Skin-Dateiversion, abweichende Bindung, fehlerhafte generierte Includes oder Visibility vorliegt. Ohne aktives Android-Profil keine Behauptung eines Geräte-PASS.

Hosttestgrenze: native Kodi 21.2/Linux und originale BINGIE-2.2.3-Dateien; synthetischer Provider mit 88 Sendern. .61-Test beginnt mit ungepatchten vier Skin-Dateien, folgt sichtbaren Menülinks, bedient echte Vorschau/Bestätigung, lässt Produktionscode sichern/anwenden und prüft anschließend Home10000/Container2510/Fokus0,1,87/persistente Logos. Externe Helfer sind isolierte Stubs. Der Builder-Stub installiert erst nach Zustimmung die Ausgabe des unveränderten, gepinnten Skinshortcuts-2.1.0-Templatecompilers; dies ist kein Beweis des vollständigen Android-Skinshortcuts-Laufs. Android21.3 bleibt NOT_TESTED.

P0-Zwischenstand wird vor Token-Erweiterung mit unveränderlichem Commit-/ZIP-Link bereitgestellt. Kein Merge, kein produktives Release, keine Geräteinstallation.

## Zentraler privater Tokenzugang (separater Commit)

Einzige Tokenauflösung: `tmdb_token61.effective_tmdb_read_token()`. Ziel ausschließlich `special://profile/addon_data/plugin.video.xtreammate/tmdb_read_access_token.txt`. Gültige Datei vor Legacy-Feld; bestehende defekte/unlesbare Datei führt zu festem Fehlercode und keiner HTTP-Anfrage. Das Format ist ein JWT-förmiger API Read Access Token; echte Authentifizierung kann nur der Verbindungstest bestätigen. Kein mitgelieferter Token.

Lokaler Kodi-Dateidialog (USB/Downloads), begrenztes Lesen, UTF-8/eine Zeile, maximal 4097 Bytes; Dateideskriptor-Walk mit O_NOFOLLOW und O_NONBLOCK blockiert Symlinks, FIFOs, Verzeichnisse, relative/Netzwerk-/VFS-Pfade und Traversal. Keine SAF-/SMB-Umgehung; nicht als lokale Datei zugängliche Quelle wird verständlich abgewiesen. Atomarer Austausch mit exklusiver temporärer Datei/0600/fsync, Prüfung des vorher ausdrücklich bestätigten Zielinhalts, Quelle bleibt erhalten. Nur temporäre Importdateien werden bei Fehlern aufgeräumt, keine Benutzerdaten.

Verbindungstest, Artwork-Tokenclient, Matchingdiagnose und gemeinsamer Programmcache verwenden dieselbe Auflösung. Private Dateilesung auf explizitem UI-/Workerpfad, maximal alle 30 Sekunden pro Interpreter/Profil; Import/Test erzwingen Refresh. Fokus-Fingerprint verwendet ausschließlich RAM/Kodi-Property und Legacy-Einstellungsfingerprint. Die Kodi-Property enthält nur eine SHA256-Revision, niemals den Token. Kein neues Netzwerk im Fokus, keine neue Datenbank, keine Änderung des Provider-Metadaten-/Coverpfads. Beide Opt-ins bleiben standardmäßig false und werden durch Import nicht geändert.

Android-Privatpfad, Dateidialog, Berechtigungen, echte TMDB-Authentifizierung und spätere Sendungsbilder sind ANDROID_NOT_TESTED; Hosttests verwenden ausschließlich generierte Syntax-/Transportfixtures.
