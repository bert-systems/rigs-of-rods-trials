# Build, rebuild, run, and record

Latest qualification: [Slice 06](slices/slice-06.md). Trial builds use `tools/trials/build.ps1 -Session <unique-root> -Parallel 6`; focused native CTests also build Release. `tools/trials/start.ps1 -Archive <unique-durable-root>` can keep trial archives on a different volume from native build outputs. Record both absolute roots and keep all originals. Storage/memory preflight floors still apply to the archive volume; do not silently lower them to fit a run. Different-volume performance measurements must remain separate. Optional observer profiling and continuous native screenshots belong in declared diagnostic/visual runs, not budget comparisons.

Canonical Windows procedure for the `bert-systems/rigs-of-rods-trials` source fork. Established from the successful 2026-10-08 trial. Read [PROJECT.md](../../PROJECT.md) and [project memory](../../project-memory.md) first.

## Repository and proof requirements

Source is `D:\Rigs of Rods\rigs-of-rods-trials`, origin `https://github.com/bert-systems/rigs-of-rods-trials.git`. Upstream is [RigsOfRods/rigs-of-rods](https://github.com/RigsOfRods/rigs-of-rods). Starter assets come from the `content` submodule.

Preserve `D:\Rigs of Rods\source-build-2026-10-08`. Its scripts hardcode that directory and overwrite logs/configuration. Do not rerun them in place. The installed `D:\Rigs of Rods\RoR.exe` and its DLLs must not provide source-build proof.

A build/run record needs source identity, commands and exit codes, executable identity, and observable simulation behavior. Record whether dependencies were cached, downloaded, or compiled. A clean game rebuild cleans game target outputs; it does not rebuild the whole dependency cache.

## Verified toolchain

| Component | Baseline |
| --- | --- |
| Visual Studio | 2022 Professional 17.14.11, C++ x64 tools |
| Compiler | MSVC 19.44.35214, toolset folder 14.44.35207 |
| CMake / Conan / Ninja | 3.31.10 / 2.33.0 / 1.13.2 |
| Python | 3.13.3 |
| Capture | FFmpeg 8.1.1, gdigrab / libx264 |
| Report checks | Playwright 1.63.0, installed Chrome, fresh headless context |

Existing tools are in `D:\Rigs of Rods\source-build-2026-10-08\tools\Scripts`. The baseline used a private `CONAN_HOME`.

Top-level CMake specifies a 3.16 minimum, but the Conan provider requires CMake 3.24 or later and Conan 2.0.5 or later. Start with the verified versions and check current source/documentation before changing them.

On a replacement machine, provision VS 2022 C++/Windows SDK tools and Git, then create an isolated Python environment. With Python 3.13 installed and a new session directory already created:

```powershell
py -3.13 -m venv "$sessionRoot\tools"
$packages = @(
    'cmake==3.31.10', 'conan==2.33.0', 'ninja==1.13.2',
    'playwright==1.63.0', 'pillow==12.3.0'
)
& "$sessionRoot\tools\Scripts\python.exe" -m pip install @packages
if ($LASTEXITCODE -ne 0) { throw 'Tool installation failed' }
```

This replacement-machine bootstrap is a procedure to verify, not a completed baseline test. FFmpeg is separate; the baseline resolved it from Windows WinGet's Links directory. Existing Chrome was used for HTML checks without downloading a Playwright browser.

## Start a separate session

Use PowerShell, a descriptive label, and a new directory:

```powershell
$ErrorActionPreference = 'Stop'
$workspace = 'D:\Rigs of Rods'
$repo = Join-Path $workspace 'rigs-of-rods-trials'
$label = 'source-build'
$sessionRoot = Join-Path $workspace (
    (Get-Date -Format 'yyyy-MM-dd-HHmmss') + '-' + $label
)
if (Test-Path -LiteralPath $sessionRoot) {
    throw "Session directory already exists: $sessionRoot"
}
New-Item -ItemType Directory -Path $sessionRoot | Out-Null
foreach ($folder in @('logs', 'scripts', 'report', 'media')) {
    New-Item -ItemType Directory -Path (Join-Path $sessionRoot $folder) | Out-Null
}
$build = Join-Path $sessionRoot 'build'
$tools = 'D:\Rigs of Rods\source-build-2026-10-08\tools'
$env:PATH = "$tools\Scripts;$env:PATH"
$env:CONAN_HOME = Join-Path $sessionRoot 'conan-cache'
$devShell = 'C:\Program Files\Microsoft Visual Studio\2022\Professional\Common7\Tools\Launch-VsDevShell.ps1'
& $devShell -Arch amd64 -HostArch amd64 -SkipAutomaticLocation
Set-Location -LiteralPath $repo

git status --short
git remote -v
git branch --show-current
git rev-parse HEAD
git submodule status --recursive
cmake --version
conan --version
ninja --version
cl
```

For a replacement-machine environment, point `$tools` at the new tools directory. The new Conan cache above supports a fresh dependency-resolution trial. Ordinary iteration may reuse a known cache by explicitly changing `CONAN_HOME` and recording that choice.

Keep user changes intact. If content is uninitialized, run `git submodule update --init --recursive` and check its exit code. Inspect any local submodule changes before updating.

Save provenance before configuring: timestamp/time zone, source path/origin/branch/commit, porcelain status, submodule commits/status, tool versions, actual compiler/architecture, profiles/environment, machine/GPU, and whether the build directory/cache initially existed. Include a source patch or equivalent record for a dirty build.

## Configure and resolve dependencies

These are the baseline options with output paths changed to the new session:

```powershell
conan profile detect --force
if ($LASTEXITCODE -ne 0) { throw 'Conan profile detection failed' }
conan remote add rigs-of-rods-deps https://nexus.anotherfoxguy.com/repository/rigs-of-rods/ -f
if ($LASTEXITCODE -ne 0) { throw 'Conan remote setup failed' }

$configureArguments = @(
    '-S', $repo, '-B', $build, '-G', 'Ninja',
    '-DCMAKE_BUILD_TYPE=Release',
    '-DCMAKE_PROJECT_TOP_LEVEL_INCLUDES=cmake/conan_provider.cmake',
    "-DCMAKE_INSTALL_PREFIX=$sessionRoot\redist",
    '-DROR_CREATE_CONTENT_FOLDER=ON'
)
cmake @configureArguments
$configureExit = $LASTEXITCODE
if ($configureExit -ne 0) { throw "Configure failed: $configureExit" }
```

Capture full output, elapsed time, and exit codes, including dependency work. Native process exit codes must be saved immediately; `$ErrorActionPreference` alone does not establish native command success.

The provider combines the default host profile with a generated `auto-cmake` profile based on the actual compiler. On this machine, Conan default detection reported compiler 195 because VS 2026 was also installed. CMake's generated host profile correctly selected 194 for VS 2022. Preserve profiles and inspect `CMakeCache.txt`/compiler identification. Do not choose a compiler solely from the default profile name.

Keep the resolved Conan graph/lock, generated profiles, CMake cache, and diagnostics with the configuration log. `CMakeUserPresets.json` is generated/ignored, not a maintained project instruction.

### Optional dependency lock replay

[The baseline lock](baselines/2026-10-08/conan.lock) records recipe versions/revisions. The original configure did not supply a lock; it recorded the resolved lock afterward.

For a deliberate replay with matching source/dependency inputs, add the following before invoking CMake:

```powershell
$lockPath = Join-Path $repo 'doc\project\baselines\2026-10-08\conan.lock'
$configureArguments += "-DCONAN_INSTALL_ARGS=--build=missing;--lockfile=$lockPath"
```

The local provider forwards `CONAN_INSTALL_ARGS` to `conan install`. A fresh locked replay has not yet been performed. Verify the resulting graph and retain its outcome. Changed requirements may need a new lock; preserve the historical file. A lock does not pin the whole toolchain or guarantee remote availability or identical executable bytes.

## Build, rebuild, and increment

Run as separate recorded steps, stopping on nonzero exits:

```powershell
# First game build in the new directory.
cmake --build "$build" --parallel 16
$buildExit = $LASTEXITCODE
if ($buildExit -ne 0) { throw "Build failed: $buildExit" }

# Clean game rebuild with configured dependencies.
cmake --build "$build" --clean-first --parallel 16
$rebuildExit = $LASTEXITCODE
if ($rebuildExit -ne 0) { throw "Rebuild failed: $rebuildExit" }

# Incremental build.
cmake --build "$build" --parallel 16
$incrementalExit = $LASTEXITCODE
if ($incrementalExit -ne 0) { throw "Incremental build failed: $incrementalExit" }

ctest --test-dir "$build" -N
```

Record command, start/end timestamps, seconds, exit code, and log for each step. Sixteen parallel jobs was the baseline choice on a 16-core/32-thread machine.

The version target intentionally runs again and can relink RoR without engine edits. Baseline CTest listed zero tests. Use a meaningful simulation scenario to validate behavior; do not describe an empty test registration as a passing suite.

Record the output executable and hash:

```powershell
$bin = Join-Path $build 'bin'
$exe = Join-Path $bin 'RoR.exe'
if (!(Test-Path -LiteralPath $exe)) { throw 'Expected executable is absent' }
$executableHash = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash
git rev-parse HEAD
git status --porcelain
$exe
$executableHash
```

Preserve source status before build and at session close. Distinguish later edits from actual build inputs.

## Private runtime profile

A `config` directory beside RoR.exe selects portable user storage. The baseline used nested paths `$bin\config\config\RoR.cfg`, `$bin\config\config\ogre.cfg`, and `$bin\config\scripts\build-proof.as`.

Create them in the new build:

```powershell
$profileDirectories = @("$bin\config\config", "$bin\config\scripts")
New-Item -ItemType Directory -Force -Path $profileDirectories | Out-Null
@(
    'app_config_long_names = false',
    'app_disable_online_api = true',
    'diag_preset_veh_enter = true',
    'gfx_fps_limit = 60',
    'gfx_shadow_type = None',
    'gfx_sky_mode = 0',
    'gfx_water_mode = 1'
) | Set-Content -LiteralPath "$bin\config\config\RoR.cfg" -Encoding UTF8
```

`diag_preset_veh_enter` is a baseline workaround: `-enter` writes a CLI CVar while config-origin spawning reads the persistent/diagnostic CVar. Recheck after any CLI/spawn fix. This configuration did not repair engine code.

Write the following to `$bin\config\config\ogre.cfg` as ASCII for this machine:

```ini
Render System=Direct3D9 Rendering Subsystem

[Direct3D9 Rendering Subsystem]
Allow NVPerfHUD=No
FSAA=0
Floating-point mode=Fastest
Full Screen=No
Multi device memory hint=Use minimum system memory
Rendering Device=Monitor-1-NVIDIA GeForce RTX 3090
Resource Creation Policy=Create on all devices
Use Multihead=Auto
VSync=Yes
VSync Interval=1
Video Mode=1280 x 720 @ 32-bit colour
sRGB Gamma Conversion=No
```

The rendering-device string is machine-specific. Inspect available renderer/device options on another machine. Record the backend, resolution, and settings actually used.

## Launch and verify provenance

Manual smoke test:

```powershell
$arguments = @('-map', 'simple2.terrn2', '-truck', 'b6b0UID-semi.truck', '-enter')
$launchParameters = @{
    FilePath = $exe
    WorkingDirectory = $bin
    ArgumentList = $arguments
    PassThru = $true
}
$process = Start-Process @launchParameters
```

The native game opens visibly for the simulation/capture. Background helper processes should use hidden windows.

For a scripted repeat, copy [the historical proof script](baselines/2026-10-08/build-proof.as) into the new session and portable profile. Update commit/toolchain/overlay labels to the actual new build, then append `'-runscript', 'build-proof.as'` to the arguments before launching. Retain the exact script in the evidence.

The baseline script initializes engine/gear/parking brake, idles for five seconds, uses 85% throttle until 29 seconds, applies 60% brake, requests screenshots around 3/16/32 seconds, logs per-second positions/wheel speed, and quits after 36 seconds. Timing starts when a current truck is available. A player who is not seated can leave the script waiting; inspect entry configuration and logs.

While running, record PID, launch arguments, working directory, observed process executable path, SHA-256, observed window title/version, and loaded DLL paths. Inspect `Get-Process -Id $process.Id`, its `Path` and `Modules`, and CIM metadata as needed. Confirm module origins match the new build, documented dependency cache, or normal system paths. Investigate any parent-installation modules. A version/title screenshot alone is insufficient provenance.

## Capture and simulation checks

The game provides native screenshots; the proof script requested them with:

```cpp
game.pushMessage(MSG_APP_SCREENSHOT_REQUESTED, null);
```

Collect the actual files from the private profile and identify their sequence/scenario state. Do not substitute generated images for evidence.

FFmpeg captured the native window. After confirming the actual game title, the baseline command pattern was:

```powershell
$ffmpeg = (Get-Command ffmpeg.exe -ErrorAction Stop).Source
$title = (Get-Process -Id $process.Id).MainWindowTitle
if ([string]::IsNullOrWhiteSpace($title)) { throw 'Game window is not ready' }
$captureArguments = @(
    '-hide_banner', '-y', '-f', 'gdigrab',
    '-framerate', '30', '-draw_mouse', '0', '-i', "title=$title",
    '-vf', 'scale=1280:-2', '-c:v', 'libx264',
    '-preset', 'veryfast', '-crf', '22', '-pix_fmt', 'yuv420p',
    '-t', '40', '-movflags', '+faststart',
    "$sessionRoot\media\simulation.mp4"
)
& $ffmpeg @captureArguments
$captureExit = $LASTEXITCODE
```

Record output/stderr and exit code. If the scripted game closes before capture's 40-second limit, inspect the log and finalized media. Require a playable clip rather than assuming the recorder status establishes simulation success. Use bounded supervision, record timeouts/termination, and start capture early enough to include idle, acceleration, and braking.

Collect `RoR.log`, `Angelscript.log`, script, launch/process records, screenshots, and video. Find actual log locations under the private profile; script messages can appear in both logs. Preserve failed attempts under clearly named paths before another attempt.

A passing driving smoke test needs:

1. Verified source-built executable and module origins.
2. Loaded requested terrain/vehicle and an available controlled actor.
3. Initialization, movement samples, and a completion marker, or equivalent recorded manual observations.
4. Position changes and nonzero wheel speed, with sample count/duration and defined metrics.
5. Screenshots and playable video from the same scenario, with logs/warnings retained.
6. Honest tested scope, workarounds, and unresolved issues in the report.

Baseline measurements were 36 samples, maximum displacement 125.54 m, and maximum wheel speed 19.9565 km/h. Displacement means distance from spawn, not path length; wheel speed is not GPS speed. Compute fresh results for each session.

## HTML evidence and packaging

Suggested portable layout:

```text
<session>/
  build/                 game, DLLs, resources, private runtime profile
  conan-cache/           optional private dependency cache
  scripts/               exact build/run/capture/report scripts
  logs/                  original outputs, including failed attempts
  media/                 native screenshots and finalized capture
  report/
    index.html
    media/               relative report media
    evidence/            selected logs and scripts
    provenance.json
    verification.json
    launch.json
    runtime-process.json
    conan.lock
    report-validation.json
    evidence-manifest.json
```

The HTML should identify fork/commit/dirty status, distinguish configuration/build/rebuild/incremental stages, report timings/exits, and show executable/process provenance. Embed native screenshots/video with relative paths. Explain the scenario, metric definitions, issues, and scope limits.

Serve on a loopback port or open locally. Use Playwright in a fresh isolated context to check local links/media, console errors, desktop/mobile overflow, video metadata, and actual playback. Playwright validates the HTML; native capture provides game video.

Archive the report with required relative assets/evidence. Include a SHA-256 file manifest, inspect archive contents, and check that extracted links/media work. The archive need not include the large build/cache trees; state what it contains and retain raw logs in the session root.

## Session closeout

For Slice 07 use a fresh durable session on a volume with sufficient capacity; `C:\Users\berts\Documents\RoR-trials-evidence\trial-slice-07-2026-10-10-013100` retains this session's build and all originals. `build.ps1 -Session <new-root> -Parallel 6`, `start.ps1 -Session <new-root> -Port <free-port> -Renderer OpenGL -EvidenceFrames`, then `verify-slice-07.py --session <new-root> --base <loopback-url> --phase qualification` exercise frozen later-collision fixtures and regressions. `verify-slice-07-ui.py` authors fresh native trials with unique names; reruns add retained attempts. Managed contract reinspection accepts the archive root and covers aggregate-only as well as optional-probe captures. See the [frozen contract](../../apps/trials/impact-fixture-format.md) and [delivery](slices/slice-07.md). PNG/video capture adds cost and must remain outside performance-budget claims.

Write a summary with objective, source inputs, commands/results, runtime behavior, media/HTML checks, issues, and absolute evidence paths. Update [todo.md](../../todo.md) and [project-memory.md](../../project-memory.md); link detailed new summaries from the project docs.

Preserve historical records. Add dated corrections rather than replacing original evidence. Keep generated build/cache/media outside Git; select lightweight docs/scripts/records for versioning when repository publication is requested.

## References

- [Versioned baseline records](baselines/2026-10-08/README.md)
- [Local BUILDING guidance](../../BUILDING.md)
- [Upstream Windows guide](https://github.com/RigsOfRods/rigs-of-rods/wiki/Compile-(Windows))
- [Developer portal](https://developer.rigsofrods.org/)
- [Conan provider implementation](../../cmake/conan_provider.cmake)

## Slice 02 recording correction

The user reported poster-then-blank video. Original/Slice 01 MP4 pixels are nonblank; WebM and decoded-image players provide compatible alternatives while preserving originals. Codex in-app rendering remains unverified. `media-evidence.py` packages alternatives and `verify-media.py` checks visible screenshot pixels and image progression.

OpenGL/GDI capture produced genuinely black frames and was rejected. Use `start.ps1 -Renderer OpenGL -EvidenceFrames` and `native-frames-video.py` to encode actual RoR renderer PNGs. Requests occur nominally every 0.5render seconds, may be delayed and add overhead. Video does not replace native physics ticks. See the [runbook](../../apps/trials/README.md).


## Slice 03 build/record continuation

Use `tools/trials/build.ps1 -Parallel 6` for the demonstrated workstation build; concurrency is now configurable (default 8). Preserve C1060/repair transcripts rather than presenting retries as a single successful first pass. Read the [Slice 03 profile/runbook](../../apps/trials/README.md) before characterization.

Run `verify-slice-03.py --phase benchmark` with continuous evidence frames disabled; it verifies exact native path/module/hash, raw CRC probes, repeated full/off coast, dry fixtures and nonzero steady wind. The common probe is part of both profiles; off bypasses the complete ledger but not trial control/probe overhead. Repeat medians/quantiles are wall-step duration, not process CPU.

For native media, restart the owned coordinator after all workers are terminal with `-EvidenceFrames`, then run `--phase visual`. Encode genuine PNGs with `native-frames-video.py`, package image/WebM fallback with `media-evidence.py` and verify visible pixels with `verify-media.py`. Retain startup images and label the presentation clock separately from physics time. The final report and bundled evidence must pass local-reference, desktop/mobile, player-progression and extracted-file SHA checks. Codex in-app GPU rendering is still not verified.
