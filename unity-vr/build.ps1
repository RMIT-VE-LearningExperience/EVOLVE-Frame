param(
    [string]$UnityEditor = 'C:/Program Files/Unity/Hub/Editor/6000.6.9f1/Editor/Unity.exe',
    [ValidateSet('Prepare', 'Preview', 'Bake', 'Reflections', 'Test', 'Android', 'QuestProfile', 'Quest', 'Pico4Profile', 'Pico4')]
    [string]$Step = 'Android'
)

$ErrorActionPreference = 'Stop'
$projectDirectory = $PSScriptRoot
$logDirectory = Join-Path $projectDirectory 'Logs'
New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
$method = @{
    Prepare = 'FrameLabBuild.Prepare'
    Preview = 'FrameLabGeometryReview.Run'
    Bake = 'FrameLabLighting.Bake'
    Reflections = 'FrameLabLighting.RefreshReflections'
    Test = 'FrameLabSmokeTest.Run'
    Android = 'FrameLabBuild.BuildAndroid'
    QuestProfile = 'FrameLabQuestBuild.ValidateProfile'
    Quest = 'FrameLabQuestBuild.BuildAndroid'
    Pico4Profile = 'FrameLabPico4Build.ValidateProfile'
    Pico4 = 'FrameLabPico4Build.BuildAndroid'
}[$Step]
$unityArguments = @(
    '-batchmode',
    '-projectPath', "`"$projectDirectory`"",
    '-executeMethod', $method,
    '-logFile', "`"$(Join-Path $logDirectory ($Step + '.log'))`""
)
if ($Step -notin @('Test','Preview')) { $unityArguments += '-quit' }
if ($Step -in @('Android', 'Quest', 'QuestProfile', 'Pico4', 'Pico4Profile')) { $unityArguments += @('-buildTarget', 'Android') }
$profileFiles = @{}
if ($Step -in @('Pico4', 'Pico4Profile')) {
    # Unity can terminate a batch build before C# finally runs. Restore on process exit too.
    foreach ($relativePath in @('ProjectSettings/ProjectSettings.asset',
        'Assets/XR/Settings/OpenXR Package Settings.asset', 'Assets/Resources/PICOProjectSetting.asset',
        'Assets/Settings/UniversalRenderPipelineGlobalSettings.asset')) {
        $absolutePath = Join-Path $projectDirectory $relativePath
        $profileFiles[$absolutePath] = [IO.File]::ReadAllBytes($absolutePath)
    }
}
try {
    $process = Start-Process -FilePath $UnityEditor -ArgumentList $unityArguments -WindowStyle Hidden -PassThru -Wait
}
finally {
    foreach ($entry in $profileFiles.GetEnumerator()) {
        [IO.File]::WriteAllBytes($entry.Key, $entry.Value)
    }
}
if ($process.ExitCode -ne 0) {
    throw "Unity $Step failed. See the log in $logDirectory."
}
Write-Output "Unity $Step completed."
