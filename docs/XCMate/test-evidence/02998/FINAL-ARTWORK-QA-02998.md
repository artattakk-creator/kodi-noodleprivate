# Independent final artwork QA — 0.1.29.98

**ARTWORK_QA_PASS in the reviewed synthetic host and native Linux Kodi 21.2, 1280×720 / 1920×1080 scope. ANDROID_NOT_TESTED. No confirmed artwork release blocker remains within that scope. This is not merge, publication or physical-device authorization.**

## Source and evidence identity

- Reviewed source/test commit: `c5ecd2ea69bb84e648cae9433d250613dceff46e`, branch `release/xcmate-02998-ci-pilot-rc`.
- Independently read local HEAD tree: `acfa4a2f6ada768f483bfc80f43c7b1e3d49d08b`.
- Exact ZIP: `docs/XCMate/test-builds/02998/plugin.video.xtreammate-0.1.29.98.zip`; independently calculated SHA256 `d37d34fbb5be5e46154b912d3ce960f6e248431fcf7d0a9651fa9785b20a12c3`; 901 files, 4,772,893 bytes.
- Fresh final workflow: [44117233113](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/44117233113); native artwork jobs `134158531190` (720p) and `134158531510` (1080p). Direct read-only GitHub job metadata confirms SUCCESS for both exact-ZIP native steps and all six jobs.
- Actual CI checkout is GitHub's virtual test merge `a7f718bc498f8dc6f86bdd802a24cdb2c8e36e48`, independently confirmed in both logs and commit metadata. The supplied `source-identity.json` records its entire tree as the same `acfa4a2f...` locally observed for c5; this is a test merge, not a merged repository branch.
- All 14 fresh final PNGs were independently viewed. Each local SHA256 matches its PNG87 record fetched directly from the corresponding final job log. Earlier .97 and initial .98 screenshots were not used as final .98 proof.

Final evidence files are currently untracked additions in the author's checkout. This reviewer wrote only this report and its checksum manifest in its own `/tmp` scratch; no source/test/Git/GitHub/profile changes.

## Runtime and guard preservation

Independently compared all 901 runtime files with base `eb6c0857e4cb3abf20ffb94a0ed31e48b7daf59a`: only `addon.xml` changes; normalizing version and news makes it identical. Product source, current package inspector, historical helper, native artwork wrapper/engine and ZIP have no diff between reviewed initial .98 `2f434987eb397011295a4039e8a6bba7ffffa42b` and frozen c5. Unchanged whole host batches were therefore not repeated at c5.

`tests/historical_release96.py:17–23` checks the retained .96 ZIP's fixed original digest and immutable sidecar before historical tests. `:25–39` executes the unchanged original methods in an isolated child checkout/interpreter. Own parent-module poison reproduction passed both historical methods without changing parent poison or contaminating the current .98 inspector.

`tools/release_candidate98.py:32–54` retains exact members, duplicates, CRC, unsafe/private-name, every-member bytes and manifest guards; `:96–149` retains output/publication/plan/sidecar protection and frozen old artifacts. `tools/run_xcmate98_native.py:15–17,30` inspects strictly before execution and injects the same inspector explicitly. Native engines preserve the .96 default when no inspector is supplied. Own tampered product ZIP was rejected as `RC98_SOURCE_BYTES` for both wrapper modes, with zero engine calls. No weakened guard or demonstrated import contamination found. Confidence: high for the exercised boundaries.

## Pipeline evidence

