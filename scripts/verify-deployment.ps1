$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

docker compose config --quiet
docker compose up -d --build
$Healthy = $false
for ($Attempt = 0; $Attempt -lt 60; $Attempt++) {
    try {
        $Health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/salud/" -TimeoutSec 3
        if ($Health.status -eq "ok" -and $Health.database -eq "ok") {
            $Healthy = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 2
    }
}
if (-not $Healthy) {
    docker compose ps
    docker compose logs --tail 100 web db
    throw "El despliegue no alcanzó estado saludable."
}
docker compose exec -T web python manage.py check
Write-Host "Despliegue verificado."
