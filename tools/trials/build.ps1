param(
    [Parameter(Mandatory=$true)][string]$Session,
    [string]$Repo="",
    [string]$Tools='D:\Rigs of Rods\source-build-2026-10-08\tools\Scripts',
    [string]$ConanHome='D:\Rigs of Rods\source-build-2026-10-08\conan-cache',
    [string]$VsShell='C:\Program Files\Microsoft Visual Studio\2022\Professional\Common7\Tools\Launch-VsDevShell.ps1',
    [switch]$Clean
)
$ErrorActionPreference='Stop'
if(!$Repo){$Repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))}
$Session=[IO.Path]::GetFullPath($Session)
$Repo=[IO.Path]::GetFullPath($Repo)
if($Session.Contains('source-build-2026-10-08') -or $Session.StartsWith($Repo+'\',[StringComparison]::OrdinalIgnoreCase) -or $Session -eq $Repo){
    throw 'Use a unique evidence session outside the checkout and protected baseline.'
}
New-Item -ItemType Directory -Force -Path "$Session\logs","$Session\report" | Out-Null
$stamp=Get-Date -Format 'yyyyMMdd-HHmmss-ffff'
$sourceFiles=Get-ChildItem "$Repo\source","$Repo\cmake" -File -Recurse |
    Where-Object { $_.Name -eq 'CMakeLists.txt' -or $_.Extension -in '.h','.cpp','.c','.cmake' }
$hashes=[ordered]@{}
foreach($file in $sourceFiles){$hashes[$file.FullName.Substring($Repo.Length+1)]=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash}
$hashes['CMakeLists.txt']=(Get-FileHash "$Repo\CMakeLists.txt").Hash
$provenance=[ordered]@{time=(Get-Date).ToString('o');repo=$Repo;head=(git -C $Repo rev-parse HEAD);branch=(git -C $Repo branch --show-current);origin=(git -C $Repo remote get-url origin);content=(git -C "$Repo\content" rev-parse HEAD);dirty=@(git -C $Repo status --short);nativeSourceHashes=$hashes;conanCache=$ConanHome}
$provenance | ConvertTo-Json -Depth 5 | Set-Content "$Session\report\source-$stamp.json" -Encoding UTF8
git -C $Repo diff --binary --output="$Session\report\tracked-source-$stamp.patch"
$env:PATH=$Tools+';'+$env:PATH
$env:CONAN_HOME=$ConanHome
& $VsShell -Arch amd64 -HostArch amd64 -SkipAutomaticLocation
$nativeLog="$Session\logs\native-$stamp.log"
cmake -S $Repo -B "$Session\build" -G Ninja -DCMAKE_BUILD_TYPE=Release '-DCMAKE_PROJECT_TOP_LEVEL_INCLUDES=cmake/conan_provider.cmake' "-DCMAKE_INSTALL_PREFIX=$Session\redist" -DROR_CREATE_CONTENT_FOLDER=ON 2>&1 | Tee-Object $nativeLog
if($LASTEXITCODE -ne 0){throw "CMake configure failed: $LASTEXITCODE"}
$buildArgs=@('--build',"$Session\build",'--parallel','16')
if($Clean){$buildArgs+='--clean-first'}
cmake @buildArgs 2>&1 | Tee-Object -Append $nativeLog
if($LASTEXITCODE -ne 0){throw "Native build failed: $LASTEXITCODE"}
cmake -S "$Repo\tests\trials" -B "$Session\ledger-tests" -G Ninja 2>&1 | Tee-Object -Append $nativeLog
if($LASTEXITCODE -ne 0){throw 'Ledger configure failed'}
cmake --build "$Session\ledger-tests" 2>&1 | Tee-Object -Append $nativeLog
if($LASTEXITCODE -ne 0){throw 'Ledger build failed'}
ctest --test-dir "$Session\ledger-tests" --output-on-failure 2>&1 | Tee-Object -Append $nativeLog
if($LASTEXITCODE -ne 0){throw 'Ledger identities failed'}
Push-Location "$Repo\apps\trials"
try {
    dotnet build coordinator/RoR.Trials.csproj -c Release -p:RestoreLockedMode=true 2>&1 | Tee-Object "$Session\logs\coordinator-$stamp.log"
    if($LASTEXITCODE -ne 0){throw 'Coordinator build failed'}
    dotnet run --project '../../tests/trials/contracts-tests.csproj' -c Release -- "$Session\contract-tests-$stamp" 2>&1 | Tee-Object "$Session\logs\contracts-$stamp.log"
    if($LASTEXITCODE -ne 0){throw 'Contract checks failed'}
    Push-Location workbench
    try {
        npm.cmd ci --cache "$Session\npm-cache" 2>&1 | Tee-Object "$Session\logs\npm-$stamp.log"
        if($LASTEXITCODE -ne 0){throw 'Locked npm install failed'}
        npm.cmd run build 2>&1 | Tee-Object "$Session\logs\workbench-$stamp.log"
        if($LASTEXITCODE -ne 0){throw 'Workbench build failed'}
    } finally {Pop-Location}
} finally {Pop-Location}
[ordered]@{time=(Get-Date).ToString('o');exe="$Session\build\bin\RoR.exe";sha256=(Get-FileHash "$Session\build\bin\RoR.exe").Hash;sourceRecord="source-$stamp.json";clean=[bool]$Clean;nativeLog=$nativeLog;dependencyCache='Existing Conan cache; new native outputs';exitCode=0} |
    ConvertTo-Json | Set-Content "$Session\report\build-$stamp.json" -Encoding UTF8
Write-Output "Built $Session\build\bin\RoR.exe; start with tools/trials/start.ps1."
