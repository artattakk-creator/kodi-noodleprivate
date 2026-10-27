# XCMate 0.1.29.44 – Android-Abnahme Box B

Stand27.10.2026. **Alle .44-Geräteprüfungen NOT_TESTED.** .43 historisch63=39PASS/19FAIL/5NOT_TESTED, H2 tatsächlich20/20PASS mit `live_exit_fullscreen42=EIN`. Diese Belege bleiben historisch und sind keine .44-Freigabe. Box B: Kodi21.3/RK3528 ARM32/BINGIE2.2.3. **Box A bleibt ausgeschlossen.** Kein Neuinstallieren/Downgrade, Cache-/DB-/Bildlöschen, Profilreset, Keymap-/Skinpatch oder USB-/SMB-/Migrationstest. Dynamisch bleibt aktiv, bisherige Daten/Portale/IR unverändert.

## Reihenfolge und Stop-Gates

1. Zunächst Draft/Quellen/Testberichte prüfen. Keine automatische Installation. Paket/SHA müssen zum selben PR-Head gehören; ein Actions-Download ist ein Container, daraus das eigentliche Add-on-ZIP entnehmen. Erst nach ausdrücklicher Freigabe als reguläres Kodi-ZIP-Update über .43, ohne Deinstallation. Kein Produktivrelease durch diesen Draft.
2. PREP44: Version44, Box B, Kompatibilitätsmodus weiterhin EIN, unverändertes Profil und Dynamisch prüfen. Default/OFF niemals probeweise testen. Vor jedem Refresh **Gate0 unten vollständig**; automatischer Legacyimport bleibt BACKUP_REQUIRED. Bestehende Geräte-EPG-Daten nicht experimentell manipulieren.
3. **Gate0 zuerst absichern:** konsistente lokale Sicherung ausdrücklich bestätigen, privat aufbewahren, Status/HASH prüfen. Noch kein Refresh durch die Sicherungsaktion. Ohne gültige Sicherung/Einwilligung alle Refresh-/Migrationsprüfungen BLOCKED, weitere Featureabnahme zurückstellen. Die Sicherungsfunktion selbst ist neu und auf Host geprüft; bei Fehler keinen Umgehungsversuch durchführen.
4. Startsender → einmal Live-Back. Bild UND Ton müssen enden und GUI reagieren. Nur bei PASS Film-Back, fünf und20Livezyklen, dann übrige Gates. Bereits ein Freeze/STOP_TIMEOUT stoppt die Testserie; keine weiteren Stop-/Recoveryaufrufe erzwingen.
5. Nach bestandenem P0-Sicherungsgate einen einzelnen ausdrücklich gewählten EPG-Refresh mit Vorher-/Nachher-Coverage prüfen. Bei ausgedünnter Sicht sofort stoppen, keine Wiederholungsrefreshs und kein Reset. Quellenfehler/0-Event/Lock/Abbruch/ENOSPC ausschließlich im Host/isolierter DB testen, niemals künstlich auf Box B verursachen.

## A–H vollständig, 63 nummerierte Fälle

Die Spalte .43 dokumentiert ursprüngliche Nutzerbewertungen. B4/B5 und C1–C3 waren funktionale PASS mit separatem visuellem FAIL. E3–E5 praktisch BLOCKED ohne wählbaren Kandidaten, kein unabhängig belegter Persistenzdefekt. E9 lokaler Teil ungeprüft ohne Datei. F7/F8 nicht unabhängig bewiesen. G4 nur Medienfavoriten; TV-Favoriten DEFERRED. G6 ohne alte Messwerte. H1 vorgefüllte5/5 nicht als Beleg verwenden.

