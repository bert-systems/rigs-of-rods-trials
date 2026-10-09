# Project memory

Durable, repository-backed context for future sessions. Established and last updated: **2026-10-08**, America/New_York. This file records stable facts and decisions; evidence files retain detailed logs.

## User intent and standing preferences

- Develop the personal fork `bert-systems/rigs-of-rods-trials`, based on Rigs of Rods.
- Build the source and actually run the simulation. The installed game in the parent workspace must not supply proof binaries.
- Show build/run outcomes with an HTML report, images, and useful video evidence.
- Prepare orderly project files before the user's upcoming design and development sessions.
- Preserve prior evidence and maintain enough context for a future session to continue without reconstructing the project history.

Platform research and architecture evaluation are complete in [platform.md](platform.md) and the [architecture evaluation](doc/project/design/trial-platform-architecture-options.md). The policy Q&A is complete. The [decision log](doc/project/design/implementation-decisions.md) is authoritative for user selections; the [implementation specification](doc/project/design/trial-platform-implementation-spec.md) and [HTML review](doc/project/reports/trial-implementation-spec-2026-10-08.html) consolidate the selected design and proposed contracts.

| Decision | Confirmed direction |
| --- | --- |
| D001–D002 | Validated simulation studies; ground impacts with free-fall/spring/damper fixtures first; flight later |
| D003 | React + .NET coordinator, local browser first; desktop wrapper later option |
| D004 | Complete force attribution/core energy first; capture plastic/breakage transitions immediately; broader energy validation later |
| D005 | Gravity, dry-air temperature/density and steady physical wind first; gusts/turbulence/particulate exposure later |
| D006 | Every-step accounting; ~200 Hz summaries; configured 2 kHz detail, initially 2 s pre/4 s post; UI 10–20 Hz, all subject to profiling |
| D007 | Controlled initial conditions/coasting approach first, driven path/speed controller later |
| D008.1 | Sequential sweeps/repeats; fresh RoR process/private profile/results per attempt |
| D008.2 | Continue after required measurement loss; preserve gaps/later data; sticky incomplete quality prevents scientific validation passing |
| D008.3 | Recorded in-process tick-boundary pause/resume; cancel preserves partial evidence; crash rerun is a new attempt |
| D008.4 | Continue eligible independent queue; manual retries initially; shared blockers hold new launches |
| D009 | Automated scenario-specific fixture, balance, repeatability and capture validation |
| D010 | Pinned Daf Semi/Simple2, controlled barrier and purpose-built reference fixtures first |
| D011 | React scientific dashboards with separate source-built RoR window; interactive scientific 3D inspector later |
| D012 | Preserve recorded data until explicit manual archive/cleanup; insufficient storage holds new launches |

Slice 01 implements native every-step aggregate observation, CRC capture, a serial .NET coordinator and a React scientific workbench. Scientific validation is deliberately NotReady; model/energy attribution, raw detail windows and analytical fixtures are unfinished. Fixture values, tolerances, capture budgets/triggers, exact protocol/durability and lease behavior remain proposed engineering work. Coupled particle/surface physics is later scope. Do not interpret a completed execution or later retained data as recovery of a required measurement gap.

## Stable project locations

| Item | Location |
| --- | --- |
| Source fork | `D:\Rigs of Rods\rigs-of-rods-trials` |
| Git origin | `https://github.com/bert-systems/rigs-of-rods-trials.git` |
| Upstream | `https://github.com/RigsOfRods/rigs-of-rods` |
| Original build/evidence root | `D:\Rigs of Rods\source-build-2026-10-08` |
| Original HTML report | `source-build-2026-10-08\report\index.html` under the workspace parent |
| Original portable archive | `source-build-2026-10-08\rigs-of-rods-source-build-evidence.zip` under the workspace parent |
| Canonical build procedure | [doc/project/build-and-record.md](doc/project/build-and-record.md) |
| Small baseline records | [doc/project/baselines/2026-10-08](doc/project/baselines/2026-10-08/README.md) |

The original tools virtual environment and dependency cache live under the baseline root. They may be reused as existing tooling/cache, but new build/config/log/media output must go into a new session directory. Do not rerun the historical wrappers against the baseline.

## Verified baseline: 2026-10-08

