# XCMate 0.1.29.45 – vollständige Android-Abnahme Box B

**Alle .45-Gerätefälle NOT_TESTED.** Box B: Kodi 21.3, RK3528 ARM32, Titan BINGIE MOD 2.2.3. Box A ausgeschlossen. Aktueller .44-Befund: mehr als 20 erfolgreiche Live-Backs im Alltag, Modus `live_exit_fullscreen42=EIN`, subjektiv schneller, mindestens ein erfolgreicher Suchtrefferstart; Navigation/Rail/Gruppen und verschwundene Ghosttexte vorläufig positiv. Das sind keine einzeln gestoppten 20 .45-Zyklen und keine vollständige .44-Abnahme. Alte .43-FAIL werden nicht als neue .44/.45-Fehler übernommen.

## Vorbereitung und Stop-Gates

1. Erst PR und Paket/SHA prüfen, dann nur nach Nutzerfreigabe auf Box B als reguläres ZIP-Update über .44. Keine automatische Installation, Deinstallation, Downgrade, Profil-/Cache-/DB-/Bildlöschung oder neue USB-/SMB-/Migrationstests. Dynamischer Artworkmodus und alle bisherigen Einstellungen erhalten.
2. Modus EIN kontrollieren, nicht OFF ausprobieren. Startsender → **einmal** Live-TV-Back: Bild/Ton enden, GUI bedienbar. Bei Freeze/STOP_TIMEOUT sofort abbrechen, keine wiederholten Stop-/Recoverybefehle erzwingen. Erst nach PASS Film-Back, dann fünf und 20 weitere Livezyklen.
3. EPG zunächst ausschließlich vorhandene Daten ansehen. **Vor jedem manuellen Refresh/Import** verifizierte konsistente Sicherung über bestehende Backup-API, SHA/Größe/Manifest und ausdrückliche Einwilligung. Keine einzelne aktive DB/WAL/SHM kopieren oder austauschen. Ohne dieses Gate Refresh BLOCKED. Die Sicherung selbst startet keinen Refresh. Kein Test darf bestehende Daten absichtlich beschädigen.
4. Vorhandene drei BINGIE-Widgetquellen/Skinsettings privat vergleichen. Keinen neuen Widgeteintrag anlegen. Zuerst unveränderte Einrichtung testen. Fehlender Reload-Hook = BLOCKED, nicht durch manuelle Neubindung als PASS kaschieren. Optionaler Adapter ist ein gesonderter, ausdrücklich bestätigter Test; bei fehlender Freigabe NOT_TESTED lassen.

## Neue .45-Pflichtfälle

