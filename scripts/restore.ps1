param(
    [Parameter(Mandatory = $true)][string]$BackupDirectory,
    [switch]$ConfirmRestore
)

$ErrorActionPreference = "Stop"
if (-not $ConfirmRestore) {
    throw "La restauración reemplaza la base y los archivos actuales. Repite con -ConfirmRestore."
}
$ProjectRoot = (Resolve-Path (Split-Path -Parent $PSScriptRoot)).Path
$ResolvedBackup = (Resolve-Path $BackupDirectory).Path
$AllowedBackupRoot = Join-Path $ProjectRoot "backups"
if (-not $ResolvedBackup.StartsWith($AllowedBackupRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "La copia debe estar dentro de $AllowedBackupRoot"
}
$DatabaseBackup = Join-Path $ResolvedBackup "database.dump"
$MediaBackup = Join-Path $ResolvedBackup "media.tar.gz"
if (-not (Test-Path $DatabaseBackup) -or -not (Test-Path $MediaBackup)) {
    throw "La copia no contiene database.dump y media.tar.gz."
}

Set-Location $ProjectRoot
docker compose stop web
try {
    docker compose cp $DatabaseBackup db:/tmp/supplier-hub-restore.dump
    docker compose exec -T db dropdb -U supplier_hub --if-exists supplier_hub
    docker compose exec -T db createdb -U supplier_hub supplier_hub
    docker compose exec -T db pg_restore -U supplier_hub -d supplier_hub --clean --if-exists /tmp/supplier-hub-restore.dump
    docker compose start web
    docker compose cp $MediaBackup web:/tmp/supplier-hub-media-restore.tar.gz
    docker compose exec -T web tar -xzf /tmp/supplier-hub-media-restore.tar.gz -C /app
} finally {
    docker compose start web
}
Write-Host "Restauración completada. Ejecuta scripts/verify-deployment.ps1."

