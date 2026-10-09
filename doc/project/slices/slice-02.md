# Slice 02 — force attribution, core energy and native analytical fixtures

Delivered 2026-10-08 on `codex/trials-slice-02`, under the existing authorization to commit, merge and push each major slice.

## Delivered

Sixteen channels retain per-node force provenance across native generation/reset/consumption. Aggregate consumed vectors, generated increments and midpoint work are captured every tick. Ground/object contact is added in the consuming tick; the carried base comes from the preceding tick.

Core accounting adds movable-node gravity potential, eligible linear beam storage, nonconservative work, initialization momentum/kinetic ports, velocity/mass mutation ports, fixed-node applied forces, generic-drag wind/relative-flow work and bounded beam parameter/removal snapshots. Unknown per-node force L1 prevents opposing omissions cancelling a coverage gap. Required transition overflow stays incomplete while simulation continues. Schema 2 explicitly serializes little-endian 2,080-byte records; the reader retains schema 1 / 240-byte support.

Three pinned dry truck assets run inside the source-built native solver. Independent double-precision kick-drift reference math gates scientific results. React adds scenario selection, force/work tables, storage/residual charts and per-check scoped qualification. Passed applies only to the analytical fixture profile, not vehicle impact or atmospheric coherence.

Explicit private-worker OpenGL selection and native renderer screenshot requests support evidence when Direct3D9 startup or GDI capture fails. WebM and ordinary-image playback preserve original recordings.

## Qualification and retained failures

Initial legacy-precision spring/damper trials failed response/energy limits. The analytical profile explicitly selects precise beam-length normalization and initializes relative coordinates near the origin. It executes native beam/integration code; the Daf profile preserves the approximate inverse-square-root kernel. Manifests record the distinction. A pinned-extension failure was corrected by assigning relative coordinates directly rather than subtracting rounded world coordinates.

Final verification completed 13 separate-process attempts with complete capture and zero required-record loss: seven scoped fixture Passed results, six vehicle NotReady results. Two fresh-process repeats per fixture showed zero difference in compared position/momentum/energy samples on this workstation. C++ ledger checks, .NET contract/archive checks, locked zero-warning .NET build, locked npm production build, process/module provenance, authoring, native pause/resume and desktop/mobile checks passed.

Retained failures include precision/initialization probes, Direct3D9 device creation, rejected black OpenGL/GDI video and repaired mobile overflow. The final video comes from 41 genuine native renderer screenshots, nominally 2 fps. Its 82 decoded 4 Hz samples were nonblank. Chrome visible-pixel and image-progression checks passed. Codex in-app GPU playback remains unverified because its browser automation helper could not initialize.

## Cost and remaining gates

Two 5 s coast runs per mode measured 61.4µs median / 78.8µs p95 with attribution disabled, versus 110.2µs median / 139.0µs p95 enabled (20,002 released steps per mode). These are steady-clock step elapsed times including scheduling/barriers, not process CPU time. Both profiles retain storage scans and aggregate capture and request evidence frames. Ratio 1.795×, about 79.5% additional duration. The proposed ≤10% overhead target is not met; this is not an instrumentation-off/upstream comparison.

Payload is about 4.16MB/s per actor at 2 kHz, excluding projections/framing. The 32,768-record ring is about 65MiB. Each record holds eight transitions. Continuous observer callbacks use preallocated buffers and no new file/network/heap operations; persistence occurs on the writer.

Storage is a linear diagnostic subset. Shock/hydro/rope/inter-actor/nonlinear storage, strength-only transitions, all external mutation gateways, arbitrary mass/cohort flux and full plastic/fracture dissipation are unqualified. Removal storage is bookkeeping, not measured fracture energy. Vehicle validation remains NotReady. Next gates: optimize attribution, true instrumentation-off comparison, barrier/contact/detail windows, broader storage and environment qualification. Driven journeys and flight remain later.

## Evidence

- [HTML report](../reports/trial-slice-02-2026-10-08.html)
- [Machine-readable results](slice-02-results.json)
- [Workbench runbook](../../../apps/trials/README.md)
- Session: `D:\Rigs of Rods\trial-slice-02-2026-10-08-221217`
- Final checks: `report\verification-20261008-230307\checks.json`
- Report/archive: `report\index.html` / `report\slice-02-evidence.zip`
- Media: `media\slice-02-native`, `media\slice-01-recovered`, `media\baseline-recovered`
- Native SHA-256: `B6176E71C8C20C732E895EC628C28DD1AD6F96ED8D38FF8A12B112BD68FD1301`
- Protected baseline SHA unchanged: `2F74316A16AE2D44B7E1D458ECF25E409E1CD0D853DBE0F1065AC91FE7BBC70A`

VS2022/MSVC19.44 x64 Release; fresh native outputs followed by recorded incremental repairs; existing Conan cache reused. .NET10.0.203, Node22.15. Matplotlib3.10.7 was installed only in the new session plotting environment, preserving baseline tools. Build provenance includes precommit base, dirty patch and native source hashes, including new files. Final feature/merge identities are recorded in session `report\publication.json` after publication. Large media/build/capture data remain outside Git.
