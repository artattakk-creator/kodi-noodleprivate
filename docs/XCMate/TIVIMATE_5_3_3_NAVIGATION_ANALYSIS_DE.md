# XCMate: statische Navigationsanalyse TiviMate 5.3.3

**Datum:** 14.10.2026 · **Zweck:** Interaktionsmuster aus einer vom Nutzer bereitgestellten Android-APK dokumentieren und als unabhängige Funktionsspezifikation für XCMate prüfen. **Keine Code-/Asset-Übernahme aus TiviMate.**

## 1. Eingabedatei und Verifikation

- Nutzerdatei: `tivimate-iptv-player-5-3-3.apk` (nur lokal analysiert; APK nicht im GitHub-Repository abgelegt).
- SHA-256 der analysierten APK: `beaebb25bf818450bf496d4cefb16885b190f156815dea280c31eaae0909ee6c`.
- Größe: rund 21 MB. Android-Manifest: `package=ar.tvplayer.tv`; `versionName=5.3.3`; `versionCode=1000005332`.
- Android `minSdkVersion=23`, `targetSdkVersion=34`.
- Enthalten: drei DEX-Dateien, `resources.arsc` mit ca. 31.293 Einträgen über verschiedene Sprachen, darunter deutsche UI-Texte.
- Die APK enthält `libdexprotector.so` und eine hochentropische `assets/assets.dat`-Datei. Anwendungscode/Klassen sind umfangreich obfuskiert bzw. geschützt. Aus der statischen Analyse sind **nicht** sämtliche realen Controller-Zustandsübergänge oder Werkseinstellungen der Tasten sicher ableitbar. Keine Behauptung, die App sei vom offiziellen Anbieter signiert oder die jüngste öffentlich verfügbare Version.
- Statische Analyse: Manifest/XML und Ressourcentabelle gelesen, keine Installation/Ausführung, keine Provideranmeldung, keine Umgehung des Schutzes.

## 2. Direkte APK-Befunde: Fernbedienungstasten

Die übersetzten Ressourcen enthalten getrennte UI-Bezeichnungen für `Back`, `Down`, `Left`, `Menu`, `OK`, `Right`, `Up`, `Play/Pause`, `Guide`, `Info`, `Record`, `Stop`, `Rewind`, `Fast forward`, `Pg-/Ch-`, `Pg+/Ch+`, Lautstärke, Stumm sowie Rot/Grün/Gelb/Blau.

Insbesondere **lange Tastendrücke** besitzen eigene Einträge: `Long Back`, `Long Down`, `Long Left`, `Long Menu`, `Long OK`, `Long Play/Pause`, `Long Right`, `Long Up` (Ressourcen-IDs `0x7f130368`–`0x7f13036f`). Weitere Eingaben `Menu+` (0x7f130011), `Reorder buttons` (0x7f130380), `Remote control` (0x7f13037f), `Restore to defaults` (0x7f13038e) bestätigen ein anpassbares Belegungskonzept.

**Wichtig:** Das Vorhandensein einer auswählbaren Aktion ist nicht der Nachweis, dass sie standardmäßig auf einer bestimmten Taste liegt.

### In der APK ausdrücklich angezeigte kontextabhängige Tastenhinweise

| Ressource | Originalhinweis, sinngemäß | Einordnung |
| --- | --- | --- |
| `0x7f130445` | Lange OK öffnet Menü; Links zeigt Gruppen; langes Links navigiert zu früheren Programmen | Direkter Hilfetext, mutmaßlich im Guide-/Gruppenkontext; keine Aussage für jeden Bildschirm |
| `0x7f130441` | Langes Zurück kehrt zum Player zurück | Expliziter Hilfetext, kontextabhängig |
| `0x7f1301c7` | Erneut drücken, um Sender zu wechseln | Hinweis auf zweistufiges Umschalten bzw. Vorschaumodus |
| `0x7f1301c8` | OK drücken, um das Menü anzuzeigen | Expliziter Hilfetext, abhängig vom aktiven Dialog |
| `0x7f130358` | OK zum Einschalten des Senders | Expliziter Hinweis für die Senderauswahl |

## 3. Nachgewiesener Katalog konfigurierbarer Fernbedienungsaktionen

In den Android-Stringressourcen liegen u. a. diese Aktionsnamen vor (IDs gehören zur **APK**, nicht zu Kodi-Action-IDs):

| APK-Ressourcen-ID | Englischer Eintrag | Vorgesehene XCMate-Entsprechung |
| --- | --- | --- |
| `0x7f13024a` | Turn on most recent channel | Vorheriger/zuletzt gesehener Sender |
| `0x7f13024b` / `0x7f13024f` | Turn on next / previous channel | Direkt zappen |
| `0x7f13024c` / `0x7f130250` | Show info panel for next / previous channel | Sender-Vorschau vor dem Umschalten |
| `0x7f130254` / `0x7f130255` | Page scroll channels down / up | Seitenweises Scrollen |
| `0x7f130256` / `0x7f130257` | Scroll to next / previous programs | Zeitachse im EPG bewegen |
| `0x7f130258` / `0x7f130259` | Show channels list groups in overlay / preview mode | Gruppenliste über laufendem TV bzw. mit Vorschau |
| `0x7f13025a` / `0x7f13025b` | Show channels list in overlay / preview mode | Senderliste in zwei Modi |
| `0x7f13025c` | Show control panel | Player-Bedienfeld |
| `0x7f13025d` | Show groups | Sendergruppen |
| `0x7f13025e` / `0x7f13025f` | Show info panel / plus control panel | Programm- und Steuerinformationen |
| `0x7f130260` | Show menu | Kontext-/Navigationsmenü |
| `0x7f130261` | Show program description | EPG-Beschreibung |
| `0x7f130262`–`0x7f130265` | Show TV guide groups / TV guide in overlay / preview mode | EPG-Raster inklusive Gruppen und Vorschau |
| `0x7f130251` | Restart current program | Catch-up-Neustart, nur sofern verfügbar |
| `0x7f130252` / `0x7f130253` | Return to current programs / player | EPG-Zeitposition zurücksetzen / Player zurück |
| `0x7f13024e` / `0x7f130266` | Play/pause / Stop playback | Wiedergabesteuerung |
| `0x7f130245` | Change Favorite status | Favoriten-Toggle |
| `0x7f130267`–`0x7f130269` | Volume down / mute / up | Kodi-Lautstärke, ohne globale Keymaps zu überschreiben |

