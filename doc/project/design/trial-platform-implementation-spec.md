# Trial platform implementation specification

Version: **0.1 — review baseline**, 2026-10-08. Project: **bert-systems/rigs-of-rods-trials**. This consolidates the completed [implementation Q&A](implementation-decisions.md); it does not describe implemented software or validated physical accuracy.

[HTML review copy](../reports/trial-implementation-spec-2026-10-08.html). [Architecture evaluation](trial-platform-architecture-options.md). [Platform evidence](../../../platform.md).

## 1. Authority and agreed delivery scope

**Confirmed requirements** come from D001–D012, including the four D008 operational selections. **Proposed engineering defaults** in this document make the design concrete for review; they are not additional user selections or measured performance. **Acceptance prerequisites** identify work that must be completed before a build/run can claim the specified behavior. Future implementation tasks should follow the confirmed requirements and resolve/freeze the appropriate defaults through source inspection and meaningful validation.

| Area | Confirmed direction |
| --- | --- |
| Scientific purpose | Validated simulation studies with scoped model coverage and explicit residuals |
| First milestone | Controlled ground impacts plus free-fall and spring/damper reference fixtures |
| Workbench | React, local browser first, with a UI-independent .NET coordinator |
| Native measurements | Complete applied-force attribution; core energy validation first; capture deformation/breakage transitions immediately |
| Environment | Configurable gravity, dry-air temperature/density and steady wind with coherent relevant drag adoption |
| Capture | Every-step accounting; approximately 200 Hz continuous summaries; configured 2 kHz detail, initially 2 s before/4 s after impact; UI 10–20 Hz |
| Approach | Controlled initialized/coasting vehicle first; driven path/speed approach later |
| Execution | Sequential queued sweeps/repeats; fresh RoR process/private profile/results per attempt |
| Required data loss | Continue observation; mark capture incomplete persistently; prevent a scientific validation pass |
| Pause/cancel/crash | Tick-boundary in-process pause/resume; preserve partial cancellation/crash evidence; rerun as a new attempt |
| Batch/retry | Continue eligible independent trials after individual failures; manual retries initially; shared blockers hold new launches |
| Validation | Automated, scenario-specific reference/balance/repeatability/capture checks |
| Pilot content | Pinned Daf Semi and Simple Test Terrain, controlled fixed barrier and purpose-built analytical fixtures |
| Live view | React scientific dashboards alongside the separate native RoR window; interactive 3D inspector later |
| Retention | Preserve recorded data until explicit manual archive/cleanup; insufficient storage holds new launches |

Flight, broader constitutive/drivetrain energy validation, structured wind/particulate exposure, driven journeys and interactive scientific 3D inspection follow the first milestone. Parallel/remote/headless workers and a desktop wrapper remain later options. Coupled particle forces, surface interactions and CFD require their own scope and validation decisions. Durable process-crash checkpoint restoration is outside the first release.

The canonical engine remains at `e85535569102b6251849af574026984e3213b3f4` and versioned starter content at `34fefdd126784bf87b068fc283f812525d159dd7` at this review. Recheck identities at implementation time; existing local documentation changes remain uncommitted. The original source-build proof is protected.

## 2. Components, responsibilities and deployment

~~~mermaid
flowchart LR
  UI["React workbench"] -->|"local commands"|Coordinator[".NET coordinator"]
  Coordinator -->|"acknowledged native commands"|Worker["C++ RoR trial worker"]
  Worker -->|"reduced snapshots"|Coordinator
  Worker -->|"durable chunks"|Archive["Retained artifacts"]
  Archive -->Analysis["Analysis / validation"]
  Analysis -->Coordinator
  Coordinator -->|"live state / results"|UI
  Worker -->Scene["Separate native scene window"]
~~~

| Component | Owns | Boundary |
| --- | --- | --- |
| Native trial adapter | Capability handshake, controlled setup, tick commands, requested/resolved/applied/observed state | Process/profile isolation does not replace state verification |
| Native observer/reducers | Applied force attribution, integration/state events, impulses/work, supported energy and capture health | Preserve solver ordering initially; calculations are independent of UI speed |
| Environment service/adapters | Effective physical inputs and subsystem adoption evidence | Uniform field initially; record the values actually used |
| Native recorder | Pre-trigger history, selected raw detail, continuous summaries, committed chunks and loss counters | Bounded memory; no file/network operations in force callbacks |
| .NET coordinator | Immutable experiment revisions, expansion, sequential queue, process identity, status/events, catalog and API | Commands express intent; the native worker acknowledges actual application |
| Analysis/validation | Archive-based balances, model coverage, fixture checks, repeatability and comparisons | A live display is not the authoritative measurement record |
| React workbench | Authoring, queue control, scientific dashboards, result inspection, manual retry/archive | Native scene remains a separate window initially |

