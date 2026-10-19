# XCMate 0.1.27 – verbindliche Ergänzung: Navigations-Freeze, Medien-Backdrops, globale Suche und BINGIE-MOD-Widgets

> **Implementierungsstand 19.10.2026:** Neue Module/Routen des 0.1.27-Kandidaten sind auf
> `feat/xcmate-027-catalogue-home` implementiert und in 312 Cloud-Tests geprüft.
> [Bericht, ZIP, genaue Teilabgrenzung](IMPLEMENTIERUNG_027_KATALOG_WIDGETS_EPG_DE.md)
> und [offene Android-Abnahme](ANDROID_TESTPLAN_027_DE.md) sind maßgeblich für den Ist-Stand.
> Produktiv bleibt 0.1.26. Die nachfolgenden Anforderungen bleiben der Vertrag;
> Aussagen „noch keine Implementierung“ beschreiben ihren ursprünglichen Auftragsstand.

**Erfasst:** 19.10.2026. **Status:** vom Nutzer festgelegte Anforderungen; **noch nicht implementiert, nicht auf Android-TV getestet, kein neuer Release**.  
**Repository:** `artattakk-creator/kodi-noodleprivate`; Kodi-Add-on `plugin.video.xtreammate`; derzeit veröffentlicht **0.1.26**.  
**Lesereihenfolge für Codex:** [Hauptauftrag 0.1.27](CODEX_AUFTRAG_027_STARTMENUE_SETTINGS_GRUPPEN_EPG_DE.md) → [Filme-/Serien-Bauanweisung](CODEX_AUFTRAG_027_FILME_SERIEN_NETFLIX_NAV_DETAIL_DE.md) → **dieses Dokument** → [aktueller Release-Status](CODEX_STATUS_CURRENT_DE.md).  
**Vorbild:** TiviMate-Bedienablauf und Titan BINGIE MOD/Netflix-artige Medienpräsentation, aber eigenständige XCMate-Implementierung und Assets.

## 0. HÖCHSTE VORGABE: Bestand 0.1.26 auf FREEZE – nur additive Entwicklung

Der Nutzer bestätigt, dass die aktuelle XCMate-Version **0.1.26 auf seinem Android-TV grundsätzlich funktioniert** und die aktuelle TV-Bedienung gefällt. Darauf basiert ein verbindlicher **funktionaler Regression-Freeze**:

- **Nicht neu erfinden oder ohne belegte Notwendigkeit ändern:** Live-Startsender, aktuelles Live-TV-Overlay, erste OK-Jetzt/Danach-Infobar/Progress, zweite Player-Tape-Deck-Ebene, dritte Einstellungen-Ebene, native Fernbedienungsaktionen einschließlich Links→Sender→Gruppen, Zurück, Playback-Lifecycle, Xtream-Session-Erkennung, Standard-Keymap, Player/Stop, BINGIE MOD als bestehender Skin.
- Alte Portalprofile, gespeicherte Einstellungen, aktive/ausgeblendete Gruppen, Favoriten, EPG-Zuordnungen, Diagnose und Zugangs-/Mediencaches **behalten**. Keine stillen Schema-/ID-Änderungen und keine Löschung vermeintlich „nicht mehr benötigter“ Pfade.
- Änderungen an bestehenden Komponenten nur **minimal und durch Regressionstests begründet**, neue UI-/Widget-/Suchfunktionen bevorzugt in **separaten Modulen und neuen Routen**. Unveränderte API-Aufrufe erhalten, alte Action-Routen nach UI-Neuordnung weiterhin unterstützen.
- Keine globale Kodi-Keymap einschalten. Ohne explizit freigegebene Skinänderung keine bestehenden BINGIE-MOD-Skin-Dateien, Menüs oder User-Widgets überschreiben. Separate, konfigurierbare Widget-Integration anbieten.
- **Automatische Tests ≠ Android-Abnahme:** Ein realer Kodi-21-TV-Test für TV-Remote/Medien-Fokus/Skin-Widgets wird vor „Funktioniert vollständig“ zwingend gefordert. Versions- und Funktionsstatus getrennt dokumentieren.

## 1. Filme und Serien: großflächige Hintergrundgrafiken, Covergruppen und stabile Fokusnavigation

