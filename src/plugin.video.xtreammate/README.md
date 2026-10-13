# XtreamMate 0.1.0 – Kodi test version

This is an independent Kodi add-on based on mr-evil1 TiViMate Kodi 2026.06.12.1 (GPL v2), with an original GS Media visual identity and new add-on ID `plugin.video.xtreammate`.

## Installation
In Kodi choose Add-ons -> Install from ZIP file -> `plugin.video.xtreammate-0.1.0.zip`. This version is published by the GS Media repository. Keep the original TiViMate Kodi installed while evaluating XtreamMate.

## First launch
Select Stalker Portal, local M3U file, M3U link, or Xtream Codes. For Xtream enter full server URL (including port), username and password. Choose which of TV, movies, series to import. Start the scan; review counts, name the list, save; optionally fetch EPG. On Xtream live accounts you can also choose multiple category IDs and change them later under Sendergruppen auswählen.

## Data handling
Xtream and Stalker credentials are stored in plaintext in Kodi's add-on-data folder, matching the original add-on's design. They are transmitted to the user-configured IPTV service, not to GS Media. Protect Kodi backups and user data accordingly. For privacy, logs attempt to avoid exposing URL or credentials. Network URLs may use HTTP because some providers do not offer HTTPS; prefer HTTPS wherever possible.

## Metadata
Xtream live, VOD, series list responses are cached by the original client's cache mechanism. EPG is fetched at the end when chosen, if the provider exposes XMLTV data. Posters are loaded on demand and stored by Kodi; this test build does not predownload every picture or query every movie's extended description. Counts depend on what the server reports and cannot guarantee stream availability.

## Limitations
This is an offline-code-tested alpha and still needs an on-device Kodi integration test. An on-video remote overlay is included for Xtream live streams opened from their portal channel lists: Back/Left opens channels, a second Back/Left opens category groups, Up/Down navigates, OK tunes/opens, Context Menu toggles a category. The overlay is automatically started by the service; Kodi skin/remote mappings vary and require an on-device test. Channels launched from global Favorites may not include portal/session metadata and therefore may not trigger this overlay. Stream legality and service access remain with the user and IPTV provider. No provider credentials are included.
