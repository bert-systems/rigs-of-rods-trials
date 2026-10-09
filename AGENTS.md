# Agent and contributor guidance

These instructions apply to this source fork and its subdirectories. The project is **rigs-of-rods-trials**, a fork of Rigs of Rods owned by `bert-systems`.

## Start of a session

1. Read [PROJECT.md](PROJECT.md), [project-memory.md](project-memory.md), and [todo.md](todo.md).
2. Read [implementation decisions](doc/project/design/implementation-decisions.md), [implementation specification](doc/project/design/trial-platform-implementation-spec.md), [platform.md](platform.md) and [trial architecture options](doc/project/design/trial-platform-architecture-options.md) for experiment, telemetry, environment, or physics-measurement work. Read [architecture.md](architecture.md) for engine or design work and [the build and recording guide](doc/project/build-and-record.md) before building or running.
3. Check `git status --short`, the current branch, HEAD, origin, and content submodule status. Preserve existing user changes. Historical baseline values are evidence, not assumptions about the current tree.
4. State the intended work briefly. Use the user's current scope; the backlog does not authorize starting unrelated features.

## Branch and publication workflow

Effective 2026-10-09, the user selected `dev` as the ongoing development and integration branch, created from `master` after Slice 04 (`b43b4bab6d760aeb55cbbfa239555f96c358769e`). Work from `dev`; commit and push completed, verified slices to `origin/dev`. If an isolated feature branch is needed, base it on `dev` and integrate it into `dev`.

The user will periodically open and merge pull requests from `dev` into `master`. Do not automatically merge or push new changes into `master`, or create/merge those periodic pull requests, unless the user explicitly requests that action. This replaces the earlier major-slice workflow that automatically merged into `master`; historical delivery records retain their original publication facts.

## Source and evidence boundaries

- Canonical source: `D:\Rigs of Rods\rigs-of-rods-trials`; origin: `https://github.com/bert-systems/rigs-of-rods-trials.git`.
- The installed game in `D:\Rigs of Rods` must not provide the executable or DLLs used as source-build proof. Do not overwrite its files.
- Preserve `D:\Rigs of Rods\source-build-2026-10-08` as historical evidence. Its original wrappers hardcode that directory and overwrite logs and configuration; do not rerun them in place.
- Create a unique new session directory for new builds or recordings. Keep binaries, caches, large logs, screenshots, and videos outside Git.
- Small provenance records, runbooks, and useful session summaries belong in Git. Never store credentials or tokens in documentation, logs intended for sharing, or project memory.

## Implementation and validation

Follow the existing code style and [CONTRIBUTING.md](CONTRIBUTING.md). Inspect the actual implementation before changing behavior; some upstream overview documentation predates current messaging and scripting support.

Build with the verified VS 2022 x64 environment unless the task intentionally validates another toolchain. Capture configuration, dependency resolution, command output, exit codes, source status, and executable hash. Distinguish a fresh game build, a clean game rebuild, and a fresh dependency cache.

For a simulation claim, launch the exact new build executable by absolute path, record its process path and loaded modules, and show observable simulation behavior. A menu screenshot or recorder exit code alone does not establish a working simulation. Collect the game's logs and meaningful telemetry as well as images/video.

Use validation appropriate to the change. For documentation-only changes, check links, facts, and the diff; a new game build is unnecessary. At the baseline, CTest listed zero tests. Do not describe this as a passing automated engine test suite.

Playwright can check the evidence HTML, responsiveness, links, and video playback. Native RoR screenshots and FFmpeg/native-window capture provide the game evidence. Describe which tool produced each artifact accurately.

## Decisions and communication

Proceed with routine reversible work within the user's authorized scope. Ask only when a necessary decision, missing constraint, or consequential action actually requires user input. Do not invent new approval gates from these docs.

Keep updates concise and distinguish observations, workarounds, hypotheses, and verified fixes. Record failures and warnings; do not silently discard an unsuccessful run or claim broader validation than the evidence supports.

The configurable experiment/trial platform has completed research, architecture evaluation and policy Q&A. The implementation specification consolidates the selected React/.NET direction, ground-impact pilot and native instrumentation scope. Confirmed decisions govern policy; proposed defaults/contracts require qualification and must not be described as measured or accepted results. Slice 01 implements the native aggregate observer, recorder, local .NET coordinator and React workbench. Read [its delivery record](doc/project/slices/slice-01.md) and [runbook](apps/trials/README.md) before changing these modules. Scientific validation remains NotReady until model attribution and analytical fixtures are qualified. Keep new work grouped into major slices with real evidence; commit and push completed slices to `dev` under the branch workflow above. Do not automatically implement the unrelated maintenance backlog.

## End of a session

