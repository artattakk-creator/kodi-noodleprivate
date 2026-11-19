# Verifikation der Superpowers-Struktur – 17.11.2026

## Ergebnis und Grenzen

Implementierung: `fd863130b1716704f3c22b37d2514cfe1d546c1e`, Draft-PR #477, Basis `ec5755e2cb3d8d30d89c24b56f72a70e9c17b3ce`.

| Prüfung | Tatsächliches Ergebnis |
|---|---|
| Eigene Validator-/Policy-/Injection-/Rename-Tests | 12 PASS mit System-Python und separater Test-venv |
| Neuer PR-Workflow | PASS: https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/44053627790 |
| Vollständiger alter main-Hostworkflow | FAIL: 3.927 Tests, 21 Fehlerwartungen fehlgeschlagen und 5 Exceptions; https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/44053628172 |
| Unveränderte main-Basis, exakt dieselben 26 Fälle | Identisch FAIL: 21 fehlgeschlagene Assertions, 5 Exceptions, 26 Tests / 4,550 s |
| Unabhängiger read-only Review | Drei P2-Befunde vor Korrektur reproduziert, anschließend durch gezielte Tests geschlossen |
| Automatisches Issue-Intake auf Defaultbranch | PREPARED_NOT_ACTIVE; nicht gemergt, kein Live-Auslöser behauptet |
| Kostenpflichtiger API-Agent | NOT_CONFIGURED; Kostenlimit 0 |
| Physische Android-Geräte | ANDROID_NOT_TESTED |

Die 26 main-Baselinefehler betreffen historische Veröffentlichungs-/Archivverträge: Tests erwarten ältere Pilot-Indizes oder inzwischen archivierte .87/.88/.89-ZIPs; Release92 kann seinen historischen Vorschlag nicht mehr unverändert bilden. Diese PR ändert keine solchen Tests oder Veröffentlichungskataloge. Ein vorübergehend zusätzlich eingeführter PyYAML-Importfehler wurde durch Standardbibliotheksvalidierung des JSON-kompatiblen YAML behoben; er ist im aktuellen Ergebnis nicht enthalten.

Baseline-Reproduktion: separater Shared-Clone, detached `ec5755e2`, unveränderte Dateien und exakt die im CI-Log genannten 26 unittest-Methoden. Keine Archivdateien in den Live-Checkout zurückkopiert. Die Gesamtsuite wird ausdrücklich nicht als grün gemeldet.

## Review und Autor-Nachprüfung

Der Reviewer las Code und Tests in eigenem Kontext. Befunde: (1) zu enger PR-Trigger ließ andere Produkt-/Schutzpfadänderungen ungeprüft, (2) Git-Rename verbarg den geschützten Ursprung, (3) veröffentlichte Repository-ZIPs im Wurzelverzeichnis fehlten im Guard. Autor-Korrekturen: Workflow für alle PRs, `git diff --no-renames --name-only -z`, expliziter Schutz von Root-Repositorypaketen. Alle drei vor Korrektur RED, danach GREEN in 12 Tests. Kein behaupteter zweiter unabhängiger Gesamt-Review.

## Parallel vorhandene Automatisierungsentwürfe

PR #475 bereitet einen anderen, optional API-gestützten read-only Triageweg mit `codex-ready` vor. Issue #476 beschreibt dessen spätere kostenpflichtige Schreibphase. PR #472 bleibt ein älterer, unveränderter Entwurf. Diese PR #477 ergänzt den API-freien, eigentümergeprüften Auftragseingang mit `codex:approved` und einheitliche Superpowers-/Schutzregeln. Kein Label startet hier eine LLM-Ausführung.

Vor Integration der parallelen Entwürfe die gemeinsame `AGENTS.md`, Labelkonvention und Rollenaufteilung abgleichen. Nichts wurde automatisch zusammengeführt oder aktiviert. Vor externem schreibendem Runner außerdem Branchschutz, Required Reviews, API-Budget und bestehende schreibende Publisher prüfen. Der vorhandene Workflow namens „Publish GS Media Kodi updates“ lief beim PR ebenfalls, sein tatsächlicher Job `publish` war **SKIPPED**; diese Arbeit veröffentlichte kein Paket.

## Erste tatsächliche Entwicklungsrunde

Produktfix #474: separater Draft-PR #478, `.96`-Source-Basis aus #471. `main/src` ist noch .92; daher bewusst gestapelt statt Produktversionen zu vermischen. Review, Paket und vollständige Produkttests sind im eigenen PR dokumentiert. Konfigurationsintegrität und globale EPG-Timeouts bleiben eigene nachfolgende Aufgaben.
