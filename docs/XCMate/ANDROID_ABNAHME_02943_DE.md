# XCMate .43 – vollständige Android-Abnahme Box B

Stand: 27.10.2026. **Sämtliche .43-Gates NOT_TESTED**, auch wenn Hosttests bestehen. Historisch: .42 mit `live_exit_fullscreen42=EIN` hat einen echten Einzel-PASS auf Box B; keine vorweggenommene 5-/20-Zyklen- oder .43-Freigabe. Originale .41/.42-Listen bleiben unverändert erhalten.

**Erst PR prüfen und ausdrücklich Merge freigeben. Nach diesem Merge die vollständige .43-Abnahme durchführen.** Codex mergt, veröffentlicht und installiert nichts. Vorher dient das ZIP der Quell-/Paketprüfung; kein automatischer Geräte-Update.

Nur Box B, Android TV 13/RK3528 ARM32/Kodi 21.3/Titan BINGIE MOD. **Box A nicht anfassen.** Kein Downgrade, Neuinstallation, Profilreset, DB-/Cache-/Artwork-Löschen, USB/SMB/SD-/Migrations-/Speichertest. Fremder Skinadapter bleibt uninstalliert. Bestehende Profile einschließlich Dynamic-Modus, IR, Favoriten, Startgruppen und Resume weiterverwenden.

## Erste Reihenfolge zwingend

1. `plugin.video.xtreammate-0.1.29.43.zip` und SHA256-Datei aus demselben PR-Stand prüfen. Das Actions-Artefakt ist nur ein Container; daraus das Add-on-ZIP entnehmen. Nach freigegebenem Merge als normales Kodi-ZIP-Update über .42 installieren.
2. **PREP43-01 – NOT_TESTED:** installierte Version .43, `live_exit_fullscreen42` auf B weiterhin EIN, Artwork weiterhin Dynamisch und vorhandene Daten vorhanden. Den Schalter nicht probeweise AUS testen; sein Default bleibt für unberührte Profile AUS.
3. **START43-01** aus der Liste unten. Dann **MINIFLICKER43-01:** Mini-EPG eine Minute offen, höchstens ein grüner Fokusrahmen, kein Zeilenflackern/Geistertext (NOT_TESTED).
4. **LIVE43-01:** einmal Back aus blankem Live-Vollbild, Bild UND Ton enden, Ansicht/IR bedienbar. **Erst bei PASS VOD43-01:** Film-Back. Bei Freeze/STOP_TIMEOUT sofort STOP, keine weitere Stop-Recovery oder Testserie.
5. Nur nach PASS zusätzliche fünf → danach zwanzig Live-Zyklen. Danach restliche Medien-/Such-/Artwork-/Widget-/EPG-/Bestandstests. Alte Reihenfolge Film vor Live aus der historischen .41-Liste wird für .43 ausdrücklich ersetzt.

## Neue Medien- und Renderinggates

Jede Zeile einzeln protokollieren; API-/Providerdaten fehlen → NOT_TESTED oder begründet BLOCKED, niemals einen positiven Dummytest eintragen. Für Vergleiche reale Titel verwenden, keine private Provideradresse veröffentlichen.

