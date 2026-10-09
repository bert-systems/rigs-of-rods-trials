# Local terrain collection

Inspected: 2026-10-08. Source: D:\Rigs of Rods\content\Terrains.

Found **23 ZIP packages**, **75 terrain definitions**, and **0.72 GiB** of compressed archives. These are **44 modern .terrn2** and **31 legacy .terrn** entries, including paired and terrain variants. Archive-directory/definition-read errors: **0**.

These packages reside in the workspace parent, outside the Git fork. The fork retains its three versioned Simple Test Terrain definitions. The selected first pilot remains the versioned Daf Semi plus Simple Test Terrain, with a controlled barrier and analytical reference fixtures (D010).

## Available packages

| Archive | Compressed MiB | Terrain definitions / names |
| --- | ---: | --- |
| airport.zip | 4.2 | Sweden Airport; Sweden Airport |
| auriga-0.4.zip | 18.9 | Auriga Proving Grounds |
| BakerRanchV2.zip | 72.6 | Baker Ranch V2 |
| Belgium.zip | 65.1 | Belgium; Belgium; Belgium FPS version |
| Box5MonsterJam.zip | 2.4 | Monster Jam Madness; Monster Jam Madness |
| Brutal_Valley_V2.zip | 102.0 | Brutal Valley; Brutal Valley; Brutal Valley Dry; Brutal Valley Dry; Brutal Valley Dry FPS; Brutal Valley Dry FPS; Brutal Valley FPS; Brutal Valley FPS; Brutal Valley Wet; Brutal Valley Wet; Brutal Valley Wet FPS; Brutal Valley Wet FPS |
| castlegreen_04.zip | 39.2 | Castlegreen |
| CM 0.5.zip | 9.4 | N-Labs Testing Facility 0.5 |
| f1track_08.zip | 7.8 | f1_testtrack 0.7; f1_testtrack 0.8 |
| fall_run_04.zip | 43.7 | fall_run; fall_run_detailed; Fall Run; fall_run_offroadrace; Fall Run Off-Road Race; fall_run_roadrace; Fall Run Road Race; slinky |
| grenoble.zip | 9.6 | Grenoble; Grenoble |
| lapaz2.zip | 11.5 | La Paz; La Paz |
| NarvalskWoods.zip | 28.3 | Narvalsk Woods; Narvalsk Woods; Narvalsk Woods FPS; Narvalsk Woods FPS |
| NeoQ2.0.zip | 66.5 | NeoQ2-0 (Dev Build Only); NeoQ2-0 |
| NeoQueretaro.zip | 35.3 | NeoQueretaro |
| Penguinville_1.zip | 20.5 | Penguinville; Penguinville |
| Pines Proving Grounds.zip | 31.7 | Pines Proving Grounds; Pines Proving Grounds; Pines Proving Grounds-Dry; Pines Proving Grounds-Dry; Pines Proving Grounds Rock; Pines Proving Grounds Rock; Pines Proving Grounds-Wet; Pines Proving Grounds-Wet |
| RockCrawlHeaven.zip | 11.4 | Wild West; Wild West |
| RoRCompound-0.4.zip | 22.1 | RoR Compound; RoR Compound 2; RoR Compound 2 - Dirt; RoR Compound 3; RoR Compound 3 - Dirt; RoR Compound - Dirt; RoR Compound Freestyle; RoR Compound Freestyle - Dirt |
| squishymonsterstadium.zip | 30.3 | Squishy Stadium |
| sunset_mesa_04.zip | 47.7 | sunset_mesa; sunset_mesa_detailed; Sunset Mesa; sunset_mesa_fps; sunset_mesa_low_fps; sunset_mesa_storm; Sunset Mesa Storm |
| TGTT-0.4.zip | 37.5 | Top Gear Test Track |
| TrainValley.zip | 18.8 | Train Valley; Train Valley FPS |

## Use in later trials

Archive and descriptor names indicate that the collection includes road/track, airport, rough-terrain and arena candidates. For example, Pines Proving Grounds, TGTT, f1track and airport merit later suitability review. This is a discovery shortlist based on names and definitions; vehicle clearance, collision surfaces, terrain friction, barriers and flight suitability require inspection and source-built runtime tests.

When a package is selected, record its full archive hash, actual resolved terrain/GUID, dependencies, relevant content permissions and collision/environment configuration in a new trial session. Retain original packages and use a private source-build profile. Asset availability is separate from executable/DLL build provenance.

## Inspection limits and records

Inspected ZIP member directories and terrain-definition text up to 256 KiB per definition. Terrain definitions that were read have SHA-256 and ZIP CRC values in the [machine-readable inventory](terrain-inventory.json), alongside sizes, GUID/config fields and license/readme candidate filenames. Complete archives were not extracted or CRC-tested across all assets, and no terrain was loaded. Permissions, compatibility, physics calibration and completeness of the upstream terrain catalog are unresolved.

Related: [implementation decisions](../../design/implementation-decisions.md), [platform research](../../../../platform.md), [project memory](../../../../project-memory.md).