| Stage | Result and boundary |
|---|---|
| Source-qualified SQLite facts/event identity | PASS: own healthy reproduction loads actual event; native fixture uses an existing verified guide revision. Fake revision remains rejected. |
| Existing consent / storage policy | PASS: disabled/deferred/invalid policy remains closed and classified; explicit healthy synthetic consent works. No automatic real-account enablement. |
| Settings health | PASS: corrupt settings through product accessors and actual worker retain `SETTINGS_XML_INVALID`, preserve private bytes and perform zero external calls. |
| Request / drain / worker | PASS: request and blocked admission statuses survive; actual worker reports RUNNING/completion or classified errors. |
| TMDB candidate matching | PASS in own host reproduction using the actual matcher and canned `search/movie` and `movie/6801` responses; real TMDB/TVMaze/XMLTV account/network availability UNKNOWN. Native metadata matching is explicitly a synthetic candidate stub. |
| Safe URL / transport / decoder | PASS: own actual bounded safe transport fully decodes a 1280×720 PNG; native loopback TLS supplies synthetic image bytes through real transport, decoder and Kodi texture machinery. |
| Local/RAM / reserve fallback | PASS: own 64 MiB free / 1 GiB archive reserve case reports RESERVE_BLOCKED while the correct dynamic local image remains eligible/LOCAL_IMAGE_READY. Native Python capacity injection is 27 MiB. Physical ENOSPC UNKNOWN. |
| Programme display / widget metadata | PASS: source-bound consumer image, completion/result and detail model control 110; native Hero/display path remains eligible. |
| BINGIE binding / texture | PASS: actual final native Hero and detail screenshots show distinct programme and logo texture areas at both resolutions. |
| Visible status | PASS for native requested/running/ready/settings-invalid/disabled projection and reviewed host terminal states; not every external fault was produced end-to-end in native Kodi. |

The own healthy reproduction traverses actual SQLite → matcher → safe transport/full PNG decode → local committed file → completed/result → ProgrammeWindow46.pump control 110. Result: READY, tmdb_movie, decoded77, LOCAL_IMAGE_READY, eligible, identical bound image, synthetic pixel `(27,89,139)`. Native fixture substitutes candidate identity, pins its synthetic origin to loopback, and exercises real image transport/decode/texture and consumer rendering. These are complementary proofs, not a claim of real TMDB access.

## Fresh visible native results

Both actual Hero PNGs show the large synthetic programme blue image, a distinct small station logo, `Sendungsbild gefunden.`, `Bild: TMDB` and local EPG data. Both 305-second detail PNGs show the same programme texture and facts with attribution; no image replacement by the magenta foreign widget behind the dialog.

Own full-screen pixel counts within ±8/channel of synthetic programme `(20,80,130)`:

| Resolution | Hero | 305-s detail | Foreign-widget frame |
|---|---:|---:|---:|
| 1280×720 | 194,110 | 151,216 | 0 |
| 1920×1080 | 437,100 | 340,236 | 0 |

Foreign-widget frames instead contain 352,376 / 794,396 pixels near independent magenta `(160,60,110)`. This distinguishes the source motifs; it is not merely URL approval or a setArt receipt.

Final logs independently contain sticky wall times 306.11 s / 306.06 s, with stable measured texture checkpoints at approximately 2, 46, 121 and 305 seconds after the injected negative status at 45 s. Only the delivered final 305-s PNGs were visually inspected, while intermediate stability comes from the native log assertions.

All four status PNGs at both resolutions contain readable, differentiated text: `Bildsuche angefordert …`, `Bildsuche läuft …`, the two-line damaged-settings explanation, and the disabled-picture-EPG explanation. Native status fixture is expressly `INJECTED_PRODUCER_STATE_NATIVE_HERO_PROJECTION`; settings mutation is false. Valid Home/ListItem receipts precede projection: window 10000, focus 2510, Home50 true, portal/channel matches and nonempty widget token. Production eligibility guards remain intact.

The 720p RUNNING and IMAGE_EPG_DISABLED PNGs catch transition frames with some other Hero metadata and rows hidden. They prove visible status, not a completely settled whole screen. At 1080p the final Hero/status frames show VOD/series placeholders and `Katalog/Bilder momentan nicht erreichbar · Erneut versuchen`; 720p earlier frames show synthetic cover cards. The synthetic data lane has ended at that point. **These frames do not establish continuous VOD/series-cover availability.** No general production catalogue-health PASS is inferred.

Logs also establish 13 unchanged foreign-widget definitions from seven synthetic independent sources and two offline native Application.Quit/supervised Kodi restarts per resolution, with changed process IDs, protected-file hashes and KODI_TEXTURE_CACHE recovery. Only the supplied representative foreign frame per resolution was visually inspected; not every foreign/restart screenshot was supplied for visual review.