| Gate | Schritte / erwartetes Ergebnis | Status |
|---|---|---|
| MINIFLICKER43-01 | Mini mindestens 1 Minute offen. Nur tatsächliche Änderungen zeichnen sichtbar, niemals mehrere grüne Rahmen; Foto/kurzes Video nur ohne private Daten. | NOT_TESTED |
| MINIFLICKER43-02 | Rechts bis letzte Sendung, wieder hoch, 20 Öffnen/Schließen/Senderwechsel; Fokus und NOW unabhängig, keine alten Texte. | NOT_TESTED |
| MINIFLICKER43-03 | Natürlicher EPG-Refresh/Programmrollover: markierte Sendung bleibt identisch, NOW wandert korrekt, kein Rücksprung in Vergangenheit. | NOT_TESTED |
| MED43-01 | Filme UND Serien über 240 und möglichst 500 echte Titel vor/zurück durchsuchen. Fortlaufende IDs/Titel, echter Gesamtzähler und Katalogende, keine Wiederholung/fehlende Seite. Nur vorhandene Gruppen verwenden. | NOT_TESTED |
| MED43-02 | Letzte Teilseite, leere/kleine Kategorie falls vorhanden, Kategorie/Detail/Back. Markierter Titel und Scrollposition stimmen. Kein künstliches Löschen/Ändern des Katalogs. | NOT_TESTED |
| MED43-03 | Provider aktualisiert natürlich während Paging: kein Mix alter/neuer Seiten, Fokus-ID erhalten. Ohne natürlichen Fall NOT_TESTED. | NOT_TESTED |
| SEARCH43-01 | Rock/Rocky, Thriller/Western/Sci-Fi in Live/Film/Serie. 20 Tabwechsel: keine verlorenen Treffer, kein 48→0→48, gleiche freigegebene Suchmaske/Cover/Fokus. | NOT_TESTED |
| SEARCH43-02 | Laufenden echten Programmtitel UND separat Sendername suchen. Frühe Senderergebnisse nicht als Programmtitelmatch zählen. Query/Tab/Back und Play/Return korrekt. | NOT_TESTED |
| SEARCH43-03 | Vorhandene Sprache/Jahr/Genre/Qualität/Staffelzahl/Portal vergleichen. Fehlende Werte bleiben aus; keine aus Titeltext geratenen Daten. | NOT_TESTED |
| ART43-01 | Bei Film Details → Links → Cover/Bild suchen und zuordnen. Provider-Kandidaten, explizite Vorschau, zurück und Abbrechen: ursprüngliche Cover/Metadaten bleiben. Auch Serie prüfen. | NOT_TESTED |
| ART43-02 | Ein eigenes gültiges Providerbild wählen, Vorschau → Bild übernehmen → Speichern. Unmittelbar Detail/Liste/Suche/Widget kontrollieren. Nach Kodi-Neustart weiterhin gewählt. Nur einzelne explizite Auswahl wird lokal gespeichert, Dynamic bleibt aktiv. | NOT_TESTED |
| ART43-03 | Im selben Dialog Rolle Poster/Hintergrund/Ersatz wechseln; Speichern erst nach erneuter Übernahme. Reset der eigenen Bildzuordnung nur auf ausdrücklichen Wunsch: Referenz zurück auf Provider, kein physisches Bildlöschen. | NOT_TESTED |
| ART43-04 | TMDb ist standardmäßig AUS. Ohne Aktivierung kein APIaufruf; fehlender Token klar gemeldet. Optional mit eigenem gültigem Read-Token einschalten, Aladdin 1992/2019 unterscheiden, richtige Werk-ID/Jahr und Herkunft. Token niemals screenshotten/loggen. | NOT_TESTED |
| ART43-05 | TMDb-Personensuche: Person klar erkennbar, Bild nur ausdrücklich als Ersatz wählen; keine Filmmetadatenübernahme. Commons: freie Lizenz/Autor/Dateiseite sichtbar, keine Filmmetadaten. | NOT_TESTED |
| ART43-06 | Metadaten separat: einzelne Felder auswählen, Vorher/Nachher prüfen, Bestätigung abbrechen, danach bewusst bestätigen. Medien-/Portal-ID und Titel unverändert; Resume/Favoriten erhalten. Manuelle Felder wirken noch nicht vollständig auf Genre-/Suchindex. | NOT_TESTED |
| ART43-07 | Gezieltes Poster erneut laden bei Dynamic öffnet Auswahl; einzelner fehlerhafter Kandidat zeigt festen Fehlercode, Quellenwechsel/Back bleibt möglich. Keine globale Queue-/Cache-Reparatur auslösen. | NOT_TESTED |
| ART43-08 | Optional lokale einzelne PNG/JPEG-Datei importieren: Vorschau, Abbrechen, Originaldatei erhalten; dann explizit speichern. Keine USB-/SMB-/Speicherprobe; bei fehlender lokaler Datei NOT_TESTED. | NOT_TESTED |
| ART43-09 | Während laufender Anfrage zurück/schließen, danach erneut öffnen; späte Ergebnisse landen nicht im falschen Titel/Portal. Eigenes Fenster bleibt IR-bedienbar, keine fremden Dialoge schließen. | NOT_TESTED |
| ART43-10 | Optionalen automatischen TMDb-Fallback separat EIN, nur fehlendes Providerposter + exakter Titel/Jahr/ein Werk. Bei Mehrdeutigkeit nichts automatisch übernehmen. Nach Test gewünschten Benutzerschalter beibehalten; keine globalen Defaults ändern. | NOT_TESTED |
| ART43-11 | Bestehende dynamische Cover 30/60/120s, Kategorie-/Suchtab-/Playerwechsel und Neustart. Interne Altbilder/Queue unangetastet; Box A nicht prüfen. | NOT_TESTED |
| WIDGET43-01 | Eigene neueste Filme/Serien-Verzeichnisrouten mit echten Einträgen öffnen, Detail-ID/Fokus, ausgewählte manuelle Bilder und normale Providercover korrekt. Bestehende BINGIE-Reihen nur ansehen, keine XML-/Skininstallation. Externen Skinshortcuts-Fehler separat FAIL/BLOCKED dokumentieren. | NOT_TESTED |