Die bereits [beauftragte Medien-UX](CODEX_AUFTRAG_027_FILME_SERIEN_NETFLIX_NAV_DETAIL_DE.md) wird hiermit ausdrücklich präzisiert.

### 1.1 Hintergrundbild/Artwork in jeder Medienansicht

- **Filme-Landingpage und Serien-Landingpage** zeigen ein passend abgedunkeltes, hochwertiges **Fanart-/Backdrop-Hintergrundbild** des gerade fokussierten Titels, dazu die Posterreihe **NEU HINZUGEFÜGT** und darunter **FILME / KATEGORIEN** bzw. **SERIEN / KATEGORIEN**.
- In **Gruppen-/Posteransicht** wird beim Kachelfokus nach Möglichkeit ein echtes **Filmbild/Serien-Fanart** als Hintergrund verwendet; Cover bleiben als vertikale Poster sichtbar. Bei der Detailansicht großes Backdrop + Cover + Metadaten wie in der Hauptspezifikation.
- Artwork-Priorität: `fanart/backdrop` (wenn vorhanden) → vom Anbieter verfügbares `cover/poster/movie_image` in geeignetem Layout → **XCMate-eigener neutraler Gradient/Placeholder**, niemals fremde Bilder oder erfundene Filmgrafiken.
- **Asynchroner Artwork-Cache**, limitierter Preload für Fokusnachbarn; Fokuswechsel dürfen Kodi nicht durch Downloads blockieren. Defekte/fehlende URL und sehr große Bilder sauber behandeln. Bei schnell wechselndem Fokus späte Bildantworten nicht auf falschen Titel legen; ruhig/optional weich überblenden.
- Poster-/Backdrop-Verhältnis 2:3 bzw. 16:9 soweit verfügbar; Textkontrast, TV-Safe-Area, Ladezustand und Fokusmarkierung aus TV-Entfernung lesbar. **Kein globaler Kodi-Skin-Mod** für dieses XCMate-interne Design nötig.

### 1.2 Exakte Gruppen- und Poster-Navigation

```text
FILME / SERIEN LANDINGPAGE
  NEU HINZUGEFÜGT   [Poster] [Poster] [Poster] ...   ←/→ scrollt horizontal
  [FILME / KATEGORIEN] bzw. [SERIEN / KATEGORIEN]
               │ OK
               ▼
GRUPPENANSICHT
  ┌──────────────────┬─────────────────────────────────────────┐
  │ Gruppen links    │ Cover-Galerie mittig/rechts             │
  │ Action           │ [Cover 1] [Cover 2] [Cover 3]          │
  │ Komödie          │ Titel · Laufzeit · Bewertung (wenn da)  │
  │ Thriller         │ Auswahl-/Fokus-Hintergrundgrafik        │
  └──────────────────┴─────────────────────────────────────────┘
    │ Fokus auf Gruppe, OK → Poster dieser Gruppe
    │ Rechts zur Galerie → linke Leiste einklappen
    ▼
VOLLFLÄCHIGE POSTERWAND
  [Cover 1] [Cover 2] [Cover 3] [Cover 4] ...
  Links am LINKEN RAND → Gruppenleiste wieder ausklappen
  OK auf Cover → Film-/Serien-Detailseite
```

**Verbindliche Aktionstabelle:**

| Kontext | Eingabe | Verhalten |
|---|---|---|
| Landingpage Neuheiten | Links/Rechts | Eine Posterposition nach links/rechts, ohne sofortiges Abspielen |
| Landingpage | Runter | Fokus auf `Filme / Kategorien` bzw. `Serien / Kategorien` |
| Kategorien starten | OK | **Erste aktivierte** Gruppe, nicht eine deaktivierte oder alle Kategorien; Session-Bewusstwahl respektieren |
| Gruppenleiste | Hoch/Runter | Nächste/vorherige freigegebene Gruppe markieren |
| Gruppenleiste | OK | Ausgewählte Gruppe laden, Fokus/Viewport nachvollziehbar |
| Gruppenleiste | Rechts | Covergalerie fokussieren und **Leiste einklappen** |
| Eingeklappte Covergalerie | Links innerhalb einer Zeile | Vorheriges Cover fokussieren; **erst am linken Rand** Leiste wieder öffnen |
| Poster-Galerie | Hoch/Runter/Rechts | Durch Grid navigieren; aktuell fokussierten Film/Serie und Scrollposition erhalten |
| Poster | OK | Detailansicht mit Backdrop/Cover/Metadaten/Aktionen |
| Detail/Posterwand | Zurück | Genau eine Ebene zurück; Gruppe, Coverposition und Poster-Fokus wiederherstellen |

