# rigs-of-rods-trials project

This is Bert's development fork of **Rigs of Rods (RoR)**, the C++ soft-body vehicle simulation platform. Start here before a design, development, build, or recording session. Latest delivery: [Slice 06 recorder/performance hardening](doc/project/slices/slice-06.md) and [HTML evidence](doc/project/reports/trial-slice-06-2026-10-09.html). Observer overhead and vehicle scientific closure remain open.

The project foundation was established on **2026-10-08**. A fresh Windows source build, clean rebuild, incremental build, and recorded driving session have been verified. Platform research, architecture evaluation and the policy Q&A establish the trial-platform implementation baseline. Implementation includes native recording, a .NET coordinator, React workbench, 16-channel accounting, analytical fixtures, performance/equivalence probes, controlled barrier/detail capture and scoped beam-transition reference qualification. Vehicle scientific closure, calibrated fracture dissipation and the observer-overhead target remain open. See [Slice 05 delivery](doc/project/slices/slice-05.md) and the [workbench runbook](apps/trials/README.md).

## Repository and workspace

| Item | Identity |
| --- | --- |
| Development repository | [bert-systems/rigs-of-rods-trials](https://github.com/bert-systems/rigs-of-rods-trials) |
| Local source checkout | `D:\Rigs of Rods\rigs-of-rods-trials` |
| Upstream project | [RigsOfRods/rigs-of-rods](https://github.com/RigsOfRods/rigs-of-rods) |
| Baseline branch | `master` |
| Current development/integration branch | `dev`; periodic user-managed pull requests into `master` |
| Verified source baseline | `e85535569102b6251849af574026984e3213b3f4` |
| Starter content submodule | [RigsOfRods/content](https://github.com/RigsOfRods/content), commit `34fefdd126784bf87b068fc283f812525d159dd7` |
| Workspace parent | `D:\Rigs of Rods` |
| Preserved build and evidence | `D:\Rigs of Rods\source-build-2026-10-08` |

The fork and upstream master matched at the October 8 baseline check. Recheck their relationship when planning a sync; this is a dated observation, not a permanent relationship.

The parent folder also contains an installed game. The development and proof executable must come from this fork's source build. Preserve the installed game separately.

## Read these documents

| Document | Purpose |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Instructions for agents and contributors working in this fork |
| [platform.md](platform.md) | Platform landscape, measurements, experiment use-case coverage, and research limits |
| [Platform evaluation HTML](doc/project/reports/platform-evaluation-2026-10-08.html) | Comprehensive illustrated report with capability filters and an explanatory calculator |
| [Implementation decisions](doc/project/design/implementation-decisions.md) | Completed policy Q&A and confirmed requirements |
| [Implementation specification](doc/project/design/trial-platform-implementation-spec.md) | Selected design, contracts, proposed defaults, 14 epics and delivery/qualification gates |
| [Implementation review HTML](doc/project/reports/trial-implementation-spec-2026-10-08.html) | Illustrated review baseline with a policy-state explorer |
| [Trial architecture options](doc/project/design/trial-platform-architecture-options.md) | Native accounting pipeline, environment, .NET/WPF vs React workbench, and 14 epics |
| [Architecture options HTML](doc/project/reports/trial-architecture-options-2026-10-08.html) | Diagrams, option comparison, delivery strategy and capture sizing |
| [architecture.md](architecture.md) | Source map, simulation flow, threading, content, and extension points |
| [Build and recording guide](doc/project/build-and-record.md) | Configure, build, rebuild, launch, record, and verify evidence |
| [todo.md](todo.md) | Completed foundation and unassigned follow-up work |
| [project-memory.md](project-memory.md) | Durable facts, user preferences, decisions, issues, and session history |
| [Baseline records](doc/project/baselines/2026-10-08/README.md) | Versioned provenance, verification, dependency lock, and historical proof script |

The upstream [README](README.md), [BUILDING](BUILDING.md), [CONTRIBUTING](CONTRIBUTING.md), and [developer portal](https://developer.rigsofrods.org/) remain useful context. For this machine, use the locally verified build guide above and check the current source when documentation differs.

## Verified starting point

Release x64 was built with Visual Studio 2022/MSVC 19.44, CMake 3.31.10, Conan 2.33.0, and Ninja 1.13.2. All game code was built locally. Conan compiled 12 missing dependency packages and fetched other dependency binaries.

The source-built game loaded Simple Test Terrain and the Daf Semi truck. A 36-second scripted driving session produced three native screenshots, a 35.3-second native-window video, and movement telemetry. Playwright verified the HTML evidence report and its video playback.

Open the local report at `D:\Rigs of Rods\source-build-2026-10-08\report\index.html`. The portable evidence archive is `D:\Rigs of Rods\source-build-2026-10-08\rigs-of-rods-source-build-evidence.zip`. These large artifacts live outside Git; the small baseline records linked above live in this repository.

This is a successful ground-vehicle smoke test. Runtime asset warnings remain, and broader simulation behavior has not yet been validated.

## Working convention

Keep engine and project documentation changes in the fork. Give each evidence session a new directory outside the source checkout, preserve previous evidence, and record source identity and executable identity together. Close each session by updating the TODO list and project memory with the actual outcome and evidence location.

From 2026-10-09, work from `dev` and commit/push completed slices to `origin/dev`. It starts from the Slice 04 merge on `master`, `b43b4bab6d760aeb55cbbfa239555f96c358769e`. Any temporary feature branches should start from and integrate into `dev`. The user will periodically manage pull requests into `master`; automatic major-slice merges/pushes to `master` are no longer the workflow. See [AGENTS.md](AGENTS.md) for the standing branch instructions.

## Latest delivery

[Slice 05](doc/project/slices/slice-05.md) adds actual native yielding, strength/removal qualification and an archived transition ledger. [HTML evidence report](doc/project/reports/trial-slice-05-2026-10-09.html). Eleven final-profile trials passed their scoped gates; the initial checker failure remains retained. Slice 04 already qualifies the pinned 3/5/10 m/s barrier approach/capture matrix. Full accounting remains about 3.06-3.14x the measured ledger-off coast baseline; the proposed overhead target is unmet. Vehicle closure, physical material calibration and broader performance remain upcoming gates. Current work is committed/pushed to dev; master promotion is user-managed.
