# XCMate Modell B — vorbereitete, nicht aktive Agentenplattform

**Stand 16.11.2026 · GitHub Issue [#470](https://github.com/artattakk-creator/kodi-noodleprivate/issues/470)**

Diese Dateien liegen ausschließlich auf `chore/xcmate-model-b-agent-prep-20261116` (Basis **main**). Die laufende Codex-Entwicklung **XCMate .96** bleibt auf ihrer eigenen Arbeitsgrundlage unverändert; dieses Branch enthält keine XCMate-Addon-, Skin-, Installer- oder Paket-Änderung.

## Verbindliche Startpunkte
- Architektur: `docs/superpowers/specs/2026-11-16-xcmate-model-b-agent-automation-design.md`
- Plan: `docs/superpowers/plans/2026-11-16-xcmate-model-b-safe-preparation.md`
- Agentenregeln: `AGENTS.md`
- PR-Vorlage: `.github/PULL_REQUEST_TEMPLATE/agent_change.md`
- Lokaler Preflight: `tools/agent_framework/preflight.py`
- Tests: `tests/test_agent_framework_preflight.py`
- Beispiel, ausdrücklich **kein Release**: `docs/agents/examples/review-only.json`
- GitHub-Action: `.github/workflows/xcmate-agent-preflight.yml`, `contents: read`, nur PR auf diese Dateien und manuelle Auslösung, **kein Publish**.
- Deaktivierte API-Konfigurationsvorlage: `docs/agents/runner-config.disabled.json` (beide Kostenlimits 0, OpenAI-/Work-/Drive-/Android-Ausführung AUS).

## Nutzungsweg — wenn eine konkrete Entwicklungsaufgabe angenommen wird
1. Nutzer gibt Issue und Entwicklungsumfang frei. Work kann Priorität/Anforderungen/Abnahme zusammenfassen, führt aber keine impliziten Freigaben aus.
2. Codex-CLI/App nimmt Issue auf separatem Feature-Branch/Worktree. Bei Superpowers-Installation im **externen** Agenten gelten Skills für Plan, TDD, Review und Verification. Der ChatGPT-Superpowers-Connector allein stellt diese Skills nicht für die CLI bereit.
3. Nach wirklich ausgeführten Tests entsteht Draft-PR mit dem PR-Template. Repo/Branch/Commit und Hash des *exakt gebauten* Pakets werden angegeben.
4. Python-Preflight prüft einen lokalen JSON-Reviewbericht **ohne Internet, Schlüssel, Runner-Secrets oder GitHub-Schreibrechte**:
   ```bash
   python -m unittest discover -s tests -p 'test_agent_framework_preflight.py' -v
   python tools/agent_framework/preflight.py --manifest docs/agents/examples/review-only.json
   ```
   Ergebnis `REVIEW_ONLY` bedeutet ausschließlich „formale Reviewdaten vollständig“, **niemals Freigabe für Merge/Release oder Android-PASS**.
5. Zusätzliche Tests auf echter Box werden dem **exakten** neuen Code/ZIP-Hash zugeordnet. Android bleibt `NOT_RUN` bis reale Prüfung; per Chat/AI erstellte Aussagen sind kein PASS-Nachweis.
6. Ein separater, expliziter Nutzerauftrag und ein nachweislich geschützter Release-Pfad sind für jede Veröffentlichung nötig.

## Work / GitHub / Google Drive
- GitHub ist der revisionssichere Zustandsanker (Issue #469 Produkt / #470 Agenten, PR, SHA, CI, Testartefakte, Freigabestatus).
- ChatGPT Work kann nach manueller Einrichtung PR/Issue-Reports erstellen, soweit entsprechende Events im Benutzerkonto verfügbar sind. Diese Vorbereitung legt **keinen Work-Auslöser** an.
- Google Drive bleibt Ablage für originale Kodi-Logs und Backups. Ein eventueller Log-Worker braucht separat begrenzte Leserechte und mustert Geheimnisse, private URLs/IPs, Zugangsdaten aus. Der Preflight greift **nicht auf Drive zu**.
- Eigene OpenAI-API ist verfügbar, aber **nicht verbunden oder konfiguriert**. Kein geplanter Kostenpunkt wird durch diese Dokumentation ausgelöst.

## Inbetriebnahme / nahtlose spätere Übernahme
1. Laufende .96-Arbeit bis zu nachprüfbarem Branch/Draft-PR/Commit/Testbericht weiterlaufen lassen; **kein Eingriff** durch diese Vorbereitung.
2. **Pflicht-Voraudit:** bestehende `.github/workflows/publish.yml` und historische `xcmate*-publish*.yml` prüfen. Die vorhandene `publish.yml` wird u. a. von `push` nach `main` ausgelöst und kann nach `main` zurückschreiben. Branch Protection, Rulesets, Release Environments und Required Reviews **noch nicht nachgewiesen**.
3. Auf einer frischen Integrationsbasis die **ausschließlich für Agenten vorbereiteten Dateien** in separatem PR übernehmen; nicht den gesamten alten .95-Baum oder .96-Worktree mergen.
4. Den schreibgeschützten Preflight auf GitHub wirklich ausführen; bisher ungetestete GitHub Actions bleiben mit `CI_NOT_RUN` ausgewiesen. Keine API-Keys in PR-Jobs.
5. Erst danach separaten **manuell gestarteten** API-Codex-Prototypen spezifizieren und freigeben (trusted Runtime/Tokenbudget, Laufzeitlimit, eine Arbeit parallel, Idempotenz, Abbruch). Agent darf nur Draft-PRs auf isolierten Branches schreiben.
6. Danach Work PR-Monitoring und optional privater Drive-Log-Worker; später LAN-ADB-Tests. Freigaben für echte Geräteschreiboperationen und Releases getrennt behandeln.

## Fortschrittsstand dieser Vorbereitung

**Verifikation:** 8/8 lokal reproduzierte gezielte Python-Unittests bestanden und der lokale Beispiel-Preflight meldet `REVIEW_ONLY`. Der lokale Code wurde inhaltsgleich mit dem GitHub-Skript (4096 Zeichen, FNV32 `4bec1366`) geprüft; ein GitHub-Actions-CI-Run **wurde noch nicht ausgeführt**. Das Beispiel verwendet rein synthetische Hashwerte und beweist keine .96-Build-Qualität.
- [x] Separate main-basierte Branchanlage
- [x] Sicherheits-/Projektregeln und PR-Berichtsformat geschrieben
- [x] Architektur- und Implementierungsplan in derselben Branch
- [ ] Hosttests und Preflight per echten GitHub Actions erfolgreich ausgeführt (bis dahin CI_NOT_RUN)
- [ ] GitHub Release-Workflow-Audit und Branch-Gates als geprüft bestätigt
- [ ] OpenAI-API-Runner eingerichtet / Schlüssel sicher hinterlegt
- [ ] Work-Ereignisauslöser eingerichtet
- [ ] Android-Runner angeschlossen
- [ ] XCMate .96 Android-PASS oder automatisches Release

**Keine Tests, Branch-Pushes oder Quellcodeveränderungen an .96 durch dieses Dokument autorisiert.**