- **Filme und Serien spiegelgleich** implementieren, gemeinsame UI-Komponenten/Viewmodelle, getrennte `vod`-/`series`-IDs/Gruppen.
- Filmlaufzeit, echte Bewertung, Jahr, Genre, Titel als fokussierte Detailinformationen; Providerdaten fehlen → klarer `Nicht verfügbar`-Zustand. Keine künstlich generierten IMDb-Werte.
- Ein Foto-/Coverwechsel darf keine Playbackaktion auslösen; Detailaktionen (Start/Neustart/Fortsetzen/Favorit/YouTube-Trailer) bleiben Teil des bereits beauftragten Film-/Serien-Detailfensters.
- Falls Kodi-`WindowXML/Dialog` nötig, native Fokus- und Callback-Signaturen unter Kodi 21 strikt testen; BINGIE MOD nicht mit einem gewöhnlichen Verzeichnis-Rendering verwechseln.

## 2. EINHEITLICHE GLOBALE SUCHE: TV, FILME, SERIEN mit separaten Rubriken und Trefferzahlen

**Nutzerziel:** Ein Suchbegriff erscheint in **allen passenden Medientypen unabhängig voneinander**. Beispiel `House of Dragon`: passende **TV-Sender**, **Filme** und **Serien** gleichzeitig. Ein Treffer in einem Abschnitt darf Treffer aus anderen Abschnitten nicht verdecken.

```text
XCMate Suche: „House of Dragon“

    LIVE-TV                       1 Treffer
      [Senderlogo] House of Dragon TV   → live abspielen

    FILME                         2 Treffer
      [Poster] ...                     → Filmdetails

    SERIEN                        1 Treffer
      [Poster] House of Dragon         → Seriendetails/Staffeln
```

**Muss-Verhalten:**
- Von allen relevanten XCMate-Menüs über **Suche** erreichbar (zusätzlicher Such-Shortcut innerhalb Film/Serie/EPG und Settings oder sichtbares Suchsymbol; **die verbindliche Startseite behält dennoch genau sechs Hauptpunkte**). Optional globale Suchaktion/Remote-Suche nur wenn Kodi-konform.
- Ergebnis-Startseite **drei klar getrennte Abschnitte** `LIVE-TV (N)`, `FILME (N)`, `SERIEN (N)` mit **wirklich typbezogenen Trefferzahlen**, nicht nur eine flache zusammengeführte Liste. Bei 0 Treffern Abschnitt `0 Treffer` darstellen. Treffen nur Sender, dürfen Film/Serie nicht fälschlich verschwinden.
- Option `Alle Ergebnisse`, eine Rubrik wählen, einzelne Cover/Treffer mit OK öffnen. Live-Sender → reguläre `play_live`-Session/Live-Overlay, Film → detailbasierte `play_vod`-Auswahl, Serie → Seriendetails/Staffeln/Episoden. Mit Zurück zur Ergebnisübersicht ohne erneute Suche.
- Case-insensitive Suche nach Titeln und soweit verfügbar Synonymen, Genres/Beschreibungen (optionale erweiterte Felder, klar kommunizieren). Umlaute/Unicode/Mehrfachwörter normalisieren, ohne relevante unterschiedliche IDs zusammenzulegen.
- Gewählte/aktivierte Sender-, Film- und Seriengruppen pro Portal **beachten**. Multi-Portal: entweder explizit `Alle aktiven Accounts` mit pro Treffer klarer Account-Zuordnung oder aktueller Account, je Einstellung. Identität `portal_id`+`media_type`+`stream_id/series_id` garantiert kein unerwünschtes Deduplizieren gleicher Titel in unterschiedlichen Medienarten.
- **Vollständige Treffermengen** aus lokalem, versioniertem Suchindex, UI nur **paginiert/virtualisiert**. Kein `[:50]` als falsche Gesamttrefferzahl. Falls Index/Katalog noch im Hintergrund lädt: `Index wird geladen`, pro Rubrik vorläufiger Status statt unbelegter finaler Anzahl.
- Keine Provider-/M3U-Netzwerkanfrage während Eingabe, Fokus oder Suchergebnisnavigation. Indizes asynchron bei erfolgreichem Katalogimport aktualisieren; Cache/Index-Lifecycle und Fehlerdiagnose dokumentieren. Für STB-/M3U-Provider mit eingeschränktem lokalen Katalog eine bewusste Hintergrundsuche anbieten und **Teilzahlen als unvollständig markieren**.
- Suchprotokoll enthält **keine** Portalpasswörter/Stream-URLs, gespeicherte Suchanfragen optional und mit Benutzerentscheidung. Keine hartcodierten Beispieltitel als echte Resultate.
- **Regressionstest:** `House of Dragon` Fixture mit 1 Live-Sender, 2 Filmen und 1 Serie → Exakt **1 / 2 / 1** getrennte Counts, gleiche Namen in mehreren Kategorien bleiben sichtbar; 5000+ Treffer werden paginiert und die Gesamtzahlen bleiben korrekt.