| Fall | Ausführung und erwartetes Ergebnis | Box B .45 |
|---|---|---|
| W45-01 | Bestehende Live/Film/Serienreihen nach Update ohne Neubindung; unveränderte gespeicherte URLs und Portalzuordnung. Bis12 echte Startgruppensender, bis24 unterschiedliche aktuelle Filme/Serien, keine All-Films-Posterattrappe. | NOT_TESTED |
| W45-02 | Mindestens drei Logos, drei Filmposter, zwei Seriencover mit realen Metadaten ansehen; bekannte gültige Providerbilder statt generischer Platzhalter. Logo proportional; native Skin-Layoutgrenzen dokumentieren. | NOT_TESTED |
| W45-03 | Livekachel → exakt Sender, Film → exakt Film, Serie → exakt Serie/Staffeln; kein Fokus-Autoplay, Rootumweg oder fremdes Portal. Back stellt bedienbare Voransicht her. | NOT_TESTED |
| W45-04 | Sender/Now/Next/Zeiten/Progress im Widget mit Mini/Info/großem EPG gleicher Sender/Uhrzeit vergleichen. Manuelle Zuordnung gewinnt. Kein EPG erfinden. | NOT_TESTED |
| W45-05 | Natürliche erfolgreiche lokale neue Kataloggeneration abwarten. Neues Medium muss ohne Neubinden/Kodi-Neustart nach Hintergrundaktualisierung erscheinen; Ereigniszeit→sichtbare Reihe messen. Fehlender Skin-Hook ausdrücklich BLOCKED_NO_RELOAD_HOOK. | NOT_TESTED |
| W45-06 | EPG-/Logoänderung nach erfolgreicher vorhandener Hintergrundpublikation; keine leere Zwischenliste, richtige Auswahl, kein periodisches Flackern. Mindestens15min beobachten und20Fokuswechsel. Keine IR-Netzabfrage. | NOT_TESTED |
| W45-07 | Kalt/Warm je5 Stichproben bis erste bedienbare Reihe/Poster/EPG separat messen, Stichproben und p50/p95 notieren. Hauptstartgruppe gesondert. | NOT_TESTED |
| W45-08 | Nur falls ausdrücklich gewünscht: Einstellungen→Darstellung→Widgets, Adaptervorprüfung. Ohne Änderung/bei Cancel Skinhash und Shortcuts identisch. Unsupported-Version/kein Hook korrekt melden. | NOT_TESTED |
| W45-09 | Nur nach eigener Freigabe/PIN/zweiter Bestätigung: privates Original/Kandidat/SHA-Manifest prüfen, Adapter anwenden, ReloadSkin, W45-05 erneut. Gespeicherte Shortcuts unverändert. Sonstige Skinänderung darf Restore nicht überschreiben. Ohne ausdrücklichen Opt-in BLOCKED. | NOT_TESTED |
| W45-10 | Nur falls Adapter tatsächlich angewandt: Rücknahme bewusst bestätigen, Originalhash gleich, keine Daten-/Skinsettingsverluste. Kein Test künstlicher Skinupdates auf produktivem Gerät. | NOT_TESTED |
| S45-01 | Genau7 Rubriken: Account & Portale, Live-TV & Sender, EPG, Medien & Wiedergabe, Darstellung & Bedienung, System & Speicher, Experimentell. Unterfunktionen sinnvoll erreichbar. | NOT_TESTED |
| S45-02 | Experimentell mit6666 öffnen; mit666, anderer PIN und Abbrechen kein Zugriff; zurück nach Einstellungen. | NOT_TESTED |
| S45-03 | Nach Verlassen erneut eintreten: erneute PIN. Direkte Aufnahme-/Download-/Diagnoseroute ohne PIN kein Zugriff. Keine Query-/persistente Freischaltung. | NOT_TESTED |
| S45-04 | Normale gespeicherte Sprache/Player/Startgruppe/Portale unverändert. Optionseditor Abbrechen schreibt nichts, explizites Speichern nur gewählten Wert. Keine riskanten Werte probeweise ändern. | NOT_TESTED |
| S45-05 | Experimentell-Untergruppen und bisherige Aktionsaliase erreichbar; separate Bestätigung für risikoreiche Aktion durch Abbrechen prüfen, keine Löschung ausführen. | NOT_TESTED |
| M45-01 | Alle Menüoberflächen anhand MENU_MATRIX_02945_DE.md prüfen: kleines passendes Icon links/Text rechts, keine zusätzliche Fokusstation, kein Platzhalter bei Medienbildern. Native Kodi-Ausnahmen getrennt. | NOT_TESTED |
| M45-02 | Ganze Fernbedienungsstrecke Home→Settings→Unterrubriken→Details→linkes Untermenü→Guidegruppen/Tools→Back; keine toten Controls/Unsichtbarfokus. | NOT_TESTED |
| I45-01 | 1.OK: neue dreispaltige Glasleiste direkt mit Nutzerbild vergleichen: Logo/Name/Datum/Uhr, Vorher/Jetzt/Danach, grüne Zeitachse, rechte2×3Technikzellen. Kein fremdes TV-Foto/Wasserzeichen. Screenshot privat abgleichen. | NOT_TESTED |
| I45-02 | Reales1080p und falls ohne riskante Umschaltung verfügbar720p: Rundungen/Abstände/Fonts/Lesbarkeit, lange Titel, Uhr/Zeiten und Clipping. Hostbilder sind keine Gerätedarstellung. | NOT_TESTED |
| I45-03 | Tatsächliche Auflösung/Codec/Audio/Kanäle/Sprache/UT/fps mit Kodi vergleichen. Unbekannt leer, keine alten Trackwerte; realer Trackwechsel falls vorhanden. Kein Atmos erfinden. | NOT_TESTED |
| I45-04 | Echte Vorhersendung nur bei gespeicherter Historie; Now/Next aus gleicher Basis. Uhren-/EPG-Fortschritt folgt realer Zeit, kein GUI-Hänger. | NOT_TESTED |
| I45-05 | 1.OK→2.OK→Transportbuttons→Back, Links Mini→Gruppen→Rail; nach20Öffnen/Schließen keine verlorenen Badges, Geistertexte, doppelte Fokusrahmen oder neue Latenz. | NOT_TESTED |
| P45-01 | Vorhandenes EPG read-only gestern/vorgestern bis−7 im großen EPG und Mini; echte verfügbare Historie vs leer korrekt. Kein Refresh vor verifiziertem Sicherungsgate. | NOT_TESTED |
| P45-02 | Suchtrefferfilm UND Serie→Episode starten/Back; gleiche Query/Tab/Fokus und richtiger Player. Frühere Einzelbeobachtung nicht als beide PASS übernehmen. | NOT_TESTED |
| P45-03 | Cover/Metadaten manuell suchen→echte Vorschau→gezielt übernehmen→speichern, nach normalem Neustart wiederfinden. Ohne echten Kandidaten BLOCKED. Keine globalen Jobs/Cache löschen. | NOT_TESTED |
| P45-04 | Resume, natürliches Autoplay inklusive Staffelwechsel, bewusster Stop ohne Autoplay. Portale/Favs/Gruppen/EPG-Zuordnungen/Cover/IR nach normalem Neustart erhalten. | NOT_TESTED |

