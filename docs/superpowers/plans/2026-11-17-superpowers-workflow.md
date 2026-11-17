# Superpowers Workflow Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans inline; one fresh read-only reviewer at the end. User explicitly requests autonomous execution, no design/plan approval pause for reversible implementation choices.

**Goal:** Reviewable approved-issue intake and safe CI, followed by an independently tested Issue474 fixPR.
**Architecture:** Stdlib Python validates authoritative event+issue metadata; GitHub Actions has read-only permissions and only uploads sanitized task references. No API runner or publication. Product changes remain in their own branch/PR.
**Tech Stack:** Python3.12, unittest, GitHub Actions, existing Kodi fixture tests.
**Spec:** docs/superpowers/specs/2026-11-17-superpowers-workflow-design.md

## Global Constraints
- No main merge/release, no API spending/secrets, no profile/backup deletion, Android NOT_TESTED.
- Existing ModelB/#472 unchanged; currentmain and actual .96 source distinguished before product edits.
- Follow installed Superpowers debugging/TDD/review/verification; if missing report that fact.

## Review Focus
- Spoofed owner/bot/fork or wrong issue cannot initiate work.
- Approval revoked or issue edited after approval blocks intake.
- Untrusted Issue body never appears in shell, logs or artifact.
- Protected paths and symlink/traversal representations cannot bypass guard.
- Synthetic CI is never promoted to Android/release PASS.

### Task1: Approved task envelope and permanent rules
**Files:** AGENTS.md, tools/agent_workflow.py, tests/test_agent_workflow.py, .github/ISSUE_TEMPLATE/codex_task.yml, .github/PULL_REQUEST_TEMPLATE/agent_change.md.
**Interface:** intake(event:dict,current:dict,base_sha:str)->dict with TASK_PREPARED or BLOCKED and fixed reason. No network or writes in pure function.
- [ ] RED: owner+approval creates sanitized reference; each spoof/revoke/edit/PR case blocks.
- [ ] GREEN: minimal validator+CLI; CLI reads files and writes sanitized JSON only.
- [ ] Rules and templates specify actual evidence and deny release/API authorization.
- [ ] Run tool suite, record results; commit.

### Task2: Read-only CI and review guard
**Files:** tools/agent_workflow.py, tests/test_agent_workflow.py, .github/workflows/superpowers-review.yml, .github/workflows/superpowers-issue-intake.yml, docs/agents/SUPERPOWERS_WORKFLOW.md.
**Interface:** inspect_paths(paths:list[str])->dict blocks protected publication/profile/secret paths; changes to CI receive explicit review flag, never automatic authorization.
- [ ] RED: protect existing catalogs/installers/backups/secret-shaped paths and reject unsafe paths.
- [ ] GREEN: CLI for git-diff scope and workflows; source loaded from trusted base for issue trigger, PR workflow no privileged checkout.
- [ ] Local dry-run of actual474 metadata, adversarial event tests, YAML/security validation. No new issue label or live runner activated.
- [ ] Independent read-only review; fix important findings test-first; open Draft-PR, inspect real CI result.

### Task3: First product round and followups
**Files:** separate issue474 branch; own cause/plan/tests per verified runtime source.
- [ ] Reproduce source collision and Save failures before implementation.
- [ ] Minimal fixes, full appropriate host/native verification; preserve actual96 pipeline and all data.
- [ ] Fresh independent review, Draft-PR with evidence. Document configuration-integrity/EPG-timeout followups separately.
