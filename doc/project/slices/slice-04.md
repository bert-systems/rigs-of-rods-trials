# Slice 04 — controlled barriers and detailed impact capture

Delivered 2026-10-09 under the user's continuing authorization for large slices, actual image/video evidence and commit/merge/push. This implements the controlled 3/5/10 m/s target repeat matrix and required whole-pilot impact windows. It does not close vehicle material/energy accuracy or fracture dissipation.

## Delivered behavior

`barrier-v1` prepares a source-defined orange 16×6×1 m native concrete box on pinned Simple2. Its transform, material and collision feature are recorded. Propulsion/braking remain off during the controlled settled rolling coast. Inputs separately specify release velocity, target approach velocity and barrier distance. The qualified release/distance combinations are 3.8/7.2, 6.2/12 and 12.25/24 (m/s and m), with 3 s settling plus 9 s motion. Actual approach is observed at the first released frontmost-node crossing of the plane 0.25 m before the face; signed COM velocity is projected onto the frozen approach direction.

The versioned approach limits remain max(0.1 m/s, 2% target), 1 degree heading and 0.25 m lateral displacement. `barrier-approach-capture-v1` Passed qualifies approach conditions and required capture only. Every vehicle run remains scientific NotReady. No acceptance tolerance or confirmed D008 policy was loosened.

The native observer captures each node's pre/post velocity, actual consumed force and all 16 channels, every beam's before/after rest/stiffness/strength/active state plus actual generated endpoint writes, and each terrain/object contact's law output, actual accumulator increment, normal and native feature/material identity. Node channels are sampled after the final attribution correction. No extra contact force is applied. Contact normal/tangent vectors, impulse and midpoint work are derived outside physics callbacks. Individual application and net barrier peaks remain distinct.

`RORDTAIL` schema1 uses CRC/DONE frames and explicit health/footer semantics; [detail-format.md](../../../apps/trials/detail-format.md) defines the padding-free x64 little-endian IEEE layout. A preallocated producer queue feeds a recorder with separate rolling history. First nonzero consumed barrier contact triggers inclusive −4000..+8000 ticks: **12,001 frames**, 2 s pre/4 s post at the native ~2 kHz rate. Callbacks allocate nothing and perform no file/database/network/UI waits.

Dense beam detail removes the aggregate eight-event projection as a required transition bottleneck. Aggregate flag16 identifies projected omissions covered by mandatory dense capture; the count remains visible. Without dense capture, projection overflow still sets required-loss flag1. Both required archives must be complete.

.NET streaming validation retains verified prefixes, enforces cohort/finite/CRC/tick/window/footer health and creates a CRC-rechecked index. React provides target/release/distance authoring, impact gates/peaks/vector impulse/transition counts, an archived tick/node/beam/contact inspector, and visible Finalizing/durability status. All 200 Hz summary envelope maxima are preserved in 20 Hz display points with gap markers. Compact polling sends history for the focused attempt; completed histories are reconstructed on service restart.

## Qualification and evidence

Fifteen fresh private processes, five per target, all Completed / Complete / vehicle NotReady, with scoped approach/capture Passed and zero required detail loss. Each contains 176 nodes and 744 beams per frame. Actual approach speeds are **3.063182, 5.066242 and 9.996183 m/s**. Peak individual applications are **0.711769, 1.171818 and 2.324126 MN**; peak net barrier magnitudes are **1.361203, 2.219685 and 5.095063 MN**. World impulse X is approximately 49.825, 81.863 and 160.527 kN·s. Five repeats per target have zero observed spread in approach/impact tick/peaks/impulse on this pinned build.

The 10 m/s matrix retains 179 parameter transitions per run; 3/5 m/s retain zero. No strength transitions or beam removals occur in this matrix. The dense records support those states, but actual fracture-path qualification remains open. Independent Python streaming CRC/DONE decoding reproduced all fifteen force peaks and impulses, and disclosed float32 reconstruction and momentum-kick residuals. Those diagnostics are not material-accuracy tolerances.

Operational checks exercise missing prehistory, one queue-full admission and a partial storage write/rollback, with later capture and independent successors; native pause/resume, partial cancellation, verified-owned abrupt worker termination, committed-prefix recovery and separate manual retry; and unchanged dry free-fall/spring/damper Passed profiles. Exact outcomes and IDs are in [results](slice-04-results.json). The storage injection does not physically fill the drive. The first pause harness read an acknowledged state before the refreshed native paused clock; its retained attempt was resumed and completed, and the corrected check waits for native paused status.