## Bisherige vollständige Funktionstrecke erneut

Jede Zeile ist eine eigenständige neue Prüfung. Frühere Bewertungen stehen weiterhin unverändert in der .43/.44-Dokumentation; sie gelten nicht automatisch für .45. Visuelle Mikrozeilenanforderungen von .44 werden durch I45 und das neue Referenzbild ersetzt.

| Fall | Prüfung / Erwartung | Box B .45 |
|---|---|---|
| A1 | Version/Kompatibilitätsmodus EIN | NOT_TESTED |
| A2 | Startsender | NOT_TESTED |
| A3 | Mini links 60–90s ohne Flackern | NOT_TESTED |
| A4 | Rechts nur ein Fokusrahmen | NOT_TESTED |
| A5 | Rechts Jetzt/Zukunft stabil | NOT_TESTED |
| A6 | Live Back beendet Bild/Ton, GUI bedienbar | NOT_TESTED |
| B1 | 1.OK Info, 2.OK Player | NOT_TESTED |
| B2 | Playercontrols/echte Streaminfos | NOT_TESTED |
| B3 | Senderliste/Gruppen | NOT_TESTED |
| B4 | Rail erreichbar; zusätzlich Ghostlabels prüfen | NOT_TESTED |
| B5 | Back je Ebene; zusätzlich visuelles Einklappen prüfen | NOT_TESTED |
| B6 | Großen EPG öffnen | NOT_TESTED |
| C1 | Filmkatalog/Kategorien; neue Fokusregeln zusätzlich prüfen | NOT_TESTED |
| C2 | >240/möglichst500 Titel Paging | NOT_TESTED |
| C3 | Details/Back/Fokus; async Nachladen zusätzlich prüfen | NOT_TESTED |
| C4 | Film aus normalem Katalog starten/stoppen | NOT_TESTED |
| C5 | Serie/Staffeln/Episoden | NOT_TESTED |
| C6 | Autoplay einschließlich Staffelwechsel | NOT_TESTED |
| C7 | Manueller Stop ohne nächstes Autoplay | NOT_TESTED |
| C8 | Resume | NOT_TESTED |
| D1 | Suche öffnen | NOT_TESTED |
| D2 | Sendername suchen | NOT_TESTED |
| D3 | Echten laufenden Programmtitel finden | NOT_TESTED |
| D4 | Rock/Rocky in passenden Tabs | NOT_TESTED |
| D5 | Genre suchen | NOT_TESTED |
| D6 | 20 Tabwechsel ohne Trefferverlust | NOT_TESTED |
| D7 | Cover/Medieninfo | NOT_TESTED |
| D8 | Suchtreffer → Film UND Episode abspielen, korrekt zurück | NOT_TESTED |
| E1 | Bildmanager eindeutig öffnen | NOT_TESTED |
| E2 | Providerkandidat vorschauen | NOT_TESTED |
| E3 | Bild bewusst übernehmen/speichern | NOT_TESTED |
| E4 | Gewähltes Bild nach Neustart | NOT_TESTED |
| E5 | Poster/Hintergrund getrennt | NOT_TESTED |
| E6 | Metadaten separat vorschauen | NOT_TESTED |
| E7 | Einzelne Metadaten bewusst speichern | NOT_TESTED |
| E8 | Optional TMDb mit eigenem Token; richtige Aladdin-Jahrgänge | NOT_TESTED |
| E9 | Commons-Bildsuche; lokal nur falls eigene Datei vorhanden | NOT_TESTED |
| E10 | Schließen während Suche/Worker | NOT_TESTED |
| E11 | Dynamische Cover bleiben bei Tab/Kategorie/Playerwechsel | NOT_TESTED |
| F1 | Home-Live-Widget kalt/warm zügig | NOT_TESTED |
| F2 | Echte Senderlogos proportional/kompakt | NOT_TESTED |
| F3 | Fokus-NOW/NEXT/Uhrzeit/Progress | NOT_TESTED |
| F4 | Neueste Filme bis24 mit echten Postern | NOT_TESTED |
| F5 | Neueste Serien bis24 mit echten Postern | NOT_TESTED |
| F6 | Konkrete Live-/Film-/Serien-Klickziele | NOT_TESTED |
| F7 | 20 Fokuswechsel/Neustart, periodischer Refresh | NOT_TESTED |
| F8 | Ehrlicher Ohne-EPG-/Index-Fallback | NOT_TESTED |
| G1 | Gemeinsamer EPG/Refresh-Bestand; nur nach Backup-Gate | NOT_TESTED |
| G2 | Gestern/vorgestern…−7, echte Historie | NOT_TESTED |
| G3 | Quellen/manuelle Zuordnungen erhalten | NOT_TESTED |
| G4 | Vorhandene Film-/Serienfavoriten erhalten; TV-Favs später | NOT_TESTED |
| G5 | Startgruppe/Startsender erhalten | NOT_TESTED |
| G6 | Startgruppen-Latenz messen, getrennt von F1 | NOT_TESTED |
| G7 | Einstellungen nach Neustart einzeln kontrollieren | NOT_TESTED |
| G8 | Einmaliger .44-Versionshinweis, danach keine Wiederholung | NOT_TESTED |
| H1 | Fünf zusätzliche Live-Back-Zyklen tatsächlich zählen | NOT_TESTED |
| H2 | 20 Live-Start/Back-Zyklen einzeln zählen | NOT_TESTED |
| H3 | Live-Dauerbetrieb entsprechend historischem Test, echte Dauer notieren | NOT_TESTED |
| H4 | Zehn Senderwechsel | NOT_TESTED |
| H5 | Drei normale Katalogfilm-Start/Stop-Zyklen | NOT_TESTED |
| H6 | Serien-Stop und reguläres Autoplay getrennt | NOT_TESTED |
| H7 | Resume erneut | NOT_TESTED |
| H8 | Normaler Kodi-Neustart/Bestandsschutz | NOT_TESTED |

