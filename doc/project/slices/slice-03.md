# Slice 03 — ledger-off baseline, observer cost and native equivalence

Delivered 2026-10-09 under the user's authorization to commit, merge and push each major slice. This prerequisite follows Slice 02; controlled barrier and detailed impact capture are the next grouping (Slice 04). The confirmed ground-impact goal is unchanged.

## Delivered behavior

Immutable trial inputs add `observation=full|off` and `performanceProbe`. React offers full force/core energy accounting, channels-disabled base accounting and ledger-off control/probe trials. Off bypasses ledger buffer preparation, force attribution, energy scans and aggregate recording; trial environment/initialization/control still runs. Off requires the declared common probe, has no `steps.rort`/force table, and cannot earn scientific Passed. Capture Complete concerns its requested probe data.

The shared native timing/state probe records every step using a preallocated 65,536-entry (8 MiB) SPSC queue and a separate writer. `RORPROBE` schema 1 serializes 128-byte little-endian records, CRC/DONE blocks and an explicit close footer. Records contain native tick/phase/cohort, step elapsed time, node 0 world position/velocity, initialization and origin metadata. Every 200 ticks, a diagnostic FNV-1a fingerprint samples all node position/velocity/force/mass/fixed flags and beam L/k/d/strength/disabled/broken state. Fingerprints are neither cryptographic nor exhaustive engine checkpoints. The 10 Hz sampled equality does not prove full-node equality at every intermediate tick.

Timing begins at pilot BeginStep and ends after native phases/job barriers and enabled ledger reduction/aggregate queue copy. Common probe sampling/queueing follows the timer. Results are steady-clock wall elapsed durations, not process CPU time; writer/scheduler contention can affect them. Off uses the same trial-aware executable and probe, not an unmodified upstream binary.

Observer optimization uses sparse touched-channel reduction/reset, a phase snapshot advanced by Delta, audited inactive-phase/empty-manager observation skips, unused beam-geometry avoidance and table-driven writer CRC. Native force routines and random-draw order are preserved. Precise fixture normalization/priming now follows the scenario independently of ledger state. Existing aggregate schemas and fixture acceptance limits remain unchanged.

.NET ProbeReader enforces CRC/finite/cohort/cadence/count/footer checks; required gaps remain incomplete while later samples can be captured. A compact per-attempt status endpoint omits historic arrays from supervision reads.

## Verified native outcomes

Final qualification set, repeated after the readiness ownership fix: twenty-four fresh-process attempts: **23 Completed, one preserved Cancelled**, all declared captures Complete and zero required-record loss. Three pinned dry fixtures Passed; vehicle/base/off/cancel scientific outcomes remain NotReady.

Fifteen declared coast full/off, repeated-process, base/full, dry-fixture and steady-wind comparisons: 189,000 tick pairs with exactly equal node-0 position/velocity, and 945 compared node/beam fingerprints with zero mismatches. These totals reuse runs across comparisons; they are not counts of independent experiments. Three full-ledger fixture archives match floating-point aggregate accounting terms in 21,000 retained Slice 02 records exactly.

| Pilot release | Off median / p95 us | Full median / p95 us | Full/off |
| --- | --- | --- | --- |
| 5 m/s | 22.1 / 33.1 | 67.6 / 89.4 | 3.059x, +205.9% |
| 15 m/s | 21.4 / 32.2 | 67.1 / 88.9 | 3.136x, +213.6% |

Three interleaved fresh-process repeats/profile/speed; 2 s settle, 5 s released motion; 30,003 released records per speed/profile. Same source build, assets, environment and OpenGL configuration. React disconnected during coast cost runs; compact status polling remains. Two scheduled native screenshots are common to benchmark profiles; continuous native image requests were enabled only in the separate visual phase.

**The proposed ≤10% total observer overhead gate is unmet.** Slice 02's 79.5% extra attribution cost used a channels-disabled observer that still scanned energy and recorded aggregates. It is a different baseline. Historical full step times were higher, but changed capture/polling conditions prevent claiming a controlled percentage speedup.

C++ checks passed sparse cancellation/reset, dense independent channel/work reconstruction, known CRC and independent bitwise/table CRC agreement. .NET contract/archive checks passed valid profiles, corrupt/nonfinite/lost/truncated probes, prefix recovery and preventing off-mode science Passed. Release .NET locked build had zero warnings; npm locked production build passed. Actual browser authoring, native off pause/resume (clock stable), cancellation retention, process/module/hash provenance, desktop/mobile layout and zero browser page errors passed.

## Visual evidence and retained failures

Native full-ledger evidence contains 56 genuine OpenGL screenshots; startup/loading frames are retained before the coast. FFmpeg encodes a nominal 2 fps sequence, then WebM and 112 decoded 4 Hz image-player samples. All decoded samples are nonblank. Image progression and Chrome visible video pixels at 1/3/5 s passed. This is native renderer evidence, not a telemetry animation or GDI capture. Media time is not the physics clock. Codex in-app GPU playback remains unverified; ordinary images are the primary playback path.

Retained build failures: MSVC C1060 at 16 parallel jobs, initially uncaught ProbeReader InvalidDataException, and a mixed-encoding JSX file rejected by the production builder. Final review also repaired readiness ownership so a second matching pilot marks scope invalid. The initial 24 single-pilot runs and their portable snapshot remain retained; final native qualification was repeated. These were corrected; source compilation completed at 6 jobs, and all final checks passed. Build concurrency is configurable with `-Parallel` (default 8). Fresh native outputs reused the existing Conan dependency cache. The protected original baseline executable/content remain unchanged.

## Evidence and reproduction

- [Illustrated HTML report](../reports/trial-slice-03-2026-10-09.html)
- [Machine-readable results](slice-03-results.json)
- [Profile/build runbook](../../../apps/trials/README.md)
- Session: `D:\Rigs of Rods\trial-slice-03-2026-10-08-235749`
- Benchmark: `report/verification-03-benchmark-20261009-003831/checks.json`
- Visual/control: `report/verification-03-visual-20261009-004713/checks.json`
- Report/package: `report/index.html` / `report/slice-03-evidence.zip`
- Media: `media/slice-03-final-native/playback.html`
- Native SHA-256: `713CFD3905237808D40CA35F432BAF89638AFE943370494A09526FAC69D2EDCC`
- Source inventory: `report/source-20261009-003714-1462.json`; all 471 native source entries match.
- Publication and package identities: `report/publication.json` / `report/bundle-check.json`.
- Feature branch: `codex/trials-slice-03`; base `34fd81c482517c3b8c0fb8b203891832ffbddf0c`.
- VS2022/MSVC19.44 x64 Release; CMake3.31.10, Conan2.33, Ninja1.13.2, .NET10.0.203, Node22.15.

Raw captures, build/log outputs, images and videos stay outside Git. Versioned scripts retain new verification directories, and the bundle contains raw attempt records/provenance, report media, hashes and build/check transcripts without copying the installed runtime. Its archive download link refers to the external ZIP container, which is not recursively embedded into itself.

## Remaining gates

Observer overhead target, larger/multi-actor scaling and detailed impact cost remain open. Next implement controlled barrier geometry, verified approach/contact identity, bounded required pre/post node/contact/beam windows and native required-loss qualification. Broader constitutive storage, strength-only transitions, mutation gateways, plastic/fracture dissipation, atmospheric coherence, driven journeys and flight remain pending. Vehicle scientific validation remains NotReady. No tolerance or confirmed policy was weakened.
