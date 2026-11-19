# Final independent artwork QA

**ARTWORK_QA_PASS within the reviewed host and native Linux Kodi 720p/1080p scope. ANDROID_NOT_TESTED. No merge, publication or release authorization.**

## Exact source

Product: `38dbe103416c0040be0285be55f657c0dbe8dbd7`. Current observer HEAD: `835bea9901602284e38ac37ecb68bb51d5fe9e1f`.

Independently verified identical product tree `1a4f5db64e90e9ad62f66c1ea2688346968eb997` and test tree `33ecdb311b1e6833d03aedbcbeadadee75fb2620` between those commits. Exact ZIP SHA256: `16c81e587cfe1739ae463ec69ba6d142ab75146e47c8273ae6a779ec750a1042`.

Published comparisons: .90 `9bbf75040378dcaead9128880a909fe7978143a4`; .97 `f0f6649edf075338bb6a806eff231eb718948368`.

This was the supported read-only equivalent of the project-local artwork_qa agent. No author-checkout source/test edits, GitHub mutations, real supplier keys or requests, installs, profile changes or cleanup.

## Findings resolved

- The silent policy request/drain rejection now publishes distinct disabled, deferred and invalid-policy states.
- Invalid settings remain fail-closed; their classified reason survives the actual worker and reaches a readable GUI explanation.
- The Hero bank publishes working and failure status through its existing Description binding.
- Terminal results have fixed, readable texts and a safe generic fallback.
- `programme_diagnosis70.py:9–12` restricts the new detail interception to policy/settings errors, preserving legacy detailed supplier explanations.
- Reserve protection and source-qualified event/mapping guards remain intact.

No open confirmed artwork defect remains in this reviewed scope. The earlier c5 host review missed legacy detail regressions found by the subsequent full suite; the final review explicitly includes those old explanation tests.

## Independently repeated host evidence

**66 PASS in 9.31 seconds**, using the exact source snapshot: `test_xcmate_artwork482.py`, `test_xcmate_art_status_02970.py`, `test_xcmate_pipeline_02968.py`.

Own reproductions verify:

- Actual SQLite event → actual own-TMDB matcher with strictly synthetic search/movie and movie/6801 responses → actual bounded safe transport and full PNG decode → committed local image → completed/result → ProgrammeWindow46.pump model control 110. Result: READY, tmdb_movie, decoded77, LOCAL_IMAGE_READY, eligible, same bound image.
- Corrupt settings through product settings accessors and the actual URL worker: SETTINGS_XML_INVALID, readable explanation, zero external calls.
- 64 MiB free with a 1 GiB archive reserve: RESERVE_BLOCKED receipt, but correct dynamic local image and LOCAL_IMAGE_READY still work.
- Ten working/terminal Hero states produce readable status text while preserving the programme description.

Reproduction scripts and exact snapshots remain in `/tmp/artwork-qa-initial-20261117/`.

## Independently inspected native proof

Run `44096702746`: artwork jobs `134085602538` (1280×720) and `134085602651` (1920×1080). Read-only GitHub job-step and log retrieval independently confirms both exact-ZIP native steps succeeded.

Logs confirm:

- Source-bound Hero and image receipts.
- Detail texture retention for 306.03 / 306.11 seconds, including checkpoints at 2, 46, 121 and 305 seconds after a negative status at 45 seconds.
- Four injected producer-state projections: REQUESTED, RUNNING, SETTINGS_XML_INVALID, IMAGE_EPG_DISABLED.
- Thirteen saved foreign-widget definitions preserved.
- Two actual Application.Quit / supervised offline Kodi restarts with changed PIDs and decoded KODI_TEXTURE_CACHE recovery.

All fourteen original PNGs were independently viewed. Their local SHA256 values match the PNG87 records fetched directly from the job logs. Directories:

- `/tmp/issue482-native-38-art720/`
- `/tmp/issue482-native-38-art1080/`

Both resolutions show the correct large blue programme image, a distinct small station logo, visible “Sendungsbild gefunden.”, and the same programme motif in native details after 305 seconds. The independent foreign-widget motif is magenta.

Actual screenshot pixels within ±8 per channel of synthetic TMDB `(20,80,130)`:

| Resolution | Hero pixels | Detail pixels | Foreign pixels near TMDB blue |
|---|---:|---:|---:|
| 720p | 194,110 | 151,216 | 0 |
| 1080p | 437,100 | 340,236 | 0 |

All four status messages are readable. The complete settings explanation wraps onto two lines. RUNNING screenshots catch transition frames with some other Hero metadata hidden; they prove visible status, not a completely settled whole-screen state.

## Gate results

| Gate | Verdict and scope |
|---|---|
| A1 — job | PASS: honest blocked/request states; host producer path and native projection |
| A2 — sources | PASS within synthetic consent/settings scope; no real account validation |
| A3 — pixels | PASS: independently inspected real native Hero/detail pixels at both resolutions |
| A4 — storage | PASS for host and injected native pressure; no physical full-volume or Android-storage proof |
| A5 — status | PASS for reviewed native working/ready/settings/policy projection and host terminal outcomes |

Stage trace: source-identified SQLite facts, explicit-consent/settings classification, request/drain, synthetic own-TMDB matching, safe URL, bytes/full decode, local/RAM pressure fallback, consumer binding and native Hero/detail pixels all have positive evidence. Real provider/CDN availability and physical Android stages remain UNKNOWN.

## Limits and release classification

The native capacity injection affects XCMate Python only: 27 MiB metadata availability while Kodi C++ textures use real free storage. It is not physical ENOSPC evidence.

Status cases inject producer state after the synthetic data lane ends. They prove native projection, not every external failure's complete producer path. Late 720p screenshots show VOD/series error text and placeholders; 1080p shows synthetic cards. Neither proves continuous production VOD/series availability.

Full cumulative CI remains red. The parent reports pytest 4206 PASS / 6 FAIL and unittest 4201 total / 4 FAIL / 2 ERROR for six inherited .96 version/package contracts. GitHub job metadata independently confirms both full host jobs failed. This scoped artwork PASS does not erase those failures. The observer-only follow-up run `44099402205` was still active when this review finished.

Physical RK3528 / Kodi 21.3 / BINGIE acceptance remains **ANDROID_NOT_TESTED**: real Hero/details, token/consent persistence, real XMLTV/TVMaze fallbacks, physical storage/SMB, provider-EPG and playback independence. There is no general Android, merge or release PASS.