| Fall | Prüfung / erwartetes Verhalten | .43 historisch | .44 Box B |
|---|---|---|---|
| A1 | Version/Kompatibilitätsmodus EIN | PASS | NOT_TESTED |
| A2 | Startsender | PASS | NOT_TESTED |
| A3 | Mini links 60–90s ohne Flackern | FAIL | NOT_TESTED |
| A4 | Rechts nur ein Fokusrahmen | PASS | NOT_TESTED |
| A5 | Rechts Jetzt/Zukunft stabil | PASS | NOT_TESTED |
| A6 | Live Back beendet Bild/Ton, GUI bedienbar | PASS | NOT_TESTED |
| B1 | 1.OK Info, 2.OK Player | PASS | NOT_TESTED |
| B2 | Playercontrols/echte Streaminfos | NOT_TESTED | NOT_TESTED |
| B3 | Senderliste/Gruppen | PASS | NOT_TESTED |
| B4 | Rail erreichbar; zusätzlich Ghostlabels prüfen | PASS | NOT_TESTED |
| B5 | Back je Ebene; zusätzlich visuelles Einklappen prüfen | PASS | NOT_TESTED |
| B6 | Großen EPG öffnen | PASS | NOT_TESTED |
| C1 | Filmkatalog/Kategorien; neue Fokusregeln zusätzlich prüfen | PASS | NOT_TESTED |
| C2 | >240/möglichst500 Titel Paging | PASS | NOT_TESTED |
| C3 | Details/Back/Fokus; async Nachladen zusätzlich prüfen | PASS | NOT_TESTED |
| C4 | Film aus normalem Katalog starten/stoppen | PASS | NOT_TESTED |
| C5 | Serie/Staffeln/Episoden | PASS | NOT_TESTED |
| C6 | Autoplay einschließlich Staffelwechsel | PASS | NOT_TESTED |
| C7 | Manueller Stop ohne nächstes Autoplay | PASS | NOT_TESTED |
| C8 | Resume | PASS | NOT_TESTED |
| D1 | Suche öffnen | PASS | NOT_TESTED |
| D2 | Sendername suchen | PASS | NOT_TESTED |
| D3 | Echten laufenden Programmtitel finden | PASS | NOT_TESTED |
| D4 | Rock/Rocky in passenden Tabs | PASS | NOT_TESTED |
| D5 | Genre suchen | PASS | NOT_TESTED |
| D6 | 20 Tabwechsel ohne Trefferverlust | PASS | NOT_TESTED |
| D7 | Cover/Medieninfo | PASS | NOT_TESTED |
| D8 | Suchtreffer → Film UND Episode abspielen, korrekt zurück | FAIL | NOT_TESTED |
| E1 | Bildmanager eindeutig öffnen | FAIL | NOT_TESTED |
| E2 | Providerkandidat vorschauen | FAIL | NOT_TESTED |
| E3 | Bild bewusst übernehmen/speichern | FAIL | NOT_TESTED |
| E4 | Gewähltes Bild nach Neustart | FAIL | NOT_TESTED |
| E5 | Poster/Hintergrund getrennt | FAIL | NOT_TESTED |
| E6 | Metadaten separat vorschauen | NOT_TESTED | NOT_TESTED |
| E7 | Einzelne Metadaten bewusst speichern | NOT_TESTED | NOT_TESTED |
| E8 | Optional TMDb mit eigenem Token; richtige Aladdin-Jahrgänge | FAIL | NOT_TESTED |
| E9 | Commons-Bildsuche; lokal nur falls eigene Datei vorhanden | FAIL | NOT_TESTED |
| E10 | Schließen während Suche/Worker | PASS | NOT_TESTED |
| E11 | Dynamische Cover bleiben bei Tab/Kategorie/Playerwechsel | PASS | NOT_TESTED |
| F1 | Home-Live-Widget kalt/warm zügig | FAIL | NOT_TESTED |
| F2 | Echte Senderlogos proportional/kompakt | FAIL | NOT_TESTED |
| F3 | Fokus-NOW/NEXT/Uhrzeit/Progress | FAIL | NOT_TESTED |
| F4 | Neueste Filme bis24 mit echten Postern | FAIL | NOT_TESTED |
| F5 | Neueste Serien bis24 mit echten Postern | FAIL | NOT_TESTED |
| F6 | Konkrete Live-/Film-/Serien-Klickziele | FAIL | NOT_TESTED |
| F7 | 20 Fokuswechsel/Neustart, periodischer Refresh | FAIL | NOT_TESTED |
| F8 | Ehrlicher Ohne-EPG-/Index-Fallback | FAIL | NOT_TESTED |
| G1 | Gemeinsamer EPG/Refresh-Bestand; nur nach Backup-Gate | FAIL | NOT_TESTED |
| G2 | Gestern/vorgestern…−7, echte Historie | FAIL | NOT_TESTED |
| G3 | Quellen/manuelle Zuordnungen erhalten | PASS | NOT_TESTED |
| G4 | Vorhandene Film-/Serienfavoriten erhalten; TV-Favs später | PASS | NOT_TESTED |
| G5 | Startgruppe/Startsender erhalten | PASS | NOT_TESTED |
| G6 | Startgruppen-Latenz messen, getrennt von F1 | PASS | NOT_TESTED |
| G7 | Einstellungen nach Neustart einzeln kontrollieren | NOT_TESTED | NOT_TESTED |
| G8 | Einmaliger .44-Versionshinweis, danach keine Wiederholung | PASS | NOT_TESTED |
| H1 | Fünf zusätzliche Live-Back-Zyklen tatsächlich zählen | NOT_TESTED | NOT_TESTED |
| H2 | 20 Live-Start/Back-Zyklen einzeln zählen | PASS | NOT_TESTED |
| H3 | Live-Dauerbetrieb entsprechend historischem Test, echte Dauer notieren | PASS | NOT_TESTED |
| H4 | Zehn Senderwechsel | PASS | NOT_TESTED |
| H5 | Drei normale Katalogfilm-Start/Stop-Zyklen | PASS | NOT_TESTED |
| H6 | Serien-Stop und reguläres Autoplay getrennt | PASS | NOT_TESTED |
| H7 | Resume erneut | PASS | NOT_TESTED |
| H8 | Normaler Kodi-Neustart/Bestandsschutz | PASS | NOT_TESTED |

