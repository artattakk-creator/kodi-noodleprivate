# XCMate – TiviMate 5.3.3: Einstellungsseiten / dritte Nutzer-Fotoserie

**Datum:** 14.10.2026 · **Status:** Fotoverifizierte UI-/Funktionsanforderung, nicht gleichbedeutend mit implementierten Kodi-Funktionen. **Quelle:** zehn vom Nutzer bereitgestellte Fotos (Originaldateien `1000118374.jpg` bis `1000118383.jpg`), TiviMate `Einstellungen`. Fotos verbleiben in der Konversation und werden wegen TV-Bildern, fremdem Design und eingeblendeten Zugangsdaten **nicht** im öffentlichen GitHub-Repository gespeichert.

**Schutzregel:** Ein Screenshot zeigt eine gekürzte, token-/benutzernamenhaltige XMLTV-URL. Die komplette oder teilweise URL, Hostname, Benutzername, Playlistname sowie Zugangsdaten **nicht** in Repository, Tests, CI, Logs oder Screenshots kopieren. In diesem Dokument nur `[private EPG source redacted]`. Zählwerte und Portalnamen sind dynamische Nutzerdaten, keine Programmkonstanten.

**Ziel:** XCMate bildet Bedienlogik, Menüstruktur, Wertefelder, Schalter und Aktionen funktionsgleich in einer eigenständigen Oberfläche ab. Eigene Marke, eigene grafische Elemente, freigegebenes Slate-Grau als Standard. Unterschiede zwischen Kodi-Add-on und nativer Android-App müssen in der UI klar gekennzeichnet werden.

## Bildindex, genaue Menüpfade und gezeigte Zustände

| Foto | Menüpfad | Sichtbarer Inhalt / bestätigter Wert |
| --- | --- | --- |
| `1000118374.jpg` | Einstellungen | Kategoriefolge: **Allgemein → Wiedergabelisten → EPG → Optik → Wiedergabe → Fernbedienung → Kindersicherung → Sonstiges → Über** |
| `1000118375.jpg` | Einstellungen / Allgemein, oben | Auto-Boot **aus**; Start nach Sleep Mode **aus** (gerätabhängig); zuletzt angesehenen Sender bei Start anzeigen **ein**; PiP beim Home-Menü **aus**; doppeltes Zurück zum Verlassen **aus**; User-Agent **Nicht festgelegt**; UDP-Proxy `Adresse:Port` **Nicht festgelegt** |
| `1000118376.jpg` | Einstellungen / Allgemein, unten | Gezeigte Schalter wie oben; zusätzlich **Daten sichern** und **Daten wiederherstellen** als getrennte Aktionen |
| `1000118377.jpg` | Einstellungen / Wiedergabelisten | Ein vorhandener, markierter/aktivierter Playlist-Eintrag mit dynamischem Namen und Anzahl Kanäle/Filme/Serien; Aktionen **Hinzufügen** und **Aktualisiere alle Wiedergabelisten** |
| `1000118378.jpg` | Wiedergabelisten / ausgewählte Playlist | **Aktivieren**; **Playlist Name**; **EPG Quellen** (im Screenshot eine zugeordnet); **Logo Priorität = Logos aus der Playlist bevorzugen**; **Archiv = Xtream Codes**; **User-Agent = Nicht festgelegt**; **Xtream Codes Parameter**; **Gruppen verwalten** |
| `1000118379.jpg` | Wiedergabelisten / ausgewählte Playlist, unten | **Update-Optionen**; **Aktualisierungsintervall (Stunden) = 24**; **Aktualisieren beim Starten der App = aus**; **Aktualisieren**; **Löschen** |
| `1000118380.jpg` | Einstellungen / EPG, oben | **EPG Quellen**; **Vergangene Tage, um EPG zu behalten = 7**; **Programmbeschreibungen speichern = ein**; **Update-Optionen**; **Aktualisierungsintervall (Stunden) = 24**; **Aktualisieren beim Starten der App = aus**; **Aktualisieren bei Playlisten-Änderung = aus**; **Aktualisieren**; **Löschen** (weiter unten) |
| `1000118381.jpg` | Einstellungen / EPG, unten | dieselben Optionen; zusätzlich **Letzter Aktualisierungsstatus** mit Zeitpunkt, Kanalanzahl und Erfolgsstatus als *dynamisches Ergebnis* |
| `1000118382.jpg` | Einstellungen / EPG / EPG Quellen | Zugeordnete **Standardquelle**, URL mit privaten Parametern **redigiert**; **Quelle hinzufügen**; Hinweis: EPG-Quellen werden den Wiedergabelisten in den Playlist-Einstellungen zugewiesen |
| `1000118383.jpg` | Einstellungen / Optik | **EPG**, **Player**, **Gruppen**, **Logos** als Unterrubriken; **Sprache = System**, **Schriftgröße = Mittel**, **Farbthema = Dunkel · Blau**, **Transparenz der Benutzeroberfläche (%) = 50** |

