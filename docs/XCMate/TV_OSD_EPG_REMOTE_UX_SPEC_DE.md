# XCMate – verbindliche Live-TV-Bedienung, EPG-Infobar und performante Senderliste

**Festgelegt durch Nutzer:** 18.10.2026, nach erfolgreichem erstmaligem Öffnen der TV-Overlay-Senderliste in XCMate 0.1.24.  
**Status:** FUNKTIONALE ANFORDERUNG / CODEX-AUFTRAG, **noch nicht implementiert oder am Gerät abgenommen**.  
**Technischer Kodi-Addonname:** `plugin.video.xtreammate` (unverändert); geplanter separater Skin heißt **XCMate Skin**.  
**Visuelle Orientierung:** Bedienablauf wie TiviMate, aber eigenständige XCMate-Optik / Icons / Assets und kein Kopieren proprietärer Medien.

## 1. Nutzerwunsch: TV-Bild → Infobar → unteres Bedienmenü

Das Overlay soll **nicht** sofort mit einer Liste von Pause/Stop/Funktionen starten. Die erste OK-Taste im laufenden Vollbildfernsehen zeigt eine kompakte **Infoleiste** mit Kanal und Sendeinformationen. Weitere Eingabe öffnet die vollständige Bedienleiste.

### Zustandsmodell und Remote-Steuerung

| Aktueller Zustand | Taste | Gewünschtes Ergebnis |
|---|---|---|
| `LIVE_FULL` (normales Vollbild, OSD verborgen) | **OK (einmal)** | **`INFO_BAR`**: Kanalicon, Kanalname, Jetzt/Danach, Zeitspanne, Fortschritt und Restlaufzeit. Video bleibt sichtbar. |
| `INFO_BAR` | **OK erneut** | **`PLAYER_CONTROLS`**: erweiterte Bedienleiste, initiale fokussierte Aktion deutlich markiert. Kein versehentliches Starten einer Aktion auf dem zweiten OK. |
| `INFO_BAR` | **Runter** | Ebenfalls `PLAYER_CONTROLS`. |
| `LIVE_FULL` | **Links** | **`CHANNEL_LIST`**: schnell und mit lokaler EPG-Vorschau öffnen. |
| `INFO_BAR` | **Links** | `CHANNEL_LIST`, ohne vorherige Internetabfrage. |
| `CHANNEL_LIST` | Hoch/Runter | **Eine Zeile** verschieben; sichtbare Auswahlmarkierung, keine doppelte Bewegung aus `onAction` / `onControl`. |
| `CHANNEL_LIST` | OK auf Sender | Ausgewählten Sender abspielen; Sender-ID und Stream-Ziel korrekt, kein Seitenlink als Sender behandeln. |
| `CHANNEL_LIST` | Links | Kategorien-/Sendergruppenansicht wie bisher, **nicht** sofort andere Add-ons beeinflussen. |
| `PLAYER_CONTROLS` | Navigation + OK | Fokussierte Player-Aktion einmalig ausführen; separate Ebene „Weitere“ mit Ton, Bild, Untertiteln, EPG, Einstellungen. |
| `INFO_BAR` | Zurück | Nur Infoleiste schließen, TV weiterspielen. |
| `PLAYER_CONTROLS` / `MORE_SETTINGS` | Zurück | Eine UI-Ebene zurück, nicht ungewollt Wiedergabe stoppen. |
| `CHANNEL_LIST` / `GROUPS` | Zurück | Logisch eine Ebene zurück bis Vollbild-TV. |
| `LIVE_FULL` | Hoch/Runter | **Bereits vereinbarter Senderwechsel** beibehalten, soweit separat von der Infoleistensteuerung; Runter **in INFO_BAR** soll dagegen erweiterte Bedienleiste öffnen. Verhalten beider Zustände gezielt testen. |
| `INFO_BAR` | Zeitablauf | Nach konfigurierbarer kurzer Inaktivität automatisch ausblenden; Status/Fokus/Remote-Zähler bleiben konsistent. |
| `LIVE_FULL` / fremde Add-ons | Stop | Kodi-Wiedergabe regulär beenden und Eingaben/Fokus sauber freigeben. |

**Wichtig:** Native Kodi-`WindowDialog`-Aktivierung und `onControl`/ `onAction`-Kollisionen sind seit Version 0.1.24 der kritische Bereich. Der zweite OK-Klick muss **nur** die Menüebene öffnen und darf nicht auf einer hinterlegten Schaltfläche eine zufällige Aktion auslösen. Globales Kodi-Keymap-Fallback bleibt standardmäßig **deaktiviert**.

## 2. INFO_BAR – Mindestinhalt beim ersten OK

