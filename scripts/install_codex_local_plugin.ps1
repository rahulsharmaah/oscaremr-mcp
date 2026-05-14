param(
    [string]$MarketplaceName = "oscar-db-mcp-local",
    [string]$PythonPath,
    [string]$ServerCwd
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
$marketplaceRoot = Join-Path $codexHome "local-marketplaces\$MarketplaceName"
$pluginRoot = Join-Path $marketplaceRoot "plugins\oscar-db-mcp"
$agentsPlugins = Join-Path $marketplaceRoot ".agents\plugins"
$venvPython = if ($PythonPath) { $PythonPath } else { Join-Path $repoRoot ".venv\Scripts\python.exe" }
$serverCwd = if ($ServerCwd) { $ServerCwd } else { $repoRoot }

if (-not (Test-Path $venvPython)) {
    throw "Python virtual environment was not found. Run: python -m venv .venv; .\.venv\Scripts\python.exe -m pip install -e `".[dev]`""
}

if (Test-Path $pluginRoot) {
    $existingPluginRoot = Get-Item -LiteralPath $pluginRoot -Force
    if ($existingPluginRoot.LinkType) {
        Remove-Item -LiteralPath $pluginRoot -Force
    } else {
        $resolvedPluginRoot = $existingPluginRoot.FullName
        $resolvedMarketplaceRoot = (Resolve-Path $marketplaceRoot).Path
        if (-not $resolvedPluginRoot.StartsWith($resolvedMarketplaceRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to replace plugin package outside the Codex local marketplace."
        }
        Remove-Item -LiteralPath $pluginRoot -Recurse -Force
    }
}

New-Item -ItemType Directory -Force -Path $pluginRoot, $agentsPlugins | Out-Null

$copyItems = @(
    ".codex-plugin",
    "assets",
    "skills"
)

foreach ($item in $copyItems) {
    $source = Join-Path $repoRoot $item
    $target = Join-Path $pluginRoot $item
    if (Test-Path $target) {
        Remove-Item -LiteralPath $target -Recurse -Force
    }
    Copy-Item -LiteralPath $source -Destination $target -Recurse -Force
}

$mcpConfig = @{
    mcpServers = @{
        "oscar-db" = @{
            command = $venvPython
            args = @("-m", "oscar_db_mcp.server")
            cwd = $serverCwd
        }
    }
}
$mcpConfig | ConvertTo-Json -Depth 6 | Set-Content -Path (Join-Path $pluginRoot ".mcp.json") -Encoding UTF8

$marketplace = @{
    name = "local"
    interface = @{
        displayName = "Local Plugins"
    }
    plugins = @(
        @{
            name = "oscar-db-mcp"
            source = @{
                source = "local"
                path = "./plugins/oscar-db-mcp"
            }
            policy = @{
                installation = "AVAILABLE"
                authentication = "ON_INSTALL"
            }
            category = "Developer Tools"
        }
    )
}
$marketplace | ConvertTo-Json -Depth 8 | Set-Content -Path (Join-Path $agentsPlugins "marketplace.json") -Encoding UTF8

Write-Host "Codex local marketplace ready:"
Write-Host $marketplaceRoot
Write-Host ""
Write-Host "If Codex is open, restart it or refresh the Plugins page, then install Oscar EMR MCP from Local Plugins."