## Gesamte bisherige Funktionsabnahme, auf .43 erneut ausführen

Die folgenden IDs sind zur laufenden Version übertragen, keine übernommenen Geräte-PASS. Bei P0-Abbruch bleiben die restlichen Gates BLOCKED; ausgeschlossene Neuinstallations-/Adapter-/Negativfälle bleiben begründet NOT_TESTED. Keine Befugnis zu Box-A-/Reset-/Fremdskin-Tests aus diesen historischen Anforderungen ableiten.

## Protokoll

Checkbox erst bei tatsächlich beobachtetem PASS setzen; Status jeGate auf PASS/FAIL/BLOCKED/NOT_TESTED ändern. Version/Datum/Pfad, Eingabe→sichtbar/Stop→Return, erwartetes und beobachtetes Ergebnis notieren. Private Logs nicht öffentlich hochladen; nur bereinigte feste Stage/Reason-/Window-/Thread-/Timingwerte. Fehlende Reproduktion oder gesperrte Adapterinstallation ist kein PASS.

## START

- [ ] **START43-01** – Normaler XCMate-/Kodi-Start: gespeicherter Startsender startet genau einmal, richtige Startgruppe, Profil Dynamisch und bestehende Navigation erhalten. **Status: NOT_TESTED**

## P0 KURZTESTS – Reihenfolge zwingend

- [ ] **VOD43-01** – Film aus Katalog starten, kurze echte Wiedergabe, sichtbares OSD mit Back verstecken, blankes Vollbild mit Back beenden; eigener Stop und richtige Herkunft/Fokus. .40-5m-Teil-PASS erhalten. **Status: NOT_TESTED**
- [ ] **LIVE43-01** – Live-TV einmal starten, anschließend aus reinem Vollbild einmal Back92: Stream endet und Herkunft/Home wird bedienbar. Genau ein nativer Stoppost und passende Barriere. Bei Freeze/Timeout sofort Testabbruch. **Status: NOT_TESTED**
- [ ] **LIVE43-02** – Nur nach LIVE43-01 PASS: fünf weitere Live-Back-Zyklen, jeweils Start/Back/Return und IR-Reaktion notieren. Bei einem Fehler abbrechen. **Status: NOT_TESTED**
- [ ] **LIVE43-03** – Nur nach allen fünf PASS:20 reguläre Live-Back-/Stop-Zyklen, verschiedene verfügbare Sender/Formate soweit sinnvoll. Keine absichtlich20fach provozierten Totalhänger. **Status: NOT_TESTED**
- [ ] **LIVE43-04** – Backzustände einzeln: Mini/Senderliste→blankes Video ohne Stop; Gruppen→Senderliste; Info→ausblenden; Optionen→Player; Player→Info; großes EPG→vorige Ansicht. Back niemals deaktiviert. **Status: NOT_TESTED**
- [ ] **LIVE43-05** – Schnelle IR-Repeats und Stop nach Senderwechsel: kein doppelter Stop/Play, keine fremde Player-/Modalsitzung stoppen oder wegnavigieren. Keine zweite Recovery-Stop-Aktion bei Timeout. **Status: NOT_TESTED**

