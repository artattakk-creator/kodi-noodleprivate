# XCMate – vollständiges technisches Übergabedokument

**Stand:** 14.10.2026 · Bezug: XCMate **0.1.10** · GS Media Repository **1.7.0**  
**Repo:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Branch:** `main` · **Display-Name:** XCMate · **Add-on-ID unverändert:** `plugin.video.xtreammate`.

## 1. Mission und technische Grundlage

Android-Kodi-IPTV-Add-on für Xtream Codes sowie M3U und STB/Stalker; eigenes GS-Media-Branding und eine TV-taugliche, schnelle Fernbedienungsoberfläche. Projekt basiert auf der unabhängigen GPL-Fork-Linie des ursprünglichen mr-evil1 TiViMate Kodi. Upstream-Hinweise/Lizenz müssen erhalten bleiben.

Kodi bleibt Video-/Audio-Engine; kein neuer Decoder. XCMate implementiert Player-Steuerung, EPG, Listen/Widgets, Senderwechsel und Serienzustand über Kodi Python API. Zielplattform ist **Android-TV-Box mit Kodi und Titan BINGIE MOD**. Andere Kodi-Plattformen möglichst nicht beeinträchtigen.

## 2. Kritische Dateien und Releaseweg

- `src/plugin.video.xtreammate/addon.xml`: aktuell XCMate 0.1.9.
- `src/plugin.video.xtreammate/resources/lib/main.py`: Router, Startsender, Portale, Live/VOD/Serien, Widgets und EPG-Menüs.
- `src/plugin.video.xtreammate/resources/lib/player.py`: Kodi-Wiedergabe.
- `src/plugin.video.xtreammate/resources/lib/live_overlay.py`: TV-Vollbildoberfläche, Zappen, EPG, OSD.
- `src/plugin.video.xtreammate/resources/lib/remote_control.py`, `remote_bridge.py`, `remote_profiles.py`: Kodi-Keymap und lernbare Android-Tasten.
- `src/plugin.video.xtreammate/resources/lib/epg.py`, `epg_sources.py`, `epg_views.py`: XMLTV, zusätzliche Quellen, Kanalzuordnung, EPG-Anzeige.
- `src/plugin.video.xtreammate/resources/lib/xtream.py`: Xtream Client und lokale Katalog-Caches.
- `src/plugin.video.xtreammate/resources/lib/group_selection.py`: Aktivierung der Live-/VOD-/Seriengruppen.
- `src/plugin.video.xtreammate/resources/lib/portals.py`: persistente Portale.
- `src/plugin.video.xtreammate/resources/lib/startup_preferences.py`: Startgruppe, Startsender.
- `src/plugin.video.xtreammate/resources/lib/metadata_views.py` und `latest_media.py`: Film-/Serieninformationen, Trailer und neue Inhalte.
- `src/plugin.video.xtreammate/resources/settings.xml`: Einstellungen.
- `.github/workflows/publish.yml`, `tools/build_repository.py`: CI-Tests, Paketgenerierung, addons.xml.
- Distribution: `plugin.video.xtreammate/plugin.video.xtreammate-0.1.10.zip`; Katalog: `addons.xml`, Prüfsumme: `addons.xml.md5`.

**Release-Regel:** Quellcode → Tests → erfolgreicher GitHub Action Publish-Build → ZIP/Katalog prüfen → erst danach öffentlich als veröffentlicht melden. Repository-Version bleibt 1.7.0, solange das Repository-Add-on selbst nicht geändert werden muss.

## 3. Bereits programmiert – Gerätefunktion weiterhin prüfen

- Portalassistent, Verbindungstest, getrennter Import von Live-TV, Filmen und Serien.
- Gruppenverwaltung als Kodi-Checkbox-Mehrfachauswahl; Sammelaktionen und persistente Auswahl.
- Zwischengespeicherte Sender-, Film- und Serienkataloge; Aktualisierung im Hintergrund.
- Startsender und Startsendergruppe, optionales Autoplay; direkte Player-Wiedergabe im Stand 0.1.8.
- Vollbild-TV-Navigation: Links → Sender, erneut Links → Gruppen; Hoch/Runter zappen; OK → Player/weitere Funktionen; EPG. Seit 0.1.8 auch nativer Android-Tastenerkennungsweg und Lernmodus.
- XMLTV-EPG des Anbieters, zusätzliche XMLTV-URLs / lokale XML- und GZ-Dateien, mehrere Quellen, Prioritäten und manuelle Xtream-Senderzuordnung.
- „Jetzt/Danach“ aus EPG-Cache, EPG-Senderliste, BINGIE-MOD-Widgetordner je aktivierter Gruppe.
- „Neueste Filme“, „Neueste Serien“, Beschreibungen und Anbieter-Trailer über YouTube-Add-on (sofern gültige ID).
- Aufnahmeordner über Kodi-Dateiauswahl.

**Nicht als behoben behaupten:** Auf der echten Android-Box meldete der Anwender wiederholt eine leere Kodi-Ansicht beim Startsender sowie nicht ansprechende Links-/OK-/Hoch-/Runter-Tasten. 0.1.8 änderte die Architektur und 0.1.9 benannte um; ein erfolgreicher neuer Gerätetest wurde noch NICHT bestätigt. EPG-Anzeigen hängen von gelieferten Daten und Sender-ID-Mapping ab. BINGIE-MOD-Hover zeigt Metadaten nur, wenn das Skin-Layout sie rendert.

