# Source-build baseline — 2026-10-08

These are small, unchanged copies of records from the original successful trial. They are retained in the source fork so repository history can preserve the evidence identity even when the full local build directory is unavailable.

| File | Contents |
| --- | --- |
| [provenance.json](provenance.json) | Fork/source/submodule identity, initially absent build directory, tools, and machine context |
| [verification.json](verification.json) | Executable hash, dated upstream comparison, build/rebuild/incremental outcomes, movement metrics, and screenshot names |
| [report-validation.json](report-validation.json) | Playwright HTML/media/playback checks |
| [conan.lock](conan.lock) | Resolved Conan recipe versions/revisions and build requirements |
| [build-proof.as](build-proof.as) | Exact historical driving/screenshot script; its labels identify this baseline |

Original artifacts remain at `D:\Rigs of Rods\source-build-2026-10-08`. The HTML is `report\index.html`, and the portable archive is `rigs-of-rods-source-build-evidence.zip` under that root. Images, video, raw logs, full build, and cache remain outside this Git checkout.

Paths and process IDs inside the records describe the historical machine/run, not portable configuration or current processes. The original source tree was clean; later documentation changes do not change that fact.

Update the script's identity labels before reuse in a different session. The lock describes the resolved graph; the original configure did not use it as an input. See [the canonical runbook](../../build-and-record.md) for new sessions and replay limitations.

This baseline shows a successful Release x64 ground-vehicle scenario, with nonfatal diagnostics and a vehicle-entry config workaround. It does not establish full engine/physics correctness.