| Fact | Recorded result |
| --- | --- |
| Branch and source commit | `master`, `e85535569102b6251849af574026984e3213b3f4` |
| Source tree during proof | Clean; 452 C++ source/header files counted |
| Upstream master at comparison | Matched the source commit at that dated check |
| Content submodule commit | `34fefdd126784bf87b068fc283f812525d159dd7` |
| Toolchain | VS 2022 Professional 17.14.11; MSVC 19.44.35214; x64 Release |
| Build tools | CMake 3.31.10; Conan 2.33.0; Ninja 1.13.2; Python 3.13.3 |
| Machine | Ryzen 9 3950X, 16 cores/32 threads, 63.93 GiB RAM, RTX 3090 |
| Configuration/dependency resolution | Approximately 627.4 seconds; 12 missing dependency packages compiled |
| Fresh game build | 368 Ninja steps; 63.953279 seconds; exit 0 |
| Clean game rebuild | 369 files cleaned, then 368 steps; 67.2503289 seconds; exit 0 |
| Incremental build | Version information regenerated and executable relinked; 28.7821338 seconds; exit 0 |
| Executable | `source-build-2026-10-08\build\bin\RoR.exe` under the workspace parent |
| Executable SHA-256 | `2F74316A16AE2D44B7E1D458ECF25E409E1CD0D853DBE0F1065AC91FE7BBC70A` |
| Window version | `2026.10-dev-e85535569` |
| Scenario | Simple Test Terrain (`simple2.terrn2`), Daf Semi (`b6b0UID-semi.truck`), 176 nodes, Direct3D9 |
| Telemetry | 36 samples / 36 seconds; maximum displacement 125.54 m; maximum wheel speed 19.9565 km/h |
| Media | Three native screenshots; 35.3-second MP4, 1280 x 720 |
| HTML checks | Playwright/installed Chrome: playback succeeded, no page errors/missing local links, desktop/mobile without horizontal overflow |
| CTest | Zero registered tests |

The executable hash differs from the installed game's comparison hash. Runtime process and loaded-module records confirmed the compiled executable and no modules from the parent installation. Process IDs in those records are historical, not a currently running simulation.

"From source" describes the game build. Some dependency binaries were fetched by Conan. A clean game rebuild does not also rebuild every dependency. The recorded Conan lock preserves recipe versions/revisions; it does not guarantee bit-identical binaries, future remote availability, or identical timing.

Wheel speed is the vehicle's wheel-speed reading, not GPS speed. Displacement is straight-line distance from the initial position, not cumulative distance traveled. These results establish an exercised driving scenario, not validated physical accuracy.

## Known issues and workarounds

1. **Preset vehicle entry.** The first scripted launch loaded the vehicle but did not seat the player. At the baseline, `AppCommandLine.cpp` sets `cli_preset_veh_enter` for `-enter`; the config-origin spawn path in `GameContext.cpp` checks `diag_preset_veh_enter`. The successful run set `diag_preset_veh_enter = true` in the private RoR.cfg. This is a workaround, not a source fix. The failed attempt's logs and idle video remain in the evidence root.
2. **Runtime diagnostics.** Fonts/materials/legacy overlays and missing English localization produced nonfatal messages. New mod cache/race-time files were initially absent. Cache generation and driving completed. Keep these findings visible when selecting future work.
3. **Compiler profile selection.** The machine also has VS 2026. Conan default detection reported compiler 195; CMake's generated host profile selected 194 for the explicit VS 2022 compiler. Check actual host/build profiles and CMake compiler identity rather than relying on a default profile's name.
4. **Incremental builds.** The generated version target deliberately runs again, so an unchanged-tree build can still compile version information and relink RoR.
5. **Historical scripts.** The baseline configure/build/run/record/report scripts contain absolute paths, overwrite outputs, and label the baseline commit. Copy/adapt them into a new session before use; refresh every identity label.
6. **Capture method.** Native computer automation was unavailable in the baseline tool session. FFmpeg captured the game window and AngelScript drove the scenario. Playwright checked the report rather than controlling or recording the native game.

## Trial-platform research findings

The inspected engine/content revisions remain the verified baseline. These are source-supported observations, not new runtime validation of every API.

- Existing scripts, vehicle AI, terrain/content definitions and node mass/position/velocity support exploratory trials. Built-in races, replay/save and diagnostic gadgets do not provide the complete requested experiment lifecycle.
- Momentum and node kinetic energy can be derived from coherent mass-weighted state with an explicitly defined body/frame/time. Actor position is not necessarily center of mass; wheel speed is not translational speed.
- getNodeForces() exposes a phase-dependent live accumulator. Integration resets it to gravity and other passes can add contributions; it is not a recorded complete contact-force waveform.
- Physics uses a 0.5 ms step, but script frameStep runs once per frame before new physics work. game.getTime() is accumulated simulation time. Tick-level contact/force/work/energy measurements need native observation with phase, channel, identity and data-loss accounting.
- Gravity is a scalar vertical setting. Non-Earth/zero-gravity behavior needs subsystem checks. No general physical ambient-wind/gust field setter was found in the inspected source; visual wind and arbitrary node forces do not establish aerodynamic wind.
- The versioned starter content has three truck definitions, two trailers and three terrains. No airplane/boat definition is included there. Community assets require independent compatibility, license and calibration checks; the resource catalog denied automated access during research.
- Fixed time steps, saved scenes and replay do not establish bitwise determinism or complete reset. No supported headless experiment mode was verified.
- The selected specification composes existing simulation/control with native force/energy instrumentation. Its proposals require source-path coverage, feasibility and independent fixture qualification before physical claims.

