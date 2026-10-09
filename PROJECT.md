# rigs-of-rods-trials project

This is Bert's development fork of **Rigs of Rods (RoR)**, the C++ soft-body vehicle simulation platform. Start here before a design, development, build, or recording session.

The project foundation was established on **2026-10-08**. A fresh Windows source build, clean rebuild, incremental build, and recorded driving session have been verified. Platform research and an experiment/trial-system evaluation are now documented. Architecture options for force/energy instrumentation, environment and the trial workbench have also been evaluated. The policy Q&A is complete and a version 0.1 implementation review specification is established. Implementation now includes source-native recording, a .NET coordinator, React workbench, 16-channel accounting, scoped analytical qualification and ledger-off performance/equivalence probes. Vehicle/impact scientific qualification and detailed event windows remain pending. See [Slice 01 delivery/evidence](doc/project/slices/slice-01.md) and the [workbench runbook](apps/trials/README.md).

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

[Slice 03](doc/project/slices/slice-03.md) adds ledger-off control trials, observer optimizations, native equivalence/performance probes and fixture accounting regression. [HTML report](doc/project/reports/trial-slice-03-2026-10-09.html). Twenty-three completed trials and one cancellation have retained evidence. Full accounting remains about 3.06-3.14x the same-build ledger-off baseline; the proposed overhead target is unmet. Barrier/detail capture, vehicle closure and broader performance qualification remain upcoming gates.
