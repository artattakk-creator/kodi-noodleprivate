# Entwicklungsablauf und Aktivierung

## Was diese PR tatsächlich tut

`AGENTS.md` macht die Projektregeln dauerhaft sichtbar. Der Auftragseingang bereitet nur freigegebene Aufgabenreferenzen vor; die PR-CI prüft reale Validator-/Injection-Regressionen und geschützte Pfade. Ein Label startet **keinen** kostenpflichtigen Codex-/OpenAI-API-Lauf. Diese erste Entwicklungsrunde wird in der bestehenden Codex-Sitzung bis zum Draft-PR ausgeführt und unabhängig überprüft.

Status vor Nutzer-Merge: **PREPARED_NOT_ACTIVE**. Neue Issue-Workflows müssen auf dem Defaultbranch liegen, bevor `issues:labeled` sie auslösen kann. Kein Merge wird dafür von Codex vorgenommen. PR-CI läuft auf dem Entwicklungsbranch; ihre tatsächlichen Ergebnisse werden verlinkt.

## Konkreter späterer Auftragseingang

1. Kleines Issue mit Reproduktion, tatsächlicher Version, Links und Abnahmekriterien erstellen. Keine Rohlogs/Geheimnisse.
2. Eigentümer `artattakk-creator` prüft den aktuellen Inhalt und setzt `codex:approved`. Nur dieser menschliche Auslöser wird akzeptiert; Bots und fremde Konten werden blockiert.
3. Workflow lädt das Issue erneut und vergleicht ID, URL, Freigabe, Zustand und Änderungsstand. Nachträgliche Änderung oder entzogenes Label blockiert die Vorbereitung. Bei Bedarf Label entfernen/neu setzen.
4. CI-Artefakt `task.json` enthält Repository, Issue-Link, Body-SHA, Baseline-SHA und Vorschlagsbranch `agent/issue-N`; kein Body, Titel oder Log. Zustände TASK_PREPARED/NOT_STARTED, API-Budget0, Android NOT_TESTED.
5. Codex liest das tatsächliche Issue und Dokumente, prüft Source-/Release-Abweichungen, legt Plan/RED-Test an, implementiert minimal, testet und lässt unabhängig prüfen. Bericht mit exaktem SHA und Draft-PR, niemals automatischer Merge/Release.

Ein manueller Dispatch erfordert denselben Eigentümer, ein offenes Issue und das noch aktuelle Freigabelabel. Die erste Sitzung darf Issue474 anhand des direkten Nutzerauftrags bearbeiten, ohne jetzt Labels oder Workflows live zu aktivieren.

## Was für einen vollautomatischen externen Entwickler noch fehlt

Ein GitHub-Actions-Job ist allein kein Codex-Agent. Eine externe CLI/API-Integration benötigt separat installierte/versionierte Superpowers-Skills, ausdrücklich freigegebenes API-Budget und Schlüsselverwaltung, isolierte Ausführung, Zeit-/Parallelitätsgrenzen sowie einen getrennten Publisher mit enger Branch-/Pfadfreigabe. Kein OpenAI-Schlüssel ist hier eingerichtet oder verwendet. Auch automatische fachliche LLM-Reviews sind ohne solche Integration nicht durch die statische CI-Policyprüfung ersetzt.

Vor Aktivierung sind effektiver main-Branchschutz/Required Reviews und Release-Environments nachzuweisen. #470/#472 dokumentieren 52 bestehende Workflows und alte schreibende Publisher. Der Audit vom16.11. ist ein historischer Befund, kein erneuter Nachweis wirksamer Schutzregeln. Diese PR verändert jene Publisher und PR472 nicht. Insbesondere kann bestehendes publish.yml bei main-Pushes publizieren: keinen Infrastruktur-Merge als unbedenklichen Rollout behandeln. Separate Härtung/Owner-Einstellungen bleiben Voraussetzung für einen unbeaufsichtigten schreibenden API-Runner.

## Abnahme dieser Struktur

`python -m unittest discover -s tests -p test_agent_workflow.py -v` prüft die echte Funktion/CLI gegen erlaubte, manipulierte und widerrufene Aufträge. `python tools/agent_workflow.py scope --base <40hex> --head <40hex>` meldet SCOPE_OK, REVIEW_REQUIRED oder BLOCKED; diese Zusatzprüfung ist kein Ersatz für serverseitige Regeln. Fachlicher Review wird gesondert durch einen nur lesenden Subagenten ausgeführt und dokumentiert.

## Offizielle Referenzen

- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows (Defaultbranch-Bedingung der Issue-Trigger)
- https://docs.github.com/en/actions/tutorials/authenticate-with-github_token (minimale Tokenrechte)
- https://github.blog/changelog/2022-09-08-github-actions-use-github_token-with-workflow_dispatch-and-repository_dispatch/ (GITHUB_TOKEN-Ereignisse lösen überwiegend keine Folge-Workflows aus; daher kein erfundener Bot-Autostart)
- Superpowers-Methoden in dieser Codex-Umgebung gelesen; externe Installation ist separat nötig. Bezug: #470/#472, aktueller konkreter Produktauftrag #474.