Detailed source references, formulas, coverage tables, caveats and proposed validation stages belong in platform.md, not duplicated here.

## Architecture evaluation findings and proposed direction

- Native observation must track generated and consumed epochs because CalcNodes integrates before much later force generation, then resets forces. Rope/link state and force transfers, contact branches and beam force corrections need direct instrumentation.
- Proposed separation: instrumented native worker, UI-independent .NET trial coordinator, durable raw archive/analysis, and either WPF or React workbench. The evaluation prefers React with a local ASP.NET Core coordinator. D003 subsequently selects React with a .NET coordinator and local browser delivery first; the detailed hosting/transport contracts remain open. No workbench or coordinator has been implemented.
- Every-step accounting is distinct from raw retention and UI refresh. Proposed profiles use 2 kHz accounting, selected/event-window raw capture and 10–20 Hz UI summaries. These are targets, not benchmarks.
- A complete ledger has supported/estimated/unclosed channels and explicit residuals, including wind reservoir and direct state/mass changes. No validated all-model energy conservation claim exists.
- Proposed environment levels start with coherent gravity/dry atmosphere/constant wind, then structured gust/shear/turbulence and passive exposure. Visual dust, passive particles and two-way physical particles remain separate modes; advanced coupling/CFD is a separate expansion.
- Fourteen epics and staged alpha/impact/flight/scale gates are recorded in the evaluation. Preliminary staffing assumes 4–5 effective people; 12–18 weeks for a narrow alpha and 6–12 months for broader scope are judgment estimates before spikes/calibration.
- The version 0.1 implementation specification now consolidates the confirmed choices and proposes fixture parameters, model coverage, capture budgets, numerical acceptance candidates and operational contracts. These require feasibility evidence and frozen acceptance profiles before validation claims.

## Decisions

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-10-08 | Use the personal fork as canonical development source. | Matches the user's repository and source-build requirement. |
| 2026-10-08 | Keep source-build outputs and evidence separate from the installed game. | Makes executable provenance reviewable and protects the installation. |
| 2026-10-08 | Retain the original proof run; create new session roots for future runs. | Prevents later work overwriting the baseline. |
| 2026-10-08 | Keep canonical project instructions and memory in the fork, with a parent-workspace AGENTS.md pointer. | Supports Git persistence and discovery when a chat starts in the parent folder. |
| 2026-10-08 | Use uppercase AGENTS.md for agent discovery and lowercase architecture.md, todo.md, project-memory.md. | Provides the requested introduction files using conventional agent naming. |
| 2026-10-08 | Retain small baseline records in Git; keep full media/build artifacts outside Git. | Preserves durable evidence references without adding large generated files to the source history. |
| 2026-10-08 | Wait for the user's next design scope before starting backlog implementation. | The current request is project preparation. |
| 2026-10-08 | Treat platform.md as the canonical platform/use-case research record and generate an offline HTML companion. | Keeps source references and caveats durable while providing an illustrated review artifact. |
| 2026-10-08 | Complete research before architecture/design and implementation. | Matches the user's requested sequence; measurement accuracy and wind remain explicit design/validation work. |

## Session history

### 2026-10-08 — Source-build evaluation

Verified fork identity, configured with an isolated Conan cache, built/rebuilt the game, exercised scripted driving, and created the HTML evidence report and archive. See baseline records for exact provenance and results. No engine source changes were made.

### 2026-10-08 — Project documentation foundation

Established the project introduction, agent guidance, architecture map, TODO list, project memory, and canonical build/record guide. Added lightweight copies of baseline records and a workspace entry point. Changes are documentation and historical records only; this foundation is saved locally and does not by itself indicate a Git commit or GitHub push.

Documentation validation: all 86 local links resolve; copied baseline records and script match the originals byte for byte; the baseline executable still matches its recorded SHA-256. PowerShell examples were syntax-checked without running another build or simulation.

### 2026-10-08 — Platform landscape and trial-system evaluation

Researched official documentation and local source at e85535569102b6251849af574026984e3213b3f4; inventoried starter definitions and scripting registrations. Saved [platform.md](platform.md), the [illustrated HTML report](doc/project/reports/platform-evaluation-2026-10-08.html), and a [research index](doc/project/research/2026-10-08/README.md) containing 54 source/documentation references.

The report includes four accessible SVG diagrams, a 22-dimension capability matrix, and a clearly labeled illustrative momentum/energy/mean-force calculator. Playwright with installed Chrome checked 12 sections, 15 tables, four diagrams, local links, 37 source ranges, formula/filter behavior and desktop/mobile layouts. The final report loads without external requests or page errors and has no page-level horizontal overflow. Screenshots and validation output: D:\Rigs of Rods\platform-evaluation-2026-10-08-123840. Earlier report-QA failures are retained in separate output directories; invalid source end anchors and mobile overflow were corrected.

