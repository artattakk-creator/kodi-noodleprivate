# XtreamMate 0.1.2 – Kodi test version

This is an independent Kodi add-on based on mr-evil1 TiViMate Kodi 2026.06.12.1 (GPL v2), with an original GS Media visual identity and new add-on ID `plugin.video.xtreammate`.

## Installation
In Kodi choose Add-ons -> Install from ZIP file -> `plugin.video.xtreammate-0.1.2.zip`. This version is published by the GS Media repository. Keep the original TiViMate Kodi installed while evaluating XtreamMate.

## First launch
Select Stalker Portal, local M3U file, M3U link, or Xtream Codes. For Xtream enter full server URL (including port), username and password. Choose which of TV, movies, series to import. Start the scan; review counts, name the list, save; optionally fetch EPG. On Xtream live accounts you can also choose multiple category IDs and change them later under Sendergruppen auswählen.

## Data handling
Xtream and Stalker credentials are stored in plaintext in Kodi's add-on-data folder, matching the original add-on's design. They are transmitted to the user-configured IPTV service, not to GS Media. Protect Kodi backups and user data accordingly. For privacy, logs attempt to avoid exposing URL or credentials. Network URLs may use HTTP because some providers do not offer HTTPS; prefer HTTPS wherever possible.

## Metadata
Xtream live, VOD, series list responses are cached by the original client's cache mechanism. EPG is fetched at the end when chosen, if the provider exposes XMLTV data. Posters are loaded on demand and stored by Kodi; this test build does not predownload every picture or query every movie's extended description. Counts depend on what the server reports and cannot guarantee stream availability.

## Limitations
This is an offline-code-tested alpha and still needs an on-device Kodi integration test. An on-video remote overlay is included for Xtream live streams opened from their portal channel lists: Back/Left opens channels, a second Back/Left opens category groups, Up/Down navigates, OK tunes/opens, Context Menu toggles a category. The overlay is automatically started by the service; Kodi skin/remote mappings vary and require an on-device test. Channels launched from global Favorites may not include portal/session metadata and therefore may not trigger this overlay. Stream legality and service access remain with the user and IPTV provider. No provider credentials are included.

## 0.1.1: Portal-Persistenz, Navigation und Kategorien

- Der Einrichtungsassistent meldet erst dann Erfolg, wenn die Zugangsdaten im lokalen `portals.json` atomar gespeichert und erneut gelesen wurden. Schreibfehler werden ausdrücklich angezeigt, statt scheinbaren Erfolg zu melden; vorhandene Portaldateien werden bei Lesefehlern nicht überschrieben.
- Nach erfolgreichem Einrichten öffnet sich die Startseite des neu gespeicherten Portals (inklusive Live-TV-Auswahl); beim nächsten Start wird das bestehende Portal erkannt. Ein automatischer Senderstart findet nicht statt, um unerwartete Wiedergabe zu vermeiden.
- Unter Portal-Startseite → **Gruppen verwalten: Live-TV, Filme und Serien** bzw. Add-on-Einstellungen → **Gruppen verwalten**: Jede Xtream-Kategorie mit OK aktivieren/deaktivieren, alle aktivieren, alle deaktivieren, neue aktivieren; optional werden neue Anbieter-Kategorien künftig automatisch aktiviert. Erst **Auswahl speichern** schreibt Änderungen, **Abbrechen** verwirft sie.
- Sender-, Film- und Seriengruppenauswahl wird getrennt pro Portal und anhand der Kategorie-ID gespeichert. Die alte Live-TV-Auswahl aus v0.1.0 bleibt kompatibel, deaktivierte Gruppen werden bei Aktualisierungen nicht ungefragt reaktiviert.
- Der Portal-Cache kann weiter über die vorhandene Aktualisierungsfunktion neu geladen werden; die Gruppenverwaltung liest die Gruppenkataloge beim Öffnen frisch ein.
- Alle Zugangsdaten bleiben ausschließlich in Kodi. Die portable Testversion wurde per Python/Stub-Tests verifiziert; Fernbedienung und Netzwerk müssen weiterhin auf dem Kodi-Gerät getestet werden.

## 0.1.2: TV-Fernbedienung und Startsender (Gerätetest ausstehend)

- XtreamMate-Einstellungen → „TV-Fernbedienung aktivieren“: optional eine eigene
  FullscreenVideo-Keymap anlegen. Ein eventuell vorhandenes fremdes
  `xtreammate.xml` wird niemals überschrieben; die Keymap ist reversibel.
- Während XtreamMate Live-TV läuft: **Hoch/Runter** schaltet einen Sender
  rückwärts/vorwärts innerhalb der aktiven Xtream-Gruppe; zyklische Navigation
  am Gruppenende. Deaktivierte Gruppen werden nicht durchgezappt.
- **Links** blendet Senderliste ein; erneut **Links** wählt die Gruppe.
- **OK** öffnet Player-Leiste, nochmal OK Zusatzfunktionen, langes OK (falls
  von der Fernbedienung unterstützt) springt zu Zusatzfunktionen.
- Start-Sendergruppe und Startsender lassen sich über das Portal-Menü wählen.
  Optional kann der Startsender beim Öffnen des Add-ons abgespielt werden.
- EPG-Autoaktualisierung läuft in einem separaten Thread, damit sie die
  Fernbedienung während des Streams nicht blockiert.
- **Achtung:** Kodi-Geräte und Skins unterscheiden sich bei Taste/OSD/Overlay.
  Die Kodi-Praxisprüfung insbesondere mit Titan BINGIE MOD steht aus.

XtreamMate speichert Xtream-Codes-Passwörter weiterhin lokal unverschlüsselt;
Kodi-Profile/Backups sicher aufbewahren. Keine Streams/Zugangsdaten in Logs veröffentlichen.
