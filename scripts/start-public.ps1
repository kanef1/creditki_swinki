$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$runtimePath = Join-Path $projectRoot '.runtime'
New-Item -ItemType Directory -Path $runtimePath -Force | Out-Null
$publicEnvPath = Join-Path $runtimePath 'public.env'
if (-not (Test-Path -LiteralPath $publicEnvPath)) {
    $generator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $keyBytes = New-Object byte[] 48
    $passwordBytes = New-Object byte[] 32
    $generator.GetBytes($keyBytes)
    $generator.GetBytes($passwordBytes)
    $publicLines = @(('DJANGO_SECRET_KEY=' + [Convert]::ToBase64String($keyBytes)), ('POSTGRES_PASSWORD=' + [Convert]::ToBase64String($passwordBytes)))
    $publicLines | Set-Content -LiteralPath $publicEnvPath -Encoding ASCII
    $generator.Dispose()
}
$composeArgs = @('compose','--env-file',$publicEnvPath,'-p','credit-public','-f','compose.public.yaml')
& docker @composeArgs up -d --wait db backend frontend
if ($LASTEXITCODE -ne 0) { throw 'Public demo startup failed' }
$sshPath = (Get-Command ssh -ErrorAction Stop).Source
$pidFile = Join-Path $runtimePath 'ssh-tunnel.pid'
$sshRunning = $null
if (Test-Path -LiteralPath $pidFile) {
    $sshRunning = Get-Process -Id ([int](Get-Content -Raw $pidFile)) -ErrorAction SilentlyContinue
    if ($sshRunning -and $sshRunning.Path -ne $sshPath) { throw 'Tracked tunnel PID belongs to another executable' }
}
if (-not $sshRunning) {
    $sshProcess = Start-Process -FilePath $sshPath -ArgumentList @('-F','none','-T','-o','IdentityFile=none','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=accept-new','-o','UserKnownHostsFile=.runtime/public-known-hosts','-o','ServerAliveInterval=20','-o','ExitOnForwardFailure=yes','-R','80:127.0.0.1:8081','nokey@localhost.run') -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimePath 'ssh-tunnel.stdout.log') -RedirectStandardError (Join-Path $runtimePath 'ssh-tunnel.stderr.log') -PassThru
    $sshProcess.Id | Set-Content -LiteralPath $pidFile -Encoding ASCII
}
$publicOrigin = $null
for ($attempt=0; $attempt -lt 30; $attempt++) {
    $tunnelLog = Get-Content -Raw -LiteralPath (Join-Path $runtimePath 'ssh-tunnel.stdout.log') -ErrorAction SilentlyContinue
    $urls = [regex]::Matches([string]$tunnelLog,'https://[a-z0-9-]+\.lhr\.life')
    if ($urls.Count -gt 0) { $publicOrigin=$urls[$urls.Count-1].Value; break }
    Start-Sleep -Seconds 1
}
if (-not $publicOrigin) { throw 'localhost.run did not return a public URL; inspect SSH tunnel logs' }
$existingLines = @(Get-Content -LiteralPath $publicEnvPath | Where-Object { $_ -notmatch '^PUBLIC_(ORIGIN|HOSTS)=' })
$existingLines += 'PUBLIC_ORIGIN=' + $publicOrigin
$existingLines += 'PUBLIC_HOSTS=localhost,127.0.0.1,backend,' + ([uri]$publicOrigin).Host
$existingLines | Set-Content -LiteralPath $publicEnvPath -Encoding ASCII
& docker @composeArgs up -d --wait backend
if ($LASTEXITCODE -ne 0) { throw 'Public origin configuration failed' }
& docker @composeArgs exec -T frontend nginx -s reload
if ($LASTEXITCODE -ne 0) { throw 'Frontend proxy reload failed' }
$publicOrigin | Set-Content -LiteralPath (Join-Path $runtimePath 'public-url.txt') -Encoding ASCII
Write-Output $publicOrigin
