# Simplified trial shell concepts

2026-10-13. Exploratory design requested while sibling traction/wheel work continues. These are three interactive UI proposals, not a selected implementation direction or new physical capability. The user has not yet selected a shell.

## Shared design

The vehicle and course are the main image. Show the minimum choices required to run a useful trial, supply explicit presets, and retain precise effective configuration automatically. The default loop is **choose → run → replay → change one thing → compare**.

The visible setup has four groups: vehicle/package, obstacle/challenge, approach speed, and physical conditions. Structure, occupant/restraint and detailed tuning expand in a small tray. Do not require trial names, file paths, recording rates, physics-step selection or scientific dashboards before the first run. Put saved trials in app navigation and local configuration beside the scene.

Vehicle choices should use recognizable archetypes and silhouettes. The concepts depict compact hatch, sports coupe, trail buggy and utility truck; these are presentation examples, not native RoR asset-loading claims. Offer tire, front structure and restraint packages rather than a long material-property form. Retain an explicit path to exact geometry/material values when tuning is requested.

Keep physical surface and environment understandable: dry/wet-asphalt/gravel presets are distinct from Earth gravity, steady headwind and Moon/vacuum examples. A wet-surface preset changes the declared surface model; it does not imply a water or weather solver. Decoration must not silently modify physics.

The shell can use the independent 2D sibling's rendering and archive services. A corresponding native RoR shell would need its own execution adapter and asset/capability mapping; the native scene remains a separate window under current decisions. These mockups do not implement an embedded native 3D view.

## Proving Ground

**Vehicle first. Recommended default.** A dominant side view shows the chosen vehicle, the obstacle and the run-up. A small dock offers vehicle, tire package, wall/ramp/bumps and launch speed. One Run trial action starts the run. Conditions & tune expands surface, environment, structure and occupant choices. Vehicle/Cutaway switches the scene emphasis.

After a run, show deformation and raw virtual occupant responses below the scene, followed by a route to replay or a fresh attempt. Progress should come from personal bests and improvements against a retained baseline. Keep measured game achievement distinct from archive completeness and scoped scientific qualification.

Tradeoff: most flexible and immediately visual, but a blank sandbox gives a new player less direction. Provide a small challenge entry point in an implementation.

## Challenge Cards

**Goal first. Fastest first run.** Three visual missions illustrate the structure: Stop short, Stick the landing and Protect the cabin. Each card names one observable objective. A mission supplies obstacle, course, approach and environment; only its allowed vehicle/package choices are initially editable.

Difficulty changes declared challenge conditions. Show the effective preset beside the start action. Goals can earn medals for braking distance, landing control, reaching a zone or a relative reduction in model loads. Do not reward injury severity. The concept's progress and medals are illustrative game states, not stored user achievements.

Tradeoff: strongest onboarding and progression, but presets constrain experimentation. A future implementation can open the same recipe in the sandbox; that action is outside the current mockup.

## Impact Studio

**Impact and occupant response first.** A vehicle cutaway and a compact dummy body view stay visible together. Setup offers vehicle, impact template, front structure, launch speed and restraint; physical conditions expand separately.

Run collapses setup into replay controls. First contact, head peak and settled bookmarks plus a scrubber emphasize event timing. Compare belt setups illustrates an A/B investigation. Present cabin change, head acceleration, restraint load, contact work and an explicit unresolved model-energy balance. Detailed channels and scientific dossiers remain drill-down views.

Tradeoff: strongest explanation of impact and body loading; more specialized than a general driving/trial home screen.

## Impact and injury language

Use **Impact & occupant response** and **Model proxy · uncalibrated** near the body/load view. Existing sibling observations include coupled dummy/seat/restraint response, head acceleration, excursion, belt loads and body contacts. Teaching-reference exceedances and virtual skeletal markers do not establish real injury, fracture probability or vehicle safety.

No clinical injury percentages, safe/unsafe ratings or injury-severity points. Missing occupants or channels display Unavailable. Captured beam transitions and contact work are not calibrated fracture dissipation. Do not relabel unclosed energy as absorbed energy. All displayed numeric outcomes in these concepts are illustrative and independent of the current worker and archives.

## Recommended combination

Use Proving Ground as the home shell, Challenge Cards as its quick-start route, and Impact Studio as its post-run replay/investigation view. This is an agent recommendation; it is not a user selection. Preserve a compact recording/model-status indication in the product without turning the default screen into the scientific workbench.

An implementation must retain immutable realized configuration, fresh attempt identities, tick-boundary run controls and the distinction between Setup preview, active worker and archived replay. Editing setup must not relabel or mutate an active worker. Existing raw archives, failures and qualification gates remain authoritative.

## Design verification and provenance

- Native source inspected on clean `dev`, HEAD `d92c95a98792817c9b5774136019ad2d0c0660db`; origin `bert-systems/rigs-of-rods-trials`. Content submodule `34fefdd126784bf87b068fc283f812525d159dd7`.
- In-conversation fragment: `C:\Users\berts\.codex\visualizations\2026\10\14\01a13841-49ae-7381-8993-aa9872665272\trials-shell-options.html`.
- New design-only evidence: `D:\Rigs of Rods\trial-shell-design-2026-10-13-01a13841`; final preview/screenshots/checks in `final/`. Earlier failed selector and narrow-layout checks remain part of the session history. The final source and small manifest are retained in that session.
- Built-in visualization renderer and bundled Node/Playwright with installed headless Chrome. Final checks: 26 passed, no page exceptions; vehicle/obstacle/conditions, challenge goals, replay bookmarks, comparison, no-dummy availability, real carousel navigation and 1080/736/390/320 px layouts. Visible desktop, phone, light and dark pixels inspected. This is UI-concept QA, not simulation evidence.
- No game build, physical trial, solver, native engine or installed-game change. Historical evidence remains preserved.

The initial sandbox process launcher failed before commands ran. Read/render/verification used reviewed host-shell execution; file edits used apply_patch. No runtime was installed. Repository documentation publication follows the standing `dev` workflow, separately from the active sibling implementation.
