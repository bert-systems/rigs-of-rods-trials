# Project TODO

Updated: 2026-10-09. This is a planning record, not authorization to implement every item. Research, architecture evaluation and policy Q&A are complete. The [implementation specification](doc/project/design/trial-platform-implementation-spec.md) establishes review baseline 0.1; its proposed defaults/contracts need feasibility and qualification work before acceptance claims.

Current publication workflow: develop, integrate, commit and push on `dev`. The user manages periodic pull requests into `master`; follow [AGENTS.md](AGENTS.md) rather than the historical automatic master-merge workflow.

## Completed foundation

- [x] Identify the personal fork, upstream relationship, source revision, and starter-content revision.
- [x] Configure in a fresh build directory and build the game from source.
- [x] Verify a clean rebuild and subsequent incremental build.
- [x] Launch the compiled executable using a private portable profile.
- [x] Record actual vehicle movement with native screenshots, video, and telemetry.
- [x] Produce and verify the HTML evidence report and portable archive.
- [x] Establish PROJECT.md, AGENTS.md, architecture.md, build/record procedures, and project memory.
- [x] Preserve lightweight baseline records in the fork and retain the full original evidence outside Git.

## Completed platform research

- [x] Research simulation domains, content/configuration, starter assets, terrains and environmental controls.
- [x] Inspect scripting, waypoint AI, autopilot, force actuators, replay/save, events, telemetry and logging.
- [x] Evaluate the requested experiment parameters and momentum, force, energy and flight outcomes.
- [x] Document measurement semantics, ambient-wind gaps, repeatability limits and validation needs.
- [x] Save [platform.md](platform.md), the [HTML report](doc/project/reports/platform-evaluation-2026-10-08.html), and pinned research records.
- [x] Verify report links/source anchors, desktop/mobile layout, calculator and capability filters.

## Completed architecture evaluation

- [x] Evaluate native force/energy observation with generated and consumed epochs, model coverage and residuals.
- [x] Evaluate coherent atmosphere/wind adoption and visual, passive and coupled particulate scope.
- [x] Compare Windows .NET/WPF and React/ASP.NET Core workbench options sharing a native worker and .NET coordinator.
- [x] Document trial lifecycle, effective configuration, tick controllers, storage/recovery, live views and comparison.
- [x] Define 14 epics, dependencies, completion evidence, delivery strategies and preliminary staffing/calendar envelopes.
- [x] Persist [architecture options](doc/project/design/trial-platform-architecture-options.md) and the [illustrated HTML](doc/project/reports/trial-architecture-options-2026-10-08.html).
- [x] Verify report source/local references, formulas, desktop/mobile layout and diagrams.
- [x] Inspect and inventory the downloaded terrain collection: 23 ZIP packages; 44 modern/31 legacy definition entries ([local inventory](doc/project/research/2026-10-08/terrain-inventory.md)).

## Before implementation

