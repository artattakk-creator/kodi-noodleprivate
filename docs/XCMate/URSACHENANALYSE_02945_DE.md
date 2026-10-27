# XCMate 0.1.29.45 – technische Analyse

Entwicklung auf dem ausdrücklich freigegebenen bestehenden Branch `freeze/xcmate-02944-box-b-baseline-20261027`, kumulativ ab main `aace7f0f85cea8b9d132b0090563e28c9941bc4a`. Master #236 und Anhang vollständig berücksichtigt. Kein Main-Merge, produktiver Release oder Gerätezugriff. Alle .45-Android-Prüfungen NOT_TESTED.

## Widgets: Datenquelle und tatsächliche Skin-Schnittstelle

Die vorhandenen drei Plugin-Aktionsrouten und Portalparameter bleiben gültig. `widget_items45` erzeugt für Plugin-Aufrufe und Hintergrundframes denselben ListItem-Vertrag: konkrete eigene Klickroute, Portal-/Medien-ID, tatsächliche Metadaten, validierte lokale bzw. dynamische Bilder und lokales Jetzt/Danach. Maximal zwölf Startgruppensender und 24 eindeutige aktuelle Filme/Serien. Die bisherige zusätzliche „Alle anzeigen“-Posterattrappe entfällt; die allgemeinen Medienrouten bleiben erhalten. Keine Wiedergabe durch Fokus.

`app_services.refresh_local` veröffentlicht nach erfolgreicher vorhandener lokaler Katalog-/Artwork-Aufbereitung ein atomisches, begrenztes privates Frame. Fehlgeschlagene/leere Publikationen ersetzen keine gute Reihe. Keine neue Import-/Netzabfrage durch IR. Live-EPG kommt aus derselben lokalen Basis, mit bestehenden manuellen Zuordnungen. `widget_refresh45` validiert Portal, Policy, Alter, Klickroute und Datenform, wartet bei Wiedergabe/fremden Dialogen und ändert nur eine bereits in der eigenen Widget-Quelle benutzte Home-Reload-Property. Änderungen werden pro Hook zusammengefasst und auf höchstens einmal pro Minute begrenzt. Gleiche Daten verursachen keine Setter, echte EPG-Fortschrittsdaten höchstens minutenweise. Das sind Host-Schranken, keine gemessene Android-Latenzgarantie.

Wichtiger API-Nachweis: Bei nativen Kodi-21.3-Skincontainern liest die Python-ControlList nur ihre Python-`vecItems`, nicht die eigentliche DirectoryProvider-Liste. Native Container mit ListProvider ignorieren LABEL_BIND/RESET; `setStaticContent` würde den Provider/Klickvertrag ersetzen. Deshalb verwendet die endgültige Lösung keine vorgetäuschte Python-Neubindung, kein Container.Refresh, keine globalen Bibliotheksscans und keine Busy-Flags, die Reihen zwischenzeitlich leeren. Kodi behält den nativen DirectoryProvider und dessen Klick-/Fokusverhalten.

`widget_hooks45` prüft die generierte Skin-XML read-only auf die drei unveränderten eigenen Quellen und vorhandene dynamische Reload-Parameter. Erkannte bestehende `widgetreload`-Hooks können auch andere bereits daran gebundene Skinreihen aktualisieren; es werden keine fremden Konfigurationen umgeschrieben. Fehlt der Hook, ist automatische Sichtaktualisierung ausdrücklich **BLOCKED_NO_RELOAD_HOOK**, nicht PASS. Die tatsächliche XML von Box B wurde nicht gelesen. Die öffentliche BINGIE-Referenz ist 2.2.2; Box B 2.2.3 muss separat abgenommen werden.

## Optionaler Adapter: ausschließlich nach Benutzeraktion

