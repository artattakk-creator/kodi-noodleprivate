# XCMate – vollständiges technisches Übergabedokument

**Stand:** 14.10.2026 · Bezug: XCMate **0.1.11** · GS Media Repository **1.7.0**  
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
- Distribution: `plugin.video.xtreammate/plugin.video.xtreammate-0.1.11.zip`; Katalog: `addons.xml`, Prüfsumme: `addons.xml.md5`.

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

## 9. Zweite Foto-Serie: TV-/EPG-/Film-Oberflächen (14.10.2026)

Weitere zehn Nutzerfotos dokumentieren Player-Farbtasten und neun konkret sichtbare UI-Zustände (OSD-Senderkarussell, erweiterte Player-Leiste, Senderliste mit Programmen/Video, Gruppenliste, EPG-Vollraster/mit Gruppen, kompakte/ausgeklappte Hauptnavigation und Filmkatalog). Vollständige strukturierte Beschreibung:
[`TIVIMATE_UI_SCREEN_REFERENCE_2026-10-14_DE.md`](TIVIMATE_UI_SCREEN_REFERENCE_2026-10-14_DE.md).
Player-Farbtasten: Rot/Grün = EPG-Overlay, Gelb = Info, Blau = Einstellungen; anders als im EPG.
Die pure-Python-Mappingdatei und Tests im Draft-PR #3 wurden angepasst. Weder EPG-Raster noch Vorschau noch neue Tastensteuerung sind bereits produktiv in XCMate aktiviert; XCMate 0.1.10 bleibt der Release.

## 10. Dritte Nutzer-Fotoserie: Einstellungen und Anbieter/EPG (14.10.2026)

Weitere zehn Fotos zeigen den Einstellungsdialog mit den neun Rubriken Allgemein,
Wiedergabelisten, EPG, Optik, Wiedergabe, Fernbedienung, Kindersicherung,
Sonstiges, Über. Details, nummerierter Bildindex und beobachtete Zustände:
[`TIVIMATE_SETTINGS_SCREEN_REFERENCE_2026-10-14_DE.md`](TIVIMATE_SETTINGS_SCREEN_REFERENCE_2026-10-14_DE.md).
Datensparsamer, maschinenlesbarer Dialogvertrag:
[`TIVIMATE_SETTINGS_CONTRACT_2026-10-14.json`](TIVIMATE_SETTINGS_CONTRACT_2026-10-14.json).

Fotografiert: Allgemein Autostart aus, Wake aus, letzter Sender beim Start ein,
Home-PiP aus, Exit-Doppelbestätigung aus; eigene Sicherungs-/Wiederherstellungsaktionen.
Playlist-Verwaltung pro Portal mit Name, Logo-Priorität, EPG-Zuordnungen, Archiv,
Xtream-Parametern, Gruppen, 24-h-Refresh. EPG: 7 Tage vergangenes Programm,
Programmbeschreibung speichern ein, 24-h-Refresh, Start-/Playlist-Trigger aus,
Quellenverwaltung/Status. Optik: Unterrubriken EPG/Player/Gruppen/Logos, Sprache
System, Schrift Mittel, beobachtet Dunkel/Blau und 50 % Transparenz.

**Datenschutz:** Die Fotos zeigen teilweise eine private XMLTV-URL mit
Benutzerkennung; diese, Playlistname und Zugangsdaten sind **nicht** in GitHub
übernommen. Keine Fotos veröffentlichen. XCMate-Vorgabe bleibt **Slate-Grau**
und unveränderte bestehende Portal-/EPG-Daten. **Noch kein Kodi-Feature-Release**.

## 11. Vierte TiviMate-Fotoserie – Wiedergabe / Kindersicherung / Sonstiges / Über (14.10.2026)

Weitere zehn Fotos dokumentieren die nun sichtbaren Menüs `Wiedergabe`,
`Kindersicherung`, `Sonstiges` mit `Suchen`, `Erinnerungen`, `Aufnahme`
und `VOD`, sowie `Über`. Bindende Detailreferenz:
[`TIVIMATE_SETTINGS_FOURTH_SERIES_2026-10-14_DE.md`](TIVIMATE_SETTINGS_FOURTH_SERIES_2026-10-14_DE.md).
Das maschinenlesbare Feldinventar
[`TIVIMATE_SETTINGS_CONTRACT_2026-10-14.json`](TIVIMATE_SETTINGS_CONTRACT_2026-10-14.json)
ist entsprechend erweitert und anonymisiert.

