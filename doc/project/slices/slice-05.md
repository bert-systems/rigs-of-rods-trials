# Slice 05 — native beam transitions and reference qualification

Developed on `dev` under the user's new branch workflow. Final verified changes are committed/pushed to `origin/dev`; periodic promotion into `master` remains user-managed. Build base `0a7d6bcff350421c5a2ef1231244ef6a85582976`. Final commit/publication identity is recorded in the session's `report/publication.json` after publication.

[Illustrated HTML](../reports/trial-slice-05-2026-10-09.html), [results](slice-05-results.json), [wire/profile contract](../../../apps/trials/transition-format.md).

Session: `D:\Rigs of Rods\trial-slice-05-2026-10-09-033000`. The session name is an identifier; build metadata records the actual start at 08:35 EDT. Fresh MSVC 19.44/VS 2022 x64/CMake/Ninja Release outputs, existing Conan cache, `build.ps1 -Parallel 6`. Native executable SHA-256 `A23CEB4EEFC682D40A412CD569D771341CEE5925A0DE5D41CC94BE15F8488544`. All 474 recorded native source hashes match the checkout. Private worker image, executable hash and modules were verified for all new qualification runs. The installed root binaries and protected baseline are separate.

## Delivered

- Strength-only transitions now emit explicit kind bit4 in the unchanged 2,080-byte aggregate schema 2. They carry zero elastic-storage port; combined parameter/removal events preserve existing no-double-removal bookkeeping.
- Four pinned native dry fixtures execute tensile yield/strength loss, compressive yield, beam break/removal, and the cab-node protection branch. These call the real native beam kernel with precise fixture length arithmetic. The synthetic protected node has no cab collision surface.
- An independent double-precision one-dimensional reference includes initialization priming, kick-drift, native yield/correction/strength/break rules and force epochs. It checks actual state, force, storage, signed ports, transition count/identity, duration and quality. This is scoped native-law implementation agreement, not material calibration.
- .NET exposes bounded CRC/DONE/footer-rechecked transition pages with invalid bounds, missing attempts and incomplete archives rejected. React supplies four new authoring choices, visible transition counts, before/after rest/strength, signed ports and omission status.
- Reproduction scripts, scientific plots from raw records, actual workbench screenshots and an unmodified native renderer PNG establish feature evidence. Ordinary PNG evidence has no video decoder dependency; no new Codex GPU-playback claim is made.

## Evidence

Eight final-profile source processes (0.2 s and 1 s for each new fixture) completed with zero required loss and scoped Passed. Each pair has an exact 400-tick state prefix, excluding observer timing/initialization-state ports. Three original analytical fixtures reran and Passed with unchanged limits. Native CTest 1/1, locked .NET build zero warnings/errors, managed contracts and production React build passed.

At tick 1, tensile rest grows 1→1.035 m and strength drops 2000→1650.000488 N, with about −11.374686 J rest-storage port. Compression rest contracts 1→0.965 m with strength unchanged and about −11.374763 J port. Removal subtracts about 12.499976 J supported storage. Protection raises strength 200→400 N with zero rest/removal ports. See JSON for exact archived values.

CRC-valid adversarial copies with wrong transition kind, port, event storage or force epoch remain complete byte captures but fail the scientific gate. Final reader reinspection covers all 12 retained captures. Playwright checks actual ledger rows/defaults, bounded API behavior, missing attempts, desktop/mobile layout and page errors; all pass. Portable packaging retains all small raw fixture captures and verifies extracted file hashes. Full original workers/records remain in the session.

Initial attempt `57da6d8386d141debd690db25f527d74` was Complete but Failed under the first checker candidate: wrong force offsets and a 10 µm position limit below float32 world-coordinate rounding. The force offsets were corrected; new profile position tolerance is explicitly 50 µm. Its original result remains Failed and its unchanged capture passes final offline reference reinspection. No historical fixture limits were relaxed.

0.65 GiB of this session's transient `.obj`/`.pch` outputs was pruned after successful native build, with verified paths restricted to its build/source tree. Executable/runtime, logs, exact source records, prior sessions and recorded originals remain. Future rebuilds recreate those objects. This is not data retention cleanup.

## Limits and next gates

All new transitions are controlled initialization-prime transitions at tick 1. Later collision-induced yielding/removal, full vehicle constitutive closure, calibrated fracture dissipation, nonlinear/shock/hydro/rope storage, arbitrary state mutation and extended impact profiles remain open. Aggregate snapshots observe net tick-boundary changes, not every intermediate mutation. Page scans suit local archived studies; high-concurrency indexing is not implemented. The large barrier matrix was not repeated in this slice. Vehicle science stays NotReady and total observer overhead remains unmet.

Portable evidence ZIP: 14,346,176 bytes; SHA-256 `6F2982AF4A93A02AAA15382BA57E3D497B32A7A1A20F3BB7FCEDCD89E89778FA`. All 785 extracted files match; 192 original archive files total 58,114,475 bytes. Original and extracted report checks verify 11 nonblank images, local links, flow SVG, desktop/mobile layout and zero page errors.

Final fixture text cleanup removes only duplicated EOF blank lines. Native C++ source hashes are unchanged; archived fixture ZIPs and frozen package files preserve exact recorded asset bytes. The session records original/final asset hashes in `report/fixture-text-normalization.json`.
