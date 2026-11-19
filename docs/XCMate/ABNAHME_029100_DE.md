# XCMate 0.1.29.100 · Entwicklungs- und Abnahmebericht

Entwicklungsstand zu #498 mit XMLTV-Folgeauftrag #499 und Backend #12. Der Kodi-Entwurf baut auf dem vollständigen .99-Quellstand aus #489 auf. Die Geräte- und Produktionsabnahme steht aus. [Masterauftrag #498](https://github.com/artattakk-creator/kodi-noodleprivate/issues/498) · [Kodi-Folgeauftrag #499](https://github.com/artattakk-creator/kodi-noodleprivate/issues/499) · [Backend-Folgeauftrag #12](https://github.com/artattakk-creator/xcmate-epg/issues/12)

## Entwicklungsbasis

| Entwurf | Befund und Integration |
| --- | --- |
| Kodi #489, `b1e4cfb8` | Kumulative .99-Basis einschließlich Settings-Reparatur, Backup- und Bildfallback. Das auf Main veröffentlichte Pilot-ZIP ist ein anderer Bezugspunkt als der Main-Quellbaum. |
| Kodi #493 | V1-Transport als Referenz für private Statusprüfung, SHA256 und LastGood. |
| Kodi #494 | V2-Transport und Tests gezielt übertragen. Die ältere Basis blieb außerhalb des kumulativen Zweigs. Schema 3 ersetzt im neuen Transport die zwei Pflicht-Payloads. |
| Kodi #486 | Ein-Schalter-Entwurf im EPG-Menü mit dem bestehenden Service und Scheduler umgesetzt. |
| Backend #3 → #5 → #7 → #9 | Bereits vorhandene Delta-, Streaming- und Artwork-Auswahl weitergeführt. Der gestapelte Entwurf #11 baut auf #9 auf. |

