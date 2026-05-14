$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$serverJson = @{
    type = "stdio"
    command = $python
    args = @("-m", "oscar_db_mcp.server")
    cwd = $repoRoot
} | ConvertTo-Json -Compress

Write-Host "Run this command to add the MCP server to Claude Code:"
Write-Host ""
Write-Host "claude mcp add-json oscar-db '$serverJson'"
Write-Host ""
Write-Host "If Claude Code is not on PATH, copy this server JSON into your Claude MCP config."
