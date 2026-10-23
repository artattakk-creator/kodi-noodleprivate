# XCMate 0.1.29.26 – Reale Android-Nutzerabnahme (23.10.2026)

**Stand:** 23.10.2026, spätere direkte Benutzerübermittlung des interaktiven 21-Punkte-Formulars. **Version:** 0.1.29.26, Lightweight, Android-TV/Kodi 21.x (bestehende Testumgebung Android 13, Kodi 21.2 Omega, Titan BINGIE MOD). Angaben stammen unmittelbar vom Gerätetest des Nutzers und **nicht** von CI oder Unit-Tests.

**Ergebnis:** **15 PASS / 6 FAIL / 0 NOT_TESTED** von **21 abgegebenen Prüfpunkten**, Bestehensquote 71,4 %. Beim Nutzer ist die neue .26 bereits installiert und alle Checkbox-/FAIL-Felder wurden ausdrücklich übermittelt. **Ein Markierungsergebnis ist kein vollständiger Funktions- oder Provider-Nachweis jenseits des Testwortlauts.**

| ID | Prüfbereich | Nutzerergebnis |
|---|---|---|
| S01 | Suche nach Upload | **PASS** |
| S02 | Suche abbrechen und wiederholen | **PASS** |
| S03 | Drei Ergebnisrubriken | **PASS** |
| S04 | Filme/Serien aus Suchergebnissen | **PASS** |
| S05 | EPG-Jetzt-Suche | **PASS** |
| S06 | Live-TV aus Suchergebnissen | **FAIL** |
| S07 | Suche aus anderem Menü | **PASS** |
| R01 | Aufnahmeordner auswählen | **PASS** |
| R02 | Sofortaufnahme starten (UI/Anforderung) | **PASS** |
| R03 | Aufnahmestatus und Datenmenge | **FAIL** |
| R04 | Aufnahme manuell beenden | **FAIL** |
| R05 | Aufnahme wiedergeben | **FAIL** |
| R06 | Unterbrechung sicher behandeln (optional) | **FAIL** |
| B01 | Version und Bestandsdaten | **PASS** |
| B02 | Original-Icon und Menüs | **PASS** |
| B03 | Live-TV-Fernbedienung | **PASS** |
| B04 | Großes EPG und Jetzt/Danach | **PASS** |
| B05 | Senderstart aus großem EPG | **PASS** |
| B06 | Staffelübergreifendes Autoplay | **PASS** |
| B07 | Filmposter und Einzelretry (optional) | **PASS** |
| B08 | Kodi-Live-TV-Skinbutton (optional) | **FAIL** |

## Wörtlicher wichtiger Beobachtungsbefund

> „Also der lässt sich noch starten, die Aufnahme. Wenn ich dann aber sofort Aufnahmen gucken gehe über den Status, da steht dann Failed 0 MB Unsupported Target.“

**Zuordnung:** R02 PASS belegt den aufrufbaren Sofortaufnahme-Workflow und die Möglichkeit, den Auftrag auszulösen, **nicht** einen laufenden Recorder oder gesicherte Streamdaten. R03 FAIL mit angezeigtem Fehlercode **`FAILED / 0 MB / UNSUPPORTED_TARGET`**. R04/R05/R06 bleiben wie vom Nutzer ausdrücklich gemeldet **FAIL**, jedoch **ohne zusätzliche Einzelbeobachtungen** zu manuellem Stop, Playback, Unterbrechungsverhalten. Diese nachgelagerten FAILs dürfen **nicht** als drei bestätigte unabhängige Ursachen interpretiert werden: Ohne laufende Aufnahme und ohne Bytes kann ihre End-to-End-Funktion noch nicht nachgewiesen werden. Kein frei erfundener Aufnahmeordner-/Dateisystemtyp; ein aktuelles diagnostisches Kodi-Log wurde in dieser Nachricht nicht beigefügt.

### Codeanalyse Speicherziel aus `main` .26 (separat von Nutzerbeobachtung)