[Entwicklungscode Kodi #500](https://github.com/artattakk-creator/kodi-noodleprivate/pull/500) · [Backend #11](https://github.com/artattakk-creator/xcmate-epg/pull/11)

## Schema 3 und Migration

- `manifest.json` gibt den Status, SHA256/Revision, die Größe, den fest gebundenen Git-Commit, die Quell-, Kanal- und Programmzahlen, die Bildrollenzähler und das tatsächliche UTC-Zeitfenster an. Bei einer Änderung folgt ein Abruf von `xcmate-epg.xml.gz` am angegebenen Commit. HTTP 304 und ein unveränderter SHA256 führen zu keinem erneuten Payload-Abruf und keinem Reimport desselben bereits geprüften Standes.
- `programme/image` steht nach den übrigen Programmfeldern am DTD-Ende. `episode_still` wird als `still`, Fanart als `backdrop` serialisiert. Senderlogos stehen in `channel/icon`, Legacy-Sendungsbilder in `programme/icon`. Bilder werden als HTTPS-Referenzen nach der Freigabe- und Quellenprüfung exportiert. Kodi prüft Bildrolle, Geometrie und Quellenfreigabe vor der Darstellung. Spezialrollen und Qualitätsbelege verbleiben in den bestehenden Backend-/Profilindizes. Kodi speichert den abgeleiteten Logo-Index lokal. [Offizielle XMLTV-DTD](https://github.com/XMLTV/xmltv/blob/f33601698cf1f1c7a67030b9ec2d3ad565421b5a/xmltv.dtd)
- Historische `PRIVATE_PENDING`-Manifeste werden als Wartestatus gelesen. Beim alten V1-/V2-READY-Vertrag bleibt ein lokal bereits bestätigter Stand erhalten. Der Schema-3-Reader akzeptiert keine neue alte READY-Generation. Anbieter-EPG, Profilzuordnungen, lokale Bild-Overrides, Archiv und Backups bleiben geschützt. Ein neuer Agent-Stand durchläuft denselben Import- und Backup-Gate wie die bestehenden Quellen.
- Der Langzeitdienst prüft nach Opt-in standardmäßig alle 24 Stunden. Der Schalter startet die vorhandene Kodi-Hintergrundkette. Die UI zeigt Prüfzeit, Revision, Status, gelesene und bestätigte Zeilen sowie Bildrollenzähler. Im öffentlichen Entwurf liegen nur synthetische XMLTV-Beispiele. Das Produktivmanifest bleibt `PRIVATE_PENDING / PRODUCTION_DATA_NOT_APPROVED`. Der lokale Backend-Lieferadapter ist synthetisch geprüft. Autorisierter Restore, Rechteprüfung, privater Live-Readback und Produktions-Scheduler stehen aus.
- Der Reader bezieht eine separat bereitgestellte, gerätebezogene Leseberechtigung aus dem lokalen Profil. Scope, Rotation und Widerruf sind Teil der privaten Bereitstellung. Das Testpaket enthält den Add-on-Code und die freigegebenen lokalen Assets. [Private GitHub-Lieferung und Tageslauf](https://github.com/artattakk-creator/xcmate-epg/pull/11)

## Änderungsbericht nach Funktionsbereich

- **Home und Medien.** Bestehender breiter Hero mit rechtem Fanart und linker Textfläche, Senderleiste und sechs Reihen bleiben der BINGIE-Einstieg. Per-Portal-Filmfilter werden vor dem Widget-Limit angewandt. Katalog, Suche und EPG-Bildsuche bleiben erreichbar. Die unterstützte MP3-Quelle liefert Album-Neuheiten. Technische Sender-/Logozähler wandern aus Home in die Widgetdiagnose. Der private Testbau enthält das originale Offline-Motiv aus #421 bytegetreu. [BINGIE und Originalmotiv](https://github.com/artattakk-creator/kodi-noodleprivate/issues/421)
- **Live-TV, EPG und Suche.** Die vorhandenen drei Links-Ebenen, Gruppen ohne EPG und OSD bleiben Eingangspunkte. Das Mini-EPG zeigt bestätigte vergangene Ereignisse und hebt Jetzt hervor, die Infoleiste zeigt die Restzeit. Die Suchergebnisse enthalten Jetzt/Danach, Zeiten und Quelle. Grid und Mini teilen die quellqualifizierte Suche, Vorschau, Speichern und Readback. Details zeigen echte Alterskennzeichnung und nachvollziehbare Sender-/Bildquelle. Merken erzeugt einen Merklisteneintrag. Erinnerungen bleiben eine ausdrückliche Aktion. [Mapping-Abnahme](https://github.com/artattakk-creator/kodi-noodleprivate/issues/482)
- **Artwork, Logos, Speicher und Darstellung.** Typisierte Referenzen laufen durch Quellenfreigabe, Qualitätsprüfung und rollenspezifische Auswahl. Der Parser übernimmt bei bisherigen XMLTV-Anbieterfeeds weiterhin Legacy-\`programme/icon\`. Der kompakte SQLite-Index hält Agent-Bildrollen und Logos für Cold-Readback und Neustart fest. Manuelle Bilder haben Vorrang. Logo-Overrides behalten Alpha und werden kompakt gespeichert. TMDB/TVMaze-Abrufe werden innerhalb des Workers dedupliziert. Speicher zeigt freie Bytes und Zielvolume. Deckkraft, Fokus-/Schriftfarben, Schriftgrößen und Preview greifen in XCMate. Space Premium bleibt optional. [Artwork-Hub](https://github.com/artattakk-creator/kodi-noodleprivate/issues/469) · [Graphics v2](https://github.com/artattakk-creator/kodi-noodleprivate/issues/27)
- **EPG-Manager und Zuverlässigkeit.** Konfigurierte Quellen erscheinen vor der Inventur. Der Bericht unterscheidet gelesene, zugeordnete, vorbereitete, gespeicherte und unabhängig zurückgelesene Daten. Die obere Schaltflächenleiste und der Berichtstext überdecken sich im neu geprüften Layout nicht. Abbruchprüfungen lesen den Auftrag in einem begrenzten Intervall. Die Hostmessungen vergleichen synthetische Daten. Die reale Android-Laufzeit vom 19.11.2026 bleibt Vergleichswert. [Manager- und Fortschrittsfehler](https://github.com/artattakk-creator/kodi-noodleprivate/issues/458) · [Reale .99-Beobachtung](https://github.com/artattakk-creator/kodi-noodleprivate/issues/495)

## Abnahmematrix

Die Ergebnisse gelten für die jeweils angegebene Testumgebung. Der Geräte- und Produktivstatus bleibt offen.

| Funktion | Ergebnis | Nachweis oder offen |
| --- | --- | --- |
| Vollständige .99-Basis und Bestandsschutz | PASS | 4.252 Hosttests auf `b1e4cfb8`. Historische Release- und Katalogbytes bleiben Gegenstand eigener Tests. |
| V3 XMLTV, DTD, typisierte Rollen und Legacy-Icons | PASS | Offizielle DTD offline und synthetischer Backend→Kodi-Vertrag. Die Fixture enthält drei Sendungen und die typisierten Bildrollen einschließlich Personen-/Charakterreferenzen. |
| Ein Pflicht-Payload, Git-Commitbindung, Größen- und SHA-Prüfung | PASS | Test wies Manifest und genau eine XMLTV-GZIP-Anfrage nach. Schema 1/2 READY bleibt inkompatibel mit neuen Generationen. |
| Streaming >185.000 Programme | PASS | Backend-Export mit offizieller DTD und Kodi-Import von 185.001 Sendungen mit je drei Bildrollen. Unabhängiger SQLite-Readback 185.001 Zeilen, drei Kanäle, 1.371.526 GZIP-Bytes, 72,16 s im separaten Hostlauf. |
| 24 h, HTTP 304, unveränderter SHA, Änderung | PASS | Synthetische 24-h-, ETag-, Neustart- und Delta-Regressionen. |
| Offline und 401/403/429, unzulässige URLs und beschädigte Dateien | PASS | Synthetischer Transport, keine LastGood-Ersetzung bei abgelehnter neuer Generation. |
| Opt-in, Quellenstatus, Prüfzeit und manuelle Prüfung | PASS | Hosttests und bestehender Kodi-Hintergrunddienst im Codepfad. Gerätebedienung bleibt separat. |
| Echter privater GitHub-Feed und Rechte | BLOCKED | Privates Manifest meldet `PRIVATE_PENDING`, tatsächlicher Geräte-Lesezugang und Rechte noch nicht abgenommen. |
| Produktiver Backend-Scheduler | BLOCKED | Tageslauf synthetisch geprüft, Betriebsfreigabe und Live-Readback erforderlich. |
| Gespeicherte manuelle Senderzuordnung, Quellen-ID-Kollision, Vorschau und Abbruch | PASS | Hosttests und synthetische Kodi-Grid-Dialoge; reale Fälle SAT.1, Disney und weitere Sender offen. |
| Provider-Basis, Sicherung und Readback | PASS | Synthetische Isolation der Quellen, `IMPORT_AUTHORIZED` und unabhängiger Readback. |
| EPG-Manager und Layout | PASS | Native Linux-Belege bei 720p und 1080p. Vergleichslauf mit den realen 192 Kanälen/21.807 Agent-Sendungen steht aus. |
| Drei Links-Ebenen, Gruppen ohne EPG, Mini/OSD/Fokus | PASS | Fokussierte Hostpfade. Tatsächlicher TV-Fokus und nahtloser MediaCodec-Übergang auf Geräten offen. |
| Mini-Elternspalte im physischen Player | BLOCKED | Native Dialogprüfung nutzt einen synthetischen Mini-Owner. Sie zeigt keine echte Mini-Elternspalte auf dem Gerät. |
| Großes EPG, Details, Suche und Merkliste | PASS | Hosttests für Fokus, Quellen, Altersangabe, Jetzt/Danach und Merk-/Reminder-Aktionen. Die physische Daueranzeige im Detailfenster steht aus. |
| Home-Gruppenfilter, Albumcover, Katalog und Benutzer-Widgets | PASS | Native Linux-Smokes 720p/1080p mit Neustart, Albumcover und Testton. Echte MP3-Quelle auf Android noch offen. |
| Sechs sichtbare BINGIE-Reihen mit echten Postern | FAIL | Der native Picker-Harness stoppte in SkinShortcuts und der Direkt-Renderer hatte keine vorbereiteten Poster. Damit blieb die vollständige visuelle BINGIE-Prüfung offen. |
| Stabile BINGIE- und Detailbilder aus Schema 3 | BLOCKED | Kodi 21.2 / Estuary zeigt die ausgewählte Bildrolle im nativen Control 110 bei 720p und 1080p. Die lange BINGIE-Anzeige und View-Wechsel auf Geräten bleiben offen. |
| Originaler Offline-Hero | PASS | PNG 1672 × 941, 1.529.639 Bytes, SHA256 `8f836ef0eaa73d40410b5391e2661e01dcbfa33027146b03f460942a8deb820e` im privaten Testbau geprüft. |
| Logo-Override, Bild-Opt-out und Cache-Limits | PASS | Gezielte Hosttests. Private Gerätefreigabe, Speicherziel USB/SMB und Langzeitverhalten noch separat. |
| Erscheinungsbild und Space Premium | PASS | Native Linux-Vorschau bei 720p, 1080p und 4K. Externe Theme-Installation und alle Geräteoberflächen noch separat. |
| Android TV 13 / RK3528 / Kodi 21.3 / BINGIE | BLOCKED | Physisches Testgerät war in der Entwicklungsumgebung nicht verbunden. |
| LG webOS / Kodi 22 / Standardskin | BLOCKED | Physisches Testgerät war in der Entwicklungsumgebung nicht verbunden. |


## Regression und privater Testbau

- **Backend, `9b1a33bc`.** 249 Offline-Tests bestanden. Der Exporttest umfasst 185.001 Programme mit offizieller DTD, verzögerten Metadaten und synthetischen Profilen. Der LastGood-Vertrag umfasst unterbrochene Veröffentlichung und Versionswechsel. [Backend-CI](https://github.com/artattakk-creator/xcmate-epg/actions/runs/44578226166)
- **Repo-übergreifender Nachweis.** Das unveränderte synthetische GZIP aus dem Backend hat SHA256 `904a7aad0ea7a6620d8e55701acdcdb96496e96b03afb97d95d8cd90352c992a`. Der Kodi-Reader prüft zwei HTTP-Anfragen im Refresh mit geändertem Inhalt, Manifest und XMLTV-GZIP. Die Zähler für Senderlogos, Legacy-Icons, Poster, Backdrop, Still, Person und Charakter werden gegen den gelesenen Inhalt abgeglichen.
- **Artwork-Nachprüfung.** Unabhängige 74 fokussierte Tests bestätigen separate Aufträge für Hero, Kachel und Details, Rollenbelege für identische Bildbytes nach Neustart und den Wechsel auf ein korrekt proportioniertes Ersatzposter. Vier historische Queue-Tests prüfen die tatsächlichen Jobs nach Profil, Ereignis und Rolle. Der Vorlauf mit 23 Fehlern führte zusätzlich zu Korrekturen am Guide-Kontrast, an der Bilddeckkraft, im Sprachkatalog und an Test-Fixtures. Alle 23 Fälle bestanden im gezielten Nachlauf.
- **Kodi-Gesamtlauf.** Separater Wiederholungslauf mit 227 historischen Eingaben auf dem konsolidierten Zweig. Ergebnis wird nach Abschluss eingetragen.
- **Kodi nativ.** Linux/Kodi 21.2 bei 720p mit dem privaten Paket und bei 1080p mit dem Schema-3-Entwurf bestätigte den Manager, 600 synthetische Programme im unabhängigen Readback, den Abbruch mit LastGood und den quellqualifizierten Grid-/Mini-Dialog. Die Mini-Tests verwendeten einen synthetischen Elternkontext. Die Gerätestatus bleiben `ANDROID_NOT_TESTED` und `LG_NOT_TESTED`.
- **Privates ZIP.** Der reproduzierbare Entwicklungs-Testbau `plugin.video.xtreammate-0.1.29.100.zip` aus `b2ca60ac` enthält 915 Dateien und hat 6.055.449 Bytes. ZIP-CRC und die Quellbytes sind geprüft. Zwei getrennte Builds und der erneute Abruf aus dem eigentümerbeschränkten Drive-Ordner stimmen bytegenau überein. SHA256 `139ef7a68b1073031347929c2f6ae51e6cfe91450b6637f9f61ccc3dd3f9a100`. Spätere Commits aktualisieren die Tests und den Bericht.


## Offene Geräteabnahme

1. Android/BINGIE bei 720p, 1080p und 4K. Startsender, sechs Reihen einschließlich MP3-Alben, persönliche Widgets, Hero-Fokus ohne Playerstart und persistente Senderlogos prüfen. Je einen realen Poster-, Backdrop- und Episodenbildfall nach Fokuswechsel, Neustart und Offline-Wechsel prüfen.
2. Android-Livebetrieb. 3 Links-Ebenen, Gruppen ohne EPG, Mini- und Groß-EPG, kurzes und langes OK, Streamwerte, OSD und Back prüfen. EPG für Das Erste HD, ZDF HD, SAT.1 HD und einen manuell zugeordneten Sender wie Disney Channel mit Titel, Zeit und Beschreibung abgleichen. Die erfolgreichen und fehlerhaften Save-Fälle aus #498 für Senderzuordnung und Bild-Override getrennt wiederholen.
3. LG/webOS Kodi 22 ohne BINGIE. Agent-Status und Anbieter-Fallback, Sendersuche/Zuordnung, Details/Bilder, Standardskin, Wiedergabe und Neustart prüfen. Speicherziel oder dynamischen Modus auf realen Volumes testen.
4. Backend und Client gemeinsam. Einen autorisierten, vollständig geprüften privaten V3-Stand mit Drei-Quellen-Abdeckung und echten Verteilrechten end-to-end prüfen. Unveränderten 24-h-Lauf, geänderte Revision, Zugriffsentzug, Offline-LastGood und Geräte-Readback getrennt dokumentieren.
