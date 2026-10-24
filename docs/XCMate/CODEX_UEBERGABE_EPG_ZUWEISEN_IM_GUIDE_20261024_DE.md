# XCMate – Codex-Übergabe: EPG-Zuweisung pro Sender direkt im großen Programmführer

**Datum:** 24.10.2026  
**Auftraggeberwunsch:** „Einige Sender haben nachweislich ein verfügbares EPG, aber XCMate zeigt keine Daten. Ich möchte im großen EPG den passenden EPG-Kanal bzw. die EPG-Quelle selbst zuweisen können.“  
**Repository:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Add-on:** `plugin.video.xtreammate`, **main bei Erstellung: 0.1.29.32**  
**Primär-Issue:** [#98 – EPG zuweisen mit Live-Vorschau ohne Speicher-Write](https://github.com/artattakk-creator/kodi-noodleprivate/issues/98); Roadmap [#143](https://github.com/artattakk-creator/kodi-noodleprivate/issues/143)  
**Abhängigkeit:** [#140 – globale EPG-/Sendersuche und Kodi-Busy-Dialog](https://github.com/artattakk-creator/kodi-noodleprivate/issues/140). Dessen bereits an Codex übergebener Suchfix ist **zuerst separat abzuschließen und auf Android abzunehmen**. **Den laufenden Suchfix NICHT durch diesen Auftrag ändern, verlängern, rebasen oder vermischen.** Danach #98 als eigenständiger kumulativer Draft-PR ab dann aktuellem, freigegebenem `main`.  
**Zielgerät:** Android TV 13 / RK3528 ARM32, Kodi 21.2 Omega, Titan BINGIE MOD, IR-Remote; Estuary als Vergleich.

## 1. Verifizierter Ist-Stand im .32-Code – wichtiger als ein neues Menü allein

1. `src/plugin.video.xtreammate/resources/lib/home_menu.py::settings(section='epg')`: **EPG-Quellen** verweist auf `epg_sources`.
2. `src/plugin.video.xtreammate/resources/lib/main.py::_epg_sources` öffnet `epg_sources.manage(portal)`.
3. `src/plugin.video.xtreammate/resources/lib/epg_sources.py::manage`: bestehende Option **„↔ Xtream-Sender einem XMLTV-Kanal zuordnen“**. `_choose_mapping` funktioniert derzeit **nur bei Xtream Codes**, nutzt den geladenen `available_channels(portal_id)`-Index, dann `set_mapping(portal_id,stream_id,epg_id)`. **Dieser Dialog schreibt direkt nach Auswahl dauerhaft**, bietet **keine Live-Vorschau**, verlangt ggf. anschließendes EPG-Update und steht nicht im großen EPG.
4. `src/plugin.video.xtreammate/resources/lib/guide_grid_window.py::_actions(channel_only=False)`: OK-/Sender-Untermenü mit Info/Wiedergabe/weiteren Aktionen. **„EPG zuweisen“ fehlt.** Es muss auch für einen Sender **ohne vorhandene Sendungen** erreichbar sein. `onClick(730..)` öffnet bereits Senderaktionen; `onAction` kennt weitere IR-Tasten. Vorhandenen Player-/Guide-Owner schützen.
5. **Kritisches Datenproblem bereits im Code:** `epg_sources.merge_sources()` vereinigt Quellen über den blanken `channel_id`; `index.update(channels)` überschreibt **gleichlautende Kanal-IDs verschiedener Quellen**, und die erste Programmequelle kann bei Kollision gewinnen. Persistenz `mappings[stream_id] = xmltv_id` kennt ebenfalls **keine eindeutige Quellidentität**. `guide_store.programmes` verwendet `(pid,cid,start,stop)` als Primärschlüssel und `source INTEGER` (Quellenreihenfolge), was bei Umordnung von Quellen nicht ohne weiteres stabile Quellidentität garantiert. **Nur einen Menüpunkt hinzufügen würde die eigentliche Nutzeranforderung daher NICHT erfüllen.**
6. Aktuell gibt es lokale XMLTV-Quellen/Pakete wie **EPGShare01**, **Kaimandura**, zusätzliche AT/CH/NL-Quellen und Anbieter-EPG. Externe Quellen können fehlen, veraltet oder deaktiviert sein. **Nur lokal tatsächlich bekannte Kanäle und Programme** als Vorschau verwenden; keine versteckten Netzwerkdownloads durch Cursorbewegungen.

## 2. Verbindlicher Bedienablauf

**A. Einstieg**
- XCMate → **großes horizontales EPG** → gewünschten Sender (auch ohne Programme) markieren → **OK** → im **Sender-Kontextmenü** den Punkt **„EPG zuweisen“** aufrufen. Langes OK kann zusätzlich angeboten werden, aber nur wenn zuverlässig auf dieser IR-Remote/WindowXML unterstützt; **nicht** als einziger Pfad und keine globale Kodi-Keymap.
- Beim Öffnen **keine Wiedergabe**, kein Startsender-/Gruppenwechsel, kein Home-/Player-Handoff; EPG-Zeitachse, Senderreihe, Scroll-/Gruppenposition und Fokus für Rollback merken.

**B. Kandidaten suchen**
- Dialog zeigt **Quellname + stabile Quell-ID/Anbieterkennzeichen + XMLTV-Kanalname + XMLTV-Kanal-ID**; gleiche XMLTV-IDs aus verschiedenen Quellen **als getrennte wählbare Kandidaten**.
- **Aktuell gespeicherte Zuordnung** deutlich hervorheben; zu markiertem Sender ähnliche Treffer zunächst oben, aber **niemals automatisch speichern**. Suche/Filter und IR-D-Pad bedienen auch bei >1000 Kanälen; geeignete begrenzte paginierte bzw. virtuelle Listen statt Einfrieren.
- Xtream-Provider-EPG ist als eigener Quellentyp einzubeziehen, falls die Programmidentität im Cache nachvollziehbar vorliegt; Quellen ohne lokalen Index als **„nicht geladen / kein lokaler Vorschau-Datensatz“** anzeigen und **nicht** mit fremden Sendungen auffüllen. Ggf. separater expliziter Button zur Quellenaktualisierung **außerhalb** der Preview, kein HTTP auf dem UI-Thread.

**C. Echte Live-Vorschau im vorhandenen großen EPG**
- Wählt der Benutzer Quell-Kanal-Kandidat A, ersetzt **nur im aktuell markierten Sender-Raster** ein temporärer, optisch gekennzeichneter Preview-Zustand die angezeigten Programmbalken: reale Titel, Start-/Endzeiten, Jetzt/Nächste, Zukunft innerhalb des geladenen Horizonts.
- Kandidat B kann unmittelbar ausgewählt werden; Vorschau wechselt zu B **ohne Persistenz**. Kein Rücksprung in den Guide und kein umständliches globales Aktivieren eines Anbieters. Keine abweichenden Kanaldaten erfinden.
- **NULL Programm-Daten** führt zu klar gekennzeichnetem „Für diese Quelle/den Zeitraum keine EPG-Daten“; keine stillschweigende Ersetzung mit Short-EPG einer anderen Quelle. Quellwechsel und Suche weiter bedienbar.
- Asynchrone **read-only** Worker mit Generation/Session-ID, bounded SQLite-Zeilenlimit, cancellable requests; verspätete Ergebnisse dürfen niemals eine neuere Auswahl oder ein geschlossenes Fenster überschreiben.

**D. Speichern, Abbrechen, Zurücksetzen**
- **Erst der explizite Button „Speichern“** persistiert atomar die **Zuordnung `(portal_id,stream_id) → (source_id,xmltv_channel_id)`** oder eine semantisch äquivalente eindeutige Struktur. Dabei **stabile Quell-IDs**, nicht nur nummerierte Quellenreihenfolge oder blanke XMLTV-ID, benutzen. Vor dem Schreiben prüfen, ob die Quelle weiterhin existiert, Kandidat zum selben Portal/Stream gehört und Write zulässig ist.
- Nach Save **genau eine** Senderzuordnung geändert; Guide, Now/Next, Suche und Zeitachsenansichten für **diesen Sender** konsistent aktualisieren, mit echtem Success-/Fehlerstatus. Andere Sender und Quellreihenfolge nicht verändern. Nach Kodi-Neustart identische manuelle Zuordnung.
- **Abbrechen / Zurück** verwirft alle Probezuordnungen und stellt sichtbare Programme, Quellbezug, Raster, Cursor-Zeit, gewählte Senderreihe, Gruppenposition und Fokus exakt wieder her. **Keine** Änderung von JSON, SQLite, Portal-/Gruppenkonfiguration, ursprünglichem Mapping, Quellpriorität oder Startsender durch Vorschau.
- „Zuordnung entfernen / Standard wiederherstellen“ als **explizite bestätigte Save-Aktion**, nicht als Nebenwirkung von Zurück oder Kandidatenwahl.
- Ältere String-`stream_id→epg_id`-Mappings **ohne Datenverlust rückwärtskompatibel lesen**. Unklare alte Quelle nicht stillschweigend einer neuen Source-ID zuordnen; Nutzer ggf. einmalig bestätigen. Migration erst nach gesichertem Backup und Test. Auf Upgrade kein Reset, kein Downgrade.

## 3. Datenarchitektur – ausdrücklich prüfen und korrigieren

- **Provider- und XMLTV-Quellen dürfen nicht auf dieselbe nackte Kanal-ID zusammenfallen.** Quelle und Kanal-ID als fachlichen Composite-Key über den **read-only Preview-Index, persistenten Mapping-Layer und EPG-Resolver** verfolgen.
- Prüfen, ob Cache und `guide_store` bei duplizierter ID tatsächlich **beide** unterschiedlichen Programmsätze bereitstellen. Falls der bisherige Merge bereits Source B verworfen hat, **einen separaten source-aware Kanal-/Programme-Index bzw. Cache** schaffen oder das Importmodell kontrolliert erweitern; **nicht** bloß `source INTEGER` in SQLite als garantiert stabil behaupten.
- Datenquelle der Vorschau vollständig vom persistierten Guide entkoppeln. Nie `set_mapping` oder `_save` in Candidate-Select, Cursor-/UI-Callbacks, Abbrechen oder Preview-Worker verwenden. Falls notwendige neuartige Migration: atomar, alter Cache/Schema lesbar, Integrationstest mit vorhandenem Nutzerprofil.
- `epg_sources.configuration`, `available_channels`, `merge_sources`, `set_mapping`, `guide_grid_data.page`, `guide_store`, `guide_views` und `epg_views` als Quellpunkte untersuchen. Namens-/Source-ID-Kollisionen sowie Fallback-/ShortEPG-Regeln bewusst modellieren.
- Auf dem D-Pad-/Owner-Thread **kein** großes XMLTV-Parsen, Netzwerk, EPG-Vollrefresh, synchrones SQL über Hunderttausende Events oder blockierende Datenmigration.

## 4. Pflicht-Teststrecke für Codex/Android

Automatisierte Tests vorbereiten und im Draft-PR dokumentieren. **Android-Status aller Gates bleibt NOT_TESTED bis echter Gerätetest.**

| ID | Gate / PASS nur wenn … |
| --- | --- |
| **MAP-01** | Sender **ohne EPG-Daten** im großen Guide markieren → OK → „EPG zuweisen“ öffnet IR-bedienbares Menü, kein TV-Autoplay. |
| **MAP-02** | Kanäle/Quellen aus EPGShare01, Kaimandura und Anbieter getrennt sichtbar; Liste performant auch mit >1000 Einträgen, Suchfeld/Filter arbeitet. |
| **MAP-03** | **Selbe XMLTV-ID in Quelle A und B**, unterschiedliche Sendungen; Preview A zeigt **nur A**, Preview B **nur B**, nicht gemischt. |
| **MAP-04** | **Drei Quellwechsel** mit Zwischen-Previews; danach **Abbrechen** – alter Guide/Zeitachse/Fokus identisch, JSON-/SQLite-Bytes unverändert. |
| **MAP-05** | Vorschau zeigt echte Jetzt-/Nächste-/Zukunft-Programme; Kandidat ohne Programme zeigt einen korrekten Leerzustand statt fremdes Short-EPG. |
| **MAP-06** | Nach bewusster Bestätigung ändert sich **genau 1 Mapping**; aktueller Sender aktualisiert, Now/Next konsistent, Neustart hält Zuordnung. |
| **MAP-07** | Weitere Sender/Quellen/Prioritäten/Portal-/Favoriten-/EPG-Profile bleiben unverändert; alter String-Mappingbestand kompatibel. |
| **MAP-08** | „Zuordnung entfernen / Standard“ nur nach expliziter Bestätigung, nie über Zurück/Kandidatenwechsel. |
| **MAP-09** | Quelle deaktiviert/fehlt, Alias-Kollision, DB_BUSY, Netzwerk offline, leere Indexdaten, schneller IR-Quellwechsel → kein Crash/Freeze/falscher Sender. |
| **MAP-10** | Großer Guide bleibt bei Save/Cancel im gleichen Gruppen-/Sender-/Zeitfenster; 20 D-Pad-/Back-/OK-Zyklen ohne Ghost-Fokus oder ungewollte Playback-Starts. |
| **MAP-11** | Kodi 21.2 Android RK3528 mit Titan BINGIE MOD und (wenn verfügbar) Estuary; tatsächlicher Player-/Owner-/Dialog-Lifecycle korrekt, keine #140-Regressions. |

**Effiziente Gerätereihenfolge:** zunächst MAP-01, MAP-03/04, MAP-06, dann Rest. Bewährte Basis-Smokes (Live-TV, Filmdetails, Seriendetails, Autoplay, Originalicon und Portal-/EPG-Profile) nur kurz regressionsprüfen. Keine pauschale 4-Stunden-Matrix.

## 5. Codex-Lieferumfang und Release-Schranken

1. **Nicht** in den derzeit beauftragten #140-Search-Busy-Fix integrieren. Erst nach dessen kumulativer Main-Integration und tatsächlicher Android-Abnahme neue Version ab dann aktuellen Stand planen. Keine fest angenommene Versionsnummer (`.33` ist für Suchfix reserviert bzw. nächster Kandidat, nicht für #98 beanspruchen).
2. Separater **Draft-PR #98** mit kommentiertem Architektur-/Migrationsplan, Code, Unit-/Integrationstests, ZIP + SHA256, Android-Checkliste MAP-01–11 und Changelog. Alle Android-Felder zunächst NOT_TESTED.
3. **Kein eigener Merge, Release, Tag, Repositoryindex-Publish oder Issue-Schluss.** Erst tatsächliche Android-Geräteprüfung und ausdrückliche Benutzerfreigabe.
4. Datenschutz: keine rohen IPTV-/XMLTV-/Provider-/SMB-URLs, Zugangsdaten oder personenbezogenen Logdaten nach GitHub; nur redigierte Phasencodes und technische Metadaten. Lizenz und sichere Quellenverarbeitung beachten.

**Abnahmesatz:** Nach Umsetzung kann der Nutzer **einen fehlenden EPG-Kanal unmittelbar im großen EPG aus mehreren Quellen eindeutig auswählen, in genau diesem Raster vergleichen und erst nach Bestätigung speichern – ohne andere Kanäle, Portale oder Daten zu verändern**.