**Proposed organization:** `source/main/trials/` for native modules, `apps/trials/coordinator/` for the .NET host, `apps/trials/workbench/` for React, `tests/trials/` for independent fixtures/contract tests, and `doc/project/design/` for versioned design/contracts. These are future directories, not existing implementations.

**Proposed transport/storage choices:** local Windows named pipes for acknowledged native control and reduced status; ASP.NET Core HTTP/SignalR for browser commands/live projections; SQLite for coordinator-owned metadata/events; self-describing binary raw chunks with an offline columnar export. Shared-memory raw transport is deferred until a measured bottleneck warrants it. The coordinator initially runs as one modular local application.

Bind the browser service to loopback, serve the workbench from the same origin, validate origins/session credentials and expose typed trial/asset IDs rather than arbitrary shell commands. Use a private pipe/session identity and verify attempt/build/schema/PID/start-time handshake. Detailed access-control and wire layouts are to be frozen in E01.

Read-only inspection found .NET SDKs **10.0.103 and 10.0.203** installed. The proposed host target is .NET 10 with a pinned SDK/dependency lock at implementation time; no framework was installed or built for this specification. Keep the verified native VS 2022 x64 toolchain until a deliberate toolchain validation changes it.

## 3. Experiment, attempt and result contracts

An experiment is an immutable versioned definition plus named sweeps/repeats. Expansion produces a realized trial configuration. Every execution/retry has a new attempt ID and private profile/archive directory. Editing an experiment creates a revision; it must not change an active attempt.

| Contract group | Required information |
| --- | --- |
| Identity | Experiment/revision/trial/attempt IDs, parent retry ID, definition hash, schema/observer/validator versions |
| Build/content | Source commit and dirty-state record, executable/module hashes, content revision/archive hashes, resolved terrain/vehicle GUIDs and dependencies |
| Scene | Terrain, barrier geometry/material/transform, vehicle configuration/topology, node cohort, physical surface settings |
| Initialization | Requested pose/velocity, settling rules, wheel/rotating-state policy, applied initialization events and realized state |
| Environment | Requested and effective gravity/temperature/density/wind, field version, samples and adapter adoption |
| Observation | Channels/cohorts/masks, actual step duration, epochs, retention/trigger profile, required streams and budgets |
| Completion/acceptance | Scientific window, approach gates, end conditions, timeouts, fixture tolerances, required model coverage |
| Evidence | Chunk manifests, counters/gaps, summaries/events, logs, images/video/time mapping and hashes |
| Result | Execution outcome, capture quality, validation scope/outcomes, calibration/model badges and archive availability |

**Proposed authoring example — explanatory, not an executable configuration:**

~~~json
{
  "schemaVersion": "proposal-0.1",
  "scenarioId": "daf-fixed-barrier-v1",
  "vehicleId": "b6b0UID-semi.truck",
  "terrainId": "simple2.terrn2",
  "initialStatePreset": "settled-coast-v1",
  "launchSpeedMps": 5.0,
  "environment": {
    "gravityYMps2": -9.81,
    "airTemperatureK": 288.15,
    "airDensityKgM3": 1.225,
    "windWorldMps": [0.0, 0.0, 0.0]
  },
  "captureProfileId": "impact-window-v1",
  "repeats": 5
}
~~~

The implementation must reject unsupported/missing assets and configuration rather than accept a fallback as the requested trial. Surface/material and asset hashes matter as much as visible scenery. The downloaded collection is at `D:\Rigs of Rods\content\Terrains` outside the fork: [23 packages, 44 modern and 31 legacy terrain-definition entries](../research/2026-10-08/terrain-inventory.md). These are available candidates, including paired variants, not loaded/calibrated terrains.

## 4. Execution, commands and quality states

The lifecycle is: draft → expanded/queued → preflight → launch/handshake → resolve scene → settle/initialize → verify realized state → observe/run → finalize/archive → analyze/validate. Pause is an acknowledged running-process state; cancellation/crash have terminal execution outcomes. Capturing/validation are independent state axes.

~~~mermaid
flowchart LR
  Loss["Required measurement gap"] -->Continue["Continue current trial"]
  Continue -->Quality["Capture remains incomplete"]
  Quality -->Validation["Validation cannot pass"]
  Finish["Attempt finishes"] -->Queue["Next independent trial"]
  Blocker["Shared blocking problem"] -->Hold["Hold new launches"]
  Crash["Process crash"] -->Retry["Manual retry / new attempt"]
~~~

