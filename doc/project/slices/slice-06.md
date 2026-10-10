# Slice 06 — recorder health, capture cost and slow-disk hardening

Completed 2026-10-09 on `dev`. [Illustrated HTML](../reports/trial-slice-06-2026-10-09.html), [measured results](slice-06-results.json), [recorder contract](../../../apps/trials/recorder-health.md).

Implemented populated-contact prefix copies in the fixed detail buffers, endian-safe slicing-by-eight CRC, cached fixture filenames and audited skips of inactive detail callbacks. Actual native force writes/order, random draws and archive wire formats remain intact. Reserved history/queue capacity, capture rates, required windows and resource preflight floors are unchanged.

Added independently sampled queue/high-water/copy/write/durability/error/timing diagnostics, writer-owned finalization progress, terminal recorder snapshots, optional phase profiling, and actual React live/closed/loss views. Phase profiling is opt-in, immutable and requires the declared common probe; diagnostic timings are excluded from performance-budget comparisons.

## Measured outcomes

- Matched D: coast baseline/prototype, three interleaved fresh-process repeats per mode: full medians 77.6 → 72.7 µs (6.3% lower); off 22.4 → 22.3 µs. The prototype precedes the final cadence repair. Final C: full/off medians 73.5/22.1 µs, 3.326×. The proposed ≤10% aggregate overhead remains unmet; no barrier-off/detail-overhead pass is claimed.
- Detail producer copy bytes 4,921,344,000 → 3,102,745,920 (36.95% lower). Raw window payload remains 1,550,318,264 bytes. ~782 MiB history and ~3 GiB queue reservations remain.
- Isolated CRC median 128.211 → 30.771 ms per 65,536,000 bytes, 4.167× throughput. This is not a whole-worker speedup.
- Live diagnostics exposed the reset-before-sync feedback loop: synchronization longer than the nominal interval caused the next frame to immediately sync. Shared tested schedule starts the next 250 ms interval after sync returns, with forced final synchronization. No hard flush/durability-latency SLA is claimed.
- Individual D: barrier worker wall times: original baseline 52.9 s, instrumented pre-cadence prototype 91.3 s, final 60.2 s. Prototype/final sync calls 70/10. A final sync blocked 16.60 s; queue high-water 13,734/15,709 (87.4%). These single samples do not establish a general end-to-end speedup over the original build. Final C: 24.1 s is a different-volume qualification run.

## Qualification and evidence

Fresh source-native build plus recorded incremental implementation rebuilds: VS2022/MSVC19.44, x64 Release, six jobs, existing Conan cache. Final executable SHA-256 `72EB4485AAC9D7F853EA6C7FF2E57D77192792C1139D136024B396A154872520`; all 475 native/CMake input hashes match. Compilation preceded commit; the exact input inventory identifies the dirty implementation beyond its starting HEAD `2a477eafc74b64c78c8b5f44ad27bdd24e418362`.

Four healthy windows across baseline/prototype/final D:/final C: are bit-for-bit identical: 12,001 frames, ticks 6267–18267, 77,363 contacts; dense payload SHA-256 `db395aa790d4a08d07b49c167adfc4306a131ef733143a11aa79e7ca6d06dabd`. Twenty-two pairwise checks, covering 276,000 paired record comparisons, have zero mismatches. Aggregate comparisons exclude only the declared timer; common-probe comparisons include every-tick sentinel/metadata plus 10 Hz diagnostic fingerprints, not complete engine checkpoints.

Final partial-write injection retains tick 10268 onward through 18267 after missing trigger tick 10267. Execution Completed, capture Incomplete, science NotReady. Independent freefall successor and unchanged spring/damper/tensile-yield fixtures earn their existing scoped Passed. Actual physical disk-full remains untested. No recorded failures or prototype archives were removed.

Focused native CTest 2/2, locked managed build/contracts, production React, final managed reinspection of 18 D: + 13 C: + 1 visual attempts, and CRC-valid semantic transition-corruption rejection pass. Actual Chrome UI checks cover running/finalizing/loss/closed views, profile form constraints, historical absence, mobile overflow and zero page errors.

Thirty-two fresh native processes were preserved in this session, including a deliberately interrupted test harness (the native worker continued to finish normally). The prototype result directory was relabeled `verification-06-prototype-*` without altering its original checks; its embedded evidence path reflects its original name. The coordinator/native workers were not killed during that relabeling.

Dedicated final-build visual attempt `da032291293a400e83925055e4b3d1a6` produced 29 genuine native PNGs and 58 nonblank decoded samples. Ordinary-image progression and visible WebM pixels pass in system Chrome. Codex in-app GPU playback remains unverified. Nominal image/video playback time is separate from physics time.

## Locations and retention

- D: build, baseline/prototype/final cadence archives, report/media/logs: `D:\Rigs of Rods\trial-slice-06-2026-10-09-230333`.
- C: final qualification: `C:\Users\berts\Documents\RoR-trials-evidence\trial-slice-06-2026-10-09-230333`.
- C: dedicated native visual: the sibling `trial-slice-06-2026-10-09-230333-visual` directory.
- Portable review bundle: D: session `report\slice-06-review.zip`; source/logs/metadata, aggregate/probe/fixture raw records and media. Full dense originals remain at the inventoried archive paths; this is not a full dense-archive export.

`start.ps1 -Archive` chooses an explicit durable archive volume while retaining the source-built runtime in the session. D: storage approached the existing preflight reservation threshold; C: supported additional runs without reducing floors or deleting recorded data. Retain both roots manually.

Development/integration remains `dev`; commit/push this verified slice there. Periodic `dev` → `master` pull requests remain user-managed. Next: controlled later impact-induced strength/removal qualification, broader energy closure, dominant solver/attribution optimization and workload qualification. No vehicle material-energy, multi-actor, barrier-off, physical disk-full or coordinator-orphan acceptance is implied.
