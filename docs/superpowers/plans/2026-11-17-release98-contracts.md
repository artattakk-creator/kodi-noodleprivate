# XCMate .98 release contracts Implementation Plan

> Inline execution with systematic debugging/TDD; independent artwork_qa and epg_mapping_qa review the same final commit. The user's concrete implementation order authorizes implementation without another plan approval loop.

**Goal:** A cumulative .98 review ZIP with genuinely green full host/native CI and preserved historical .96/.97 bytes; prepare, never publish, a Pilot candidate.
**Architecture:** Keep runtime exactly PR484 except addon version/news. Separate immutable .96 source/package checks from explicit .98 current-source/package checks. Existing native engines accept an explicit inspector instead of changing the historical inspector's global version.
**Tech Stack:** Python3.12, unittest/pytest, pinned Git objects, canonical ZIP builder, native Linux-Kodi21.2/BINGIE 720p/1080p.
**Spec:** docs/XCMate/CODEX_KORREKTURAUFTRAG_02998_CI_PILOT_2026-11-17_DE.md.

## Global Constraints
- Base eb6c0857e4cb3abf20ffb94a0ed31e48b7daf59a, PR484; isolated branch release/xcmate-02998-ci-pilot-rc.
- No main merge, regular/Pilot/NeoDark3 catalog edits, installer edits, or historical package replacement.
- Frozen .96 source bc06f521d23ee5c1e6c9aaca456c2b3cc062f3fc has899files exactly matching historical ZIP, SHA64d08c78581d074a9c86fee26ba94011119c1ab0f297de6a0bc9afee13cf1ba9.
- New release .98; .97 Pilot and PR484 review ZIP remain byte-identical. Android NOT_TESTED.
- No test skips/xfails, broad source exclusions, or weakened file/CRC/hash/metadata/publish guards.

## Review Focus
- Historical checks must compare to the exact old source, not .98, and still reject modified old ZIP/sidecar bytes.
- Current checks must reject a jointly wrong manifest/package version, not infer the desired version from the file under test.
- Extra/missing/duplicate/unsafe ZIP members and changed content must fail.
- A changed publication path or approval bit must fail even though the output is review-only.
- Native observer dependencies must not mutate the historical .96 validator or contaminate other test modules.

### Task1: Reproduce and separate contracts
**Files:** tests/historical_release96.py, tests/test_release_candidate96.py, new tests/test_release_candidate98.py; four existing current-version assertions; tools/release_candidate98.py.
**Interfaces:** historical_release96.check(method) executes the unchanged pinned historical package test in an isolated local clone, after verifying the actual retained ZIP/sidecar. release_candidate98 exposes inspect_package(path), stage(output), verify(output), frozen(), safe_output(output), explicit VERSION/NAME/BASE.
- [x] Reproduce six original failures and RED negative historical/current package cases.
- [x] Add immutable historical subprocess fixture; preserve original .96 tests verbatim in pinned checkout; no shared import globals.
- [x] Add versioned .98 review contract and equally strong current packaging/negative tests; update four current-version expectations to explicit .98.
- [x] Focused green tests and commit.

### Task2: Version/package/native CI
**Files:** addon.xml only under runtime; exact reviewed-delta fixture, tools/run_xcmate98_native.py, two native runner optional-inspector arguments, .github/workflows/xcmate98-review.yml, docs/XCMate/test-builds/02998/.
**Interfaces:** native main(package_inspector=None) retains old defaults; .98 wrapper supplies strict .98 inspector.
- [x] RED exact-version/metadata-only/upgrade and no-global-contamination checks.
- [x] Version/news .98, deterministic ZIP/SHA; no live staging.
- [ ] Full pytest/unittest and 17 PO catalogs; native artwork+mapping at720p/1080p against exact .98 ZIP.
- [ ] Commit/push new Draft stacked on484; inspect real CI, fix failures without masking.

### Task3: Independent gates and handoff
- [ ] Both QA agents independently review the same final source and actual new native evidence; preserve profile/token/mapping/widget guards.
- [ ] German test report, historical package proofs, exact build SHA and checksum, Android plan, PILOT_READY only with green gates else RELEASE_BLOCKED.
- [ ] Document in new Draft and related GitHub issue/PR484. No merge or publication.