Sichtbar: Wiedergabepuffer klein, Hardware-Audio-/Video-Decoder,
AFR aus, Surround-Spur/Passthrough aus, externer Player nein;
Suche Verlauf/Favoriten zuerst ein, vergangene Sendungen aus;
Erinnerungen 0 Minuten/10 Sekunden/„Anschauen“; Aufnahme-Vor-/Nachlauf je 0;
Kindersicherung aus mit gesonderten PIN-Gates; VOD-Auto-Next-Funktion vorhanden.
Einige dunkle Schalter (Sprachsuche, Auto-Next, anonyme Statistiken)
sind fotografisch **nicht eindeutig ein/aus**, daher `null` statt Vermutung.
Private Kontodaten, Gerätename und Aufnahmepfad **nicht** ins GitHub übernommen.

**Status:** Erweiterung der Spezifikation – keine aktive Laufzeitintegration.
Kodi-Hardware-/Systemeinstellungen (Decoder, AFR, Passthrough) nicht ungefragt
global ändern. Eltern-PIN nur sicher implementieren, nicht kosmetisch. P0
Startsender/Android-Remote und Release-Version 0.1.10 bleiben unverändert.

## 12. P0 XCMate 0.1.11 veröffentlicht – Android Fernbedienung priorisiert (14.10.2026)

