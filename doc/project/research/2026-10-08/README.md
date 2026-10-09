# Platform research record — 2026-10-08

Canonical narrative: [platform.md](../../../../platform.md). Illustrated, offline companion: [HTML report](../../reports/platform-evaluation-2026-10-08.html).

## Scope and authority

Research evaluates `bert-systems/rigs-of-rods-trials` at source `e85535569102b6251849af574026984e3213b3f4`, with starter content `34fefdd126784bf87b068fc283f812525d159dd7`. Engine source remained unchanged; foundation docs were already saved locally. No new build, simulator run, asset download, native instrumentation or trial-system implementation was performed.

Authority order: checked-out implementation for semantics/names, versioned content for starter assets, then primary official documentation for the broader landscape. Developer documentation carries older version labels than this source. The report distinguishes source-supported, previously runtime-demonstrated and proposed capabilities.

The existing [source-build proof](../../baselines/2026-10-08/README.md) is historical evidence for one ground-driving scenario. It does not validate new impact, wind, flight or repeatability claims. The community resource catalog denied automated access, preventing exhaustive current asset/license/compatibility research.

## Preserved artifacts

| File | Purpose |
| --- | --- |
| [source-inspection.json](source-inspection.json) | Identity, inspection scope, starter-asset hashes and registration counts |
| [binding-inventory.json](binding-inventory.json) | Index of 2,236 recognized static scripting registrations, with paths/lines |
| [references.json](references.json) | 54 references: 37 pinned source ranges and 17 official documentation/repository references |
| [render-report.mjs](render-report.mjs) | Markdown renderer plus explanatory diagrams and report UI |
| [report-style.css](report-style.css) | Stylesheet embedded into the report |
| [report-client.js](report-client.js) | Calculator and capability filters embedded into the report |
| [verify-report.py](verify-report.py) | HTML/source-anchor QA; new timestamped capture folder for each run |
| [report-validation.json](report-validation.json) | Final verification result and screenshot locations |
| [terrain-inventory.md](terrain-inventory.md) | Later Q&A inspection of the local downloaded terrain collection; separate from versioned starter content |
| [terrain-inventory.json](terrain-inventory.json) | ZIP metadata, terrain definitions/config fields, descriptor hashes and inspection limits |

The registration index includes methods, functions, properties, types and enums recognized by the scanner. Conditional/dynamic registrations and overloads need direct review. This is an index, not a runtime API conformance test.

## Reproduce the HTML

Use the bundled Node runtime and `marked` 17.0.5. CSS, JavaScript and accessible SVGs are embedded; no external requests/CDN are required. Linked source/docs and local records are references, not embedded copies.

```powershell
& 'C:\Users\berts\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' `
  'D:\Rigs of Rods\rigs-of-rods-trials\doc\project\research\2026-10-08\render-report.mjs' `
  'D:\Rigs of Rods\rigs-of-rods-trials' `
  'C:\Users\berts\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules\marked\lib\marked.esm.js'
```

The renderer replaces this research HTML at its documented path. It must not overwrite an archived build/run evidence report. Refresh Markdown, references, identity/date labels and diagrams deliberately when scope changes. Illustrations do not update from engine measurements.

## Reproduce report QA

Reuse the previous tools environment without modifying baseline evidence. Verification uses Playwright and a fresh headless installed-Chrome context. It creates a timestamped folder under the workspace and updates only this research folder's latest lightweight validation JSON.

```powershell
& 'D:\Rigs of Rods\source-build-2026-10-08\tools\Scripts\python.exe' `
  'D:\Rigs of Rods\rigs-of-rods-trials\doc\project\research\2026-10-08\verify-report.py'
```

Final automated checks passed: 12 sections, 15 tables, four accessible SVGs, 22 coverage dimensions, 37 valid source ranges, 14 local HTML links, calculator/filter behavior, no browser errors/external requests, and no page horizontal overflow at 1440 px and 390 px.

Visual inspection covered the overview, platform map, sampling diagram, energy ledger, trial lifecycle and mobile navigation. Final screenshot/JSON directory: `D:\Rigs of Rods\platform-evaluation-2026-10-08-123840`. Earlier failed report-QA captures remain separately. Source end anchors, duplicate SVG markers, a non-rendered capture target and mobile text overflow were corrected before the successful check.

Playwright validates this report, not native simulator physics. Calculator results are ideal illustrations, not simulation measurements. The next architecture/design session must define measurement contracts, pilot scenarios, validation criteria and implementation scope.
