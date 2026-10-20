# Phase D – gemeinsamer Setup-Assistent und Quellenverwaltung

20.10.2026. Testkandidat **0.1.29.2**, Branch `feat/xcmate-universal-setup`,
[Draft-PR #48](https://github.com/artattakk-creator/kodi-noodleprivate/pull/48), auf Phase C / PR #47, B / #46, A / #45 und Start-Hotfix / #39.
Produktiv bleibt **0.1.28**, Main-Basis `63b4cd6`. Kein Merge, Tag oder Release.
[Vollständiger Auftrag](CODEX_AUFTRAG_UNIVERSAL_029_DE.md) ·
[Analyse, Architektur, Dateien und Abhängigkeiten](ARCHITEKTUR_UNIVERSAL_029_DE.md).

## Nachgewiesene Ursachen und Änderungen

Der bisherige Wizard rief ganze Xtream-/Stalker-Kataloge vor der Auswahl ab und
registrierte Accounts vor der nachträglichen Gruppenauswahl. Die M3U-URL-Prüfung
verwarf legitime Queryparameter. `iptv.load_m3u()` konnte M3U-Accounts zudem beim
Lesen still in Xtream umwandeln. Diese Umwandlung und der zweite unbenutzte
Portal-Add-Wizard sind entfernt; alle neuen Accounts verwenden denselben Ablauf.
Bestehende Settings-Migration und alte Wiedergabelesezeichen bleiben kompatibel.

`source_adapters.py` bietet Kategorien, Streaming-Import, sichere lokale Medien-IDs,
Play-Resolver, XMLTV, Kurz-EPG und Details. Konstruktoren kontaktieren keinen Provider.
Xtream nutzt den vorhandenen Streaming-Client. Stalker-Kataloge werden über
`stalker_stream.py` seitenweise gelesen, ohne frühere 50-Seiten-Grenze; JSON-Ende
und Metadaten werden vor Freigabe einer Kategorie geprüft. Bei ignoriertem
Kategorieparameter werden ausschließlich ausgewählte Kategorien persistiert.
Providerkommandos liegen im privaten vorhandenen Medienindex, nicht in Plugin-URLs.
Stalker-Logs enthalten feste Meldungen statt MAC, Tokens, Streamadressen oder
Exceptiontext. Optional explizit eingegebene Serien-/Geräte-ID wird beim Auth verwendet.

`setup_draft.py` legt eine neue UUID und ein privates Arbeitsverzeichnis an.
Kategorien/ausgewählte Inhalte/EPG werden dort vorbereitet. Ein Scan verändert keine
produktive Portalliste, Gruppenauswahl oder manuelle EPG-Zuordnung. Beim expliziten
Speichern werden ausschließlich Daten dieser neuen ID in kurzen Batches vorbereitet;
**die atomare Portalliste ist der letzte Veröffentlichungsschritt**. Bei Fehlern
Rollback ausschließlich dieser neuen ID. Ein unsicherer Readback darf keine eventuell
bereits erfolgreich veröffentlichte Konfiguration löschen. Bestehende Accounts bleiben
unverändert. Ein endlicher, wiedereintrittsfähiger Schreiblock begrenzt konkurrierende
Konfigurationsschreiber; `flock` ist für Android/Linux vorgesehen, Windows ungeprüft.

`source_sync.py`, `catalog_sync.py` und `app_services.py` verwenden denselben
versionierten `library_index.py`. Nur ausgewählte Kategorien synchronisieren;
kein automatischer Import neuer Länder. Bei alten Nicht-Xtream-Accounts ohne gespeicherte
Auswahl werden zunächst Kategorien ermittelt, Inhalte erst nach expliziter Auswahl
in den neuen Index übernommen. Vorhandene Legacy-Daten/Bookmarks werden nicht gelöscht.
Lokale Editoränderungen werden ohne Providerzugriff projiziert. Ein bestehender
Live-Navigator übernimmt später abgeschlossene Hintergrundimporte aus einem Worker.

## Benutzeroberfläche

1. Quelle und Name: Xtream, M3U-URL, Kodi-Dateiauswahl (intern/USB/SMB/NAS), Stalker.
   M3U-Queryparameter erhalten; Kennwort verdeckt. Kein HTTP-Uploadserver.
2. Native **WindowXML**-Oberfläche: Live-/Film-/Serientasten, Checkboxzeilen,
   Alle/Keine je Bereich. Zunächst **keine** Kategorie/EPG-Quelle vorausgewählt.
   Menü an einer M3U-Gruppe ordnet deren Medienart manuell zu.
   **Weiter befindet sich rechts unten**. Kodi verarbeitet Pfeile und OK nativ;
   `onAction` wiederholt diese Ereignisse nicht.
3. EPG-Auswahl: Anbieterfeed ausdrücklich aktivierbar, eingegebene XMLTV-Adresse,
   DE-/AT-/weitere mitgelieferte Presets oder eigene URL. Ohne Auswahl kein Import.
4. Weiter: ein abbrechbarer Worker importiert gewählte Kategorien. Angezeigt werden
   gelesene und **bestätigt gespeicherte** Werte, keine erfundenen Provider-Gesamtzahlen.
   Einzelne EPG-Fehler stehen in der Zusammenfassung; verfügbare Medien bleiben nutzbar.
5. Automatische Zusammenfassung, danach **Speichern**. Vorheriger Schritt erreichbar;
   Abbruch vor Save registriert keinen Account. Danach unmittelbar bestehendes Home;
   zusätzliche Datenaufträge sind lokal registriert und laufen im Hintergrund.

`XCMateSetup.xml`, `setup_window.py` und `playlist_editor.py` verwenden ausschließlich
Kodi-21-API-Argumente. Kein manuell ausgelöstes `WindowDialog.onInit()`.
Der neue XML-Assistent und Editor haben englische Basis-/deutsche Bundlestrings;
Kodi-Sprache und Skin werden nicht verändert. Vorhandene Legacy-Dialogtexte werden
nicht im Rahmen dieses PR vollständig neu übersetzt.

## Private M3U-Arbeitskopie und Editor

Unter **Einstellungen → Gruppen → Playlist-Editor** (M3U-Account):
100er-Seiten, Suche, Gruppen erstellen/umbenennen/Medienart ändern, Sender verschieben,
Name/Logo-URL/EPG-ID ändern, aktivieren/deaktivieren, Reihenfolge ändern, hinzufügen,
entfernen, Duplikate erkennen (erste 1000 Gruppen) und M3U8 exportieren.

`m3u_store.py` liest begrenzte 32-KiB-Blöcke, höchstens 256-KiB-Zeilen, UTF-8/BOM,
UTF-16 und CP1252-Fallback. Es hält keine vollständige Python-Playlist im RAM. Schreibblöcke werden zusätzlich zur
256er-Zeilengrenze bei etwa 1 MiB (plus einer einzelnen begrenzten Zeile) geleert;
eine Regression prüft sehr lange Streamadressen.
Basisgeneration und separate Overrides/custom-Einträge liegen in einer privaten
SQLite-Arbeitskopie. Das ist bewusst zusätzliche **Editierdatenhaltung**: der gemeinsame
Bibliotheksindex enthält nur normalisierte aktive Medien, nicht Original-URLs/Editorzustand.
Ein Source-Update ersetzt erst die vollständig geprüfte Basisgeneration und behält
Overrides. `tvg-id` bzw. bereinigte URI plus Duplikatvorkommen bilden stabile IDs;
bei mehreren identischen Provider-IDs bleibt deren Reihenfolge als Unterscheidung nötig.

Die Originaldatei wird nicht verändert; der Editor verhindert Export auf Original
oder interne Kompatibilitätskopie. Existierende andere Exportdateien verlangen
explizite Bestätigung; temporäre Datei/VFS-Rename statt Löschen des alten Exports.
Die Arbeitskopie funktioniert nach Entfernen des ursprünglichen USB-Playlistspeichers;
**Medien auf demselben entfernten USB/NAS werden dadurch nicht verfügbar**.
M3U-Serieneinträge ohne Staffelmetadaten bleiben direkt abspielbare einzelne Einträge.
Kein Erfinden von Staffeln/Episoden. Eigener Fortschritt/Favoriten bleiben möglich.

## Gemeinsame Medien-, Live- und EPG-Integration

`app_routes`, `media_window`, `media_data`, `media_progress` und `media_state` benutzen
für alle Quellen dieselben Rails, Detailseiten, Favoriten und Fortschrittsdaten.
Stalker-Folgen werden nur bei echten numerischen Staffel-/Folgenfeldern angeboten;
fehlende verwertbare Metadaten sind sichtbar. Wiedergabe validiert den lokalen Index
und vorher gespeicherte Episodendaten statt beliebige Nutzer-URLs zu übernehmen.

`source_live.py` erbt die bestehenden Kodi-Controls und Callbacklogik. Im bisherigen
`LiveNavigator` sind nur die explizite optionale Client-Injektion und die separat in
Phase C autorisierten Gruppen-/Listenstellen verändert. Der ursprüngliche Freeze-
Digest bleibt erhalten; ein AST-Test normalisiert exakt diese Zusatzstellen. Die
anderen fünf Remote-/Player-Dateien und sieben geschützten Router-Playmethoden sind
weiter unverändert geprüft. Xtream-Zap/OK/Back wird nicht neu implementiert.

M3U-/Stalker-Ownership verlangt das aktuelle Kodi-InfoTag mit PID/SID/Nonce/Datum;
keine unsichere URL-Heuristik für beliebige nichtnumerische Sender-IDs. Linkauflösung
läuft auf einem Worker. Erst der Dienst übernimmt das Ergebnis nach erneuter Prüfung
der Sitzung; verworfene/überholte Aufträge oder Fremdplayer lösen kein Play/Stop aus.
Menü/Back schließen weiterhin vorgesehene Overlayebenen, nicht pauschal den Stream.
Startsenderauswahl für Nicht-Xtream arbeitet lokal; **automatischer Start dieser
Quellen beim Add-on-Öffnen ist weiterhin nicht implementiert**, manuelles Home-Starten ja.
Globale Keymaps bleiben opt-in; BINGIE/andere Add-ons werden nicht geändert.

EPG bleibt im vorhandenen `guide_store`. Nur aktivierte Feeds/Sender importieren,
zehn Tage aufbewahren, Fehler behalten den alten Stand. Bereits vorhandene gültige
Guide-Abdeckung wird über Neustarts verwendet. Der kleine schnelle Snapshot kann
ablaufen, während SQLite noch gültige Tage enthält: `tv_data.GuideSnapshot` liest dann
nur die sichtbaren Sender im Worker aus SQLite; GUI-Ereignisse lesen weiterhin RAM.
Setup erstellt bei vorhandenem Guide zusätzlich den gemeinsamen schnellen Snapshot.
Stalker-Kurz-EPG nutzt die vorhandene servicegesteuerte sichtbare Priorität.
M3U hat keinen erfundenen Kurz-EPG-Endpunkt. Manuelle Senderzuordnungen bleiben erhalten.

## Prüfungen und Grenzen

**448/448 vollständige Tests in 64,884 s**, darunter 23 neue Quellen-/Navigationsregressionen; zusätzlich **26/26 HTTP-/EPG-Tests in 1,036 s** mit httpx/urllib.
Isolierter offizieller Build: **120 Dateien / 375.229 Bytes**, CRC/Syntax/jedes Quellbyte geprüft.
SHA256 `55b6b74e262b30cca37eaf8d251753e5cfb5fcfe06f3e13bd28d3452f56b73d6`.
[Installierbare Test-ZIP](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.2.zip) ·
[Maschineller Bericht](TESTERGEBNISSE_PHASE_D_029.json) · [Geräteplan](ANDROID_TESTPLAN_UNIVERSAL_029_DE.md).
Neue Regressionen prüfen echte SQLite, lokale und echte HTTP-M3U-Übertragung,
Kodi-WindowXML-Lebenszyklus sowie strikt modellierte native Omega-Dialogcallbacks.
Es werden keine fehlenden echten `WindowDialog.onInit()`-Callbacks vorgetäuscht.

Gemessen: **20.005 M3U-Einträge / 1.727.118 Bytes**, davon nach expliziter DE-Auswahl
**5.002** im Medienindex. XMLTV-Selektionstest: **400 Bytes übertragen, 2 Programme
geparst, 1 relevant gespeichert**. Das reduziert gespeicherte Inhalte; bei einem
Gesamtfeed wird keine reduzierte Netzwerkübertragung behauptet. Bestehende Großtests
prüfen zusätzlich >80 MiB HTTP, >200.000 Film-/Serientitel und >150.000 Programme.

Keine realen Providerzugänge, Android-Box, USB oder SMB-Hardware in der Cloud.
Stalker-Dialekte/Authentifizierung, tatsächliche saisonale Metadaten/Stream-Header,
IR-Tastencodes, XML-Fokus/Rendering, Hardware-Speicher und Player-Transitions müssen
am Gerät abgenommen werden. Die ursprüngliche Startup-Ursache #38 bleibt unbewiesen.
Themes/optionale Sprachpaketinstaller und komfortable selektive Bildbereinigung sind
nicht Bestandteil dieser Quellintegration. Kein Android-PASS allein aus Cloudtests.
