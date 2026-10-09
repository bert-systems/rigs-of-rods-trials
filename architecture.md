# Architecture

Source-grounded introduction for the baseline `e85535569102b6251849af574026984e3213b3f4`, inspected on 2026-10-08. Update this map when the fork changes.

## Proposed trial-platform extension

The current engine map below remains the baseline implementation. [Trial architecture options](doc/project/design/trial-platform-architecture-options.md) and their [HTML companion](doc/project/reports/trial-architecture-options-2026-10-08.html) evaluate a native force/energy observer, common environment service, isolated trial worker, .NET coordinator, and WPF or React workbench.

The complete evaluated architecture remains the roadmap. Slice 01 now implements an initial subset described below; full model attribution and scientific qualification remain unfinished. The evaluation recommends preserving current solver ordering for initial observation, recording generated/consumed force epochs, and validating energy/model coverage before scientific claims. D003 in the [implementation decision log](doc/project/design/implementation-decisions.md) selects a React workbench with a .NET coordinator, delivered through a local browser first. D011 selects scientific dashboards alongside the separate source-built RoR scene window, with interactive scientific 3D inspection later. The completed Q&A is consolidated in the [implementation specification](doc/project/design/trial-platform-implementation-spec.md) and [HTML review](doc/project/reports/trial-implementation-spec-2026-10-08.html): native tick instrumentation and recorder, uniform physical environment/adapters, controlled coast execution, sequential isolated workers, retained archive/analysis and React scientific views. It defines 14 epics and five delivery gates. Wire/storage layouts, numerical limits and resource defaults are proposals requiring qualification. The static [platform landscape](platform.md) provides capability evidence.

## Implemented trial foundation — Slice 01

- **Native:** ActorManager brackets actor force jobs with an actor-owned ledger and publishes completed aggregate records after the physics barriers. CalcNodes observes the actual force and pre/post velocity at integration. Trial mode initializes coherent body/wheel rolling velocity after settling, applies pilot gravity/density/steady wind, and acknowledges pause/resume after synchronization.
- **Capture:** TrialRuntime passes every-step aggregates through a bounded 32,768-record SPSC queue to an independent writer. Chunks contain explicit little-endian records, CRC-32 and completion markers; grouped durable flushes and a footer distinguish verified prefixes from clean complete archives. Required loss never blocks the physics producer.
- **Coordinator:** apps/trials/coordinator owns immutable revisions, sequential fresh workers/private profiles, process/content provenance, typed local commands, a retained archive and a SQLite catalog. Execution, capture and validation are independent states. Retry creates a fresh attempt; interruption never restores a physical checkpoint.
- **Workbench:** apps/trials/workbench provides a local React form, queue, native-clock status, force/energy/momentum charts, environment, event timeline, artifacts and controls. Native RoR remains a separate window. Charts are a reduced projection; the archive retains every recorded aggregate tick.
- **Quality:** Total consumed force and ground/object-contact deltas are observed; beam/aero/drive/hydro/free-force attribution and conservative/dissipative energy terms remain incomplete. Kinetic-work and momentum update residuals test the integration boundary, not whole-model conservation. All attempts remain scientific validation NotReady.

See [the runbook](apps/trials/README.md), [Slice 01 evidence](doc/project/slices/slice-01.md), and [the source observer](source/main/trials/TrialRuntime.cpp). The current capability is restricted to one pinned pilot actor and controlled coast. The supplied game profile uses this workstation's verified Direct3D9 renderer.

## System shape

Rigs of Rods is a native C++ application. Its own application loop coordinates input, simulation, scripting, graphics, audio, and GUI. Vehicles are actors built from nodes, beams, wheels, engines, and other components. Content files describe those actors and their terrain; they are separate from the engine executable.

```mermaid
flowchart LR
    Content["Vehicle / terrain content"] --> Load["Content index, parser, actor spawn"]
    Load --> Physics["ActorManager / Actor physics"]
    Input["OIS input / scripts / GUI"] --> Game["GameContext and message queue"]
    Game --> Physics
    Physics --> Buffers["Simulation snapshots"]
    Buffers --> Graphics["OGRE graphics / deformable meshes"]
    Graphics --> Window["Game window"]
```

The diagram summarizes data flow. It does not imply that all subsystems are isolated or that every action travels through the message queue.

## Source map