## Zusätzliche verbindliche Gateprüfungen

Jede Zeile einzeln, nicht als Sammel-PASS. Fehlen reale Kandidaten/Quellhistorie/Decoderformate: NOT_TESTED mit Ursache. Keine externe API oder BINGIE-Anpassung erzwingen.

| Fall | Schritte und Erwartung | .44 |
|---|---|---|
| EPGSAFE-01 | Vor jeder Änderung read-only aktuellen Bestand prüfen: Revision, Anzahl je Tag/Quellrang, min/max, Startsender NowNext, Quelle/Mapping im privaten Kontext. Keine öffentliche DB/Config hochladen. | NOT_TESTED |
| EPGSAFE-02 | Wartung & Diagnose → EPG sichern und Importschutz aktivieren; explizite Bestätigung. BACKUP_VERIFIED, SHA256/Dateigröße, lokale .sqlite + ggf .sources.json + Manifest vorhanden. Kein automatischer Refresh. | NOT_TESTED |
| EPGSAFE-03 | Sicherung privat separat verwahren. Bei laufendem Kodi nur Backup-API-Kopie, niemals einzelne DB/WAL/SHM-Dateien austauschen. Ohne verifizierte Kopie stoppen. | NOT_TESTED |
| EPGSAFE-04 | Nach Genehmigung EIN Refresh: angefordert/läuft/verifiziert/teilweise/Fehler unterscheiden. Vorher gültige Programme bleiben außer exakt begründeter Korrektur; echte Lücken füllen. | NOT_TESTED |
| EPGSAFE-05 | Mini/Info/Groß/Suche/Widgets am selben Sender und Zeitpunkt vergleichen: reale Jetzt/Danach, gemeinsame Revision, keine Shortcache-Verkürzung. UI-Refreshzeit notieren. | NOT_TESTED |
| EPGSAFE-06 | Gestern/vorgestern bis−7, mit vorhandenen Daten und leeren Tagen. Header zeigt tatsächliche gespeicherte Tage, kein Fake-Catch-up. DST negativ nur Host, nicht Geräteuhr verstellen. | NOT_TESTED |
| EPGSAFE-07 | Nach normalem Kodi-Neustart Bestand/History/Quellen/Zuordnungen erhalten. Keine Restore-/DB-Tauschprobe auf B. | NOT_TESTED |
| WIDGET44-01 | Vorhandene drei Reihen ohne Neukonfiguration lesen: bis12 Startgruppensender, bis24 eindeutige echte Film-/Serientitel, Titelanzahl und echte Art notieren. | NOT_TESTED |
| WIDGET44-02 | Kalt/Warm5 Stichproben jeweils Request→erste bedienbare Reihe→Art/EPG notieren; nach20Fokuswechseln p50/p95 mit Stichprobenumfang melden. Startgruppe separat messen. | NOT_TESTED |
| WIDGET44-03 | Reale Startgruppe/Startsender zuerst; aktuelle Quelle/Daten-Revision, echter NowNext/Progress, kein Fokus-Autoplay/HTTP/Popup. | NOT_TESTED |
| WIDGET44-04 | Film→genau dessen Detail, Serie→richtige Serie/Staffeln, Live→genauer Sender. Dann Back/Return, kein Rootumweg. | NOT_TESTED |
| WIDGET44-05 | Natürliche neue Kataloggeneration/periodischer Refresh, vorherige gute Reihe bleibt bedienbar. Kein künstlicher Index-/Netzdefekt. | NOT_TESTED |
| WIDGET44-06 | Fokus-EPG, halbe Logos und Skin-Build auf echtem BINGIE prüfen. Falls Properties vorhanden, Renderer fehlt: BLOCKED und separate Adapterfreigabe nötig; keine Fremdskinänderung. | NOT_TESTED |
| SEARCHPLAY44-01 | Film aus Suchtreffer starten/Back; exakte Film-/Portalzuordnung, Query/Tab/Trefferposition wieder da. | NOT_TESTED |
| SEARCHPLAY44-02 | Serie aus Suchtreffer→Staffel/Episode→Play, Stop und Return. Kein fremdes Portal, kein Doppelstart oder Autoplay nach Stop. | NOT_TESTED |
| SEARCHPLAY44-03 | Bei natürlichem Fehler nur feste MEDIA44/PORTAL_READ_REASON/Bootroute sammeln; keine URLs, IDs, Suchtexte oder rohe Exceptions veröffentlichen. Kein Profil absichtlich sperren/korrumpieren. | NOT_TESTED |
| COVER44-01 | Fehlendes Poster: Links→Cover & Metadaten→Bild suchen/zuordnen, Quellen erreichbar, Back-Fokus wieder da. Film UND Serie. | NOT_TESTED |
| COVER44-02 | Separater Metadateneintrag auch ohne Bild; Provider/TMDb-Felder vorschauen, abbrechen ohne Änderung; einzeln bewusst übernehmen/speichern. | NOT_TESTED |
| COVER44-03 | TMDb standardmäßig AUS klar melden; ohne privaten Token Token fehlt, kein APIaufruf. Mit eigenem gültigem Token optional echte Aladdin-Jahrgänge unterscheiden. Kein Sharedtoken. | NOT_TESTED |
| COVER44-04 | Vorhandenen Kandidaten Poster/Hintergrund separat wählen→Übernehmen→Speichern; Neustart und Quellenrefresh erhalten Auswahl. Ohne echten Kandidaten BLOCKED. | NOT_TESTED |
| COVER44-05 | Commons echte Rechte/Attribution, Person als Ersatzbild ohne Filmdaten. Eigene lokale PNG/JPEG nur falls bereits vorhanden; keine neue Datei voraussetzen. | NOT_TESTED |
| NAV44-01 | Linkes Mini60–90s und20Öffnen/Schließen, echte Eventgrenze; keine Flashes. Rechter Fokus/Now/Future unverändert. | NOT_TESTED |
| NAV44-02 | Rail20mal aus/einklappen: vor Gruppen nur Icons, keinerlei alte Texte. Back schließt jeweils eine Ebene. | NOT_TESTED |
| NAV44-03 | Film UND Serie: Up/Down nur Fokus; OK lädt Kategorie und behält Kategorienfokus; Right1 Poster0+Sidebar; Right2 Poster1+Fullwidth; Left zum Rand+extraLeft zeigt Sidebar. | NOT_TESTED |
| NAV44-04 | Lange Kategorie/Scroll/Details/PlayerBack und natürliches Hintergrundupdate: Film-ID, Kategorie und Fokus bleiben; keine Mitte-Sprünge oder leere Zwischenliste. | NOT_TESTED |
| INFOMICRO-01 | 1.OK: winzige neutrale Monitor-/Lautsprechericons **unten rechts innerhalb** Panel, Screenshotreferenz; keine lange zweite Technikzeile. | NOT_TESTED |
| INFOMICRO-02 | Tatsächliche1080p-Oberfläche: Icon etwa13px, kleine registrierte Schrift, Abstand18–24px rechts/12–18px unten; Sender/EPG/Progress unberührt. | NOT_TESTED |
| INFOMICRO-03 | Tatsächliche720p-Oberfläche: proportional, keine Clipping-/Fontprobleme, optisch gemeinsame Grundlinie. Ohne sichere Anzeigeumschaltung nicht erzwingen. | NOT_TESTED |
| INFOMICRO-04 | Echt1920×1080/AAC2.0 bzw reales anderes Format: nur gemessene Kodi-Trackwerte, kein Sendername als Beleg; tatsächliche Werte notieren. | NOT_TESTED |
| INFOMICRO-05 | Reales AC3/EAC3 mit5.1 falls vorhanden; keine Dolby-/Atmosannahme allein aus Codec. Ohne passenden Track NOT_TESTED. | NOT_TESTED |
| INFOMICRO-06 | Unbekannt/verzögert/Trackwechsel: leer bis echte Werte, danach aktualisiert, keine alten Werte. Keine zusätzliche Abfragelast erwarten. | NOT_TESTED |
| INFOMICRO-07 | 1.OK→2.OK→Back, Links-Mini/Gruppen/Rail, Schließen/Neuöffnen: Mikrozeile korrekt sichtbar/weg, IR/Fokus stabil. | NOT_TESTED |
| INFOMICRO-08 | H2 nach UIänderung erneut20/20 echte Live-Backs mit Modus EIN. Fremde Player nicht ändern, sofort Stop bei Freeze. | NOT_TESTED |