## 4. Aktuelle neue Anforderungen

**P0 – Android-Realtest und Fehlerbehebung:** Startsender direkt aus XCMate ohne leeres Verzeichnis starten; native Kodi-Action-IDs und Keymap mit TV-Dialog diagnostizieren; Kodi-Version, Fernbedienungs-IDs und Kodi-Log ohne Zugangsdaten dokumentieren; keine neue Release-Erfolgsaussage ohne Gerätetest.

**P1 – Serienfortschritt und Auto-Next:** Verbindliche Spezifikation in `SERIES_PROGRESS_SPEC_DE.md`. Diese Funktion ist am 14.10.2026 **geplant, NICHT implementiert**: pro Folge Wiedergabeposition speichern, bereits gesehene Folgen markieren, weiterschauen, optionale automatische nächste Folge (Reihenfolge Staffel/Folge).

**P1 – bestätigtes Space-Design:** Freigegeben ist das Bildkonzept mit monochromer Weltraumszene, Planet, Sternenhimmel und silbernem XCMate-Logo. Graues Standardtheme mit optionalen Farbakzenten und später einstellbarem Theme. Freigegebene Chat-Originaldateien `grafik.png` (Logo, 573×358) und `imagegen.png` (16:9-Space-Motiv, 1672×941); Quellen nur verwenden, wenn physisch vorhanden. Siehe `DESIGN_SYSTEM_DE.md`. **Artwork-Einbindung und Theme-Auswahl sind noch nicht als Release verifiziert.**

## 5. Daten und Migration

- Kodi-Daten bleiben unter `special://profile/addon_data/plugin.video.xtreammate/` und werden beim Namenswechsel NICHT verschoben.
- Eingeführte Dateien: `portals.json`, Gruppen-/EPG-/Fernbedienungskonfigurationen und lokale Caches (je nach Modul).
- Künftige Serienprogress-Datei separat, atomisch schreiben; siehe Spezifikation.
- Display-Name XCMate; **nicht** das Add-on in `plugin.video.xcmate` umbenennen, da sonst Updates, Kodi-Routen, Cache und Portalzugänge brechen könnten.
- Keine Xtream-Passwörter, API-Token, private EPG-URLs mit Query-Token oder reale Portalprofile in GitHub, Testlogs oder Übergabedokumenten ablegen.

## 6. Übergabe-Workflow für einen neuen Chat

Neuen Chat mit `NEW_CHAT_COPY_BLOCK_DE.md` beginnen. Zuerst aktuellen GitHub-`main`, `addon.xml`, ZIP, `addons.xml`, aktuellen Actions-Build und diese Dokumente lesen. Ein bereits besprochener Ansatz ist keine fertige Implementierung. Für jede neue Funktion erst Definition of Done + Tests, dann Code und Release. Neue Entscheidungen, Fehlerbefunde und Versionen hier nachtragen.

## 7. Entwicklung am 14.10.2026 – Kandidat 0.1.10

Ausgehend von `main` f74e647a4e15415f808d065790e88db45b473b21
wurde der separate Entwicklungsbranch
`fix/xcmate-0.1.10-android-p0` für die P0-Fehler angelegt.
`main` / Repository 1.7.0 bleiben bis zur erfolgreichen Veröffentlichung
die gültige Release-Quelle. Startsender-Menü wird über
`xbmcplugin.setResolvedUrl` aufgelöst, Autoplay über `RunPlugin`
mit separater direkter Player-Routine gestartet. OSD-OK löst die jeweils
markierte Funktion aus; „Weitere“ ist explizit erreichbar.
Automatisierte Kodi-API-Simulation ergänzt. **Ein Android-Erfolg ist
noch nicht nachgewiesen.** Einzelheiten: `ROADMAP_AND_QA_DE.md`.

## 8. TiviMate-5.3.3-Fernbedienung als Nutzerreferenz (14.10.2026)

Der Nutzer hat 10 Fotos seiner **tatsächlich eingestellten** TiviMate-Fernbedienung bereitgestellt. Die exakt sichtbaren Player- und EPG-Aktionen (kurzer/langer Tastendruck, Kontextwechsel) sowie sechs Suchoptionen stehen vollständig in
[`TIVIMATE_REMOTE_REFERENCE_2026-10-14_DE.md`](TIVIMATE_REMOTE_REFERENCE_2026-10-14_DE.md). Alle künftigen Einstellungsfotos ebenfalls kontextgenau indexieren.

Entwicklungsbranch: `feat/xcmate-tivimate-remote-profile` · Draft-PR [#3](https://github.com/artattakk-creator/kodi-noodleprivate/pull/3).
CI-Run [38557640506](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/38557640506) erfolgreich. Im PR liegen `tivimate_keys.py` (reine unabhängige Semantiktabellen) und Regressionstests. **Noch keine Kodi-Laufzeitintegration und keine neue Release-Version**; Add-on 0.1.10 bleibt unverändert. Unterschiedliche Kodi-/Android-Keycodes und Langdruck sowie echte EPG-/Preview-Anzeige müssen am Gerät geprüft werden. Nicht ungeprüft auf das Android-Gerät ausrollen.