| Condition | Active trial | Capture/validation | Queue/retry |
| --- | --- | --- | --- |
| Required measurement gap | Continue observation where possible | Persistent incomplete quality; explicit gaps; cannot pass | After finish, next eligible independent trial |
| Dashboard disconnect | Physics/capture continue independently | UI stale state; archive counters determine actual quality | Coordinator owns the queue |
| Deliberate pause | Pause at a safe physics boundary; preserve process state | Pause event; no invented advancing physics samples | Active attempt retains its slot |
| Cancel | Acknowledge, stop and finalize recoverable evidence | Cancelled execution; preserve partial data/diagnostics | Continue eligible queue; rerun is a new attempt |
| Native crash | Reconcile PID/start time and recover valid chunk prefixes | Failed execution; partial/unavailable evidence marked | Manual retry creates a fresh attempt |
| Validation failure | Preserve execution outcome and records | Failed scoped check with thresholds/residuals | Continue independent trials |
| Shared storage/worker blocker | Existing measurement-loss policy still applies | Preserve known health/errors | Hold new launches and display reason |
| Insufficient preflight storage | Keep trial queued/blocked | No claim that an attempt ran | Resume eligibility once the blocker clears |

**Proposed native envelope:** protocol version, session/attempt/build/schema identity, request ID, monotonic command sequence, target tick/boundary, operation and typed payload. ACKs distinguish accepted, rejected and applied, with applied epoch and resolved values. Duplicate request IDs return the recorded result rather than repeat a physical mutation. Capability mismatches fail preflight.

Only acknowledged setup/control operations may mutate the trial. Initial accepted studies hold environment and scenario definition fixed during observation. Pause/resume/cancel are recorded; later driven-control commands receive the same timing/provenance rules. The browser never directly drives a mutable force accumulator.

**Proposed timeout defaults:** 120 s startup/asset-resolution budget, 30 s settling budget, 60 s simulation-time pilot cap and 300 s wall-time cap, configurable per revision. Pause excludes the ordinary simulation/wall progress timers but has a separate explicit idle/lease policy. A suggested 2 s heartbeat/10 s suspected-disconnect interval is for detection, not proof of worker failure. Reconnection reconciles worker identity and durable state. Coordinator-loss stop/drain at a safe boundary is a proposed lease action, not a confirmed policy or existing feature; freeze and failure-test it before enabling unattended trials.

## 5. Native force and energy instrumentation

### Timing and mutation coverage

The inspected solver integrates nodes before many later force passes. CalcNodes adds ground/object contact, consumes forces, integrates, resets to gravity, and generates drag/water terms for later use. Actor passes then generate other forces; inter-actor passes follow task barriers. Track **generated epoch, actual consumed integration ID and evaluation state**. Do not relabel a frame-level force getter as a complete waveform.

Observe the actual final vectors applied by each write/add/replace/reset/transfer operation. Maintain channel attribution beside the real accumulator and reseed/transfer it in the same branch. Capture pre/post mass/velocity/position and direct state changes. Rope velocity/position copies, force transfer/clear, cached terms, wake/reset/spawn and topology changes require explicit records. Publish coherent snapshots after the relevant barriers, while preserving the earlier node/phase timing.

Actor/job-owned preallocated buffers feed a stable barrier merge. Cross-actor records use task-owned scratch with audited ownership. Callbacks perform no allocation, file flush, formatted logging, database/browser/.NET calls or waits. Off mode must preserve the original force operations and random-draw behavior; observation equivalence and overhead tests are acceptance prerequisites.

| Channel/model | First-milestone requirement | Energy interpretation |
| --- | --- | --- |
| Gravity | Actual consumed nodal contribution and effective field | Potential/work in the declared uniform field |
| Beam elastic/damping | Final applied endpoint vectors, effective parameters, generated/consumed state | Validate linear storage/damping fixtures first |
| Contact normal/friction | Branch and actual node applications; stable object/feature IDs, relative motion and material | Signed contact work; dissipative interpretation only for supported branches |
| Plastic/break/detach | Parameter/topology transitions and actual final force; cascades | Qualified transition estimates/unclosed terms; broader validation later |
| Wheel/drive/brake/actuator | Attribute all contributions active in the chosen pilot; explicit disabled/inactive status | Broader rotating/drivetrain energy validation later |
| Aero/fluid/propulsion | Attribute any active contribution and environment adoption | Validate initial relevant dry-drag work; other enabled models require declared coverage |
| Constraints/links/artificial forces | Transfers/replacements, reactions and state corrections | Boundary/state ports; unsupported models remain explicit |
| Uninstrumented/unknown | Visible coverage gap; no invented attribution | Required unknown coverage blocks a scoped validation pass |

A normalized contact identity must preserve actual applications, including barycentric node distributions, without double-counting one interaction in cohort totals. Track resultant peak norm, node/contact peak, normal/tangential components and duration separately. Independent component maxima at different ticks do not form an observed peak vector.