## A1–A5

| Gate | Verdict |
|---|---|
| A1 — image job | PASS: visible request/work state, honest policy-blocked admission, producer-path host coverage and native projection. |
| A2 — sources | PASS within synthetic consent/settings/source selection scope; no real token or service validation. |
| A3 — pixels | PASS: fresh final .98 real native Hero/detail pixels independently inspected at 720p and 1080p. |
| A4 — storage | PASS for host and injected native pressure, preserving dynamic fallback/reserve; physical full disk and Android storage untested. |
| A5 — status | PASS for the native working/ready/settings/policy cases and host terminal explanations, with the transition-frame limits above. |

High confidence in the reviewed synthetic host/native scope. No newly confirmed artwork defect or artwork-specific release blocker. Mapping, playback, real suppliers and hardware remain outside this gate's certification.

## Tests and retained regressions

Own independent initial .98 focused result: 74 PASS in 18.99 s (current package/native release, artwork482, legacy art_status70 and pipeline68). Historical parent-poison and tampered-ZIP reproductions additionally passed. Healthy/settings/reserve scratch reproductions are retained beside this report.

Direct final host job logs independently confirm **4225 pytest PASS**, four warnings, 1108.09 s; **4214 unittest tests, OK**, 983.879 s. Current final job metadata also confirms all four native matrix jobs succeeded. Historical .96 checks are executed, not skipped/xfailed.

Keep these regression boundaries: `tests/test_xcmate_artwork482.py:23,40` distinct policy request/drain reasons; `:55` actual corrupt-settings worker/privacy; `:71` healthy decode-to-detail; `:110,118` loading and sanitized terminal Hero text; `:130` real revision required; legacy detail explanations in art_status70/pipeline68. `programme_diagnosis70.py:9–12` must intercept only policy/settings errors so legacy Helper/Kodi/HTTP/NO_IMAGE details are retained. `programme_state482.py:43–50` must retain fixed texts and the safe fallback. Native future regression assertions must require actual non-logo motif pixels, source identity, visible consumer/control receipts, 305-s retention, readable text at both resolutions and negative settings/policy paths without changing consent.

## Open device acceptance

**ANDROID_NOT_TESTED** for physical RK3528 / Kodi 21.3 / BINGIE: cumulative .97→.98 update preserving profiles/keys/maps/widgets; real source-correct Hero and detail texture after five minutes; requested/running/ready/no-match/auth/settings/policy messages; existing opt-out and valid prior consent respected; provider guide available with artwork disabled; two real offline restarts; low-space/SMB behavior without forced reserves or deletion; foreign widgets and playback/back/remote navigation. Real API/token/CDN and hardware decoder behavior remain unverified. No physical ENOSPC test was performed; Kodi C++ texture writes still had actual host free space during Python capacity injection.

The earlier evidence-pending ARTWORK_QA_FAIL is superseded solely because fresh final .98 native proof is now present. This scoped PASS supports the parent's release-candidate assessment; it does not authorize merging, publishing, installing or changing user data.

## Reproduction / evidence locations

- Own scripts: `/tmp/artwork-qa-02998-2f434987/healthy98.py`, `guard_probe98.py`; own source snapshot in this directory.
- Shared independent stage probe: `/tmp/artwork-qa-initial-20261117/stage_probe_final.py` with the exact .98 snapshot argument.
- Fresh viewed PNGs: `/tmp/release98-final-evidence/artwork-720/` and `artwork-1080/`.
- Fresh PNG checksums independently compared with final GitHub logs: `FINAL-PNG-SHA256SUMS` beside this report.
- Exact native reproduction command (CI-capable host): `python tools/run_xcmate98_native.py --kind artwork --report-dir /tmp/native98-review --addon-zip docs/XCMate/test-builds/02998/plugin.video.xtreammate-0.1.29.98.zip --resolution 1280x720`; repeat with a fresh report directory and `1920x1080`. Not executed locally due disk limits; the final CI execution and pixels above were reviewed.
