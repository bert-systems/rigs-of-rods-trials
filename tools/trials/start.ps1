param(
    [Parameter(Mandatory=$true)][string]$Session,
    [string]$Repo=(Resolve-Path "$PSScriptRoot\..\..").Path,
    [int]$Port=54321
)
$ErrorActionPreference='Stop'
$Session=[IO.Path]::GetFullPath($Session)
$stamp=Get-Date -Format 'yyyyMMdd-HHmmss-ffff'
if(!(Test-Path "$Session\build\bin\RoR.exe") -or !(Test-Path "$Repo\apps\trials\workbench\dist\index.html")){throw 'Run build.ps1 first.'}
if(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue){throw "Port $Port already in use. Stop that coordinator explicitly."}
New-Item -ItemType Directory -Force -Path "$Session\logs","$Session\report" | Out-Null
$trialArgs=@('--game-bin',('"'+$Session+'\build\bin"'),'--archive',('"'+$Session+'\archive"'),'--repo',('"'+$Repo+'"'),'--web-root',('"'+$Repo+'\apps\trials\workbench\dist"'),'--port',"$Port")
$p=Start-Process -FilePath "$Repo\apps\trials\coordinator\bin\Release\net10.0\RoR.Trials.exe" -ArgumentList $trialArgs -WorkingDirectory "$Repo\apps\trials" -WindowStyle Hidden -RedirectStandardOutput "$Session\logs\coordinator-$stamp.log" -RedirectStandardError "$Session\logs\coordinator-errors-$stamp.log" -PassThru
$p.Id | Set-Content "$Session\report\coordinator-pid.txt"
Write-Output "Coordinator PID $($p.Id). Workbench http://127.0.0.1:$Port/"