No engine source change, build, simulator run, asset download or physical-accuracy claim was added during research. Original source-build evidence remains separate and preserved. Limitations include frame-level observation, missing contact/energy ledger, no verified ambient-wind interface, no new flight/impact/repeatability runtime tests, and incomplete community-catalog access. Foundation/research documentation is saved locally; no commit or push was performed.

### 2026-10-08 — Instrumentation/environment/trial architecture evaluation

Inspected the native force/integration/collision/beam/constraint and aerodynamic paths at the unchanged baseline. Evaluated two workbench options sharing a C++ worker and .NET coordinator, and documented candidate contracts, 14 epics, dependencies, validation and delivery strategies in [the architecture evaluation](doc/project/design/trial-platform-architecture-options.md) and [HTML report](doc/project/reports/trial-architecture-options-2026-10-08.html).

Primary .NET/WPF/React/SignalR/storage and NASA references were checked. Four accessible diagrams and an illustrative capture-budget calculator accompany the report. Browser/source/link checks are recorded in [design evidence](doc/project/design/2026-10-08/README.md); screenshots remain outside Git in the directory identified by its validation JSON. The report loads without external requests/page errors and has no desktop/mobile page overflow.

No engine code, game build/run, dependency/framework installation or calibration was performed. Existing platform report and source-build evidence remain preserved. The result is an architectural recommendation awaiting detailed implementation decisions, saved locally without a commit/push.

### 2026-10-08 — Implementation Q&A: scientific purpose

The user selected A: validated simulation studies. Recorded D001 in the [implementation decision log](doc/project/design/implementation-decisions.md), including reference-test and honest accounting requirements. Exact scenarios, tolerances, UI, environment and operational decisions remain open. The next question selects the pilot domain. Documentation only; source/content revisions and existing local changes are preserved; no build, implementation, commit or push.

### 2026-10-08 — Implementation Q&A: first milestone

The user selected A: ground impacts first. Recorded D002 in the [implementation decision log](doc/project/design/implementation-decisions.md): controlled vehicle-to-barrier trials with free-fall and spring/damper reference fixtures, followed by flight in a later milestone. Exact assets, parameters and acceptance remain open; the next question selects the workbench UI. Documentation only; engine/content identity and prior evidence remain unchanged. Saved locally; no build, implementation, commit or push.

### 2026-10-08 — Implementation Q&A: workbench

The user selected A for the workbench question: React with a .NET coordinator, local browser first, with a desktop wrapper possible later. Recorded D003 in the [implementation decision log](doc/project/design/implementation-decisions.md), clarified the question-local option lettering and updated the architecture introduction and TODO. Force/energy scope is the next decision; detailed contracts and implementation remain pending. Checked local documentation links and whitespace; engine/content revisions and existing source-build evidence are unchanged. Saved locally; no build, implementation, commit or push.

### 2026-10-08 — Implementation Q&A: accounting sequence

The user selected A for force/energy staging. Recorded D004 in the [implementation decision log](doc/project/design/implementation-decisions.md): complete force attribution and core energy validation first, immediate capture of deformation/breakage transitions with qualified estimates and explicit residuals, and broader energy validation afterward. Exact channels, tolerances and acceptance remain open; the next question selects initial environmental scope. Checked local documentation links and whitespace. Source remains e85535569102b6251849af574026984e3213b3f4; content remains 34fefdd126784bf87b068fc283f812525d159dd7. Existing local documentation and historical build/run evidence are preserved. Saved locally; no engine implementation, build, commit or push.

### 2026-10-08 — Implementation Q&A: initial environment

The user selected A for initial environmental scope. Recorded D005 in the [implementation decision log](doc/project/design/implementation-decisions.md): configurable gravity, dry-air temperature/density and steady wind with consistent drag treatment first; gusts/turbulence and particulate exposure afterward. Coupled particle forces/surface interactions remain a separate open scope decision. Exact environment contracts, supported ranges and validation remain open; recording profiles are the next question. Checked local documentation links and whitespace. Source remains e85535569102b6251849af574026984e3213b3f4; content remains 34fefdd126784bf87b068fc283f812525d159dd7. Prior local changes and historical build/run evidence are preserved. Saved locally; no engine implementation, build, commit or push.

### 2026-10-08 — Implementation Q&A: recording profile

