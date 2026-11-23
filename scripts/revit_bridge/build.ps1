$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$revitDir = 'C:/Program Files/Autodesk/Revit 2027'
$pluginDir = Join-Path $env:APPDATA 'Autodesk/Revit/Addins/2027/revit_mcp_plugin'
$commandDir = Join-Path $pluginDir 'Commands/RevitMCPCommandSet/2027'
$destination = Join-Path $root 'tmp/revit-compiler/EvolveRevitCodeCommand.dll'
$references = @(Get-ChildItem 'C:/Program Files/dotnet/shared/Microsoft.NETCore.App/10.0.9' -Filter '*.dll' | ForEach-Object { try { [System.Reflection.AssemblyName]::GetAssemblyName($_.FullName) | Out-Null; $_.FullName } catch {} })
$references += @((Join-Path $revitDir 'RevitAPI.dll'), (Join-Path $revitDir 'RevitAPIUI.dll'), (Join-Path $pluginDir 'RevitMCPSDK.dll'), (Join-Path $pluginDir 'Newtonsoft.Json.dll'), (Join-Path $commandDir 'Microsoft.CodeAnalysis.dll'), (Join-Path $commandDir 'Microsoft.CodeAnalysis.CSharp.dll'))
$compilerArgs = @('/nologo','/target:library','/langversion:preview',('/out:"' + $destination + '"'))
$compilerArgs += $references | ForEach-Object { '/reference:"' + $_ + '"' }
$compilerArgs += Get-ChildItem $PSScriptRoot -Filter '*.cs' | ForEach-Object { '"' + $_.FullName + '"' }
$responseFile = Join-Path $root 'tmp/revit-compiler/build.rsp'
[System.IO.File]::WriteAllLines($responseFile, $compilerArgs)
& 'C:/Program Files/dotnet/dotnet.exe' --roll-forward LatestMajor (Join-Path $root 'tmp/revit-compiler/toolset/tasks/netcore/bincore/csc.dll') ('@' + $responseFile)
if ($LASTEXITCODE -ne 0) { throw 'Revit command compilation failed' }
Write-Output $destination
