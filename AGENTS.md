# GS Media / XCMate — Codex project instructions (pilot .97 workspace)

## Grounding and safety
- Repo: `artattakk-creator/kodi-noodleprivate`. Confirm actual branch and commit. `main` source may remain older than the published Pilot package. The .97 working baseline is `release/xcmate-02997-pilot-issue474`; the pilot ZIP was built from PR #478 plus the .97 version bump.
- Honor the user's reported Android behavior; do not present simulated/native Linux evidence as physical Android proof.
- Keep the Xtream provider EPG available as the baseline; additional XMLTV feeds and pictures are optional. Existing explicit TMDB/TVMaze consent or opt-out must not be silently changed.
- Preserve all portal configuration, guide databases, EPG mappings, backups, local artwork, station logos, favorites, token stores and Skin/Widget definitions. Never log, print or commit credentials, token values or authenticated URLs.
- Use Superpowers systematic-debugging/TDD skills only if present in this Codex runtime. Do not claim they ran if absent.
- Work on isolated branches and draft PRs. No edits to regular, Pilot, NeoDark3 repository indexes, installer, main, tags or releases without a separate, explicit approval. Do not reset or rebuild an Android box.

## Required independent QA agents before approval of picture or mapping work
For changes affecting image retrieval, artwork opt-in/storage, Hero and BINGIE displays, **spawn the custom subagent `artwork_qa`** defined in `.codex/agents/artwork_qa.toml`, independently of the implementer. For changes affecting manual EPG source/channel mapping, large EPG, Mini-EPG, preview, or saving, **spawn `epg_mapping_qa`** from `.codex/agents/epg_mapping_qa.toml`.

When both are affected, run the two read-only reviewers independently on the exact same code/commit after the implementation and have the parent wait for both. A reviewer's report is not a merged pass, a GitHub CI run or an Android user test. If custom agents aren't selectable in the running Codex client, explicitly delegate the same read-only checklists to supported subagents or run a separate reviewer session and state that limitation; do not falsely report automatic interception.

The parent developer must:
1. Identify the regression vs published .90 and reproductions vs .97 (issues #468, #482, #474).
2. Produce red tests before editing code and pass focused/full relevant tests after.
3. Obtain agent reports with exact `file:line` findings, pass/fail/unknown per gate and native Kodi screenshots at 720p/1080p when available.
4. Fix reviewer findings in a subsequent isolated draft PR; rerun both gates after change.
5. Keep `ANDROID_NOT_TESTED` until the user confirms actual RK3528/Kodi 21.3 BINGIE pixels and manual Save persistence/aborting; do not confuse download/URL with visible textures.
6. Do not merge, publish, or treat CI/agent quality gate as human release authorization.

## Key acceptance
- Pictures: visible, source-correct, persistent-enough Hero and details; explicit visible status for queued/fetching/ready/blocked/failed; transparent settings/storage errors; no forced large reserves.
- EPG mapping: `EPG zuweisen` directly lists configured sources, offers current channel prefilled search, click shows a reversible preview before Save, Save explains disabled state and confirms post-write/readback in parent grid/Mini, no clipping or focus traps at 720p or 1080p.
- Provider guide continues to work with optional picture/XMLTV disabled. No accidental play/stop while previewing.