## Live-Stop-Einzelprotokoll

Einzelstart/Back: NOT_TESTED. Fünferserie: 01 NOT_TESTED; 02 NOT_TESTED; 03 NOT_TESTED; 04 NOT_TESTED; 05 NOT_TESTED. Erst nach den vorherigen PASS:

- [ ] LIVE45-20-01: NOT_TESTED
- [ ] LIVE45-20-02: NOT_TESTED
- [ ] LIVE45-20-03: NOT_TESTED
- [ ] LIVE45-20-04: NOT_TESTED
- [ ] LIVE45-20-05: NOT_TESTED
- [ ] LIVE45-20-06: NOT_TESTED
- [ ] LIVE45-20-07: NOT_TESTED
- [ ] LIVE45-20-08: NOT_TESTED
- [ ] LIVE45-20-09: NOT_TESTED
- [ ] LIVE45-20-10: NOT_TESTED
- [ ] LIVE45-20-11: NOT_TESTED
- [ ] LIVE45-20-12: NOT_TESTED
- [ ] LIVE45-20-13: NOT_TESTED
- [ ] LIVE45-20-14: NOT_TESTED
- [ ] LIVE45-20-15: NOT_TESTED
- [ ] LIVE45-20-16: NOT_TESTED
- [ ] LIVE45-20-17: NOT_TESTED
- [ ] LIVE45-20-18: NOT_TESTED
- [ ] LIVE45-20-19: NOT_TESTED
- [ ] LIVE45-20-20: NOT_TESTED

## Ergebnis aufzeichnen

Pro Fall Version/PR-Head/SHA, Gerät/Kodi/Skin, Datum/Uhrzeit, Schritte, Beobachtung, PASS/FAIL/NOT_TESTED oder BLOCKED mit Ursache. Bei Latenz Messpunkte/Stichproben notieren; nicht aus Hostzeiten auf Android schließen. Private Logs/URLs/Tokens/SMB-Zugänge niemals öffentlich posten. Keine automatische Issue-Schließung oder Merge-/Releasefreigabe. Alles bleibt bis zur echten Nutzerabnahme offen.
