# XCMate – realer Android-Gerätetest v0.1.29.7 (21.10.2026)

**Status:** Teiltest mit mehreren **negativen** Befunden; EPG-/Medien-Langzeitabnahme und unabhängiger Recorder nicht abgeschlossen. Auswertung aus unmittelbar vom Nutzer mündlich berichteten Beobachtungen; ein dazugehöriges **aktuelles Kodi-Log ist angekündigt, aber hier noch nicht ausgewertet**. Keine private Log-Datei oder Secrets ins öffentliche Repo übernehmen.

**Gerät:** Android 13 / RK3528 ARM32, Kodi 21.2 Omega, Titan BINGIE MOD. **Version:** XCMate `plugin.video.xtreammate` **0.1.29.7** erfolgreich über reguläres Kodi-Update installiert. **Live-TV:** gewöhnliches Senderauswählen funktioniert laut Nutzer; positive 0.1.29.6 Fenster-Smoke-Historie existiert, andere Features nicht automatisch bestanden.

## A. Mediennavigation – kritischer neuer P0-Befund

**Reale Reproduktion:** `XCMate-Hauptmenü -> Filme -> Medienlanding (Neuheiten, Favoriten, zuletzt gesehen) -> unterer Kategorien-Button -> Kategorien/Medienübersicht -> Zurück -> Landing` funktioniert. **Ein weiteres Zurück** lädt/öffnet wieder dieselbe Landing statt `XCMate Home (Live-TV / Filme / Serien / Einstellungen)`. Nach weiteren Back-Eingaben verlässt Kodi manchmal XCMate ganz. **Bei Serien** endet derselbe Ausstieg schließlich in **schwarzem Bild mit drei Punkten**, keinerlei Fernbedienungsreaktion, Kodi hängt; davor erschien einmal eine XCMate-Startfehler-/Protokollaufforderung ohne genauen Fehlercode. P0 [#73](https://github.com/artattakk-creator/kodi-noodleprivate/issues/73). Mit [#59](https://github.com/artattakk-creator/kodi-noodleprivate/issues/59) und [#40](https://github.com/artattakk-creator/kodi-noodleprivate/issues/40) cross-referenziert.

**Codehypothese, kein Ursachenbeweis:** `media_window.py::_handle_action` setzt am Landing `_return_home=True` und schließt; `open_media` ruft nach Fensterende `Container.Update(...action=xcmate_home...,replace)` auf; dazu `app_routes.py` bereits abgeschlossene Plugin-Directory. Prüfen auf Reentrancy/Focus/OwnerDispatch/native Kodi window life cycle, `stop_owned` und tatsächliche Kodi-Logfehler. Aktueller Log folgt erst.

**P0-Abnahme:** Home→Film/Serie→Kategorie→Details→Zurück stufenweise→XCMate Home; 10 Wiederholungen, keine Spinner, kein Kodi-Stall oder doppelte Aktivierung. Danach Back aus XCMate Home führt bewusst zu Kodi. Live-TV/Portale/EPG/Favoriten/Resume intakt.

## B. Film- und Serien-Landing – Benutzerwunsch P1

**Ist:** Drei Rails (Neu, Favoriten, Weitersehen), Medienposter und Text auf Fernseher zu klein; `XCMateMedia.xml` 720p verwendet 106×118-Itemlayouts mit Poster 100×92 und Label `font12` in 100×24. Kategorienbutton unterhalb der Rails; Suche separat rechts oben.

**Soll:** eigene obere Navigationszeile **Kategorien / (Film- oder Serienkategorien) / Suchen**, Kategorien nicht unten; darunter in Reihenfolge **(1) Weiter ansehen, (2) Meine Favoriten, (3) Neu hinzugefügt**. Deutlich größere Poster samt gut lesbarem Titel unter jeder Kachel; Bildschirmhöhe maximal sinnvoll nutzen, **vertikales Scrollen zulassen statt Lesbarkeit zu opfern**. Focus-/Back-/Scroll-Test für beide Medientypen. Neues [#74](https://github.com/artattakk-creator/kodi-noodleprivate/issues/74), Schnittstelle #24/#44; nach P0 #73.

## C. Artwork-Datenbankprüfung und Artwork-Kapazität

- Menü **Einstellungen → Speicher → Artwork-Jobdatenbank prüfen und reparieren** ist auf 0.1.29.7 verfügbar.
- Anzeige **`Code: OK`**; Nutzer berichtet keine klare Erklärung und eine technische `artwork-...sqlite`-Zeichenfolge bei `Backup:`. **Nicht** behaupten, Backup fehle: die lange Dateibezeichnung könnte der Sicherungsdateiname sein. Exakte UI-/Logbelege stehen noch aus.
- `Code OK` bedeutet nach aktuellem `artwork_db.py` eine erfolgreiche Integritäts-/Schemadiagnose der Artwork-Jobdatenbank, **nicht** vollständig vorhandene Bilder oder Platzreserve.
- Vor „Fehlende Bilder erneut laden“ gemeldete Statuswerte: **514/512 MiB**, **FAILED 11**, **READY 3767**, **SPACE_FULL 17667**. Nach Retry: **514/512 MiB**, **PENDING 17638**, **READY 3767**. Das sind getrennte Momentaufnahmen, nicht gemeinsam zu summieren.
- `art_store.budget()` nutzt Default 512 MiB, `used()` summiert Bildjobgrößen. `media_art.fetch()` verweigert neue Bilder bei `budget-used() <= 0` via `OSError(28)`, welcher `SPACE_FULL` erzeugt; `import_budget.check_space` löst denselben Status auch bei physisch knappem Dateisystem aus. **512-MiB-Cachelimit ist bereits überschritten. Disk physisch voll ist NICHT belegt.**
- `retry()` setzt alle nicht-READY-Jobs blind zu PENDING zurück; bei weiter vollem Cache keine Fortschrittsgarantie. Fehlende Filmposter sind daher plausibel.
- **Keine Datenbank-/Bilddateien löschen und keinen weiteren massenhaften Retry auslösen**. Erst tatsächlichen freien Gerätespeicher, verwendeten Cache-/Datenträgerplatz und Bilder je Favoriten/aktiven sichtbaren Elementen diagnostizieren, Budget und kontrollierte nutzerbestätigte Cache-Politik/optionale USB-Lokalisierung planen.
- [#69](https://github.com/artattakk-creator/kodi-noodleprivate/issues/69) gilt für Integrität/lesbare Diagnose, [#41](https://github.com/artattakk-creator/kodi-noodleprivate/issues/41) für Persistenz/Cachebudget/Bildvollständigkeit. Noch keine Behauptung neuer SQLite-Korruption.

## D. FFmpeg-Aufnahmeprobe

- Nutzer meldet „kein FFmpeg-Partner gefunden“. In `recording_probe.py` und `recordings.py` wird nur eine ausführbare `ffmpeg`-CLI über PATH (`/usr/bin/ffmpeg`, `/usr/local/bin/ffmpeg`) gesucht.
- Das offizielle Kodi-[Inputstream FFmpeg Direct](https://kodi.wiki/view/Add-on%3AInputstream_FFmpeg_Direct) unterstützt TS/HLS/DASH-Wiedergabe, Catch-up und Timeshift, liefert jedoch für XCMate **nicht automatisch** eine externe FFmpeg-CLI oder eine dauerhafte Timer-/Dateiaufnahme.
- Auf ARM32 eigenständig verifiziertes Aufnahmebackend nötig. Machbarkeitsoptionen: direkten geeigneten ungeschützten TS über eigene Hintergrund-Sitzung zuverlässig byteweise auf USB/HDD/SMB schreiben, oder ARMv7-kompatibler nativer Android-Helper für komplexe Streams; FFmpegKit-AARs sind häufig nicht ARM32-vorkompiliert. Keine pauschale Erfolgsmeldung / DRM-Umgehung.
- Aufnahme-Ziel bleibt **Sender A unabhängig speichern, während Sender B normal live gesehen/gewechselt wird**; **kein Multiview/PiP/Split**. [#62](https://github.com/artattakk-creator/kodi-noodleprivate/issues/62).

## Aktuelle Freigaberegel

**0.1.29.7 NICHT als vollständig Android-stabil freigeben**, obwohl reguläre Installation und Basis-Live-TV funktionieren. **0.1.30.1 / PR #50 nicht mergen**, bis P0 Back/Kodi-Hänger #73 geprüft und real behoben. 0.1.29.6-Backup/Rollback behalten. Fixes als separate Draft-PRs und Testpakete, Daten und Skin nicht zurücksetzen; kein Merge/Release ohne ausdrückliche Freigabe.

## Noch erwartete Beweismittel

- Aktuelles privates Kodi-Log **nach P0-Back-/Serienhang** möglichst `kodi.log` plus `kodi.old.log` nach Neustart, Zugangsdaten und Token vor öffentlichem Teilen maskieren.
- Optional Foto der Artwork-Prüfung einschließlich **Code/Backup-Dateiname**, sowie echter Android **freier Gerätespeicher**, nicht nur 514/512-MiB-App-Cache-Budget.

## Rückverweise

- [Zentrale Roadmap](ROADMAP_AKTUELL_2026-10-21_DE.md)
- [P0 Back/Kodi-Hänger #73](https://github.com/artattakk-creator/kodi-noodleprivate/issues/73)
- [UI-Größen und Reihenfolge #74](https://github.com/artattakk-creator/kodi-noodleprivate/issues/74)
- [Artwork-Budget/Cover #41](https://github.com/artattakk-creator/kodi-noodleprivate/issues/41)
- [Artwork-DB-Integrität #69](https://github.com/artattakk-creator/kodi-noodleprivate/issues/69)
- [Aufnahmeengine #62](https://github.com/artattakk-creator/kodi-noodleprivate/issues/62)