- Update [todo.md](todo.md) with completed work and remaining actionable items.
- Update [project-memory.md](project-memory.md) with durable decisions, important findings, and a dated session entry. Avoid duplicating lengthy logs.
- Link any new session summary and evidence directory. Include commit, dirty-tree status, toolchain, commands, checks, and material limitations.
- Update the architecture or runbook when behavior or procedures change. Preserve dated baseline facts.
- Review `git diff --check` and the final status. For files with existing CRLF endings, use `git -c core.whitespace=trailing-space,space-before-tab,cr-at-eol diff --check` to check whitespace without flagging carriage returns. Report what changed, how it was verified, and what remains.
- A local documentation update does not imply that it was committed or pushed. Make repository publication status explicit.

## Slice 02 continuation

Read [Slice 02](doc/project/slices/slice-02.md) and [results](doc/project/slices/slice-02-results.json) before changing accounting/fixture contracts. Schema2 captures 16 channels and a linear storage subset. Pinned dry analytical fixtures can earn scoped Passed; vehicle scientific validation stays NotReady. Fixture precision explicitly differs from the preserved vehicle kernel. Do not silently loosen acceptance limits or label removed storage as fracture energy. Optimize measured observer cost before claiming the proposed overhead target.

For media, inspect visible pixels and image progression. OpenGL/GDI may be black despite encoder success. Use native renderer PNGs and ordinary-image playback; preserve failures and distinguish Chrome checks from unverified Codex in-app GPU rendering.


## Slice 03 continuation

Read [Slice 03](doc/project/slices/slice-03.md) and [results](doc/project/slices/slice-03-results.json). Observation `off` disables node/channel/energy/aggregate capture but retains native trial controls and a declared common timing/state probe. It is not an unmodified-upstream baseline and cannot earn scientific Passed. Do not display absent force/energy terms as zero.

Keep probe schema 1 / 128 bytes distinct from aggregate schemas 1/2. Probe loss/corruption stays incomplete; preserve later samples. Timing ends before common probe sampling/queueing; full ledger reduction and queue copying are included. Fingerprints sample specified node/beam state at 10 Hz and are diagnostic, not every-tick full-state proof or checkpoints. Preserve the unchanged fixture acceptance profile. The measured total observer overhead remains about 3.06-3.14x, so do not claim the proposed ≤10% target or compare directly with the earlier channels-disabled baseline.

Build wrapper `-Parallel` controls concurrency; this session used 6 after MSVC C1060 at 16. Update precise native source hashes and executable identity after repairs. The planned barrier/detail grouping follows this prerequisite as Slice 04.

## Slice 04 continuation

Read [Slice 04](doc/project/slices/slice-04.md), [results](doc/project/slices/slice-04-results.json) and [detail-format.md](apps/trials/detail-format.md). `barrier-approach-capture-v1` Passed concerns frozen approach conditions and required data only; all vehicle science stays NotReady. Preserve distinct individual-contact/net-force peaks, actual law output/applied increment and consumed/generated epochs. Contact midpoint work is not material dissipation. Dense strength/removal states are not calibrated fracture energy; the matrix did not exercise actual fracture.

The qualified 3/5/10 m/s target matrix uses release 3.8/6.2/12.25 m/s and distance 7.2/12/24 m, 3 s settle + 9 s motion. Keep the unchanged speed/heading/lateral thresholds. The realized 176-node/744-beam detail needs ~782 MiB history, a separate ~3 GiB queue and ~1.55 GB/window. The resource v2 revision follows retained real failures; do not reinstate the failed 768 MiB/256 MiB proposals or hide loss by reducing rates. Required loss continues observation and prevents capture/scientific acceptance. Longer/separated/retriggered/multi-actor profiles need additional qualification.

Aggregate flag16 distinguishes projection truncation covered by mandatory dense beam detail. Without healthy required dense capture, omitted transitions cannot pass quality. Archive inspectors must recheck CRC/identity; downsampled envelopes preserve maxima and mark gaps. Finalizing is archive drain, not completed capture. Native command acknowledgement and paused clock refresh can arrive in different polls; qualify pause using native paused status. Injected partial-write tests are not physical disk exhaustion. Worker abrupt-exit tests do not qualify coordinator orphan ownership. Preserve all originals; portable packaging includes one representative full raw window rather than duplicating every large archive.


## Slice 05 continuation

Read [Slice 05](doc/project/slices/slice-05.md), [results](doc/project/slices/slice-05-results.json) and [transition contract](apps/trials/transition-format.md) before changing beam events/reference profiles. Event kind bit4 is strength metadata, not the record flags' unsupported-state bit4. Strength alone carries zero elastic-storage port. Preserve schema 2/2080 layout and declare producer semantics in manifest schema 5. Historical producers did not independently emit strength-only events. Aggregate projection omissions require the existing mandatory healthy dense-capture gate.

`beam-transition-reference-v1` qualifies frozen dry single-beam tick-1 initialization transitions with a native prime and double reference. It does not qualify later collision fracture, vehicle materials or material energy dispersal. Keep original three fixture limits unchanged; the new 50 micrometre world-coordinate envelope explicitly accounts for float32 COM rounding near 500 m. Preserve the first failed checker result and the correction history. Test CRC-valid semantic corruption, not integrity alone. Use new evidence sessions, preserve recorded originals, and commit/push dev without automatic master promotion.