- [x] Capture the user's intended use case: configurable vehicle/environment/path trials with impact and flight outcomes.
- [x] Select the first-release scientific purpose: validated simulation studies (D001).
- [x] Select the first end-to-end milestone: ground impacts with free-fall/spring/damper fixtures; flight later (D002).
- [x] Select first pilot assets: pinned Daf Semi and Simple Test Terrain, with a controlled barrier/free-fall/spring-damper fixture package (D010).
- [x] Select automated scenario-specific validation checks with scoped pass/failure evidence (D009).
- [ ] Qualify fixture definitions/parameters, constraints, native model coverage and numerical acceptance profiles (E01/E13; O01/O02/O05).
- [x] Map the proposed behavior to native observer/solver, environment, execution adapter, coordinator, storage and workbench areas.
- [x] Record architectural options and epic-level delivery strategies.
- [x] Select the workbench UI/coordinator boundary: React + .NET coordinator, local browser first (D003).
- [x] Select the accounting validation sequence: complete force attribution/core energy first; capture deformation/breakage immediately and expand energy validation later (D004).
- [x] Select initial environmental scope: configurable gravity, dry-air temperature/density and steady wind; gusts/turbulence/particulate exposure later (D005).
- [x] Select the default capture profile: every-step accounting, continuous summaries and detailed impact windows, with rates/windows to profile (D006).
- [x] Select impact approach sequencing: controlled initial conditions first; driven approach with path/speed control later (D007).
- [x] Select initial batch execution: sequential sweeps/repeats with a fresh RoR process, private configuration and separate results per trial (D008.1).
- [x] Select required measurement-loss behavior: continue capture, mark incomplete and prevent scientific validation from passing (D008.2).
- [x] Select first-release pause/cancel/recovery scope: recorded tick-boundary pause/resume in process, preserved cancellation evidence and fresh attempts after crashes (D008.3).
- [x] Select continued independent batch progression and manual retries initially, with shared blockers holding new launches (D008.4).
- [ ] Finalize timeout/lease, shared-blocker, eligibility and recovery/drain contracts (O03; the selected D008 policies remain fixed).
- [x] Select initial live visualization: React scientific dashboards and separate RoR window; interactive 3D inspector later (D011).
- [x] Select retention: preserve recorded data until manual archive/cleanup; insufficient storage holds new launches (D012).
- [x] Complete the policy Q&A and preserve all confirmed decisions.
- [x] Write the implementation review specification with proposed contracts, model coverage, resource budgets, numerical acceptance candidates and delivery gates.
- [x] Verify the implementation HTML, seven policy cases, source/local references and desktop/mobile layout; retain reproducible documentation checks.
- [ ] Resolve/freeze O01–O07 through scoped native/coordinator feasibility and qualification work; no implementation is authorized merely by this backlog.
- [x] Select and exercise a meaningful first scenario: private Daf/Simple2 settled rolling coast with live measurements and controls.

Implementation is underway in [Slice 01](doc/project/slices/slice-01.md). D003 confirms React with a .NET coordinator and local browser delivery first. D004 selects force attribution and core energy validation first, with broader energy validation afterward. D005 selects the environmental foundation first. D006 selects detailed impact windows with every-step accounting and continuous summaries. D007 selects controlled initial conditions followed by a later driven/path-speed approach. D008.1 selects sequential isolated batch execution; D008.2 selects continued capture after required data loss, with incomplete quality and a nonpassing scientific-validation result; D008.3 selects in-process pause/resume, preserved cancellation evidence and fresh attempts after crashes; D008.4 selects continued independent queue progression and manual retries, holding new launches for shared blockers. D009 selects automated scenario-specific validation gates. D010 selects the starter Daf Semi/Simple Test Terrain pilot and preserves the broader downloaded terrain collection for later trials. D011 selects React scientific dashboards and the separate native scene view, with interactive 3D inspection later. D012 selects manual retention and closes the policy Q&A. The version 0.1 specification records proposed instrumentation, environment/initialization contracts, fixture parameters/tolerances, capture byte budgets/triggers and operational details. These remain qualification work rather than achieved measurements. Coupled particle forces/surface interactions remain a later scope decision.

## Implementation slices

