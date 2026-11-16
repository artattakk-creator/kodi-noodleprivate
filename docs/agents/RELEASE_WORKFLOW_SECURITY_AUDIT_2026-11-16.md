# XCMate Agentenplattform – Sicherheitsinventar für GitHub-Veröffentlichungen

**Stand 16.11.2026 · Inventar der Dateien auf `main` (nicht der .96-Codex-Worktree) · Status: EINSATZBEREIT FÜR REVIEW, NICHT FÜR AUTO-RELEASE**

## Befund: 52 vorhandene GitHub-Actions-Workflows
Die 52 YAML-Dateien unter `.github/workflows/` wurden hinsichtlich Triggern, `permissions`, Veröffentlichungskommando und PR-/Push-Bedingungen durchgesehen.

| Klasse | Anzahl | Beispiele | Risiko |
|---|---:|---|---|
| Schreibfähige Publish-/Release-Workflows | 29 | `publish.yml`, `gsmedia-050-beta-publish.yml`, `gsmedia-online-setup.yml`, `xcmate80-publish-all.yml`, `xcmate87-publish-all.yml` | `contents: write`, `git push origin HEAD:main` in den für bestimmte Ereignisse aktivierten Schritten |
| GitHub Pages Deployment | 1 | `gsmedia-pages-pilot.yml` | `pages: write`, `id-token: write`, `deploy-pages@v4`, Branch `main` und `workflow_dispatch` |
| Primär lesende Review-/Diagnose-Workflows | 22 | `xcmate82-review.yml`, `xcmate89-review.yml`, `neodark3-latest-only.yml` | keine direkte Git-Push-/Release-Aktion erkannt; Host-Tests allein liefern keine Android-Freigabe |

**Unmittelbar relevant:** `.github/workflows/publish.yml` führt auf `push` nach `main` für seine gefilterten Pfade Hosttests und unter `github.event_name == 'push' && github.ref == 'refs/heads/main' && steps.channel75.outputs.regular == 'true'` eine eigenständige Release-Commit-Stufe mit `git push origin HEAD:main` aus. Der generelle Tokenumfang dieses Workflows ist `contents: write`. Er ist **nicht** der sichere Ort, einen untrusted API-Agenten zu betreiben.

Eine Reihe der historischen Release-Dateien bietet `workflow_dispatch` und veröffentlicht auch bei manuellem Aufruf; teilweise schützen exakt gepinnte Versionen/Approval-Manifeste das individuelle Paket, **aber das ist keine zentrale, versionsübergreifende Freigabe-Infrastruktur**. Diese historischen Release-Workflows bleiben in der vorliegenden Vorbereitung bytegleich.

## Tatsächlicher GitHub-Schutzstatus – API-Nachweise
- `GET /repos/artattakk-creator/kodi-noodleprivate/rulesets` → **`[]`** (keine über diese Repo-Abfrage sichtbaren eigenen Rulesets).
- `GET /repos/artattakk-creator/kodi-noodleprivate/branches/main/protection` → **403 `Resource not accessible by integration`**. Die klassische Branch-Protection ist **UNBEKANNT**, nicht automatisch `OFF`.
- GitHub-Verbindungsaktionen für `create/update ruleset`, `set branch protection` und Environments sind aktuell **nicht verfügbar**. Ebenso liefert die erlaubte `fetch`-Route kein verifiziertes Environment-Inventar. Keine Schutzfunktion wird deshalb als aktiv behauptet.
- `allow_auto_merge` ist im Repo-Metadatensatz `false`; dies verhindert **keine** anderen Schreibzugriffe oder Workflow-Pushes.

