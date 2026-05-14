$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$manifest = Join-Path $repoRoot ".codex-plugin\plugin.json"
$mcpConfig = Join-Path $repoRoot ".mcp.json"

if (-not (Test-Path $manifest)) {
    throw "Missing Codex plugin manifest: $manifest"
}

if (-not (Test-Path $mcpConfig)) {
    throw "Missing MCP config: $mcpConfig"
}

Write-Host "Codex plugin root:"
Write-Host $repoRoot
Write-Host ""
Write-Host "Manifest:"
Write-Host $manifest
Write-Host ""
Write-Host "MCP config:"
Write-Host $mcpConfig
Write-Host ""
Write-Host "Add this local plugin path in Codex:"
Write-Host $repoRoot