Unter Widgets → optionaler BINGIE-Adapter bzw. Experimentell (PIN 6666) gibt es einen getrennten, reversiblen Opt-in. Kein Worker ruft ihn automatisch auf. Er akzeptiert ausschließlich installierte BINGIE-Version 2.2.3 mit passender addon.xml und kontrollierter generierter `script-skinshortcuts-includes.xml` innerhalb des Skinverzeichnisses. Keine Symlinks, DTDs, fremden Pfade oder unbeschränkten Dateien. Er ergänzt nur an den drei eigenen literalen Quellen einen quellenspezifischen dynamischen Reload-Parameter; gespeicherte Shortcut-URLs und alle anderen XML-Bytes bleiben identisch.

Zuerst entstehen private Originalkopie, Kandidat und SHA256-Manifest, ohne Skinänderung. Erst PIN plus gesonderte explizite Bestätigung erlaubt die atomare Änderung mit erneutem Originalhash unmittelbar vor Rename. Abbrechen und falsche PIN schreiben keinen Skin. Restore ist nur bei exakt unverändertem Kandidaten möglich; Skinupdate/sonstige Änderung werden nicht überschrieben. Erst nach dieser manuellen Bestätigung wird ReloadSkin ausgelöst, ohne Kodi-Neustart. Updatefestigkeit einer generierten Skin-Datei ist nicht garantiert: Regeneration kann den Adapter entfernen; erneut prüfen, nie automatisch wieder aufspielen. Hosttests verwenden ausschließlich künstliche Temp-Skins. **Adapter auf Box B NOT_TESTED / ohne ausdrückliche Aktion nicht angewandt.**

## Sieben Einstellungen und PIN

Die sieben Hauptbereiche verwenden dieselben bestehenden Kodi-Setting-IDs, Typen, Defaults, Optionswerte und Aktionsrouten. Alte Rubrik-URLs werden als sichere Aliase auf die neue Struktur geführt. Native experimentelle Felder sind nicht direkt sichtbar; eigener Optionseditor fragt vor jeder Änderung nochmals Speichern/Abbrechen. Keine Migration gespeicherter Werte.

`experimental45` schützt Root-Router und Unterrouter sowie direkte eigene Download-/Aufnahme-UI-Einstiege. Exakt vier Sechsen, kein 666, kein Query-Token, keine persistente Freischaltung. Wiederöffnen fragt erneut. Ein ContextVar gilt nur für den gerade autorisierten Aufruf; Exceptions stellen den Zustand wieder her. Positive Directory-Handles werden vor dem PIN-Dialog beendet und Popup-Aktionen mit Handle −1 ausgeführt, damit keine BusyDialog-Selbstblockade entsteht. Lösch-/Wartungsaktionen behalten zusätzliche Bestätigung. Die feste PIN ist eine Bedienungssperre und keine starke Authentifizierung.

## Einheitliche Menüicons

35 lokale originale transparente Glyphen, zentral nach Funktion zugeordnet. Native eigene Select-/Multiselect-Menüs verwenden ListItems mit kleinen gepolsterten Icons; eigene XML-Listen und Buttons erhalten unfokussierbare Bilddekorationen. Bestehende IDs, Trefferflächen und Fernbedienungslinks bleiben erhalten. Original-XCMate-Appicon und Quell-XML der Suchmaske bytegleich. Inhaltsposter und Senderlogos werden nicht durch Menüicons ersetzt. Keine Netzwerk-/Theme-Scans pro Menüzeile; Registry-Pfade sind rein lokal. Native Contextmenu, Tastatur, Dateiauswahl und Kodi-eigene Bestätigungsdialoge unterstützen keine eigenen Zeilenicons und bleiben Ausnahmen.

## Infobar nach dem neuesten Bildmuster

Der aktuelle ausdrückliche Wunsch „eins zu eins“ hat Vorrang vor den älteren Anhang-Richtwerten „schlanker/20px“. Deshalb setzt .45 die dreispaltige große Referenzleiste um: Logo/Name/Datum/Uhrzeit, Vorher/Jetzt/Danach mit grüner Zeitachse, rechts sechs technische Zellen. Panel bei 1920×1080: x26/y670/b1868/h362; proportional bei 1280×720. Sie ist gegenüber .44 höher. Kein falsches Versprechen einer gleichzeitig schlankeren Leiste.

