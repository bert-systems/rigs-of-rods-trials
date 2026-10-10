# Recorder health and diagnostic profiling

Slice 06 adds `recorder-health.json` schema 1, also exposed as `recorderHealth` on compact state/status and retained attempt results. `aggregate`, `probe`, and `detail` are null when absent. Historical archives without diagnostics remain readable and show unavailable; absence is not zero.

| Field | Meaning |
| --- | --- |
| enqueued / processed / queued | Admitted queue frames, recorder-consumed frames, independently sampled remaining frames |
| capacity / highWater | Fixed frame reservation and producer-observed maximum admitted queue occupancy |
| reservedQueueBytes / copiedBytes | Reserved fixed slots; logical populated bytes copied by the producer (not history copies) |
| written / durable / pendingSync | Successful DATA-block records, records acknowledged after file sync, successful writes awaiting sync |
| archiveBytes | Successful DATA-block bytes, including DATA/CRC/DONE framing; excludes header/footer and rolled-back partial writes |
| dropped / ioError / closed | Existing sticky required loss/I/O flags; recorder thread completed close path. Closed alone does not establish integrity or required coverage. Detail dropped combines queue-frame and contact-application loss as in the existing native contract. |
| syncCalls / syncWallUs / maxSyncWallUs | All attempted file synchronizations and steady-clock elapsed durations, including header/final/footer sync |
| encodeCrcWallUs / fileWriteWallUs | Recorder encoding/projection/checksum work and DATA fwrite elapsed durations. Aggregate/probe encoding timing includes formatted summary projection. Parallel recorder durations must not be summed as whole-worker elapsed time. |

Atomic snapshots are independently sampled diagnostics, not a transaction or scientific measurement. Queue slots may be reclaimed before durability. Detail admission includes all streamed prehistory/out-of-window frames; `enqueued - durable` is therefore not detail backlog. Use queued for transport pressure and pendingSync for successfully written selected data awaiting sync. A queue-depth sample can precede a writer's just-completed tail update.

Main-thread status refreshes around 100 ms. Writer-owned aggregate/probe/detail progress files publish around sync intervals and during final drain; I/O stalls may delay publication. The coordinator refreshes these during Finalizing, then adopts the final recorder snapshot after all native writers join. Malformed/transiently truncated JSON reads preserve last-known diagnostic state. Archive CRC/footer/count/coverage checks remain authoritative; required loss continues later observation and stays Incomplete. The UI's 80% pressure warning does not change admission, rates, retention or qualification.

The nominal 250 ms flush interval starts **after synchronization returns**. A slow sync cannot immediately force another sync on the next frame. This is not a hard durability latency SLA. Header and final drain/footer synchronization remain forced. Raw aggregate/probe/detail wire schemas and scientific acceptance profiles are unchanged.

`observerProfiling=true` requires full observation and `performanceProbe=true`. It is part of the immutable experiment definition/native configuration and checked capability handshake. It emits `observer-profile.json` schema 1 with step count, total elapsed and five phase sums/maxima: energy before, detail before, solver/attribution (including job waits), energy after/detail, and ledger finalize/queue. Clock overhead is included. Use separate diagnostic runs; budget runs leave this disabled.

No allocations, formatted logging, disk I/O or UI waits were added to physics callbacks. Counters are preallocated atomics; fixed detail slots copy only the coherent populated prefix. Unused contact tails cannot enter frame encoding, even after slot reuse. The slot budget and required history/contact capacity remain resource v2.

See [Slice 06](../../doc/project/slices/slice-06.md) for matched-drive and alternate-volume evidence. Larger/multi-actor workloads, separated/retriggered windows, physical disk exhaustion and coordinator orphan recovery remain unqualified.
