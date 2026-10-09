# Rigs of Rods platform landscape and trial-system evaluation

Research date: **2026-10-08**. Project: **bert-systems/rigs-of-rods-trials**, forked from **RigsOfRods/rigs-of-rods**. Source inspected: **e85535569102b6251849af574026984e3213b3f4**; starter content: **34fefdd126784bf87b068fc283f812525d159dd7**.

[Open the comprehensive HTML report](doc/project/reports/platform-evaluation-2026-10-08.html). [Project introduction](PROJECT.md). [Build and recording guide](doc/project/build-and-record.md).

## 1. Evaluation outcome

**RoR is a promising base for an exploratory vehicle-trial platform.** Existing source and scripting provide configurable deformable vehicles, terrains, controls, gravity, waypoint AI, node state, event callbacks, diagnostic tools, and recording hooks. The locally built fork already demonstrated scripted driving and evidence collection.

**The complete requested experiment system is not present as a ready-to-use subsystem in the inspected fork.** Reuse RoR's simulation and scripting, then add experiment management, controlled setup, consistent records, outcome analysis, and validation. This is an evaluation recommendation, not a finalized architecture or authorization to implement it.

**Impact-force peaks and energy dispersal are the major measurement gap.** Node momentum and kinetic energy can be derived from exposed masses and velocities. Reliable contact-force histories, impulses, beam work, deformation/break energy, and energy attribution need carefully placed solver instrumentation. Frame-level script samples and diagnostic getters do not establish those quantities.

**Physical ambient wind is a separate capability gap.** Scalar vertical gravity is exposed. The inspected wing/fuselage code derives airflow from node motion and propeller wash; a shared configurable ambient wind/gust field was not found. Visual cloud/water settings and an arbitrary node force are different physical models.

Use three evidence labels throughout:

| Label | Meaning |
| --- | --- |
| Source-supported | Binding, configuration, data structure, or implementation exists at the inspected commit. This session did not run every feature. |
| Runtime-demonstrated | The earlier source-built Daf/Simple2 driving scenario actually exercised it. |
| Proposed / needs validation | A composition, instrumentation change, analytical derivation, or scientific claim that remains to be designed/tested. |

No engine changes, trial-run implementation, or new physics experiments were performed during this research. The HTML diagrams and calculator explain concepts; they are not measured simulation results.

## 2. Research scope and provenance

The authority order is the local fork's implementation, its versioned content, official developer/game documentation, then explicitly marked evaluation inferences. The public developer portal advertises an older version label and a January 2026 generation date; exact names and semantics were checked in source instead of assuming the portal matches this commit. [D01 · Official developer portal](https://developer.rigsofrods.org/)

The tree already contained the locally saved foundation docs and README edit when research began. Engine source remained at the baseline commit. A [source inspection record](doc/project/research/2026-10-08/source-inspection.json) records identity, asset hashes, and scope; a [binding inventory](doc/project/research/2026-10-08/binding-inventory.json) provides a mechanical index of registrations. Conditional/dynamic registrations and overloaded methods require direct review; the index is not a runtime conformance test.

The earlier proof remains at `D:\Rigs of Rods\source-build-2026-10-08\report\index.html`: one 36-second ground-vehicle session, three screenshots, 35.3-second video, and position/wheel-speed telemetry. It validates that source build and scenario, not wind, flight, force accuracy, or deterministic repeated trials. [Baseline records](doc/project/baselines/2026-10-08/README.md).

The community resource catalog at `https://forum.rigsofrods.org/resources/` returned an anti-bot denial during research. We could verify supported categories and bundled assets, but not exhaustively inspect current downloadable assets, licenses, or compatibility. No catalog counts or third-party asset certification are claimed.

## 3. Platform capabilities

### 3.1 Simulation domains

| Domain | Existing landscape | Relevance to experiments | Boundary |
| --- | --- | --- | --- |
| Cars, trucks, buses, trailers | Node/beam chassis, wheels, suspension, drivetrain, braking, differentials, loads and articulated combinations | Acceleration, braking, handling, mass distribution, rollover and impact scenarios | Asset parameters govern results; representative appearance is not calibration |
| Aircraft | Wings/control surfaces, airfoils, propeller/piston/turboprop/jet propulsion, airbrakes, flaps, autopilot | Takeoff, climb, flight path, maneuver, landing, structural failure | Simplified aerodynamic models; wind/atmosphere configuration and validation are incomplete for this use case |
| Boats | Deformable hulls, submesh-based buoyancy, screw propulsion, water/wave systems | Buoyancy, water contact, propulsion and coupled land/water trials | Not a general fluid/CFD solver |
| Rail and tracked vehicles | Node/beam mechanisms, wheels and slide-node/rail constraints; tracked constructions are content-driven | Mechanical linkage and constrained-motion studies | Detailed mechanisms require suitable content and validation |
| Machinery and non-drivable structures | Commands/hydraulics, ropes, hooks, ties, slide nodes, loads, fixed actors | Lifting, towing, payload transfer, structural response and coupled actors | Constraints and external support forces must be part of the measurement boundary |
| Sandbox interaction | Multiple actors, terrain objects, player control, scripting and multiplayer | Scenario assembly and visual inspection | Multiplayer/AI restrictions make single-player the simpler trial baseline |