Auf dem unverdeckten TV-Bild erscheint unten eine **kompakte, hochwertige, semitransparente Leiste**, nicht die komplette Senderliste.

- **Senderlogo/Channel-Icon** (vorhandenes `channel.logo`; bei Fehlen neutrales XCMate-Platzhaltericon), **Sendername**.
- **JETZT**: echter aktueller EPG-Sendungstitel.
- **Zeitfenster JETZT**: lokale Beginn-/Endzeit, z. B. `20:15–21:45 Uhr`.
- **Fortschrittsbalken** mit Prozentwert auf Basis des gültigen tatsächlichen EPG-Zeitfensters. Optional daneben `seit 59 Min.` und `noch 31 Min.`.
- **DANACH**: Titel der nächsten Sendung, bevorzugt mit Beginn, optional Beginn–Ende.
- Wenn EPG fehlt: explizit `Keine EPG-Daten für diesen Sender`, **keine erfundenen Titel, Zeiten oder Fortschrittswerte**. Logo und Sendername trotzdem sofort anzeigen.
- Zeitformat: lokale Zeitzone des Kodi-Geräts, Mitternachtsübergänge korrekt. Aktualisierung bei Sendungswechsel und gelegentlich während offener Leiste, nicht per Netzwerk-Tick bei jeder Sekunde.

Berechnung nur bei `start <= now < stop` und `stop > start`:  
`progress = clamp((now - start) / (stop - start), 0, 1)`; `elapsed = now - start`, `remaining = stop - now`. Ungültige Zeiten -> neutrales „keine Programminfo“ ohne Balken. Bei Now/Next und manueller Zuordnung muss dieselbe normalisierte Datenquelle gelten.

## 3. PLAYER_CONTROLS / MORE_SETTINGS – zweites OK oder Runter

- `PLAYER_CONTROLS` zeigt die untere fokussierbare Leiste mit Bedienung (Play/Pause, Stop, ggf. Timeshift/Seek nur wenn unterstützt, **Weitere**). Ein Druck auf das zweite OK beim `INFO_BAR` ist ein **Übergang**, kein implizites Auslösen des ersten Buttons.
- `MORE_SETTINGS` über `Weitere` enthält mindestens: **Ton/Audioauswahl**, **Bild/Videoeinstellungen**, **Untertitel**, **EPG**, **Einstellungen** sowie Zugang zu **Sendergruppen**. Kodi-Standardfunktionen wiederverwenden, statt eigenständigen Video-/Audio-Decoder anzufassen.
- Sichtbare Fokusmarkierung und klare Links/Rechts/Hoch/Runter-Logik. Die erweiterte Leiste darf Video nicht unnötig abdecken; Safe-Area/Schriftgröße für Android-TV beachten.
- Vorhandene Controls mit nicht unterstützten Kodi-Unicode-Icons zeigen teils leere Quadrate: Bild-Icons oder tatsächlich verfügbare Fontglyphen statt defekter Symbolzeichen.
- Eigenständiges XCMate-Design: dunkles edles Grau/Slate mit dezenten Space-Akzenten und optional später einstellbaren Farben. `docs/XCMate/DESIGN_SYSTEM_DE.md` beachten. Dies ist **bereits in XCMate-Addon umsetzbar**; `XCMate Skin` ist ein späterer unabhängiger PoC.

## 4. CHANNEL_LIST – Links: schneller Aufruf mit Jetzt/Danach

Die bereits sichtbar funktionierende linke Senderliste soll beim **ersten Links** ohne spürbares Hängen aufgehen. Pro **tatsächlich sichtbarer Senderzeile**:

- Sendericon (oder definierter Fallback), Sendername.
- **Jetzt: aktueller Sendungstitel** (ggf. auf zwei Zeilen / responsives Layout).
- **Von–bis**: Beginn/Ende der aktuellen Sendung in Gerätezeit.
- Optional / erwünscht: kleiner Fortschrittsbalken pro Sender und `Danach: …`. Mindestens für selektierte Zeile den nächsten Titel deutlich darstellen.
- Ausgewählter Sender und aktuell laufender Sender müssen klar unterscheidbar sein (Fokus vs. spielt gerade).
- EPG-Missing-State auf den betroffenen Sender begrenzen. Andere Sender nicht mit leeren Daten blockieren.
- Paging von Version 0.1.24 (`CHANNEL_PAGE_SIZE=100`) darf beibehalten werden; die Gestaltung soll deutlich weniger Zeilen gleichzeitig auf die TV-Fläche quetschen. Fokusposition/Seitenwechsel dürfen nicht springen.
- Bestehender Kategorienmodus und Favoriten-/Gruppenfilter sollen erhalten bleiben.

## 5. EPG-Datenabhängigkeiten (separat von bloßem Design)

