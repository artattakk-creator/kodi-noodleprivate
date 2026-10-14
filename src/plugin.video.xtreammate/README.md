# XCMate 0.1.11 – Android remote P0 test candidate

This is an independent Kodi add-on based on mr-evil1 TiViMate Kodi 2026.06.12.1 (GPL v2), with an original GS Media visual identity and new add-on ID `plugin.video.xtreammate`.

> **Projektübergabe (Stand 14.10.2026):** [Zentraler Einstieg](../../docs/XCMate/README.md) · [Technische Übergabe](../../docs/XCMate/PROJECT_HANDOFF_DE.md) · [Serien-Autoplay/Bookmarks – spezifiziert, noch nicht implementiert](../../docs/XCMate/SERIES_PROGRESS_SPEC_DE.md) · [Designsystem](../../docs/XCMate/DESIGN_SYSTEM_DE.md).

## Installation
Install XCMate preferably via Kodi → Install from repository → GS Media Kodi Repository → XCMate. Current candidate ZIP: `plugin.video.xtreammate-0.1.15.zip` (after release). Kodi ID `plugin.video.xtreammate` remains unchanged to preserve updates and the existing userdata profile. The original upstream TiViMate addon can stay installed separately.

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

## 0.1.3: TV-Fernbedienung und Startsender (Gerätetest ausstehend)

- XCMate-Einstellungen → „TV-Fernbedienung aktivieren“: optional eine eigene
  FullscreenVideo-Keymap anlegen. Ein eventuell vorhandenes fremdes
  `xtreammate.xml` wird niemals überschrieben; die Keymap ist reversibel.
- Während XCMate Live-TV läuft: **Hoch/Runter** schaltet einen Sender
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

XCMate speichert Xtream-Codes-Passwörter weiterhin lokal unverschlüsselt;
Kodi-Profile/Backups sicher aufbewahren. Keine Streams/Zugangsdaten in Logs veröffentlichen.

 
## 0.1.3 – Cache-first catalog loading

The IPTV overlay always opens from the local catalog index, without network
roundtrips from the remote-control thread. On Kodi start, a background worker
warms Live/Movies/Series indexes as selected for each portal and refreshes them
when expired. Existing cached indexes remain readable up to 30 days if the
server is temporarily unresponsive; manually selecting refresh still forces a
network request. A loading row is displayed on first use when no local list
exists. Xtream cache keys include the provider URL to avoid collisions across
servers with identical credentials. The overlay holds its active channel group
in memory for immediate repeated Back/Left navigation. Stream links are not
downloaded as video files; artwork remains managed by Kodi's image cache.

## 0.1.4: checkbox group editor and recordings folder browser

Choose individual Live-TV, film or series categories using Kodi's native
checkbox multiselect; the list stays open and preserves position as you
toggle. Press OK to save, Back to discard. Separate bulk actions permit
All On, All Off, enable newly discovered groups, and automatic new groups.
In Kodi settings, Recordings Folder now opens the native file manager
folder picker; the confirmed path is saved/displayed automatically.
FFmpeg requires a writable local or mounted folder, not necessarily a
Kodi SMB URL.


## 0.1.5 – Player repair, newer titles, TV guide and BINGIE widgets

- Fixed Kodi on-video control creation and nonblocking on-video EPG.
- The Live-TV channel listing and overlay display cached 'Jetzt' and 'Danach'.
- Added 'Neueste Filme' and 'Neueste Serien' based on provider's added dates
  or locally observed genuinely new IDs (first scan sets baseline only).
- VOD and series posters show provider-supplied descriptions via Kodi metadata;
  use context menu 'Beschreibung und Details' for on-demand extended metadata.
- Valid provider YouTube trailer IDs offer the YouTube Kodi add-on link.
- Portal home -> BINGIE MOD Widgets -> choose an enabled channel category;
  in your BINGIE MOD skin settings use that category's folder as a widget.
  Widgets carry logos, possible EPG still images and now/next in ListItem.Plot.
  Skin hover appearance depends on BINGIE MOD widget layout; no live preview.
- Existing IPTV portal/userdata/settings are not reset or overwritten.

Kodi's on-device keymap needs enabling and restart; remote/skin behaviour
must be tested on the actual Kodi box.

## 0.1.6 – Faster remote controls, playable start channel, guide fallback
- Startsender abspielen is marked IsPlayable instead of a folder, and resolves
  using the saved Xtream stream ID without another network catalog request.
