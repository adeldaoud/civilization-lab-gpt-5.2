param(
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

python -m civlab.cli refresh-dashboard --root .
python -m civlab.cli serve-dashboard --root . --port $Port