### Measurement boundary and balances

Use SI units, recorded native world axes with Y up, explicit cohort membership/mass/topology and a fixed reference/datum. Record any body-frame transform rather than assume heading. Node kinetic energy already includes the motion of those wheel/deforming nodes; adding another rigid-body rotational term for the same mass would double-count it. Internal drivetrain reservoirs outside node state require separate coverage.

~~~text
p = sum(m_i v_i)
K = sum(0.5 m_i |v_i|^2)
x_COM = sum(m_i x_i) / sum(m_i)

J_channel = F_channel_consumed * dt
W_channel = v_mid dot J_channel
v_mid = 0.5 (v_before + v_after)

For fixed mass, J_actual = m (v_after - v_before)
Delta K = v_mid dot J_actual
~~~

Archive the actual native integration factor/precision. Channel impulse from F·dt and actual m·Δv can differ through rounding, mass/state mutation or an integration branch; preserve that residual. The midpoint work identity is an accounting identity, not a change to the integrator.

Maintain two related checks: **kinetic update closure** against all actually consumed channels, and **mechanical storage/work closure** for declared supported models. When gravitational/elastic storage is included on the energy side, do not also count the same conservative contribution as independent external energy input. Direct state/mass changes and fluxes have explicit ports. Contact work is not automatically heat; removed beam storage is not automatically fracture energy.

Report signed absolute residuals and relative residuals with declared nonzero scales/absolute floors. Keep supported, estimated and unclosed terms separate. Missing data makes an interval's balance unavailable; later retained samples do not silently reconstruct it. Ambient drag uses u = v − wind and F·v = F·u + F·wind where that model decomposition is supported, so prescribed wind can supply vehicle energy.

## 6. Environment and controlled initial conditions

A versioned uniform dry environment initially provides vertical gravity, air temperature/density and world wind velocity. Each relevant physical adapter records effective samples and adoption state: migrated, inactive, unsupported or legacy. The accepted pilot must not treat a visual weather change as physical adoption.

**Proposed baseline:** gravity Y = −9.81 m/s², temperature 288.15 K, density 1.225 kg/m³, wind [0,0,0] m/s. Temperature/density are explicit dry-air inputs; derived pressure, reference altitude and any override consistency must be specified. A coherent zero-wind/reference-density mode needs regression checks against the original drag path and random-draw behavior. Seed/order policy is part of the manifest; it does not by itself establish bitwise determinism.

Use relative airflow in the adopted generic dry-drag path, retaining/calibrating the actual model coefficient and force distribution. Do not silently replace a node-based model with a guessed whole-vehicle drag law. Wind/density changes and zero/non-Earth gravity require fixture tests. Existing gravity normalization, fixed fluid/pressure constants and separate aero inputs are known audit points; capability ranges stay limited until those paths are verified.

Resolve the requested pose before settling; any later pose reapplication must refresh/verify relevant contact state. At the release boundary initialize coherent nodal/body motion, wheel motion/internal state and disabled propulsion/braking policy; record resulting p/K and state-injection ports. Define a measurement start after initialization and verify actual approach speed/alignment before impact. Do not continuously clamp speed during the observed coast/impact. A changed initial state is a new configuration/attempt.

A constant-wind equivalence fixture compares relative flow under vehicle motion and ambient wind, with gravity/contact confounders removed. Later flight/gust/particle adapters extend the same field/observation contract; unsupported active paths cannot earn a coherent-environment validation badge.

## 7. Recorder, archive and resource budgets

Observe/reduce each active native step, independently of retention/display. The confirmed starting targets are approximately 200 Hz summaries, configured 2 kHz event detail for 2 s pre/4 s post and 10–20 Hz UI updates. Physics tick IDs and the actual step duration are the authoritative clock; wall/renderer/video time is mapped separately. Profiling must establish achievable capture demand.

**Proposed raw records:** native state/integration, force application/channel, contact, beam/model transition, direct state correction, environment sample, cohort summary, command/event and capture gap. Include attempt, actor/node/topology generation, stream/sequence, tick/phase, field precision/units and coverage. Detailed masks select retained nodes/contacts/beams; every-step accounting still covers the declared cohort and all active force channels.

Versioned little-endian chunks carry schema/build/attempt identity, field layout, tick/sequence ranges, record counts, checksum and a commit marker. Separate produced, enqueued, written and durable counters. Recover only verified committed prefixes after a crash, and classify any tail uncertainty. Catalog/event durability and raw-chunk durability need their own journal rules.

