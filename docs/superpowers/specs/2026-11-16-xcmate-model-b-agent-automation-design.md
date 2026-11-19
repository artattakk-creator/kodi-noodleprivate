# XCMate Model B — Agentengesteuerte Entwicklungsplattform (Design)
**Status:** ENTWURF ZUR FREIGABE · 16.11.2026 · Dokumentation, KEINE produktive Automatisierung aktiviert
**Projekt:** `artattakk-creator/kodi-noodleprivate`
**Kontext:** separate XCMate-.96-Implementierung basiert auf `fix/xcmate-02995-backup-gate-profile-locks`; kanonische Fachspezifikation #469 und .96-Codex-Übergabe auf `docs/xcmate-02996-codex-uebergabe-20261116`.

## 1. Motivation und Ziel
Den gegenwärtigen Chat-→GitHub-Issue-→Codex-→CI-→Android-Test-→Release-Zyklus reproduzierbar automatisieren, ohne das Eigentümerrecht an Produktentscheidung, bestehenden Kodi-Daten oder Veröffentlichung abzugeben. Vorhandene GitHub-/Drive-Integration und OpenAI-API-Zugang des Auftraggebers nutzen; Superpowers (MIT-lizenzierte Skills) als einheitliche **Entwicklungsmethodik**, nicht als autonomen Agentenserver verwenden.

**Zielwerte (Prozess, keine künstlich vorgegebenen Zeiten):** Jeder genehmigte Codex-Auftrag produziert nachvollziehbar Branch/Draft-PR, Testprotokolle, SHA256-verifizierbaren Test-ZIP und Bericht; jeder P0-Fix benennt Reproduktion, Ursprungshypothese, Test und tatsächlichen Android-Status. Alle Iterationen lassen sich auf eindeutige Commit-SHAs zurückführen.

**Nichtziele:** unbeaufsichtigtes Veröffentlichen in Main/Pilot/NeoDark3; automatische Installation oder Bereinigung auf der Kodi-Box; Work als undokumentierte, extern programmatisch steuerbare Dauer-API; neue TMDB-/IPTV-Zugangsdaten im Repository; Austausch der bereits laufenden .96-Implementierung; ein eigenes komplexes Kubernetes-/Multi-Agent-Cluster.

## 2. Evaluierte Ansätze
- **A. Nur GitHub + Codex:** geringste Einführungskosten, aber fachliche Koordination und wiederholte Entscheidungen bleiben manuell.
- **B. Work + GitHub + Codex + Superpowers + optional eigener OpenAI-API-Runner [gewählt]:** GitHub behält den überprüfbaren Zustandsautomaten; Work betreut Status, Anforderungen und sichtbare Reviews; Codex programmiert; Superpowers regelt den methodischen Workflow; API-Runner kann nach ausdrücklicher Einrichtung eigenständig Issues abarbeiten.
- **C. Vollautomatisches Agentencluster mit dauerhafter Android-Steuerung:** höhere Einrichtungs-/Sicherheitslast, derzeit wegen realem RK3528-Gerät und sensiblen Portal-/Profil-Daten nicht gerechtfertigt.

**Entscheidungen:** Nutzer hat Modell B und Möglichkeit eines vorhandenen OpenAI-API-Zugangs bestätigt. Die folgenden Details sind **vorgeschlagene Architektur-Defaults**, keine schon eingerichtete oder freigegebene Dauerautomatisierung.

