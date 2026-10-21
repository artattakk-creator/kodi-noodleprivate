> **Aktuell – 21.10.2026, P0-Hotfix 0.1.29.4:** Basis PR #52 / 0.1.29.3, neuer Branch `fix/xcmate-0294-setup-scan-save`. Worker-GUI-Pfad korrigiert, grafische Checkboxen und drei getrennte Listen, lange Scans ohne Gesamtdeadline, verifiziertes Speichern und Rollback nur neuer ID. **496/496 Tests**, 20 neue Regressionen; Android-/IR-/BINGIE-Abnahme und alleinige native Crashursache **offen**. Kein Merge/Release/Produktivindex-Update, PR #50/0.1.30 unberührt.
> [Vollständiger Prüfbericht und beide ZIPs](HOTFIX_0294_SETUP_SCAN_SAVE_DE.md) · [Testdaten/CI](TESTERGEBNISSE_0294_SETUP_SCAN_SAVE.json) · [Android-Test und manueller Onlinequellenweg](ANDROID_TESTPLAN_0294_SETUP_SCAN_SAVE_DE.md) · [vorher dokumentierte Ursachen](HOTFIX_0294_ROOT_CAUSES_DE.md).
> Alle älteren „Aktuell“-/Versions-/Freigabeangaben darunter sind historische Übergaben. Maßgeblich ist der oben verlinkte aktuelle Hotfix-Bericht; keine Android-Abnahme aus Cloudtests.

## Historische Übergaben

# XCMate – vollständiges technisches Übergabedokument

> **VERBINDLICHER INTEGRATIONSSTAND – 20.10.2026:** Ein vollständiger **RC 0.1.29.2** für das direkte Update von **0.1.28**, keine fünf Installationen.
> [Strukturierter Prüfbericht, Paket und Freigabeplan](INTEGRATIONSPRUEFUNG_RC_0292_DE.md) · [462/462 Integrationstests + 26/26 HTTP-/EPG-Tests](TESTERGEBNISSE_INTEGRATION_0292.json) · [Android-/Sicherungs-/Rollbackplan](ANDROID_TESTPLAN_UNIVERSAL_029_DE.md).
> Alle fünf Draft-PRs #39/#45/#46/#47/#48 offen; #48 enthält alle Vorgänger und die gezielten QA-Fixes. **Produktiv weiter 0.1.28, kein Main-Merge/Release. Android-Abnahme offen.**
> Frühere 448-/459-Testangaben und Paketprüfsummen sind historische Zwischenstände; für den jetzigen RC ausschließlich diesen Integrationsbericht verwenden.
> [CI erfolgreich / Publish übersprungen](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39449616224) · [CI-RC-Artefakt](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39449616224/artifacts/12278445261).


