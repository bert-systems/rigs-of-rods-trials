param(
    [Parameter(Mandatory=$true)][string]$Session,
    [string]$Repo="",
    [string]$Archive="",
    [int]$Port=54321,
    [ValidateSet("Direct3D9","OpenGL")][string]$Renderer="Direct3D9",
    [switch]$EvidenceFrames
)
$ErrorActionPreference='Stop'
if(!$Repo){$Repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))}
$Session=[IO.Path]::GetFullPath($Session)
if(!$Archive){$Archive=Join-Path $Session 'archive'}
$Archive=[IO.Path]::GetFullPath($Archive)
$stamp=Get-Date -Format 'yyyyMMdd-HHmmss-ffff'
if(!(Test-Path "$Session\build\bin\RoR.exe") -or !(Test-Path "$Repo\apps\trials\workbench\dist\index.html")){throw 'Run build.ps1 first.'}
if(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue){throw "Port $Port already in use. Stop that coordinator explicitly."}
New-Item -ItemType Directory -Force -Path "$Session\logs","$Session\report" | Out-Null
$trialArgs=@('--game-bin',('"'+$Session+'\build\bin"'),'--archive',('"'+$Archive+'"'),'--repo',('"'+$Repo+'"'),'--web-root',('"'+$Repo+'\apps\trials\workbench\dist"'),'--port',"$Port",'--renderer',$Renderer,'--evidence-frames',([bool]$EvidenceFrames).ToString())
$p=Start-Process -FilePath "$Repo\apps\trials\coordinator\bin\Release\net10.0\RoR.Trials.exe" -ArgumentList $trialArgs -WorkingDirectory "$Repo\apps\trials" -WindowStyle Hidden -RedirectStandardOutput "$Session\logs\coordinator-$stamp.log" -RedirectStandardError "$Session\logs\coordinator-errors-$stamp.log" -PassThru
$p.Id | Set-Content "$Session\report\coordinator-pid.txt"
Write-Output "Coordinator PID $($p.Id). Workbench http://127.0.0.1:$Port/"