A pre-trigger ring is distinct from the writer queue. Trigger on the first required consumed vehicle/barrier-contact event; the exact threshold/feature predicate must be versioned. Merge overlapping windows or reserve them explicitly, extend later triggers and verify required prehistory/posthistory. Conditioning records may appear before the scientific measurement start but carry their phase. If history is missing, record the gap and retain later observations under D008.2.

Recorder overflow/loss does not block a force callback or silently reduce the configured rate. Use bounded buffers, explicit dropped/unknown counts and a reserved health/event path. If an archive cannot accept health records, retain known counters in the worker/coordinator and mark archive availability/quality honestly. The active attempt continues where possible; future launches remain held while shared storage is unavailable.

| Budget/default | Proposed starting point | Verification needed |
| --- | --- | --- |
| Pre-trigger memory | 256 MiB per native worker | Required 2 s history for the actual configured payload |
| Writer queue | Separate 256 MiB | Burst throughput, high-water behavior and gap recording |
| Pilot raw reservation | 1 GiB per attempt, expanded by preflight estimate when needed | Actual node/beam/contact record mix and requested duration |
| Free-space floor | 10 GiB after planned reservations | Suitable operating margin on the selected archive volume |
| Recording scope | Whole-cohort accounting; bounded configured detailed traces | Freeze required masks and inspect transient peaks |
| Aggregate observer overhead | Target ≤10% over observation-off physics workload | Same workload/build/graphics settings and repeated profiling |
| Event-detail overhead | Target ≤25% over observation-off workload | CPU/physics timing, writer lag and no hidden sampling reduction |

These are **engineering proposals**, not user-approved byte limits or benchmark results. If the required profile exceeds a budget, preflight returns the reason and a revised estimate; it must not silently omit required data. Resource proposals can change through a versioned rationale/profiling record.

**Calculated example:** 176 nodes × 2,000 Hz × 4 × (9 + 8×3) float32 values = 46,464,000 bytes per simulated second, or 278,784,000 bytes for a 6 s detailed window. This uses the historical Daf node count and a hypothetical eight extra vector channels. It excludes IDs, masses, beam/contact/events, alignment, summary/video data, compression and the potentially different realized node count. It is not an archive-size or disk-throughput measurement.

Retain archives, reports, logs/images/video and failed/incomplete attempts until explicit manual archive/cleanup. An archive action produces a verified manifest before original-location cleanup. Cleanup targets the configured trial archive and records what was removed; historical baseline/source/build inputs remain protected. Archive availability is separate from the historical execution/validation outcome. No automatic retention deletion is selected.

## 8. Pilot fixtures and numerical acceptance proposals

The first package uses the pinned `b6b0UID-semi.truck` and `simple2.terrn2` plus versioned purpose-built fixtures. Additional downloaded terrains remain future candidates. The fixture implementation must establish a valid minimal RoR actor/scene and actual force path; analytical reference math alone does not validate the runtime.

| Fixture | Proposed parameters | Independent evidence |
| --- | --- | --- |
| Uniform free fall | 100 kg cohort, zero initial velocity, gravity −9.81 m/s², 0.5 s measurement; enough clearance; drag/contact/actuation inactive | Recorded masses, gravity impulse, velocity/displacement and kinetic/work/potential changes |
| Linear undamped spring | 100 kg moving mass, fixed anchor, k = 10,000 N/m, 0.05 m extension, c = 0; gravity disabled after zero-gravity guards pass | Initial linear storage 12.5 J; analytic oscillator and native-step reference; anchor reaction and energy drift |
| Linear damped spring | Same k/m/extension, c = 200 N·s/m, 5 s bounded observation | Damped reference response and actual signed damping work/storage balance |
| Steady relative-air test | Adopted dry drag, vehicle motion versus equivalent opposite wind; isolated from ground forces | Relative-flow force/work equivalence and recorded environment samples |
| Daf/fixed barrier | Proposed launch speeds 3, 5 and 10 m/s, five repeats; neutral/off propulsion and coherent rolling initialization; controlled flat barrier | Actual approach state, contacts/impulses/peaks, deformation transitions, core ledger/coverage and retained impact window |

Numbers and geometry are **proposals for review/spikes**. Record actual realized mass; the truck's nominal header mass is not sufficient. Fix barrier material/transform/contact features and actor/node cohorts. Require demonstrated 2 s trigger history; select distance/conditioning phases accordingly. Resolve wheel initialization, fixed-node reaction semantics, gravity-zero normalization and drag-disable capability before accepting relevant fixtures.

Proposed approach gate: actual speed within max(0.1 m/s, 2% of target) and heading/alignment within 1 degree of the declared barrier approach. Exact speed definitions, crossing plane, lateral tolerance and rejection rules must be frozen per scenario. A valid integration ledger does not make an out-of-condition approach the requested impact experiment.

### Automated gates