> **VERBINDLICHER STAND – 20.10.2026, universelle Weiterentwicklung:** Produktiv bleibt **0.1.28** (`main` `63b4cd6`).
> Geprüfter kumulativer **Testkandidat 0.1.29.2**, **448/448 Tests + 26/26 HTTP-/EPG-Tests**, Android-Abnahme **offen**.
> Getrennte gestapelte Draft-PRs: [A: Wiedergabestopp #45](https://github.com/artattakk-creator/kodi-noodleprivate/pull/45),
> [B: Bilder/Favoriten/Folgen #46](https://github.com/artattakk-creator/kodi-noodleprivate/pull/46),
> [C: aktive Gruppen/Senderliste #47](https://github.com/artattakk-creator/kodi-noodleprivate/pull/47),
> [D: universeller Setup/Editor #48](https://github.com/artattakk-creator/kodi-noodleprivate/pull/48), vorausgesetzt [Start-Hotfix #39](https://github.com/artattakk-creator/kodi-noodleprivate/pull/39).
> [Auftrag](CODEX_AUFTRAG_UNIVERSAL_029_DE.md) · [Bestandsanalyse/Dateiplan](ARCHITEKTUR_UNIVERSAL_029_DE.md) ·
> [Implementierung/Grenzen](PHASE_D_UNIVERSAL_SETUP_029_DE.md) · [Testnachweise](TESTERGEBNISSE_PHASE_D_029.json) ·
> [Android-Test, Test-ZIP und regulärer Update-/Rollbackweg](ANDROID_TESTPLAN_UNIVERSAL_029_DE.md).
> Branch `feat/xcmate-universal-setup`; A/B/C-CI erfolgreich. [D-Prüflauf](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39438464927) zunächst gestartet; verbindliches Endergebnis im Testbericht.
> **Kein Main-Merge, Tag, Release oder Produktivupdate.** Startup-Geräteursache #38 bleibt unbewiesen; kein Android-PASS aus Cloudtests ableiten.
> Ältere „AKTUELL“-Abschnitte darunter sind historische Nachweise und keine heutige Versions-/Freigabeangabe.


> **AKTUALISIERUNG 18.10.2026:** XCMate **0.1.22** wurde nach 180 bestandenen GitHub-CI-Tests via [PR #11](https://github.com/artattakk-creator/kodi-noodleprivate/pull/11) in `main` aufgenommen und über das GS-Media-Repository veröffentlicht. **Android-TV-Abnahme steht aus.** Dieses Dokument enthält darunter teilweise historische Versions-/Fehlerstände. Für den verbindlichen aktuellen Zustand zuerst [CODEX_STATUS_CURRENT_DE.md](CODEX_STATUS_CURRENT_DE.md) und [KODI21_FIX_022_DE.md](KODI21_FIX_022_DE.md) lesen.


**Stand:** 14.10.2026 · Bezug: XCMate **0.1.17** · GS Media Repository **1.7.0**  
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

## 14. XCMate 0.1.14: Wiederherstellung fehlender Live-Session während aktivem Video (14.10.2026)

**Vorliegender Android-Nachweis (realer Nutzer-Foto-Dialog):** Service `LÄUFT`,
`Dienstschleifen: 2134`, `Letzte Live-Beobachtung: Video JA / XCMate-Sitzung NEIN`.
Somit ist der Kodi-Dienst aktiv, aber es fehlt beim laufenden Video
die XCMate-Sitzung. Der eigene XCMate-`WindowDialog` benötigt diesen Marker;
ohne ihn startet das TV-Overlay nicht. Die genaue ursprüngliche Ursache
für den Verlust des Markers ist anhand dieses Fotos nicht abschließend geklärt.

**PR #7:** https://github.com/artattakk-creator/kodi-noodleprivate/pull/7
**CI PR:** https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/38587564991
**Release-CI:** https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/38587667244

**XCMate 0.1.14 veröffentlicht:** `plugin.video.xtreammate/plugin.video.xtreammate-0.1.14.zip` 215793 Bytes.
`addons.xml` deklariert 0.1.14, `addons.xml.md5` vorhanden.
Altes 0.1.13-Paket bleibt erhalten; Repository-Add-on weiterhin 1.7.0.

**Implementierung:** `resources/lib/live_recovery.py` gleicht den aktuellen
Kodi-`Player.getPlayingFile()`-Pfad ausschließlich lokal (ohne Netzwerk)
mit konfigurierten aktiven Xtream-Live-Sendern ab. Die exakte URL muss
inklusive Portaladresse, Nutzername, Passwort und Sender-ID passen,
oder eine eindeutige XCMate-`plugin://`-Live-Route sein.
Nur die daraus gewonnenen IDs, niemals Stream-URL, Credentials oder
private Portalmetadaten, gehen an `live_overlay.announce()`.
Der Hintergrunddienst probiert höchstens alle drei Sekunden, wenn
`Player.isPlayingVideo()` wahr ist, aber kein gültiger Sitzungsmarker
vorliegt. Fremde Kodi-Videos, unbekannte Portale, VOD und Serien
dürfen den XCMate-Player nicht übernehmen.
`TV-Fernbedienung: Diagnose` zeigt neu
`Live-Sitzungswiederherstellung`: Erfolg, kein exakter Match oder Fehlerklasse.

**P0 auf Android weiterhin offen:** Nach Update Kodi neu starten,
XCMate-WELT-Startsender laufen lassen; OK und Links prüfen; dann
Diagnose öffnen. Erwartung: `Dienststatus LÄUFT`,
`Letzte Live-Beobachtung Video JA / XCMate-Sitzung JA`,
`Live-Sitzungswiederherstellung XCMate-Live-Stream erkannt`,
`Letzte TV-Einblendung TV-Dialog gestartet`.
Nur wenn Kodi wirklich einen passenden Player-Pfad meldet und der
Dialog über der Android-Skin gerendert wird, ist die Fernbedienung
auch auf dem Gerät funktionsfähig. Keine funktionale Gerätetestfreigabe
ohne Nutzerbestätigung.

## 15. XCMate 0.1.15 – eigene Kodi-Popups und isolierter Remote-Test (14.10.2026)

**Aktueller veröffentlichter Stand:** `plugin.video.xtreammate-0.1.15.zip`
(219453 Bytes), GS Media Repository 1.7.0, unveränderte
`plugin.video.xtreammate`-Add-on-ID. PR
[#8](https://github.com/artattakk-creator/kodi-noodleprivate/pull/8)
mit erfolgreichen Python-/Kodi-API-Mocktests, erfolgreicher
[PR-CI 38592365190](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/38592365190)
und [Publish-CI 38592489957](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/38592489957).
`addons.xml` deklariert 0.1.15; vorherige ZIP bleibt erhalten.

**Neuer Menüpunkt im Xtream-Portal:**
„XCMate Popup- und Fernbedienungstest“, ohne gestartetes TV und ohne
laufenden Service-/LiveSession-Marker erreichbar. Er öffnet
`resources/lib/popup_probe.py` als eigenen fokussierbaren Kodi-`WindowDialog.doModal()`,
erfasst native Kodi-Action-IDs und Richtungstasten/OK/Zurück. Die zuletzt
empfangenen Ereignisse, der Fokus und der Popup-Status stehen anschließend
in „TV-Fernbedienung: Diagnose“. Keine Stream-Adressen oder Zugangsdaten.

**Auto-Live-Popup:** `LiveNavigator` beginnt im sichtbaren Zustand
`channels` statt unsichtbar `hidden`. Es zeigt sofort die Senderliste und
EPG-Kurzzeilen als linke Sidebar vor laufendem TV; nach 16s ohne
empfangene Taste verschwindet nur die Sidebar, nicht die Wiedergabe.
Der Dienst protokolliert `Auto-TV-Popup` und das Ergebnis von
`WindowDialog.onInit`. Das **unverkleinerte Live-Bild bleibt in der
nicht überlagerten Fläche sichtbar**, dies ist noch keine echte
skalierte Mini-TV-Vorschau.

**Verbindlicher Stufenplan:** `docs/XCMate/POPUP_UI_IMPLEMENTATION_PLAN_DE.md`.
Nach gesichertem Android-Gerätebeleg: 0.1.16 Sender/Gruppen,
0.1.17 EPG-Raster/Video-Machbarkeit, 0.1.18 Komfort,
0.1.19 Optik. **Noch kein Android-PASS.**

**Bitte Nutzer zuerst:** Kodi vollständig neu starten; im XCMate-Portal
ohne Video das neue Popup aufrufen, Links/Hoch/Runter/OK/Zurück prüfen und
Popup-Status danach über Diagnose fotografieren. Anschließend Startsender
testen: 16s sichtbare Senderliste? Meldung „Auto-TV-Popup“ und Session/
Overlay-Zeilen nachher kontrollieren. So den Kodi-Popup-Fokus unabhängig
vom TV-Laufzeitproblem isolieren.

## 16. Android P0: Autoplay blockiert Popup-Test → XCMate 0.1.16 (15.10.2026)

**Reale Nutzer-Rückmeldung zu 0.1.15:** Beim Aufruf des neuen
„XCMate Popup- und Fernbedienungstests“ wird sofort der konfigurierte
Startsender abgespielt. Die eigene GUI erscheint nicht; normale
Kodi-Playersteuerung blockiert erneut die benötigten Fernbedienungstasten.

**Bestätigter Codepfad:** `Router._root()` führt bei genau einem
aktiven Portal direkt nach `_show_portal_home(active[0])` ein
`_maybe_autoplay_start(active[0])` aus. Bei konfiguriertem
`autoplay_start=True` triggert das `RunPlugin(...play_start_direct...)`,
bevor eine Person auf dem Portalmenü den Popup-Test anwählen kann.

**P0-Release 0.1.16:**
- Pull Request [#9](https://github.com/artattakk-creator/kodi-noodleprivate/pull/9),
  erfolgreiche PR-CI [38708867907](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/38708867907)
  und Publish-CI [38708940824](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/38708940824).
- ZIP `plugin.video.xtreammate/plugin.video.xtreammate-0.1.16.zip`,
  221251 Bytes, Quellmanifest/Katalog beide 0.1.16;
  `addons.xml.md5` geprüft: `97b9a4e353d3f13427c0c83eb39e2f12`.
  Alte ZIP 0.1.15 erhalten.
- Neuer Kodi-Add-on-Schalter `autoplay_diagnostics_safe` (Standard `true`):
  unterbindet ausschließlich `_maybe_autoplay_start()` bei geöffnetem
  Add-on. Die Benutzereinstellung `autoplay_start` **im Portal wird nicht
  verändert**, Startsender-ID, Zugangsdaten, EPG, Tastenbelegung bleiben.
  `▶ Startsender abspielen` bleibt ausdrücklich manuell verfügbar.
- **Erste Portalmenüzeile:** `▶ XCMate Popup- und Fernbedienungstest (OHNE TV)`.
  Direkt darunter die bewusste Freigabe/Pausierung des Autostarts.
  Ein zweiter Einstieg liegt unter `Kodi → Add-ons → XCMate →
  Konfigurieren → XCMate: Popup- und Fernbedienungstest OHNE TV`
  und ist unabhängig von der Portalnavigation.
- Diagnose ergänzt `Autostart-Diagnosemodus: PAUSIERT/FREIGEGEBEN`.
  Die bestehenden Popup-/Service-/Sessiondiagnosen bleiben vorhanden.
- Tests `test_xcmate_safe_popup_entry_016.py` und aktualisierter
  `test_xcmate_p0_playback.py`: single portal root darf beim
  Safe-Modus nicht autonom starten, manueller Senderstart weiterhin
  möglich, explizite Autostart-Freigabe, Popup-Route und Einstellungen.

**Nächster Android-Nachweis:** Nach Update Kodi wirklich komplett beenden
und wieder öffnen. XCMate muss diesmal das Portalmenü anzeigen **ohne**
den Startsender abzuspielen. Oben den Popup-Test ausführen, echte
D-Pad-Tasten/OK/Zurück prüfen, dann Diagnosefoto.
Nur wenn dieses isolierte Popup funktioniert, weitere Live-TV-Diagnose.
Bei Nichtdarstellung den Kodi-Add-on-Einstellungs-Direkteinstieg testen;
Fehler dann in `popup_probe.py` / Fokus/GUI-Thread suchen, nicht
erneut Overlay-Layout vergrößern. Bis dahin bleibt P0 Android-Remote offen.

## 17. Android P0: Dialog nimmt 16 Tastendrücke an, aber wird nicht sichtbar → XCMate 0.1.17 (15.10.2026)

**Echte Android-Fotos 0.1.16:** Kodi-Hintergrunddienst `LÄUFT`,
letztes Lebenszeichen 0,1 s, 497 Loops, kein Dienstfehler,
`Autostart-Diagnosemodus: PAUSIERT`. Popup-Teststatus
`PER ZURÜCK GESCHLOSSEN`, `Popup-Ereignisse: 16`,
letzte Popup-Taste `Zurück (Navigation) (Kodi-ID 92, Code 61448)`,
Popup-Fokus `Schließen`. Nutzer: Richtungstasten und
Audio-/Fokusbewegung wahrnehmbar, aber **keine sichtbaren
Steuerelemente/Schaltflächen**. **Damit ist D-Pad-Dispatch zum
Addon-eigenen modalen Dialog nachgewiesen; die Darstellung nicht.**
`Native Tastenereignisse: 0` in der **separaten TV-Einblendung**
widerspricht dem nicht: bisher ohne laufendes Video getestet.
Noch kein EPG-/Live-Remote-Geräte-PASS.

**Technische Intervention 0.1.17:**
- Der zuvor programmgesteuert mit `ControlImage/ControlLabel/
  ControlButton` befüllte `xbmcgui.WindowDialog` wird im Testpfad
  durch ein **zweistufiges Testverfahren** ersetzt.
- Schritt 1: standardmäßiger, bereits auf dem Gerät sichtbarer
  `xbmcgui.Dialog().select()`, Titel
  „XCMate – SICHTBARER POPUP-TEST“, Optionen
  „Eigenes XCMate-XML-Fenster jetzt öffnen“ und
  „Nur Kodi-Popup bestätigen und zurück zum Menü“.
- Schritt 2: `xbmcgui.WindowXMLDialog('XCMatePopupTest.xml', addon_path,
  'Default', '720p')` mit Add-on-eigener Datei
  `resources/skins/Default/720p/XCMatePopupTest.xml`. Kodi-Standard-
  XML-Layout mit fest definierten Positionen/Labels,
  eigenen Hintergrundtexturen, zwei fokussierbaren Buttons
  (IDs 100/101), beschreibenden Labels (IDs 52/53) und
  D-Pad/OK/Back-Ereignisprotokoll.
- Bei XML-Load-Exception: nur Exception-Klasse, keine privaten
  Anbieteradressen/Passwörter, über **nativen Kodi-Dialog** anzeigen.
- Offline-„TV-Fernbedienung: Diagnose“ zeigt
  `Popup-Darstellungsweg`, `Popup-Status`, `Popup-Ereignisse`,
  `Popup-Letzte Taste`, `Popup-Fokus`.
- Autostart-Pause 0.1.16 bleibt unverändert aktiv; manuelle
  Senderwiedergabe verfügbar.

**GitHub:** PR [#10](https://github.com/artattakk-creator/kodi-noodleprivate/pull/10),
grüne PR-CI [38731122534](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/38731122534),
grüne Publikation [38731226443](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/38731226443).
ZIP `plugin.video.xtreammate/plugin.video.xtreammate-0.1.17.zip`
223470 Bytes; Source/Katalog jeweils 0.1.17;
`addons.xml.md5` vorhanden. Altes ZIP bleibt vorhanden.

**Abnahme:** Nach Update Kodi ganz neu starten; XCMate
öffnen, kein Autoplay. Popup-Test erste Zeile; **Kodi-nativen
Auswahldialog sichtbar?** Foto. Darin erste Option für
eigenes XML wählen; **XML-Dialog mit lesbaren Buttons?** Foto.
Dann Richtungstasten/OK/Zurück; nachher Offline-Diagnose
fotografieren. Wenn native Stufe sichtbar aber XML weiterhin
unsichtbar, `WindowXMLDialog`/Kodi-Skin-Font, Layout und
Kontrolltexturen untersuchen; auf keinen Fall zuerst Live-TV,
EPG oder Tastenprofile ändern. Keine Android-GUI-PASS-Aussage,
solange XML-Bild nicht real bestätigt ist.