Glasfläche, Rundungen, Abstände, Trennlinien, Badges und eigene Glyphen sind lokale PNGs. Laufendes Video bleibt dahinter; kein TV-Foto/Wasserzeichen wird mitgeliefert. Die Alpha-Glasfläche verwendet keine neue Live-Unschärfe oder Screenshots. Installierte registrierte Fonts werden anhand ihrer tatsächlich deklarierten Größe gewählt; exakte Skin-Fontdarstellung bleibt Android-Abnahme. Hostvorschauen sind echte Renderer-Geometrie mit Testdaten/Hostfonts, keine Gerätescreenshots und kein Nachweis von Bildgleichheit auf BINGIE. Lange Titel und andere Formate separat prüfen.

Technikwerte kommen unverändert aus `stream_details.py` und dessen vorhandener ownergebundener 2-Sekunden-Abtastung. Keine zusätzlichen Player-RPCs, HTTPs oder Poller. Nur tatsächliche Auflösung, Codec, Audio/Kanäle, Sprache, Untertitelstatus und fps; unbekannte Werte bleiben leer. Kein Dolby/Atmos oder Qualität aus Sendernamen. Zusätzlicher Vorher-Titel wird auf dem bestehenden EPG-Worker begrenzt read-only aus derselben Revision/manuellen Zuordnung gelesen, niemals im GUI. Fehlt echte Historie, bleibt Vorher leer. Uhr/Datum verwenden Kodi-Systeminformationen. Diffsetter verhindern identische Schreibvorgänge. Zweite Infobar, Transport, Back- und Player-Ownership bleiben bestehen.

## Bestandsschutz und Grenzen

Die vier kritischen Live-Stop-/Exit-Dateien, Streamdaten, Medienprogress/Autoplay/State/Sequence, EPG-Store/Publisher/Backup/Mapping und Portale sind bytegleich zur freigegebenen .44. Alle 1.652 vorhandenen Hosttestmethoden bleiben erhalten. Alte UI-Tests werden nur für ausdrücklich neue Menüs/Icons/PIN/Referenzabmessungen angepasst; neue Tests prüfen Ablehnung, Abbruch, Reentry und tatsächliche API-Grenzen. Historische Freezeverträge werden über exakt reviewbare Diffblöcke rückwärts geprüft, nicht pauschal übersprungen.

Keine Geräteinstallation, kein EPG-Refresh, keine Migration oder Datenlöschung. Vor einem Geräte-EPG-Refresh ist weiterhin eine verifizierte konsistente SQLite-Sicherung mit ausdrücklicher Einwilligung zwingend. #98/#161 vollständiger Quellchooser, Downloads/Aufnahmen, externe Speicher und weitere Roadmaparbeiten bleiben separat. Nicht durch Hosttests ersetzbar: tatsächliche BINGIE-Reload-/Fokusdarstellung, Android-Frameverhalten, reale Trackwerte, 20 neue Live-Back-Zyklen, Suche Film/Episode, Autoplay und Neustartpersistenz.

## Quellennachweise

- Kodi 21.3 Omega: https://github.com/xbmc/xbmc/tree/21.3-Omega ; `xbmc/interfaces/legacy/Control.cpp`, `Window.cpp`, `xbmc/guilib/GUIBaseContainer.cpp`, `xbmc/listproviders/DirectoryProvider.cpp` sowie Container-/Application-Builtins.
- BINGIE MOD omega, geprüfter öffentlicher Commit `1197a8e421b2836a1c18ea7223b5b6a1f4f2d7ff`: https://github.com/AchillesPunks/skin.titan.bingie.mod ; Font.xml, IncludesHomeWidgets.xml, shortcuts/template.xml, Home.xml und addon.xml (2.2.2).
- Auftrag: https://github.com/artattakk-creator/kodi-noodleprivate/issues/236 ; historische Android-Baseline #235. Keine privaten Kodi-Rohlogs veröffentlicht.