A result references a versioned acceptance profile, observed values and per-check outcomes. If required thresholds/coverage are unresolved, validation is `NotReady`, not `Passed`. Numerical tolerances must account for native precision and discrete integration, with an independent expected result and absolute floor.

| Check | Candidate numerical budget / rule | Qualification |
| --- | --- | --- |
| Required capture | Zero missing required records/ticks/transitions in the declared window | Missing capture persists as incomplete and cannot pass |
| Force attribution | norm(real consumed F − sum(channel F)) ≤ 0.001 N + 0.00001 × sum(norm(channel F)) | Explicit unknown/uninstrumented coverage is a separate failing check, not a residual-filling channel |
| Fixed-mass momentum update | Residual ≤ 0.0001 kg·m/s + 0.00001 × declared impulse/state scale | Include direct state/cohort flux ports and rounding semantics |
| Discrete kinetic/work update | Residual ≤ 0.001 J + 0.00001 × declared work/energy scale | Uses actual integration state; no blanket thermodynamic interpretation |
| Free-fall response | Candidate velocity 0.1%, displacement 0.5%, with absolute floors | Compare the native-step reference and continuous theory separately |
| Linear storage response | Candidate 1% normalized mechanical-energy/response envelope with a declared absolute floor | Derived fixture-specific numerical bound; damping tails need absolute treatment |
| Repeatability | Five repeats initially; report spread in impact time, impulse, approach and K/work | Derive/freeze metric envelopes through repeatability/concurrency spikes |
| Observation equivalence | No unexplained change in reference trajectories/force branches with observation enabled | Do not claim whole-engine bitwise determinism |
| Capture/compute performance | Meet the selected profile without unreported loss; report overhead/lag | Candidate overhead budgets from Section 7, distinct from physical accuracy |

The numerical budgets are not calibrated or achieved. E01/E13 must verify them against independent references, document the error budget and freeze meaningful acceptance profiles before milestone evidence. A deliberate tolerance revision records its reason/version and does not rewrite past results or automatically convert a prior failure into success.

A core scoped pass can coexist with estimated/unclosed nonlinear energy coverage. Full deformation/fracture/drivetrain, real-world predictive accuracy, heat/sound and asset/material calibration remain separate work. Report the scope and unsupported terms rather than apply one global “validated” badge.

## 9. Workbench and evidence experience

The initial local React workbench provides experiment drafts/revisions, unit-aware vehicle/terrain/environment/initial-state forms, capability errors, sweeps/repeats, a sequential queue, per-attempt timeline and pause/resume/cancel/manual retry/archive actions. Read-only active configuration displays requested, resolved, applied and observed values.

Scientific dashboards show force-vector components and peak-preserving envelopes, contact impulse/normal/friction, momentum, node K and supported storage/work, residuals/coverage, gravity/air/wind, critical transitions and capture produced/written/durable/gap health. Drill-down selects cohort/channel/time interval and reads archived detail. Downsampled plots retain extrema and must not draw a false continuous line across an archive gap.

Render model/estimate/calibration and capture-quality labels with the relevant values. A disconnected live view shows last-known tick/time and resynchronizes from a snapshot plus durable event cursor. Reconnecting the UI does not restart or reissue a physical trial command.

The source-built RoR scene remains a separate window. Later interactive 3D inspection consumes reduced immutable node/beam/contact state with stable identities, selection and force glyphs. Browser video streaming/native-renderer embedding is not a prerequisite.

For milestone evidence, run the exact new source-built executable with process/module provenance, capture meaningful native scene movement/impact plus telemetry, and retain logs/hashes. Map video/screenshot wall time to recorded physics events with synchronization uncertainty. A recorder success code, menu screenshot or browser chart alone does not prove the requested physical run.

## 10. Delivery epics and milestone gates

The epic IDs retain continuity with the architecture evaluation. First-release work is selected by the decision log; a later feature appearing here does not authorize its implementation now. No calendar or effort commitment is established.