Vehicle construction is a lumped node/beam network: nodes carry mass/state, while beams act as axial spring/damper connections. Elastic deformation, plastic changes and breakage follow parameters and solver logic. This provides useful deformable dynamics, but is not automatically a continuum finite-element/material model. [S01 · Source: node and beam data](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/SimData.h#L250-L338) [D02 · Official node/beam concepts](https://docs.rigsofrods.org/vehicle-creation/vehicle-concepts/)

Aircraft and boat support are documented separately; using those subsystems does not establish flight-test or hydrodynamic accuracy. [D12 · Official aircraft creation guide](https://docs.rigsofrods.org/vehicle-creation/aircraft-and-aerodynamics/) [D13 · Official boat creation guide](https://docs.rigsofrods.org/vehicle-creation/boats/)

### 3.2 Content and configuration layers

A vehicle setup includes more than its filename:

| Layer | Data to identify and preserve |
| --- | --- |
| Base definition | Exact .truck/.trailer/.airplane/.boat/.load/.machine/.fixed file, resource bundle, hash and dependencies |
| Section/module configuration | Selected configuration name; engine can fall back to the first section if the requested one is invalid |
| Physical parameters | Node mass/distribution, beam stiffness/damping/yield/break thresholds, wheel/suspension/drivetrain/aero values |
| Loaded/coupled state | Payload, trailer, hook/tie/rope/rail links and actor IDs |
| Addons/tuneup | Applicable .addonpart/.tuneup data, conflicts, edited parameters and resulting topology |
| Visuals | Skin, mesh/material variants, dashboard and camera settings; visual changes need not change physics |
| Live overrides | Mass APIs, ActorSimAttributes, controls and persistent FreeForces, with time/order recorded |
| Initial state | Spawn pose, settled node state, engine/gear/brakes, link state, initial velocities and deformation |

The tuning feature supports addons, visual toggles and saved tuneups. Do not assume every cosmetic replacement changes the underlying node/beam model or tire characteristics. [D11 · Official tuning guide](https://docs.rigsofrods.org/gameplay/tuning/)

The ActorSimAttr enum exposes traction-control and engine/transmission/turbo/aircraft/boat propulsion settings. It is a finite list, not arbitrary access to every spring, beam or environmental property. Indexed attributes are used for multi-engine propulsion settings. [S09 · Source: supported simulation attributes](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/SimData.h#L924-L978) [S32 · Source: multiplayer guard and attribute-change events](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/Actor.cpp#L5110-L5127)

Mass setters and node mass options are exposed independently. Changing mass/stiffness may change numerical stability and the scenario's dynamics; preserve the effective values and verify the model after setup. [S08 · Source: actor telemetry and control bindings](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/scripting/bindings/ActorAngelscript.cpp#L135-L225)

### 3.3 Terrain, surfaces and environment

Terrn2 describes geometry, starting location, water, gravity, sky/render configuration, objects, scripts, traction maps and other terrain-specific data. Terrain geometry, placed objects, collision geometry and physical ground models must be identified together. [D04 · Official terrn2 format](https://docs.rigsofrods.org/terrain-creation/terrn2-subsystem/)

| Component | Existing control | Experiment interpretation |
| --- | --- | --- |
| Geometry and objects | Terrn2/OTC/TOBJ/ODEF, height maps, collision meshes, procedural roads, object/editor APIs | Terrain slope, collision shape and placement are experimental inputs |
| Gravity | Terrain value and game.getGravity()/setGravity(float); Earth preset -9.81 | Scalar acceleration on world Y; not an arbitrary 3D gravity vector |
| Ground/traction | Landuse mapping and ground_models.cfg with static/sliding friction, adhesion, Stribeck behavior and fluid parameters | Friction/mud experiments are feasible with pinned physical surface assignments |
| Water | Water line/height APIs and terrain/wave settings | Water contact is separate from visual water quality |
| Sky/time | SkyX/Caelum/render settings and available time controls | Primarily presentation; inspect physical coupling before treating a visual setting as an environmental force |
| Ambient wind/gusts | No shared physical wind-field setter found in inspected game bindings/aerodynamic paths | Requires a defined airflow model and likely engine changes |
| Atmosphere | Wing/fuselage code contains altitude-dependent air-density approximation | No general validated pressure/temperature/humidity editor found for trials |
| External forces | Persistent node FreeForces | Useful controlled actuator/disturbance; not equivalent to an aerodynamic wind field |

World Y is up; gravity is signed and normally negative. Ground fluid buoyancy in the inspected collision path uses DEFAULT_GRAVITY rather than the terrain's live gravity. The local camera g-force calculation divides by terrain gravity. Thus zero/altered gravity requires explicit cross-subsystem validation, particularly fluids and g-force telemetry. [S25 · Source: collision reaction and friction calculation](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/collision/Collisions.cpp#L1265-L1344) [S05 · Source: local camera g-force calculation](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/Actor.cpp#L4529-L4548)

A visual mesh movement is not proof of a moved collision shape. Verify the chosen editor/object operation updates physical geometry and rebuilds relevant caches when a trial fixture moves.

## 4. Assets and terrains available to this fork

### 4.1 Versioned starter inventory

The inspected content submodule contains **three terrain definitions, three truck definitions and two trailer definitions**. The main repository's resources additionally contain **six .fixed definitions**. These are definition-file counts, not a count of successfully loaded or scientifically validated assets. [D17 · Starter content repository at the inspected revision](https://github.com/RigsOfRods/content/tree/34fefdd126784bf87b068fc283f812525d159dd7)

| Asset | Definition | Trial value |
| --- | --- | --- |
| Simple Test Terrain | simple2.terrn2 | Existing baseline drive; simple setup and debugging |
| Simple Test Terrain Asphalt | simple2_a.terrn2 | Ground/traction-focused trials; verify its landuse mapping and surface model |
| Simple Test Terrain Water | simple2_w.terrn2 | Water/contact scenarios; waterline is 100 and spawn is above it |
| Daf Semi truck | b6b0UID-semi.truck | Source-built driving already demonstrated; engine/load/coupling candidate |
| Bus RVI Agora S | 95bbUID-agoras.truck | Second vehicle class for controlled comparison |
| Bus RVI Agora L | 95bbUID-agoral.truck | Alternate bus geometry and mass configuration |
| Semi trailer (37tons) | b6b0UID-semi.trailer | Articulated/load transfer studies; name is not a verified effective measured mass |
| Flatbed semi trailer | b6b0UID-semiflat.trailer | Payload and coupling scenarios |

Exact file hashes are in the source inspection record. A complete content identity must also hash referenced configuration, meshes/collision assets, airfoil data, materials and any scripts that influence physics.

No .airplane or .boat definition was found in this starter content inventory. The engine supports those domains, but a flight/boat evaluation needs a curated external asset or an intentionally constructed test rig.

### 4.2 Broader ecosystem and useful tools

The documented mod landscape covers vehicles, trailers/loads, terrain/static objects, skins, dashboards, addons/tuneups and gadgets. Suitable trial terrain families include flat pads, tracks, slopes, roads, off-road surfaces, ramps, barriers and water/airport environments. That is a selection taxonomy, not a verified installed catalog. [D10 · Official scripting features overview](https://developer.rigsofrods.org/d7/d61/_scripting_features_overview_page.html)

The official AI guide uses F1 Test Track, Bajarama V2 and Rock Falls Raceway as examples. They are candidate leads, not pinned/downloaded trial fixtures in this workspace. Community-maintained waypoint presets can be loaded locally rather than fetched dynamically. Freeze any selected preset file/version with the trial. [D05 · Official vehicle AI guide](https://docs.rigsofrods.org/gameplay/vehicle-ai/) [D06 · Community-maintained waypoint presets](https://github.com/RigsOfRods-Community/ai-waypoints)

Bundled gadgets include a script editor, rig/road/ODEF editors, OGRE/overlay inspection, an alpha Engine Tool, an alpha Shock Tool, and TerrnBatcher. Engine/Shock tools are useful diagnostic starting points. TerrnBatcher concerns static mesh/material batching, not experiment batches. [S35 · Source: engine diagnostics gadget](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/resources/gadgets/engine_tool.gadget#L7-L17) [S36 · Source: shock diagnostic samples](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/resources/gadgets/shock_tool.as#L178-L191) [S37 · Source: terrain mesh batcher role](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/resources/gadgets/terrn_batcher.as#L1-L15)

For trial assets, curate a small initial set with: provenance/license, bundle/dependency hashes, units, expected mass, coordinate conventions, node groups/measurement locations, surface assignment, calibration evidence, and compatible engine revision. Keep author-controlled simple fixtures for validation. Community content can support exploratory comparisons; it does not arrive as certified physical data.

The source content repository includes a GPL license file; community assets have their own author/license conditions. Asset redistribution must be assessed per selected bundle, rather than inferred from the engine's license.

## 5. Existing control and automation surfaces

### 5.1 Startup, spawning and actor lifecycle

The CLI supports -map/-terrain, -truck, -truckconfig, -pos, -rot, -runscript, -enter, -resume and -checkcache. No dedicated headless experiment/batch command was found in the inspected options. RoR's normal entry point runs a render/event loop; this report has not verified renderer-free execution. [S23 · Source: supported launch arguments](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/system/AppCommandLine.cpp#L52-L135)

The source-supported spawn message is **MSG_SIM_SPAWN_ACTOR_REQUESTED**. It accepts a filename, position and quaternion rotation, with optional configuration, skin, entry flag and instance ID. Some public overview prose uses a different historical spelling; use the inspected bindings/dispatch code. [S11 · Source: actor spawn validation and fallback](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/scripting/GameScript.cpp#L1583-L1639) [S12 · Source: bound message types](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/scripting/bindings/MsgQueueAngelscript.cpp#L35-L116)

Two important reproducibility behaviors: lookup allows a partial filename match, and an invalid configuration may be logged and replaced by the first available configuration. A future trial runner should resolve exact asset identity and reject unintended effective configuration, rather than accept a plausible-looking launch. Spawn placement can also be adjusted by the engine; verify the realized node pose.

The earlier CLI -enter issue is preserved in project memory. The successful baseline used diag_preset_veh_enter=true. It remains a workaround; the message-based spawn path has its own entry flag and should be checked independently.

### 5.2 Journey, pathing, speed and acceleration

| Mechanism | What it offers | Suitability |
| --- | --- | --- |
| Scripted input schedule | Per-actor simulated throttle, brake, steering and other events; persistent values must be cleared | Repeatable control intent and useful low-complexity trials |
| Waypoint AI | Waypoint list, activation, events, speed/power values at waypoints | Route-following experiments; actual trajectory/speed must be measured |
| Built-in AI modes | Normal, race, drag race, crash, chase; repeat paths and multiple vehicles | Rapid scenario exploration and visual repeated runs |
| Flight autopilot | Heading, altitude, vertical-speed, IAS and related modes | Basic flight control experiments after selecting/calibrating an aircraft |
| Engine APIs | Gear, clutch, throttle, start/stop, RPM and finite simulation attributes | Setup and controller composition; not an arbitrary vehicle velocity setter |
| FreeForces | Persistent forces applied to specified actor nodes | Controlled actuator/fixture forces; timing is frame-requested and applied by physics |

AI speeds are km/h for land vehicles and knots for boat/aircraft settings. The native route controller supports AI_SPEED and AI_POWER per waypoint. Target speed is a controller setting, not a guaranteed state. Normal/race/chase modes have different path/turn/obstacle behaviors; a path can be missed. Aircraft AI altitude is not a complete 3D waypoint mission planner. [D05 · Official vehicle AI guide](https://docs.rigsofrods.org/gameplay/vehicle-ai/) [S26 · Source: waypoint and per-waypoint control bindings](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/scripting/bindings/VehicleAiAngelscript.cpp#L34-L56) [S27 · Source: waypoint speed and power setters](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/gameplay/VehicleAI.cpp#L134-L150) [S28 · Source: flight autopilot bindings](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/scripting/bindings/AutopilotAngelscript.cpp#L31-L52)

A desired acceleration curve must become a feedback-control objective or a declared force actuator. Throttle percentage does not prescribe acceleration. No generic actor/node initial-velocity setter appeared in the inspected bindings; boostCurrentTruck changes engine RPM, not translational velocity. Saved scenes include velocities and could be investigated as an initial-state mechanism, but editing/restoring one is not a verified trial API.

Distinguish **control replay**, **tracking a requested state**, and **imposing an artificial state**. They answer different physical questions. For impacts, accept a run based on observed approach velocity/orientation at a defined gate, not merely requested throttle/speed.

### 5.3 Persistent force actuators and synthetic fixtures

FreeForces support constant-direction, toward-coordinate, toward-node and half-beam types. A FreeForce affects one node; a complete two-sided artificial beam needs matching opposite half-beams. Add/modify/remove requests and freeforce activity events are available. [D07 · Official FreeForces description](https://developer.rigsofrods.org/d0/dde/_free_forces_page.html) [D08 · Official FreeBeams description](https://developer.rigsofrods.org/d5/d34/_free_beams_page.html) [S14 · Source: persistent force and half-beam calculation](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorManager.cpp#L1624-L1768)

For constant forces, the solver adds force_magnitude times direction to the node accumulator. Normalize direction and record units as force in newtons. The public FreeForces text uses a confusing Newton/meters label; that should not be carried into trial units. Torque uses N·m, while beam stiffness uses N/m.

These are persistent effects, not a script-call impulse API synchronized to a single physics tick. A duration-limited actuator needs defined activation/removal tick semantics. Record actuator work and its effect on the system boundary; a one-node external force can inject linear and angular momentum.

### 5.4 Existing trial-like systems

| Existing subsystem | Reuse | Missing for the requested system |
| --- | --- | --- |
| Vehicle AI and local waypoints | Paths, repeats, multi-actor driving/crash setups | Frozen experiment identity, acceptance gates, rich measurements and outcome records |
| Race system/checkpoints | Route/checkpoint events, timing, lap/results infrastructure | General experiment semantics and physics accounting; manipulation rules can invalidate races |
| Replay | Node position/velocity samples and broken/disabled beam flags | Durable full-rate force/energy export, experiment orchestration and complete restart state |
| Save/load scene | Vehicle/control/link/node/beam state persistence | Proof of full simulation-state restoration, RNG/wind/profile reset and consistent cross-version meaning |
| Gadgets/scripting | Configurator, controller and diagnostics UI | A complete experiment registry, batch queue and robust result storage |
| OutGauge | External dashboard stream | Node/contact/beam physics and high-bandwidth impact events |
| Dedicated server | Multiplayer/session services | Not established as a substitute for a client physics experiment worker |

A combined script/gadget could reuse much of this control surface. No complete requested experiment harness was found in the inspected source/resources or official materials searched. This is a bounded research finding, not a claim that no community project exists anywhere. [S34 · Source: bundled race management](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/resources/scripts/races.as#L1-L70) [D14 · Official race script generator](https://docs.rigsofrods.org/terrain-creation/race-generator/) [S20 · Source: replay samples and beam flags](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/gameplay/Replay.cpp#L183-L211) [S21 · Source: saved node and beam state](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/Savegame.cpp#L719-L763) [D16 · Official dedicated-server repository](https://github.com/RigsOfRods/ror-server)

## 6. Telemetry, event streams and logging

### 6.1 Available measurements and their semantics

| Quantity | Existing access | Meaning / caution |
| --- | --- | --- |
| Actor position/orientation | getPosition(), getOrientation(), heading/rotation methods | Position may be a camera-selected node or unweighted average; not guaranteed center of mass |
| Scalar speed | getSpeed(), getWheelSpeed() | getSpeed derives from the actor reference-position change; wheel speed is a separate drivetrain/wheel reading |
| Node position/velocity/mass | getNodeCount(), getNodePosition(), getNodeVelocity(), getNodeMass() | Useful basis for mass-weighted motion/energy; sample all selected nodes coherently |
| Node force accumulator | getNodeForces() | Mutable solver accumulator; not a saved per-step contact/net-force sensor |
| Camera g-force vector | getGForces() | Local camera axes, batch averaging/smoothing, gravity normalization; not raw world acceleration or peak impact load |
| Actor mass | getTotalMass(bool), dry/loaded/initial mass methods | Linked actors may be included; define actor cohort and avoid double counting |
| Shock state | Count, spring rate, damping, velocity and endpoint IDs | Exposed diagnostics; does not represent all beam stress/work channels |
| Engine/controls | RPM, gear, torque-related APIs, throttle/clutch, flags and input state | Useful operational telemetry; verify per-function units and nominal/instantaneous meaning |
| Flight/boat components | Propulsion/autopilot component APIs | Useful control/status; force decomposition still needs solver observation |
| Beam state | C++ beam fields; selected flags in replay/savegame | No general public all-beam force/work time-series exporter found |

getPosition() is explicitly camera-mode-dependent. getTotalMass(true) adds linked actor masses. A mass-weighted center of mass and momentum therefore require an explicit node/actor cohort rather than multiplying an arbitrary displayed position/speed by a total mass. [S04 · Source: actor reference position and camera-dependent averaging](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/Actor.cpp#L1166-L1193) [S08 · Source: actor telemetry and control bindings](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/scripting/bindings/ActorAngelscript.cpp#L135-L225)

**Critical force-reading trap:** getNodeForces() returns ar_nodes[n].Forces directly. CalcNodes integrates velocity/position, then resets Forces to gravity for the next loop. Other passes can add later/carry-over contributions. A script reading that accumulator sees its phase-dependent contents, not an archived complete pre-integration force, and cannot infer peak collision load from its name. [S03 · Source: node mass, velocity and force getters](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/Actor.cpp#L4854-L4900) [S02 · Source: node integration and force reset](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorForcesEuler.cpp#L1602-L1675) [S14 · Source: persistent force and half-beam calculation](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorManager.cpp#L1624-L1768)

The source has camera/force-feedback sensors and last-collision diagnostics, but their purposes, smoothing, channels and availability differ. They are useful evidence of internal data, not a ready research telemetry contract. [S05 · Source: local camera g-force calculation](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/Actor.cpp#L4529-L4548) [S25 · Source: collision reaction and friction calculation](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/collision/Collisions.cpp#L1265-L1344)

### 6.2 Three clocks and sampling limits

Physics uses a fixed **0.0005 s step**, equivalent to a nominal **2,000 steps per simulated second**. It runs batches whose size depends on frame elapsed time, simulation-speed settings, remainders and pause/sleep state. Batch input time is clamped before scaling. A fixed step does not imply constant wall-clock throughput or bit-identical repetitions. [S33 · Source: fixed step and compile-time limits](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/SimConstants.h#L20-L37) [S06 · Source: frame batching and fixed-step accumulation](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorManager.cpp#L1120-L1234)

At the start of the main loop, pending physics is synchronized. Script frameStep(float) runs before new actor physics tasks launch; this is a suitable existing point for coherent frame-level node reads. It is not called once for every 0.5 ms substep. [S07 · Source: synchronized scripting before new physics tasks](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/main.cpp#L2196-L2237)

game.getTime() uses ActorManager's accumulated simulation time; frameStep's dt and video timestamps serve different roles. Record wall time, simulation time/tick and media time separately. Use actual timestamp differences for derivatives, account for pauses/scaling, and preserve tick counts in any native observer.

At 60 rendered frames/s, a script nominally samples every 16.7 ms, spanning roughly 33 physics substeps at 1× speed. A 5 ms collision pulse can fit entirely between those samples. More CSV rows cannot recreate missing physics samples; repeatedly polling the same frame is not increased solver bandwidth.

### 6.3 Events and messages

Scripts register for events and receive eventCallback/eventCallbackEx payloads. Existing families include eventbox entry/exit, player/vehicle entry/exit, engine death/fire, water contact, actor creation/deletion/reset/teleport, input-related toggles, linking changes, freeforce changes/deformation/breaks, script diagnostics/exceptions and resource activity. [S13 · Source: event definitions and payloads](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/gameplay/ScriptEvents.h#L29-L132)

An eventbox crossing is a region/trigger event, not automatically a collision impulse or contact-force record. Freeforce half-beam break events do not constitute a universal break stream for every ordinary vehicle beam. No general every-contact/every-beam energy event stream was found in the inspected event enum.

Messages request lifecycle/control operations through the main queue. They are asynchronous requests, not transactions with a complete experiment acknowledgement and durable event log. A future harness needs correlation IDs, effective-state confirmation, timestamps and terminal outcomes where current events do not supply them. [S12 · Source: bound message types](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/scripting/bindings/MsgQueueAngelscript.cpp#L35-L116) [S11 · Source: actor spawn validation and fallback](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/scripting/GameScript.cpp#L1583-L1639)

### 6.4 Existing logs and export mechanisms

| Channel | Existing behavior | Trial use |
| --- | --- | --- |
| RoR.log | Startup, content, rendering, configuration and runtime diagnostics | Preserve full raw log and classify warnings/failures |
| Angelscript.log / game.log | Script diagnostics and explicitly emitted data | Good for orchestration breadcrumbs or an initial low-rate recorder; log text is not a typed telemetry schema |
| Script text resources | Read/write text through OGRE resource groups; filenames cannot contain paths | Possible buffered CSV/JSON export into a writable group, with return-value/error checks |
| LocalStorage/.asdata | Persistent key/value-style script storage | Settings/metadata, not a full impact waveform pipeline |
| Replay | Configurable history sampling with node state/beam flags | Visual debugging and selected state recovery, not force/energy accounting |
| Savegames | Node position/velocity plus beam/configuration state | Candidate setup/reset asset; prove restoration semantics |
| Screenshots/video | Native requests and external capture | Visual evidence correlated to physical/experiment timestamps |
| OutGauge | Windows/SocketW UDP packet for player vehicle dashboard | Lightweight external monitoring; not the primary measurement bus |

OutGauge populates wheel speed, RPM, gear, turbo, controls and lights. Engine temperature, fuel, oil pressure and oil temperature are zero placeholders in the inspected sender. Packet time uses the renderer timer. Its interval checks 0.1 times io_outgauge_delay, so the default 10 means approximately one second before frame quantization—not 10 ms. UDP delivery and the current player/engine dependency limit its role. [S18 · Source: OutGauge interval, data fields and sender](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/network/OutGauge.cpp#L103-L202) [S19 · Source: OutGauge packet field definitions](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/network/OutGauge.h#L87-L118) [S22 · Source: runtime configuration variables](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/system/CVar.cpp#L32-L198)

The text-resource API is resource-group-based and checks writable streams; it does not offer arbitrary absolute-path file output. Buffering/chunking and a supervisor that copies finalized artifacts would need design, rather than repeatedly overwriting whole data files every substep. [S30 · Source: script text-resource creation and path restrictions](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/scripting/GameScript.cpp#L2044-L2191)

Telemetry should distinguish observations, commanded inputs, effective configuration, engine events and derived metrics. Native instrumentation would need typed records, actor/node/beam identity, units/frame/phase, source hashes, sequence/tick IDs, and explicit dropped-data counters.

## 7. Physics measurements: what is defensible

### 7.1 Define the body, frame, units and time first

A trial must declare its measurement boundary: one actor, a linked vehicle/trailer set, selected structural nodes, a whole closed system, or a vehicle against an externally supported ground/barrier. Include fragments or explicitly account for mass leaving the cohort. Actor deletion, teleport, reset, mass changes and artificial actuators are discontinuities, not ordinary collision outcomes.

Use a declared world frame with Y up, SI units, and separate sensor/body axes. Preserve transform conventions and reference point. Engine outputs mix km/h, knots, RPM, kN, kW and dimensionless settings; normalize on export with original units retained. Record actual simulated time, rather than treating video frame time or requested control duration as the physics clock.

### 7.2 Kinematics, momentum and kinetic energy

For a defined set of mass-bearing nodes i with positions r_i, velocities v_i and masses m_i:

```text
M       = sum(m_i)
r_COM   = sum(m_i * r_i) / M
v_COM   = sum(m_i * v_i) / M
p       = sum(m_i * v_i)                         [kg m/s]
K_nodes = 0.5 * sum(m_i * dot(v_i, v_i))         [J]
K_COM   = 0.5 * M * dot(v_COM, v_COM)            [J]
L_COM   = sum((r_i-r_COM) cross (m_i*v_i))       [kg m²/s]
a_COM   ≈ change(v_COM) / actual change(time)    [m/s²]
```

These are proposed derived measurements, supported by exposed node state. They have not been runtime-validated in this session. Exclude zero/invalid masses appropriately, audit immovable/virtual components, verify totals against the intended body, and avoid counting a linked actor twice. Internal/rotating/deforming motion can make K_nodes exceed K_COM; the latter alone is not the total kinetic energy of a deformable vehicle.

For fixed-mass cohorts, a momentum change gives **net external impulse**, J_net=change(p), and average net external force over a defined interval, F_mean=change(p)/change(t). This does not by itself isolate barrier contact from gravity, tire friction, aerodynamic loads, propulsion, constraint reactions, or measurement error.

Angular momentum from node state is useful for rollover/flight evaluation. It still needs a clear reference point, included bodies and any separately represented rotating state. Source fields for propulsion/rotation may need additional accounting beyond a generic node sum.

### 7.3 Impact-force vectors and impulse

Measure approach velocity at a plane/gate before contact, contact interval, force vector/sign convention, contacted fixture/body, net/contact impulses, rebound, deformation and post-contact state.

For a contact channel with force vector F_contact at each solver tick:

```text
J_contact ≈ sum(F_contact[tick] * physics_dt)
F_peak    = maximum magnitude over the defined channel/window
```

Peak resultant force, component peaks and the sum of individual node peak magnitudes are different statistics. A trustworthy exporter must say which it reports and whether multiple contacts are summed. Integrate matched samples to check momentum balance, including other external loads.

The collision code has reaction/friction computations and per-node diagnostic state, so adding a meaningful observer has identifiable source locations. However, the live force accumulator and frame-level script callback do not provide a reliable complete contact waveform. Native sampling must specify the phase before force reset, account for actor/ground/inter-actor passes, and avoid double counting pairs or one-step carry-over contributions. [S25 · Source: collision reaction and friction calculation](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/collision/Collisions.cpp#L1265-L1344) [S02 · Source: node integration and force reset](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorForcesEuler.cpp#L1602-L1675) [S14 · Source: persistent force and half-beam calculation](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorManager.cpp#L1624-L1768)

A 0.5 ms sample is still a discrete numerical sample, not an infinitely resolved real-world force peak. Contact duration, smoothing, geometry, material parameters, solver approximations and convergence all affect the interpretation.

### 7.4 Beam force and deformation

The solver's beam field named stress stores a signed axial **force-like value**, computed from spring extension and damping velocity. Do not label it material stress in Pa/MPa without a defined physical cross-sectional area and calibrated material model. Plastic changes modify rest length/thresholds, and breakage disables load transmission according to source rules. [S15 · Source: beam force, yield and break processing](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorForcesEuler.cpp#L1317-L1445)

For a simple linear elastic beam with constant stiffness k and unchanging rest length L0, an illustrative stored energy is U=0.5*k*(length-L0)^2. For a passive linear dashpot c, dissipation rate is c*(relative axial velocity)^2. Actual shocks, bounded beams, ropes, actuated beams, plastic changes and break logic require their own model-consistent accounting. Do not apply the simple formula universally.

A deformation visualization, count of broken beams or final crush distance can be a useful exploratory outcome. Those are not equivalent to energy absorbed by calibrated real materials.

### 7.5 Energy dispersal and the missing ledger

A useful energy balance would track:

| Channel | Interpretation | Current assessment |
| --- | --- | --- |
| Translational/internal/rotational kinetic energy | Motion of the selected cohort | Node-derived estimates feasible; explicit rotating-state audit required |
| Gravity/potential work | Position change in the declared field | Derivable with fixed gravity/mass/reference; handle altered gravity coherently |
| Beam elastic storage | Recoverable strain energy | Needs effective topology, stiffness, rest length and model-specific sampling |
| Damping dissipation | Mechanical energy removed by damping terms | Needs solver-term work/power integration |
| Plastic deformation | Irrecoverable changes to model state | Needs defined model accounting at yield/rest-length changes |
| Breakage and fragments | Transfer/removal/release of energy when connectivity changes | Needs before/after state and bookkeeping; not a universal fracture-energy material law |
| Contact/friction/constraints | Work/impulse exchanged with ground, barrier or other actors | Needs per-channel observer and explicit external bodies/reactions |
| Aero/water loads | Energy transferred through simplified air/fluid models | Needs subsystem-specific force/work channels |
| Engine/hydraulic/FreeForce work | Added/removed actuator energy | Needs logged controls and measured work, not nominal engine power alone |
| Numerical/residual balance | Unaccounted change after declared terms | Must remain visible; not relabeled as physical dissipation |

A reduction in kinetic energy is **not automatically impact energy absorbed by the vehicle**. Energy may remain in motion, elastic deformation, another actor, gravity, friction, numerical damping or omitted channels. A residual can diagnose model/export issues but does not identify a physical channel.

"Impact energy dispersal" must be defined before design: whole-system energy balance, per-component work, spatial energy maps, residual crush, structural failure, occupant proxy, or a combination. RoR does not already expose a validated full energy-budget exporter.

### 7.6 Flight outcomes

Frame-level scripts can support trajectory, mass-weighted speed, altitude, orientation, climb/descent, path deviation, control/engine state and ground/water interactions. Angle-of-attack/airfoil forces and exact lift/drag/thrust decomposition are internal-model concerns requiring additional observation.

The inspected wing model uses relative node motion plus propwash and an altitude-density approximation with an explicit tropospheric-range comment. It is not CFD. A new ambient wind field must be applied consistently to wing, fuselage and propulsion-related flow calculations; simply adding a lateral FreeForce changes a different model. [S16 · Source: wing-relative flow and air-density model](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/flex/FlexAirfoil.cpp#L590-L678) [S17 · Source: fuselage-relative flow and drag](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorForcesEuler.cpp#L123-L151)

For flight or drop tests, start with declared supported altitude/velocity ranges, selected asset/aero data, known coordinates, controlled initial state and analytical or empirical references. Avoid assuming that aircraft visual flight behavior proves physically accurate momentum, stability or impact loads.

## 8. The requested experiment use case

### 8.1 Parameter and outcome coverage

| Requested dimension | Status | Practical evaluation |
| --- | --- | --- |
| Vehicle and section configuration | Native + verification | Select exact bundled identity; confirm effective section and topology |
| Mass/payload/config variants | Native + compose | Mass APIs, content variants and supported live attributes; archive effective setup |
| Terrain and collision fixture | Native + content | Terrain/objects/ground models; author and verify a simple barrier/ramp when needed |
| Scalar vertical gravity | Native + validate | Terrain/script setting; check non-Earth/zero-gravity subsystem assumptions |
| Spatial/time-varying physical wind | Extend | No general ambient-wind trial interface found; define and instrument airflow model |
| Water/ground surface | Native + configure | Pin physical water/traction/ground settings independently of visuals |
| Journey/waypoint path | Native + compose | AI or scripted controller; measure achieved path and checkpoints |
| Requested speed/acceleration profile | Compose + validate | Closed-loop controller or declared actuator with tracking/acceptance limits |
| Exact initial velocity/rotation/deformation | Investigate / extend | No general bound velocity setter found; saved-scene route requires proof |
| Repeated experiment sweeps | Compose | External process supervision and/or script queue; native AI repeats are narrower |
| Position/velocity/node mass | Native, frame-level | Useful low-bandwidth observation with stable cohort and timestamps |
| Linear/angular momentum | Derive + validate | From coherent mass-weighted node state and declared boundaries |
| Kinetic energy | Derive + validate | Node energy, not just displayed speed times gross mass |
| Average net force/impulse | Derive + validate | Momentum differences with other forces/boundary conditions declared |
| Peak contact-force vectors | Extend | Physics-tick observer, contact identity, phase and event window |
| Beam forces/work/failure timeline | Extend | Existing internal data but missing general typed time-series export |
| Energy dispersal/decomposition | Extend + validate | Integrated channel ledger and calibrated model assumptions |
| Flight trajectory/control outcomes | Native + compose | Aircraft asset selection, control logic and trajectory metrics |
| Flight load and gust response | Extend + validate | Consistent airflow and synchronized aerodynamic force channels |
| Visual evidence and raw diagnostics | Native + compose | Screenshots, video, logs, hashes and synchronized timestamps |
| Headless/high-throughput execution | Unverified / extend | Renderer-dependent client baseline; no experiment CLI found |
| Bitwise deterministic replay | Unverified | Fixed step alone is insufficient; define and measure repeatability |

"Native" means source-supported, not newly runtime-proven. The earlier smoke test demonstrated startup, vehicle entry workaround, simple controls, position/wheel-speed logs and visual capture.

### 8.2 Reuse versus build options

| Option | Benefits | Limits | Assessment |
| --- | --- | --- | --- |
| Built-in AI/race/save/replay only | Quick manual scenario exploration | Narrow outcomes and incomplete experiment/data lifecycle | Useful evaluation tool; insufficient alone |
| Script/gadget plus external supervisor | Reuses public controls/state and preserves the engine initially | Frame-rate sampling, no full force/energy observer or physical wind field | Strong candidate for initial exploratory trials |
| Script control plus native physics observer | Preserves existing dynamics while capturing tick/channel data | Engine changes, synchronization/export overhead and validation work | Likely required for the full measurement use case |
| Larger engine refactor/new execution mode | Could add batch/headless stepping and stronger reset/reproducibility | Greater scope and maintenance; performance benefit not yet measured | Defer until precise needs and pilot results justify it |

The recommended **evaluation direction** is to reuse RoR for assets/dynamics/control, build an explicit trial lifecycle around it, and add native observation only for measurement requirements that cannot be met honestly through scripts. Do not start with a large engine rewrite.

No competing RoR-integrated experiment package was verified to satisfy the full requested use case. Existing AI and race tools should be tested against proposed acceptance requirements before deciding to replace or wrap them.

### 8.3 Trial identity and lifecycle

A future experiment should distinguish a **parameterized experiment** from each **realized trial** and repetition. Pin a manifest containing vehicle/content hashes, engine build, effective config, initial conditions, terrain/surface/environment, controller/path definition, requested values, observer version, sampling policy and outcome definitions.

A conceptual lifecycle is:

```text
Define → Resolve/validate → Fresh setup → Settle/verify → Arm
       → Execute/observe → Outcome gate → Finalize/export → Review/archive
```

This is an evaluation pattern, not the later architecture specification. Each phase needs observed completion/timeout/failure criteria. A spawn request being queued is not the same as successful settled setup. A process exit code is not the same as accepted trial data.

Proposed trial records should include wall/simulation/tick times, expected/actual inputs, actor/node/beam identifiers, data-loss counters, messages/events, outcome window, source/binary/content identities, warnings and terminal status. Retain rejected/failed runs, explaining why they did not satisfy the acceptance gate.

### 8.4 Illustrative experiment families

| Family | Parameters to vary | Outcomes | First measurement layer |
| --- | --- | --- | --- |
| Acceleration/braking | Vehicle, payload, gear/control policy, traction | Speed curve, COM acceleration, stopping distance, path error | Script/node state |
| Impact approach | Mass, observed approach speed, barrier angle, structural variant | Pre/post momentum, rebound, crush, failure; later contact waveform | Script coarse outcomes, then native observer |
| Drop/bounce | Height, gravity, orientation, ground model | Flight time, impact velocity, bounce, momentum change | Simple calibrated fixture + native contact observation |
| Ramp/jump/rollover | Approach control, ramp geometry, mass distribution | Trajectory, angular momentum, landing attitude and failure | Script trajectory plus native impact metrics |
| Aircraft maneuver/landing | Aircraft config, speed/altitude targets, control policy | Path tracking, climb/descent, stability, landing loads | Curated aircraft + scripts; native aerodynamic/contact channels as required |
| Gust response | Wind field, duration/frequency, direction, aircraft setup | Load/attitude response and recovery | Extend airflow first, then validate |
| Towing/load transfer | Trailer/payload, links, slope, control | Cohort momentum, link loads, load shift, failure | Script state plus native link forces |
| Surface/water transition | Ground/fluid model, speed, immersion, load | Drag/stopping/buoyancy/contact effects | Model-specific calibration and observer |

An illustrative first impact sweep might vary requested approach speeds of 5/10/15 m/s and selected mass variants on an author-controlled straight approach/barrier. Those are planning examples; no such runs were executed. Accept each repetition only if measured approach pose/velocity and setup meet declared tolerances.

## 9. Repeatability, accuracy and throughput

### 9.1 Repeatability is a test result

Fixed-step physics does not establish bitwise determinism. Inputs arrive at frame boundaries; batches/clamping, async worker scheduling, actor order, sleep/reset state, platform/compiler floating-point behavior, content scripts, random variation and scene restoration may matter. Source contains random parameter/material/terrain behavior and no general trial seed/reset interface was found in the inspected binding/CLI/config surfaces.

Record compiler/build mode, CPU/worker settings, async setting, frame cap, simulation speed, terrain/content revisions, controller and all initial-state data. Use multiple identical repetitions to measure variation, then define tolerances appropriate to the outcome. Do not promise identical results merely by fixing a seed.

Scene saves preserve extensive node/beam/control data, and replays preserve selected sampled state. Neither has been demonstrated here to restore every stateful subsystem, force/observer state, random stream or active script. They must be validated as reset strategies rather than assumed to be complete checkpoints. [S21 · Source: saved node and beam state](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/Savegame.cpp#L719-L763) [S20 · Source: replay samples and beam flags](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/gameplay/Replay.cpp#L183-L211)

### 9.2 Calibration before physical interpretation

| Validation gate | Question answered |
| --- | --- |
| Units and mass audit | Does exported state match known masses, frames, speed conversions and node cohorts? |
| Free flight / free fall | Do simple known-gravity fixtures match analytical position/velocity within declared limits? |
| Constant actuator force | Does the chosen boundary satisfy momentum change and known applied-force impulse? |
| Linear spring/damper | Does a simple rig match the selected model's frequency/damping and energy behavior? |
| Momentum/contact accounting | Do isolated pair and externally supported barrier cases close their declared impulse balances? |
| Energy ledger closure | Do stored/dissipated/actuator/contact channels explain changes, leaving an explicit residual? |
| Sampling/convergence | How do capture phase/rate, time step or numerical settings affect peaks and outcomes? |
| Repeated-run variation | Are distributions/tolerances stable under identical requested inputs? |
| Asset calibration | Are geometry, mass, tire/beam/aero properties tied to known reference data? |
| Export overhead | Does observation change frame timing, control arrival, or the outcome materially? |

These are proposed gates, not passed tests. Use simple known rigs before calibrating complex community vehicles. Comparative sandbox results may be useful early; prediction of real-world crash/flight loads requires substantially stronger model and asset evidence. This report does not assign an engineering certification to RoR.

### 9.3 Data volume and performance

A nominal native recorder exporting position, velocity and force vectors as 9 float32 values for 1,000 nodes at 2,000 Hz produces **72 MB/s** before IDs, timestamps, masses, beam/contact records or compression: 1,000 × 2,000 × 9 × 4 bytes. Ten minutes is **43.2 GB decimal** for that subset alone. These are calculated examples, not RoR benchmarks.

This suggests selective node groups/channels, tick summaries, configurable decimation, and event-triggered pre/post-impact windows with loss counters. A binary buffer/file can be more suitable for native high-rate capture than logging every value as text. Its buffer capacity, overflow policy and writer synchronization belong in the later design.

A paused/slow-motion recording can improve inspection, but it changes wall/frame-to-simulation relationships; it is not proof that high-rate logging is inexpensive or that control delivery matches a real-time run.

The source-defined actor limit of 5,000 is a compile-time ceiling, not evidence that 5,000 deformable actors run at a useful trial rate. Actual throughput depends on node/beam/contact workload, graphics, hardware and export policy. [S33 · Source: fixed step and compile-time limits](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/SimConstants.h#L20-L37)

No headless throughput or concurrent-worker benchmark was executed. Single-player AI and manipulation restrictions also argue for isolated workers rather than relying on a multiplayer session as the experiment coordinator.

## 10. Findings and proposed next evaluation stages

| Stage | Research conclusion / proposed gate | Expected deliverable |
| --- | --- | --- |
| A — Define the measurement contract | Decide exploratory comparison versus calibrated physical prediction; choose one vehicle/scenario and outcome definitions | The forthcoming architecture/design specification |
| B — Low-rate trial feasibility | Validate exact asset resolution, setup/reset, script controls, COM/momentum calculations, acceptance gates and archive lifecycle | A scoped prototype proposal and validation plan |
| C — Impact instrumentation feasibility | Define physics phase, contact/beam channels, tick/event synchronization, units and buffering | Native-observer design and toy-rig calibration plan |
| D — Energy accounting | Define work/storage/loss channels and boundary conditions; keep residual visible | Energy-ledger design, validation references and limitations |
| E — Flight/wind extension | Curate aircraft/aero data; define consistent airflow/atmosphere and instrument loads | Separate flight/gust capability plan |
| F — Scale/repeatability | Measure repetition variance and observer overhead before headless/parallel refactors | Benchmarks and justified execution-mode requirements |

Do not equate Stage B completion with Stage D/E correctness. A useful exploratory trial platform can emerge earlier while advanced physics quantities remain clearly labeled.

## 11. Decisions needed for the architecture/design specification

1. **Purpose and fidelity:** exploratory comparisons, educational visuals, automated regression, or predictions tied to real physical reference data?
2. **First domain:** ground acceleration/impact, drop/jump, coupled loads, or aircraft/landing? Select a minimal pilot.
3. **Bodies and metrics:** which actors/nodes, what reference frame, what impact window, what force/energy meaning, and which quantities need tick-level capture?
4. **Control semantics:** replayed inputs, closed-loop velocity/acceleration tracking, or explicitly imposed initial state/forces? Define acceptance tolerances.
5. **Assets:** source-owned fixtures versus third-party vehicles/terrains; calibration, redistribution rights, dependency identity and versions.
6. **Environment:** scalar gravity only initially, or true wind/gusts/atmosphere/water-model parameters? Which interactions must be physically consistent?
7. **Repeat/reset:** process-per-run, actor respawn, scene restore, or another strategy; how to prove a clean comparable setup?
8. **Storage/events:** required sampling windows, retention, data-loss policy, metadata schema, outcome status and correlation with video.
9. **Validation:** analytical/toy-rig references, empirical datasets, allowed errors and regression checks.
10. **Execution/UI:** interactive trials first, batch size/runtime budget, supported machines, and whether headless execution is a measured necessity.

These questions establish the input to the next specification. They are not a request to start implementation now.

## 12. Evidence, limits and references

### Local research artifacts

- [Source inspection and starter-asset hashes](doc/project/research/2026-10-08/source-inspection.json)
- [Static binding registration inventory](doc/project/research/2026-10-08/binding-inventory.json)
- [Reference catalog](doc/project/research/2026-10-08/references.json)
- [Historical source-build proof records](doc/project/baselines/2026-10-08/README.md)
- [Canonical build/record procedure](doc/project/build-and-record.md)

The new research is static code/documentation analysis. Source-supported APIs and proposed derivations still need runtime tests in a new evidence session. Community catalog access was limited; no new assets were downloaded. No source build/rebuild was required for this documentation/report change.

### Source and documentation catalog

All source links below pin the inspected fork commit. Web documentation was checked on 2026-10-08 and can evolve independently. The public documentation's version label, message spellings, force-unit wording and default assumptions may lag or differ from the fork; the report calls out material differences.

- [S01 · Source: node and beam data](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/SimData.h#L250-L338) — source/main/physics/SimData.h, lines 250–338.
- [S02 · Source: node integration and force reset](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorForcesEuler.cpp#L1602-L1675) — source/main/physics/ActorForcesEuler.cpp, lines 1602–1675.
- [S03 · Source: node mass, velocity and force getters](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/Actor.cpp#L4854-L4900) — source/main/physics/Actor.cpp, lines 4854–4900.
- [S04 · Source: actor reference position and camera-dependent averaging](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/Actor.cpp#L1166-L1193) — source/main/physics/Actor.cpp, lines 1166–1193.
- [S05 · Source: local camera g-force calculation](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/Actor.cpp#L4529-L4548) — source/main/physics/Actor.cpp, lines 4529–4548.
- [S06 · Source: frame batching and fixed-step accumulation](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorManager.cpp#L1120-L1234) — source/main/physics/ActorManager.cpp, lines 1120–1234.
- [S07 · Source: synchronized scripting before new physics tasks](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/main.cpp#L2196-L2237) — source/main/main.cpp, lines 2196–2237.
- [S08 · Source: actor telemetry and control bindings](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/scripting/bindings/ActorAngelscript.cpp#L135-L225) — source/main/scripting/bindings/ActorAngelscript.cpp, lines 135–225.
- [S09 · Source: supported simulation attributes](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/SimData.h#L924-L978) — source/main/physics/SimData.h, lines 924–978.
- [S10 · Source: game, terrain, AI and resource bindings](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/scripting/bindings/GameScriptAngelscript.cpp#L86-L206) — source/main/scripting/bindings/GameScriptAngelscript.cpp, lines 86–206.
- [S11 · Source: actor spawn validation and fallback](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/scripting/GameScript.cpp#L1583-L1639) — source/main/scripting/GameScript.cpp, lines 1583–1639.
- [S12 · Source: bound message types](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/scripting/bindings/MsgQueueAngelscript.cpp#L35-L116) — source/main/scripting/bindings/MsgQueueAngelscript.cpp, lines 35–118.
- [S13 · Source: event definitions and payloads](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/gameplay/ScriptEvents.h#L29-L132) — source/main/gameplay/ScriptEvents.h, lines 29–132.
- [S14 · Source: persistent force and half-beam calculation](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorManager.cpp#L1624-L1768) — source/main/physics/ActorManager.cpp, lines 1624–1768.
- [S15 · Source: beam force, yield and break processing](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorForcesEuler.cpp#L1317-L1445) — source/main/physics/ActorForcesEuler.cpp, lines 1317–1445.
- [S16 · Source: wing-relative flow and air-density model](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/flex/FlexAirfoil.cpp#L590-L678) — source/main/physics/flex/FlexAirfoil.cpp, lines 590–678.
- [S17 · Source: fuselage-relative flow and drag](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/ActorForcesEuler.cpp#L123-L151) — source/main/physics/ActorForcesEuler.cpp, lines 123–151.
- [S18 · Source: OutGauge interval, data fields and sender](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/network/OutGauge.cpp#L103-L202) — source/main/network/OutGauge.cpp, lines 103–202.
- [S19 · Source: OutGauge packet field definitions](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/network/OutGauge.h#L87-L118) — source/main/network/OutGauge.h, lines 87–126.
- [S20 · Source: replay samples and beam flags](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/gameplay/Replay.cpp#L183-L211) — source/main/gameplay/Replay.cpp, lines 183–211.
- [S21 · Source: saved node and beam state](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/Savegame.cpp#L719-L763) — source/main/physics/Savegame.cpp, lines 719–763.
- [S22 · Source: runtime configuration variables](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/system/CVar.cpp#L32-L198) — source/main/system/CVar.cpp, lines 32–198.
- [S23 · Source: supported launch arguments](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/system/AppCommandLine.cpp#L52-L135) — source/main/system/AppCommandLine.cpp, lines 52–135.
- [S24 · Source: friction and fluid ground parameters](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/resources/skeleton/config/ground_models.cfg#L7-L78) — resources/skeleton/config/ground_models.cfg, lines 7–78.
- [S25 · Source: collision reaction and friction calculation](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/collision/Collisions.cpp#L1265-L1344) — source/main/physics/collision/Collisions.cpp, lines 1265–1344.
- [S26 · Source: waypoint and per-waypoint control bindings](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/scripting/bindings/VehicleAiAngelscript.cpp#L34-L56) — source/main/scripting/bindings/VehicleAiAngelscript.cpp, lines 34–61.
- [S27 · Source: waypoint speed and power setters](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/gameplay/VehicleAI.cpp#L134-L150) — source/main/gameplay/VehicleAI.cpp, lines 134–150.
- [S28 · Source: flight autopilot bindings](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/scripting/bindings/AutopilotAngelscript.cpp#L31-L52) — source/main/scripting/bindings/AutopilotAngelscript.cpp, lines 31–52.
- [S29 · Source: drivetrain bindings](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/scripting/bindings/EngineAngelscript.cpp#L55-L138) — source/main/scripting/bindings/EngineAngelscript.cpp, lines 55–138.
- [S30 · Source: script text-resource creation and path restrictions](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/scripting/GameScript.cpp#L2044-L2191) — source/main/scripting/GameScript.cpp, lines 2044–2191.
- [S31 · Source: script simulation clock](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/scripting/GameScript.cpp#L110-L113) — source/main/scripting/GameScript.cpp, lines 110–113.
- [S32 · Source: multiplayer guard and attribute-change events](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/Actor.cpp#L5110-L5127) — source/main/physics/Actor.cpp, lines 5110–5127.
- [S33 · Source: fixed step and compile-time limits](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/source/main/physics/SimConstants.h#L20-L37) — source/main/physics/SimConstants.h, lines 20–37.
- [S34 · Source: bundled race management](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/resources/scripts/races.as#L1-L70) — resources/scripts/races.as, lines 1–70.
- [S35 · Source: engine diagnostics gadget](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/resources/gadgets/engine_tool.gadget#L7-L17) — resources/gadgets/engine_tool.gadget, lines 7–17.
- [S36 · Source: shock diagnostic samples](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/resources/gadgets/shock_tool.as#L178-L191) — resources/gadgets/shock_tool.as, lines 178–191.
- [S37 · Source: terrain mesh batcher role](https://github.com/bert-systems/rigs-of-rods-trials/blob/e85535569102b6251849af574026984e3213b3f4/resources/gadgets/terrn_batcher.as#L1-L15) — resources/gadgets/terrn_batcher.as, lines 1–15.
- [D01 · Official developer portal](https://developer.rigsofrods.org/) — documentation/ecosystem reference checked 2026-10-08.
- [D02 · Official node/beam concepts](https://docs.rigsofrods.org/vehicle-creation/vehicle-concepts/) — documentation/ecosystem reference checked 2026-10-08.
- [D03 · Official vehicle file format](https://docs.rigsofrods.org/vehicle-creation/fileformat-truck/) — documentation/ecosystem reference checked 2026-10-08.
- [D04 · Official terrn2 format](https://docs.rigsofrods.org/terrain-creation/terrn2-subsystem/) — documentation/ecosystem reference checked 2026-10-08.
- [D05 · Official vehicle AI guide](https://docs.rigsofrods.org/gameplay/vehicle-ai/) — documentation/ecosystem reference checked 2026-10-08.
- [D06 · Community-maintained waypoint presets](https://github.com/RigsOfRods-Community/ai-waypoints) — documentation/ecosystem reference checked 2026-10-08.
- [D07 · Official FreeForces description](https://developer.rigsofrods.org/d0/dde/_free_forces_page.html) — documentation/ecosystem reference checked 2026-10-08.
- [D08 · Official FreeBeams description](https://developer.rigsofrods.org/d5/d34/_free_beams_page.html) — documentation/ecosystem reference checked 2026-10-08.
- [D09 · Official ActorSimAttributes description](https://developer.rigsofrods.org/d3/d52/_actor_sim_attributes_page.html) — documentation/ecosystem reference checked 2026-10-08.
- [D10 · Official scripting features overview](https://developer.rigsofrods.org/d7/d61/_scripting_features_overview_page.html) — documentation/ecosystem reference checked 2026-10-08.
- [D11 · Official tuning guide](https://docs.rigsofrods.org/gameplay/tuning/) — documentation/ecosystem reference checked 2026-10-08.
- [D12 · Official aircraft creation guide](https://docs.rigsofrods.org/vehicle-creation/aircraft-and-aerodynamics/) — documentation/ecosystem reference checked 2026-10-08.
- [D13 · Official boat creation guide](https://docs.rigsofrods.org/vehicle-creation/boats/) — documentation/ecosystem reference checked 2026-10-08.
- [D14 · Official race script generator](https://docs.rigsofrods.org/terrain-creation/race-generator/) — documentation/ecosystem reference checked 2026-10-08.
- [D15 · Official controls and replay bindings](https://docs.rigsofrods.org/gameplay/controls-config/) — documentation/ecosystem reference checked 2026-10-08.
- [D16 · Official dedicated-server repository](https://github.com/RigsOfRods/ror-server) — documentation/ecosystem reference checked 2026-10-08.
- [D17 · Starter content repository at the inspected revision](https://github.com/RigsOfRods/content/tree/34fefdd126784bf87b068fc283f812525d159dd7) — documentation/ecosystem reference checked 2026-10-08.