Weitere optionale UI-Einstellungen:
`Overlay mode` (0x7f130335), `Preview mode` (0x7f13035a),
`Stay on list when switching channels` (0x7f1303c8),
`Stay on TV guide when switching channels` (0x7f1303c9),
`Panels timeout` (0x7f130336), `Transparency` (0x7f1303d5),
`Recent channels` (0x7f13035d), `Delay before adding to recent channels` (0x7f13035e),
`Turn on last channel on app start` (0x7f1303db),
`Selection color` (0x7f130398), `Accent color` (0x7f130243).

## 4. Nachgewiesene Navigationsbereiche

Die APK-Ressourcen und Android-Manifest-Aktivitäten belegen:
- Live-TV, Sendergruppen, Senderliste und EPG mit Overlay/Vorschau, Zeitnavigation und Kanalwechsel.
- Player-Menü mit Wiedergabesteuerung, Audio, Aufnahme/Recordings, Catch-up, Favoriten und Programmtexten.
- Navigationsmenü, Verlauf/zuletzt gesehene Sender, Suche und deren Verlauf, EPG-Quellen, Playlists/Portale und Einstellungen.
- VOD-Bereiche **Movies**, **Shows**, **Season**, **My list**, **Trailer**.
- Serien: **Autoplay next episode** (`0x7f130474`), **Play from beginning** (`0x7f130482`), **Resume** (`0x7f130483`) — UI-Funktionen nachgewiesen, nicht intern implementiertes Fortschrittsmodell.
- Erscheinungsbild: Akzent-/Auswahlfarbe, Senderlogos, Panel-Transparenz, Panel-Timeout, Info-/Guide-Sichtbarkeit.
- Datensicherung/Restore, Sender- und Gruppenverschiebung, Fernbedienungseinstellungen.

`MainActivity`, Playlist-/EPG-Konfigurationsaktivitäten und weitere Android-Komponenten sind im Manifest benannt. Daraus ergibt sich **keine** vollständige klickbare Bildschirmhierarchie oder das genaue werkseitige Mapping.

## 5. Vorschlag für ein eigenständiges XCMate-Navigationsmodell

Nach der Android-P0-Stabilisierung ein zentrales Kodi-Overlay als Zustandsautomat:

`FULLSCREEN` ↔ `CHANNELS_OVERLAY` ↔ `GROUPS_OVERLAY`;
`FULLSCREEN` ↔ `PLAYER_CONTROLS` ↔ `PLAYER_EXTRAS`;
`FULLSCREEN` ↔ `GUIDE_OVERLAY` ↔ `GUIDE_GROUPS`;
optional `CHANNELS_PREVIEW`, `GUIDE_PREVIEW`, `PROGRAM_INFO`, `HISTORY`, `VOD`, `SERIES`.

Trennung:
1. **Rohes Eingabeereignis** `Kodi Action ID` + sofern lieferbar Android-Buttoncode.
2. **Belegung je Kontext** (`fullscreen`, `channels`, `groups`, `guide`, `player_controls`, `vod`) mit Kurz-/Langdruck und Konfliktprüfung.
3. **Semantischer Befehl** (`open_channels`, `open_guide`, `zap_next`, `show_extras` etc.).
4. **Zustandsübergang** und GUI-Fokus/Playback.
5. **Persistente Konfiguration** ausschließlich im unveränderten XCMate-Kodi-Profil.

Kontextbedienung darf sich je Bildschirm unterscheiden. Lange Tastendrücke nur aktivieren, wenn die konkrete Android-Kodi-Version sie tatsächlich liefert; Kodi-eigene Bedienung fremder Add-ons darf nicht verändert werden. TiviMate-Design, geschützter Code, Artworks und APK werden **nicht** in XCMate eingebaut.

## 6. Offener Abgleich für eine 1:1 vergleichbare Benutzerführung

**Unbestätigt:** Standardbelegung der einzelnen Tasten im Fullscreen-TV, Senderliste, EPG, VOD und Player; Fokusreihenfolge und Schließ-/Zurück-Pfade; tatsächliche Double-/Long-Press-Zeiten; Unterschiede zwischen 5.3.3 und anderer Versionen.

Am Testgerät TiviMate `Einstellungen → Fernbedienung` (Player, TV-Guide, Senderliste sofern separat verfügbar) aufrufen und die voreingestellten Belegungen dokumentieren; anschließend bei Live-TV mit den Tasten und langen Tastendrücken die tatsächlich sichtbaren Bildschirmzustände abgleichen. Die Android-Tastenwerte per Kodi-Diagnose **in XCMate** messen. Keine privaten Portal-/Stream-URLs in Screenshots und Logs veröffentlichen.

**Release-Grenze:** Dies ist eine APK-Ressourcenanalyse, kein Kodi-Implementierungs- oder Android-Gerätetest. XCMate 0.1.10 und die offenen P0-Tests bleiben davon unberührt.
