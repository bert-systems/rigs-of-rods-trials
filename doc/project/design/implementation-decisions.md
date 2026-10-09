# Implementation decision log

Project: bert-systems/rigs-of-rods-trials. Updated: 2026-10-08.

This is the canonical record of choices confirmed during the implementation Q&A. The [architecture evaluation](trial-platform-architecture-options.md) provides options and recommendations; this log records the user's actual selections. The policy Q&A is complete; unresolved engineering details are identified in the implementation specification.

## D001 — First-release purpose and scientific fidelity

**Confirmed: validated simulation studies.**

Question: What should the first release's physical results be used for?

User response: **A** — validated simulation studies.

The selected goal is to verify force, momentum and energy accounting against known test cases and clearly report model limitations and unexplained residuals.

Implementation implications:

- Define canonical analytical/discrete reference fixtures and independent balance checks.
- Record measured quantities, supported model coverage, estimates and unclosed residuals explicitly.
- Select scenario-specific numerical tolerances and validation gates in the detailed specification.
- Calibrate selected assets as coverage expands; this decision does not establish existing runtime or real-world accuracy.

Still open for D001: exact validation fixtures/error bounds and supported energy models. D002 selects the pilot domain, D003 the UI/coordinator boundary, D004 the accounting sequence and D005 the initial environmental scope. Detailed contracts and delivery policies remain open.

## D002 — First end-to-end milestone

**Confirmed: ground impacts first.**

Question: What should the first implementation milestone demonstrate end to end?

User response: **A** — controlled vehicle-to-barrier trials, supported by free-fall and spring/damper validation fixtures. Flight follows afterward.

Implementation implications:

- Prioritize a pinned ground vehicle and controlled barrier setup, with approach-state verification and impact outcome capture.
- Include free-fall and spring/damper reference fixtures for validating momentum, work and energy accounting.
- Exercise trial definition, setup, execution, native instrumentation, durable capture and result review in the same milestone.
- Preserve the architecture's path to atmospheric flight; flight/gust demonstration is a later milestone.

Still open: exact vehicle/fixture assets, speeds, bodies, model coverage, error tolerances and milestone acceptance.

## D003 — Workbench UI and deployment boundary

**Confirmed: React workbench with a .NET coordinator, local browser first.**

Question: Which workbench interface should we implement?

User response: **A** — React plus a .NET coordinator: a local browser interface for trial definition, live dashboards and result comparisons. The .NET backend launches and manages RoR; a desktop wrapper can follow later.

Implementation implications:

- Use React for the workbench and a UI-independent .NET coordinator for trial execution and local process/filesystem integration.
- Keep force/energy instrumentation in the native C++ worker.
- Make the first UI available through a local browser with configuration, live status and result comparison views.
- Preserve a path to a desktop wrapper; including that wrapper in the first milestone has not been requested.
- Define command, reduced live telemetry and durable-result boundaries in the detailed specification. Specific frameworks, versions, ports, authentication and packaging remain to be settled.

The Q&A's A selection corresponds to the architecture report's Option B. Option letters are question-local; the selected technology names above are authoritative.

Still open: detailed frontend/backend contracts, charting approach, packaging and deployment/lifecycle policy.

## D004 — Force attribution and energy validation sequence

**Confirmed: complete force attribution and core energy validation first; expand energy coverage afterward.**

Question: How should we stage force and energy validation?

User response: **A** — first validate force vectors, impulses, momentum, kinetic/gravitational energy, spring storage and damping/friction work. Record plastic deformation and breakage immediately, with clearly labeled energy estimates and unexplained residuals; validate those energy models afterward.

Implementation implications:

- Target attribution of the forces actually applied by the solver, with coherent generated/consumed epochs, identities and integration state.
- Use the ground-impact and analytical reference fixtures to validate force/impulse/momentum balances and the core energy terms before expanding energy-model claims.
- Capture plastic deformation and breakage transitions from the start. Label available energy estimates and unclosed terms explicitly; a captured transition does not establish validated material or fracture energy.
- Preserve unexplained residuals rather than reclassifying them as absorbed energy.
- Expand validation of nonlinear deformation, breakage and drivetrain energy after the first end-to-end milestone. The full instrumentation pipeline remains the project goal.

