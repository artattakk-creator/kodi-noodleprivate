# XCMate .41 – Android-Installation und Abnahme Box B

Stand26.10.2026. **Alle neuen Android-Testfälle NOT_TESTED.** Host/CI ist kein Geräte-PASS. Die `.40`-Historie bleibt separat: ein echter Film-Back-Teil-PASS nach5m27s, aber Live-Back P0 FAIL und Mini-Textüberlagerung FAIL (#212). Kein genereller VOD-Fail behauptet.

**Box A vollständig ausgeschlossen.** B bleibt Android RK3528 ARM32, Kodi21.3, Titan BINGIE MOD2.2.3, Artwork Dynamisch. Keine Deinstallation, kein Downgrade, kein Profil-/Cache-/DB-Reset, keine Portal-/Mappingänderung, keine USB-/SD-/SMB-/Speicher-/Migrations-/Löschtests.

## Manuelles reguläres Update

1. Test-ZIP und SHA256 aus dem Draft herunterladen und vergleichen. Nur `plugin.video.xtreammate-0.1.29.41.zip` als normales Kodi-ZIP-Update installieren, nicht den CI-Artefaktcontainer und nicht das separate Skin-Adapter-Review-ZIP.
2. Add-on-Version .41 und bestehenden Dynamisch-Modus kontrollieren; gespeicherte Profile weiterverwenden. Der Versionshinweis wartet bei aktiver Wiedergabe auf einen sicheren Zeitpunkt.
3. Reihenfolge zwingend: START41-01 → VOD41-01 → LIVE41-01 (einmal) → bei PASS LIVE41-02 (fünfmal) → erst danach LIVE41-03 (20 Zyklen).
4. **Bei einem vollständigen Kodi-Hänger oder STOP_TIMEOUT/STOP_POST_UNCONFIRMED sofort abbrechen.** Keine zweite Stop-Recovery und keine20 Totalausfälle provozieren. Weitere kritische Gates dann BLOCKED dokumentieren. Keine automatische Geräteaktion durch Codex.
5. BINGIE-Adapter bleibt standardmäßig aus/uninstalliert. Er benötigt gesonderte ausdrückliche Freigabe und Preflight einer Kopie. Bestehende Widgets können ohne Änderung geprüft werden; fremde Skin-/Shortcut-Fehler nicht durch Neuinstallation/Reset umgehen.

## Protokoll

Checkbox erst bei tatsächlich beobachtetem PASS setzen; Status jeGate auf PASS/FAIL/BLOCKED/NOT_TESTED ändern. Version/Datum/Pfad, Eingabe→sichtbar/Stop→Return, erwartetes und beobachtetes Ergebnis notieren. Private Logs nicht öffentlich hochladen; nur bereinigte feste Stage/Reason-/Window-/Thread-/Timingwerte. Fehlende Reproduktion oder gesperrte Adapterinstallation ist kein PASS.

## START

- [ ] **START41-01** – Normaler XCMate-/Kodi-Start: gespeicherter Startsender startet genau einmal, richtige Startgruppe, Profil Dynamisch und bestehende Navigation erhalten. **Status: NOT_TESTED**

## P0 KURZTESTS – Reihenfolge zwingend

- [ ] **VOD41-01** – Film aus Katalog starten, kurze echte Wiedergabe, sichtbares OSD mit Back verstecken, blankes Vollbild mit Back beenden; eigener Stop und richtige Herkunft/Fokus. .40-5m-Teil-PASS erhalten. **Status: NOT_TESTED**
- [ ] **LIVE41-01** – Live-TV einmal starten, anschließend aus reinem Vollbild einmal Back92: Stream endet und Herkunft/Home wird bedienbar. Genau ein nativer Stoppost und passende Barriere. Bei Freeze/Timeout sofort Testabbruch. **Status: NOT_TESTED**
- [ ] **LIVE41-02** – Nur nach LIVE41-01 PASS: fünf weitere Live-Back-Zyklen, jeweils Start/Back/Return und IR-Reaktion notieren. Bei einem Fehler abbrechen. **Status: NOT_TESTED**
- [ ] **LIVE41-03** – Nur nach allen fünf PASS:20 reguläre Live-Back-/Stop-Zyklen, verschiedene verfügbare Sender/Formate soweit sinnvoll. Keine absichtlich20fach provozierten Totalhänger. **Status: NOT_TESTED**
- [ ] **LIVE41-04** – Backzustände einzeln: Mini/Senderliste→blankes Video ohne Stop; Gruppen→Senderliste; Info→ausblenden; Optionen→Player; Player→Info; großes EPG→vorige Ansicht. Back niemals deaktiviert. **Status: NOT_TESTED**
- [ ] **LIVE41-05** – Schnelle IR-Repeats und Stop nach Senderwechsel: kein doppelter Stop/Play, keine fremde Player-/Modalsitzung stoppen oder wegnavigieren. Keine zweite Recovery-Stop-Aktion bei Timeout. **Status: NOT_TESTED**

## Film/Serie und bestehende Funktionen

- [ ] **VOD41-02** – Film aus Suchergebnis, Episode aus Staffel und aus Suche starten; korrekt abspielen und per Back/Stop zurück zu Query/Tab/Staffel/Fokus/Scroll. **Status: NOT_TESTED**
- [ ] **VOD41-03** – Resume/Gesehen mit vorhandenem ausreichend langen Medium: Position speichern, später fortsetzen; bestehende Fortschritte nicht löschen. **Status: NOT_TESTED**
- [ ] **VOD41-04** – Natürliches Episodenende startet nächste gültige Folge einschließlich Staffelwechsel; manuelles Stop/Back verhindert Autoplay. Manueller Next funktioniert. **Status: NOT_TESTED**
- [ ] **VOD41-05** – Früheren Movies-Hänger nur bei natürlichem Auftreten gesondert erfassen: Home/Movies-Ansicht, Auswahl, OpenFile und Exitzeit getrennt. Nicht den neuen Live-Stop zum Beweis eines generellen VOD-Fehlers machen. **Status: NOT_TESTED**

## Mini-EPG Layout und Zeitfenster

- [ ] **MINIVIS-01** – Nur eine sichtbare Zeit-/Titeltextebene, native Liste mit IR/OK/Scroll bedienbar. Keine doppelt gezeichneten Zeilen. **Status: NOT_TESTED**
- [ ] **MINIVIS-02** – Lange und nichtlateinische Titel höchstens zweizeilig, keine Nachbarzeilenüberlagerung.720p/1080p soweit verfügbar separat erfassen. **Status: NOT_TESTED**
- [ ] **MINIVIS-03** – Mehr als fünf Programme durchscrollen, NOW dauerhaft unabhängig vom Auswahlfokus; kein Kanalstart durch bloßen Fokus. **Status: NOT_TESTED**
- [ ] **MINIVIS-04** – 20 Öffnen/Schließen und Senderwechsel: keine Geistertexte, korrekte Auswahl, keine späte alte SID. **Status: NOT_TESTED**
- [ ] **MINIVIS-05** – Reales Kodi21.3/BINGIE-Foto oder Benutzerbeobachtung des finalen Layouts; Hostmodell ist kein visueller Geräte-PASS. **Status: NOT_TESTED**
- [ ] **FUTURE41-01** – Mini zunächst Jetzt/Danach/Zukunft, nach regulärer Hintergrundaktualisierung weiterhin Zukunft; Vergangenheit verdrängt nichts. Keine neuen Quellen oder künstlichen Datenreset nutzen. **Status: NOT_TESTED**
- [ ] **FUTURE41-02** – Identischer Sender/Zeitpunkt einschließlich bestehendem manuellem Mapping: Mini/Info/großes Raster stimmen bei NOW/NEXT überein, verschiedene Zukunftshorizonte zulässig. **Status: NOT_TESTED**
- [ ] **FUTURE41-03** – Natürlicher Programmwechsel/Mitternacht und20 schnelle Senderwechsel: korrekter Zeitrollover, kein veralteter Worker überschreibt neue Auswahl. **Status: NOT_TESTED**

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
- [ ] **UPDATE-NOTICE-02** – Tatsächliches .40→.41-Update auf B: exakt eine sichtbare Meldung mit installierter .41 aus Kodi, OK oder Back quittiert. Vorhandener .40-Servicebuild als Legacybeleg protokolliert, kein erzwungener Profilreset. **Status: NOT_TESTED**
- [ ] **UPDATE-NOTICE-03** – Kodi zweimal normal neu starten und Add-on mehrfach öffnen: nach Bestätigung keine Wiederholung. **Status: NOT_TESTED**
- [ ] **UPDATE-NOTICE-04** – Laufendes Live-/Filmvideo und native Modals werden nicht unterbrochen; Meldung erst am sicheren Home-/Videos-Zeitpunkt. Keine Serviceblockade/Playeraktion zum Erzwingen der Anzeige. **Status: NOT_TESTED**
- [ ] **UPDATE-NOTICE-05** – Host prüft Versionssprung, Downgrade, Corruption, Parallelität und Stromverlustfenster. Keine echte Downgrade-/Stromausfall-/Dateikorruption auf B provozieren; echte ungeprüfte Varianten NOT_TESTED. **Status: NOT_TESTED**
- [ ] **UPDATE-NOTICE-06** – Native Lesbarkeit/OK/Back in Kodi21.3/BINGIE720p/1080p, normales Update perZIP; keine fremde Fokusübernahme. **Status: NOT_TESTED**

## Regression und Bestand

- [ ] **REG41-01** – Rock/Rocky in Live/Filmen/Serien,20 schnelle Reiterwechsel/Paging: bestätigte Treffer/Cover/Fokus erhalten; kein48→0→48-Pending-Flackern. **Status: NOT_TESTED**
- [ ] **REG41-02** – Erstes OK Live-Info, zweites OK Player; große Buttons und echte Bild-/Ton-/Untertitelinfos, fehlende Daten unbekannt, native OSD-Fallbacks nur bei echter Reproduktion bewerten. **Status: NOT_TESTED**
- [ ] **REG41-03** – Links/Rückwege mit Gruppen+schmaler Icon-Leiste, großer EPG-Senderstart/Return, Startsender/-gruppe und Fernbedienung unverändert. **Status: NOT_TESTED**
- [ ] **REG41-04** – Dynamische Cover bei30/60/120s, Kategorie-/Tab-/Playerwechsel erhalten. Keine Archivierung/Migration oder Massendownloads. **Status: NOT_TESTED**
- [ ] **REG41-05** – Portale, Gruppen, EPG-Mappings, Favoriten, Resume/Gesehen, Originalicon, Skin und Remoteprofil nach regulärem Neustart unverändert. Keine zusätzliche Inventur auf Box A. **Status: NOT_TESTED**

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

## Mess- und Freigabegrenzen

PLAYER_STOP_START kennzeichnet nun das Posting des eigenen Live-Stop-Befehls; NATIVE_STOP_POSTED ist kein STOP_DONE. Nur die passende nachfolgende Main-Queue-Barriere bestätigt die native Rückkehr. STOP_TIMEOUT bleibt auch nach LATE_NATIVE_RETURN fehlgeschlagen; kein Home-Erfolg vortäuschen. MediaCodec-/AudioTrack-/Rendererfehler getrennt zu den XCMate-Stopereignissen erfassen. VOD verwendet unverändert den .40-Pfad.

P0 Live-Back ist zwingendes Freigabegate. Film/Serie, Resume und Autoplay danach separat abnehmen. Widget-SQL und fremde Skinshortcuts/XML sind verschiedene Fehlerklassen. Live-Fokuslayout im optionalen Adapter bis Freigabe/Renderingprüfung BLOCKED, alle .41-Gerätegates bleiben zunächst NOT_TESTED.

Kein Merge/Release/Issue-Close ohne ausdrückliche Nutzerfreigabe nach tatsächlicher Abnahme. Keine Keymap-/Skin-/Remote-Featureausweitung aus neuem Backlog #64 innerhalb dieses Stabilisierungspatches.
