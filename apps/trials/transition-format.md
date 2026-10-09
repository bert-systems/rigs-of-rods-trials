# Beam transitions and scoped reference fixtures

Slice 05 extends aggregate schema 2 (2,080 bytes/record) without changing its byte layout. Manifest schema 5 declares `transition-flags-v2`. Historical schema 2 archives remain readable; the old producer did not independently emit strength-only changes.

Eight event slots start at byte 1376, with 88 bytes/event: beam ID and kind (uint32), then ten float64 values: length, old/new rest, old/new stiffness, old/new strength, old/new diagnostic storage and final recorded native law stress. Kind is a bit mask: 1 linear rest/stiffness change; 2 active beam removed; 4 strength change; 8 unsupported rest/stiffness change. Strength can coexist with other bits. Strength alone contributes zero storage port. Native snapshots compare the beginning and end of each tick; they do not preserve every intermediate mutation within that tick.

`restPort = U(new parameters, current length) - U(old parameters, current length)`. Removal contributes `-U(new parameters, current length)`, so a combined rest change/removal removes storage once. These signed ports explain changes to modeled storage. They are **not calibrated material dissipation, crack energy or energy dispersal**. `lawStressN` is the final stored native stress; applied force includes the native correction and can differ, especially for removal. Consumed and generated epochs remain distinct. Fixture initialization primes the real beam kernel before first integration, with consumed epoch zero.

Required overflow without dense capture marks quality invalid. Barrier flag16 declares projection omissions covered by mandatory dense detail. The aggregate inspector reports omissions; its projected counts are not the full dense totals.

## Pinned dry native fixtures

All use one 100 kg moving node, three fixed anchors, one active normal beam, precise fixture length arithmetic, k=10,000 N/m, c=0, rest=1 m, initial velocity=0, gravity=0, disabled drag/ground contact, zero settling, and a 0.1–1 s observation window. Two other fixture beams are disabled. The immutable scenario/asset pair selects initialization; these are not editable material definitions.

| Scenario | Extension | Yield bounds | Strength | Purpose |
| --- | --- | --- | --- | --- |
| `yield-tension-v1` | +0.05 m | ±200 N | 2,000 N | Rest grows and strength decreases; plastic coefficient 0.25 |
| `yield-compression-v1` | −0.05 m | ±200 N | 2,000 N | Rest contracts; native compression preserves strength; coefficient 0.25 |
| `fracture-v1` | +0.05 m | ±1e9 N | 200 N | Real native break/removal before integration |
| `protected-beam-v1` | +0.05 m | ±1e9 N | 200 N | Synthetic moving node is cab-flagged with one live beam; native guard preserves beam and changes strength to 400 N |

The protected fixture has no cab collision surface and does not qualify vehicle cab topology/contact. The first transition is at tick 1. Initialization prime and subsequent solve share that record. Qualification concerns this controlled initialization, not later high-speed collision fracture.

`beam-transition-reference-v1` independently integrates the native one-dimensional rules in double precision, including initialization prime, correction, strength update, storage ports and epochs. Limits include 50 µm world-position error (float32 COM near x=500 m), 0.001 m/s velocity, 0.05 N consumed/generated force, 0.001 J storage/ports, 0.1 J closure envelope, 1e-5 N unattributed/reconstruction, 1e-3 impulse/work discrepancies and 0.001 s duration. Counts and identity must agree exactly. Scoped Passed validates implementation/capture agreement; material calibration remains unqualified. Original freefall/spring/damper limits are unchanged.

## Inspector

`GET /api/attempts/{id}/transitions?offset=0&limit=20` serves terminal attempts with a complete CRC/DONE/footer-verified aggregate archive. Offset is 0–1,000,000; limit 1–100. Missing/active attempts return 404, invalid pages 400, incomplete/corrupt/unsupported archives 409. Each explicit query rechecks the archive, with a bounded event page. This is a local retained-study scan, not a high-concurrency index. The workbench starts with 20 events and displays signed ports, no-event states and omitted projections.