Still open: exact channel definitions and subsystem coverage, supported estimation methods, error tolerances and acceptance gates. This decision selects sequencing; it does not assert that any instrumentation or energy model has already been implemented or validated.

## D005 — Initial environmental scope

**Confirmed: environmental foundation first.**

Question: What environmental scope belongs in the first ground-impact milestone?

User response: **A** — configurable gravity, dry-air temperature/density and steady wind, applied consistently to the relevant drag models. Add gusts, turbulence and particulate exposure in subsequent milestones.

Implementation implications:

- Establish a coherent effective environment configuration for the ground-impact pilot, including gravity, dry-air temperature/density and a steady ambient-wind vector.
- Apply the environment consistently to the relevant physical drag models, and record which models consume the configuration.
- Include environment configuration/application evidence and reference validation in the first milestone; a visual weather setting alone does not establish a physical environment.
- Stage structured wind, including gusts/turbulence, and particulate transport/exposure after the foundation milestone.
- Keep particle forces and surface interactions as a separate unresolved scope decision. Selecting the foundation does not select a coupled particulate model.

Still open: supported gravity/atmosphere ranges, parameter relationships and units, specific drag adapters, validation tolerances, later structured-wind/particle details and their acceptance gates. The selection is implementation scope, not a claim of existing physical wind support or validated environment behavior.

## D006 — Default recording profile

**Confirmed: detailed impact windows with every-step accounting and continuous summaries.**

Question: Which default recording profile should we use?

User response: **A** — calculate force/energy balances every physics step, retain continuous summaries around 200 Hz, and capture configured node/contact/beam detail at 2 kHz around impact, initially 2 seconds before and 4 seconds after. Refresh the live dashboard at roughly 10–20 updates per second.

Implementation implications:

- Separate native accounting frequency, retained raw detail, retained summaries and UI refresh cadence.
- Keep force/energy accounting on every active physics step even outside detailed capture windows.
- Maintain the configured pre-impact history in a bounded buffer and retain the trigger window with its tick/epoch identity.
- Record continuous summaries and critical transitions; summaries must retain relevant peaks and integrated balances before downsampling.
- Use reduced live updates for the dashboard, with durable results as the authoritative analysis record.
- Treat approximately 200 Hz summaries, 2 kHz configured detail, a 2-second pre/4-second post-impact window and 10–20 Hz UI refresh as selected starting targets to verify through profiling.

Still open: the configured nodes/contacts/beams and channels, trigger definition, multiple/overlapping impacts, byte/storage budgets, buffer sizing and long-run retention. D008.2 selects behavior after required measurement loss. This selection does not establish achieved throughput or runtime performance. Continuous full-rate capture can be evaluated as an additional bounded audit mode; it is not the selected default.

## D007 — Impact approach and later journey control

**Confirmed: controlled initial conditions first, then a driven approach later.**

Question: How should the first vehicle-impact trials reach the barrier?

User response: **A then later B.** First settle the vehicle, initialize its configured pose and velocity, and let physics carry it into a fixed barrier while verifying actual approach speed/alignment. Later add throttle, braking and steering through a path/speed controller to reach desired impact conditions.

Implementation implications:

- Make controlled vehicle initial conditions and a fixed barrier the first impact approach mode.
- Define settling, initialization and measurement-start boundaries explicitly, with coherent node/body/wheel state and a recorded realized initial state.
- Distinguish requested launch conditions from observed approach conditions; evaluate actual speed/alignment against scenario-specific acceptance limits.
- Account explicitly for initialization changes at the measurement boundary; do not impose continuous velocity corrections during the observed coast/impact.
- Plan the driven approach as a later milestone, including journey/path and speed control, control-command provenance, controller validation and drivetrain-work accounting.
- Preserve both approach modes in the trial configuration model. The later driven mode is explicitly selected in the roadmap, rather than merely an optional recommendation.