## 3. Tatsächlich vorgefundene Basis (16.11.2026)
Im `.95`-Quellzweig sind über 50 `.github/workflows/*.yml` sichtbar, darunter `xcmate94-review.yml`, `xcmate89-review.yml`, `neodark3-latest-only.yml`, `publish.yml`; ein Root-`AGENTS.md` wurde im gezielten Tree-Check nicht gefunden. Bestehende Workflows prüfen synthetische Kodi-/Python-Tests, erstellen ZIP+SHA256 und haben mehrere historisch versionsgebundene Release-Pfade. **`.github/workflows/publish.yml` wird auf `push` nach `main` für bestimmte Pfade getriggert und kann in einem Publikationsjob einen Commit nach `main` pushen.** Dieser Pfad ist vor jeder CI-Bot- oder Auto-Merge-Einführung auf Side-Effects zu prüfen. Branch-Protection/Rulesets wurden noch nicht überprüft; ihre Existenz wird hier **nicht** behauptet.

Der installierte Superpowers-Pluginstatus in ChatGPT bedeutet **nicht**, dass jeder externe Codex-Prozess es schon geladen hat. Für externe Codex-CLI/SDK-Läufe müssen offizielle Superpowers-Skills explizit bereitgestellt und ein korrekter Skill-Pfad/Version im Runprotokoll ausgewiesen werden. Codex-Multiagent-Funktion ist eine **optionale** Konfiguration, nicht in diesem Chat nachgewiesen.

## 4. Architektur und verbindliche Rollen
```text
Nutzer / Freigaben (Produkt, Gerät, Release)
       |                                ChatGPT Work (nicht-kritische Koordination,
       |                                 PR-/Log-Reports, Status, Issue-Hygiene)
       v                                       ^
GitHub Issue/PR/Labels/Approvals <------------+
       |
       | genehmigter agent-ready-Auftrag / manueller workflow_dispatch
       v
GitHub Actions / koordinierender API-Runner
       | -- Codex Implementierer (isolierter Branch/Worktree; eigener Scope)
       | -- Superpowers: Specs -> Plan -> TDD -> Review -> Verifikation
       | -- unabhängiger Reviewer + Regressionstests
       v
Draft-PR + konkrete Tests + SBOM/ZIP/SHA256/Statusbericht
       |
       +--- Android Realgerät: NOT_RUN -> echter PASS/FAIL, manuelle Abnahme
       |
       +--- GitHub geschütztes Release Environment: nur explizite Freigabe
Google Drive: privater Backup-/Log-Quellspeicher; bereinigte Befundberichte in Issues
```
**GitHub ist die einzige dauerhafte technische Wahrheit** für Issue-ID, Branch, Commit SHA, CI-Status, Candidate-ZIP-Hash, Android-Status, Freigaben. Work kann Berichte vorbereiten, soll aber weder einen versteckten Deployment-Zustand noch die einzigen Zugangsdaten halten. Eigener OpenAI-API-Runner ist ersetzbar: Codex CLI/SDK als bevorzugte Code-Ausführung mit Git-/Testzugriff; alternativ ein Responses-API-Agent mit eingeschränkten Tools und eigenem Job-Controller.

**Agentenrollen:**
1. **Triage/Plan:** vorhandene Issue-Duplikate, Korrelationen, sichere Akzeptanztests, bounded Scope und Abhängigkeiten.
2. **Codex Implementierer:** genehmigtes Issue auf eigenem Branch/Worktree, Tests zuerst, punktuelle Fixes, Draft-PR.
3. **Unabhängiger Reviewer:** Code ohne Implementierer-Kontext auf Sicherheits-, Datenverlust-, P0- und Regressionseigenschaften prüfen. Kein Self-Approval.
4. **CI/Test-Automat:** Hosttests, synthetische Kodi-Tests, Paketbaum-/ZIP-SHA256-Checks, Version/Repo-Index-Konsistenz.
5. **Log-Analyst:** private Kodi-Logs lesen, Portale/Tokens/Netz-URLs/SMB-Credentials entfernen, Ereignisanzahlen/Zeiträume/Codepfade dokumentieren.
6. **Release Gatekeeper:** prüft ausschließlich formale Gates, kann nie allein aufgrund einer Agentenbehauptung Android-PASS oder Releasefreigabe setzen.

