# XCMate 0.1.27 – Codex-Zusatzauftrag: Filme und Serien in fernbedienbarer Streaming-Oberfläche

> **Implementierungsstand 19.10.2026:** Neue Module/Routen des 0.1.27-Kandidaten sind auf
> `feat/xcmate-027-catalogue-home` implementiert und in 313 Cloud-Tests geprüft.
> [Bericht, ZIP, genaue Teilabgrenzung](IMPLEMENTIERUNG_027_KATALOG_WIDGETS_EPG_DE.md)
> und [offene Android-Abnahme](ANDROID_TESTPLAN_027_DE.md) sind maßgeblich für den Ist-Stand.
> Produktiv bleibt 0.1.26. Die nachfolgenden Anforderungen bleiben der Vertrag;
> Aussagen „noch keine Implementierung“ beschreiben ihren ursprünglichen Auftragsstand.

**Beschlossen:** 19.10.2026, ergänzende Nutzeranforderung zum bereits auf GitHub hinterlegten [0.1.27-Hauptauftrag](CODEX_AUFTRAG_027_STARTMENUE_SETTINGS_GRUPPEN_EPG_DE.md).  
**Basis:** `main`, aktuell veröffentlichte XCMate-Version `0.1.26`; noch **KEINE** Implementierung/Abnahme für diese neue Oberfläche.  
**Produktziel:** Eigenständiger XCMate-Film-/Serienbereich mit dem Navigationsprinzip von Netflix-/BINGIE-MOD-/TiviMate-Oberflächen, **ohne** proprietäre Grafiken, Software oder UI-Assets zu übernehmen. Format: Kodi 21/Omega, Android-TV/Fernbedienung, BINGIE MOD als installierter Skin. **Die bestehende, nun funktionierende Live-TV-Infobar samt drei Bedienebenen bleibt Freeze.**

## 0a. Ergänzungs-Freeze: Hintergrundgrafik und exakte Gruppensteuerung

