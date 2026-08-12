param([string]$OutputDirectory = ".\backups")

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$Target = Join-Path $OutputDirectory $Timestamp
New-Item -ItemType Directory -Force -Path $Target | Out-Null

docker compose exec -T db pg_dump -U supplier_hub -d supplier_hub -Fc -f /tmp/supplier-hub.dump
docker compose cp db:/tmp/supplier-hub.dump (Join-Path $Target "database.dump")
docker compose exec -T web tar -czf /tmp/supplier-hub-media.tar.gz -C /app media
docker compose cp web:/tmp/supplier-hub-media.tar.gz (Join-Path $Target "media.tar.gz")

Get-FileHash (Join-Path $Target "database.dump"), (Join-Path $Target "media.tar.gz") |
    Format-Table -AutoSize | Out-String | Set-Content (Join-Path $Target "SHA256SUMS.txt")

Write-Host "Copia creada en $Target"

