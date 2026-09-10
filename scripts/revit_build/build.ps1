$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$references = @(Get-ChildItem 'C:/Program Files/dotnet/shared/Microsoft.NETCore.App/10.0.9' -Filter '*.dll' | ForEach-Object { try { [System.Reflection.AssemblyName]::GetAssemblyName($_.FullName) | Out-Null; $_.FullName } catch {} })
$references += @('C:/Program Files/Autodesk/Revit 2027/RevitAPI.dll','C:/Program Files/Autodesk/Revit 2027/RevitAPIUI.dll',(Join-Path $env:APPDATA 'Autodesk/Revit/Addins/2027/revit_mcp_plugin/Newtonsoft.Json.dll'))
$destination = Join-Path $root 'tmp/revit-compiler/EvolveBuildHelpersV2.dll'
$compilerArgs = @('/nologo','/target:library','/langversion:preview',('/out:"' + $destination + '"'))
$compilerArgs += $references | ForEach-Object { '/reference:"' + $_ + '"' }
$compilerArgs += Get-ChildItem $PSScriptRoot -Filter '*.cs' | ForEach-Object { '"' + $_.FullName + '"' }
$responseFile = Join-Path $root 'tmp/revit-compiler/build-helpers.rsp'
[System.IO.File]::WriteAllLines($responseFile, $compilerArgs)
& 'C:/Program Files/dotnet/dotnet.exe' --roll-forward LatestMajor (Join-Path $root 'tmp/revit-compiler/toolset/tasks/netcore/bincore/csc.dll') ('@' + $responseFile)
if ($LASTEXITCODE -ne 0) { throw 'Helper compilation failed' }
Write-Output $destination
