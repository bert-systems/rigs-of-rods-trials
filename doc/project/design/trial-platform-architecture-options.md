# Trial platform architecture options: force accounting, environment and workbench

Evaluated **2026-10-08** against the personal fork **bert-systems/rigs-of-rods-trials**, source **e85535569102b6251849af574026984e3213b3f4**, content **34fefdd126784bf87b068fc283f812525d159dd7**.

**Status: architecture evaluation and proposed delivery strategy.** This document recommends boundaries, candidate contracts, validation gates and epics. It does not claim a completed instrumentation pipeline, calibrated physics, final technology selection or implementation. [Illustrated HTML](../reports/trial-architecture-options-2026-10-08.html). [Platform research](../../../platform.md). [Current engine map](../../../architecture.md).

## 1. Recommendation and decision framing

Build an **instrumented native RoR worker**, an independent **trial coordinator**, and a replaceable **workbench UI**. Keep physical force/energy observation inside the C++ solver; keep process supervision, experiments, records and presentation outside it. An external launcher alone cannot reconstruct accurate contact peaks or an energy ledger from current script getters.

Evaluate two delivery options:

| Option | Shape | Best fit | Main tradeoff |
| --- | --- | --- | --- |
| A — Windows .NET workbench | Native worker + .NET coordinator + WPF desktop UI; authenticated local pipes; native game window alongside dashboard | A Windows laboratory tool with straightforward desktop/process integration | Windows UI commitment and more specialized chart/3D tooling |
| B — React workbench with .NET coordinator | Same native worker + ASP.NET Core local coordinator + React/TypeScript UI; HTTP commands and SignalR summaries; optional WebView2 shell | Rich trial authoring, comparisons and live scientific views, with a route to remote workers later | More deployment/browser/state boundaries; browser still needs the native coordinator to launch RoR |

**Recommended evaluation direction: B, local first**, using the same reusable .NET coordinator that A could consume. React fits a growing configuration/dashboard/analysis product; .NET provides strong local process and filesystem integration. If one Windows workstation is the long-term product and desktop conventions dominate, A is a sound lower-scope choice. Neither UI choice removes the native physics work.

Implement the coordinator initially as a modular application with a local durable catalog, not a fleet of services. Run one isolated native process per realized trial initially. Add concurrent or remote workers only after measuring simulation, capture, graphics and storage demand. Keep a potential future headless execution adapter behind the worker contract; extracting the solver now would multiply coupling and validation work.

The most difficult work is **complete force attribution, model-consistent energy transitions, synchronized atmosphere adoption, and validation**. Trial forms and live charts are substantial product work, but they are not the critical scientific dependency.

## 2. What “medium to high resolution” should mean

Resolution has four independent dimensions: **time**, **spatial/component coverage**, **numerical precision**, and **physical/model fidelity**. Increasing sample rate or using double-precision sums does not make an uncalibrated vehicle a validated material/flight model.

RoR's baseline step is 0.5 ms: nominally 2,000 integration steps per simulated second. At this step a 2 ms pulse spans only about four intervals. “High resolution” here means observing the existing solver faithfully; changing the solver step, contact law, vehicle mesh or material model is a separate convergence/model programme. [A14 · Native physics step](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/SimConstants.h#L17-L21)

Proposed initial capture profiles, subject to profiling:

| Profile | Observe/reduce | Retain | Live display | Intended use |
| --- | --- | --- | --- | --- |
| Medium | Every active 0.5 ms step: body/channel impulses, work totals, extrema and health checks | Actor/channel aggregates at 100–200 Hz; full node state around 200 Hz; selected nodes/contact events at up to 2 kHz | 10–20 updates/s; peak-preserving envelopes and last-known status | End-to-end exploratory trials with bounded storage |
| High event capture | Same every-step accounting plus detailed selected beam/contact/node traces | 2 kHz detailed state in trigger windows, e.g. 2 s before and 4 s after impact; low-rate baseline outside | Same UI cadence, with drill-down to raw archived windows | Crash/landing/load events where peaks and timing matter |
| Full audit | Every actual force/state mutation and active integration | Full configured node/channel detail at 2 kHz for a short bounded run; all transitions | Reduced live feed, authoritative raw archive | Coverage debugging and model validation; expensive |

These are targets, not achieved performance numbers. A medium profile still computes impulses/energy each step: reducing *retention* must not reduce accounting fidelity. Preserve transient event records and tick extrema before downsampling; distinguish capture gaps from intentionally omitted raw channels.