The user selected A for recording profiles. Recorded D006 in the [implementation decision log](doc/project/design/implementation-decisions.md): every-step force/energy accounting, continuous summaries around 200 Hz and configured node/contact/beam detail at 2 kHz in an initial 2-second pre/4-second post-impact window; live UI around 10–20 Hz. Rates/windows are selected profiling targets, not achieved performance. Byte budgets, trigger semantics and loss policies remain open; the next question selects how impact trials establish their approach state. Checked local documentation links and whitespace. Source remains e85535569102b6251849af574026984e3213b3f4; content remains 34fefdd126784bf87b068fc283f812525d159dd7. Prior local changes and historical build/run evidence are preserved. Saved locally; no engine implementation, build, commit or push.

### 2026-10-08 — Implementation Q&A: impact approach

The user selected A then later B. Recorded D007 in the [implementation decision log](doc/project/design/implementation-decisions.md): controlled settled/initialized vehicle conditions and verified approach speed/alignment for the first impact milestone; a driven approach using throttle/brakes/steering and path/speed control follows later. The later driven mode is an explicit roadmap decision. Exact state initialization, assets, speeds and tolerances remain open; execution of trial batches is the next question. Checked local documentation links and whitespace. Source remains e85535569102b6251849af574026984e3213b3f4; content remains 34fefdd126784bf87b068fc283f812525d159dd7. Existing local changes and historical build/run evidence are preserved. Saved locally; no engine implementation, build, commit or push.

### 2026-10-08 — Implementation Q&A: batch execution

The user selected A for batch execution. Recorded D008.1 in the [implementation decision log](doc/project/design/implementation-decisions.md): sequential queued sweeps/repeats, one fresh RoR process with private configuration and separate results per trial. Parallel isolated execution remains a later option. Measurement-loss policy is the next question; pause/cancel, recovery and detailed contracts remain open. Checked local documentation links and whitespace. Source remains e85535569102b6251849af574026984e3213b3f4; content remains 34fefdd126784bf87b068fc283f812525d159dd7. Existing local changes and historical build/run evidence are preserved. Saved locally; no engine implementation, build, commit or push.

### 2026-10-08 — Implementation Q&A: measurement loss

The user selected B for required measurement loss. Recorded D008.2 in the [implementation decision log](doc/project/design/implementation-decisions.md): continue collecting later observations, persist explicit gaps and incomplete capture quality, and prevent the affected attempt from passing scientific validation. Execution completion, capture quality and validation are separate states. This selects continued observation with incomplete quality; implementation must follow this decision rather than the stop/reject policy discussed in the historical architecture evaluation. Pause/cancel and crash recovery are the next topic; detailed gap/resource contracts remain open. Checked local documentation links and whitespace. Source remains e85535569102b6251849af574026984e3213b3f4; content remains 34fefdd126784bf87b068fc283f812525d159dd7. Existing local changes and historical build/run evidence are preserved. Saved locally; no engine implementation, build, commit or push.

### 2026-10-08 — Implementation Q&A: pause and recovery

The user selected A for pause/recovery. Recorded D008.3 in the [implementation decision log](doc/project/design/implementation-decisions.md): recorded tick-boundary pause/resume within the current process, cancellation preserving partial results and new attempts after crashes. Durable checkpoint restoration is outside the first release. D008.2 still governs measurement loss: continue with incomplete/nonpassing quality. Detailed timeout/retry/queue rules remain open; the next question selects pilot assets and fixtures. Checked local documentation links and whitespace. Source remains e85535569102b6251849af574026984e3213b3f4; content remains 34fefdd126784bf87b068fc283f812525d159dd7. Existing local changes and historical build/run evidence are preserved. Saved locally; no engine implementation, build, commit or push.

### 2026-10-08 — Implementation Q&A: pilot assets and terrain collection

The user selected start with A and invited inspection of the downloaded terrain collection. Recorded D010 in the [implementation decision log](doc/project/design/implementation-decisions.md): the pinned Daf Semi and Simple Test Terrain, with a controlled barrier and free-fall/spring-damper fixtures, anchor the first pilot.

Located downloaded terrains at D:\Rigs of Rods\content\Terrains, outside the Git fork. Read ZIP directories and bounded terrain-definition text: 23 packages, 44 .terrn2 entries, 31 legacy .terrn entries, 772,194,711 compressed bytes, and zero inspection errors. Counts include paired/variant definitions; they are not counts of tested terrains. Saved a [terrain inventory](doc/project/research/2026-10-08/terrain-inventory.md) and JSON containing names/config fields, CRC/definition hashes, sizes and license/readme candidate filenames. Additional candidates include Pines/Auriga proving grounds, Top Gear Test Track, N-Labs Testing Facility and Sweden Airport. No extraction, full-package CRC validation, license conclusion, terrain loading or physical calibration was performed. Preserve packages and pin complete archive identity before later trial use.

Next question selects scientific-validation approval/gates. Checked local documentation links, recorded descriptor counts and whitespace. Source remains e85535569102b6251849af574026984e3213b3f4; content remains 34fefdd126784bf87b068fc283f812525d159dd7. Existing local changes and historical build/run evidence are preserved. Saved locally; no engine implementation, build, simulator run, commit or push.