- `home_menu.py::recording_folder()` akzeptiert nach `xbmcgui.Dialog().browseSingle(0,...)` einen Pfad, wenn `probe_directory(...,xbmcvfs)` Schreiben/Lesen per Kodi-VFS erlaubt. Die Probe deckt **nicht** POSIX-Hardlink-/NoFollow-/`dir_fd`-Semantik ab.
- `capture_ui.py::_start()` übersetzt `recordings_folder` via `xbmcvfs.translatePath`, prüft absolut/nicht VFS-URL und schreibt den Auftrag über `capture_store.add()`.
- `capture_service.py::_run()` führt `resolve(job)` **vor** der endgültigen Zielprobe aus, startet dann den Recorder-Thread.
- `direct_ts.py::Recorder.run()`: `Path.is_absolute`, Symlinkprüfung, `os.open(O_DIRECTORY|O_NOFOLLOW)`, Speicherprüfung, danach `_probe_target()` mit `os.link(..., src_dir_fd=..., dst_dir_fd=..., follow_symlinks=False)`. Dort wird bei fehlgeschlagenem Hardlink **`Failure('UNSUPPORTED_TARGET')`** ausgegeben. Das ist ein klar plausibler Ursprung für **genau diesen Code**, aber der tatsächliche fehlgeschlagene Systemaufruf/Dateisystemtyp ist **ohne Geräte-Trace nicht bewiesen**. Die eigentliche HTTP-Verbindung des Recorders wird erst nach Zielprobe geöffnet; **0 MB** sind deshalb konsistent mit früher Zielablehnung.
- **Nächster Fix**: gleichwertige Zielprüfung **bei Auswahl/Start und vor zusätzlicher Providerverbindung**, gute nutzerseitige Gründe und verlässlich geeigneten lokalen Android-Standardpfad; nur freigegebene Dateisysteme. Issue [#126](https://github.com/artattakk-creator/kodi-noodleprivate/issues/126).

## Neue Funktions-/Regressionsbewertung

**S01–S05/S07 PASS:** Der zuvor in .25 reproduzierte Komplettabsturz bei Suche nach `Upload` ist in diesem .26-Test **nicht aufgetreten**; Eingabe und Suchoberfläche, Rubriken, EPG-Jetzt-Suche, Film-/Seriendetails und Back wurden vom Nutzer als PASS markiert. Dies ist eine reale **Teilabnahme** von [#118](https://github.com/artattakk-creator/kodi-noodleprivate/issues/118) und [#25](https://github.com/artattakk-creator/kodi-noodleprivate/issues/25). Keine Behauptung, die bisher nicht durch nativen Stack belegte Absturzursache sei lückenlos geklärt.

**S06 FAIL:** Suche liefert Live-TV-Treffer, aber der Start eines daraus gewählten Live-Senders funktioniert nicht laut Nutzer. **Spezifische Regression [#125](https://github.com/artattakk-creator/kodi-noodleprivate/issues/125)**. Direktes Live-TV **B03 PASS** und Senderstart aus großem EPG **B05 PASS**: Es ist nicht belegt, dass der generelle Player versagt. Zu prüfen: `media_search.py::SearchMixin._search_click()`/`handoff()`, `guide_playback.py` und `window_navigation.py`. Keine exakte Fehlermeldung oder aktuelles Log für S06 vorliegend.

**R01–R02 PASS / R03–R06 FAIL:** Sofortaufnahme noch nicht end-to-end funktional, Fehler `UNSUPPORTED_TARGET`, [#126](https://github.com/artattakk-creator/kodi-noodleprivate/issues/126). Weder vollständige native Recorderunterstützung noch Aufnahmeabschluss/Offline-Wiedergabe als PASS deklarieren. Der explizite Nutzer-FAIL für R06 bleibt bestehen, obwohl ein isolierter Unterbrechungsablauf ohne erfolgreiche Aufnahme noch nicht belegt wurde.

**B01–B06 PASS:** Version/Bestandsdaten/Original-Icon/Mediennavigationsoberfläche, Live-TV-Overlay/IR, großes EPG Jetzt/Danach und nun **Senderstart direkt aus großem EPG** wieder PASS. Damit überstimmt der jüngste **B05-PASS in .26** den vorherigen **E05-FAIL in .25**; [#121](https://github.com/artattakk-creator/kodi-noodleprivate/issues/121) als späteren Android-PASS kommentieren, aber nicht automatisch als dauerhaft behoben schließen, weil keine dedizierte Codekorrektur/RCA belegt ist.

**B06 PASS:** Die bereits .25 erfolgreiche **staffelübergreifende Serien-Autoplay-Funktion bleibt ausdrücklich PASS**. Code einfrieren/schützen, [#85](https://github.com/artattakk-creator/kodi-noodleprivate/issues/85).

**B07 PASS:** Nutzer bestätigt Film-Poster/Einzelretry **im Umfang dieses Formularfelds**. Dies ist kein Beweis, dass jeder zuvor bekannte Timeout (z.B. spezielle Aladdin-Quelle in [#111](https://github.com/artattakk-creator/kodi-noodleprivate/issues/111)) beseitigt ist; keine automatische Schließung von #111.

**B08 FAIL:** Kodi-Titan-BINGIE-MOD-Hauptmenü-Live-TV-Skinbutton bleibt defekt; [#120](https://github.com/artattakk-creator/kodi-noodleprivate/issues/120).

## Abnahme-/Release-Entscheid

**XCMate .26 nicht vollständig abgenommen** (15 PASS / 6 FAIL). Die neuen Such-Rubriken und der frühere Suchabsturz sind **weitgehend positiv abgenommen**, aber ein Live-Suchtreffer kann noch nicht wiedergegeben werden und die Sofortaufnahme ist blockiert. Fehlende Einzel-Fehlermeldungen und Gerätelogs nur **noch nicht geliefert**, nicht erfinden. Keine rückwirkende Umklassifizierung von FAIL in NOT_TESTED. Erst gezielte Korrektur und erneute Android-Tests von S06/R03–R06/B08 und Bestandsregression. Weitere noch nicht implementierte Anforderungen Plug-and-Play-Erststart #43, Lightweight Splash #122, Rich EPG Details #123 sind **nicht Teil dieser .26-Abnahme**. Kein unaufgeforderter weiterer Merge/Release.

## Technische und organisatorische Referenzen
- Testplan `docs/XCMate/ANDROID_TEST_02926_DE.md`
- PR [#119](https://github.com/artattakk-creator/kodi-noodleprivate/pull/119) – .26 Suche + Sofortaufnahme
- Neu: [#125](https://github.com/artattakk-creator/kodi-noodleprivate/issues/125) – Suchtreffer → Live-TV FAIL
- Neu: [#126](https://github.com/artattakk-creator/kodi-noodleprivate/issues/126) – Aufnahmeziel UNSUPPORTED_TARGET
- Offen: [#120](https://github.com/artattakk-creator/kodi-noodleprivate/issues/120) – Skin-Live-TV FAIL
- Erneuter PASS: [#121](https://github.com/artattakk-creator/kodi-noodleprivate/issues/121) – großer EPG → Senderstart
