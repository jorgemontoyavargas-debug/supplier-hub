param(
    [string]$PythonExecutable = ""
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

if (-not $PythonExecutable) {
    $PythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($PythonCommand) {
        $PythonExecutable = $PythonCommand.Source
    } else {
        $PyCommand = Get-Command py -ErrorAction SilentlyContinue
        if ($PyCommand) {
            $PythonExecutable = $PyCommand.Source
        } else {
            throw "No se encontró Python. Instala Python 3.12+ o usa -PythonExecutable."
        }
    }
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    & $PythonExecutable -m venv .venv
}

& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe manage.py migrate --noinput
& .\.venv\Scripts\python.exe manage.py seed_demo

Write-Host "Supplier Hub está preparado."
Write-Host "Ejecuta: .\.venv\Scripts\python.exe manage.py runserver"