Die präzisierte **verbindliche** Nutzeranforderung steht zusätzlich in [FREEZE / Suche / BINGIE-MOD-Widgets](CODEX_AUFTRAG_027_FREEZE_GLOBAL_SEARCH_BINGIE_WIDGETS_DE.md), einschließlich Codeansatz, Such-Trefferzahlen und drei Kodi-Homepage-Widgets ([#25](https://github.com/artattakk-creator/kodi-noodleprivate/issues/25), [#26](https://github.com/artattakk-creator/kodi-noodleprivate/issues/26)). **Jede Film- und Serienansicht** soll möglichst ein echtes Backdrop/Fanart des fokussierten Titels als dunkel überlagertes Hintergrundbild zeigen (kein Fake-Bild). Innerhalb der Kategorie-Galerie muss **Rechts von der Gruppenleiste** zur **vollbreiten Posteransicht** führen, und **Links erst an der linken Grid-Grenze** die Gruppenleiste automatisch wieder öffnen; Fokus, Gruppenauswahl und Scrollposition bleiben erhalten. Alle bisherigen Live-TV-, Player- und Fernbedienungsfunktionen von 0.1.26 sind **funktionaler Freeze**; Änderungen daran sind ohne besonderen nachweisbaren Grund untersagt.

## 1. Verbindlicher Einstieg: sechs XCMate-Hauptpunkte bleiben unverändert

`Startkanal · Live-TV · EPG · Filme · Serien · Einstellungen` bleiben die **einzigen sechs Einträge** im obersten Hauptmenü. **Filme** und **Serien** öffnen jeweils eine **eigene Landingpage** mit Neuheiten-Karussell oben und darunter einem anwählbaren Bereich für alle Kategorien/Gruppen. Keine Rückkehr zur bisherigen flachen Gruppenliste als erste Seite.

**Filme → Film-Landingpage:**
```text
╔══════════════════════════════════ XCMate · FILME ═════════════════════════════╗
║ NEU HINZUGEFÜGT                                                               ║
║  [Poster 1]   [Poster 2]   [Poster 3]   [Poster 4]   [Poster 5]   →         ║
║   ←/→: horizontal durch den Filmkatalog; OK: Filmdetails; ggf. Schnellstart    ║
║                                                                               ║
║ FILME / KATEGORIEN  →                                                          ║
║     Beim Anwählen: erste AKTIVIERTE Filmgruppe, links Gruppen, rechts Poster  ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Serien → Serien-Landingpage:** exakt analog mit `NEUE SERIEN`, horizontaler Reihe von **Seriencovern** und `SERIEN / KATEGORIEN`. Seriencover öffnen Seriendetails (mit Staffeln/Folgen), **nicht** wahllos die erste Episode abspielen.

**Horizontale Neuheitenreihe – verbindliches Verhalten:**
- Querformatiger oberer Bereich mit **vertikalen Filmplakaten/Serienpostern in einer horizontal scrollbaren Reihe**; bei Fokus Links/Rechts um genau eine Kachel, Fokusvergrößerung/Markierung wie in BINGIE MOD; mit Hoch/Runter zwischen Neuheitenreihe und Kategorieschaltfläche wechseln.
- Aus **allen** vorhandenen, freigegebenen Katalogtiteln in der korrekten Reihenfolge der **tatsächlichen Hinzufügedaten** bedienen. **Nicht** auf bisherige `recent_entries(limit=50)` beschränken, aber **nur einen begrenzten sichtbaren Ausschnitt plus nachfolgende Kacheln laden** (virtuelles Scrolling/Paging). „Alle“ heißt durchscrollbar, **nicht** alle 20.000 Poster gleichzeitig in Kodi bauen oder laden.
- Datenquelle Xtream-`added`/`date_added` sowie die bereits implementierte `latest_media.first_seen()`-Erkennung nutzen. Wenn Anbieter keine Zeitstempel hat, initialen Scan **nicht fälschlich vollständig als Neuheiten bezeichnen**; alternativ ehrliche Rubrik „Kürzlich erkannt“/„Für dich verfügbar“ mit eindeutigem Hinweis und stabiler Fallbacksortierung.
- Nur Film-/Seriengruppen anzeigen, die der Nutzer für den jeweiligen Account aktiviert hat. Duplikate nach **(`portal_id`, `media_type`, `stream_id`/`series_id`)** verhindern, nicht nur nach Titel. Bei mehreren Portalen Portalbezug anzeigen, keine zufällige Vermischung.
- OK auf Poster führt **standardmäßig in Detailansicht**, von dort `Abspielen` unmittelbar erreichbar (ein zusätzlicher Klick). Für schnellen Direktstart **separate Aktion** (z.B. Kontextmenü/Schnellstart), damit Nutzer gleichzeitig Coverdetails und direktes Starten nutzen kann. Fokus allein **niemals** Wiedergabe starten.
- Keine synchronen Katalog-/Bild-Metadaten-Netzwerkanfragen pro Tastendruck; lokaler Index, asynchroner Artwork-Cache, bounded Prefetch. Bei leerem/fehlendem Katalog aussagekräftiger Empty-State.

## 2. Film-Kategorien: linke Gruppenleiste, mittige Cover, Rechts maximiert Posterwand

**Auswahl `FILME / KATEGORIEN` aus der Landingpage:**
- In **erste aktivierte Filmgruppe** wechseln; wenn vorher innerhalb derselben Session eine andere Filmgruppe bewusst gewählt wurde, darf diese Auswahl erhalten bleiben. Fehlt die erste aktive Gruppe, deutliche Leermeldung mit Einstellungslink zur Gruppenverwaltung.
- Startansicht hat **linke vertikale Gruppenleiste** (nur aktivierte Filmgruppen) und **mittige/rechte Cover-Galerie** mit Postern der selektierten Gruppe. Sichtbare Titeldaten, Lade-/Selektionsmarkierung, ggf. Zahl der Titel, Gruppennamen. Default-Fokus sinnvoll (Gruppe oder erste Kachel).
- **Links in der Coveransicht** öffnet/fokussiert den Gruppen-Navigator; Hoch/Runter dort wählt Gruppe, OK übernimmt und aktualisiert die Cover. **Rechts vom Gruppenbereich** wechselt Fokus zur Filmgitteransicht und **klappt die linke Navigationsleiste ein**, sodass die Posterübersicht die volle Breite erhält.
- Im ausgeklappten Filmgitter über Links/Rechts/Hoch/Runter zwischen Covern navigieren; **Links am linken Rand** soll die Gruppenleiste wieder aufklappen, nicht als Tastendruck verschluckt werden. **Zurück** geht nur eine Ebene zurück, hält Gruppen-/Scrollposition wo sinnvoll. Fokus darf nach dem Ein-/Ausklappen oder Paging nicht verloren gehen.
- Pro Film: **Cover und Titel**, weitere Metadaten wie **Laufzeit und Bewertung**, soweit Anbieter oder genehmigte Metadatenquelle sie liefern. Gruppen-Galerie kann bei Fokus Titel/Laufzeit/Bewertung am oberen oder unteren Rand anzeigen, statt zu viele unlesbare Texte unter jedes Poster zu setzen. Nicht verfügbare Ratings/Laufzeiten ehrlich als fehlend behandeln, nie schätzen.
- Klick/OK auf ein Cover → **Film-Detailseite**. Mit einem separaten Direktabspiel-Shortcut/Kontextmenü kann ohne Umweg gestartet werden.

## 3. Vollwertige Film-Detailansicht (nicht bloß xbmcgui.Dialog().textviewer)

Beim Film-Cover-OK **eigene schöne Film-Detailseite** mit:
- Großem **Backdrop/Fanart-Hintergrundbild** aus Provider-Metadaten, ggf. bildschirmfüllend dunkel überlagert, und **Poster links**. Fehlt Backdrop, Poster als Fallback/Gradient, niemals defektes oder frei erfundenes Artwork.
- Titel, Jahr, Genre, Beschreibung/Inhaltsangabe, **Laufzeit** und **Bewertung mit Quellhinweis** (nur echte verfügbare Daten), ggf. Regie/Besetzung/Freigabe soweit Quelle verifiziert. Lokaliserte Anzeige in Kodi-/Gerätesprache, gute Lesbarkeit und TV-Safe-Area.
- **Interaktive Aktionen:** `Abspielen` / `Neu starten` (ab Sekunde 0), **`Fortsetzen ab HH:MM:SS`** wenn gültiger gespeicherter Wiedergabefortschritt existiert, **`Zu Favoriten hinzufügen` ↔ `Aus Favoriten entfernen`** als dynamische Schaltfläche, **`Trailer auf YouTube`** nur wenn gültige ID geliefert und Kodi-`plugin.video.youtube` vorhanden; andernfalls ausblenden/deaktivieren und Grund erklären.
- Richtige Zustände: unfertiger Film → Fortschrittsbalken und Fortsetzen; nie gesehener Film → Abspielen; beendeter Film → Neu starten. Ein Filmstart aus Kontextmenü darf dabei Bookmark nicht versehentlich löschen.
- **Wichtig für die Umsetzung:** Bestehende Favoriten (`load_favourites`, `toggle_favourite`) sind stark auf Kanal-`url`-Einträge ausgerichtet. Für VOD/Serien **eigenen stabilen Medien-Favoriten-Datensatz** nach Portal-/Stream-/Series-ID nutzen oder kompatibel erweitern. Aktuelle Live-TV-Favoriten **nicht beschädigen**, keine URL mit Credentials in Favoriten/Debug schreiben.
- **Wiedergabefortschritt/Resume ist aktuell für Filme nicht sauber Ende-zu-Ende bestätigt.** Zuerst vorhandene Kodi-Bibliotheks-Bookmarks und Player-Capabilities prüfen; andernfalls eigenes persistentes, atomar gespeichertes Resume-Schema für XCMate-VOD implementieren (IDs statt URLs), `xbmc.Player` Ereignisse korrekt abgrenzen, tatsächliche Position beim Stop/Exit speichern, erst nach Playback-Ready wieder seeken und nur bei seekbarer VOD-Quelle. Der Fullscreen-Live-TV-Overlay darf nicht beeinflusst werden.
- **YouTube-Trailer:** `metadata_views.trailer_id()` und `main._play_youtube_id()` schon vorhanden, aber bislang teils als Kontextmenü/Textviewer. Sichere validierte YouTube-ID wiederverwenden, bei fehlendem YouTube-Add-on klare Meldung; **keine** frei erfundenen Videolinks.
- **Direkte Wiedergabe** mittels vorhandener Kodi-Player-`play_vod`-Route erhalten, Episode gesondert behandeln. VOD-Detailansicht/Back zurück zum selben fokussierten Poster, kein schwarzer Kodi-Bildschirm.

## 4. Gleiche UX für Serien, ergänzt um Staffeln/Folgen

**Serien-Landingpage:** horizontal durch **alle als neu belegbaren Serien**, `SERIEN / KATEGORIEN` darunter; Auswahl erste **aktivierte Seriengruppe**, links Gruppenleiste und mittig Poster, Rechts blendet Gruppe für volle Galerie aus. TV-Fokus identisch zu Filmen.

**Serien-Detailseite:**
- Großes Backdrop, Poster, Titel, Jahr, Genres, Bewertung, Beschreibung, ggf. Anzahl Staffeln/Folgen, sofern Provider verfügbar.
- Favorit ein/aus wie bei Film, aber stabile Identität `(portal_id,series_id)`.
- Button `Staffeln und Episoden`: Staffel-Auswahl (numerisch sortiert), Episodenliste mit Folgennummer, Laufzeit, Episodebild, Beschreibung (soweit verfügbar). Play startet **gewählte** Episode, kein falscher sofortiger Start der ganzen Serie.
- **Fortsetzen** bei einer konkret begonnenen Folge, `Nächste Folge` / `Weiterschauen`, Gesehen-Status und optional Auto-Next entsprechend bereits vorhandener [Serienfortschritt-Spezifikation](SERIES_PROGRESS_SPEC_DE.md) – dort steht ausdrücklich **noch nicht implementiert**. Keine pauschale Behauptung, Kodi halte jeden Episodenfortschritt automatisch vor.
- Trailer für Serie nur wenn gültige ID vorhanden, über vorhandenen Kodi-YouTube-Pfad. Fehlende Trailer nicht erfinden.
- Episode-/Serienfavoriten, Resume/Watched-Status und Gruppenauswahl müssen bei Kodi-Neustart und Accountwechsel erhalten bleiben.

## 5. Kodi-21-Implementierungsentscheidung und technische Grenzen

**Wichtig:** Eine normale Kodi-`xbmcplugin`-Verzeichnisliste kann **nicht** zuverlässig eine unabhängige horizontale Neuheitenreihe **UND** einklappbare linke Kategorienleiste **UND** rechtsseitiges Poster-Gitter in exakt der gewünschten Weise bestimmen. Das endgültige Layout hängt sonst vom installierten Skin ab. Codex soll für diese **konkrete**, skinunabhängige Navigation **ein eigenes Kodi-`WindowXML`/`WindowXMLDialog` bzw. gleichwertig unterstütztes UI-Fenster** prüfen und **die tatsächliche Kodi-21-Konstruktorsignatur, Fokuslogik und XML-Control-Navigation** gegen strikte Tests absichern. Alternativ ist eine Skin-Widget-Lösung nur akzeptabel, wenn sie unter BINGIE MOD die volle gewünschte Fernbedienungsnavigation wirklich ermöglicht, ohne den globalen Skin zu überschreiben.

- **Keine Annahme**, dass ein normaler Kodi Directory-Folder eine horizontale Netflix-Rail rendert. Nach Auswahl der Lösung einen minimalen funktionierenden Fokus-/Navigations-Prototyp bauen und auf Android-TV zeigen.
- Shared, testbarer Daten-/Viewmodel-Layer `media_type=movie|series`, Stable IDs, Content-Type, Now/Resume/Favorites, Artwork-Metadaten, Group-Index und Viewport-Cache.
- Xtream-`get_vod_streams`, `get_vod_categories`, `get_vod_info`, `get_series`, `get_series_info` vorhandene APIs wiederverwenden; M3U/STB nur so weit unterstützen wie tatsächliche Metadaten vorhanden, klare Fallback-UIs. Keine unaufgeforderte Vollabfrage aller Detailmetadaten.
- Progressive Bilder: bounded Logo-/Poster-/Backdrop-Cache im privaten Add-on-Profil, verfügbare Quellbilder, leere/kaputte HTTP-Bilder robust behandeln; Ladeabbruch beim Gruppenwechsel. Memory-Budget bei tausenden Filmen/Serien.
- **Kein Netzwerk im UI-Key-Handler**, keine ungegrenzten synchronen Kodi-`xbmcgui`-Control-Objekte, 1000+-Poster-Katalog und 53.664 Live-Sender dürfen keinen Kodi-Hänger erzeugen.
- Metadaten/Logos von Xtream nur verwenden, soweit vom Account geliefert; Drittanbieter-Trailer/Artwork nur bei erlaubter Nutzung. Account-Passwörter maskieren, keine Stream-URLs/Provider-Token in Log/PR-Screenshots.
- Bestehende Kodi-Movie-/Episode-InfoTag-Felder sauber setzen (Art: poster, fanart, thumb; Titel, Laufzeit, Jahr, Genre, Rating). Unbekannte Werte **nicht erfinden**.
- Der getrennte [Lizenz-/Code-Herkunfts-Audit](CODE_ORIGIN_LICENSE_AUDIT_025_DE.md) bleibt offen; keine Entfernung von GPL-/Fork-Attribution.

## 6. Prüfbare Abnahmekriterien auf Android-TV

1. Startmenü hat weiterhin genau sechs Haupteinträge; `Filme` und `Serien` öffnen jeweils eine **Landingpage**, nicht sofort eine nackte Gruppenliste.
2. Obere `Neu hinzugefügt`-Reihe ist **horizontal rechts/links vollständig traversierbar** (lazy/virtuell geladen), erkennt neue Titel ohne erfundene Uploadzeiten; OK öffnet Film-/Seriendetail. Erklärter Direktstart-Shortcut funktioniert.
3. Untere `Filme / Kategorien`- bzw. `Serien / Kategorien`-Aktion führt zur **ersten aktivierten** Gruppe. Links zeigt Gruppen, Rechts schließt linke Gruppenleiste zugunsten einer **vollen Posteransicht**. Gruppenwechsel per Remote ohne verlorenen Fokus/fehlerhafte Sender.
4. Covergalerie zeigt Poster und auf Auswahl Titel, Laufzeit/Bewertung nur mit echten Providerwerten; scrollt auch bei mehreren tausend Einträgen flüssig.
5. Film-Detailseite zeigt Hintergrundbild/Poster/Text + Abspielen/Neu starten/Fortsetzen/Favorit an/aus/Trailer, abhängig von Daten und Capability. Kein „Fortsetzen“, wenn kein plausibler Bookmark existiert; Start/Stop speichert echten Fortschritt.
6. Serien-Detailseite mit Staffeln/Episoden, Start gewählter Episode, Favoriten, Fortsetzen/Gesehen-Status gemäß separate Serienfortschrittsspezifikation. Titel/Staffeln und Fortschritt bleiben nach Neustart stabil.
7. Fehlende oder defekte Bilder, ungültige Bewertungen, fehlende Trailer, unseekable Videos und fehlendes YouTube-Addon sauber behandeln – keine leeren Klicks oder imaginären Funktionen.
8. Fokusfolge `Neuheiten → Kategorien → Gruppen → Posterwand → Details → Wiedergabe → Zurück` auf echtem Kodi 21/Android vollständig testen, einschließlich zweitem Account, abgebrochener Wiedergabe, alter Favoritendateien und D-Pad-Repeat.
9. **Regression Freeze:** Live-TV-Infobar und dreistufige Steuerung von 0.1.26, Links-Navigation, EPG, Startkanal, GS Media Repository, BINGIE MOD und andere Add-ons bleiben intakt. Keine globalen Keymaps.

## 7. Priorisierung / PR-Schnitt für Codex

- **A:** Bestehender Hauptauftrag 0.1.27: sechs Punkte und kategorisierte Einstellungen als grundlegender Einstieg, keine Regression.
- **B (neuer Pflichtbaustein):** Film- und Serien-Landingpages, horizontaler Neuheitenbereich und linke Gruppen-/vollbreite Poster-Navigation, danach schöne Detailseiten (erst Movie, dann Series mit gemeinsamem UI-Baukasten).
- **C:** Media-Favoriten/Resume/Serienfortschritt als gesondert klar testbare Services; je nach Umfang separate PRs. **Nicht** die GUI mit nicht ausführbaren „Fortsetzen“-Buttons freigeben.
- **D:** Großer EPG und 7–10-Tage-Plan aus [Hauptauftrag](CODEX_AUFTRAG_027_STARTMENUE_SETTINGS_GRUPPEN_EPG_DE.md) und [#21](https://github.com/artattakk-creator/kodi-noodleprivate/issues/21). Wenn B–D zusammen zu umfangreich, eigenständige PRs + klarer Meilenstein-Status, nicht alles halb fertig in 0.1.27 deklarieren.

**Für jede Phase:** Branch ab aktuellem `main`, Kodi-21-GUI-Test/Stubs und echte Android-TV-Abnahmebeschreibung; CI und PR, **kein Merge/Update-Release ohne Freigabe des Nutzers**. Je Funktion getrennt `implementiert` / `CI bestanden` / `in main` / `Android geprüft` fortschreiben.

**GitHub-Umsetzungsticket:** [Issue #24 – Filme/Serien-UX](https://github.com/artattakk-creator/kodi-noodleprivate/issues/24). **Oberauftrag:** [Issue #23 – 0.1.27-Hauptmenü](https://github.com/artattakk-creator/kodi-noodleprivate/issues/23). Beide enthalten eine Entwicklungsanforderung, keinen bereits veröffentlichten Code.

## 8. Code-Fundstellen (bereits geprüft)

- `main.py::_recent_media`: verwendet `latest_media.recent_entries(...limit=50)`, liefert Kodi-Directory-Widgets und bei VOD **sofortigen Abspiel-Link**, bei Serie Staffelordner. Als Datenbasis brauchbar, aber **noch keine horizontale XCMate-Landingpage**.
- `latest_media.py`: Provider-`added/date_added`, danach ID-Erkennung erst ab zweitem erfolgreichem Katalogscan; nicht alle vorhandenen Titel bei Erstlauf fälschlich als neu markieren.
- `main.py::_vod_categories/_vod_list`, `_series_categories/_series_list/_series_seasons/_series_episodes`: bereits aktivierte Gruppen und Listen, aber **noch keine einklappbare Gruppenleiste oder Posterwand**.
- `metadata_views.py`: `provider_plot()`, `trailer_id()`, `youtube_kodi_url()`, `enrich()`; `main.py::_media_details` derzeit **nur Textviewer + optionaler Trailer**, nicht die gewünschte Detailoberfläche.
- `player.py::vod_list_item/series_list_item/episode_list_item` setzt einige Kodi Metadaten und Artwork; `_play_vod` und `_play_episode` existieren, Resume und Media-Favoriten verlangen getrennte Prüfung/Umsetzung.
- `main.py::_favourites` verarbeitet bisher primär `Channel`/URL-Favoriten; darf bei VOD-Favoriten nicht unkontrolliert wiederverwendet werden.
- `SERIES_PROGRESS_SPEC_DE.md`: sauberes, aber noch nicht implementiertes Modell für Watch-/Resume-/Auto-Next-Funktionen.
- `docs/XCMate/CODEX_AUFTRAG_027_STARTMENUE_SETTINGS_GRUPPEN_EPG_DE.md`: übergeordneter, auf GitHub verankerter 0.1.27-Auftrag; **dieser Zusatzauftrag ergänzt dessen §§1/4/6/7**.

## 9. Kopierfertiger Codex-Kurzauftrag

> Lies zuerst `docs/XCMate/CODEX_AUFTRAG_027_STARTMENUE_SETTINGS_GRUPPEN_EPG_DE.md` und danach diese verbindliche Zusatzdatei `docs/XCMate/CODEX_AUFTRAG_027_FILME_SERIEN_NETFLIX_NAV_DETAIL_DE.md`. Die sechs Startmenüpunkte bleiben, aber `Filme` und `Serien` sollen jeweils mit einer **horizontal scrollbaren Neuheitenreihe wie bei BINGIE MOD** starten (alle echten Neuheiten über virtuellen Cache durchscrollbar). Darunter führt `Filme/Kategorien` bzw. `Serien/Kategorien` in die erste aktivierte Gruppe; **links Gruppenleiste, rechts/zentral Poster**, Rechts klappt Gruppenleiste zugunsten eines vollflächigen Postergrids ein, Links am Rand zeigt Gruppen wieder. OK auf Cover öffnet eine **eigene große Detailseite mit Backdrop/Poster, Titel, Laufzeit/Bewertung/Beschreibung, Film abspielen/neustarten/fortsetzen, Favorit ein/aus, validiertem YouTube-Trailer**. Für Serien analog mit Staffeln, Episoden und progress-/resume-fähiger Folgenauswahl gemäß `SERIES_PROGRESS_SPEC_DE.md`. Vorhandene `latest_media.py`, `metadata_views.py`, `get_vod_info`, `get_series_info`, Gruppen und Kodi-Playerrouten nutzen; normale Kodi-Directories allein liefern das exakte Layout nicht, daher Kodi-Omega-`WindowXMLDialog`-Machbarkeit/Fokus prüfen und Test-Prototyp. Auf Android keine Kodi-Hänger, keine fiktiven Uploadzeiten oder Metadaten und keine Regression des funktionierenden 0.1.26-Live-TV. Branch, Tests, PR; **noch nicht nach main mergen**.