## 5. Vertrauensgrenzen und GitHub-Zustandsautomat
**Vorgeschlagene, ausdrücklich einzuführende Labels:** `agent:planned` (Entwurf), `agent:ready` (menschlich geprüft), `agent:running`, `agent:review`, `agent:blocked`, `android:not-run`, `android:pass`, `android:fail`. Labels allein sind kein Sicherheitsnachweis: jeder Job überprüft Repo, Issue-Autorisierer, SHA/Ref, GitHub-Akteur/Rechte und ein getrenntes Freigabeereignis; kollidierende/alte Runs werden per Concurrency/Generation abgebrochen.

**Ausführungsvorschlag:**
- `workflow_dispatch` oder von Berechtigten gesetztes `agent:ready` startet nach noch zu definierender Authentifizierungsprüfung genau einen API-Agent-Lauf.
- Agent erstellt nur Feature-Branch und **Draft-PR**. Niemals direkte Commits nach `main`, `pilot`, `online-test` oder veröffentlichte Repo-Verzeichnisse.
- CI muss auf *exaktem Commit* bestehen. PR-Testjobs haben `permissions: contents: read`; keine Secrets für PR-/Fork-Code. Externe LLM-Schlüssel ausschließlich in genehmigtem und isoliertem trusted Workflow oder kontrolliertem selbst gehostetem Runner.
- Keine `pull_request_target`-Ausführung ungeprüften PR-Codes, keine `GITHUB_TOKEN`-/OPENAI_API_KEY-Ausgabe in Logs, keine untrusted Shell-Konstruktion aus Issue-Text.
- Merge nur mit Branch-Protection/Required-Checks/CODEOWNERS-/Mensch-Review, *nach* Audit des bestehenden `publish.yml`; Release über separat geschütztes GitHub Environment mit `required_reviewers` und kanonischem Manifest. **Weder ein Auto-Merge noch das Verschieben eines Labels darf bestehende Publikations-Gates umgehen.**
- Rohtexte aus Issues/PRs/Logs sind **untrusted Inputs**, nie Systemanweisungen. Codex-Scope und schreibbare Pfade vorgeben, keine Geheimnisse an den Implementierungsagenten übergeben, nur synthetische Portale in CI.

## 6. Superpowers-Prozess und Auslieferungen
Für *jeden* Development-Auftrag:
1. `brainstorming` und genehmigte fachliche Spezifikation, bei neuen Funktionen zuerst Design-Freigabe;
2. `writing-plans` mit konkreten Dateien, Funktionssignaturen, Fehler-/Regressionstests;
3. `using-git-worktrees` oder vergleichbar isoliertes Git-Arbeitsverzeichnis;
4. `systematic-debugging` (bei Defekten) und `test-driven-development` mit *zuerst rotem Test*;
5. `subagent-driven-development`/gleichwertige sequenzielle Arbeitsaufträge mit je Aufgabe unabhängigem Review; parallele Arbeiten nur bei voneinander isolierten Dateien/Schnittstellen;
6. `verification-before-completion` anhand tatsächlicher CI-/Testausgaben; `requesting-code-review` vor Freigabe;
7. `finishing-a-development-branch` nur Draft-PR/Abnahmevorschlag, kein selbstständiger Main-Merge.

**`AGENTS.md`-Vorgabe:** Herkunft verifizierter Fachanforderungen, Pflicht-Tests, CI-Befehle, Python/Kodi-21.3/ARM32-Versionen, Privatsphäre/Logs, Branch-Gates, `ANDROID_NOT_RUN` bis realer Test, Legacy-`settings.xml`-/EPG-LastGood-Schutz, Schutz vor Produktivdaten-Migration und Offline-Hardware-Testkriterien.

