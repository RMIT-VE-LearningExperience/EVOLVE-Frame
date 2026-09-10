param([switch]$CheckOnly)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$old = 'C:\Users\Stormtrooper\Git\EVOLVE - Frame'
$files = @(Get-ChildItem -LiteralPath (Join-Path $root 'scripts') -Recurse -File | Where-Object Extension -in '.cs','.ps1','.py','.mjs')
$files += @(Get-ChildItem -LiteralPath (Join-Path $root 'output/revit') -File -Filter '*manifest.json')
$changed = @()
foreach ($file in $files) {
    $text = [IO.File]::ReadAllText($file.FullName)
    $updated = $text.Replace($old, $root).Replace($old.Replace('\','/'), $root.Replace('\','/'))
    # JSON stores each backslash twice; replace that representation too.
    if ($file.Extension -eq '.json') { $updated = $updated.Replace($old.Replace('\','\\'), $root.Replace('\','\\')) }
    if ($updated -ne $text) {
        $changed += $file.FullName
        if (!$CheckOnly) { [IO.File]::WriteAllText($file.FullName, $updated, [Text.UTF8Encoding]::new($false)) }
    }
}
Write-Output "$($changed.Count) files contain paths to update for $root"
$changed | Write-Output
if (!$CheckOnly) {
    Write-Output 'Source paths updated. Existing DLLs and in-model PDF links were NOT rewritten. Rebuild helper assemblies with a new assembly name and relink PDFs as described in TRANSFER_HANDOFF.md.'
}