## Film/Serie und bestehende Funktionen

- [ ] **VOD43-02** – Film aus Suchergebnis, Episode aus Staffel und aus Suche starten; korrekt abspielen und per Back/Stop zurück zu Query/Tab/Staffel/Fokus/Scroll. **Status: NOT_TESTED**
- [ ] **VOD43-03** – Resume/Gesehen mit vorhandenem ausreichend langen Medium: Position speichern, später fortsetzen; bestehende Fortschritte nicht löschen. **Status: NOT_TESTED**
- [ ] **VOD43-04** – Natürliches Episodenende startet nächste gültige Folge einschließlich Staffelwechsel; manuelles Stop/Back verhindert Autoplay. Manueller Next funktioniert. **Status: NOT_TESTED**
- [ ] **VOD43-05** – Früheren Movies-Hänger nur bei natürlichem Auftreten gesondert erfassen: Home/Movies-Ansicht, Auswahl, OpenFile und Exitzeit getrennt. Nicht den neuen Live-Stop zum Beweis eines generellen VOD-Fehlers machen. **Status: NOT_TESTED**

## Mini-EPG Layout und Zeitfenster

- [ ] **MINIVIS-01** – Nur eine sichtbare Zeit-/Titeltextebene, native Liste mit IR/OK/Scroll bedienbar. Keine doppelt gezeichneten Zeilen. **Status: NOT_TESTED**
- [ ] **MINIVIS-02** – Lange und nichtlateinische Titel höchstens zweizeilig, keine Nachbarzeilenüberlagerung.720p/1080p soweit verfügbar separat erfassen. **Status: NOT_TESTED**
- [ ] **MINIVIS-03** – Mehr als fünf Programme durchscrollen, NOW dauerhaft unabhängig vom Auswahlfokus; kein Kanalstart durch bloßen Fokus. **Status: NOT_TESTED**
- [ ] **MINIVIS-04** – 20 Öffnen/Schließen und Senderwechsel: keine Geistertexte, korrekte Auswahl, keine späte alte SID. **Status: NOT_TESTED**
- [ ] **MINIVIS-05** – Reales Kodi21.3/BINGIE-Foto oder Benutzerbeobachtung des finalen Layouts; Hostmodell ist kein visueller Geräte-PASS. **Status: NOT_TESTED**
- [ ] **FUTURE43-01** – Mini zunächst Jetzt/Danach/Zukunft, nach regulärer Hintergrundaktualisierung weiterhin Zukunft; Vergangenheit verdrängt nichts. Keine neuen Quellen oder künstlichen Datenreset nutzen. **Status: NOT_TESTED**
- [ ] **FUTURE43-02** – Identischer Sender/Zeitpunkt einschließlich bestehendem manuellem Mapping: Mini/Info/großes Raster stimmen bei NOW/NEXT überein, verschiedene Zukunftshorizonte zulässig. **Status: NOT_TESTED**
- [ ] **FUTURE43-03** – Natürlicher Programmwechsel/Mitternacht und20 schnelle Senderwechsel: korrekter Zeitrollover, kein veralteter Worker überschreibt neue Auswahl. **Status: NOT_TESTED**

## Widgets – Datenbackend separat von fremder Skinintegration

