# Controlled barrier and detailed impact contract

Implemented in Slice 04; qualification results are linked from its dated delivery report. This file describes the format and acceptance scope, not an assertion that all runs passed.

## Scenario

`barrier-v1` uses the pinned Daf Semi and Simple2. Before settling, the main thread freezes the horizontal vehicle direction and creates a fixed native collision box, 16 m wide, 6 m high and 1 m deep, with local bounds `[-.5,-.2,-8]` to `[.5,6,8]`. Its front face is the configured distance from the initial frontmost node. The resolved transform, native feature index and concrete material parameters are in `barrier.json`. An orange native mesh shows the same box geometry. Collision uses the existing `primitiveCollision` box path, including its zero penetration argument.

At release, the existing controlled initialization assigns body and coherent wheel motion, engine off, neutral, braking disabled. Speed is never continuously clamped. Release speed and target approach speed are separate immutable inputs. Calibration attempts remain in the archive.

The approach sample is the first released tick at which the frontmost node is no more than 0.25 m before the frozen front face. Signed movable-node mass-weighted COM velocity projected on the frozen direction must differ from the target by at most `max(0.1 m/s, 2% target)`. Heading error must be at most 1 degree; lateral COM displacement from the barrier centerline at most 0.25 m. The approach tick must precede or equal first contact. `barrier-approach-capture-v1` Passed covers these checks and complete required capture. Scientific vehicle/material/energy validation stays NotReady.

## Observation and retention

All realized pilot nodes, 16 consumed node force-channel vectors, all beams and terrain/object contact applications are observed each native tick. Nominal rate is 2 kHz; actual `PHYSICS_DT` is stored as double. The node/beam/contact state and application values retain native float32 precision. Aggregate accounting remains schema 2, double reductions. Cross-reference streams by immutable attempt and tick.

The first nonzero actual increment applied by the pilot/barrier box contact triggers 4,000 prior ticks and 8,000 subsequent ticks, inclusive of the trigger. A later closing contact after at least 1,000 ticks without barrier contact starts another episode; overlapping windows extend the end. Continuous resting contact does not repeatedly retrigger. Unavailable history is a gap, never invented state. Insufficient final posthistory remains incomplete.

The recorder uses a preallocated single-producer queue. The recorder thread retains a distinct rolling history buffer and writes CRC/commit-framed records. Native callbacks allocate no memory and perform no file/network/browser waits. Bounded contact capacity is four applications per node plus 32 each tick; any excess is counted as loss. The main thread allocates buffers after joining physics.

`daf-detail-resources-v2` revises engineering proposals after retained real overflow: 1 GiB maximum history and a separate 3 GiB writer queue. The pinned 176-node/744-beam realized cohort has a maximum frame stride of 205,056 bytes; 4,001 history slots require 820,429,056 bytes. Windows memory preflight requires 6 GiB available physical memory. Disk preflight reserves 3 GiB plus the existing 10 GiB floor and probes archive writability. These resource limits do not change physical tolerances or sample rate.

## Binary schema 1

Magic `RORDTAIL`, followed by six little-endian uint32 fields: schema=1, node count, beam count, maximum contact count, pre ticks=4000, post ticks=8000. Header length is 32 bytes.

Each committed frame is `DATA`, uint32 count=1, uint32 payload length, uint32 IEEE CRC-32 of payload, payload, `DONE`. Only complete frames with a matching checksum are analyzed. Footer is `END!`, uint64 written frame count, uint64 dropped observations, uint64 missing required ticks, uint32 sticky I/O error. Footer length is 32 bytes. No footer or a corrupt tail preserves a verified prefix and prevents Complete.

The explicitly supported representation is little-endian IEEE Windows x64. Runtime and compile-time endian/size/offset checks guard a bulk wire copy. All reserved fields are initialized, and the declared records have no implicit padding. Other host representations require a new adapter; this is not an unrestricted ABI dump.

| Payload record | Bytes | Layout |
| --- | ---: | --- |
| Tick header | 128 | uint64 tick; double dt; uint32 actor/nodes/beams/contacts/phase/flags/lost/barrierApplications; double COM[3], COM velocity[3], K, heading, front distance, lateral displacement |
| Node | 256 | uint32 id/fixed flags; float mass/reserved; float world position[3], pre-kick velocity[3], post-kick velocity[3], total consumed force[3]; 16 float force-channel vectors |
| Beam | 112 | uint32 id/endpoints/disabled-broken flags; nine floats length/rest/k/d/stress/strength/old rest/old k/old strength; uint32 old active/type/bounded; float actual generated endpoint 1/2 force vectors and elastic/damping vectors |
| Contact | 104 | uint32 node/kind/feature/barrier; float position/normal/pre-kick velocity/raw law force/actual increment/pre-application force vectors; float mass/penetration; uint32 material ID/reserved |

Contact kinds: 1 terrain, 2 native box, 3 native triangle. Material IDs are FNV-1a uint32 of the native model name and resolve through `contact-materials.json`. Actor identity comes from the enclosing tick header. Native indices are meaningful within the immutable scene; the controlled barrier additionally has logical feature 1.

Contact impulse is actual increment times dt. Normal/tangential vectors are projections of that same increment on the recorded native normal; they do not add another force to physics. Contact work is its contribution to actual node midpoint integration work. Individual application peaks and net barrier force peaks are distinct. These are solver observations, not calibrated sensor readings or a measurement of heat/sound/fracture dissipation.

Dense beam snapshots capture rest/stiffness/strength and active-state transitions, plus actual endpoint writes. Aggregate schema-2 flag 16 means its bounded eight-event projection omitted transitions covered by the required dense stream. The omitted count remains visible. Without dense capture, the original event overflow still sets invalid/loss flag 1. Complete requires both archives to be healthy. Beam removal remains a storage bookkeeping port; full fracture energy remains unqualified.

## Recovery and inspection

`detail-health.json` records produced, enqueued, written, durable, dropped, missing, trigger/range and sticky I/O state. `detail-gaps.jsonl` retains explanations. Partial frame writes attempt truncation back to the preceding frame boundary before later writes; rollback failure leaves a nonpassing archive. Actual storage exhaustion still depends on restoring writable space. No callback waits for that restoration.

Post-run streaming inspection verifies identities, finite values, CRCs, tick continuity and required ranges. It writes `detail-index.jsonl` only for verified frames, plus dense transition projections. The HTTP tick inspector rechecks the selected frame's CRC and identity before returning node/channel, beam/application and contact vectors. Missing ticks return no sample; the UI does not interpolate a gap.

Fault qualification definitions are immutable and prominently labeled: `short-history` omits required history, `queue-overflow` injects one queue-full admission at trigger+500 through the normal drop path, and `storage-error` injects a partial block failure with rollback. They exercise continued capture and sticky Incomplete; they are not claims that the disk was physically filled. Earlier real queue overflow attempts remain evidence of the actual resource failure.

Commands use native tick-safe pause/resume/cancel. Cancelling before a required post-window completes retains records and stays incomplete. Abrupt process exit preserves committed prefixes; a fresh manual retry has its own identity. A successful successor cannot change the earlier attempt's quality.