Still open: exact vehicle/terrain/barrier assets, settling criteria, coherent initialization mechanics, launch distances/speeds, observation gates, approach tolerances and driven-controller design. The choice does not establish an existing complete reset or controller implementation.

## D008 — Trial execution and operational policies

### D008.1 — Initial batch execution model

**Confirmed: sequential, isolated runs.**

Question: How should the first release execute batches of trials?

User response: **A** — queue sweeps and repeats, running one trial at a time. Each trial gets a fresh RoR process, private configuration and a separate results directory. Parallel execution can follow later.

Implementation implications:

- Provide a persistent queue for configured sweeps/repeats and individual trial status tracking.
- Limit initial execution to one active native trial worker.
- Launch the pinned source-built executable in a fresh process for each trial with private configuration and separate results/provenance.
- Preserve trial definition, realized configuration and worker identity for review.
- Keep parallel isolated workers as a later option, subject to resource/capture profiling and coordinator changes; this answer does not require parallel execution in the first release.

D008.2 below selects measurement-loss behavior. A fresh process improves isolation but does not by itself establish reproducibility or validated initial state.

### D008.2 — Required measurement-loss policy

**Confirmed: continue collecting and mark the result incomplete.**

Question: What should happen if required measurement data is lost?

User response: **B** — continue collecting, preserve subsequent observations for inspection and mark the result incomplete, while preventing the trial from passing scientific validation.

This covers missing accounting steps, critical events or required impact-window records. Live-dashboard refresh coalescing is independent of the authoritative measurement archive.

Implementation implications:

- Continue the affected trial after measurement loss and retain subsequent observations that can still be captured.
- Make incomplete capture quality persistent for that attempt; resumed delivery does not erase an earlier gap.
- Record gap ranges, affected streams/ticks and known counts/causes alongside retained data and diagnostics.
- Track execution outcome, capture quality and scientific validation independently: a simulation may finish normally while its required capture remains incomplete.
- Prevent an attempt with required measurement loss from passing scientific validation. Show retained observations with their coverage limits.
- Preserve missing data explicitly in force/energy analysis; do not silently fill gaps or treat unsupported balances across a gap as validated.

D008.3 below selects initial pause/cancel/crash recovery scope. Detailed gap encoding, resource-exhaustion behavior and per-stream required coverage belong in the implementation specification. Continuing after measurement loss does not establish recoverability after an engine/process crash.

### D008.3 — Initial pause/cancel and crash recovery scope

**Confirmed: in-process pause/resume and fresh attempts after crashes.**

Question: What pause and recovery capability should the first release provide?

User response: **A** — pause at a recorded physics-tick boundary and resume within the running process. Cancellation preserves partial results; crashed trials can be rerun as separate attempts.

Implementation implications:

- Provide acknowledged pause/resume at a native physics-tick boundary, preserving simulation state in the active process.
- Record pause/resume events and distinguish paused wall time from advancing simulation time and measurement ticks.
- Preserve partial archives and diagnostics on cancellation or crash, with explicit terminal execution/capture states.
- Rerun a crashed trial through a fresh attempt and worker, preserving the prior attempt's identity and evidence.
- Exclude durable mid-trial state checkpoints and process-crash state restoration from the first release.
- Keep D008.2 unchanged: required measurement loss alone selects continued capture with incomplete quality, rather than restarting the attempt.

D008.4 below selects initial retries and queue progression. Timeout/lease rules, cancellation acknowledgement/drain mechanics and crash-archive recovery details remain specification work. Re-running a trial is a new attempt; resuming a deliberate pause stays within the existing active process.

### D008.4 — Batch progression and retries

**Confirmed: continue independent queued trials, with manual retries initially.**

Question: How should a batch react to a failed or incomplete attempt?

User response: **A** — preserve each attempt's results and failure status, continue independent queued trials, and provide manual retries initially. Hold new launches when a shared problem such as unavailable storage blocks execution.

Implementation implications:

- An individual failed/incomplete attempt does not automatically hold the whole batch after it finishes.
- Continue eligible independent trials in the sequential queue while keeping earlier outcomes and partial evidence visible.
- Provide manual retry as a distinct new attempt linked to the prior attempt; initial execution has no automatic retries.
- Hold new launches on a shared blocking problem and show the queue's blocking reason. Define recovery/clearing rules in the coordinator specification.
- Preserve D008.2 for an active trial: required measurement loss alone selects continued observation and incomplete/nonpassing quality.
- Keep execution, queue progression, capture quality and scientific validation as separate states.

Still open for D008: timeout/lease values, detection/clearing of shared blockers, dependency/eligibility rules, cancellation drain/acknowledgement and crash-archive recovery mechanics. These are detailed contracts to specify within the confirmed operational policy.

## D009 — Scientific validation approval

**Confirmed: automated scenario-specific checks.**

Question: How should scientific validation be approved?

User response: **A** — require reference-fixture checks, force/momentum/energy balances, repeatability checks and complete required capture to pass defined tolerances. Show failures and model limitations in results. Numerical tolerances are to be defined in the specification for each fixture and supported model.

Implementation implications:

- Define automated fixture/balance/repeatability/capture checks with versioned scenario-specific acceptance rules.
- Use independent analytical or discrete reference expectations where available; define absolute and relative tolerances with meaningful reference scales.
- Record expected values, observations, residuals, thresholds, coverage and each check's outcome so a pass/failure is reviewable.
- Scope a passing validation result to the declared scenario, measurement quantities and supported models. Estimated/unclosed energy terms and uncalibrated asset behavior remain visible.
- Retain D004's staged energy validation: nonlinear deformation/breakage/drivetrain coverage expands later, rather than claiming an initial pass validates all models.
- Apply D008.2: required measurement gaps prevent that attempt from passing scientific validation even if execution completes and later observations are retained.

Still open: numerical tolerance values, exact fixture definitions/parameters, repeatability envelopes and run counts, evidence thresholds and build/performance gates. This decision selects approval mechanics; it does not establish current physical accuracy or permit thresholds to be silently relaxed to obtain a pass.

## D010 — First pilot assets and reference fixtures

**Confirmed: start with the existing Daf Semi and Simple Test Terrain.**

Question: Which assets should anchor the first impact pilot?

User response: **Start with A**, with permission to inspect the downloaded terrain collection; starting simple is acceptable.

Selected pilot:

- Versioned Daf Semi: content/dafsemi/b6b0UID-semi.truck.
- Versioned Simple Test Terrain: content/simple2-terrain/simple2.terrn2.
- A controlled fixed barrier and purpose-built free-fall and spring/damper reference fixtures, to be implemented as part of the pilot.

Use the pinned content revision and record resolved asset identities/hashes in trial provenance. The source-built baseline exercised driving with this truck/terrain, not impact or physical-accuracy validation.

Local collection inspection:

- Found the additional packages at D:\Rigs of Rods\content\Terrains, outside the Git fork.
- Read 23 ZIP package directories and 75 terrain-definition entries: 44 .terrn2 and 31 legacy .terrn. Compressed total: 772,194,711 bytes. The entries include duplicate legacy/current variants and are not 75 independently validated terrains.
- Examples include Pines Proving Grounds, Top Gear Test Track, Auriga Proving Grounds, N-Labs Testing Facility and Sweden Airport.
- Saved the [terrain inventory](../research/2026-10-08/terrain-inventory.md) and machine-readable metadata. No assets were extracted, modified or loaded; catalog completeness, compatibility and physical suitability are unverified.
- Retain the extra terrains for later scenario selection; the first pilot remains Simple Test Terrain.

Still open: barrier geometry/contact configuration, fixture definitions and parameters, launch speeds/distances, measured approach tolerances and scenario-specific acceptance gates. Inventorying asset data does not use installed-game binaries as source-build proof.

## D011 — Initial live visualization

**Confirmed: scientific dashboards plus the separate RoR window; interactive 3D inspection later.**

Question: What should the first release provide for live visualization?

User response: **A** — show force components, momentum, energy, environment, events and capture health in React alongside the separate native RoR simulation window. Add an interactive 3D inspector later.

Implementation implications:

- Provide React panels/charts for configured force components, momentum/energy balances, environment conditions, trial events and capture health.
- Retain the source-built native simulation window as the initial live scene view.
- Align dashboard values with observation ticks/epochs and show capture coverage, stale/disconnected state, estimates and model limitations.
- Keep the selected 10–20 Hz UI cadence separate from every-step accounting and archived high-detail impact traces.
- Stage the synchronized scientific 3D node/beam/contact inspector after the first release, including picking, vector arrows and deformation inspection.
- Preserve observation identities and immutable snapshots so later scene inspection can use the same telemetry/archive contracts.

Still open: exact dashboard layout/charts, initial channel filters, evidence video timing policy and the later 3D renderer/interaction design. This choice does not request native-renderer embedding or live game-video streaming inside the browser.

## D012 — Retention and cleanup

**Confirmed: preserve recorded data until manual cleanup.**

Question: How should recorded data be retained?

User response: **A** — keep recorded telemetry, reports, images and video until explicitly archived or deleted. Hold new launches when available storage cannot meet the capture budget. Historical build/run evidence remains protected.

Implementation implications:

- Retain completed, failed and incomplete attempt artifacts by default, including partial archives and diagnostics.
- Provide explicit archive/cleanup actions; do not implement automatic age-based or space-based deletion as the default.
- Preflight available storage against the configured capture reservation/budget and hold new launches when it is insufficient.
- Retain D008.2 for an already active trial if required measurements are lost; retain explicit gaps and incomplete quality.
- Preserve the original source-build proof and protected/pinned evidence independently of ordinary trial cleanup.

Detailed resource budgeting, archive/cleanup manifests and lifecycle mechanics belong in the implementation specification.

## Decision status and specification work

| ID | Topic | Status |
| --- | --- | --- |
| D002 | First pilot domain and canonical scenarios | Confirmed: ground impacts with reference fixtures; flight later |
| D003 | Workbench UI and deployment boundary | Confirmed: React + .NET coordinator, local browser first |
| D004 | Required force/energy metrics and supported model coverage | Confirmed sequence: force attribution/core energy first; broader energy validation later; detailed coverage open |
| D005 | Atmosphere/wind/particulate scope | Confirmed initial scope: gravity/dry air/steady wind; gusts/turbulence/exposure later; coupled particles open |
| D006 | Capture profiles, storage budgets and live status | Confirmed: impact windows/every-step accounting/continuous summaries; rates are profiling targets; byte budgets open |
| D007 | Initial state, path/controller and outcome tolerances | Confirmed sequence: controlled initial conditions first, driven/path-speed approach later; exact assets/tolerances open |
| D008 | Execution, pause/cancel/recovery and data-loss policies | D008.1–4 confirmed: serial isolation, continued incomplete capture, in-process pause, manual retries and continued independent queue progression; detailed contracts open |
| D009 | Validation thresholds, milestones and implementation sequencing | Confirmed: automated checks per scenario; exact numerical thresholds/fixture parameters remain open |
| D010 | First pilot assets and reference-fixture package | Confirmed: Daf Semi/Simple Test Terrain plus controlled barrier and analytical reference fixtures; exact fixture parameters open |
| D011 | Initial live dashboard and scientific scene-view scope | Confirmed: React scientific dashboards plus separate RoR view; interactive 3D inspector later |
| D012 | Data retention and cleanup policy | Confirmed: preserve until manual archive/cleanup; insufficient storage holds new launches |

The policy Q&A is complete. Confirmed choices above govern implementation direction; fixture parameters, numerical tolerances, schema/protocol details and resource budgets are engineering specification work. Proposed defaults must remain labeled and must be verified before acceptance claims. See the [implementation specification](trial-platform-implementation-spec.md) and [HTML review copy](../reports/trial-implementation-spec-2026-10-08.html) for the consolidated baseline and proposed engineering contracts. No engine or launcher implementation has started.

## Session record

2026-10-08: began one-topic-at-a-time Q&A; recorded D001 from the user's explicit answer. Source remains e85535569102b6251849af574026984e3213b3f4; starter content remains 34fefdd126784bf87b068fc283f812525d159dd7. Existing local documentation changes were preserved. This turn updates documentation only; no engine implementation, build, commit or push.

