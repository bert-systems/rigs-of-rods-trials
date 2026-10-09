# Slice 01 — local workbench and native aggregate measurement foundation

Implemented 2026-10-08 in `codex/trials-slice-01`. The user authorized large slices, real image/video evidence, and committing, merging and pushing each major slice.

## Delivered scope

React/.NET local browser workbench; immutable bounded experiment definitions and repeated attempts; serial private source-built workers/profiles; SQLite catalog and retained archives; process/executable/content identity; actual force/contact, mass/COM/momentum and kinetic-work integration observations; constant gravity/density/world-space wind in the pilot generic drag path; native clock and tick-acknowledged pause/resume; cancellation, independent queue continuation, manual retries and archival marking.

The supported study is pinned Daf Semi + Simple Test Terrain, settled then initialized with coherent body/wheel rolling velocity, followed by a propulsion-free coast. Every physics tick writes an **aggregate** observation (~2 kHz); reduced summaries are ~200 Hz and UI updates ~10 Hz. Detailed node/beam/contact windows are unfinished.

Execution, capture and validation are separate. All results remain scientific validation **NotReady**. Whole-model force attribution, conservative/dissipative energy closure, barrier impact qualification and real engine analytical fixtures are future work. The independent ledger identity fixture verifies accounting arithmetic; it does not qualify the full vehicle model.

## Evidence and reproduction

- [Illustrated HTML evidence report](../reports/trial-slice-01-2026-10-08.html).
- [Machine-readable slice results](slice-01-results.json).
- [Workbench build/run and capability runbook](../../../apps/trials/README.md).
- [Reusable build script](../../../tools/trials/build.ps1), [start script](../../../tools/trials/start.ps1), [real-worker verification](../../../tools/trials/verify-workbench.py) and [report generator](../../../tools/trials/write-slice-report.py).
- Full local evidence: `D:\Rigs of Rods\trial-slice-01-2026-10-08-1938`; main report `report\index.html`. Large native binaries, videos, screenshots, runtime profiles and logs are outside Git.
- Actual Git publication identifiers are saved after successful merge/push in `report\publication.json`. Git history identifies the source changes; build provenance explicitly records the pre-publication dirty implementation tree.

The fresh native build reused the existing Conan dependency cache, then later changes were incrementally rebuilt. It did not use installed game binaries or claim a fresh dependency-cache rebuild. Original baseline executable SHA-256 remains `2F74316A16AE2D44B7E1D458ECF25E409E1CD0D853DBE0F1065AC91FE7BBC70A`.

## Checks and observations

- Standalone C++ CTest passes the independent impulse/kinetic-work identities, weighted COM, detectable state mutation, invalid/nonfinite observations and standard CRC vector.
- .NET checks pass configuration/capability bounds, SQLite quality persistence, CRC corruption detection and truncated-footer verified-prefix recovery.
- Release .NET build has zero warnings/errors; Vite production build succeeds. The existing native CMake policy deprecation warning remains recorded.
- Playwright checks a live real-worker run, stable form input during polling, responsive layout and local mutation restrictions. FFmpeg records the native window; native screenshot requests capture settling and nonzero-speed coasting.
- Native pause/resume acknowledges the same tick; the physical clock stays fixed during pause.
- Two fresh repeats adopt changed gravity, density and wind, retain distinct process/profile identities and share an immutable revision.
- Cancellation preserves a partial archive, the next independent attempt proceeds, manual retry creates a fresh attempt and archive marking retains files.
- Coordinator restart recovers 14 terminal attempts with incomplete and archived quality preserved; this is terminal catalog recovery, not a tested hard-crash physical checkpoint.
- Final record counts, hashes, residuals, applied tick, outcome matrix and displacement are recorded in the JSON/HTML above.

## Corrections preserved in the evidence

The first native build needed the custom ActorPtr `GetRef()` accessor. Initial ASP.NET startup needed builder-time web-root configuration. Early tooling needed load rather than network-idle waiting for a continuously polling application, robust nullable summaries and navigation selectors. A restore-only switch was corrected to MSBuild `RestoreLockedMode`.

An early recorder run lost 3,251 required records; it remains Completed / Incomplete / NotReady. A larger bounded queue and grouped durable flushes eliminated loss in the final checked runs. This observation does not replace broad performance or disk-failure stress qualification. The early pause check read a lagging recorder projection; native event ticks confirmed the pause and the new independent heartbeat clock fixes the display/check semantics.

## Next slice

Explicit generated/consumed force channels, initialization/mass/state ports, closed core energy accounting and native free-fall/spring-damper fixtures precede scientific passes. Then implement the controlled barrier, verified impact conditions, deformation/breakage outcomes and required detailed pre/post event windows. Preserve the selected policy decisions and distinguish each slice's measured scope from the remaining 14-epic roadmap.
