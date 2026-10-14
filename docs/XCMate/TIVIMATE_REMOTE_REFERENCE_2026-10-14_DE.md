# XCMate – verbindliche Fernbedienungsreferenz aus TiviMate 5.3.3

**Stand:** 14.10.2026 · **Referenz:** 10 vom Nutzer fotografierte Ansichten der TiviMate-Android-Einstellungen „Fernbedienung“. Diese Ansichten sind **eine tatsächliche gezeigte Konfiguration**, nicht zwingend die Werksbelegung. Die Originalfotos sind im Chat, **nicht** im öffentlichen Repository (Sender-/TV-Bilder und Rechte Dritter). Vollständig transkribiert sind die sichtbaren Abschnitte „Player“, „EPG“ und „Suchoptionen“. Weiterer Einstellungsseiten folgen.

**Verbindliches Entwicklungsziel:** Bedienungssemantik, Tastendrücke, Kontextwechsel und einstellbare Optionen funktional nachbilden; keine TiviMate-Grafiken, Logos oder proprietären Programmteile kopieren. Android/Kodi kann sich bei Raw-Keyevents, langem Tastendruck, Timeshift/Recording und Video-Preview unterscheiden. Abweichungen transparent machen.

## Player: vom Nutzer fotografierte Zuordnung

| Auslöser in TiviMate | Hinterlegte Aktion laut Foto | XCMate-Aktionsschlüssel |
| --- | --- | --- |
| Okay | Infofenster und Bedienfeld anzeigen | `show_info_controls` |
| Lang OK | Zeige Menü | `show_menu` |
| Zurück | Gehe zurück | `back` |
| Lang Zurück | Wiedergabe stoppen | `stop` |
| Links | Senderliste im Overlay-Modus anzeigen | `channels_overlay` |
| Lang Links | Senderliste im Vorschaumodus anzeigen | `channels_preview` |
| Rechts | Den zuletzt angesehenen Sender anzeigen | `recent_channel` |
| Lang Rechts | Zeige Programmbeschreibung | `program_description` |
| Hoch | Nächsten Sender anzeigen | `channel_next` |
| Lang Hoch | Verlauf | `history` |
| Runter | Vorherigen Sender anzeigen | `channel_previous` |
| Lang Runter | Suchen | `search` |
| Pg+ (Ch+) | Infofenster für nächsten Sender anzeigen | `preview_next_channel` |
| Pg- (Ch-) | Infofenster für vorherigen Sender anzeigen | `preview_previous_channel` |
| Lautstärke erhöhen | Lauter | `volume_up` |
| Lautstärke senken | Leiser | `volume_down` |
| Stumm | Lautstärke stumm schalten | `mute` |
| Menü | Zeige Menü | `show_menu` |
| Lang Menü | EPG im Overlay-Modus anzeigen | `guide_overlay` |
| Play / Pause | Play/Pause | `play_pause` |
| Lang Play/Pause | Gehe zum Live Stream | `return_live` |
| Stopp | Wiedergabe stoppen | `stop` |
| Zurückspulen (RW) | Infofenster für vorherigen Sender anzeigen | `preview_previous_channel` |
| Vorspulen (FF) | Infofenster für nächsten Sender anzeigen | `preview_next_channel` |
| Aufnahme | Start/Stopp Aufnahme | `toggle_recording` |
| Rücktaste | EPG im Overlay-Modus anzeigen | `guide_overlay` |
| Info | Infofenster anzeigen | `show_info` |
| Guide | EPG im Overlay-Modus anzeigen | `guide_overlay` |

**Wichtig:** „Nächsten/vorherigen Sender anzeigen“ und „Infofenster für nächsten/vorherigen Sender anzeigen“ sind laut TiviMate **verschiedene** Aktionen. Ohne Gerätevergleich nicht pauschal beides als sofortiges Umschalten behandeln. „Zurück“ und „Rücktaste“ sind als separate in der UI benannte Auslöser erhalten; die Android-/Kodi-Scancodes muss die Geräte-Diagnose klären.

## EPG: vom Nutzer fotografierte Zuordnung

