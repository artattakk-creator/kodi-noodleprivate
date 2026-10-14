# XCMate – Roadmap, Bugliste und Release-Checkliste

**Statusdatum:** 14.10.2026 · letzter geprüfter veröffentlichter Stand: 0.1.12.  
Labels: [RELEASED] in GitHub gebaut; [ON-DEVICE OPEN] Nutzergerätetest fehlt/negativ; [PLANNED] nur spezifiziert.

## Priorisierung

| Prio | Thema | Status | Nächster konkreter Schritt |
| --- | --- | --- | --- |
| P0 | Startsender aus Portalstartseite | [ON-DEVICE OPEN] | Android: direkt WELT starten; leere Verzeichnisansicht darf nicht erscheinen; Kodi-Log analysieren |
| P0 | Android TV-Fernbedienung Links/Hoch/Runter/OK und Zusatzmenü | [ON-DEVICE OPEN] | Native Action-ID per Diagnose/Anlernmodus prüfen; LiveNavigator-Fokus und BINGIE MOD testen |
| P0 | Senderliste sofort öffnen | [ON-DEVICE OPEN] | Warmcache messen; wiederholter Aufruf aus Vollbild ohne Serverwartezeit |
| P1 | Serien-Fortschritt, gesehen, fortsetzen, Auto-Next | [PLANNED] | Implementieren gemäß SERIES_PROGRESS_SPEC_DE.md und Android-Tests |
| P1 | EPG in Senderliste, Jetzt/Danach und manuelle XMLTV-Zuordnung | [RELEASED, ON-DEVICE OPEN] | Mit echten Daten Sender-ID-Mapping und Sichtbarkeit prüfen |
| P1 | Freigegebenes Bildpaket in Kodi integrieren | [DESIGN APPROVED / INTEGRATION OPEN] | Originale ins Repo, Assets referenzieren, ZIP und Anzeige prüfen |
| P1 | Frei wählbare XCMate-UI-Farben; Default edles Grau | [PLANNED] | Persistente Einstellung + TV-OSD-Theme + Kontrasttests |
| P2 | BINGIE MOD Sendergruppen-Widgets und Programminfo-Hover | [RELEASED, ON-DEVICE OPEN] | Skin-Widget-Typ prüfen, Fokus-Infopanel testen |
| P2 | Neueste Filme/Serien, Beschreibungen/YouTube-Trailer | [RELEASED, ON-DEVICE OPEN] | Providerfelder, Metadaten & Kodi-YouTube-Erreichbarkeit prüfen |

## Vor jedem Release

1. `addon.xml`-Version erhöhen, Ziel-ID `plugin.video.xtreammate` beibehalten, Name **XCMate**; Installer- und XML-Katalogversion müssen übereinstimmen.
2. Keine aktiven Zugangsdaten, privaten URLs, Tokens, Portalprofile oder realen Logs in Commit, Testdaten oder ZIP.
3. Python `compileall` + `python -m unittest discover -s tests -v` (CI), neue Tests für die Änderung; nicht nur String-/Mock-Tests als Android-End-to-End-Nachweis werten.
4. `.github/workflows/publish.yml` muss erfolgreich durchlaufen; danach existieren tatsächlich `plugin.video.xtreammate/plugin.video.xtreammate-VERSION.zip`, `addons.xml`, `addons.xml.md5`.
5. Beim Upgrade aus der Vorversion unveränderte Portale/Gruppen/Tasten/EPG/Startsender belegen; Kodi nicht deinstallieren und Profile nicht löschen.
6. Android-Test: WELT/anderen gespeicherten Sender starten, Links/Links, Up/Down, OK/OK, Guide, Zurück, Audio/Video, Streaming-Stop, wiederholter Cache-Aufruf.
7. Serien-Funktion zusätzlich: bookmark, resume, watched, next, Ende vs manuelles Stop, Doppelereignisse, Offline/Kodi-Neustart.
8. UI: echtes Kodi/Titan BINGIE MOD, 10-Foot-View, Standardgrau, Fokusrahmen, lesbare EPG-Infos.
9. Erfolgsbericht trennt **CI-Grün**, **GitHub-ZIP vorhanden** und **Android-Gerätetest bestanden** ausdrücklich.