## 7. API-Runner, Work und Kosten
- **Erstes MVP:** weiterhin ein durch Nutzer/Codex gestarteter Task, aber standardisierte Reviewer und CI; *kein* Dauerdaemon nötig.
- **Optionale zweite Phase:** eigenständiger API-Runner mit OpenAI-Schlüssel aus Secret Store, nicht als Datei/Commit/Issue. Er prüft vor jedem Job Authorisierung, begrenzt Laufzeit, Token-/Budget, Parallelität (Default **1 aktiver Entwicklungsjob**), Iterationen/Fehler-Retry und erzeugt einen vollständigen Audit-Trail. **Keine vorgegebenen Eurobeträge** – Nutzer legt monatliche API-Kostenobergrenze fest. Zahlungen/Keyzugang sind getrennt vom ChatGPT-Tarif.
- **Work:** PRs beobachten, Querverweise/Statusberichte vorbereiten, Screenshots/Logs organisieren; Work-Auslöser nur nutzen, wenn im Konto tatsächlich verfügbar und vom Nutzer eingerichtet. **Keine Behauptung, dass wir Work programmgesteuert aus dem API-Runner starten oder dessen Bearbeitungserfolg aus der GitHub-Action garantieren können.**
- **Superpowers:** quelloffene MIT-Skills, keine eigene Modelllizenz; in ChatGPT verbunden, extern je Runner zu konfigurieren; optionaler kommerzieller Herstellersupport ist unabhängig.

## 8. Google Drive und Android
- Drive bleibt privater Ablageort für vollständige Kodi-Logs, Backup-ZIPs, Profile und Diagnoseartefakte. Der CI-Agent bekommt **keine blanket Drive/Google-Account-Credentials**. Ein separater, explizit autorisierter Logimport-Service kann bei Bedarf einen einzigen Ordner lesen; Dateiendungen/Maxgröße/Hashes/Dateiänderung belegen, Credentials/redact und lokale Berichte erstellen.
- Logsanitizer behandelt HTTP-/IPTV-/SMB-URLs mit Queryparametern, Passwörter, IPs/Hostnamen, Geräte-IDs, Profil- und Portal-IDs als Geheimnisse. Eine Zählung von `GROUP_SQL_BUSY` ist **kein** funktionierender Hardware-Abnahmetest.
- Optional später dedizierter Windows-/Linux-/LAN-Testagent über ADB/JSON-RPC an Android-Box **nur mit lokaler Netzfreigabe**; kein ADB an das Internet, keine universelle Remote-Löschung. Geräteprüfungen: Startsender, Gruppenwechsel, EPG, 16:9-Hero, Senderlogo-Override, Neustart, Cache 32–256 MiB, aktuelles `.96`-ZIP.
- Android Teststatus initial `NOT_RUN` bei jedem neuen exakten Commit/ZIP; PASS gilt nur für getesteten Commit/Hash auf realem Gerät; mit jedem neuen Code-Commit zurücksetzen.

## 9. Schichtenweise Einführung (je ein eigenes prüfbares PR)
**Phase 0 / Inventar & Absicherung:** vollständiges Audit aller Push-/Release-Workflows, die `main`, `online-test`, Pilot/NeoDark3 beschreiben; Branch-Rulesets/Required-Checks/GitHub Environment verifizieren. Ergebnis: dokumentierter "keine Auto-Release trotz Agentenänderung"-Beweis.

**Phase 1 / Agenten-Vertrag:** Root-`AGENTS.md`, `docs/superpowers`-Speicherplatz, PR-Vorlage mit Abnahme-Befunden, vorhandene Tests/Build-Skripte verlinken; zunächst **nur** Policy-/Docs-PR, kein Publikationsworkflow.

**Phase 2 / Review-only CI:** ein kanonischer `xcmate-agent-review.yml` Workflow, ausschließlich PRs und manuell, least privilege, exakte ZIP-/SHA256-/Repo-Tests, Datenschutzscanner, Statusbericht; keine neuen Publikationsschritte. Bestehende versionsgebundene Review-YMLs erst nach CI-Parität konsolidieren.