### Sichtbarkeitsgrenzen / Unsicherheiten

- Ein durch Aktivierungs-Häkchen erkennbar verwendeter Playlist-Eintrag ist vorhanden; die Position des Schalters `Aktivieren` auf dem markierten Detailbild ist optisch nicht hinreichend eindeutig. **Nicht** als unabhängige Boolean-Auswertung speichern.
- Alle dargestellten `aus`/`ein`-Zustände sind Nutzerkonfigurationen aus dem Screenshot, nicht zwingend TiviMate-Werksdefaults und keine für bestehende XCMate-Installationen ungefragt zu überschreibenden Werte.
- Inhalte der Menüpunkte `Wiedergabe`, `Fernbedienung` (ergänzend zu bisher gelieferten Fotos), `Kindersicherung`, `Sonstiges`, `Über` und der Optik-Untermenüs werden mit späteren Fotos konkretisiert. Für nicht sichtbare Untermenüs **keine Funktionen erfinden**.

## Verbindliches Einstellungsmodell für XCMate

### Navigation

`SETTINGS_ROOT` → `GENERAL` | `PLAYLISTS` | `EPG` | `APPEARANCE` | `PLAYBACK` | `REMOTE` | `PARENTAL` | `MISC` | `ABOUT`.

Weitere Pfade:
- `PLAYLISTS` → `PLAYLIST_DETAIL(portal_id)` → `PLAYLIST_EPG_ASSIGNMENTS` / `LOGO_PRIORITY` / `ARCHIVE_CATCHUP` / `XTREAM_PARAMS` / `GROUP_MANAGER` / `PLAYLIST_UPDATE_OPTIONS`.
- `EPG` → `EPG_SOURCES` → `EPG_SOURCE_DETAIL(source_id)`.
- `APPEARANCE` → `EPG_APPEARANCE` / `PLAYER_APPEARANCE` / `GROUPS_APPEARANCE` / `LOGOS_APPEARANCE`; Sprach-, Schrift-, Farb-, Transparenzauswahl.
- Aktionen `backup`, `restore`, `update_one`, `update_all`, `update_epg`, `delete_playlist`, `clear_epg`, `add_playlist`, `add_epg_source`.

### 1. Allgemein