- Pull Request [#4](https://github.com/artattakk-creator/kodi-noodleprivate/pull/4) erfolgreich getestet und gemergt.
- PR-CI erfolgreich: [Run 38565230410](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/38565230410).
- Release-CI erfolgreich: [Run 38565339149](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/38565339149).
- In `main` veröffentlicht: `plugin.video.xtreammate/plugin.video.xtreammate-0.1.11.zip`, Datei mit 209252 Bytes; `addons.xml` enthält XCMate 0.1.11. `addons.xml.md5` stimmt unabhängig berechnet mit dem Katalog überein (`f9aa9e4f7d8ae26a0f1af4a3ada46316`). GS Media Repository-Add-on unverändert 1.7.0, alte 0.1.10-ZIP vorhanden.
- XCMate-verwaltete FullscreenVideo-Keymap wird beim ersten gültigen **XCMate-Xtream-Live-TV-Start** automatisch eingerichtet und bei Bedarf aktualisiert. Fremde Dateien werden nicht überschrieben, explizites Deaktivieren bleibt erhalten. Außerhalb aktiver XCMate-Live-Sessions routet die Bridge die Tasten zurück an Kodi.
- Der Kodi-`WindowDialog` verarbeitet zusätzlich native Android-Actions. Links Sender, erneut Links Gruppen, Hoch/Runter Senderwechsel (Hoch nächster/Runter vorheriger), Rechts vorheriger Sender, OK eigene Player-Leiste, Menü eigene Zusatzleiste, Zurück EPG/Schließen. Alte Kodi-eigene OSD-Öffnung wird damit für die übernommenen Tasten innerhalb XCMate umgangen. Volumentasten und andere Add-ons sollen unbeeinflusst bleiben.
- EPG in 0.1.11 zunächst cache-basierte Fokusliste; das vollständige horizontale TiviMate-EPG ist **nicht** implementiert. Langes Drücken hängt vom Android-KeyEvent-/Kodi-Keymap-Support ab.
- Diagnostics: `XtreamMate.NativeActionCount`, `XtreamMate.KeymapStatus`, `XtreamMate.OverlayStatus`, `XtreamMate.LastRemoteKey`, `XtreamMate.LastHandledKey`.
- **P0 noch nicht am Gerät bestätigt:** Alle API-/Mock-Tests und CI-Builds sind grün, echte Android-Box mit Titan BINGIE MOD steht aus. Vor dem Test **Kodi komplett neu starten**, damit der neue Kodi-Service geladen wird.
- Verbindliche Datenschutz-/Profilregel: keine Portal-/EPG-/Remote-Zugangsdaten oder Zuordnungen gelöscht oder migriert. Add-on-ID bleibt `plugin.video.xtreammate`.

### Prüfschritte auf der Android-Box

1. Reguläres Update im GS Media Repository auf XCMate **0.1.11**; Kodi vollständig beenden und neu starten.
2. Xtream-Live-TV starten (manuell und Auto-Startsender). **OK** muss die XCMate-Leiste zeigen, nicht Kodi-OSD.
3. Links → Sender, Links → Gruppen, Rechts → Senderliste, Hoch → nächster Sender, Runter → vorheriger, Rechts → zuletzt geschalteter Sender; Menü → XCMate-Zusatzfunktionen.
4. Zurück/Guide → EPG/Zurück, Stopp/Pause kontrollieren. Fremdes Kodi-Video starten und standardmäßige Fernbedienung dort prüfen.
5. Diagnose anzeigen und anonymisierte `kodi.log`-Fehlermeldungen nachreichen. Keine Android-Pass-Aussage ohne Protokoll.

## 13. XCMate 0.1.13 – Service-Heartbeat, Offline-Diagnose, manuelle Startanforderung (14.10.2026)

Der Nutzer zeigte ein tatsächliches Kodi-Fernbedienungsdiagnosefoto: Keymap AKTIV, aber zum Zeitpunkt der Aufnahme keine XCMate-Session, kein laufendes Video, keine TV-Einblendung und 0 native Tastenereignisse. **Dies belegt nicht automatisch, dass der Hintergrunddienst während des zuvor gespielten Streams ausgefallen war**, denn die Diagnose wurde nach der Wiedergabe geöffnet.

P0-Implementierung in PR [#6](https://github.com/artattakk-creator/kodi-noodleprivate/pull/6), CI [38579474322](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/38579474322) erfolgreich, Veröffentlichung [38579669527](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/38579669527) erfolgreich. **Stand 0.1.13** (Add-on-ID unverändert). ZIP `plugin.video.xtreammate/plugin.video.xtreammate-0.1.13.zip`, 213083 Bytes. Katalog enthält 0.1.13, Repository-Add-on bleibt 1.7.0. Prüfsumme `addons.xml.md5`: `6b2b1f8a08e3fbf578e5ca16a3eb30f3`.

- `resources/lib/service_health.py`: XCMate-Service-Heartbeat in Kodi Home Window, Zeitstempel, Schleifenzähler, Phase, letzte Fehlerklasse, letzte Video-/Session-, Overlay- und Fernbedienungs-Bridge-Beobachtung. Status: LÄUFT, KEIN AKTUELLES LEBENSZEICHEN, GESTOPPT, NICHT BESTÄTIGT.
- `service.py`: meldet Heartbeat periodisch auch bei ruhendem Player. Dienstbeobachtungen bleiben im Kodi-Window erhalten, wenn die Wiedergabe beendet wird; keine Provider-Credentials in den Werten.
- `main.py`: „TV-Fernbedienung: Diagnose“ zeigt Lebenszeichen und letzte Beobachtungen **ohne laufenden Stream**. Neue Menüaktion „XCMate-Hintergrunddienst prüfen / manuell starten“. Nur bei fehlendem frischem Heartbeat wird der bestehende Dienst über Kodi `RunScript(special://home/addons/plugin.video.xtreammate/service.py,manual)` best-effort angefordert, kein doppelter Start bei frischem Dienststatus, Wiederholungen kurzzeitig gesperrt; erfordert Bestätigung. Kein aktives „Dienst wurde gestartet“ behaupten, wenn kein Heartbeat zurückkommt.
- Tests: `tests/test_xcmate_service_health_p0.py` prüft Offlinestatus, Heartbeat/Timeout, Beobachtungsspeicher, Start-/Doppelstart-Schutz und UI-Anbindung. Insgesamt 116 GitHub-Unittests erfolgreich.
- P0 **Android-Gerätetest noch offen**. Bisherige 0.1.12 Session-Grace-Fixes bleiben integriert. Die UI-Referenzfotos/Optik bleiben P1; auch 0.1.13 beweist noch keine aktive eigene Fernbedienung.
- Test: 0.1.13 installieren, Kodi vollständig neu starten, im Portalmenü zunächst Hintergrunddienst prüfen. Bei „LÄUFT“ Testsender starten, bei unverändert defekter Fernbedienung Wiedergabe beenden und im normalen Menü erneut Diagnose öffnen (letzte Beobachtungen). Wenn kein aktuelles Lebenszeichen: Button betätigen, bestätigten Startversuch abwarten, Diagnose erneut prüfen und ggf. anonymisierte `kodi.log` prüfen. Keine sensiblen Portale, EPG-URLs oder Passwörter teilen.