## Diagnostik und Mindestdaten vom Testgerät

Kodi-Version und Android-Version erfragen, aber keine Zugangsdaten. Menü `TV-Fernbedienung: Diagnose` verwenden: Tastenbelegung, Xtream-Session, Overlay-Status, letzte Kodi-Taste, zuletzt verarbeitet, Startsender-Status. Fehlerzeilen aus `kodi.log` anonymisieren. Nicht ungefragt ein neues Kodi-Repository oder eine vollständige Neuinstallation verlangen.

## Pflege dieses Projekts

Bei jeder Änderung: Bug und verifizierte Ursache, Dateien, Tests, GitHub Commit-SHA, Action-Run-ID, installierbares ZIP, noch offene Gerätetests und neues nächstes To-do hier nachtragen. Einen neuen Chat stets mit `NEW_CHAT_COPY_BLOCK_DE.md` beginnen.

## 14.10.2026 – P0-Untersuchung / Kandidat 0.1.10

**Quellcodebefund (Android-Log noch nicht verfügbar):** Das bisherige
`play_start` stand als Kodi-`IsPlayable`-Verzeichniseintrag zur Verfügung,
verwendete jedoch direkt `xbmc.Player().play()` statt
`xbmcplugin.setResolvedUrl()`. Beim über `RunPlugin` gestarteten Autoplay
ist dagegen direkte Wiedergabe erforderlich. Beide Kontexte sind im Kandidaten
0.1.10 getrennt (`play_start` / `play_start_direct`). Damit wird eine
plausible Ursache für leere Verzeichnisansichten behoben; der konkrete Fehler
am Zielgerät muss noch durch anonymisierte Kodi-Logs nachgewiesen werden.

**Fernbedienung:** OK führt in der geöffneten Player-Leiste nun die fokussierte
Aktion aus. Ein expliziter Knopf „Weitere“ öffnet Zusatzoptionen. Zapping
übergibt den von `build_playable_item` aufbereiteten Pfad an den Player.
Player-Logmeldungen enthalten keine unmaskierte Stream-URL mehr.

**Tests:** `tests/test_xcmate_p0_playback.py`, angepasste Android-/OSD-Tests;
PR-Workflow ist auf Build/Test ohne Release-Push ausgelegt. Im Releasebericht
Commit, CI-Run, ZIP/Index und Android-Ergebnis separat angeben.

**Offen:** Echtes Android-Gerät mit Titan BINGIE MOD; Startsender manuell und
automatisch je zweimal; Links/Links, Hoch/Runter, OK/Pause, „Weitere“, EPG,
Zurück, Stop, Wiedereinstieg; anonymisierte Kodi-Logzeilen und Diagnosewerte.
Kein Device-Pass ohne protokollierten Nutzergerätetest.

### Verifizierte GitHub-Veröffentlichung 0.1.10

- PR: https://github.com/artattakk-creator/kodi-noodleprivate/pull/2
- PR-CI erfolgreich: Run 38552786543 (Python, Tests, Build).
- Merge-Commit: `77aec9be727182582b5e06a040490215c3df1e4d`.
- Publish-CI erfolgreich: Run 38552874789.
- Generierter Distributions-Commit: `d4174ca391198ad1319b0ddaa046cfd9f66e0a4f`.
- ZIP: `plugin.video.xtreammate/plugin.video.xtreammate-0.1.10.zip`;
  Kodi-Repository-Katalog trägt `id=plugin.video.xtreammate`,
  `name=XCMate`, `version=0.1.10`.
- `addons.xml.md5` unabhängig gegen `addons.xml` berechnet und
  übereinstimmend: `a117cadb3f3ddb84deff45900bfbf69e`.
- Repository-Add-on 1.7.0 unverändert; vorhandene 0.1.9-ZIP bleibt verfügbar.
- **Android-Status: weiterhin offen**. Kein erfolgreicher Startsender-,
  Navigation-/OSD- oder BINGIE-MOD-Gerätetest vorliegend.

## P1 – Fotoverifizierte TiviMate-5.3.3-Fernbedienung (14.10.2026)