**Phase 3 / API-Codex-Prototyp:** nur `workflow_dispatch`, authorisiertes Test-Issue, ein isolierter Agenten-Run, Taskbudget/Timeout, max. ein Draft-PR, kein Secrets-Zugriff im Code-Runner. Folge: `agent:ready`-Anstoß bei nachweisbarer Autorisierung. Work-PR-Bericht optional und als unterstützender, nicht zwingender Prozess.

**Phase 4 / Log-Worker & reale Tests:** redigierte Drive-Loganalyse und später LAN-ADB-Smoke-Runner separat; explizite Geräteautorisierung. Menschliche Freigabe vor jedem Schreiben am Gerät.

**Phase 5 / geschützte Releaseverwaltung:** erst nachdem Phase 0–4 nachweislich korrekt sind. Release-Freigabe getrennt von Merge-/PR-Autorisierung; keine automatisierte Freigabe allein durch Erfolg eines LLM-Agenten.

## 10. Abnahmekriterien für Modell B
1. Eine untrusted Issue / PR kann **weder** API-Schlüssel noch Kodi-/Drive-Geheimnisse auslesen, **noch** einen Release/Deployment anstoßen.
2. Ohne manuelle Agentenfreigabe **kein** Codex-Lauf; bei parallelen Labels/Dispatches kein doppelter kostenpflichtiger Job; bei Budgetende sicherer STOP + Ursache.
3. Agent generiert Draft-PR auf Feature-Branch, mit Rückverfolgbarkeit `issue_id`, `run_id`, Commit-SHA, Code-Änderungsumfang, Test-/Review-/Build-Reports und ZIP+SHA256.
4. Für jeden geänderten Commit Android-Status wieder `NOT_RUN`; CI-PASS darf das Hardware-Gate nicht automatisch erfüllen.
5. Changes to `main` oder Pilot/NeoDark3 sind nachweislich durch verpflichtende Reviewer/Protected Environment/Release-Manifest gesperrt, auch bei bestehenden `publish.yml`-Side-Effects.
6. Private Kodi-Logs und Tokens bleiben aus Issues, PRs, Workflow-Logs und ZIPs heraus.
7. Vollständiger Entwicklungsprozess funktioniert auch ohne Work-Ereignis-Plugin (GitHub ist source of truth).
8. Nutzungs-/Tokenverbrauch und API-Abrechnungsgrenzen pro Issue verfolgbar; keine unbegrenzten selbstgestarteten Agentenketten.
9. Das laufende XCMate .96-Entwicklungsprojekt bleibt unverändert und bekommt keine ungeprüfte neue Runtime-Abhängigkeit.

## 11. Noch zu bestätigende Implementierungsvorgaben
1. **API-Ausführungsort:** zunächst GitHub-hosted Runner als vorgeschlagener Standard, bei Sicherheits-/Budget-Constraints kontrollierter eigener Runner; erst in der Implementierungsplanung verbindlich entscheiden.
2. **Monatliches API-Budget / Maximalzeit pro Auftrag:** vom Nutzer zu setzen (keine automatische Abrechnungslimit-Veränderung).
3. **Automatische Aufgabe starten:** zunächst ausschließlich `workflow_dispatch` (sicherer), Labels erst nach erfolgreichem Test der Berechtigungsprüfung.
4. **Android-Testzugriff:** nicht für Phase 0–3 erforderlich, später eigene Freigabe.

## 12. Nächster Schritt nach Nutzerfreigabe
Ein detaillierter Superpowers-Implementierungsplan in `docs/superpowers/plans/` mit kleinen testbaren Aufgaben und getrennten PRs; **noch keine Produkt-/Workflow-Änderung** durch dieses Design.

Referenzen: `https://github.com/obra/superpowers` (MIT); `https://github.com/artattakk-creator/kodi-noodleprivate/issues/469` und die im Projekt vorhandenen Workflows.