**Bestandsanalyse im aktuellen main (0.1.26):** `main.py::_search_results()` und `_search_in_portal_collect()` durchsuchen bereits Providerdaten, fügen aber **alle ListItems in einer flachen Kodi-Liste** zusammen und rufen pro Xtream-Medienart teils `[:50]` ab. Diese Routen als Kompatibilitätserhalt behandeln; neue `global_search`, `search_section` o.ä. ergänzen, nicht alte `search`-Links zerstören.

## 3. BINGIE MOD KODI-HOMESCREEN – 3 XCMate-Widgetreihen

**Nutzerziel:** Nicht nur die XCMate-App, sondern **die bestehende Titan-BINGIE-MOD-Startseite** soll drei horizontal navigierbare, direkt benutzbare XCMate-Reihen anzeigen:

1. **XCMate · Live-TV** – Sender aus der **aktivierten Haupt-/Startsendergruppe**, in der der gespeicherte **Startkanal** liegt. Senderlogo, Sendername, `Jetzt: Titel`, `Danach`, Start-/Endzeiten und ggf. Fortschritt nur aus echtem lokalen EPG. **Erstes Widget-Element bevorzugt Startkanal**, danach die übrigen aktivierten Sender dieser Gruppe in definierter Reihenfolge; die Gruppe folgt aktiver Portalwahl/Startkanal. Klick auf Sender → `play_live` und bestehende LiveSession/Infobar, nicht nur Gruppenauswahl. Wenn Startkanal ohne aktive Gruppe, definierter Fallback und Hinweis.
2. **XCMate · Neueste Filme** – letzte tatsächlich neu hinzugefügte freigegebene Filme aus dem aktiven IPTV-Account, als horizontale Posterreihe. Klick → Filmdetails, von dort startbar (optional Context-Schnellstart).
3. **XCMate · Neueste Serien** – letzte nachweislich neue Serien mit Postern. Klick → Seriendetails/Staffel, **nicht** direkt irgendeine Episode.

**Wichtige technische Tatsache:** Ein Kodi-Video-Add-on kann nicht zuverlässig allein durch eine neue Python-Route fremde Skin-Homepage-Dateien ändern oder an einer beliebigen BINGIE-MOD-Version automatisch drei feste Rows rendern. **Erforderlich:** Kodi-konforme **Skin-Widget-Directory-Routen** und ein **konkreter, auf der vorhandenen BINGIE-MOD-Version geprüfter Einrichtungsweg** (Skin-Einstellungen → Widgets), oder ein separater freiwillig installierter Skin-Patch/Prototyp **nur nach ausdrücklicher Zustimmung**. Bestehende BINGIE-MOD-Einstellungen **nicht ungefragt überschreiben**.

