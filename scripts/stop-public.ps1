$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$pidFile = Join-Path $projectRoot '.runtime/ssh-tunnel.pid'
if (Test-Path -LiteralPath $pidFile) {
    $tunnelProcess = Get-Process -Id ([int](Get-Content -Raw $pidFile)) -ErrorAction SilentlyContinue
    if ($tunnelProcess) {
        $sshPath = (Get-Command ssh -ErrorAction Stop).Source
        if ($tunnelProcess.Path -ne $sshPath) { throw 'Tracked PID belongs to another executable; refusing to stop it' }
        Stop-Process -Id $tunnelProcess.Id
    }
}
Write-Output 'Public SSH tunnel stopped. Docker data and local project remain available.'
