# XCMate Model B — Safe Agent Framework Preparation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create an isolated, verifiable, opt-in foundation for XCMate's Work/Codex/Superpowers/OpenAI-API development process, without changing XCMate .96, accessing secrets, spending API budget, or publishing releases.

**Architecture:** A main-based preparation branch contains the human/agent contract (`AGENTS.md`), templates, a pure Python **review-only** gate with focused unit tests, an unprivileged opt-in GitHub Actions preflight and a migration checklist. GitHub is the source of truth; no background agent, AI API call or hardware process is started by this preparation.

**Tech Stack:** GitHub Issues/Actions, Python 3.12 standard library, Codex, Superpowers skills, ChatGPT Work as optional coordination layer.

**Spec:** `docs/superpowers/specs/2026-11-16-xcmate-model-b-agent-automation-design.md` (approved scope: non-production *preparation* only; architecture's future paid/automated execution remains gated).

## Global Constraints

- Repository `artattakk-creator/kodi-noodleprivate`. Source version .96 under active separate Codex work; no XCMate add-on or pilot/regular/NeoDark3 repository code modifications here.
- No direct commits to `main`, `online-test`/Pilot channels; no automatic publish, merge, installation, cleanup or setting migration.
- Never put IPTV credentials, token values, private Drive links, raw Kodi logs or secret-bearing URLs into code, issues, CI output or test ZIP.
- `ANDROID_NOT_RUN` is the default for each *new exact commit + ZIP SHA256*; mocked Kodi tests do not constitute a hardware PASS.
- The OpenAI API key is **not** available in any PR workflow; external Codex Runner and Work triggers must be separately approved and connected.
- Preserve remote UX (D-Pad/OK/long-OK/Back), provider EPG baseline, user mappings, TMDB token and settings on Kodi 21.3 / ARM32.
- Superpowers installed in ChatGPT does **not** mean CLI/SDK runner has its skills: provision/version them separately before enabling paid jobs.

## Review Focus

1. Untrusted PR tries to set `approval.release=true`: manifest preflight must fail and never publish.
2. `android.status=PASS` without exact matching SHA/evidence: preflight must reject, not assume hardware validation.
3. Case-insensitive or malformed hashes, missing mandatory test results: fail closed.
4. Path traversal via CLI manifest argument: reject external paths.
5. Agent event triggered twice while .96 runs: read-only CI has no LLM invocation, zero GitHub writes, zero secrets; later API runner must enforce idempotency and concurrency.

---

### Task 1: Document human/agent contract and integration points

**Files:**
- Create `AGENTS.md`
- Create `.github/PULL_REQUEST_TEMPLATE/agent_change.md`
- Create `docs/agents/MODEL_B_HANDOVER.md`

**Interfaces:**
- Consumes the design document and issues #469 (XCMate .96) / #470 (agent framework).
- Produces mandatory branch/review/release boundaries for future Codex sessions.

- [ ] **Step 1: Define testable contract:** allowed writes confined to independently approved feature branches; release permission never implied by CI PASS; no tokens or private logs in PR.
- [ ] **Step 2: Provide task-specific instructions:** read exact issue, confirm branch/base, use Superpowers when externally installed, TDD, exact SHA, report Android test as NOT_RUN unless validated.
- [ ] **Step 3: PR template:** source SHA, issue, host/Kodi-sim PASS/FAIL evidence, ZIP/SHA256, screenshot/hardware acceptance, reviewer and explicit release authority fields.
- [ ] **Step 4: Commit in isolated prep branch, no PR or deploy side effects.**

### Task 2: Contract-first, local-only preflight gate

**Files:**
- Create `tools/agent_framework/preflight.py`
- Create `tests/test_agent_framework_preflight.py`
- Create `docs/agents/examples/review-only.json`

**Interfaces:**
- `evaluate(manifest: dict) -> dict` returns `{"status":"REVIEW_ONLY","reason":"..."}` for an eligible report, otherwise `{"status":"BLOCKED","reason":"..."}`.
- `main(argv: list[str] | None = None) -> int` reads a **repo-local** JSON manifest; exit code 0 only for `REVIEW_ONLY`, code 2 for invalid/blocked.
- No network I/O, subprocess, GitHub mutation, secret access or API calls.

- [ ] **Step 1: Write failing unit tests** for well-formed review-only, missing hash, release/merge flags true, spoofed Android PASS, failed tests and path traversal.
- [ ] **Step 2: Execute `python -m unittest tests/test_agent_framework_preflight.py -v` to witness RED.**
- [ ] **Step 3: Implement minimum standard-library schema gate** with strict bool/int/string validation, hexadecimal exact lengths and explicit release-denial.
- [ ] **Step 4: Execute same command for GREEN; then full repo tests if feasible; report both exact results.
- [ ] **Step 5: Commit on prep branch.

### Task 3: Read-only, opt-in GitHub Actions review workflow

**Files:**
- Create `.github/workflows/xcmate-agent-preflight.yml`

**Interfaces:**
- Events: `workflow_dispatch` and `pull_request` scoped ONLY to agent preparation files; no `push` and no release environment.
- Permissions `contents: read` only; run Python standard-library unit tests and `preflight.py` against sample manifest; upload an optional non-sensitive text summary (not required).

- [ ] **Step 1: Check action trigger and permission scope** against current `.github/workflows/publish.yml` and existing CI.
- [ ] **Step 2: Configure `actions/checkout@v4`, `actions/setup-python@v5`, timeout 5m and job concurrency; no `OPENAI_API_KEY`, repo-write token or local Android access.
- [ ] **Step 3: Execute local Python checks and validate workflow YAML syntax; GitHub Action run remains NOT_RUN until a real runner executes it.**
- [ ] **Step 4: Commit only workflow file, not any existing release workflow.

### Task 4: Seamless .96 integration without release side effects

**Files:**
- Modify `docs/agents/MODEL_B_HANDOVER.md` with handoff commands/links.
- Add non-executable checklist to Issue #470, no webhook or state-changing label.

**Interfaces:**
- Codex .96 finishing: capture draft PR, commit SHA, exact build ZIP/SHA256, 37+ host tests' actual evidence, explicit `ANDROID_NOT_RUN/PASS/FAIL`.
- Reviewer reads #469, #470, plan/AGENTS; no rebase, merge, release or auto-start.
- External API runner phase **not implemented**: must separately decide trusted runtime, key secret storage, token/time/monthly budget and one-job concurrency.

- [ ] **Step 1: Handoff steps for Work, Codex, GitHub Actions and Drive; separate human release check.**
- [ ] **Step 2: Verify exact GitHub file content and branch base, public/private URLs and master issue.**
- [ ] **Step 3: Report what was actually tested vs prepared, alongside next activation approvals.**

## Not in this preparation
- No automatic Codex tasks, no API-key secrets, no live Work trigger, no Drive watch, no Android ADB/JSON-RPC control, no GitHub environment/ruleset changes, no merge to main.
- Future implementation separate PRs: GitHub CI/release audit, authenticated issue-to-Codex runner with rate/cost limits, Work PR monitoring (only when available), private log sanitizer, LAN hardware runner, protected release environments.