- [ ] **WIDGETMEDIA-01** – Die vorhandenen Quellen Neueste Filme/Serien als eigene Kodi-Verzeichnisse öffnen: begrenzte echte Einträge oder verständliche temporäre Fehlendanzeige, kein IndexReadError-Dispatchcrash. **Status: NOT_TESTED**
- [ ] **WIDGETMEDIA-02** – Bestehende Film-/Serien-Home-Reihen getrennt öffnen, kein XML-/Buildfehler; bei SkinShortcuts-Fehler exakte Eingabe/Stack privat sichern, keinen Skinreset durchführen. **Status: NOT_TESTED**
- [ ] **WIDGETMEDIA-03** – Kalt/Warm/Neustart,20 Fokus-/Refresh-/Backwege, bestehende Widget-/Shortcutkonfiguration erhalten. **Status: NOT_TESTED**
- [ ] **WIDGETMEDIA-04** – Filmitem öffnet richtigen Filmdetail, Serienitem Staffel-/Episodendetails; Stream nur durch ausdrückliche Wiedergabeaktion. **Status: NOT_TESTED**
- [ ] **WIDGETMEDIA-05** – Fehlender/offline/unvollständiger Index bleibt bedienbar und verständlich; keine künstliche DB-Sperre/Korruption auf Box B erzeugen. Negativfälle ohne natürliches Beispiel NOT_TESTED. **Status: NOT_TESTED**
- [ ] **WIDGETLIVE-01** – Nach gesonderter Adapterfreigabe: kleine zentrierte Logos, kompakte Reihe, proportionales Bild ohne Cropping; Ziel80×45 in160×90, realen Altvergleich notieren. **Status: NOT_TESTED**
- [ ] **WIDGETLIVE-02** – Zehn vorhandene Sender mit EPG: D-Pad-Fokus zeigt eigene NOW/NEXT/Uhrzeiten/echten Progress, natürliche Eventgrenze korrekt; keine Daten des vorherigen Senders. **Status: NOT_TESTED**
- [ ] **WIDGETLIVE-03** – Sender ohne EPG ehrliches fehlend, gleicher gespeicherter Snapshot/Mapping wie großes EPG. Keine Fantasieprogramme/Watch-Prozentwerte. **Status: NOT_TESTED**
- [ ] **WIDGETLIVE-04** – 20 schnelle Fokuswechsel ohne Popup/Tune/HTTP proFokus, danach OK startet genau ausgewählten Sender, Back/Return korrekt. **Status: NOT_TESTED**
- [ ] **WIDGETLIVE-05** – Versions-/ID-/XML-Preflight und reversibler Einbindeort genehmigt. Ohne ausdrückliche Freigabe keinen fremden Skin ändern: Gate bleibt NOT_TESTED; Adaptercode BLOCKED_APPROVAL. **Status: NOT_TESTED**

## Einmaliger Versionshinweis

- [ ] **UPDATE-NOTICE-01** – Neue Installation nur auf separat erlaubtem leeren Testprofil: Baseline ohne falschen Upgradehinweis. Box A/B dafür niemals zurücksetzen. **Status: NOT_TESTED**
- [ ] **UPDATE-NOTICE-02** – Tatsächliches .40→.43-Update auf B: exakt eine sichtbare Meldung mit installierter .43 aus Kodi, OK oder Back quittiert. Vorhandener .42-Servicebuild als Legacybeleg protokolliert, kein erzwungener Profilreset. **Status: NOT_TESTED**
- [ ] **UPDATE-NOTICE-03** – Kodi zweimal normal neu starten und Add-on mehrfach öffnen: nach Bestätigung keine Wiederholung. **Status: NOT_TESTED**
- [ ] **UPDATE-NOTICE-04** – Laufendes Live-/Filmvideo und native Modals werden nicht unterbrochen; Meldung erst am sicheren Home-/Videos-Zeitpunkt. Keine Serviceblockade/Playeraktion zum Erzwingen der Anzeige. **Status: NOT_TESTED**
- [ ] **UPDATE-NOTICE-05** – Host prüft Versionssprung, Downgrade, Corruption, Parallelität und Stromverlustfenster. Keine echte Downgrade-/Stromausfall-/Dateikorruption auf B provozieren; echte ungeprüfte Varianten NOT_TESTED. **Status: NOT_TESTED**
- [ ] **UPDATE-NOTICE-06** – Native Lesbarkeit/OK/Back in Kodi21.3/BINGIE720p/1080p, normales Update perZIP; keine fremde Fokusübernahme. **Status: NOT_TESTED**

## Regression und Bestand