| Auslöser in TiviMate | Hinterlegte Aktion laut Foto | XCMate-Aktionsschlüssel |
| --- | --- | --- |
| Okay | Sender ansehen | `watch_channel` |
| Lang OK | Zeige Menü | `show_menu` |
| Zurück | Gehe zurück | `back` |
| Lang Zurück | Zurück zum Player | `return_player` |
| Links | Zeige Gruppen | `show_groups` |
| Rechts | Zum nächsten Programm scrollen | `scroll_next_program` |
| Pg+ (Ch+) | Sender nach oben scrollen | `page_up_channels` |
| Pg- (Ch-) | Sender nach unten scrollen | `page_down_channels` |
| Menü | Zeige Menü | `show_menu` |
| Lang Menü | Suchen | `search` |
| Play / Pause | Zeige Programmbeschreibung | `program_description` |
| Lang Play/Pause | Extern öffnen | `open_external` |
| Stopp | Favoritenstatus ändern | `toggle_favourite` |
| Zurückspulen (RW) | Sender nach oben scrollen | `page_up_channels` |
| Vorspulen (FF) | Sender nach unten scrollen | `page_down_channels` |
| Aufnahme | Aufnahmen | `recordings` |
| Rücktaste | Zurück zum Player | `return_player` |
| Info | Zeige Programmbeschreibung | `program_description` |
| Guide | Zeige Gruppen | `show_groups` |
| Rot | Favoritenstatus ändern | `toggle_favourite` |
| Grün | Kanaloptionen | `channel_options` |
| Gelb | Gruppenoptionen | `group_options` |
| Blau | Einstellungen | `settings` |

`Hoch/Runter` und `Lang Links/Rechts` sind auf den EPG-Bildern nicht als eigene Zeilen vollständig zu erkennen. **Nicht raten.** Weitere Ansichten abwarten.

## Player – Suchoptionen, sichtbare Schalterzustände

| Option, sinngemäß nach Screenshot | Sichtbarer Zustand |
| --- | --- |
| RW / FF / Pause zum Suchen/Pausieren während des Anschauens | **Ein** (blau) |
| RW zum Zurückspulen des Live-Streams | Aus |
| Links / Rechts zum Suchen während des Suchens | Aus |
| Links zum Zurückspulen des Live-Streams | Aus (erscheint deaktiviert) |
| Down / Up zum Suchen während des Catch-up-Anschauens | Aus |
| Down zum Zurückspulen des Live-Streams mit Catch-up | Aus |

„Suchen“ bezeichnet in diesem Bereich **Spulen/Seek**, nicht unbedingt die Programmsuche. TiviMate-Schalter können vom Anbieter-/Timeshift-Modus abhängen. Werte als **fotografierte Zielkonfiguration**, nicht als universelle Standardeinstellungen führen. Bei nicht seekbaren Live-Streams keine Seek-Befehle ausführen.

## Implementierungs- und Abnahmeprinzipien

1. **Einzelne Kontexte:** Player und EPG haben ausdrücklich unterschiedliche Bindings (z. B. Stopp = Stop im Player, Favorit im EPG). Kein globales Einheitsmapping erzwingen.
2. **Kurz und Lang:** Pro Taste getrennte Bindings. Kodi-/Android-Events müssen wirklich zwischen den beiden unterscheiden, bevor Langdruck als „funktionierend“ bezeichnet werden darf.
3. **Unterscheidbare Ansichten:** Senderliste Overlay/Vorschau, Guide Overlay/Vorschau, Infofeld, Verlauf und Suche benötigen definierte eigene Zustände; nicht eine Info-Aktion stillschweigend durch Zappen ersetzen.
4. **Tasten lernen:** Ursprüngliche benutzerspezifische Belegung `xtreammate_remote_actions.json` unangetastet lassen; zukünftige Referenzbelegung in eigener Datei, atomisch und mit Fallback.
5. **P0 bleibt:** Der Startsender und die Kodi-Overlay-Fokus-/Tastenerkennung sind auf Android weiterhin offen. Kein „1:1 fertig“-Label, bevor sämtliche Kontexte und Gerätetests bestanden sind.
6. **Andere Kodi-Add-ons:** Fernbedienungsänderungen nie global wirksam; Kodi-Keymap nicht fremd überschreiben.
7. **Neue Fotos:** Fortlaufend Referenzmatrix ergänzen, Umsetzung per Tests/PR separiert freigeben.

## Relevante Bestandsarchitektur

`resources/lib/live_overlay.py` bietet bislang primär `hidden`, `channels`, `groups`, `controls`, `extras`. `_epg()` nutzt aktuell einen Kodi-Textviewer und **noch kein TiviMate-artiges, kontextsensitives EPG-Raster**. Ein umfangreicher EPG-/Preview-Controller ist daher **noch umzusetzen**. Statusangaben dürfen UI-Spezifikation und bereits funktionierende Kodi-Implementierung nicht vermischen.
