# XCMate 0.1.29.24 – Kritischer Android-Nachtest / Premium P0

**Datum:** 23.10.2026, später als der erste .24-Gesamttest. **Gerät:** Android 13 RK3528 ARM32, Kodi 21.2 Omega, Titan BINGIE MOD, IR-Fernbedienung. **Installiert:** XCMate 0.1.29.24, optionales Space Premium aktiviert.

## Warum dieser Nachtest wichtig ist

Der [zuvor übermittelte Android-Gesamttest](ANDROID_GESAMTTEST_02924_ERGEBNISSE_20261023_DE.md) bewertete A Update/Datenbestand, B Original-Icon, D Space Premium, E EPG und F Wiedergabe/Fernbedienung jeweils mit PASS, C Poster/Artwork mit FAIL. **Die nachfolgende direkte Benutzererfahrung widerspricht der pauschalen Freigabe von D/F für Medienfenster und Designwechsel.** Dies ist **kein nachgewiesener vollständiger Systemausfall** und keine Rücknahme des Icon-/EPG-PASS; die **späteren konkreten Teil-FAILs haben Vorrang für die betroffenen Funktionen**.

## Nutzerberichte (ohne technische Ursachenbehauptung)

| Teilfunktion | Neuer Status | Beobachtung des Nutzers |
|---|---|---|
| Space Premium → Standard Lightweight | **FAIL/P0** | Rückwechsel versucht; funktioniert nicht |
| Filme und Serien: Fokus-/Cover-Navigation | **FAIL/P0** | Tastentöne zu hören, aber kein sichtbar ausgewähltes Cover/Element |
| Datei-/Ordnerfenster | **FAIL/P0** | Tastentöne zu hören, Fokus/Positionswechsel nicht sichtbar |
| Medien-Detailansicht → OK | **FAIL/P0** | Statt gewünschter Aktion öffnet sich wiederholt die Suche |
| Poster aktualisieren | **FAIL/P1** | Weiter Netzwerkfehler; direkte Aktualisierung nicht möglich beziehungsweise durch Detailaktionsproblem nicht zuverlässig bedienbar |

**Nicht belegt:** aktueller Netzwerk-HTTP-Status, konkrete Betroffenheit einer Kodi-Systemdateiauswahl vs. XCMate-Ordnerliste, `appearance_v1`/Theme-Selection-Inhalt, tatsächlicher Kodi-Playerstatus beim Umschaltversuch, ein echter Crash oder beschädigte Kodi-Systemdaten. **Keine Root Cause ohne Diagnose behaupten.**

## Ermittlung im aktuellen main

- `resources/lib/theme_store.py::select`: Theme-Wechsel `pending`, solange `xbmc.Player().isPlaying()`; mögliche, aber nicht verifizierte Ursache des Rückwechsel-FAIL.
- `resources/lib/theme_ui.py::manage`: Standard-`select('')`, Dialog und Rückmeldungen; Manager und Offline-Rückweg nachvollziehbar instrumentieren.
- `resources/lib/theme_render.py::apply_xml` und `resources/lib/appearance.py::window_source`: Ersatz der Media-Fokustexturen, zusätzliche Bild-Controls, Layout-/Alpha-/Renderreihenfolge; Kodi 21/BINGIE Fokus-Kontrast gerätebezogen prüfen.
- `resources/lib/media_window.py`: `400` ist Such-Button; `onClick(400)` öffnet Suche. `_show('detail')`, `_detail_ready()`, `setFocusId()`, `_valid_focus()` und asynchrone Updates auf unabsichtliches Beibehalten von Fokus 400 statt erste Aktion 300 prüfen.
- `resources/lib/media_art.py`, `art_store.py`, `art_errors.py`: Artwork-C-FAIL mit tatsächlicher Einzelposterdatenlage analysieren; UI-Fokus-FAIL getrennt von HTTP-FAIL.

## Verbindlicher Codex-Auftrag

**P0-Issue:** [#115 – Premium-Fokus, Lightweight-Recovery, OK/Suche](https://github.com/artattakk-creator/kodi-noodleprivate/issues/115). Dort vollständige Reproduktionsbedingungen, Code-Hypothesen, gewünschte Architektur und Abnahmekriterien.

- Bei aktiver Wiedergabe einen **persistenten, später tatsächlich wirksamen** Rückwechsel zu Lightweight ermöglichen, ohne Playback zu stoppen, keine XCMate-Profile, EPG, Resume und Cover zu löschen. Nach Neustart muss Standard verlässlich aktiv sein.
- In **Filme/Serien, Gruppenlisten, Kachelgittern, Detailaktionen, Staffeln/Episoden und Dateifenstern** muss bei Tastendrücken ein eindeutig sichtbarer Fokus erscheinen. Notfalls nicht kompatible Premium-Fokusgrafiken vorerst komplett auf bewährte Core-Fokustexturen zurücksetzen; Premium-Design darf nie die Bedienbarkeit verlieren.
- Fokus 300 (erste echte Detailaktion) vs. Suchbutton 400 sauber behandeln; `OK` startet die fokussierte Aktion, Suche nur bei explizitem Suchfokus. Tab-/Media-/EPG-/IR-Regressionstests.
- Posterfehler isoliert korrigieren/diagnostizieren; kein globaler Art-Queue-/Cache-Reset, kein Löschen der Userdaten.
- Nach Hotfix Tests/CI/ZIP/SHA256; vom Nutzer **Freigabe zum Merge nach bestandenen technischen Gates** erteilt. **Die Android-Geräteabnahme für tatsächlich sichtbare Navigation bleibt gesondert erforderlich.** Kein ungeprüfter Merge oder Behauptung, das Gerät wäre bereits repariert.

## Entwicklung / Release

Aktueller veröffentlichter Core **0.1.29.24**. Als nächstes freies isoliertes Hotfix nach Versionsabgleich beispielsweise **0.1.29.25**; separater PR auf aktuellem main. Aus PR #50 nichts pauschal übernehmen. GS-Media-Repository-Update erst nach erfolgreichem Merge/Build; kein Versand an Kodi allein durch Anlage dieses Dokuments.