- [ ] **REG43-01** – Rock/Rocky in Live/Filmen/Serien,20 schnelle Reiterwechsel/Paging: bestätigte Treffer/Cover/Fokus erhalten; kein48→0→48-Pending-Flackern. **Status: NOT_TESTED**
- [ ] **REG43-02** – Erstes OK Live-Info, zweites OK Player; große Buttons und echte Bild-/Ton-/Untertitelinfos, fehlende Daten unbekannt, native OSD-Fallbacks nur bei echter Reproduktion bewerten. **Status: NOT_TESTED**
- [ ] **REG43-03** – Links/Rückwege mit Gruppen+schmaler Icon-Leiste, großer EPG-Senderstart/Return, Startsender/-gruppe und Fernbedienung unverändert. **Status: NOT_TESTED**
- [ ] **REG43-04** – Dynamische Cover bei30/60/120s, Kategorie-/Tab-/Playerwechsel erhalten. Keine Archivierung/Migration oder Massendownloads. **Status: NOT_TESTED**
- [ ] **REG43-05** – Portale, Gruppen, EPG-Mappings, Favoriten, Resume/Gesehen, Originalicon, Skin und Remoteprofil nach regulärem Neustart unverändert. Keine zusätzliche Inventur auf Box A. **Status: NOT_TESTED**

## Einzeln abhakbare sichere Wiederholungsfolge

Jede Stufe erst nach vollständigem PASS der vorigen. Bereits ein Hänger stoppt die Serie.

- [ ] Ein erster Live-Back: NOT_TESTED
- [ ] Zusatzzyklus5-1: NOT_TESTED
- [ ] Zusatzzyklus5-2: NOT_TESTED
- [ ] Zusatzzyklus5-3: NOT_TESTED
- [ ] Zusatzzyklus5-4: NOT_TESTED
- [ ] Zusatzzyklus5-5: NOT_TESTED
- [ ] Stabilitätszyklus20-01: NOT_TESTED
- [ ] Stabilitätszyklus20-02: NOT_TESTED
- [ ] Stabilitätszyklus20-03: NOT_TESTED
- [ ] Stabilitätszyklus20-04: NOT_TESTED
- [ ] Stabilitätszyklus20-05: NOT_TESTED
- [ ] Stabilitätszyklus20-06: NOT_TESTED
- [ ] Stabilitätszyklus20-07: NOT_TESTED
- [ ] Stabilitätszyklus20-08: NOT_TESTED
- [ ] Stabilitätszyklus20-09: NOT_TESTED
- [ ] Stabilitätszyklus20-10: NOT_TESTED
- [ ] Stabilitätszyklus20-11: NOT_TESTED
- [ ] Stabilitätszyklus20-12: NOT_TESTED
- [ ] Stabilitätszyklus20-13: NOT_TESTED
- [ ] Stabilitätszyklus20-14: NOT_TESTED
- [ ] Stabilitätszyklus20-15: NOT_TESTED
- [ ] Stabilitätszyklus20-16: NOT_TESTED
- [ ] Stabilitätszyklus20-17: NOT_TESTED
- [ ] Stabilitätszyklus20-18: NOT_TESTED
- [ ] Stabilitätszyklus20-19: NOT_TESTED
- [ ] Stabilitätszyklus20-20: NOT_TESTED


## Ergebnis und Schutz

Pro Gate: Version, Datum/Uhrzeit Europe/Berlin, Gerät/Kodi, Setting EIN, Eingabe, erwartetes und beobachtetes Verhalten, PASS/FAIL/BLOCKED/NOT_TESTED. Private Rohlogs niemals auf GitHub; nur anonymisierte feste Phasen/Reason-/Zeitwerte. API-Token, Provider- und SMB-Adressen auslassen.

Alle ursprünglichen .41-Funktionen und .42-Gates sind damit fortgeführt. UPDATE-NOTICE-02 gilt jetzt für tatsächliches .42→.43 und genau eine Meldung .43. Leeres Neuinstallationsprofil oder fremder Widgetadapter benötigt weiter einen separaten Auftrag und ist kein durchzuführender .43-Test auf Box B. Offene EPG-Zuweisung/Hub, Fernbedienungslernen, Storage, Downloads und Aufnahmen bleiben DEFERRED.

Ein Main-Merge ist keine Android-Abnahme und schließt kein Issue. Nach dem ausdrücklich freigegebenen Merge prüft der Nutzer Box B; tatsächliche Einzelresultate werden den jeweiligen Issues zugeordnet. Kein automatisches Release und kein pauschaler Gesamt-PASS.
