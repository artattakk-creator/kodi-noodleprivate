# XCMate 0.1.29.35 – Testbox B: Wizard-Endphase, Gruppen-Nachimport und Speicherwarnung

**Ergänzender realer Nutzerbericht vom 25.10.2026**, weitere Kodi-Logs angekündigt, **in diesem Arbeitsschritt noch nicht vorliegend/ausgewertet**.

**Gerät B:** neue Android-TV-Box mit neuerer Kodi-/Android-Umgebung, Versionen/Hardware-ABI noch nicht belegbar. **Installiert und tatsächlich getestet ist die reguläre XCMate 0.1.29.35**, **NICHT** die isolierte Wizard-Preview PR #162. Hauptbox A / bestehende Profile unverändert.

## Nutzerbeobachtung – ausschließlich gesicherte Aussagen

1. Die zuvor ausgewählten **4 EPG-Quellen** werden sequenziell verarbeitet; Anzeige zunächst 1/4, später 2/4, Scan schließlich abgeschlossen. **Ein Fortschrittsbalken erscheint erst ganz gegen Ende und geht praktisch sofort bis 100 %**. Benutzer hält die Oberfläche während längerer Quellen-Durchläufe verständlicherweise für eingefroren. EPG-Progressthema #164.
2. Nach Scan erscheint eine Bestätigung; Benutzer wählt **Speichern**. Während einer Meldung sinngemäß „Arbeitsdatei wird abgelegt“ (**kein exakter Meldungstext belegt**) beendet sich **Kodi komplett / stürzt ab**. Android-Kill, Python-Crash, OOM, Kodi-UI-Race oder ENOSPC **noch NICHT ursächlich belegt**, da neue Logdateien noch ausstehen.
3. Nach erneuter Kodi-Öffnung wird **Wizard NICHT wieder automatisch aufgerufen**. Account/Verbindung ist gespeichert; Startsender lässt sich einstellen und Fernsehwiedergabe klappt; EPG scheint ebenfalls funktionsfähig. Diese positiven Funktionsbefunde **beweisen noch keine vollständige transaktionssichere Persistenz sämtlicher Gruppen/EPG-/Medienindizes**. P0 Save-Crash #165.
4. Eine ursprünglich im Wizard vergessene **Sendergruppe lässt sich nachträglich auswählen und speichern**; die Gruppe zeigt danach **„keine aktiven Sender gefunden“** bzw. inhaltlich 0 Sender. Vorher importierte Live-Kanäle funktionieren. P1 Gruppen-/Catalog-Nachimport #166.
5. Zusätzlich erscheint auf der neuen Box **sinngemäß „Speicher voll“**, obwohl Nutzer echten Speicherplatzmangel nicht erwartet. **Exact UI wording, Dateisystem/Mount und technische Fehlerquelle erst mit Logs prüfen**. #90/#91 und #165.

## Statische Codeprüfung gegen tatsächliches main .35

### EPG-Progress als belegte UI-Lücke
- `setup_draft.py::_scan_epg()`: pro Quelle nur `status(None, "EPG-Quelle X/Y")`; erst am `scan()`-Ende `status(100,...)`.
- `setup_window.py::WorkWindow._paint_status()`: `getControl(4).setVisible(percent is not None)`. Bei `None` wird bestehender Progress-Control verborgen; erst mit `100` sichtbar. **Exakt passend zur Nutzerbeobachtung.** Indeterminierter animierter, stets sichtbarer Busy-Balken und echte Quellen-/Events-/Byteszähler, keine erfundenen 25-/50-%-Totalwerte.

### Fehlender Xtream-Nachimport als belegte asymmetrische Code-Stelle
- `group_selection.py::choose_groups.commit()` speichert die aktivierten IDs für alle Portaltypen. Danach wird `catalog_sync.request(portal, kind, priority=1)` **nur für `('m3u','stb')`** ausgeführt, nicht für `xtream`. Bei Xtream fehlt also der explizite Sync-Trigger für nachträglich aktivierte Gruppen. Die UI `main._groups_manager` aktualisiert nur die Liste, ohne Sync.
- `catalog_sync.run_next()` und `library_index.sync_kind()` können bereits selektiv aktivierte Kategorien importieren, persistieren `heads/sync_status`. **Codex sollte bestehenden Service-Importer nutzen**, keine globale Neueinrichtung auslösen. Ggf. `include_live/include_vod/include_series`-Flags aktualisieren, auch wenn beim Wizard ursprünglich 0 Gruppen dieser Gattung gewählt wurden. Tatsächlichen Portaltyp auf Testbox noch über Logs/eigenen ungefährlichen Status prüfen.
- **Wichtige Differenz:** Speichern einer Checkbox ist nicht Nachweis „Kanäle importiert“; Status PENDING/INDEXING/READY/FAILED sichtbar machen.