### 2026-10-08 — Implementation Q&A: validation approval

The user selected A for scientific-validation approval. Recorded D009 in the [implementation decision log](doc/project/design/implementation-decisions.md): automated checks per scenario for reference fixtures, force/momentum/energy balances, repeatability and complete required capture, with reviewable observations/residuals/thresholds. A pass is scoped to declared measurements and supported models; estimates, unclosed terms and calibration limitations remain visible. D008.2 still prevents attempts with required capture gaps from passing. Exact fixture parameters, numerical tolerances and repeatability gates are specification work. Queue progression and retry behavior are the next question. Checked local documentation links and whitespace. Source remains e85535569102b6251849af574026984e3213b3f4; content remains 34fefdd126784bf87b068fc283f812525d159dd7. Existing local changes and historical build/run evidence are preserved. Saved locally; no engine implementation, build, commit or push.

### 2026-10-08 — Implementation Q&A: batch progression

The user selected A for batch progression. Recorded D008.4 in the [implementation decision log](doc/project/design/implementation-decisions.md): continue eligible independent trials after individual failed/incomplete attempts, preserve their evidence/status and provide manual retries as separate attempts. Shared blockers hold new launches with a visible reason. D008.2 still governs active-trial measurement loss. Timeout/lease, blocker-clearing, eligibility and archive-recovery mechanics remain detailed specification work. Live visualization scope is the next question. Checked local documentation links and whitespace. Source remains e85535569102b6251849af574026984e3213b3f4; content remains 34fefdd126784bf87b068fc283f812525d159dd7. Existing local changes and historical build/run evidence are preserved. Saved locally; no engine implementation, build, commit or push.

### 2026-10-08 — Implementation Q&A: live visualization

The user selected A for live visualization. Recorded D011 in the [implementation decision log](doc/project/design/implementation-decisions.md): React charts/status for force components, momentum/energy, environment, events and capture health, alongside the separate source-built RoR window. The interactive scientific 3D inspector is planned for later. Updated the architecture introduction to reflect the selected view boundary. Data retention is the final policy question before consolidating the specification; detailed engineering contracts and numerical targets remain specification work. Checked local documentation links and whitespace. Source remains e85535569102b6251849af574026984e3213b3f4; content remains 34fefdd126784bf87b068fc283f812525d159dd7. Prior local changes and historical evidence are preserved. Saved locally; no engine implementation, build, commit or push.

### 2026-10-08 — Q&A completion and implementation review baseline

The user selected A for the final retention question. Recorded D012: preserve recorded data until explicit manual archive/cleanup; insufficient storage holds new launches. All 15 policy selections are complete, including the user's B choice for continuing after required measurement loss and A-then-later-B choice for controlled versus driven approach.

Saved the [version 0.1 implementation specification](doc/project/design/trial-platform-implementation-spec.md) and [HTML review](doc/project/reports/trial-implementation-spec-2026-10-08.html). They consolidate native force/energy timing and coverage, physical environment adoption, trial/attempt contracts, capture/archive and independent quality states, React/.NET workbench, proposed fixtures/tolerances/budgets, 14 epics and five qualification/delivery gates. Proposed transport/storage/lease/default choices remain separate from confirmed policy and achieved results. Updated project introduction, agent guidance, architecture map and backlog; E01 feasibility/contract work is the suggested first implementation step.

Playwright with installed Chrome passed 12 sections, 10 tables, two accessible SVG diagrams, all seven illustrative policy cases, seven pinned source ranges and local Markdown/HTML links. Desktop/mobile have no page-level overflow, external requests or page errors. Native measurements are not exercised by the report. Screenshots were visually reviewed for legibility. Final QA captures: D:\Rigs of Rods\trial-implementation-review-2026-10-08-192445-773386. [Reproduction/check records](doc/project/design/2026-10-08/implementation-review.md) retain results and protected-evidence comparisons.

Read-only inspection found .NET 10.0.103/10.0.203 SDKs already installed. Native source/content remain e85535569102b6251849af574026984e3213b3f4 / 34fefdd126784bf87b068fc283f812525d159dd7. No engine/launcher implementation, game build/run, framework installation, asset modification, commit or push occurred. Original build and prior reports remain preserved. Contracts, resource/performance feasibility and physical acceptance/calibration are future work.

### 2026-10-08 — Implementation Slice 01: native capture and local trial workbench

The user authorized large implementation slices with actual image/video evidence and commit/merge/push for each major slice. Implemented the first end-to-end foundation: actor-owned integration ledger, bounded native recorder/CRC archives, pilot gravity/density/steady-wind adoption, controlled settled rolling coast, immutable experiments and serial private source-built workers, retained SQLite/catalog recovery and React live views/controls.

