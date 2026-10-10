# Later collision fixture and qualification contract

Slice 07 adds `impact-yield-v1` and `impact-fracture-v1`, distinct from tick-1 initialization fixtures. Manifest schema 6 declares `two-mass-impact-reference-v1` and `two-mass-detail-resources-v1`. Aggregate schema 2/2,080 bytes, detail schema 1 and all existing profiles retain their layouts and limits.

Both freeze two 100 kg moving nodes at local X=1/0 m, three normal beams and two fixed 1 kg anchors. Only beam 0 is active: k=10,000 N/m, c=0, rest=1 m, strength=2,000 N, plastic coefficient 0.25, no cab protection. Initial velocity is +5 m/s for both masses; initial extension and force are zero. Origin=(500,20,500) m; box center=(514.5,20,500), local bounds=(-0.5,-0.2,-8)/(0.5,6,8). Native primitive collisions are enabled for moving nodes; drag, gravity and wind are disabled. Observation is seven seconds, zero settling, distance 13 m. Precise fixture beam normalization is retained. These are pinned parameters, not a general material editor.

Yield uses ±200 N bounds: compression changes rest without reducing strength, then rebound/tension reduces strength. Removal uses ±1e9 N yield bounds and the same 2,000 N strength. No beam mutation is directly commanded after initialization; native collision and constitutive routines produce changes.

First actual nonzero consumed contact triggers the existing 4,000 pre/8,000 post tick window, inclusive. All four nodes, 16 channels, three beams and populated contacts remain at every 0.5 ms step. This small profile reserves 25,926,480 history bytes and 67,106,880 queue bytes (10,356 frames); Daf v2 is unchanged. Existing conservative 6 GiB available-memory and 10 GiB + 3 GiB archive-disk gates apply. Required loss continues recording, stays Incomplete and prevents science from passing.

## Scoped reference

`ImpactFixtureValidation` requires complete execution, independently verified aggregate/dense captures, pinned configuration and cohort/epoch identities. Its double-precision **local conformance reference is driven by recorded beam lengths and contact inputs**. It is not an independent predicted trajectory or material calibration. It recomputes yield/correction/strength/removal and axial zero-penetration contact reaction; checks world step/velocity continuity, carried/generated endpoint writes, event state/storage, contact geometry and independently reduced aggregate/dense forces, momentum and kinetic energy. The first transition must follow consumed contact. Both readers recheck actual CRC/DONE/footer bytes; cached health cannot certify science.

| Quantity | Frozen limit |
| --- | --- |
| Identity, epochs, counts, outcome | Exact |
| Beam/channel force | 0.1 N |
| Contact law, strength and unassigned contact rounding | 0.25 N |
| Rest/state continuity | 1e-5 m |
| Kick/velocity continuity | 2e-6 m/s |
| Per-step world-position envelope | 1.5e-4 m |
| Combined dense/aggregate force, momentum and kinetic parity | 1e-5 in the associated units |
| Storage/event ports | 0.001 J |
| Integration impulse and midpoint work residual | 0.001 kg m/s and 0.001 J |

The new contact rounding envelope accounts for float32 accumulation around a 0.8 MN kick. Historical contactless fixtures keep their tighter limits. Initial kinetic energy is 2,500 J; initial supported storage is zero. Signed rest/removal ports are model-storage bookkeeping, not calibrated plastic/fracture dissipation. This profile does not gate full cumulative thermodynamic closure or material energy dispersal.

## Interface and evidence

React supplies frozen choices, live health, `impactTimeline` (first contact/parameter/strength/removal ticks/counts), verified paged transitions and exact retained tick inspection. Distinct sibling keys prevent inspectors/ledgers accumulating during selection. Fixture environment views declare drag-disabled metadata; vehicle drag is unchanged.

Three fresh repeats per scenario have identical dense payloads and aggregate physics bytes excluding wall timers. Actual contact is tick 5,202; yield 5,210; strength loss 5,978; removal in the other fixture 5,284. Required ticks are 1,202–13,202. CRC-valid kind/port/epoch/contact-normal/velocity/strength adversaries cannot pass science. Queue-overflow/partial-write tests retain later frames but stay Incomplete/NotReady. Physical disk-full and coordinator-orphan recovery remain unqualified.

[Delivery](../../doc/project/slices/slice-07.md), [results](../../doc/project/slices/slice-07-results.json). Reproduce with `build.ps1 -Parallel 6`, `start.ps1 -Renderer OpenGL -EvidenceFrames`, `verify-slice-07.py --phase qualification`, `verify-slice-07-ui.py`, managed real-archive contract checks and `write-slice-07-report.py` under `tools/trials`. Always use a new session; UI evidence scripts author fresh trials.