- [x] Slice 01: immutable bounded trial contracts, serial isolated source workers and SQLite attempt catalog.
- [x] Slice 01: actual consumed force/contact, momentum and kinetic-work integration observer with CRC aggregate archives.
- [x] Slice 01: physical gravity/density/steady-wind adoption in the pilot generic-drag path; dry-air state metadata.
- [x] Slice 01: React live form/charts/queue, native clock, pause/resume, cancel, retained results and separate retries.
- [x] Slice 01: native source build, accounting/archive checks, real simulation screenshot/video evidence and reproduction scripts.
- [x] Slice 02: force channels, linear core energy/work, initialization/state ports and visible unqualified mass/cohort exchange; scoped native fixture balances.
- [x] Slice 02: native analytical fixtures, repeatability/cost characterization and scoped acceptance profiles; [delivery](doc/project/slices/slice-02.md).
- [x] Slice 03: sparse observer/CRC optimizations, ledger-off with a declared common timing/state probe, native equivalence and fixture accounting regression; [delivery](doc/project/slices/slice-03.md).
- [ ] Meet/resolve the proposed ≤10% total observer overhead gate and characterize larger/multi-actor workloads. Same-build full/off medians are 67.6/22.1 microseconds at 5 m/s (3.059x), with similar 15 m/s results; ledger-off is trial-aware and retains the common probe.
- [ ] Extend nonlinear/shock/hydro/rope storage, external state mutation gateways and calibrated fracture dissipation; current vehicle validation stays NotReady.
- [x] Slice 04: controlled barrier asset and frozen approach/trigger profile; five-repeat 3/5/10 m/s target matrix, dense beam state/parameter records and scoped approach/capture gates; [delivery](doc/project/slices/slice-04.md).
- [x] Slice 04: whole-pilot 2 kHz node/channel/contact/beam windows (2 s pre/4 s post), independent CRC/force/impulse analysis and required-loss recovery checks.
- [x] Slice 05: actual native tensile/compressive yield, tensile strength degradation, beam removal and strength-only protection; independent dry reference checks and bounded verified workbench ledger; [delivery](doc/project/slices/slice-05.md).
- [x] Slice 05: eight fresh native transition runs, exact 400-tick pair prefixes, unchanged three-fixture regression, CRC-valid semantic corruption rejection and image evidence.
- [ ] Qualify later collision-induced strength/removal and physical material energy interpretation. Slice 05 qualifies controlled tick-1 initialization transitions and signed storage bookkeeping; calibrated dissipation and vehicle fracture remain open.
- [ ] Optimize detail memory/drain cost and qualify longer/separated/retriggered windows, larger scenes and barrier observation-off equivalence. Current pilot needs ~782 MiB history, ~3 GiB queue and ~1.55 GB per window; proposed overhead targets remain unmet/unqualified.
- [ ] Later: generalized asset/configuration selection, driven journeys, flight, gusts/particulates, live 3D inspector and comparison/export.
- [ ] Broader operational qualification: coordinator hard-crash/orphan ownership, physical storage exhaustion/holds, workload stress and alternate renderers. Slice 04 qualifies owned-worker abrupt exit/verified-prefix recovery/fresh retry and injected partial-write recovery, not physical disk-full or coordinator orphan recovery.

These slice groupings are implementation sequencing; they do not replace the confirmed decisions or the 14-epic specification. Completed capture is not scientific acceptance.

## Observed maintenance candidates

| Item | Evidence and proposed completion criteria | Status |
| --- | --- | --- |
| CLI `-enter` / preset vehicle entry | CLI writes `cli_preset_veh_enter`, while config-origin spawn checks `diag_preset_veh_enter`. Investigate intended semantics, fix if selected, and verify a launch without the workaround. | Observed; workaround documented; unassigned |
| Runtime asset/localization diagnostics | Baseline logs contain nonfatal font/material/legacy-overlay issues and missing English localization. Triage specific messages and compare visuals before changing assets or code. | Observed; unassigned |
| Portable session tooling | Historical scripts hardcode paths and baseline labels. If selected, parameterize session root, provenance, capture target, and report generation; verify a new independent session. | Procedure documented; tooling unassigned |
| Locked dependency replay | Preserve baseline Conan recipe revisions. If selected, perform and record a fresh configure using the documented lock argument and verify generated profiles. | Lock preserved; replay not yet verified |
| Alternate installed compiler | VS 2026 is present, but only VS 2022/MSVC 19.44 was validated. Test another toolchain only when needed and retain separate evidence. | Unvalidated; unassigned |

## Additional validation when a feature requires it

- [ ] Ground contact, vehicle deformation, crashes, and more than one actor.
- [ ] Aircraft, boats, other terrains/content, and graphics backends.
- [ ] Multiplayer, network configuration, and server interactions.
- [ ] Performance measurements with an explicit workload and repeatable metrics.
- [ ] Suitable regression coverage for the chosen change; the baseline CTest registration contains zero tests.

## Session closeout

Each completed session should update [project-memory.md](project-memory.md), link its evidence/summary, and mark only work that was actually finished. Keep unresolved failures or hypotheses visible. Do not rewrite historical baseline numbers to match a later run.