## Einzelzählung Stop-Zyklen und Ergebnisprotokoll

Einzel-Live-Back: NOT_TESTED. Fünferserie01–05: jeweils NOT_TESTED. H2-20erSerie:

- [ ] LIVE44-20-01: NOT_TESTED
- [ ] LIVE44-20-02: NOT_TESTED
- [ ] LIVE44-20-03: NOT_TESTED
- [ ] LIVE44-20-04: NOT_TESTED
- [ ] LIVE44-20-05: NOT_TESTED
- [ ] LIVE44-20-06: NOT_TESTED
- [ ] LIVE44-20-07: NOT_TESTED
- [ ] LIVE44-20-08: NOT_TESTED
- [ ] LIVE44-20-09: NOT_TESTED
- [ ] LIVE44-20-10: NOT_TESTED
- [ ] LIVE44-20-11: NOT_TESTED
- [ ] LIVE44-20-12: NOT_TESTED
- [ ] LIVE44-20-13: NOT_TESTED
- [ ] LIVE44-20-14: NOT_TESTED
- [ ] LIVE44-20-15: NOT_TESTED
- [ ] LIVE44-20-16: NOT_TESTED
- [ ] LIVE44-20-17: NOT_TESTED
- [ ] LIVE44-20-18: NOT_TESTED
- [ ] LIVE44-20-19: NOT_TESTED
- [ ] LIVE44-20-20: NOT_TESTED

Pro Fall: Version/PR-Head, Gerät/Kodi/Skin, Datum/Uhrzeit Europe/Berlin, Modus EIN, echte Aktion/Beobachtung, PASS/FAIL/NOT_TESTED/BLOCKED, bei Latenz Start-/Endpunkt und Stichproben. Private Logs vor Weitergabe redigieren. Kein pauschales PASS aus Host/CI. Issue #233 und Einzelissues bleiben offen; Merge/Produktivrelease benötigen ausdrückliche Freigabe und tatsächliche Abnahme. Vollständiger Hub und Fremdskin-Anpassung sind zusätzliche offene Gates; nichts stillschweigend als bestanden zählen.
