param([switch]$CheckOnly)
$ErrorActionPreference = 'Stop'
$payload = Join-Path $PSScriptRoot 'payload'
$root = Split-Path $PSScriptRoot -Parent
$manifest = Get-Content -LiteralPath (Join-Path $payload 'SHA256.json') -Raw | ConvertFrom-Json
foreach ($item in $manifest) {
    $file = Join-Path $payload $item.file
    if ((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash -ne $item.sha256) {
        throw "Archive checksum mismatch: $file"
    }
}
$revit = 'C:/Program Files/Autodesk/Revit 2027/Revit.exe'
if (!(Test-Path -LiteralPath $revit)) { throw 'Install Revit 2027.2 on this PC before restoring the add-in.' }
if ($CheckOnly) { Write-Output 'Archive checksums and Revit installation checked. No files changed.'; return }
if (Get-Process Revit -ErrorAction SilentlyContinue) { throw 'Close Revit before restoring its add-in, then run this script again.' }
$runtime = Join-Path $env:LOCALAPPDATA 'RevitMCP'
$addins = Join-Path $env:APPDATA 'Autodesk/Revit/Addins/2027'
$compiler = Join-Path $root 'tmp/revit-compiler'
foreach ($target in @($runtime, (Join-Path $addins 'revit_mcp_plugin'), (Join-Path $addins 'mcp-servers-for-revit.addin'), $compiler)) {
    if (Test-Path -LiteralPath $target) { throw "Existing installation found at $target. Inspect it before merging; this restore will not overwrite it." }
}
New-Item -ItemType Directory -Path $runtime, $addins, $compiler -Force | Out-Null
Expand-Archive -LiteralPath (Join-Path $payload 'revit-mcp-runtime.zip') -DestinationPath $runtime
Expand-Archive -LiteralPath (Join-Path $payload 'revit-addin-2027.zip') -DestinationPath $addins
Expand-Archive -LiteralPath (Join-Path $payload 'revit-compiler.zip') -DestinationPath $compiler
$node = (Join-Path $runtime 'node-v22.23.2-win-x64/node.exe').Replace('\','/')
$server = (Join-Path $runtime 'node_modules/mcp-server-for-revit/build/index.js').Replace('\','/')
$config = "[mcp_servers.revit]`ncommand = `"$node`"`nargs = [`"$server`"]`n"
Set-Content -LiteralPath (Join-Path $PSScriptRoot 'mcp-config.local.toml') -Value $config -Encoding UTF8
Write-Output 'Connection files restored. Open the RVT in Revit and enable Add-Ins > Revit MCP Switch.'
Write-Output 'mcp-config.local.toml contains this PC''s server paths for merging into the assistant configuration. Existing user settings were not changed.'
Write-Output 'Run the read-only check shown in TRANSFER_HANDOFF.md before any modelling commands.'