**Ohne echte EPG-Daten sind Fortschritt, Von–bis und Jetzt/Danach nicht darstellbar.** Daher die Arbeit aus [Issue #13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13) vorrangig abschließen:

1. Einheitliches normalisiertes Modell für Xtream Provider XMLTV, externe XMLTV-Feeds, kurze Xtream-`get_short_epg`-Ergebnisse und manuelle `stream_id → XMLTV id`-Overrides. Anbieterinformationen und manuelle Zuordnung vorrangig korrekt verwenden, Quellenprioritäten nicht stillschweigend ändern.
2. **Aktuelle Inkonsistenz in `main` (0.1.24):** `main._live_channels()` nutzt bei fehlendem Guide einen lokalen `cached_short_guide`-Fallback. `live_overlay._render()` benutzt für `channels` und `guide` ausschließlich `guide_for_channel(load_cache(...))` und sieht deshalb nicht dieselben gecachten Kurz-EPG-Daten. Beide Views müssen dieselbe **lokale, nicht-blockierende** Guide-Funktion mit identischen manuellen IDs verwenden.
3. `live_overlay._epg()` zeigt nur Kurz-EPG des aktiven Senders oder triggert Hintergrund-Nachladen; aktuelle `guide`-Seite ist primär eine andere Beschriftung für die Senderliste. **EPG-Aktion** künftig auf eine funktionale, benutzbare Ansicht führen (mindestens Heute/Jetzt/Danach und folgende Sendungen; detaillierte Timeline später). Kein Button, der still ins Leere läuft.
4. Ein eigenständiger **EPG-Status & Vorschau** im XCMate-Menü: Quelle, letzter erfolgreicher Import, `PROVIDER_LIMIT`/GZIP/XML-/HTTP-Fehler und gesetztes Limit, Sender-/Programmanzahl und verifizierbarer Eintrag mit Titel/Zeiten. Nicht `Download gestartet` mit `EPG erfolgreich` verwechseln.
5. Historische echte Android-Diagnose aus 0.1.23: `PROVIDER_LIMIT → NO_NEW_GUIDE`, `DOWNLOAD_FAILED` bei externer Quelle. 0.1.24 hat nur präzisere Klassifizierung; **neuer 0.1.24-Quellenstatus ist noch nicht ausgelesen**. Quellfehler zuerst in Diagnose prüfen, bevor große Files/Importlimits geändert werden.

## 6. Geschwindigkeit: keine Netzwerkarbeit bei D-Pad/OK/Links

Der Nutzer meldet **lange Wartezeit beim Öffnen der linken Senderliste**. Ursache ist am Gerät noch nicht gemessen; denkbare Anteile im aktuellen Overlay:

- `channels_for_category(self.channels,...)` durchsucht bei Bedarf einen Katalog von früher **53.664 Sendern**; im aktuell gewählten Bereich zeigt das Gerät **2746 Sender / 28 Seiten**.
- `live_overlay._render()` erstellt `ControlList`-Zeilen neu und liest `load_cache(portal_id)`; `guide_for_channel` kann für bis zu 100 Sender pro Seite Zeitfensterdaten sortieren. Wiederholte UI-Berechnungen sind zu prüfen.
- Der Xtream-Katalog existiert bereits im Cache, aber der für die Sidebar benötigte Kategorie-/Senderindex und **aktuelle Now/Next-Ansicht** werden nicht zwingend als fertiger View-Cache vorgehalten.

**Empfohlene Architektur und Testpunkte:**

- Beim Portal-/Katalog-Refresh **im Hintergrund** Index pro Gruppe, Sender-ID-Lookup und Metadaten vorbereiten; beim tatsächlichen Öffnen der Liste kein synchrones Neuladen von Netzwerkkatalogen.
- EPG-Daten **asynchron** laden und normalisiert in einem **bounded local now/next snapshot** für laufenden Sender + sichtbare Liste vorhalten, mit gezielter Aktualisierung bei Zeitwechsel/Quellenimport; niemals alle 53.664 Sender permanent im Sekundentakt neu berechnen.
- Auf Fernbedienungsaktionen nur vorgefertigte Daten lesen; UI-Thread-Operationen auf sichtbare Zeilen/Fenster begrenzen. Snapshot-Caches pro `portal_id`, Kategorie, Datenversion und Zeitintervall mit kontrolliertem Invalidieren bei Senderwechsel, Cache-/EPG-Refresh und Benutzerzuordnung.
- Bestehendes `load_cache` nicht unbegrenzt auf jedem Steuerereignis von Disk lesen. Verwende memoisierten lokalen EPG-Zugriff mit kontrolliertem Cache-Lebenszyklus; persistierte Profildaten, manuelle Zuordnungen, Zeitlimits unverändert schützen.
- Die 100er-Pagination und Navi-Position beibehalten; ggf. nur die tatsächlich sichtbaren ~8–12 Zeilen rendern (Lazy/Viewport) statt 100 Widgets/Now-Next-Titel bei jedem Menüaufruf. Keine Netzanfragen aus `onAction` oder `onControl`.
- **Messbare Zielwerte, kein bereits erreichter Istwert:** auf echtem Android-TV bei warmem Cache Infoleiste möglichst **<250 ms**, linke Senderliste **<500 ms** bis zur ersten sichtbaren Fokusmarkierung; langsame Geräte und kalter Cache getrennt protokollieren. Diese Werte nach echten Vorher/Nachher-Messungen anpassen.
- Performance-Diagnose als anonymisierte Phasen-Timings (Katalogindex, EPG-Snapshot, Render/Focus), ohne Provider-URLs oder Credentials. Korrekte Fehlermeldung bei Cache-/EPG-Miss statt schwarzem Bildschirm oder Endlos-Spinner.

## 7. Vorschlag für Lieferung und Abnahme mit Codex

**Phase A – Datenbasis:** Issue #13 prüfen; echte Now/Next-Titel + Start/Stop, Kurz-EPG-Fallback und Portal-/Quellenstatus für regulären Sender am Android-TV verifizieren. Fake-/Fixture-Daten nur für Tests, nicht als reale Ergebnisse ausgeben.

**Phase B – Interaktionsmodell:** `LIVE_FULL → INFO_BAR → PLAYER_CONTROLS → MORE_SETTINGS` unter Kodi 21 programmatisch abbilden; Links `CHANNEL_LIST`; Right/Back konsistent. Native Keyevents und OnControl-Events deduplizieren; Long-OK und zurück nicht nebenbei kaputtmachen. Sichtbarer Fokus und Buttons für Ton/Bild/Untertitel/EPG.

**Phase C – Performance:** Senderindex und Now/Next-Snapshot vorbereiten; UI-Eröffnungszeiten auf echtem Android-TV messen und optimieren, 2746- und 53.664-Sender-Fälle testen. Kein Netzwerk in Input-Callbacks. Keine Kodi-weiten Keymap-Eingriffe.

**Phase D – visueller Feinschliff:** Skin-unabhängige Icon-Assets, gut lesbare Zeilen, progressbar, TV-safe-area, XCMate-Farben. Vollständigen späteren `XCMate Skin` nicht zum Blocker machen.

**Abnahme:** 
1. Einmal OK zeigt **Senderlogo, Jetzt, Von–bis, Danach, Progress und Restzeit** (oder klaren Missing-State).
2. Nochmal OK oder Runter auf der Infoleiste öffnet **die Bedienleiste**, ohne sofort Pause/Stop auszuführen.
3. Links öffnet binnen gemessener kurzer Wartezeit die Senderliste; pro sichtbarer Zeile Sendername, Jetzt, Von–bis; fokussierter Sender mit korrekt gematchtem EPG.
4. Hoch/Runter/OK/Links/Zurück/Stop funktioniert wiederholt ohne doppelten Fokuswechsel, falsche Sender oder schwarze Kodi-Screens. Andere Add-ons und BINGIE MOD bleiben intakt.
5. EPG-Button öffnet ein echtes Programmfenster oder verständlichen Quellstatus, nicht bloß eine leere „EPG“-Senderliste. Quellen-/Matchingdiagnose ist nach Neustart auslesbar.
6. Tests und Android-Geräteprotokoll mit **korrekter Versionsnummer**. Änderungen ausschließlich neuer Branch + PR; kein automatischer Merge/Publish ohne Nutzerfreigabe.

## 8. Verweise / aktueller Stand

- [Letzter realer Android-TV-Test der 0.1.24](ANDROID_DEVICE_TEST_024_EPG_NAV_DE.md): Overlay und Zusatzleiste erstmals sichtbar; EPG leer, Navigation teilweise unsicher, Senderliste langsam laut Nutzer.
- [P0-TV-Navigation, Issue #12](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12).
- [EPG-Daten/Status, Issue #13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13).
- [Separater XCMate Skin, Issue #14](https://github.com/artattakk-creator/kodi-noodleprivate/issues/14).
- [Aktueller Projektstatus](CODEX_STATUS_CURRENT_DE.md), [Designgrundlage](DESIGN_SYSTEM_DE.md).

**Wichtig für den nächsten Chat:** Dieses Dokument ist die verbindliche **neue UX-Anforderung**, noch keine getestete Implementierung. Alles in `main` bleibt vorerst auf XCMate 0.1.24.