## Sofort technisch durch diese PR vorbereitet
1. `AGENTS.md`: Entwickler dürfen nur isolierte Agenten-/Feature-Branches und Draft-PR verwenden; `main`, `online-test`/Pilot, regular/NeoDark3 nur nach expliziter Eigentümerfreigabe.
2. `tools/agent_framework/preflight.py`: fail-closed Review-Metadatenprüfer, **keine** Workflow- oder Deployment-Freigabe; falsche Android-PASS, Merge-/Release-Flags und fehlerhafte Hashes → BLOCKED.
3. `.github/workflows/xcmate-agent-preflight.yml`: nur `pull_request` für Agenten-Dateien oder `workflow_dispatch`, `permissions: contents: read`, keine GitHub Secrets, kein `git push`, keine Publikationsjobs und kein kostenpflichtiger Modellaufruf.
4. `docs/agents/runner-config.disabled.json`: `enabled=false`, max. API-Kosten **0**, keine Codex-/Work-/Drive-/Hardware-Aktivierung.

## Erforderliche GitHub-Einstellungen vor API-Agenten-/Release-Aktivierung (Owner in der GitHub UI)
1. Repository `Settings → Rules → Rulesets`: neues aktives **Branch ruleset** für `main`; mindestens `Require a pull request before merging` + **1 unabhängige Review-Freigabe**, `Block force pushes`, `Restrict deletions`, keine Agenten-/Bot-Bypasses; für andere Publikationszweige entsprechend. Statuschecks erst dann als Required Checks auswählen, wenn sie unter genauem Namen einmal real gelaufen sind.
2. `Settings → Environments`: gesondertes Release-Environment, z. B. `xcmate-release`, mit Required Reviewers und auf autorisierte veröffentlichte Branches begrenztem Deployment. **Wichtig:** Das Environment schützt alte Publish-Jobs **erst nach tatsächlicher Anpassung der alten Workflows**. Es ist kein rückwirkender Schutz vor bestehenden `git push`-Schritten.
3. `Settings → Actions → General`: `GITHUB_TOKEN` standardmäßig schreibgeschützt; Pull Requests von Forks ohne Workflow-Secrets; ggf. Genehmigungen für externe Contributors. Alte Workflows mit `contents: write` benötigen eine kontrollierte Umstellung/gezieltes Berechtigungskonzept, bevor Agenten solche Actions auslösen können.
4. **Danach** separates Release-Hardening-PR: alle 29 historischen schreibfähigen Workflows prüfen/entschärfen, Versions-/Approval-Manifest, Kanal-Scope, `workflow_dispatch`-Freigaben, sichere Retention, Post-Push-Guard. Eine bloße Branch-Regel **allein** kann keinen ausdrücklich erlaubten API/Bot-Bypass garantieren; echte Testausführung und Nichtveröffentlichungsnachweis erforderlich.
5. Kein Agenten-Label, API-Runner oder Work-Trigger wird vorher automatisch den Release-/Main-Zustand verändern.

## Bedrohungstest / Negativszenarien
- PR aus untrusted Branch ergänzt `approval.release=true` → Preflight `BLOCKED`.
- Offenes Issue mit eingefügtem Shell-/Codex-Befehl → nicht als Berechtigung zur Code-/Secret-/Deployment-Aktion akzeptieren.
- Falsches Android-PASS bei nur synthetischem Kodi-Test → `BLOCKED`; echte Geräteevidenz separat.
- Push nach Main kann unvermutet altes Workflow-Release triggern → deshalb **kein Merge**, bis pro Ereignis und Pfad sichere Grenzen bestätigt sind.
- GitHub-Actions `workflow_dispatch` eines historischen Veröffentlichers ist **keine** geeignete Testaktion für unsere neue Agentenstrecke.

## Freigabestatus
- **Vorbereitungsbranch + Draft-PR:** zulässig, ohne Main-Änderung; PR-CI nur nach tatsächlicher Jobprüfung als PASS ausweisen.
- **Merge dieses PR auf Main:** **BLOCKED bis Branch-Protection/Sicherheitsmaßnahmen geprüft und Nutzerfreigabe gegeben.**
- **Automatischer Codex API-Start, Work-Webhooks, Drive-Logzugriff oder Android-/Release-Automation:** **OFF / nicht Gegenstand dieser Phase.**
