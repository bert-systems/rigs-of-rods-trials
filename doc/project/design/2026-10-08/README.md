# Trial architecture evaluation records — 2026-10-08

Canonical evaluation: [trial-platform-architecture-options.md](../trial-platform-architecture-options.md). [Illustrated HTML](../../reports/trial-architecture-options-2026-10-08.html).

The document proposes native force/energy observation, a common environment service, two UI options, and 14 implementation/validation epics. It is an evaluation, not a final approved implementation contract. Source remains `e85535569102b6251849af574026984e3213b3f4`; content remains `34fefdd126784bf87b068fc283f812525d159dd7`. No engine code, dependencies, build or simulator behavior changed.

| Record | Purpose |
| --- | --- |
| [references.json](references.json) | 16 pinned local-source ranges plus 11 primary physics/technology references |
| [render-architecture.mjs](render-architecture.mjs) | Reproducible report generator; uses the canonical evaluation Markdown |
| [architecture-client.js](architecture-client.js) | Illustrative capture-payload calculator, embedded in the HTML |
| [report-validation.json](report-validation.json) | Latest source/link/browser checks and outside-Git screenshot locations |
| [verify-architecture.py](verify-architecture.py) | Reproducible report QA, using a fresh installed-Chrome context |

The renderer reuses the preserved [platform-report stylesheet](../../research/2026-10-08/report-style.css) and bundled `marked` 17.0.5. HTML embeds the stylesheet, JavaScript and four accessible SVGs, and requires no external network resources to read.

```powershell
& 'C:\Users\berts\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' `
  'D:\Rigs of Rods\rigs-of-rods-trials\doc\project\design\2026-10-08\render-architecture.mjs' `
  'D:\Rigs of Rods\rigs-of-rods-trials' `
  'C:\Users\berts\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules\marked\lib\marked.esm.js'
```

```powershell
& 'D:\Rigs of Rods\source-build-2026-10-08\tools\Scripts\python.exe' `
  'D:\Rigs of Rods\rigs-of-rods-trials\doc\project\design\2026-10-08\verify-architecture.py'
```

The renderer replaces only the new architecture report; the verifier creates a fresh timestamped capture folder under the workspace, then updates this design record's latest lightweight validation JSON. Both use previously available tools; no framework/dependency installation is implied.

Source inspection focused on actor/global phase order, consumed force/reset, contact branching and barycentric application, beam force adjustment/transitions, direct rope-linked state/force transfer, scattered atmospheric models and graphical particle construction. These are static observations, not broad runtime tests.

Performance rates are theoretical payload calculations. Capture/latency/overhead numbers are proposed targets. Staffing/calendar ranges are judgment estimates before integration spikes and calibration. The final physics/energy interpretation must pass independent scenario-specific validation.

## Implementation review baseline

The completed Q&A is now consolidated in the [implementation specification](../trial-platform-implementation-spec.md) and [HTML review copy](../../reports/trial-implementation-spec-2026-10-08.html). Reproduction, new validation records and evidence boundaries are in [implementation-review.md](implementation-review.md). Historical architecture evaluation files above remain preserved.