**Empfohlene stabile Widget-Routen (nur Vorschlag, Codex entscheidet namespaced):**
- `plugin://plugin.video.xtreammate/?action=widget_live_start_group&pid=<portal_id>`
- `plugin://plugin.video.xtreammate/?action=widget_recent_vod&pid=<portal_id>`
- `plugin://plugin.video.xtreammate/?action=widget_recent_series&pid=<portal_id>`

Pfadangaben dienen als Architekturkontrakt; Implementierung muss Query-Schema/`self.url()` im tatsächlichen Code sicher erzeugen. **Keine Credential-URLs** in Widgets.

**Bestehende Ausgangspunkte, die weiter zu verwenden sind:**
- `main.py::_widget_groups()` und `_widget_channels()` sind bereits bestehende Kodi-Skin-Routen. `_widget_channels` benötigt aktuell eine konkrete `cat_id` und listet Sender samt lokalem `XtreamMate.Now/Next`; ermittelt die Gruppe des Startkanals **nicht automatisch**. Eine neue Startgruppenroute kann bestehende `widget_channels` reuse/parameterisieren.
- `main.py::_recent_vod()` / `_recent_series()` liefern bereits Kodi-Widget-Directory-Items über `_recent_media()`; `latest_media.recent_entries(...limit=50)` liefert derzeit höchstens 50. Für BINGIE-MOD-Widget genügt ggf. eine **begrenzte aktuelle Rail mit sauberem `Alle anzeigen`-Link**; für das separat beauftragte komplette Neuheiten-Carousel im XCMate-Film-/Serienbereich muss der Katalog **vollständig paginiert durchsuchbar** bleiben. Keine 50er-Grenze als „alles“ darstellen.
- Für Poster/Logo/Fanart `Kodi ListItem.setArt`, korrekten `setInfo`-/InfoTag-Inhalt, `IsPlayable` und den passenden `xbmcplugin.setContent('videos'/'movies'/'tvshows')` sauber setzen, damit BINGIE MOD tatsächlich Karten aus den Widget-Endpunkten darstellt.
- Kodi-Widgets sollen aus dem **lokalen Cache** gelesen werden und sofort rendern; Kodi-Hover/Widgets dürfen **keine** kompletten Katalogdownloads oder 53.664× EPG-Berechnungen auslösen. Sender-/Titelindex/EPG-Snapshot durch Hintergrundservice warm halten, Daten per deterministischem TTL/Update erneuern; erkennbaren Cold-Cache-State statt Kodi-Hänger anbieten.
- Aktuelle Sendergruppe/Favoriten-/Account-Filter respektieren. Wenn BINGIE MOD eine Widget-Liste anhand `folder`/isPlayable anders rendert, echten Kodi-TV-Screenshot und Skin-/Build-Version dokumentieren und unterstützte Widget-Ansicht wählen.
- **Komplette Einrichtungsanleitung:** Die drei genauen XCMate-Widgetpfade, Schritte in BINGIE MOD für drei Rows in richtiger Reihenfolge, Artwork-/Aspect-Ratio-Einstellung und Rückkehrmöglichkeit zum bisherigen Homescreen. Optional XCMate-Menüpunkt „BINGIE-MOD-Widgets einrichten“ mit Anleitung/Test, nicht automatische Manipulation des installierten Skins.

## 4. Arbeiten/Prioritäten/Tests

**PR A – FREEZE + bestehender Hauptauftrag:** Sechs XCMate-Startpunkte, Einstellungen, EPG-Langzeitplan; bestehendes Live-Overlay unberührt (siehe [Hauptauftrag](CODEX_AUFTRAG_027_STARTMENUE_SETTINGS_GRUPPEN_EPG_DE.md)).

**PR B – Film-/Serien-UI:** Background/Fanart pro Fokus/Details, horizontale Neuheitenreihe und linke/einklappbare Gruppen-Navigation bei Film **und** Serie; wenige gleichzeitig sichtbare Poster, Browser-Fokus/Back/Android-Input absichern (siehe [Medien-UX](CODEX_AUFTRAG_027_FILME_SERIEN_NETFLIX_NAV_DETAIL_DE.md)).

**PR C – globale Suche:** Gesonderte drei Rubriken mit typbezogenen echten Counts und zugehöriger Navigation; vorhandene Suchrouten als Fallback. Fixture-Tests Multi-Portal, verschiedene Medientypen, >50 Treffer, deaktivierte Gruppen, Suche ohne Netz.