| Area | Main entry points | Responsibility |
| --- | --- | --- |
| Application lifecycle | [main.cpp](source/main/main.cpp), [AppContext.cpp](source/main/AppContext.cpp), [Application.h](source/main/Application.h) | Startup, filesystem setup, rendering window, input listeners, global services and configuration variables |
| Simulation orchestration | [GameContext.cpp](source/main/GameContext.cpp), [GameContext.h](source/main/GameContext.h) | Simulation state, actor lifecycle, terrain transitions, and queued `MsgType` requests |
| Input and configuration | [InputEngine.cpp](source/main/utils/InputEngine.cpp), [CVar.cpp](source/main/system/CVar.cpp), [AppConfig.cpp](source/main/system/AppConfig.cpp), [AppCommandLine.cpp](source/main/system/AppCommandLine.cpp) | OIS input/events, CVars, persistent settings, and CLI options |
| Actor construction | [ActorSpawner.cpp](source/main/physics/ActorSpawner.cpp), [ActorSpawnerFlow.cpp](source/main/physics/ActorSpawnerFlow.cpp), [rig_def_fileformat](source/main/resources/rig_def_fileformat) | Vehicle definition parsing/validation and construction of simulation/visual components |
| Physics | [ActorManager.cpp](source/main/physics/ActorManager.cpp), [Actor.h](source/main/physics/Actor.h), [ActorForcesEuler.cpp](source/main/physics/ActorForcesEuler.cpp), [SimData.h](source/main/physics/SimData.h) | Physics scheduling, actor state, force/integration steps, and node/beam data |
| Collision | [Collisions.cpp](source/main/physics/collision/Collisions.cpp), [DynamicCollisions.cpp](source/main/physics/collision/DynamicCollisions.cpp), [PointColDetector.cpp](source/main/physics/collision/PointColDetector.cpp) | Ground/object and actor collision handling |
| Graphics | [gfx](source/main/gfx), [SimBuffers.h](source/main/gfx/SimBuffers.h), [FlexBody.cpp](source/main/physics/flex/FlexBody.cpp) | OGRE scene/actor graphics, simulation snapshots, CPU mesh deformation |
| Terrain | [Terrain.h](source/main/terrain/Terrain.h), [TerrainGeometryManager.cpp](source/main/terrain/TerrainGeometryManager.cpp), [TerrainObjectManager.cpp](source/main/terrain/TerrainObjectManager.cpp), [ProceduralRoad.cpp](source/main/terrain/ProceduralRoad.cpp) | Terrain geometry, objects, roads, and environment |
| Resources | [ContentManager.cpp](source/main/resources/ContentManager.cpp), [CacheSystem.cpp](source/main/resources/CacheSystem.cpp) | OGRE resource groups, packaged resources and mod discovery/indexing |
| Scripting | [ScriptEngine.cpp](source/main/scripting/ScriptEngine.cpp), [GameScript.cpp](source/main/scripting/GameScript.cpp), [bindings](source/main/scripting/bindings) | AngelScript runtime, game API, and native type/function bindings |
| UI, audio, network | [gui](source/main/gui), [audio](source/main/audio), [network](source/main/network) | ImGui panels, MyGUI HUD/dashboard integration, OpenAL audio, and multiplayer/network services |
| Build and dependencies | [CMakeLists.txt](CMakeLists.txt), [conanfile.py](conanfile.py), [DependenciesConfig.cmake](cmake/DependenciesConfig.cmake), [conan_provider.cmake](cmake/conan_provider.cmake) | Targets, options, dependency graph, and Conan/CMake integration |
| Build products | [source/main/CMakeLists.txt](source/main/CMakeLists.txt), [version_info](source/version_info), [angelscript_addons](external/angelscript_addons) | RoR executable/resources, generated commit/date version information, and compiled script addons |
| CI | [build-game.yml](.github/workflows/build-game.yml) | Upstream Windows/Linux build workflow |

## Simulation and rendering

[SimConstants.h](source/main/physics/SimConstants.h) defines `PHYSICS_DT = 0.0005f`, a fixed 0.5 ms physics step. ActorManager determines the number of steps needed from elapsed time and retains the remainder. Work can run asynchronously and uses worker tasks for actor forces and collision work.

Graphics uses the snapshots described in `gfx/SimBuffers.h`, including `GameContextSB`, `ActorSB`, and `NodeSB`. Simulation is synchronized for copying data, then rendering can consume the snapshots while simulation proceeds. Deformable visual meshes are updated from simulated node positions.

The code still contains shared services and coupling. When changing physics or threading, inspect synchronization, actor lifetime, and ownership rather than assuming snapshots make arbitrary cross-thread reads safe. Recheck timing assumptions if changing integration, simulation speed, or scheduling.

## Content and scripting

The `content/` Git submodule supplies starter assets. Community mods and user profiles are external data; their versions and licenses can differ from the engine. A source build needs the recorded content revision as well as compiled code to reproduce a session.

The content cache indexes discoverable vehicles and terrains. A new portable profile can rebuild that cache on first launch. A missing or stale cache is a runtime/content issue rather than evidence of failed C++ compilation.

AngelScript supports startup `main()` and per-frame `frameStep(float)`; `-runscript` selects a startup script. Scripts can drive inputs, read actor state, and enqueue actions with `game.pushMessage`. The historical API name `BeamClass` represents a vehicle actor. Inspect the actual bindings when planning extensions. Some Doxygen stub headers under `doc/angelscript` document the API without implementing it.

The baseline driving script used ordinary throttle and brake input, read positions/wheel speed, requested screenshots, and quit after completion. It did not teleport the actor or manipulate positions to produce movement.

## Change impact

| Proposed change | Inspect and validate |
| --- | --- |
| Vehicle force/integration or collision | Actor state/manager, time step, affected content, motion telemetry, and relevant contact/deformation scenarios |
| New script API or automation | Native bindings, script lifetime/thread context, queued actions, and an actual script-driven session |
| CLI or configuration | CLI-to-CVar mapping, configuration precedence, portable profile, and launch behavior |
| GUI or rendering | Graphics snapshots/actor lifetime, GUI systems, native screenshots, and the selected render backend |
| Build/dependency change | Conan profiles/lock, CMake configuration, fresh build, and exact executable/module provenance |
| Content format or asset change | Parser/validator, cache rebuild behavior, content revision, and load/runtime diagnostics |

## Evidence boundary

The baseline validates a Release x64 build and one ground-vehicle scenario using Direct3D9. It does not establish correctness of the full physics model, networking, aircraft, boats, complex collisions, multi-actor scaling, or other graphics backends.

A startup vehicle-entry mismatch is documented in [project memory](project-memory.md). The successful proof used a config workaround; no engine fix has been applied.

For upstream orientation, see [CodebaseOverview.md](doc/doxygen/CodebaseOverview.md). Treat its statements about future messaging/scripting work as historical and verify them against current source.