| Epic | First-release scope | Completion evidence / later boundary |
| --- | --- | --- |
| E01 · Measurement and trial contracts | Cohorts, SI units/world axes, epochs, capability matrix, immutable manifests and acceptance profiles | Independent reference fixtures and reviewed schemas; freeze meaningful tolerances before qualification |
| E02 · Native integration observer | Generated/consumed attribution, final force writes, resets/transfers, state corrections and barrier publication | Every active pilot force path classified; observation-on/off equivalence and fixed-mass update checks |
| E03 · Contact and beam observations | Actual contact applications/impulses, distributions, beam forces and plastic/break transitions | Trace representative ground/barrier and beam cases without double counting; distinct peak definitions |
| E04 · Core energy ledger | Node kinetic energy, supported conservative storage, discrete work, direct-state ports and explicit residual/coverage | Free-fall and linear spring/damper checks; broader nonlinear deformation/fracture/drivetrain closure follows later |
| E05 · Capture and archive | Bounded prehistory/writer queues, configured detail windows, summaries, gaps, committed recovery and manual retention | Overflow, disk-full and abrupt-exit tests preserve verified records and sticky incomplete quality |
| E06 · Environment foundation | Uniform gravity, dry-air state, steady vector wind, physical drag adoption and capability reporting | Zero-wind regression, gravity guards and relative-air equivalence; effective inputs are observable |
| E07 · Structured atmosphere and particles | Contract extension points and explicit unsupported status | Gusts, correlated turbulence and particle exposure are later work; coupled particle/surface physics needs a separate coverage gate |
| E08 · Execution adapter | Controlled settling, coherent velocity release, coasting barrier scenario, tick-safe pause/resume/cancel | Actual approach-state checks and recorded state injection; driven journey/path controller is the next execution milestone |
| E09 · Coordinator and queue | Fresh worker/private profile per attempt, sequential repeats/sweeps, acknowledged commands, catalog, shared-blocker handling and manual retry | Independent queued trials continue after an attempt failure; process/queue recovery creates no duplicate run |
| E10 · Trial authoring | Unit-aware React forms, asset/capability resolution, immutable revisions and requested/resolved/applied views | Invalid definitions fail preflight with specific reasons; edits cannot mutate an active attempt |
| E11 · Live scientific workbench | Force/momentum/energy/environment charts, event timeline, capture health and separate native RoR scene | Reconnect/coalescing tests preserve history semantics; interactive 3D scientific inspection is later |
| E12 · Analysis and reporting | Archived metric queries, repeat comparisons, scoped validation and HTML evidence exports | Metrics tie to immutable inputs, coverage, accepted profiles and source-built process evidence |
| E13 · Integrated qualification | Analytical fixtures, balance/repeatability checks, resource profiling and injected capture/control failures | Reproducible pass/fail reports for the declared pilot scope; no general real-world accuracy claim |
| E14 · Scale and advanced studies | Preserve extensible identities, schemas and export boundaries | Parallel workers, remote/headless execution, flight studies and advanced coupling are later gated options |

### Dependency strategy

1. **Contract and feasibility gate:** inventory actual native force paths, define initial schemas/coverage and demonstrate viable minimal fixtures. Spike wheel/release initialization, zero-gravity guards, trigger timing and representative recorder demand.
2. **Scientific core gate:** instrument the integration path and qualify free-fall/spring/damper references, force attribution and energy semantics. Add the adopted dry environment and relative-air fixture. Record unsupported branches explicitly.
3. **Execution and capture gate:** produce a controlled Daf/barrier attempt with required pre/posthistory, pause/cancel semantics and durable archive. Inject buffer/storage/process failures and verify D008.2 continuation and honest classification.
4. **Workbench integration gate:** connect the coordinator, serial queue and React authoring/live/history views to real worker commands and artifacts. UI work can proceed against visibly labeled synthetic fixtures while native work advances; mock values never become simulation evidence.
5. **Pilot qualification gate:** run the versioned approach-speed/repeat matrix, independent validation, observation/performance comparisons and source-built native evidence capture. Accept only the declared core scope; retain failures and incomplete attempts.

The coordinator can share an initial contract with the workbench before the complete physics recorder exists. Integration still depends on the native timing/coverage and archive gates. A successful dashboard demonstration does not complete E02/E04/E13.

### What the first milestone delivers

A locally authored experiment resolves pinned assets, performs preflight, launches a new instrumented source-built RoR process, establishes controlled initial conditions, executes a coast/barrier impact, records the declared measurement profile and presents live and archived results. The archive contains configuration/provenance, actual environment/state, forces/impulses, core energy accounts, capture quality, events and scoped automated checks. The sequential queue and manual retry/retention policies behave as selected.

It does not require a driven journey controller, flight/gust/coupled-particle models, an embedded native viewport, parallel execution or a restartable physical checkpoint.

## 11. Readiness and open engineering contracts

The product-policy Q&A is complete. The following items are engineering work within that selected direction, not another unanswered A/B questionnaire. Proposed defaults in this document require evidence and a versioned contract before they can support a passing scientific result.

