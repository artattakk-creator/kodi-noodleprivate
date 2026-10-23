# Android-Test 48 – Nachtrag Artwork-Downloadpause

## Gemeinsamer Stand und Schutz

Basis ist `main` 0.1.29.20, Commit `b6407e750470c2b8dc250e1030ee0fceb147791e`.
Android-Test 48 der .20: **10 PASS, 0 FAIL, 1 NOT_TESTED**. Bestätigt sind die tatsächlich geprüften Grundpfade, nicht alle EPG-Oberflächenanforderungen.
Nachtrag des Nutzers: **Kein erreichbarer Artwork-Downloadpause-Button vorhanden. Test E ist nicht durchführbar (BLOCKED_UI / NOT_TESTED)**. Der boolesche Backend-Schalter in der nativen `resources/settings.xml` ersetzt keinen sichtbaren Zugang im eigenen XCMate-Menü. `home_menu.settings(storage)` bietet Status, Wiederholung, DB-Zustand und weitere Speicherpunkte, aber keinen Pause-Schalter. Fast alle Bilder sind bereits heruntergeladen; kein Nachladen, Löschen oder Reset für diesen Test erforderlich. Dieser Menü-Nachtrag wird separat geführt und nicht in einen fachfremden Test-PR gemischt.

Beide Kandidaten stammen direkt von .20 und sind **unabhängig**. .21 enthält Autoplay, .22 ausschließlich den EPG-Fix und deshalb **kein .21-Autoplay**. Spätere gemeinsame Integration erst nach separater Android-Abnahme und ausdrücklicher Freigabe. Kein Merge, Release, Tag oder produktiver Repository-Index wird durch diese Arbeit ausgelöst. .20 und ihre ZIP-Datei bleiben unverändert. Keine Keymaps, Portale, Favoriten, Resume-, Gesehen-, Mapping-, XMLTV- oder Artwork-Daten löschen/zurücksetzen. Vorhandene privaten Provideradressen niemals in Testberichte kopieren.
