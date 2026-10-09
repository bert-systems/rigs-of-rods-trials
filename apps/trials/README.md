# Local trial workbench — Slice 01

React 19.3 and ASP.NET Core/.NET 10 run a serial queue of fresh source-built RoR workers. Each attempt has an immutable configuration, private copied runtime/profile, native binary capture, SQLite catalog and separately reported execution/capture/scientific-validation states.

This first slice supports Daf Semi (`b6b0UID-semi.truck`), Simple Test Terrain (`simple2.terrn2`), settling followed by initialized rolling motion and a propulsion-free coast. It records consumed forces, ground/object-contact force deltas, movable-node momentum, kinetic energy and kinetic-work integration residuals. All completed attempts remain `NotReady` for scientific validation.

The native observer archives one **aggregate** record per physics tick (~2 kHz), publishes summaries at ~200 Hz, and the UI requests state about 10 Hz. The configured node/beam/contact detail windows, barrier trials, force-model attribution, deformation/breakage energy and analytical engine fixtures remain future slices. The ledger identity tests are useful accounting tests; they are not engine calibration.

## Build and start on the verified Windows workstation

Use PowerShell from the fork root. .NET SDK 10.0.203 and Node 22.15 are installed. VS 2022 x64, CMake/Ninja/Conan and the existing dependency cache are reused. The new native outputs are compiled from this fork; no installed game executable or DLL is copied.

```powershell
$trialSession='D:\Rigs of Rods\trial-slice-01-new-session'
.\tools\trials\build.ps1 -Session $trialSession
.\tools\trials\start.ps1 -Session $trialSession
# Workbench: http://127.0.0.1:54321/
```

Supply `-Tools`, `-ConanHome` and `-VsShell` for another workstation. Initialize the pinned content submodule first. Run `build.ps1 -Clean` for a clean native rebuild in the same session. Every invocation writes dated logs and source/build provenance; use a new session for distinct evidence work. This is a source build with cached dependencies, not a fresh dependency-cache qualification.

Stop an existing coordinator before rebuilding its .NET executable. The supplied start script refuses an occupied port. To stop, read `report\coordinator-pid.txt`, verify the process path and stop that process. An interrupted active attempt is preserved and marked incomplete on the next startup. Reconnection does not silently retry it.

## Evidence check

```powershell
& 'D:\Rigs of Rods\source-build-2026-10-08\tools\Scripts\python.exe' tools/trials/verify-workbench.py --session $trialSession
```

The check needs Playwright, installed Chrome, and FFmpeg at the workstation paths in the script. It starts real native workers, records FFmpeg video/native screenshots, checks pause against the native clock, verifies two isolated repeats with changed gravity/density/wind, cancellation, queue continuation, manual retry, archival retention, local mutation restrictions and responsive rendering. Evidence is placed in a unique `report\verification-...` directory. This test consumes time and archive storage; run it deliberately.

## Runtime contract and limits

- Loopback IPv4 service. Mutations require a per-service session token and matching Origin; typed configuration rejects arbitrary assets/path input and nonfinite/out-of-range values.
- Native capability handshake and observed process/module provenance identify the copied source build. Manifests include vehicle/terrain package hashes and units/world axes.
- Gravity is scalar Y-down; density and steady world-space wind affect the pilot's existing generic drag law through air-relative velocity. Temperature records a dry-air state with derived pressure; it does not introduce thermal exchange. Other aerodynamic models are not qualified.
- Native callbacks do not allocate or write files. One actor-owned observer and a bounded SPSC queue hand aggregate records to a writer. The single-pilot-actor boundary is deliberate.
- `steps.rort` uses explicit little-endian 240-byte records in ≤128-record chunks with CRC-32 and DONE markers. Durable flushes are grouped around 250 ms; abrupt interruption can lose the unflushed tail. Verified prefixes are retained and never treated as complete.
- Every-step capture gaps, nonfinite observations or I/O errors are sticky incomplete quality. The worker continues observing. No scientifically passing result is available in this slice.
- Pause/resume acknowledgements record their applied tick. Recorder publication can lag physics; independent native heartbeat time drives the dashboard clock.
- Cancellation retains partial capture. Retries create new IDs and private worker processes. Archive currently marks and retains data; it does not delete files.
- New launches hold below an 11 GiB free-space threshold. A startup lease of 120 s, active wall budget of 300 s and paused lease of 1800 s are engineering safeguards awaiting broader performance qualification.
- The current renderer profile is Direct3D9, windowed 1280×720, verified on this workstation. General renderer configuration and asset-catalog selection come later.

See [Slice 01 evidence and delivery](../../doc/project/slices/slice-01.md) and the [implementation specification](../../doc/project/design/trial-platform-implementation-spec.md).

After verification, run `tools/trials/write-slice-report.py --session $trialSession` to produce the illustrated evidence report and `tools/trials/verify-report.py --session $trialSession --repo <fork-path>` to verify its images, references and actual video decoding.
