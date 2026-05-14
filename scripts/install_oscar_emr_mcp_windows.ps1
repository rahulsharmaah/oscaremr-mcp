param(
    [switch]$SkipDatabaseWizard,
    [switch]$SkipCodex,
    [switch]$SkipCursor
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$installRoot = Join-Path $env:LOCALAPPDATA "OscarEmrMcp"
$python = Join-Path $installRoot ".venv\Scripts\python.exe"
$envFile = Join-Path $HOME ".oscaremr-mcp\.env"

Write-Host "Oscar EMR MCP setup"
Write-Host "===================="
Write-Host ""

New-Item -ItemType Directory -Force -Path $installRoot | Out-Null

if (-not (Test-Path $python)) {
    if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
        throw "Python 3 was not found. Install Python 3.11 or newer from python.org, then run this installer again."
    }

    Write-Host "Creating Python virtual environment..."
    py -3 -m venv (Join-Path $installRoot ".venv")
}

Write-Host "Installing Oscar EMR MCP dependencies..."
& $python -m pip install --upgrade pip
& $python -m pip install "$repoRoot"

if (-not $SkipDatabaseWizard) {
    Write-Host ""
    Write-Host "Configuring OSCAR EMR database connection..."
    & $python -m oscar_db_mcp.configure --interactive --env-path $envFile
} elseif (-not (Test-Path $envFile)) {
    Write-Warning "Database wizard skipped and no user env file exists yet. Run oscar-db-mcp-configure --interactive --env-path `"$envFile`" before using the MCP server."
}

if (-not $SkipCodex) {
    Write-Host ""
    Write-Host "Preparing Codex local plugin marketplace..."
    & (Join-Path $repoRoot "scripts\install_codex_local_plugin.ps1") -PythonPath $python -ServerCwd $installRoot
}

if (-not $SkipCursor) {
    if (Test-Path $envFile) {
        Write-Host ""
        Write-Host "Installing Cursor MCP configuration..."
        & (Join-Path $repoRoot "scripts\install_cursor_mcp.ps1") -PythonPath $python -EnvFile $envFile
    } else {
        Write-Warning "Skipping Cursor registration because .env is missing."
    }
}

Write-Host ""
Write-Host "Setup complete."
Write-Host ""
Write-Host "Next steps:"
Write-Host "- Restart Codex, open Plugins, and install Oscar EMR MCP from Local Plugins."
Write-Host "- Restart Cursor or reload MCP servers from Cursor Settings > MCP."
Write-Host "- To verify the MCP stream, run scripts\test_oscar_mcp_stream.ps1."
