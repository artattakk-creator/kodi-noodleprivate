# XCMate – GitHub/Codex/Superpowers-Automatisierung (17.11.2026)

## Was eingerichtet wird

Ein neuer, **bewusst freizugebender** GitHub-Workflow übernimmt zunächst die automatische **lesende Fehleranalyse**: GitHub-Issue mit Label codex-ready -> Codex liest Code und Testfälle -> Analyse wird als Kommentar zum Issue geschrieben. Alternativ kann eine berechtigte Person den Workflow manuell mit einer Issue-Nummer starten.

Dieser erste Schritt schreibt **keinen Code**, öffnet **keinen PR** und löst **keinen Merge, Release oder Publisher** aus. Er ist deshalb getrennt von den vielen bestehenden GS-Media-Publish-Workflows. Der Setup-PR enthält außerdem AGENTS.md mit den verbindlichen Projektregeln.

## Einmalig durch Repository-Administrator

1. Diesen **Draft-Setup-PR** prüfen und nach ausdrücklicher Freigabe in main übernehmen. Vorher ist der neue Workflow nicht aktiv.
2. Das Label codex-ready ist bereits auf Issue #474 gesetzt. Es darf nur für bewusst freigegebene Aufgaben eingesetzt werden; bereits gesetzte Labels lösen nach dem Merge keinen rückwirkenden Lauf aus.
3. Unter Settings -> Secrets and variables -> Actions -> New repository secret den Namen OPENAI_API_KEY eintragen. Den Wert ausschließlich in GitHubs Secret-Dialog eingeben, **nie** in Chat, Issue, Workflow-Datei oder Pull Request. Für API-Nutzung fallen separate OpenAI-API-Kosten an; die ChatGPT-Plus-/Codex-Berechtigung deckt dies nicht automatisch ab. Nutzungsbudget und Key-Berechtigungen begrenzen.
4. Unter Settings -> Actions -> General die Action-Freigaben kontrollieren. Die neue Analyse benötigt nur contents:read und issues:read. Ein zweiter Job bekommt issues:write ausschließlich zum Schreiben des Diagnosekommentars.
5. Branch-Schutzregeln für main und erforderliche CI-Checks prüfen bzw. setzen (Review-Pflicht, kein automatischer Merge). Diese Admin-Einstellungen werden durch den Setup-PR nicht verändert.
6. Nach Merge in Actions den Workflow XCMate Codex issue triage öffnen, Run workflow wählen und mit Issue 474 testen. Alternativ das Label codex-ready neu auf #474 setzen. Ein Label von **vor** dem Merge löst keinen rückwirkenden Workflow aus.
7. Prüfen, ob ein Codex-Analysekommentar im Issue erscheint. Bei fehlendem OPENAI_API_KEY wird nur ein Setup-Hinweis kommentiert, keine KI-Abfrage gestartet.

## Codex im Browser mit Superpowers

Unter https://chatgpt.com/codex das Repository wählen und Superpowers für die Codex-Umgebung aktivieren, falls diese Option dort vorhanden ist. Dass das Superpowers-Plugin in ChatGPT installiert ist, aktiviert es **nicht automatisch** im GitHub-Actions-Codex.

Mit genau einem Issue (z. B. #474) starten, die Analyse und AGENTS.md berücksichtigen, Reprotest anlegen, Fix implementieren und Draft-PR erzeugen. Host-/CI-Tests nicht als Android-Gerätetest ausgeben. Unveränderte Portal-EPG-Grundversorgung, optionale XMLTV/Bilder, Backup-Schutz und keine Releasefreigabe sind zwingend.

## Phase 2: Automatische Draft-PRs (noch nicht freigeschaltet)

Wenn der reine Analyse-Workflow zuverlässig funktioniert, kann ein gesonderter PR-Publisher vorbereitet werden: Ein nicht-privilegierter Codex-Job erzeugt einen streng auf XCMate-Quellen und Tests begrenzten Patch; ein separater Job prüft Dateipfade und erstellt einen **Draft-PR**, ohne KI-generierten Code mit schreibberechtigtem Token auszuführen. Kein Modell-Patch für .github/workflows, Release-Skripte oder Secrets. Auch dann gilt: Kein Merge ohne menschliche Freigabe.

## Erste Themen

- #474: Disney Channel – manuelle EPG-Zuordnung schließt Dialog ohne Bestätigung; Persistenz und UI-Neuladen testen.
- #427: manuelle EPG-Zuordnung / Akzeptanzkriterien.
- #464: EPG-Gate, Profil-Locks und Readback.
- Die 16.11.-Backups und Android-Protokolle liefern weitere Hinweise zu SETTINGS_XML_INVALID, EPG_READ_TIMEOUT und Bild-/Speicherfehlern. Zugriff auf private Drive-Daten ist nicht Bestandteil der GitHub Actions.

Repository: https://github.com/artattakk-creator/kodi-noodleprivate
