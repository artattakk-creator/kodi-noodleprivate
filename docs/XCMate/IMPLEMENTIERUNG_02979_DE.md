# XCMate 0.1.29.79 – Ursachen, Änderungen und Grenzen

Stand: 08.11.2026. Master #387; Referenzen #385, #366, #367, #368, #380.
Basis: `3b2a52859feda4d9413231bb4d3cf4121b1f1d67` (main, .78).
Branch: `fix/xcmate-02979-native-widget-cache`.

## Nachgewiesene Pfade

Die im Übergabedokument anonymisiert ausgewerteten Android-.78-Logs bleiben FAIL. Die vier privaten Dateien wurden hier nicht erneut bereitgestellt; die Implementierung stützt sich auf die dokumentierte Forensik und reproduzierbare Code-/Hostbefunde. Keine privaten Rohlogs werden übernommen.

1. `widget_refs74` hat eine kurze Lease für öffentliche Bildreferenzen. Nach einem Prozessneustart kann diese abgelaufen sein, obwohl Kodi das Bild bereits erfolgreich in Thumbnails gespeichert hat. `.79` ergänzt eine exakte, profil-/anbieter-/artikel-/quellengebundene Wiederauffindung **vorhandener** Kodi-Texturen. Der Worker fragt `Textures.GetTextures` ab, prüft lokalen Pfad, vollständige Bilddekodierung, Größe, Dateistempel und SHA256. Kodis reale `image://`-Darstellung enthält auch kleingeschriebene Prozentkodierung der HTTP-Optionen; dies ist eigens abgesichert. Ein privates, begrenztes Metadatenjournal verweist auf diese Dateien. Kein neuer Bildarchiv-Modus, keine Cache-Löschung, keine Kopie des gesamten Texturecache. Dynamische Profile bleiben dynamisch; interne/externe Bestandsprofile bleiben auf ihrem bisherigen Pfad.
2. Ein unveränderter Widget-Frame kehrte bisher vor der erneuten Anmeldung bei `widget_notice46` zurück. Nach Interpreter-Neustart fehlte damit die Bekanntmachung an den gespeicherten Reload-Hook. `.79` meldet unveränderte gültige Frames erneut an, ohne ihre Dateien umzuschreiben.
3. Vorhandene Hero-Controls bestätigten bisher Runtime-Bereitschaft, obwohl gerade reparierte native Consumer-Hooks noch nicht geladen waren. `.79` transportiert den tatsächlichen Änderungszustand und verlangt danach den bestehenden kontrollierten Skin-Reload. Persönliche SkinShortcuts werden dabei nicht neu aufgebaut. Die vorhandene idempotente, gesicherte Reparatur betrifft ausschließlich generierte eigene Hook-Consumer.
4. Die zusätzliche `Directory79`-Generation wird an den **wirklich ausgegebenen** Kodi-Items gesetzt. Nur dieselbe Generation im aktiven sichtbaren Container zählt als Reload-ACK. Zählwerte allein, fremde oder alte Einträge sowie vorhandene XML-Dateien zählen nicht. Fehlende Controls, verborgene Reihen und leere Controls werden unterschieden. Höchstens zwei gezielte Hook-Wiederholungen je Generation; keine Fokusübernahme und kein Player-Eingriff. Worker-Inventarisierung fragt keine GUI-Controls ab.
5. Unterschiedliche Fokus-/Senderbatches konnten dieselben fehlenden EPG-Daten immer wieder lesen. `.79` ergänzt kanalbezogene 15/30/60-Sekunden-Leases mit begrenztem Speicher. Guide-/WAL- und Mappingänderungen invalidieren sie; reale Programmgrenzen bleiben wirksam. Explizite `tvg_id`/`xmltv_id` aus Provider-Dictionaries werden berücksichtigt, ohne ähnliche Sendernamen zusammenzuführen. Manuelle Zuweisungen haben weiterhin Vorrang.
6. Die Kodi-Bibliotheksdiagnose prüft ausschließlich lesend bekannte Tabellen, gespeicherte Schemaversion, Integrität und Kompilierbarkeit der drei Views. Ein vorhandener, aber kaputter View ist kein READY. Ohne die konkrete Android-Datenbank ist die Ursache fehlender Views weiterhin offen. Keine erfundenen Views, kein DB-Schreibzugriff, keine Migration.

## Bestandsschutz und Aussagegrenzen

Die bisherigen Source-Dateien und Testmethoden sind über einen exakten .78-Baseline-Vertrag geschützt; nur die dokumentierten Hooks werden normalisiert. Neue Tests prüfen ihr tatsächliches Verhalten zusätzlich. Installer 0.5.26, veröffentlichte .78-Kataloge und Pilot-Pakete bleiben byteidentisch. Widget-Routen, Klickziele, gespeicherte Benutzeranordnung, fremde Reihen und „Neu im Kino“ werden erhalten. Ein beschädigtes `videodb://`-Backend kann durch die Diagnose nicht automatisch wieder funktionsfähig werden.

TMDB-Einstellungen und Tokenverwaltung werden nicht verändert. Programme verwenden weiterhin die vorhandene XMLTV-/Provider-/TMDB-/TVMaze-Kette und deren Nutzerfreigaben. EPG-Bild- und Player-Exit-Implementierung aus .78 wird erhalten und erneut regressionsgeprüft; kein weiterer Player-Rewrite.

`TEXTURE_REQUESTED` beweist eine gebundene Artadresse, kein Pixel. `decode_verified=-1` bleibt unbestätigt, kein synthetischer Fehler-/Erfolgswert. Die sichtbare Textur wird im nativen Test separat durch tatsächliche Kodi-Screenshots geprüft. Eine solche Linux-Prüfung ersetzt keine Android-Prüfung. Bis zum realen Gerätetest: **ANDROID_NOT_TESTED** für jede neue .79-Funktion; .78-Fehler bleiben historisch FAIL.

## Veröffentlichung

Dieser Build ist ein prüfbarer Kandidat auf einem separaten Branch. Kein Merge und keine Änderung regulärer/Pilot-/NeoDark3-Updatekanäle. Die Freigabe von #385 galt ausdrücklich nur für .78. Vor einem .79-Merge und einer Veröffentlichung ist eine neue Freigabe erforderlich.