Adopt integer tick/epoch IDs and the recorded step duration as the analytical clock. Keep monotonic wall time, renderer/video timestamps and batch simulation time separately. Paused/sleeping actors have explicit active/inactive flags; a UI value repeated during pause is not a new physical sample. The current frame batching and simulation clock remain relevant until a controlled trial execution mode is validated. [A15 · Wall-time batching and simulation clock](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorManager.cpp#L1120-L1234)

Tentative acceptance targets to negotiate in the detailed specification:

- Zero missing accounting ticks or critical transitions within an accepted observation window; selected raw retention can be narrower by policy.
- A source-attribution check at each integration: applied channel sum matches the actual consumed force within absolute-plus-relative numerical tolerance; unsupported channels remain explicit.
- No silent relaxation of capture rate, validation rules or environment coverage. A profile change has its own event and affects acceptance.
- Live status age target under 250 ms at one real-time worker; UI publishes around 10–20 Hz. This is a product SLO to benchmark, not a timing claim.
- Observer overhead target below 5% for Medium and below 10% for High event capture on a declared workload. Benchmark actual outcome variation as well as throughput.
- Energy closure must use scenario-specific tolerance and reference scale. Start with simple fixtures; do not impose one arbitrary percentage on every nonlinear crash.

## 3. Shared architecture and ownership

### 3.1 Native worker boundary

The RoR process owns simulation, tick-scheduled control, atmosphere evaluation, applied-force observation, immediate reductions and a bounded asynchronous recorder. It can publish immutable summaries and chunk metadata. No dashboard or IPC thread may read live ar_nodes/ar_beams directly.

Proposed native modules:

| Module | Responsibility | Ownership rule |
| --- | --- | --- |
| TrialExecutionAdapter | Exact asset/config verification, lifecycle, initial state, tick-scheduled controller and acceptance probes | Commands enter only at defined safe barriers |
| ObservationContext | Trial/epoch/tick identity, force-channel registry, immutable selection and coverage configuration | No arbitrary script callbacks inside the solver |
| ForceAttribution / MutationAudit | Pending and consumed force channels, direct velocity/position/mass changes, link/contact identity | Mirrors actual force reset/transfer behavior |
| EnergyReducer | Body momentum/kinetic state, work/impulse integrals, stored energy, transitions and residuals | Worker-local accumulation; stable merge order |
| EnvironmentService | Versioned gravity, atmosphere, wind/gust field and optional particulate field | Thread-safe immutable configuration with deterministic sampling |
| Recorder / LivePublisher | Preallocated buffers, chunk writer, peaks/envelopes, sequence/gap counters and heartbeat | Disk/compression/network work outside physics tasks |

The first implementation can keep these modules compiled into the existing executable. A build/runtime observation switch and an independently testable reducer library limit the fork's maintenance surface. A runtime plugin ABI is not needed initially; per-mutation dispatch across a plugin boundary would complicate the hottest code and lifecycle.

### 3.2 Coordinator and storage boundary

The .NET coordinator owns experiment definitions/revisions, realized trial expansion, asset/build resolution, queueing/resource leases, process/profile isolation, command acknowledgements, durable trial state, archive catalog, analysis jobs and UI APIs. The native writer owns raw capture until completed chunks are handed off; the coordinator does not insert a database row for every physics value.

Use SQLite for local metadata/status with a single coordinator write owner. Keep raw chunks and finalized columnar files in a trial directory outside Git. WAL helps local reader/writer concurrency but still has one writer at a time and is unsuitable as a shared network database. A future remote service can use a server database through the coordinator rather than placing SQLite on a network share. [T09 · SQLite WAL concurrency](https://sqlite.org/wal.html)

Store immutable artifacts by identity/hash and mark results complete only after capture closure, inventory/hash verification and metric validation. SQL transactions and filesystem writes are not one atomic transaction: write to staging, finalize files, commit references, then reconcile orphan/staged items after a crash.

### 3.3 UI boundary

The workbench edits draft definitions, validates server-returned capabilities, monitors trials, and compares archived results. It consumes derived snapshots and a durable event cursor. It cannot directly change a running actor, choose its actual force-integration timing, or make an invalid run valid.

A separate RoR window is the first live visual view. An eventual synchronized vehicle/node view can use reduced immutable geometry/state, selectable vector glyphs and force/energy coloring. Embedding OGRE into WPF/WebView or sending video into a browser should be a separately justified feature, not a prerequisite for the accounting pipeline.

### 3.4 Two independent data paths

**Authoritative path:** force/state mutation → tick reduction → bounded native buffers → finalized raw chunks → analysis/columnar archive → scientific result.

**Presentation path:** native peak/envelope summaries → coordinator → WPF bindings or SignalR → charts/vector scene.

Losing or slowing the UI must not drop authoritative data or steer the controller. A live disconnected/stale indicator is distinct from capture corruption. A coordinator crash must not cause the engine to keep running indefinitely without an explicit lease policy.

## 4. Instrumentation must follow the actual solver

### 4.1 Source-grounded phase map

At the inspected commit, ActorManager iterates substeps. Active actor compute tasks run in parallel and complete before inter-actor beams; another parallel phase resolves inter-actor collisions; FreeForces runs afterwards. [A01 · Global physics loop, actor barriers and FreeForces](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorManager.cpp#L1247-L1320)

Within an actor compute task, CalcNodes runs first, followed by aircraft/fuselage/buoyancy, wheels/shocks/hydros/commands/engine, beams, cab collisions and slide-node work. CalcNodes adds ground/object contact, integrates velocity and position, then resets each node's force to gravity and adds drag/water contributions for a later integration. This is **not** a clean “clear all forces → calculate all forces → integrate all actors” loop. [A02 · Actor force/integration ordering](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorForcesEuler.cpp#L46-L67) [A03 · Ground contact, integration, force reset and generic drag](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorForcesEuler.cpp#L1602-L1699)

Consequences for the design:

1. Introduce a **generated epoch** and **consumed integration epoch**. Forces accumulated after an integration may be consumed later; some cached terms have additional lag.
2. Maintain attribution buffers alongside the force accumulator. When it resets to gravity, reset/reseed its channel buffer in the same branch. When forces move between nodes, move the corresponding attribution.
3. Capture the actual consumed vector immediately before a node's velocity integration, after that node's ground/object collision contribution. Retain pre/post mass/velocity/state with that integration ID.
4. Do not reinterpret previously generated forces as having arisen from the current post-integration geometry. Carry their evaluation state/timing or clearly expose the lag.
5. Publish a coherent actor/world boundary only after all relevant task barriers. This does not make earlier per-node integration phases simultaneous; the record must retain those semantics.
6. Keep first-tick initialization, actor sleep/wake/reset, disabled nodes and queued actor changes in the model. An inactive actor's force buffer is not an ordinary new active integration.

Audit all write/replace/transfer paths, including rope-linked nodes that copy velocity/position and transfer then clear a force. A first regex pass found 68 force write expressions under physics, but aliases, helpers, resets, spawning and other modules make that a lead list, not exhaustive coverage. [A13 · Rope-linked node velocity/force replacement](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorForcesEuler.cpp#L1827-L1853)

### 4.2 Force attribution and contact identity

Prefer small inline hooks/wrappers at force-producing sites that record the **same final applied vector** without recomputing a different physical law. Classify the contribution and mirror it into the existing accumulator. Initially preserve solver ordering and physical results; a later force-assembly refactor is optional after observation equivalence tests.

Channels should cover gravity; beam elastic/damping/nonlinear response; drivetrain/wheel drive/braking; actuators/hydros; ground/object normal and friction response; actor contact; fluid/buoyancy; generic aero drag; wing/fuselage/propulsion; links/constraints; and artificial/user forces. Include Unknown/Uninstrumented and StateCorrection explicitly.

The primitive collision function mixes solid normal/friction response and ground-fluid effects. Record branch contributions there, then record their actual application at the caller. Inter-actor contact distributes the hit-node force over three triangle nodes using barycentric weights. One contact record should include the hit actor/node, triangle actor/three nodes, feature IDs, weights, normal, penetration, material/ground-model identity, relative velocity, generated/consumed phase, and applied vectors. [A05 · Ground collision and combined contact/fluid response](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/collision/Collisions.cpp#L1243-L1344) [A06 · Inter-actor contact and barycentric force distribution](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/collision/DynamicCollisions.cpp#L92-L115)

Do not double-count one physical interaction in scene-level totals merely because both endpoints are recorded. Preserve every actual application needed to reproduce the solver sum. A normalized contact key supports correlation/aggregation; it must not silently remove two separate solver applications under the assumption that they are duplicates.

For actor-only momentum, internal beams should cancel net force while external contact/actuation remain. For multi-actor boundaries, contacts/links internal to that cohort cancel net impulse, yet still transfer work between bodies. Unsupported externally held/fixed nodes can transmit a reaction with zero displacement/work; both facts matter.

Define distinct peak outputs: largest norm of the whole-body contact resultant per tick; largest node contact load; per-contact peak; normal/tangential components; and threshold duration. A vector formed from independent component maxima at different times is not a physically observed peak vector.

### 4.3 Beam forces and transition events

Capture effective k, damping, branch, extension/rate, rest length before/after, yield/strength before/after, final endpoint vectors and enabled/broken state. In CalcBeams, stress is assigned before plasticity/break logic may change the force; use the final applied vector, not that field alone, as authoritative load. If a branch clamps/changes the combined elastic and damping force, retain pre-branch diagnostics and the actual correction separately; do not invent a physical decomposition by scaling components. Detacher groups can disable additional beams/wheels; report the cascade as structured transitions. [A04 · Beam models, deformation, breakage and final applied forces](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorForcesEuler.cpp#L1210-L1465)

Linear spring/damper accounting is a tractable first model. Shocks, support/rope bounds, changing hydraulic length, nonlinear damping, plastic rest-length updates and beam deletion need model-specific storage/work terms. Beam break sound modulation uses an energy-like expression, but a sound effect is not a validated fracture-energy measurement.

### 4.4 Concurrency and hot-path constraints

Use actor/job-owned preallocated buffers for parallel actor work. For cross-actor collision jobs, record into task-owned scratch records and merge at existing barriers; avoid concurrent mutation of one observation accumulator without an audited ownership rule. The observer must not introduce data races or hide existing synchronization assumptions.

No allocations, formatted logging, file flushes, chart serialization, database calls, mutex-heavy aggregation, .NET calls or network waits inside each force callback. Select channels/nodes with precomputed masks; use an observation-disabled fast path. Merge in a stable order with double-precision reductions; this improves accounting stability without changing native solver precision.

Keep compile options and observation levels separable: Off, aggregate accounting, selected raw, full audit. Coverage tests compare channel sums to real consumed forces, not merely observer outputs to their own formulas.

## 5. Energy accounting: a measured ledger with residuals

### 5.1 Declare the measurement boundary

Use a fixed world frame with Y up and SI units. Define the actor/node cohort and reference point; pin topology and mass definitions. Do not mix the vehicle's camera reference with center of mass. Include payloads/trailers/fragments in a declared cohort or account for transfer across its boundary.

The initial mechanical ledger should cover node translational kinetic energy, supported model-consistent elastic storage, gravitational potential where valid, external work and documented dissipation/state transitions. A full vehicle system may also contain engine/drivetrain rotating inertias or other internal energy reservoirs not represented by node kinetic energy. Their state/work ports must be included or declared outside scope. Fuel chemistry, heat, sound radiation and fracture material physics cannot be inferred from display gauges.

### 5.2 Discrete work and momentum

For a fixed-mass node whose only velocity change is the observed integration:

~~~text
v_after = v_before + J_total / m
ΔK = 0.5 m (|v_after|² - |v_before|²)
   = v_mid · J_total,  v_mid = 0.5 (v_before + v_after)

J_channel = F_channel_consumed × dt
W_channel = v_mid · J_channel
~~~

The midpoint velocity here is an **accounting identity for that discrete velocity update**, not a replacement integrator. Sum channels against the same actual consumed epoch. If velocity is directly set, mass changes, or a constrained node bypasses integration, the identity needs explicit state-correction/boundary terms. Position integration, gravity potential and approximate constitutive forces can still leave a numerical residual.

For an endpoint pair, evaluate both endpoint work contributions in the same epoch. Net internal force may cancel, while internal work changes deformation/storage/dissipation. For a static barrier, vehicle energy can leave the measured body through contact/model dissipation despite the supported barrier doing no displacement work.

Keep a momentum residual Δp minus external impulse, and an energy residual. Report absolute residual and relative residual normalized to a declared nonzero reference scale with an absolute floor. Near-zero inputs need absolute tolerances, not unstable percentages.

### 5.3 Proposed ledger channels

| Term | Initial implementation | Interpretation / extension |
| --- | --- | --- |
| Node kinetic energy and momentum | Coherent pre/post node mass/velocity with cohort mapping | Distinguish COM motion, internal vibration, rotational/deformation contributions; node K already includes motion of all selected nodes |
| Gravity potential/work | Constant uniform gravity with declared zero datum; also retain actual gravity work | Spatial/time-varying gravity may lack a single conservative potential; retain field work instead of forcing mgh |
| Elastic storage | Supported linear beam fixture and branch-specific state functions | Nonlinear/hysteretic models need explicitly derived storage; use “unclosed” until supported |
| Damping loss | Actual damping contribution and endpoint work | Check signs and discrete energy behavior; do not substitute c·v² for every nonlinear branch |
| Plastic/rest-length transition | Record parameter/state jumps and associated work/storage change | Label model-transition estimate; current laws do not automatically supply a thermodynamic heat/fracture split |
| Beam break / detach | Before/after stored state and actual final applied force | Removed model storage is not proven fracture/heat energy; preserve signed transition and residual |
| Contact normal/friction/fluid | Branch forces, endpoint relative motion and consumed work | Separate support/penalty response from dissipative friction and fluid effects |
| Actuator/propulsion work | Applied node/constraint work and rotating-state ports where represented | Engine torque×RPM alone may not equal delivered chassis work; internal losses/states need boundaries |
| Aerodynamic exchange | Vehicle work plus relative-air loss and ambient-reservoir term where model supports it | Wind can add energy to a vehicle; never label all aero work as positive dissipation |
| Direct state/mass changes | Reset/teleport/velocity-copy/loading/detach events and energy/momentum deltas | Mark discontinuities or reject within scientific windows; open systems need flux terms |
| Numerical / unsupported residual | Visible signed residual and coverage flags | Never allocate it automatically to “energy absorbed” |

For air relative velocity u = v − w and a dissipative drag force F opposing u, vehicle power is F·v = F·u + F·w. The first term is relative-motion loss; the second is exchange with the prescribed wind reservoir. Lift/propwash/propeller work requires additional ports and consistent local frames. This decomposition explains why windy trials need environment fields inside the ledger.

A complete, accurate ledger is **incremental model coverage**, not one total-energy formula. Display Supported, Estimated and Unclosed status for each term and list coverage by subsystem/version. “All forces captured” and “all energies physically explained” are different acceptance gates.

## 6. Improved environment configuration

### 6.1 A common physical environment service

Introduce a pure, versioned environment query at declared position/time:

~~~text
EnvironmentSample = sample(world_position, evaluation_tick)
  gravity vector / configured scalar mode
  air velocity vector, density, pressure, temperature, viscosity
  gust/turbulence components, model and seed identity
  optional particulate concentration/size-bin properties
  coverage flags, validity range and configuration version
~~~

Start with uniform gravity and dry atmosphere; design the service to accommodate spatial profiles rather than prematurely implementing full meteorology. Make terrain origin/height versus physical altitude datum explicit. Validate units, wind azimuth convention (“from” versus “toward”), world/body transformation, weather profiles, and supported ranges.

One provider must serve generic node/body drag, wings, fuselage, propellers/propwash and relevant propulsion models. Record the sample actually used at the force evaluation epoch. A higher-level actor-center sample is useful for the UI but does not prove the same flow at every wing/node.

Current code has separate density formulas in wing/fuselage/propeller paths, generic node drag with random terms, velocity-derived airflow, and a jet thrust model with its own assumptions. Hull buoyancy also uses fixed pressure constants, while ground-fluid buoyancy uses DEFAULT_GRAVITY. A configuration change is incomplete until its subsystem adoption/limitations are explicit. [A03 · Ground contact, integration, force reset and generic drag](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorForcesEuler.cpp#L1602-L1699) [A07 · Wing airflow, propwash and density](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/flex/FlexAirfoil.cpp#L590-L678) [A08 · Fuselage airflow and drag](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorForcesEuler.cpp#L125-L149) [A09 · Turboprop density and force update](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/air/TurboProp.cpp#L222-L244) [A10 · Propeller airflow, blade forces and wash](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/air/TurboProp.cpp#L350-L432) [A11 · Jet thrust model](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/air/TurboJet.cpp#L227-L283) [A12 · Hull pressure/drag and water velocity](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/water/Buoyance.cpp#L69-L110) [A05 · Ground collision and combined contact/fluid response](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/collision/Collisions.cpp#L1243-L1344)

### 6.2 Proposed environmental levels

| Level | Features | Work / validation |
| --- | --- | --- |
| ENV-1 — Coherent basic atmosphere | Explicit gravity, dry temperature/pressure/density profile, constant vector wind, per-asset drag configuration | Replace scattered airflow/density reads; zero-wind regression and uniform-wind relative-flow tests |
| ENV-2 — Structured wind | Altitude shear, time ramps/step/sine gusts, spatial gust regions, seeded band-limited turbulence, optional wind-field import | Deterministic spatial/time sampling, domain/interpolation provenance, controller/load response and RNG-order tests |
| ENV-3 — Particulate exposure | Concentration/size bins, tracer/super-particle advection and settling, optional deposition/visibility | Physical particle state independent of graphics; material/size/drag inputs, one-way transport first |
| ENV-4 — Coupled advanced effects | Vehicle/air/particle feedback, accretion/mass changes, surface wetness/traction, thermal/humidity interactions or obstacle wakes | Separate constitutive models, stability and calibration; significantly larger scientific scope |
| CFD / resolved granular programme | Resolved fluid obstacles, detailed wakes, granular contact/erosion or two-way multiphase solver coupling | Separate solver/coupling architecture and validation budget; outside the recommended first delivery |

Atmospheric drag depends on density, relative speed, drag coefficient and a declared reference area. A per-node arbitrary force/drag multiplier does not establish calibrated vehicle CdA; splitting a vehicle into more nodes must not accidentally multiply its physical drag. Preserve legacy mode for existing content and add an explicit physical-drag model/parameters for calibrated fixtures. NASA's drag and simplified atmosphere guides provide useful reference equations, not an RoR accuracy certification. [P01 · NASA drag equation and reference area](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/drag-equation/) [P02 · NASA simplified Earth atmosphere model](https://www.grc.nasa.gov/www/k-12/airplane/atmosmet.html)

### 6.3 Wind, atmosphere and model consistency

- Use u = body velocity − ambient flow, adding propwash in the force model with its existing sign convention verified. Test stationary craft in wind, craft moving with the air, and Galilean-equivalent relative flow.
- Centralize pressure/temperature/density calculations with validity limits. Support either a derived thermodynamic profile or an explicitly overridden density; flag inconsistent overrides. Humidity/viscosity additions need calibrated equations and relevant force-model adoption.
- Supply gusts as known time/space functions first. Add spatially correlated stochastic turbulence using seeded, order-independent sampling or precomputed fields keyed by tick/cell; a seeded global RNG consumed in parallel callbacks is insufficient.
- Audit engine thrust/propeller behavior, ground/fluid gravity assumptions, caching and wake/propwash timing. A complete atmosphere badge requires all enabled subsystems to adopt the chosen provider or clearly declare legacy behavior.
- Version the physical environment separately from visual sky/water/cloud/dust settings; the UI can preview both, but each has its own provenance.
- Freeze environment configuration during an accepted trial by default. Scheduled changes belong in the definition; manual changes create a new version/event and may invalidate comparison.

### 6.4 Particulates require an explicit interpretation

Existing DustPool constructs OGRE particle systems; it is a visual surface, not evidence of particulate momentum/energy coupling. [A16 · Native particle-system construction](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/gfx/DustPool.cpp#L39-L65)

Offer three explicit feature modes: **visual appearance**, **passive transport/exposure**, and **coupled physical particles**. Passive tracers can provide concentration/deposition/exposure without claiming forces on the vehicle. Super-particles represent many grains and require weights/size/material distribution, drag/settling laws, emission boundaries, collision/deposition rules, deterministic updates and numerical limits.

Two-way coupling requires equal/opposite momentum exchange, corresponding work/energy terms, removed/deposited particle accounting, and mass/inertia changes if material sticks to the vehicle. Visibility or rain visuals alone cannot set friction, lift or mass. Weather-to-surface traction and particulate wear/erosion should be separate model epics, not hidden consequences of a graphical intensity slider.

For an initial end-to-end system, ship ENV-1/ENV-2 plus visual/passive particulate mode; make full coupled particulates a separately gated expansion.

## 7. Two workbench implementation options

### 7.1 Option A — .NET/WPF Windows workbench

**Components:** WPF MVVM application; UI-independent .NET coordinator/domain library; native RoR worker; local named-pipe command/summary transport; native raw writer; SQLite artifact catalog; background analysis.

WPF supports data binding, Windows controls and 2D/3D presentation, and runs on Windows. .NET offers pipe primitives for local native/managed interprocess communication. These capabilities fit the current Windows source-build workflow, while charting/vector presentation still needs a selected and benchmarked UI implementation. [T01 · WPF overview](https://learn.microsoft.com/en-us/dotnet/desktop/wpf/overview/) [T07 · Pipe operations in .NET](https://learn.microsoft.com/en-us/dotnet/standard/io/pipe-operations)

Advantages: desktop process/file dialogs and native window placement are direct; fewer browser deployment boundaries; a self-contained local product is practical. Limits: Windows-only UI, scientific plotting/navigation still substantial, and future remote/browser access needs an API facade rather than exposing UI-bound objects.

Keep TrialCoordinator independent of WPF Dispatcher and application lifetime. Prefer a local host process if trials must outlive closing the UI. Do not host simulation in-process through C++/CLI or P/Invoke into the existing application: process isolation improves crash/reset boundaries and protects the UI from native faults.

### 7.2 Option B — React + ASP.NET Core workbench

**Components:** React/TypeScript front end; ASP.NET Core .NET coordinator; REST commands/queries; SignalR live snapshots/events; same native worker/pipe/raw-writer contract; same local metadata/files; optional WebView2 desktop shell.

A browser page cannot directly launch a local executable or inspect its modules. The local .NET host performs those actions. React is the presentation layer; WebView2 can provide an optional Windows desktop package without moving simulation ownership into the browser. [T05 · React UI model](https://react.dev/learn) [T06 · WebView2 introduction](https://learn.microsoft.com/en-us/microsoft-edge/webview2/)

SignalR supports asynchronous streaming; reconnect support is configurable and bounded. Use it for reduced live snapshots and notifications, **not** as the authoritative physics archive or a durable experiment event store. The coordinator must retain durable event sequences and offer snapshot/cursor resynchronization after a gap or restart. [T03 · SignalR streaming](https://learn.microsoft.com/en-us/aspnet/core/signalr/streaming?view=aspnetcore-10.0) [T04 · SignalR reconnect/configuration](https://learn.microsoft.com/en-us/aspnet/core/signalr/configuration?view=aspnetcore-10.0)

Advantages: rich reusable forms, route/path editors, comparisons and web-based visualization; clearer future remote-worker/API path. Limits: local host plus web asset deployment, two-language contracts, browser reconnection/stale state, and secure loopback launch/control access.

Bind locally by default. Use an application-scoped authenticated session, origin/CSRF checks and capability-limited commands; a web page must not supply arbitrary shell command text or unconstrained filesystem destinations. Named pipes need appropriate local access rules. Remote access is a distinct deployment mode with authenticated/TLS transport and worker identity.

### 7.3 Comparison and migration strategy

| Decision | Option A | Option B |
| --- | --- | --- |
| First Windows desktop experience | Strong | Strong with optional shell; browser dashboard also works |
| Forms/charts/comparison product growth | Native MVVM/chart work | React composition and web visualization |
| Native process management | Coordinator, same in both | Coordinator, same in both |
| Raw force capture/energy correctness | Same C++ work | Same C++ work |
| Remote workers | Add an API-facing host | Natural extension of host contract, still substantial work |
| Installation/runtime | .NET desktop package and RoR assets | .NET host, compiled web assets, optionally WebView2 |
| Engine view | Separate game window first | Separate game window first; synchronized web view later |
| First delivery scope | Smaller if permanently Windows-only | Slightly more boundaries; better long-term workbench flexibility |

Target an actively supported .NET LTS runtime at implementation time. On the research date, .NET 10 is active LTS under Microsoft's current policy; this is a proposed coordinator target, **not a verified installed SDK/toolchain**. Pin React, charting, transport and storage package versions only after a dependency/interop spike. [T02 · Current .NET support policy](https://dotnet.microsoft.com/en-us/platform/support/policy)

The reversible strategic choice is **native worker contract + UI-independent coordinator first**. Choose one UI for the alpha; implementing two full front ends at once would dilute physics and acceptance work.

## 8. Trial definition, execution and management

### 8.1 Definition versus realization

An experiment is an immutable revision of a template plus sweep/repetition policy. A realized trial resolves every asset, setting, seed and controller choice. A retry is a new attempt with its own artifacts, not overwriting the failed attempt.

| Contract group | Required information |
| --- | --- |
| Identity | Experiment/revision, trial/attempt, schema version, created-by context, parent sweep/repetition |
| Engine | Source commit, dirty patch hash/archive, executable hash, build/toolchain, observer/environment versions, worker capabilities |
| Asset closure | Vehicle/config/tuneup, skins if relevant, terrain, surface/fixture data, dependencies, hashes, licenses/redistribution metadata |
| Body/initial state | Actor cohort and linked bodies, pose, per-node mass/topology, payload, initial linear/angular velocity, engine/rotating states, settle criteria |
| Environment | Gravity and altitude datum; air profile; wind/gust/turbulence; seeds/field hash; particulate mode and physical/visual parameters; water/surface conditions |
| Controller/path | Waypoints/route, open-loop inputs or closed-loop target profiles, speed/acceleration constraints, actuators, controller gains/version/limits |
| Observation | Channels/cohorts, accounting and retention profiles, peak definitions, trigger windows, raw selection, buffer/disk limits, omission policy |
| Outcome/acceptance | Impact/flight window, preconditions, completion rules, tolerances, invalidation events, supported model coverage and required metrics |
| Execution/evidence | Wall/sim timeout, pause/cancel policy, worker lease, resource budget, screenshot/video settings, archive root and retention |

Keep **requested**, **resolved**, **applied**, and **observed** values separate. Archive the effective vehicle configuration and spawned topology. Partial asset name lookup or a fallback to the first configuration section cannot silently satisfy an exact requested setup.

Use a shared versioned schema and units library with generated .NET/TypeScript types where practical, but make the native worker perform its own capability and bounds checks. Examples in a later specification must distinguish omitted defaults from explicitly zero values.

### 8.2 Engine execution adapter

A startup adapter establishes an isolated portable profile, loads exact pinned content, creates known actor/fixture identities, verifies effective settings, settles the scene and arms observation. Existing scripts/AI can assemble early scenarios, but high-resolution control and reliable initial state need native, tick-safe extensions.

For a rigid initial translational/angular motion, the adapter can propose per-node velocity v_i = v_COM + ω×(r_i − r_COM) on the chosen free-node body. It must handle constrained nodes, internal modes, existing engine states and force-cache initialization explicitly. Do not use an RPM “boost” as a general velocity setter. Reject unsupported initial deformations or constrained configurations rather than pretending all fields are applied.

Schedule controllers and environment changes inside the worker on the integration clock. Remote/UI commands express intent with command IDs and target ticks; responses distinguish Received, Validated, Applied, Rejected and Finalized. Record the actual tick/phase applied. A late command has a declared reject/reschedule policy; never backdate it.

Begin with a simple native open-loop input timeline and a validated speed-tracking controller, retaining achieved speed/acceleration/path. Existing waypoint AI/autopilot remain optional controller adapters. Wall-frame input timing is not sufficient for a high-resolution repeatability contract.

### 8.3 State machine and result axes

Proposed phases: Draft → Validating → Queued → Provisioning → Loading → Settling → Armed → Running → Finalizing → Completed. Paused is an explicit substate of execution; cancelling drains capture before a terminal state.

Result classification is separate: **Accepted**, **Rejected**, **Failed**, **Cancelled**, **Partial**. Capture integrity, model coverage, calibration status and statistical repeatability are independent fields. A run can finish successfully as a process yet be rejected for a missed target velocity or unsupported energy channel.

Examples:

- Simulation crash: Failed; preserve last valid chunks and diagnostics.
- Normal finish with missing required capture sequence: Rejected or Partial by declared policy.
- Impact outside target approach-speed tolerance: Rejected even if video looks convincing.
- Complete exploratory capture with unsupported plastic-energy decomposition: Accepted only for metrics that explicitly exclude that claim.
- Pause/manual setup adjustment during an accepted impact window: record the event and apply the experiment's invalidation policy.

Initial execution uses a fresh process/profile per attempt. This avoids claiming a full reset interface before it exists. Later scene/actor reuse is an optimization gated by tests of state, force caches, RNG, scripts, controller and observer reset.

### 8.4 Queueing, sweeps and recovery

Support named experiment revisions, parameter sweeps, deterministic expansion order, repetition/seed plans, queue priority, worker resource leases, disk reservation, pause/cancel/retry, search/tags and immutable result comparisons. Bound sweep size and show the predicted trial count/storage/time envelope before enqueueing.

A worker has a capability matrix, executable identity and heartbeat. Native ticks emit progress; the coordinator uses monotonic wall time to detect stalls. A controller never waits for the next UI frame. Closing/reloading the UI leaves execution governed by a lease/owner policy in the coordinator; reconnect reconstructs status from the durable store.

Retries create new attempts, preserving the original failure and inherited definition. After coordinator/native crashes, reconcile journaled state, verify process identity with PID/start time/build handshake, recover valid chunk prefixes, and mark incomplete work. Do not infer success from an exit code or stale completed flag.

Start with one rendered worker per workstation. Parallel workers require GPU/window placement/capture contention, CPU/task-pool caps, content-cache isolation, sufficient sustained disk throughput and measured variation. Remote worker agents/fleet scheduling are optional later epics; multiplayer is not the trial runner.

## 9. Records, transport and live observability

### 9.1 Candidate record families

| Record | Contents / semantics |
| --- | --- |
| TrialResolved | Requested-to-effective settings, build/content/environment/controller versions, capability and topology maps |
| NodeState | Integration tick, actor generation/node ID, mass, pre/post position/velocity, active/constrained flags; state corrections identified |
| ForceContribution | Channel, feature/pair ID, generated and consumed epoch, actual applied vector/impulse, evaluation state reference |
| BeamStateTransition | Model/branch, endpoints, effective parameters, extension/rate, rest-length/yield/strength changes, final force, break/detach reason |
| ContactSample | Node/triangle or fixture identity, normal/tangent/penetration/material, relative velocity, branch forces, weights and actual application |
| EnvironmentUsed | Provider/config/field/seed version; sampled position/time; air velocity/density/temperature/pressure and coverage |
| BodyLedger | Cohort definition, p/L/K and supported U, integrated channel work/impulse, state-transition terms, residuals, coverage |
| TrialEvent / CommandApplied | Durable sequence, causal command ID, lifecycle/acceptance reason, actor generation and applied tick/phase |
| CaptureHealth | Produced/written sequences, queue high-water, omissions/gaps, writer latency, disk state, checksums and termination reason |
| LiveSnapshot | Summary window start/end, min/max/mean/integral/peak vector/tick, newest sample age, coverage and capture health |

Treat these as candidate contracts to refine, not a finalized protobuf/database schema. Use stable IDs plus actor-generation IDs so respawns cannot reuse old state identity. Schema and force-channel registries are versioned; an unsupported channel means Unknown, not zero. Non-finite values are flagged/rejected, not coerced into missing-free charts.

### 9.2 Native capture and files

First choice: a bounded in-process recorder with per-producer buffers and a native background writer, plus low-volume pipe summaries. Avoid transferring all raw values through JSON, HTTP or SignalR.

Use self-describing versioned binary blocks: header/endian/field layout, trial/build/schema identity, tick/sequence ranges, row counts, checksum, block payload, and commit marker. Chunk by time and byte limit, with small maximum uncommitted tail. Flush/fsync policy defines durability exposure; “enqueued” and “written” are not yet durable. A process crash may lose the tail; a power loss may lose more according to the selected flush policy.

Readers consume only finalized blocks/chunks. Use temp/staging names and finalization markers, plus recovery that scans valid prefixes and reports the missing range. The archive is append-only for raw evidence; derived analysis may be regenerated under a new version.

Parquet is suitable for finalized analytical datasets because it is columnar and widely supported. Convert outside the physics loop in bounded batches; do not depend on an unfinished Parquet footer for crash recovery. Choose a tested C++/managed converter after an interop spike, preserving types, null/unknown semantics and units metadata. CSV exports are conveniences, not the full raw representation. [T08 · Parquet overview and interoperability](https://parquet.apache.org/docs/overview/)

Shared memory with a versioned ring is an optional later raw-data path if native file ownership or copying becomes a measured bottleneck. It adds buffer ownership, atomic indices, ABI/layout compatibility, crash recovery and access-control work; a memory-mapped ring is not inherently durable or lossless.

### 9.3 Backpressure policy

Separate capture pressure from presentation pressure. The live feed may coalesce windows and resynchronize; authoritative capture cannot silently coalesce required ticks.

For an exhausted raw buffer, choose an explicit policy per profile: terminate/reject strict real-time trials; or pause/throttle only at a declared safe barrier for offline controlled stepping, with an event and changed wall-time semantics. A bounded queue cannot promise losslessness during an arbitrarily long disk outage. Never block inside a force callback.

Reserve space before launching, monitor write throughput/high-water/disk fullness, and stop with preserved evidence before uncontrolled overwrites. Ring space for pre-trigger history is distinct from the writer queue; overlapping impact windows must merge or reserve additional capacity. Required trigger history is verified after the event.

A slow UI gets newest summaries, timestamped gap notices and a durable event cursor; it does not delay the raw writer. Reconnect gets a current snapshot plus missing persistent events. Critical acceptance events must remain reconstructable after restart.

### 9.4 Data volume and sizing examples

For position, velocity and total force (nine float32 values), excluding all metadata:

| Example | Arithmetic | Payload rate | 10 min at real-time |
| --- | --- | --- | --- |
| 1,000 nodes at 200 Hz | 1,000 × 200 × 9 × 4 bytes | 7.2 MB/s | 4.32 GB |
| 100 selected nodes at 2 kHz | 100 × 2,000 × 9 × 4 | 7.2 MB/s | 4.32 GB |
| 1,000 nodes at 2 kHz | 1,000 × 2,000 × 9 × 4 | 72 MB/s | 43.2 GB |
| Above plus 8 force-channel vectors per node | 1,000 × 2,000 × (9 + 8×3) × 4 | 264 MB/s | 158.4 GB |
| Ten actors, 160-byte aggregate each at 2 kHz | 10 × 2,000 × 160 | 3.2 MB/s | 1.92 GB |

All MB/GB above are decimal, theoretical payload only. Contact/beam records, IDs, timestamps, environment values, indices, alignment and duplication add cost. Compression is workload-dependent. Rates scale with achieved simulated seconds per wall second, not just tick frequency.

At 72 MB/s, a 2 s raw pre-trigger history needs 144 MB plus metadata; a 512 MiB queue absorbs about 7.46 seconds of writer lag. At 264 MB/s the same queue covers about 2.03 seconds. A six-second full-node impact window is 432 MB before metadata. Do not assume RAM or disk headroom from the earlier hardware specification without benchmarking this load.

The report's bandwidth calculator is illustrative arithmetic, not a benchmark or a configured launcher.

## 10. Workbench feature set and user experience

### 10.1 Trial authoring

Provide an experiment workspace with versioned presets, exact asset/config selectors, payload/body cohorts, terrain/fixture selection, physical and visual environment panels, path/waypoint editing, target velocity/acceleration curves, controller selection, measurement profiles, outcome gates and sweep/repetition setup.

Show units at entry and output, parameter dependencies, supported bounds and capability errors. An environment feature with no active force-model coverage is visibly unsupported, not a successful slider. The resolved trial preview should show effective settings, expected capture volume, selected metrics and known limitations before launch.

Support save/duplicate/revise/import/export definitions, dry-run resolution, asset hash comparison and definition diffs. Treat user scripts/external content as executable/trusted extensions, versioned and explicitly selected; keep generated controller parameters separate from arbitrary code.

### 10.2 Live trial console

Suggested panels:

| View | Contents |
| --- | --- |
| Trial progress | Phase, current trial/repetition, simulation time/tick, wall time, playback speed, heartbeat, queue/resource state |
| Physical loads | Contact/beam/actor resultant vectors with world/body frame selector; current and peak loads, impulse and threshold duration |
| Energy ledger | Signed cumulative work, K/U, supported loss/transition channels, unclosed residual, scope/coverage/calibration badges |
| Environment | Requested vs applied provider/version, sampled wind/gust/density/temperature, particle mode and spatial sample location |
| Motion/control | COM speed/acceleration, route tracking, targets versus achieved values, steering/throttle/brake/propulsion |
| Structural state | Selected-node/beam force coloring, deformed shape, failures/detacher cascade and component timeline |
| Capture/evidence | Written versus produced ticks, gaps/omissions, raw queue/disk state, screenshots/video sync, warnings |
| Event timeline | Native physics transitions, command acknowledgements, environment versions and acceptance reasons |

Every live metric carries sample time/window, units/frame, reduction type and data freshness. Peak displays retain the actual vector and tick that produced the magnitude. Use a signed energy chart or balance table; a Sankey with all values forced positive would hide wind work and residual signs.

A native in-game overlay can provide synchronized scene force arrows for selected nodes/contacts, but it consumes an immutable observation snapshot. The separate workbench can initially show a simplified reduced node/beam scene. Limit glyph count, use cohort filters and scalable picking; sending every 2 kHz value into React component state is unnecessary.

### 10.3 Archive, comparison and governance of results

Provide search/filter/tags; trial/attempt history; definition/build/asset/environment diffs; synchronized charts/video/event cursor; selected raw-window inspection; sweep heatmaps and distributions; export reports/datasets; metric recomputation with analysis version; and configurable retention/pinning.

Comparisons must use compatible units, body boundaries, metrics, observer versions, calibration and capture coverage. Warn on differing assets or environment/controller versions. Show rejected/partial trials distinctly and keep them discoverable. Statistical repeatability requires enough repetitions and declared tolerances; one pleasing plot is insufficient.

## 11. Epics, dependencies and completion criteria

Sizes below are rough **engineer-week bands**, not commitments: S ≈ 2–4, M ≈ 4–8, L ≈ 8–16, XL ≈ 16–32+. Dependencies and acceptance work limit parallelism. They include implementation and local verification for the named scope; scientific calibration datasets, unknown content behavior and advanced coupling can expand them.

| Epic | Feature/subsystem scope | Dependencies | Completion evidence | Indicative size |
| --- | --- | --- | --- | --- |
| E01 — Measurement and capability contract | Units/frame/cohort/clock, peaks, ledger scope, accepted result rules, schema and unsupported states | User fidelity/pilot decisions | Reviewed contracts and hand-calculated fixtures; no ambiguous force/energy labels | S–M |
| E02 — Native epoch/force observer | Applied/generation epochs, gravity/reset/transfer hooks, channel registry, job ownership and consumed-force check | E01 | Per-tick sums match consumed forces; observation-off/on equivalence; initialization/sleep/reset tests | XL |
| E03 — Contact/beam/constraint detail | Branch contact forces/IDs, barycentric allocation, effective beam forces, break/detach and direct state corrections | E02 | Pair/boundary impulse tests; no double-count; transitions cover enabled pilot models | L–XL |
| E04 — Energy reducers and model coverage | K/p/L, work/impulse, linear storage/damping, nonlinear state transitions, internal reservoirs, explicit residuals | E01–E03 | Toy-rig closure/convergence; independent balance checker; coverage by model/version | XL |
| E05 — Capture and analytical archive | Buffers/pre-trigger windows, chunk recovery, integrity/gaps/durability, Parquet conversion and resource sizing | E01–E02 | Crash/disk-slow/full injection; strict trials rejected on missing required data; measured throughput | L |
| E06 — Coherent basic environment | Shared gravity/atmosphere/relative-airflow provider, legacy compatibility and migrated drag/wing/fuselage/propulsion paths | E01–E02 | Zero-wind regression; moving-air equivalence; density/gravity cross-subsystem checks | L–XL |
| E07 — Structured wind and particle exposure | Gust/shear/seeded correlated fields/imports; separate visual/passive particles and sampling provenance | E06; E05 for field records | Order-independent field tests; known gust response; transport/settling and exposure fixtures | L–XL |
| E08 — Trial execution/controller adapter | Exact resolution, initial state/settle/arm, tick input/controller, acknowledgements, completion and invalidation | E01–E02; E06 for environment claims | Repeated fresh-process trial; exact effective config; late command and target-tolerance tests | L |
| E09 — Coordinator and queue | Definitions/sweeps/revisions, leases/process/profile isolation, metadata, recovery, retries and artifact reconciliation | E01; E05/E08 contracts | Crash/restart/timeout/cancel paths preserve attempts; UI disconnect does not corrupt runs | L |
| E10 — Authoring workbench | Chosen WPF or React UI, asset/environment/path/profile editors, validation, diff/preview | E01/E09 | End-to-end create/resolve/launch flow; invalid configurations blocked; units/accessibility checked | L |
| E11 — Live telemetry and scene views | Snapshot/events, extrema-preserving charts, vector views, structural/env/capture panels and stale/resync state | E02/E04/E05/E09–E10 | UI overload/disconnect cannot lose raw capture; plotted peaks trace to raw ticks | L–XL |
| E12 — Analysis, comparison and evidence | Metric jobs, repeated-run statistics, archive browser, video/time correlation and portable reports | E04/E05/E09 | Raw-to-result reproducibility; accepted/rejected filtering; comparable cohorts/units/versions | L |
| E13 — Scientific/performance validation | Canonical fixtures, balances/convergence, asset calibration, observer perturbation and regression | Begins with E01, gates every epic | Published validation matrix and declared error/coverage envelope for each scenario | L–XL, ongoing |
| E14 — Scale and advanced physical coupling | Concurrent/remote workers, optional controlled/headless mode, two-way particles/wakes/thermal/surface models | Validated local pipeline and measured need | Resource/variance benchmarks; exchange conservation and model-specific validation | Separate expansion; XL+ |

These are overlapping work packages, not additive calendar estimates. E04/E13 are the critical scientific path. E10/E11 can develop against recorded fixtures/synthetic datasets while native work advances; all such UI development data must be labeled as fixtures, not measured trials.

## 12. Delivery strategies and planning envelope

### 12.1 Recommended staged delivery

| Stage | Scope | Exit gate |
| --- | --- | --- |
| S0 — Contract and integration spikes | Choose Option A/B; agree E01; map mutation coverage; measure recorder payload; compile schema/interop and UI-state prototype | Agreed supported model/pilot and measured bottleneck hypotheses |
| S1 — Narrow end-to-end alpha | One pinned ground rig/terrain, fresh-process trials, native epoch/force accounting, linear fixture energy, durable capture, constant atmosphere/wind, minimal chosen workbench | Repeatable accepted/rejected trials with source-built executable proof and closed toy-rig balances |
| S2 — Medium/high impact workbench | Contact/beam/constraint detail, event windows, model coverage/residuals, authoring/sweeps, live vector/energy views, crash recovery and comparison | Bounded error/overhead/retention envelope on selected impact scenarios |
| S3 — Atmosphere and flight expansion | Shared aero/propulsion adoption, shear/gust/correlated fields, aircraft asset calibration, passive particle exposure | Wind-load/flight validation and synchronized environment/energy reporting |
| S4 — Scale/advanced coupling | Only justified concurrency/remote/controlled stepping; two-way particles or other chosen models | Resource/variance/conservation gates for the expansion |

For staffing, assume **4–5 effective people**: two C++/physics engineers, one .NET/coordinator engineer, one UI engineer, plus 0.5–1 validation/physics-analysis capacity (some roles can overlap). As an initial planning envelope, a narrow alpha may be **12–18 calendar weeks**; a broad medium/high pipeline with the selected nonlinear models, atmospheric flight, mature trial management and credible validation may be **6–12 months**. These are judgment estimates before spikes, not promises or estimates for resolving every material/CFD/particulate model.

With one developer, the same programme is a substantially longer sequence; reducing UI polish alone does not remove accounting/calibration dependencies. Access to suitable assets/reference datasets, the number of supported model branches and required scientific error bounds are dominant schedule variables.

### 12.2 Alternative strategies

**Observer-first strategy:** establish native coverage and archive using a thin script/CLI supervisor before a polished workbench. This provides the earliest evidence on force/energy feasibility; use a skeletal UI for progress/status so end-to-end contracts are exercised. Appropriate if measurement correctness is the primary risk.

**Product-first parallel strategy:** build the coordinator and chosen workbench against labeled replay fixtures while two native engineers build the observer/environment. Freeze shared contracts early; gate live scientific claims until E13 passes. Appropriate if trial authoring/operator experience is equally important.

**Solver modernization strategy:** later introduce an explicit whole-world force-assembly/integrate barrier, controlled tick stepping or headless worker. This may simplify subsequent timing/throughput but changes numerical/control/contact ordering and could change outcomes. Take it only after observing the existing solver, with an A/B regression and convergence programme. Do not combine it silently with first instrumentation.

For the first implementation decision, select B + observer-first milestones with parallel minimal coordinator/UI development, unless the user prioritizes a permanently Windows-native application.

## 13. Validation, major risks and decisions still needed

### 13.1 Proposed validation matrix

| Test family | What it establishes |
| --- | --- |
| No-force/constant-force free node | Momentum and kinetic-work accounting against analytic/discrete reference |
| Uniform gravity / free fall | Applied gravity, timing and potential/work residual; zero/non-Earth gravity and fluid adoption boundaries |
| Linear beam/damper pair | Equal/opposite force, internal work, stored energy and damping behavior |
| Collision pair / supported barrier | Cohort impulse cancellation, normal/friction separation, contact IDs and externally held support |
| Plasticity/break/detach toy rigs | Exact transition capture and honest model-energy coverage; no implied fracture calibration |
| Rope/slide/immovable node fixtures | Direct-state correction and constraint/reaction accounting |
| Stationary/moving body in uniform wind | Relative-flow conventions, drag reference-area/density behavior, ambient-reservoir work |
| Wing/propeller/gust fixture | Shared atmosphere, propwash signs/lag, gust response and model coverage |
| Passive particulate transport | Known advection/settling, emission/deposition and no claimed two-way force in passive mode |
| Recorder failure injection | Slow/full disk, overflow, crash tail, partial chunks, loss counters and result rejection |
| Coordinator/UI failure injection | Restart, lease expiry, duplicate/late commands, disconnect/resync and attempt recovery |
| Repeated runs and observation perturbation | Variation versus defined tolerances under identical definitions; Off/Medium/High overhead and outcome differences |

Tests should compare independent analytical/discrete references and actual consumed state, not merely mirror the implementation. Lowering the physics time step or changing the mesh can be a diagnostic convergence experiment; it is not a routine user sampling slider.

### 13.2 Major risks and mitigations

| Risk | Consequence | Mitigation |
| --- | --- | --- |
| Phase/lag misattribution | Plausible but incorrect force/work traces | Generated/consumed epochs and channel-sum assertion at integration |
| Incomplete constitutive energy | “Absorbed energy” includes numerical/model artifacts | Supported/estimated/unclosed ledger and toy-rig validation |
| Observation changes timing/RNG/ownership | Different results or data races | Hot-path isolation, stable merge, per-field RNG design and paired repeated benchmarks |
| Partial environment adoption | Displayed wind/density differs across force models | Migration coverage mask, actual sample records and legacy mode |
| Full-rate channel explosion | RAM/disk overload and silent loss | Retention profiles, peak-preserving reductions, event windows and explicit backpressure |
| Arbitrary community assets | Uncalibrated masses/drag/materials and unstable comparisons | Pin dependencies, start with owned fixtures, calibrate selected assets |
| UI/coordinator too tightly coupled to solver | Crashes, blocked steps or reset ambiguity | Native process isolation, immutable snapshots, acknowledged barrier commands |
| Premature headless/distributed rewrite | Scope/correctness regressions before baseline | Local rendered worker first; optimize from measured need |
| Visual dust mistaken for physics | False particulate/environment claims | Distinct visual/passive/coupled modes with separate coverage |

### 13.3 Decisions for the detailed implementation specification

1. Which first two canonical scenarios: ground barrier impact plus free-fall/linear fixture, or flight/gust as a co-primary requirement?
2. Which physics claims must be calibrated at first delivery, and which remain exploratory? What reference data/error bounds define acceptance?
3. Choose A or B; confirm Windows-only local alpha versus immediate remote/multi-user requirements.
4. Approve actual observer/retention budgets: node counts, channel coverage, event-window duration, storage cap, duration and runtime/overhead limits.
5. Define closed-loop profile/path tolerances and whether exact initial angular/linear state is required for the pilot.
6. Select the initial nonlinear/constraint/drivetrain models in the energy boundary, and how unsupported terms appear.
7. Choose ENV-1/ENV-2 scope and particulate interpretation; coupled particles/CFD need separate requirements.
8. Set pause/cancel/reconnect/lease behavior, accepted-trial data-loss rules and archival/retention policy.
9. Confirm staffing and whether scientific validation/asset calibration can proceed alongside native/UI work.

This evaluation has enough detail to choose an architectural direction and a scoped programme. A final implementation specification should resolve these choices and pin contracts, tolerances, dependencies and milestone acceptance before code is started.

## 14. Evidence, references and limits

This is a documentation-only evaluation. Engine source and content remain at the original inspected revisions. Existing local foundation/research changes were preserved. No new simulator build, native run, framework install, performance benchmark or physical calibration was performed. .NET/React capabilities were checked in primary documentation; specific package/toolchain compatibility still requires a spike.

Local companions: [platform landscape](../../../platform.md), [engine map](../../../architecture.md), [baseline evidence records](../baselines/2026-10-08/README.md), [build/record procedure](../build-and-record.md), and [architecture evaluation records](2026-10-08/README.md).

The diagrams show proposed component boundaries and actual inspected solver ordering. The storage calculator uses transparent arithmetic. Neither is runtime measurement evidence.

### Source and primary technology references

- [A01 · Global physics loop, actor barriers and FreeForces](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorManager.cpp#L1247-L1320) — inspected local file source/main/physics/ActorManager.cpp, lines 1247–1320.
- [A02 · Actor force/integration ordering](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorForcesEuler.cpp#L46-L67) — inspected local file source/main/physics/ActorForcesEuler.cpp, lines 46–67.
- [A03 · Ground contact, integration, force reset and generic drag](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorForcesEuler.cpp#L1602-L1699) — inspected local file source/main/physics/ActorForcesEuler.cpp, lines 1602–1699.
- [A04 · Beam models, deformation, breakage and final applied forces](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorForcesEuler.cpp#L1210-L1465) — inspected local file source/main/physics/ActorForcesEuler.cpp, lines 1210–1465.
- [A05 · Ground collision and combined contact/fluid response](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/collision/Collisions.cpp#L1243-L1344) — inspected local file source/main/physics/collision/Collisions.cpp, lines 1243–1344.
- [A06 · Inter-actor contact and barycentric force distribution](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/collision/DynamicCollisions.cpp#L92-L115) — inspected local file source/main/physics/collision/DynamicCollisions.cpp, lines 92–115.
- [A07 · Wing airflow, propwash and density](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/flex/FlexAirfoil.cpp#L590-L678) — inspected local file source/main/physics/flex/FlexAirfoil.cpp, lines 590–678.
- [A08 · Fuselage airflow and drag](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorForcesEuler.cpp#L125-L149) — inspected local file source/main/physics/ActorForcesEuler.cpp, lines 125–149.
- [A09 · Turboprop density and force update](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/air/TurboProp.cpp#L222-L244) — inspected local file source/main/physics/air/TurboProp.cpp, lines 222–244.
- [A10 · Propeller airflow, blade forces and wash](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/air/TurboProp.cpp#L350-L432) — inspected local file source/main/physics/air/TurboProp.cpp, lines 350–432.
- [A11 · Jet thrust model](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/air/TurboJet.cpp#L227-L283) — inspected local file source/main/physics/air/TurboJet.cpp, lines 227–283.
- [A12 · Hull pressure/drag and water velocity](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/water/Buoyance.cpp#L69-L110) — inspected local file source/main/physics/water/Buoyance.cpp, lines 69–110.
- [A13 · Rope-linked node velocity/force replacement](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorForcesEuler.cpp#L1827-L1853) — inspected local file source/main/physics/ActorForcesEuler.cpp, lines 1827–1853.
- [A14 · Native physics step](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/SimConstants.h#L17-L21) — inspected local file source/main/physics/SimConstants.h, lines 17–21.
- [A15 · Wall-time batching and simulation clock](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorManager.cpp#L1120-L1234) — inspected local file source/main/physics/ActorManager.cpp, lines 1120–1234.
- [A16 · Native particle-system construction](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/gfx/DustPool.cpp#L39-L65) — inspected local file source/main/gfx/DustPool.cpp, lines 39–65.
- [T01 · WPF overview](https://learn.microsoft.com/en-us/dotnet/desktop/wpf/overview/) — primary documentation checked 2026-10-08.
- [T02 · Current .NET support policy](https://dotnet.microsoft.com/en-us/platform/support/policy) — primary documentation checked 2026-10-08.
- [T03 · SignalR streaming](https://learn.microsoft.com/en-us/aspnet/core/signalr/streaming?view=aspnetcore-10.0) — primary documentation checked 2026-10-08.
- [T04 · SignalR reconnect/configuration](https://learn.microsoft.com/en-us/aspnet/core/signalr/configuration?view=aspnetcore-10.0) — primary documentation checked 2026-10-08.
- [T05 · React UI model](https://react.dev/learn) — primary documentation checked 2026-10-08.
- [T06 · WebView2 introduction](https://learn.microsoft.com/en-us/microsoft-edge/webview2/) — primary documentation checked 2026-10-08.
- [T07 · Pipe operations in .NET](https://learn.microsoft.com/en-us/dotnet/standard/io/pipe-operations) — primary documentation checked 2026-10-08.
- [T08 · Parquet overview and interoperability](https://parquet.apache.org/docs/overview/) — primary documentation checked 2026-10-08.
- [T09 · SQLite WAL concurrency](https://sqlite.org/wal.html) — primary documentation checked 2026-10-08.
- [P01 · NASA drag equation and reference area](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/drag-equation/) — primary documentation checked 2026-10-08.
- [P02 · NASA simplified Earth atmosphere model](https://www.grc.nasa.gov/www/k-12/airplane/atmosmet.html) — primary documentation checked 2026-10-08.