| Contract / risk | Resolution needed | First-release gate |
| --- | --- | --- |
| O01 · Fixture and release mechanics | Valid minimal actors; fixed-anchor reactions; coherent node/wheel/internal motion; conditioning/contact refresh; zero-gravity/drag-disable guards | E01/E06/E08 before accepting the affected fixtures or approach conditions |
| O02 · Force/model coverage | Enumerate actual writes, alias/rope corrections, mass/cohort changes, sleep/reset paths, contact distributions and native factor/precision | E02–E04: every active pilot term covered or explicitly disqualifying the requested scope |
| O03 · Protocol and durability | Native IPC/chunk layout, schema negotiation, command deduplication, checksums/flush policy, catalog reconciliation and control-owner leases | E05/E09: test crash/disconnect/reconnect and distinguish confirmed loss policy from proposed coordinator-loss behavior |
| O04 · Capture profile and demand | Exact trigger predicate, required masks/cohort, overlapping-window rules, prehistory phase, high-water and storage reservations | E05/E13: measured payload/overhead support the selected profile or fail preflight explicitly |
| O05 · Numerical acceptance | Independent native-step/analytic references, unit/scales/floors, approach definition and repeat envelopes | E01/E13: freeze versioned thresholds before acceptance, with reasoned error budgets |
| O06 · Build and local packaging | Pin .NET/Node/React/toolchain/dependencies, native schema/build identities, browser launch/origin and private worker profiles | E09/E10: reproducible clean build/launch with installed-game binaries excluded |
| O07 · Views and evidence mapping | Peak/gap-preserving chart reduction, event cursors, exports and native video/physics time correlation | E11/E12: UI/offline results match archived data and evidence states synchronization limits |
| O08 · Future physical coupling | Flight adapters, correlated turbulence, passive/coupled particles and material calibration | Later scope; not a prerequisite for the first ground-impact pilot |

The coordinator-loss lease/stop-and-drain proposal must be specified independently of recorder gaps. Losing required telemetry invokes the confirmed continue-and-mark-incomplete policy. Losing the control owner is a different lifecycle condition; test and record its eventual contract rather than infer approval for an unrecorded behavior.

A first implementation session should start with E01 and the small native feasibility work in E02/E06/E08, using a new build/evidence directory. Preserve the existing source-build baseline. Use the build guide's source/process/module provenance and update this document with measured results and frozen contracts as work progresses.

**Current readiness:** planning baseline established; engine instrumentation, environmental adapters, coordinator, React workbench and new automated physical validation are unimplemented. This review does not claim that any proposed rate, tolerance, payload budget or physical model has been achieved. Documentation verification below concerns the report and its references only.

## 12. Evidence, references and maintenance

This specification consolidates the [decision log](implementation-decisions.md), [architecture evaluation](trial-platform-architecture-options.md) and [platform research](../../../platform.md). Those evaluations contain the detailed pinned-source and primary-document references. The [downloaded terrain inventory](../research/2026-10-08/terrain-inventory.md) is a read-only candidate inventory, not an asset qualification.

- [Project introduction](../../../PROJECT.md), [architecture overview](../../../architecture.md), [project memory](../../../project-memory.md) and [backlog](../../../todo.md) establish session context and open work.
- [Build and recording guide](../build-and-record.md) establishes source-build and native evidence procedures.
- [Original source-build records](../baselines/2026-10-08/README.md) record historical build/run evidence; it does not validate this new pipeline.
- [Architecture reference inventory](2026-10-08/references.json) and [platform source inspection](../research/2026-10-08/source-inspection.json) preserve research provenance.
- [Implementation review reproduction and checks](2026-10-08/implementation-review.md) records how the HTML companion was rendered and checked.

Local code findings are tied to source HEAD `e85535569102b6251849af574026984e3213b3f4` and content commit `34fefdd126784bf87b068fc283f812525d159dd7`, with local documentation changes. Verify the current tree before implementation. Read-only tool inspection found .NET 10 SDKs installed; dependency pinning and a coordinator build remain future work.

Maintain the decision log for user policy, this specification for contracts and measured refinements, and dated evidence records for validation. Preserve historical reports. A changed profile creates a new schema/configuration/acceptance revision; do not revise archived measurements or silently reinterpret a prior outcome.

### Pinned native implementation anchors

- [A01 · Global physics loop, actor barriers and FreeForces](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorManager.cpp#L1247-L1320)
- [A03 · Ground contact, integration, force reset and generic drag](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorForcesEuler.cpp#L1602-L1699)
- [A04 · Beam models, deformation, breakage and final applied forces](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorForcesEuler.cpp#L1210-L1465)
- [A05 · Ground collision and combined contact/fluid response](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/collision/Collisions.cpp#L1243-L1344)
- [A06 · Inter-actor contact and barycentric force distribution](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/collision/DynamicCollisions.cpp#L92-L115)
- [A13 · Rope-linked node velocity/force replacement](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorForcesEuler.cpp#L1827-L1853)
- [A14 · Native physics step](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/SimConstants.h#L17-L21)

These are static code references at the pinned revision. Runtime branch coverage remains an implementation acceptance obligation.