| Feld-ID (Vorschlag) | Label | Foto-Wert | Typ / Sicherheitsregel |
| --- | --- | --- | --- |
| `android_auto_start_on_boot` | Automatisch nach dem booten starten | aus | Gerätespezifisch; Android-Boot-Broadcast nicht durch Kodi-Add-on erzwingbar; ggf. nur als separat unterstützte Host-Integration |
| `android_resume_from_sleep` | Automatisch aus dem Sleep Mode starten | aus | Android-Gerätefunktion, in Kodi ggf. nicht verfügbar; Hinweis anzeigen |
| `startup_last_channel` | Zuletzt angesehenen Sender beim Start anzeigen | **ein** | optional; Konfliktregel zu bestehendem XCMate-Startsender, persistente Sender-ID je Portal, nur mit Nutzerfreigabe setzen |
| `android_home_pip` | Wechsel in den Bild-in-Bild-Modus bei Home | aus | Android-Host-/Kodi-Unterstützung prüfen, nicht vortäuschen |
| `double_back_to_exit` | Doppelt mit Zurück bestätigen, um zu verlassen | aus | nur add-on-eigenes Exit-Verhalten, niemals Kodi global umbelegen |
| `user_agent_global_override` | User-Agent | nicht festgelegt | optionaler Override; vorhandenen XCMate-`user_agent`-Wert NICHT ändern oder löschen |
| `udp_proxy_override` | UDP Proxy (Adresse:Port) | nicht festgelegt | Validierung und sichere Persistenz; Kodi-Proxy-Schnittstellen nachweislich unterstützen |
| `backup` | Daten sichern | Aktion | Backupdatei außerhalb GitHub, sensiblen Inhalt kennzeichnen / optional verschlüsseln |
| `restore` | Daten wiederherstellen | Aktion | explizite Bestätigung, Vorab-Backup, Schema-/Konfliktprüfung, atomische Wiederherstellung; niemals unbestätigt überschreiben |

### 2. Wiedergabelisten / Portalverwaltung

- Liste dynamischer Portale/Playlists mit Auswahl-/Aktivindikator, Name, `live/vod/series`-Anzahl und Detailnavigation.
- `Hinzufügen` → existierenden XCMate-Portalassistenten nutzen (Xtream/M3U/Stalker, keine neue Provider-Bindung).
- `Aktualisiere alle Wiedergabelisten` → pro Portal Background-Worker und Statusmeldung; vorhandene gute Caches bei Fehlern belassen.
- `Playlist Name` → bestehende Portal-ID muss erhalten bleiben, nur Anzeigename ändern.
- `EPG Quellen` → vorhandene EPG-Quellen im **jeweiligen Portal** zuweisen; bestehende Zuordnungen unverändert lassen.
- `Logo Priorität` → `Playlistlogos bevorzugen`; spätere Auswahlalternativen erst nach weiteren Fotos festlegen.
- `Archiv` → `Xtream Codes` als fotografierte Auswahl; keine Aussage zu anderen verfügbaren Archiven.
- `User-Agent` → portalbezogene Abweichung vom Globalwert (keine Credentials in Logs).
- `Xtream Codes Parameter` → nur eigenes Untermenü, Eingabe von Zugangsdaten nie im UI-Log ausgeben.
- `Gruppen verwalten` → bestehende Gruppenselektion, IDs und deaktivierte Gruppen beibehalten.
- `Aktualisierungsintervall (Stunden)` → 24 (fotografiert).
- `Aktualisieren beim Starten der App` → aus.
- `Aktualisieren` → explizit pro Portal; `Löschen` → nur nach Bestätigung, andere Portale/EPG-Zuweisungen unberührt.

### 3. EPG-Verwaltung

- Globale EPG-Quellenliste, Quelle hinzufügen und Quellzuweisung **je Portal** (auch benutzerdefinierte XMLTV-Feeds).
- `Vergangene Tage, um EPG zu behalten` → 7; für Catch-up vergangene Sendungen nicht vorzeitig löschen.
- `Programmbeschreibungen speichern` → ein.
- `Aktualisierungsintervall (Stunden)` → 24.
- `Aktualisieren beim Starten der App` → aus.
- `Aktualisieren bei Playlisten-Änderung` → aus.
- `Aktualisieren` und `Löschen`: getrennte Aktionen, Löschen nur nach expliziter Bestätigung. Präzise unterscheiden zwischen Entfernen einer Quelle, Löschen zwischengespeicherter EPG-Daten und Löschen der Portal-EPG-Zuordnung.
- `Letzter Aktualisierungsstatus`: Zeitstempel, Anzahl verarbeiteter Sender, Erfolg/Fehler je Quelle oder Portal, **keine** XMLTV-URL inklusive Tokens.
- Mehrere Quellen und Priorität sind bereits in XCMate spezifiziert; ein Hinweis „in Playlist-Einstellungen zuweisen“ soll analog erscheinen.

