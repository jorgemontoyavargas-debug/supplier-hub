param([string]$Version = "0.1.0-rc.1")

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

if (git status --porcelain) {
    throw "El repositorio debe estar limpio antes de generar un paquete."
}

powershell -ExecutionPolicy Bypass -File .\scripts\verify.ps1
$OutputDirectory = Join-Path $ProjectRoot "dist"
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$Archive = Join-Path $OutputDirectory "supplier-hub-$Version.zip"
git archive --format=zip --prefix="supplier-hub-$Version/" --output=$Archive HEAD
Get-FileHash $Archive -Algorithm SHA256 |
    Format-List | Out-String | Set-Content "$Archive.sha256.txt"
Write-Host "Paquete creado: $Archive"