- Portal home uses saved account metadata without synchronous provider requests.
- Fullscreen ControlList uses setItemHeight()/setSpace() for Kodi portability.
- TV remote diagnostics shows the latest bridge input and last processed input.
- Live TV listing shows XMLTV Now/Next or cached Xtream short EPG if available.
  Missing short EPG entries are preloaded asynchronously for up to 24 visible
  channels per page (maximum 3 concurrent requests). No synchronous wait.
- Kodi profile, portal credentials and selected start channel are retained.

## 0.1.7 – XMLTV EPG source management (Android/Kodi)
- New EPG-Verwaltung from the portal home page and from Kodi add-on EPG settings.
- Add and name multiple HTTP(S) XMLTV feeds or pick a local XML/XML.GZ
  file with Kodi's native file browser (including permitted NAS shares).
- Enable/disable, remove, and reorder external feeds. Later enabled sources
  take precedence when the same XMLTV channel ID appears more than once.
- Built-in Xtream XMLTV remains the fallback. A failing custom feed does not
  delete the working provider guide.
- Map Xtream stream IDs to XMLTV channel IDs manually. Saved assignments
  survive updates and the same cached EPG becomes available in Live-TV and
  skin widgets. Fetch/update happens in a background thread.
- Kodi file permissions and Android storage access are device dependent.
  Use local files or accessible Kodi network shares where possible.
- URLs and paths may contain private access tokens and remain in the local
  add-on profile. Avoid sharing this profile or its backups publicly.
- The 0.1.6 playback and remote-control fixes are retained. Custom Android
  remote-key capture/configuration requires a separate on-device test.

 