### „Speicher voll“ muss technisch geklärt werden
- `import_budget.py` prüft tatsächliches freies lokales Dateisystem mit 32 MiB Reserve + erwarteter Batchmenge und wirft ggf. `OSError(28)`.
- `art_storage.py` unterscheidet `BUDGET_FULL` (interner Grenzwert) von `DISK_FULL` (physischer Platz, Artwork-Reserve); aktueller Artwork-Reserve-Standard 1024 MiB. `art_store.py` kann Artwork-Jobs pausieren, obwohl EPG-/Live-TV funktioniert. Daher **keine** ungesicherte Diagnose „physische Platte voll“ und **keine** blind aufgehobenen Schutzreserven.
- Zusätzlich Android-Scoped-Storage/Schreibrechte, temporäre Staging-Kopie und SQLite-Journal/WAL/Speicherort prüfen. **Kein Cache-Clear, kein Profil-Reset, keine DB-/Artwork-Datenlöschung als vorgeschlagener Fix**.

### Save-Crash: zeitliche Eingrenzung, noch keine Ursache
- `setup_draft.py::_save()`: Import-Kopien in persistenten Katalog/Guide, Konfiguration, `portals.add()`, nachgelagerte Verifikation; `setup_window.py::saved()` schließt Dialog, `main.py::_setup_wizard()` ruft Container.Update auf. Unterscheiden: vor/nach Publish, Worker-Exception vs Kodi-Prozessabsturz, Directory-/Window-Übergang vs OOM/ENOSPC. **Kein Schluss aus „Portal vorhanden“ auf vollständig ausgeführten letzten Schritt**.

## Verbindliche neue .37-Wizard-Abnahmematrix (NICHT als bestanden buchen)

| Gate | Pflichtkriterium | Status |
| --- | --- | --- |
| WIZ-FIX-01 | EPG 1/4→4/4 zeigt durchgehend sichtbaren Aktivitätsindikator ab erster Quelle, wahrheitsgemäße Counts, READY/FAILED, kein 100-%-Sprung erst ganz am Ende | NOT_TESTED |
| WIZ-FIX-02 | Speichern nach vollem EPG-/Medienimport ohne Kodi-Absturz, erfolgreiche GUI-Navigation/Directory-Abschluss | NOT_TESTED |
| WIZ-FIX-03 | Nach Neustart exakt ein Portal, persistente Gruppen/Startsender/EPG/VOD, kein Auto-Wizard-Reentry, keine Korruption | NOT_TESTED |
| WIZ-FIX-04 | Nachträglich aktivierte Xtream-Live-Gruppe landet automatisch mit Sendern im lokalen Index ohne Vollscan/Reset | NOT_TESTED |
| WIZ-FIX-05 | Nachträglich hinzugefügte Film-/Seriengruppen werden ebenso indexiert; während Sync PENDING/INDEXING statt „0 aktiv“ | NOT_TESTED |
| WIZ-FIX-06 | „Speicher voll“ mit echtem Code, realer freier Kapazität, Speicherort und gewählter Budget-/Reservequelle erklärt; Daten bleiben erhalten | NOT_TESTED |
| WIZ-FIX-07 | Bei echtem ENOSPC/Importfehler/restart während Save wird kein halbes Portal als fertig bestätigt; sichere Recovery | NOT_TESTED |
| WIZ-FIX-08 | Original-XCMate-Icon + entsprechende Wizard-Hintergrundgrafik sichtbar; Fokus/IR/Abbruch unbeschädigt | NOT_TESTED |
| WIZ-FIX-09 | Bestehende .35-Hauptbox/Autoplay/TV/Guide/Film/Serie/Favoriten/Portal/EPG bleiben kumulativ unverändert | NOT_TESTED |

**Zuordnung:** #43 (Wizard komplett), #164 (Fortschritt), #165 (P0 Crash/Save), #166 (P1 Nachimport), #90/#91 (Budget/SQLite). [Verbindliche Release-Roadmap](VERBINDLICHE_RELEASE_ROADMAP_AB_02935_20261025_DE.md): .36 Suche/Genre/OSD-Latenzen, **.37 Wizard plus alle .36 Restbefunde**. Live-EPG/Rail .38 bleibt geplant. **PR #163 .36 läuft bereits separat**, **#162 ist nur nicht getesteter Preview-Draft**. Keinerlei eigenmächtige Merges/Publikationen/Desinstallationen. Nach Eintreffen der versprochenen Logs diese datensparsam anhand echter Zeitmarken, Ausnahmen, Prozessstatus und Speicherdiagnose ergänzen. Keine Geheimnisse/Provider-URLs in GitHub.
