param(
    [string]$PythonPath,
    [string]$EnvFile
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$python = if ($PythonPath) { $PythonPath } else { Join-Path $repoRoot ".venv\Scripts\python.exe" }
$envFile = if ($EnvFile) { $EnvFile } else { Join-Path $repoRoot ".env" }
$cursorDir = Join-Path $HOME ".cursor"
$cursorMcp = Join-Path $cursorDir "mcp.json"

if (-not (Test-Path $python)) {
    throw "Missing virtual environment Python: $python. Run the project installation steps first."
}

if (-not (Test-Path $envFile)) {
    throw "Missing .env file: $envFile. Run .\scripts\configure_oscar_mcp.ps1 first."
}

New-Item -ItemType Directory -Force -Path $cursorDir | Out-Null

if (Test-Path $cursorMcp) {
    $raw = Get-Content -LiteralPath $cursorMcp -Raw
    if ([string]::IsNullOrWhiteSpace($raw)) {
        $config = [ordered]@{ mcpServers = [ordered]@{} }
    } else {
        $config = $raw | ConvertFrom-Json -AsHashtable
    }
} else {
    $config = [ordered]@{ mcpServers = [ordered]@{} }
}

if (-not $config.ContainsKey("mcpServers") -or $null -eq $config["mcpServers"]) {
    $config["mcpServers"] = [ordered]@{}
}

$config["mcpServers"]["oscar-emr-mcp"] = [ordered]@{
    type = "stdio"
    command = $python
    args = @("-m", "oscar_db_mcp.server")
    envFile = $envFile
}

$config | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $cursorMcp -Encoding UTF8

Write-Host "Installed Oscar EMR MCP in Cursor global MCP config:"
Write-Host $cursorMcp
Write-Host ""
Write-Host "Restart Cursor or reload MCP servers from Cursor Settings > MCP."
