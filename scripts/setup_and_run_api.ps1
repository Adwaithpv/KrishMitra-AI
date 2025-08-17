param(
  [string]$PythonExe = ""
)

$ErrorActionPreference = "Stop"

function Resolve-PythonExe {
  $candidates = @("python", "py -3", "py")
  foreach ($c in $candidates) {
    $cmd = $c.Split(" ")[0]
    try {
      $null = Get-Command $cmd -ErrorAction Stop
      return $c
    } catch { }
  }
  throw "Python was not found on PATH. Please install Python 3.10+ and retry."
}

if ([string]::IsNullOrWhiteSpace($PythonExe)) {
  $PythonExe = Resolve-PythonExe
}

Write-Host "Using Python: $PythonExe"
Write-Host "Setting up virtual environment for API..."
Set-Location "$PSScriptRoot/../services/api"

& $PythonExe -m venv .venv
& .venv/Scripts/python -m pip install --upgrade pip
& .venv/Scripts/python -m pip install -r requirements.txt

Write-Host "Starting API on http://127.0.0.1:8000 ..."
& .venv/Scripts/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

