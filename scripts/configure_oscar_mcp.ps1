param(
    [switch]$SkipInstall,
    [switch]$UserGlobal
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Host "Creating virtual environment..."
    py -3 -m venv (Join-Path $repoRoot ".venv")
}

if (-not $SkipInstall) {
    Write-Host "Installing OSCAR DB MCP server..."
    & $python -m pip install -e "$repoRoot[dev]"
}

Write-Host ""
Write-Host "Starting interactive connection setup..."
if ($UserGlobal) {
    $globalEnv = Join-Path $HOME ".oscaremr-mcp\.env"
    & $python -m oscar_db_mcp.configure --interactive --env-path $globalEnv
} else {
    & $python -m oscar_db_mcp.configure --interactive
}