The new source-built executable SHA-256 is 42BFCDF0171C6986474D2616B742FF3B4D997C7E16E28076A77823B67548A2EC. Build provenance records baseline HEAD e85535569102b6251849af574026984e3213b3f4 plus dirty implementation source hashes; starter content stays 34fefdd126784bf87b068fc283f812525d159dd7. A new native build reused the verified Conan dependency cache; subsequent fixes were incrementally rebuilt. No installed game executable/DLL provided proof. Original baseline executable hash remains unchanged.

The final six-worker feature check passed: pause/native-clock stop/resume at tick 8752; isolated wind repeats with shared immutable revision and distinct PID/profile; native adoption of gravity −8, density 1 and wind [3,0,−1]; retained cancellation; next independent attempt; separate manual retry and non-destructive archival marking. The primary 12-second coast (plus 3-second settle) captured 30,068 verified aggregate records with zero loss and moved the mass-weighted COM 33.394 m. Maximum native integration residuals were 0.000681712 kg·m/s and 0.003220181 J. These are update-boundary observations, not a closed conservative/dissipative energy validation.

Standalone C++ CTest and .NET contract/archive checks pass. The Release .NET build has zero warnings/errors and Vite builds successfully. Playwright checked live inputs/controls, desktop/mobile layout, report references/images and actual video decoding. The 15.3-second native-window MP4 is 1280×720; native screenshots show settling and nonzero-speed coasting. Coordinator restart recovered 14 terminal attempts with incomplete/archived states preserved. A final UI-only change improves small-residual axis scaling and was checked against retained real measurements.

Early compiler/host/tooling failures are preserved. One pressure-loss run has 3,251 missing records and remains Completed / Incomplete / NotReady. Recorder buffering/grouped flushes produced zero-loss final feature runs; workload/filesystem-failure stress remains pending. An initial pause assertion read delayed recorder samples; native applied ticks confirmed the pause and an independent heartbeat clock corrected the display/check.

[Slice 01 delivery](doc/project/slices/slice-01.md), [HTML evidence](doc/project/reports/trial-slice-01-2026-10-08.html) and [runbook](apps/trials/README.md) record implementation boundaries and reproduction. Full evidence: D:\Rigs of Rods\trial-slice-01-2026-10-08-1938. Publication identifiers are recorded in its report/publication.json after commit, merge to master and remote verification; source changes and lightweight results belong in this slice's commit. The prior uncommitted foundation/research/design documentation is preserved and included in publication.

Scientific validation remains NotReady for every attempt. Next: explicit force generation/consumption attribution, initialization/mass/state ports, closed core energy and native free-fall/spring-damper fixtures, then controlled barrier/impact and raw node/beam/contact event windows. General assets, driven paths, flight/gust/particles and live scientific 3D views remain later work.

## How to maintain this file

Append a dated session entry with objective, outcome, checks, unresolved issues, and evidence location. Promote only durable decisions/findings into the relevant sections. Distinguish facts from hypotheses; resolve or retire stale items explicitly. Link detailed session records instead of pasting logs. Never rewrite the dated baseline as if it described a later build.

## 2026-10-08 — Slice 02 and video playback recovery

Implemented [native force channels, core energy/work, analytical fixtures and live qualification](doc/project/slices/slice-02.md). Final native SHA-256 B6176E71C8C20C732E895EC628C28DD1AD6F96ED8D38FF8A12B112BD68FD1301 at `D:\Rigs of Rods\trial-slice-02-2026-10-08-221217\build\bin\RoR.exe`. Newly compiled native outputs reuse the established Conan cache. Content revision and protected baseline executable hash remain unchanged.

Thirteen final attempts completed with complete capture and zero loss: seven scoped fixture Passed, six vehicle NotReady. Fixture repeat pairs matched compared positions/momentum/energy on this workstation. Ledger/contract checks, zero-warning .NET build, locked npm production build, provenance, native pause/resume and responsive browser checks passed. Results: `doc/project/slices/slice-02-results.json`.

Initial legacy-precision spring/damper cases failed budgets. Analytical fixtures explicitly use precise beam lengths/local relative coordinates; vehicles retain the approximate kernel. Do not generalize fixture Passed to vehicle/impact/environment qualification. Two-run-per-mode step-time characterization measured 61.4µs median disabled vs 110.2µs enabled (1.795×). These are elapsed wall durations, not CPU time or an instrumentation-off baseline. Optimization remains required.

Old user-reported poster-then-blank MP4s decoded visible images. WebM/image players recover baseline/Slice 01 playback without overwriting originals. New OpenGL/GDI capture really was black and was rejected/preserved. Final recording uses41 actual native renderer screenshots;82 decoded samples were nonblank. Chrome visible-pixel/image-progression checks passed. Codex in-app GPU playback remains unverified due automation-helper initialization failure; use Play frames if video remains blank.