## 0.1.8 – Startsender and Android native TV control
- Startsender is started with xbmc.Player().play() rather than trying to
  resolve a plugin URL from a RunPlugin context. Autoplay invokes RunPlugin
  rather than PlayMedia(plugin://...), which Android Kodi can treat as a folder.
- While an XCMate live stream is active, the WindowDialog keeps a tiny
  focusable control even if its TV sidebar is hidden. Kodi Android remote
  keys are received via native WindowDialog.onAction, independently of the
  FullscreenVideo keymap. Keymap remains an optional fallback.
- Kodi remote action IDs can be learned for channels, up/down zapping,
  playback OSD, EPG and extra settings; mappings are stored atomically
  under addon_data/plugin.video.xtreammate and can be reset to defaults.
- Playback/remote diagnostics include the direct-play attempt and the most
  recent native Kodi action. This is a device-tested-pending release:
  real remotes and BINGIE skin behavior still require Android validation.

## 0.1.9 – Rebranding zu XCMate
Die angezeigte Bezeichnung wurde von XtreamMate in **XCMate** geändert. Kodi-Add-on-ID `plugin.video.xtreammate`, ZIP-Namen, Benutzerprofil und Kodi-Fenstereigenschaften behalten absichtlich die bisherigen technischen Schlüssel, damit Updates vorhandene Konfigurationen und Daten nicht verlieren.

## 0.1.10 – Android P0 playback and OSD candidate (device verification pending)

- Separate the Kodi *playable* Startsender menu entry (setResolvedUrl) from
  autoplay launched through RunPlugin (direct xbmc.Player.play).
  This avoids leaving Kodi's playable plugin request unresolved.
- In the on-video TV control bar, OK now executes the focused command.
  A dedicated "Weitere" control opens audio/video/EPG/setting options.
- Channel changes pass the prepared ListItem path, including Kodi headers,
  to the player. Direct stream URLs are no longer emitted by debug().
- New mock-Kodi API tests and PR preflight builds verify the two paths.
- **NOT Android-verified:** Test on the actual Android box with Titan BINGIE
  MOD before marking startup, remote, EPG or overlay issues resolved.
- No portal/credentials/cache/EPG/userdata migration or deletion.

## 0.1.11 – native Android Fernbedienung (P0, Gerätetest erforderlich)

- **Erster XCMate-Live-TV-Start:** Der Kodi-Service installiert bzw. aktualisiert
  automatisch ausschließlich die selbst verwaltete `xtreammate.xml`-Keymap.
  Fremde Keymap-Dateien werden nicht überschrieben. Über
  „TV-Fernbedienung aktivieren/deaktivieren“ kann der Nutzer die Installation
  jederzeit widerrufen; die Abwahl wird persistent respektiert.
- **Nur im XCMate-Live-TV:** Links zeigt Senderliste, erneut Links Gruppen;
  Hoch nächster / Runter vorheriger Sender; Rechts letzter Sender;
  OK XCMate-Steuerleiste; Menü XCMate-Zusatzleiste; Zurück EPG/Zurück.
  Kodi-Lautstärkeregelung wird nicht ersetzt. Außerhalb aktiver XCMate-Sessions
  leitet die Keymap Tasten an Kodi zurück.
- Kodi-Dialog fängt Android-`onAction` direkt ab. Eine Namespaced-Keymap mit
  kurz-/lang-gedrückten Einträgen leitet alternativ Aktionen über
  `remote_bridge.py` weiter. Unterschiedliche Android-Fernbedienungen
  liefern ggf. keine separate Langdruck-Aktion.
- TV-Guide-Schnelleinstieg nutzt zunächst eine eigenständige fokussierbare
  Senderliste mit zwischengespeicherten EPG-Zeilen; der vollständige
  TiviMate-ähnliche horizontale EPG-Zeitraster bleibt ein separates P1-Ziel.
- Remote-Diagnose zeigt native Kodi-Action-IDs, Tastenereignis-Zähler,
  Keymap-Status und den Status der TV-Overlay-Initialisierung.
- Für den **ersten Test nach dem Update bitte Kodi vollständig neu starten**
  (nicht nur das Add-on erneut öffnen), damit der Kodi-Service aktualisiert ist.
- Regressionstests inkl. Kodi-/Android-API-Stubs sind **kein Nachweis eines
  erfolgreichen Gerätetests**. Der unveränderte interne Add-on-Bezeichner
  `plugin.video.xtreammate` und alle persönlichen Portal-, EPG- und
  Tastenprofil-Dateien bleiben erhalten.

### Android-Gerätetest (Titan BINGIE MOD)

1. Kodi neu starten, XCMate öffnen, XTREAM-Live-TV-Sender starten.
2. Bei laufendem Vollbild **OK** drücken: XCMate-Leiste statt Kodi-OSD?
3. **Links, Links, Rechts, Hoch, Runter, Rechts**:
   Senderliste, Gruppen, zurück, Senderwechsel in beide Richtungen und
   letzter Sender.
4. **Menü, Zurück, Guide/Zurück, OK, Pause** testen; EPG/Senderliste darf nicht
   zu einer leeren Kodi-Verzeichnisansicht wechseln.
5. Unter „TV-Fernbedienung: Diagnose“ Kodi-Tastenwerte, `NativeActionCount`,
   `KeymapStatus`, `OverlayStatus`, `LastHandledKey` ablesen;
   bei Fehlverhalten anonymisierte `kodi.log`-Zeilen sichern.
6. Fernbedienung bei **fremdem Kodi-Video** gegenprüfen: Kodi-Standardbefehle
   dürfen dort nicht vom XCMate-Player ersetzt werden.

**Kein Android-PASS** ohne protokolliertes tatsächliches Ergebnis.

## 0.1.13 – Hintergrunddienst-Prüfung ohne Video

Das Xtream-Portalmenü bietet nun **TV-Fernbedienung: Diagnose** und
**XCMate-Hintergrunddienst prüfen / manuell starten**. Eine neue Dienst-
Heartbeatmeldung (Status, Alter, Zähler, Fehlerklasse) wird auch bei
gestopptem TV angezeigt. Die letzte Live-/Overlay-Beobachtung bleibt nach
Ende des Streams abrufbar.

Ist kein frisches Lebenszeichen vorhanden, kann Kodi gebeten werden, die
bereits zum Add-on gehörende `service.py` über `RunScript` erneut zu
starten. Bereits aktive Dienste und kurz nacheinander wiederholte Versuche
werden abgefangen. Die Aktion verändert weder Portale, EPG noch die
Fernbedienungsprofile. Ein akzeptierter Startauftrag bedeutet **nicht**,
dass Kodi den Dienst tatsächlich ausführen konnte.

**Android-Test:** Kodi nach Update vollständig neu starten; XCMate-Menü →
Dienst prüfen (ohne Stream), Testsender starten, bei fehlender Steuerung
zurück ins Menü → Diagnose öffnen. Nur wenn der Dienststatus tatsächlich
„LÄUFT“ anzeigt, ist sein Hintergrundloop bestätigt. Die praktische
Fernbedienungsfunktion ist damit noch nicht nachgewiesen.

## 0.1.14 – laufenden XCMate-Live-TV-Stream nach Verlust des Session-Markers wiedererkennen

Auf einem realen Android-Screenshot zeigte die Dienstdiagnose:
`LÄUFT` mit über 2000 Heartbeats, `Video JA` aber `XCMate-Sitzung NEIN`.
Der laufende Kodi-Player konnte deshalb die XCMate-eigene Oberfläche nicht
aktivieren, obwohl die Taste-Keymap geladen war.

Der Kodi-Dienst prüft jetzt bei fehlender XCMate-LiveSession höchstens
alle 3 Sekunden `xbmc.Player().getPlayingFile()`, ohne die Adresse zu loggen,
zu persistieren oder zu zeigen. Nur eine **exakte Übereinstimmung**
mit einem aktiven, vom Benutzer konfigurierten Xtream-Live-Portal und dessen
bekannter Sender-ID stellt den XCMate-Session-Marker wieder her.
Erlaubt sind Xtream-`.ts`/`.m3u8`-Live-URLs sowie explizite
XCMate-`plugin://`-Live-Aktionen. Keine Netzwerkzugriffe oder
unsichere „ähnliche URL“-/Hostnamen-Heuristik. Externe Medien, Filme,
andere Plugins und unbekannte Sender werden nie übernommen.

**Wichtig:** Ein URL-Match beseitigt die fehlende Session, beweist aber noch
nicht, dass Kodi den eigenen `WindowDialog` über der Skin-Oberfläche zeigt.
Die Diagnose ergänzt `Live-Sitzungswiederherstellung` mit einem
nicht-sensiblen Ergebnis. Falls Kodi auf dieser Box keine passende
`getPlayingFile()`-Adresse liefert, bitte nach einem Test das Diagnosefenster
fotografieren; Zugangsdaten und Kodi-Log-Passwörter vorher verdecken.
Die Android-Geräteabnahme bleibt zwingend.

## 0.1.15 – eigener Kodi-Popup-Test und sichtbare TV-Senderliste

Die vorherige Fernbedienung erhielt auf einer Android-Box weiterhin
keine Events während Live-TV. Deshalb ist ein vollständig eigenständiger
**Kodi-Dialogtest aus dem Xtream-Portalmenü** hinzugekommen:

**XCMate Popup- und Fernbedienungstest**
- Funktioniert **ohne aktiven TV-Stream** und ohne Service-Marker.
- Ein eigener `WindowDialog.doModal()` wird in der Kodi-Addon-Anwendung
  gezeigt, mit Fokus auf einem OK-Testfeld und einer Schließen-Schaltfläche.
- Hoch/Runter/Links/Rechts verändern den Fokus, OK wird als Tastenevent
  angezeigt und Zurück schließt den Dialog.
- Der letzte Action-Code, Fokus und Empfangszähler bleiben im Kodi-Home-Window
  erhalten und sind anschließend unter **TV-Fernbedienung: Diagnose** abrufbar.

**Automatische Live-Einblendung:** Wenn Kodi eine gültige XCMate-Session
besitzt und den vorhandenen `LiveNavigator` öffnet, startet dieser nun
**sichtbar** mit der Sender-/EPG-Seitenleiste (bisher zunächst unsichtbar).
Nach 16 Sekunden ohne Taste wird nur die Sidebar verborgen, während der
Stream weiterläuft. Jede empfangene Taste bricht das automatische Ausblenden
ab. Die freie Bildschirmfläche zeigt das laufende Hauptvideo, kein
versprochenes separat skaliertes Mini-Video.

Nach Aktualisierung Kodi vollständig neu starten. **Zuerst ohne Video**
den neuen Popup-Test aufrufen, Tasten drücken, Zurück, dann Diagnose.
Erst anschließend Testsender starten und prüfen, ob die Senderleiste
automatisch über dem Livevideo erscheint. Wenn nicht, die gespeicherten
Diagnosewerte auswerten. Diese Version ist nicht durch Android-Hardware
bestätigt; Github-Mocktests können den tatsächlichen Dialogfokus nicht
garantieren.

**Roadmap:** `docs/XCMate/POPUP_UI_IMPLEMENTATION_PLAN_DE.md`.