Final native visual attempt `42bb2468b83746469e1e5a4f8e937a5a` matches the 10 m/s target and retains 56 genuine OpenGL screenshots showing approach/contact/rebound. FFmpeg nominal 2 fps encoding yields 112 decoded 4 Hz image samples, all nonblank. Chrome verified visible WebM pixels at 1/3/5 s and ordinary-image progression. Native PNGs were visually inspected. Media time is not the physics clock; Codex GPU video playback remains unverified. Ordinary-image playback is primary.

Standalone CTest (one ledger test), locked Release .NET build (zero warnings/errors), archive contract/corruption/prefix tests, peak/gap projection checks, React production build and real dashboard/inspector desktop/mobile checks pass. The chart envelope was checked against the raw 5.095063 MN peak. Invalid node IDs/missing ticks/impossible capture definitions are rejected; browser page errors and page overflow are zero.

## Resource findings and retained failures

The realized actor exceeds the initial 768 MiB history proposal. Its maximum stride is 205,056 bytes and 4,001 history slots need **820,429,056 bytes (~782 MiB)**. A 256 MiB queue suffered real loss on this archive volume. Resource revision `daf-detail-resources-v2` reserves up to 1 GiB history and a separate **~3 GiB queue**, checks 6 GiB available RAM and 3 GiB raw reservation plus a 10 GiB disk floor, and probes storage writability. Each six-second dense window is approximately **1.55 GB**. These are engineering resource changes, not reductions in rate or altered physical tolerance.

The near-full ST2000DM008 spinning-disk archive has substantial drainage latency; Finalizing separates physics completion from archive durability. Worker wall and released per-step elapsed ranges are reported per target in the measured results/HTML. No barrier off-mode equivalence or proposed overhead-budget achievement is claimed. The earlier coast full/off 3.06–3.14x comparison is a different workload. The current detail buffer/profile qualifies these 9+3 s single-impact runs; long/separated/retriggered windows, multiple actors and alternate renderers remain unqualified.

All failed prototypes remain retained: initial history-budget rejection, two real queue-loss captures and the under-speed 10 m/s setup. Prototype captures preceding the final node-channel snapshot correction are excluded from final qualification. The UI's initial summary decimation missed a narrow peak and was replaced by tested peak-preserving coalescing. The first UI harness also had an invalid locator regex; corrected tooling passed.

Contact work is its midpoint integration contribution, not dissipated impact energy in concrete. Nonlinear/shock/hydro/storage/plastic/fracture closure, broader contact/mutation/cohort transitions and calibration remain open. Raw detail covers terrain/object contact, not qualified cab/inter-actor contact. No dynamics faster than the 0.5 ms step are resolved. Future driven journeys, environment expansion and flight remain separate work.

## Reproduction and publication

- [Illustrated HTML evidence](../reports/trial-slice-04-2026-10-09.html)
- [Measured results](slice-04-results.json) and [runbook](../../../apps/trials/README.md)
- Session: `D:\Rigs of Rods\trial-slice-04-2026-10-09-011428`
- Report: `report/index.html`; image player: `media/slice-04-native/playback.html`
- Native SHA-256: `560F21EB692A33125292C0CA1C418674698DCF2406F05F4DF27EEA9231086CC9`
- Exact source inventory: `report/source-20261009-015649-3790.json`, 474 native files
- Final identity: `report/final-build-identity.json`
- Portable package: `report/slice-04-evidence.zip`; check: `report/bundle-check.json`
- Publication: `report/publication.json` records feature/merge/remote identity and clean-tree/source checks after push
- Branch: `codex/trials-slice-04`; base: `5bfcb126270544e79f5410cc726648e884967ebd`
- Content: `34fefdd126784bf87b068fc283f812525d159dd7`
- VS2022/MSVC19.44 x64 Release; CMake3.31.10, Conan2.33, Ninja1.13.2, .NET10.0.203, Node22.15

Fresh session native outputs reuse the verified dependency cache; subsequent repairs use incremental builds at six jobs. The installed root game supplies no executable/DLL proof. The protected original source-build baseline remains untouched. Large raw captures/media/logs stay outside Git. The portable bundle includes metadata/logs/media for all attempts, one representative complete raw impact window and analytical fixture records; other raw windows remain retained with a SHA-256 inventory.
