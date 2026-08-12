$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$PythonExecutable = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $PythonExecutable)) {
    throw "Falta .venv. Ejecuta primero .\scripts\setup.ps1."
}

& $PythonExecutable manage.py check
& $PythonExecutable manage.py makemigrations --check --dry-run
& $PythonExecutable manage.py test
& $PythonExecutable manage.py evaluate_local_ai
& $PythonExecutable -m compileall -q accounts config core organizations qualifications suppliers

$env:SUPPLIER_HUB_DEBUG = "false"
$env:SUPPLIER_HUB_SECRET_KEY = "verify-only-secret-key-with-more-than-fifty-characters-1234567890"
$env:SUPPLIER_HUB_ALLOWED_HOSTS = "localhost,127.0.0.1,testserver"
$env:SUPPLIER_HUB_HSTS_PRELOAD = "true"
& $PythonExecutable manage.py check --deploy --fail-level WARNING

Write-Host "Verificación completada."