- 10 Nutzerfotos der Einstellungen ausgewertet. Exakte, fotografierte Zuordnung in [`TIVIMATE_REMOTE_REFERENCE_2026-10-14_DE.md`](TIVIMATE_REMOTE_REFERENCE_2026-10-14_DE.md).
- Zwei **verschiedene Kontexte**: Player vs. EPG; z. B. Stop = Wiedergabe stoppen (Player), Favoritstatus wechseln (EPG).
- Kurz-/Langdruck-Bindings und sechs Seek-Optionen im Entwurfs-Branch `feat/xcmate-tivimate-remote-profile` als getestete Konstanten hinterlegt.
- Draft-PR [#3](https://github.com/artattakk-creator/kodi-noodleprivate/pull/3), CI erfolgreich: [38557640506](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/38557640506).
- **Noch nicht als Funktion veröffentlicht:** Android-Keyevent-Decoder, Langdruck, EPG-Raster, Vorschaumodus, kontextabhängige Kodi-UI/Fokuswechsel, Speicherung einer vom Benutzer änderbaren Tastenmatrix.
- Keine APK, geschützte Originalgrafik oder Live-Sender-Screenshots in das öffentliche Repository geladen. Gespeicherte Portale, Schlüssel, EPG und bestehende Tastenbelegung unverändert lassen.
- Nächster Schritt: weitere TiviMate-Einstellungsseiten entgegennehmen, Matrix fortführen, XCMate-Controller unabhängig implementieren, Mock-/CI-Test, Gerätetest und eigener Versions-Release.

## P1 – Weitere TV-/EPG-/Film-Ansichten aus Fotos (14.10.2026)

Die zweite TiviMate-5.3.3-Fotoserie ist in
[`TIVIMATE_UI_SCREEN_REFERENCE_2026-10-14_DE.md`](TIVIMATE_UI_SCREEN_REFERENCE_2026-10-14_DE.md)
als Zustands-/Bildschirmreferenz mit 10 Foto-IDs indexiert. Die Player-Farbtasten
wurden im Draft-Branch #3 ergänzt. **Keine Behauptung einer identisch
implementierten Kodi-Oberfläche**: EPG-Zeitraster, Preview, Hauptmenü,
Karussell und Filmkatalog-Layout sind zunächst referenziert, nicht umgesetzt.
Die QA muss die tatsächlichen Taste-zu-Zustand-Übergänge und Fokus-Führung
auf Android belegen. P0 Startsender/Remote bleibt vorrangig.

## P1 – Einstellungsmenü anhand dritter Fotoserie (14.10.2026)

- 10 weitere Fotos indexiert: [`TIVIMATE_SETTINGS_SCREEN_REFERENCE_2026-10-14_DE.md`](TIVIMATE_SETTINGS_SCREEN_REFERENCE_2026-10-14_DE.md).
  Strukturierte Soll-Daten: [`TIVIMATE_SETTINGS_CONTRACT_2026-10-14.json`](TIVIMATE_SETTINGS_CONTRACT_2026-10-14.json).
- Menüfolge: Allgemein, Wiedergabelisten, EPG, Optik, Wiedergabe, Fernbedienung, Kindersicherung, Sonstiges, Über.
- Allgemein: fotografierte Schalterzustände einschließlich „letzter Sender ein“,
  aber keine bestehende Kodi-Konfiguration ungefragt überschreiben.
- Wiedergabelisten: aktivieren, Name, zugeordnete EPG-Quellen, Logo-Priorität,
  Archiv, Xtream-Parameter, Gruppen, Aktualisierung, nur bestätigt löschen.
- EPG: 7 Tage Vergangenheit, Beschreibungen ein, Intervall 24h, Update-Trigger
  aus, Quelle hinzufügen/zuweisen und Status anzeigen.
- Optik: EPG/Player/Gruppen/Logos; Sprache System, Schrift Mittel, 50 % UI-Transparenz;
  TiviMate zeigt Blau, **XCMate bleibt Slate-Grau**.
- Abhängigkeiten: Android-Boot/Wake und Home-PiP sind Kodi-Host-/Android-Themen;
  bisherige `epg_hours_back`-Einstellung ist nicht automatisch siebentägige
  Datenhaltung. Kodi braucht eigene Dialog-/Fokusnavigation.
- **Status: fotoverifiziert, Umsetzung offen**, keine neue veröffentlichte
  Add-on-Version. Vor Lösch-, Restore- und EPG-Refresh-Aktionen Bestätigung,
  atomische Datensicherung sowie strikte Portaltrennung.
- Auf einem Foto ist eine teilweise lesbare EPG-URL mit Zugangsdaten zu sehen:
  im öffentlichen GitHub niemals Domain, Benutzernamen, URL oder das
  Originalbild veröffentlichen. P0 Android-Fernbedienung bleibt Vorrang.

## P1 – Vierte Foto-Serie: Wiedergabe, Kinder-PIN, Suche, Aufnahme, VOD, Über (14.10.2026)

- Vollständiges Foto-Inventar:
  [`TIVIMATE_SETTINGS_FOURTH_SERIES_2026-10-14_DE.md`](TIVIMATE_SETTINGS_FOURTH_SERIES_2026-10-14_DE.md);
  maschinenlesbar in [`TIVIMATE_SETTINGS_CONTRACT_2026-10-14.json`](TIVIMATE_SETTINGS_CONTRACT_2026-10-14.json).
- Untermenüs erfasst: Wiedergabe, Sonstiges → Suche/Erinnerungen/Aufnahme/VOD,
  Kindersicherung und Über.
- Systemabhängige Player-Punkte (Puffer/Decoder/AFR/Passthrough) dürfen
  Kodi- oder Android-weite Einstellungen nicht unbemerkt ändern.
- Kindersicherung benötigt sichere PIN-Prüfung, getrennte Zugriffsregeln
  pro Untermenü, Throttling und nachvollziehbare Akzeptanztests.
- Aufnahmen: zeitlicher Vor-/Nachlauf, Kodi-kompatibler Speicherpfad,
  Rechte und Gerätesupport vor Release prüfen.
- VOD: nächste Folge automatisch spielen ist durch Foto als Einstellung
  bestätigt, der beobachtete Schalterwert bleibt **unklar**. Nicht mit bereits
  implementierter Serien-Fortsetzung verwechseln.
- Konto, Gerät und realer Aufnahmepfad wurden aus öffentlichen Artefakten entfernt.
  Telemetrie nur nach freiwilliger Aktivierung; fremde AGB/Abos nicht kopieren.
- **Unverändert offen**: P0 Startsender und Fernbedienungssteuerung auf Android,
  danach eigenständige UI-Implementierung und differenzierte Kodi-/Geräte-QA.

## 14.10.2026: P0 – veröffentlichter XCMate-0.1.11-Fernbedienungskandidat

Die Remote-Stabilisierung wurde als XCMate **0.1.11** über PR
[#4](https://github.com/artattakk-creator/kodi-noodleprivate/pull/4) veröffentlicht
(PR-CI 38565230410, Publish-CI 38565339149). ZIP 209252 Bytes ist auf
`main` vorhanden, `addons.xml` weist Version 0.1.11 aus und der unabhängig
überprüfte `addons.xml.md5`-Hash lautet
`f9aa9e4f7d8ae26a0f1af4a3ada46316`.
Kodi Repository 1.7.0, Add-on-ID und persönliche Benutzerdateien bleiben erhalten.

**Behoben laut Code/automatisierten Tests:** die bisher nur optional installierte
Fullscreen-Bridge wird bei XCMate-Live-TV automatisch und widerrufbar
aktiviert; Native-`WindowDialog.onAction` und Keymap/Service-Bridge bilden zwei
Eingabewege; Kodi-Player-OSD wird über die eigene XCMate-Buttonleiste umgangen;
Fernbedienungs-Diagnose erfasst native Ereignisse und Keymap-Status.
Die API-Tests behandeln Kodi-stub-basierte Navigation, nicht reale
Android-Geräteeingaben.

**P0 weiterhin offen:** zuverlässiger Startsender und echte Links/OK/Hoch/Runter/
Menü/Zurück-Erfassung unter Titan BINGIE MOD. **Erster Test nach 0.1.11
erfordert vollständigen Kodi-Neustart.** Am Zielgerät die Diagnosewerte und
anonymisierten `kodi.log`-Abschnitt auswerten. Full-EPG-Raster, lang gedrückte
Tasten auf diesem Remote-Modell und Hardware-Eingabequellen bleiben
geräteabhängige beziehungsweise folgende Arbeitsschritte.

**Kein Android-Funktionserfolg behaupten**, bis das Box-Protokoll vorliegt.

## 14.10.2026 – P0 Follow-up, Kandidat 0.1.12: Startsender-Sitzung wird zu früh gelöscht

**Gemeldetes Android-Verhalten:** DIE WELT HEVC startet und läuft normal;
die Lautstärkeregelung funktioniert, jedoch öffnet die Menu-Taste nur das
Kodi-Player-Menü. XCMate-Senderliste, OK-Leiste und Fernbedienungszuordnung
erscheinen nicht. Im Diagnosefoto nach Verlassen des Videos stand
"XCMate-Stream erkannt: NEIN" und "Video läuft: NEIN"; der Screenshot allein
belegt den Status *während* des Fernsehens nicht.

**Belegbarer Quellcodefehler:** `service.py` entfernt `XtreamMate.LiveSession`
nach >8 s anhand von `_stopped_since`, auch wenn der Timer vor dem
gerade neu angekündigten `RunPlugin`-Autoplay-Start abgelaufen war.
`announce()` läuft vor `xbmc.Player().play()`; Video-Startlatenz kann
somit dazu führen, dass der Service den neuen Marker löscht, bevor Kodi
überhaupt `isPlayingVideo()` meldet. Dann findet `start_if_eligible()`
keine Sitzung und startet kein `LiveNavigator`-Fenster.

**Fix (PR #5, noch kein Gerätetest):** Maximal 60 s Schonfrist für frisch
angekündigte, noch nicht durch die Overlay-Nonce bestätigte Sitzungen.
Normales 8-s-Cleanup für abgelaufene oder schon angezeigte Sitzungen
bleibt unverändert. Status `warte auf Videostart` signalisiert das
Übergangsstadium. Tests reproduzieren einen seit Minuten abgelaufenen
Idle-Timer plus neuen Marker sowie den normalen Stopp und abgelaufene
Ankündigungen. `addon.xml` wird auf 0.1.12 erhöht, Add-on-ID und
Konfigurationsdaten bleiben unangetastet.

**Nach CI/Veröffentlichung offen:** Vollständiger Kodi-Neustart auf der
Android-Box, DIE WELT HEVC starten, OK/Links/Hoch/Runter/Menü/Zurück/Guide
prüfen; wenn immer noch defekt, Kodi-Log auf
`XCMate navigator cannot start`, `XCMate WindowDialog startup failed`
und `XCMate TV navigation unavailable` anonymisiert auswerten.

### Verifizierte GitHub-Veröffentlichung 0.1.12

- Ursache, Regressionstests und Abgrenzung: PR [#5](https://github.com/artattakk-creator/kodi-noodleprivate/pull/5) (squash-merge `26c03e6c94027ad4cd9fba18bf15f579e2980c49`).
- PR-CI erfolgreich (letzter PR-Head): [38570173207](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/38570173207).
- Publish-CI erfolgreich: [38570255156](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/38570255156).
- Publizierter Commit: `0ea54335d52d7b62281c649b191ef021cdf77de8`.
- ZIP: `plugin.video.xtreammate/plugin.video.xtreammate-0.1.12.zip`, Größe 209791 Bytes; `addons.xml` meldet 0.1.12, MD5-Datei vorhanden (`9dd6666e3daf6f8edfcee95ba161fdab`).
- GS-Media-Repository 1.7.0, Add-on-ID und Benutzerdateien unverändert.
- **P0 Android-Gerätetest weiterhin offen:** Senderstart bestätigt in 0.1.11, Fernbedienungsübernahme nicht. In 0.1.12 prüft ein Hardwaretest, ob die neue Schonfrist das Problem tatsächlich löst.