**PR D – BINGIE-Widgets:** Drei spezialisierte, stable Plugin-Routen, Kodi-Metadaten, Startkanalgruppenauflösung, Lazy/Cache, Test mit echtem BINGIE-MOD-Skin und klarer Einrichtungsanleitung. Bestehende Benutzerskin-Konfiguration nicht ohne Freigabe überschreiben. Spätere optionale Autoeinrichtung eigener Skin-Patch nur nach separater Zustimmung.

**Regression/DoD:**
- [ ] 0.1.26 Live-TV/Player/OK-/Links-/Zurück-Fernbedienung unverändert nutzbar.
- [ ] Filme/Serien mit echtem Art-Hintergrund, Cover, Laufzeit/Bewertung soweit vorhanden, korrektem Gruppenfokus und vollständiger navigierbarer Posterwand.
- [ ] `Links` am Coverrandschritt öffnet Gruppen; `Rechts` aus Gruppen klappt sie ein; keine Fokus-/Scrollposition verloren.
- [ ] Globale Suche mit **Live/Film/Serie** und **getrennten Count-Badges/Zeilen**; gleiche Titel in mehreren Rubriken, Teilkataloge nicht fälschlich als vollständig kennzeichnen; Detail-/Play-Routen korrekt.
- [ ] BINGIE MOD zeigt auf realem Kodi-TV **3 getrennte horizontale Reihen in der gewünschten Reihenfolge** und Live-Widget startet echten Stream; Filme/Serien öffnen richtige Detailseite.
- [ ] Kalt-/Warmcache-Messung, Rücknavigation/Android-Resume, Kodi 21, große Kataloge, defekte Bilder, fehlender EPG, M3U/STB-Teilkompatibilität, mehr als ein Portal.
- [ ] Kein stiller Datenverlust, keine Geheimnisse in Widget-URLs/Logs, keine Veränderung der Kodi-Skin-Files ohne gesonderte Einwilligung.
- [ ] CI erfolgreich, PR mit exakten Änderungen/Modulaufteilung, dokumentierter Android-Abnahme und neuer Versionsnummer. **Nicht automatisch nach `main` mergen oder Repo-Update publizieren.**

**Stand:** Dieser gesamte Block ist **Planung**, noch keine Version 0.1.27. Ein 0.1.27-Meilenstein darf Unterfunktionen sauber in folgende Versionen verschieben, wenn sie nicht vollständig implementiert und getestet sind; solche Abgrenzung im PR klar machen.

## 5. Direktauftrag für Codex

> Lies zuerst `docs/XCMate/CODEX_AUFTRAG_027_STARTMENUE_SETTINGS_GRUPPEN_EPG_DE.md`, `docs/XCMate/CODEX_AUFTRAG_027_FILME_SERIEN_NETFLIX_NAV_DETAIL_DE.md` und **dieses Dokument** `docs/XCMate/CODEX_AUFTRAG_027_FREEZE_GLOBAL_SEARCH_BINGIE_WIDGETS_DE.md`. **FREEZE:** Live-TV-/Remote-OSD aus 0.1.26 nicht umbauen oder degradieren. Implementiere bei Film und Serie echte Backdrop-/Posteransichten, linkes gruppenbasiertes Menü, Rechts→vollbreite Posterwand und Links am Gridrand→Gruppenleiste, mit stabilem Fokus und lokalen Caches. Implementiere **eine gemeinsame Suche** über TV, Filme und Serien mit **drei separaten Ergebnisrubriken und korrekter Trefferzahl pro Rubrik** (auch wenn derselbe Suchbegriff in allen drei auftaucht). Erstelle zusätzlich **drei BINGIE-MOD-Home-Widget-Routen** für Live-Sender **aus der Startkanal-Gruppe** mit echten Now-/Next-Titeln sowie neueste Filme und neueste Serien; liefere dokumentierte Skin-Widget-Einrichtung, verändere nicht ungefragt den BINGIE-MOD-Skin. Kodi-21-Fokus-/Performance-Tests, Branch + PR; **kein Merge nach `main` und keine öffentliche 0.1.27-Behauptung ohne Freigabe**.