Report: `doc/project/reports/trial-slice-02-2026-10-08.html`. Session: `D:\Rigs of Rods\trial-slice-02-2026-10-08-221217`; report/index.html and report/slice-02-evidence.zip. Slice 01 HTML gained a dated recovery link; the protected baseline remains untouched. User authorization to commit/merge/push major slices persists; final identity is in session report/publication.json after Git publication. Next gates: observer optimization, barrier/detail windows, broader storage/environment qualification; driven journeys/flight remain later.


### 2026-10-09 — Slice 03 observer baseline and equivalence

Continued under the user's major-slice commit/merge/push authorization. This prerequisite takes Slice 03; planned controlled barrier/detail capture moves to Slice 04 without changing the confirmed ground-impact goal. Implemented sparse node-channel caches/phase reductions, audited inactive-phase observer skips, unused beam-geometry avoidance, writer CRC table and full-ledger-off runtime mode. Native force routines and random-draw order remain; fixture precise normalization/priming follows scenario independently of observer state.

.NET/React expose full/base/off profiles and an explicit common timing/state probe, compact per-attempt status reads, probe-only charts/archives and nonpassing off-mode science. Probe schema 1 / 128 bytes remains separate from aggregate schema 2 / 2080 bytes. Required probe failure remains incomplete while later capture continues. Timer includes native phases/barriers and enabled ledger reduction/copy, ends before common probe sampling/queueing, and measures steady-clock elapsed time rather than process CPU.

Initial source-built native SHA-256 before readiness ownership repair `679EEAF627F53C7AF157C97E783C83DE17CF1D5D25DCB14131A57F8F2E68D822`. Session `D:\Rigs of Rods\trial-slice-03-2026-10-08-235749`. Three interleaved fresh-process repeats/mode at 5 m/s: off median/p95 21.6/31.6 us, full 68.7/89.7 us, 3.181x. At 15 m/s: off 21.4/31.0, full 68.3/88.3, 3.192x. Each speed/profile retains 30,003 released probe records. Earlier Slice 02's 79.5% added channels cost used a partial baseline; these total full/off ratios are not the same measurement. Historical duration changes also have capture/polling confounds. Proposed ≤10% target remains unmet.

Twenty-three completed attempts and one preserved cancellation; all declared captures complete, zero required-record loss. Three dry fixture Passed, others NotReady. Fifteen declared full/off/base/repeat/wind comparisons have exact sentinel position/velocity equality and zero specified 10 Hz fingerprint mismatches. They do not prove all state at every tick or broad determinism. Fixture accounting terms match 21,000 preserved Slice 02 records exactly. C++/.NET/production build checks, native pause/resume/cancel, source process/module provenance and desktop/mobile/no-browser-error checks passed.

Native full-ledger visual evidence uses 56 real OpenGL renderer screenshots, with loading/startup retained; nominal 2 fps sequence produces 112 decoded 4 Hz image samples, all nonblank. Ordinary-image progression and Chrome visible WebM pixels verified. Codex GPU playback remains unverified. Report: [Slice 03 HTML](doc/project/reports/trial-slice-03-2026-10-09.html), [delivery](doc/project/slices/slice-03.md), [results](doc/project/slices/slice-03-results.json). Package/publication identities are in session `report/publication.json` and `report/bundle-check.json`.

Retained build failures: MSVC C1060 at 16 jobs (6 worked; wrapper defaults to 8 and accepts explicit concurrency), initially uncaught probe InvalidDataException and mixed-encoding JSX rejected by Vite. All corrected checks passed. Protected original baseline executable/content are unchanged. Remaining gates: overhead budget, controlled barrier/contact identity and required impact detail, broader energy/environment/scale qualification. No scientific tolerances were loosened. Final feature/merge/remote identities will be recorded in publication.json after the authorized publication.


Final review repaired readiness ownership: first matching pilot owns preparation; a second matching actor sets sticky scope invalidity instead of replacing the ready actor. Repeated the full native qualification and visual/control set using final executable SHA-256 `713CFD3905237808D40CA35F432BAF89638AFE943370494A09526FAC69D2EDCC` and source inventory `source-20261009-003714-1462.json` (all 471 entries match). Final 5 m/s off/full medians 22.1/67.6 us, p95 33.1/89.4 us, ratio 3.059x; 15 m/s 21.4/67.1, p95 32.2/88.9, ratio 3.136x. Same 23 Completed + one Cancelled, three scoped Passed, zero required loss, 15 matching comparisons and exact 21,000-record accounting regression. Final native media again has 56 real frames and 112 nonblank decoded samples, in `media/slice-03-final-native`. Initial 24 attempts/media and `report/initial-slice-03-evidence.zip` remain retained. Final readers also distinguish closed from complete probe archives. Report/results select the final qualification set; both source builds' raw evidence is preserved.