2026-10-08: recorded D002 from the next explicit A response. The first milestone is ground impact plus reference fixtures; flight follows afterward. No engine implementation, build, commit or push.

2026-10-08: recorded D003 from the explicit A response to the workbench question. React with a .NET coordinator is selected; local browser delivery comes first and a desktop wrapper remains a later option. No engine implementation, build, commit or push.

2026-10-08: recorded D004 from the explicit A response to the force/energy sequence question. Complete force attribution and core energy validation come first, while deformation/breakage transitions and qualified estimates are captured immediately. Broader energy validation follows; exact definitions and acceptance remain open. No engine implementation, build, commit or push.

2026-10-08: recorded D005 from the explicit A response to initial environmental scope. Gravity, dry-air temperature/density and steady wind form the first milestone; gusts, turbulence and particulate exposure follow later. Coupled particle forces and surface interactions remain open. No engine implementation, build, commit or push.

2026-10-08: recorded D006 from the explicit A response to recording profiles. Every-step accounting, continuous summaries and high-detail impact windows are the selected default, with rates/windows subject to profiling. Byte budgets, triggers and capture-loss policy remain open. No engine implementation, build, commit or push.

2026-10-08: recorded D007 from the explicit A then later B response. Controlled initial conditions lead the first impact milestone; a driven approach with path/speed control is selected for later delivery. Exact initialization contracts and acceptance remain open. No engine implementation, build, commit or push.

2026-10-08: recorded D008.1 from the explicit A response to batch execution. The first release queues sequential trials with a fresh native process, private configuration and separate results per trial. Parallel execution remains a later option; measurement-loss and other operational policies remain open. No engine implementation, build, commit or push.

2026-10-08: recorded D008.2 from the explicit B response to required measurement loss. Continue capturing later observations, mark the attempt incomplete and prevent scientific validation from passing. Execution outcome and capture/validation quality remain distinct. Pause/cancel and crash recovery remain open. No engine implementation, build, commit or push.

2026-10-08: recorded D008.3 from the explicit A response to pause/recovery scope. First-release pause/resume stays within the active process, cancellation preserves partial results and crashed trials can be rerun as new attempts. Durable checkpoint restoration is outside the first release. Detailed retry/queue rules remain open. No engine implementation, build, commit or push.

2026-10-08: recorded D010 from the explicit start with A response. Inspected the downloaded terrain collection read-only: 23 packages, 44 modern and 31 legacy definition entries, outside the fork. The first pilot stays with the pinned starter truck/terrain; no new simulation, asset modification, build, engine implementation, commit or push.

2026-10-08: recorded D009 from the explicit A response to validation approval. Automated scenario-specific fixture/balance/repeatability/capture checks gate scoped validation results; exact tolerances and reference parameters belong in the detailed specification. No engine implementation, build, commit or push.

2026-10-08: recorded D008.4 from the explicit A response to batch progression. Independent queued trials continue after individual failures/incomplete attempts; retries are manual initially and shared blocking problems hold new launches. Live visualization scope is the next question. No engine implementation, build, commit or push.

2026-10-08: recorded D011 from the explicit A response to live visualization. React scientific dashboards and a separate source-built RoR window come first; a synchronized interactive scientific 3D inspector follows later. Data retention is the final policy question before specification consolidation. No engine implementation, build, commit or push.

2026-10-08: recorded D012 from the explicit A response to retention. Preserve recorded data until explicit manual archive/cleanup; insufficient storage holds new launches. This closes the policy Q&A. Consolidating a review specification and HTML companion is documentation work; no engine implementation, build, commit or push.

2026-10-08: consolidated all confirmed choices in the [implementation review specification](trial-platform-implementation-spec.md) and [HTML companion](../reports/trial-implementation-spec-2026-10-08.html). Report QA passed; proposed engineering defaults remain qualified and unimplemented. No build, engine/launcher implementation, commit or push.

Related records: [project memory](../../../project-memory.md), [TODO](../../../todo.md), and [platform research](../../../platform.md).