### 4. Optik

- `EPG`, `Player`, `Gruppen`, `Logos` als Unterseiten.
- `Sprache` → System.
- `Schriftgröße` → Mittel.
- `Farbthema` → fotografierter TiviMate-Wert „Dunkel · Blau“, aber **XCMate-Standard bleibt eigenes dunkles Slate-Grau**. Blau und weitere Akzentfarben werden als optionale Designs auswählbar, nicht als automatischer Standardwechsel.
- `Transparenz der Benutzeroberfläche (%)` → fotografierter Wert 50; später Einstellregler mit Live-Vorschau und ausreichendem Textkontrast.
- Der visuelle Fokuszustand und die Overlay-Transparenz gehören zur freigegebenen eigenständigen Space-/Silver-Branding-Spezifikation.

## Bestehender XCMate-Stand und Abweichungen (geprüft gegen `main`)

- Add-on `plugin.video.xtreammate` Version **0.1.10**, Repository **1.7.0**.
- Bereits vorhanden: Portal hinzufügen/verwalten, EPG-Quellen verwalten/Zuordnungen, `epg_refresh_hours`, `epg_hours_back`, globale `user_agent`-Einstellung, Fernbedienung anlernen und eigenständige Live-Overlay-Bausteine.
- Der derzeitige `settings.xml`-Dialog ist in Kodi-eigenen Kategorien aufgebaut und **nicht** die nun fotografierte TiviMate-Einstellungsnavigation. Ein eigener Kodi-Einstellungscontroller müsste die neun Hauptrubriken reproduzieren; keine blinde Änderung der existierenden Setting-IDs.
- `epg_hours_back` begrenzt bestehende Vergangenheitsdarstellung und ist **nicht automatisch** eine Aufbewahrung von sieben vergangenen Tagen.
- Android-Auto-Boot, Wake, Home-PiP sind **Host-Funktionen** und können nicht durch ein Kodi-Plugin allein garantiert werden.
- Die projektweit höchste Priorität **P0 Startsender / Fernbedienungsfokus / Android-Log-Validierung** bleibt ausdrücklich offen.
- Frühere Referenzen: [Fernbedienung](TIVIMATE_REMOTE_REFERENCE_2026-10-14_DE.md), [TV/EPG/Film-Bilder](TIVIMATE_UI_SCREEN_REFERENCE_2026-10-14_DE.md), [Design](DESIGN_SYSTEM_DE.md).

## Test- und Releaseanforderungen

1. Bildgetreue UI-Feldliste und nummerierte Fotoquellen in Regressionstest gegen die Spezifikationsdatei prüfen.
2. Neue Einstellungen ausschließlich durch additive, versionierte und **nicht destruktive** Profilfelder mit Default-Fallback ergänzen; niemals bestehende Providerdaten beim Lesen/Schreiben überschreiben.
3. Keine Secrets oder originalen URL-Strings auf GitHub oder in CI ausgeben; persönliche Screenshotdaten auf Platzhalter begrenzen.
4. Bei jeder tatsächlichen Implementierung automatisierte Tests, GitHub-Build, ZIP und `addons.xml`-Checksumme prüfen, danach Android mit Titan BINGIE MOD; erst dann **ON-DEVICE PASS**.
5. Bei nächsten Fotos die fehlenden Unterseiten ergänzen und die bereits fotografierten Werte als Nutzerreferenz beibehalten. Alle Einstellungen müssen künftig **änderbar** sein; fotografierte Schalterzustände sind kein Vorschlag, bestehende Nutzereinstellungen zurückzusetzen.
