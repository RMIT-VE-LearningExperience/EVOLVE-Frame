param(
    [string]$UnityEditor = 'C:/Program Files/Unity/Hub/Editor/6000.6.9f1/Editor/Unity.exe',
    [ValidateSet('Prepare', 'Preview', 'Bake', 'Reflections', 'Test', 'Android', 'QuestProfile', 'Quest')]
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
}[$Step]
$unityArguments = @(
    '-batchmode',
    '-projectPath', "`"$projectDirectory`"",
    '-executeMethod', $method,
    '-logFile', "`"$(Join-Path $logDirectory ($Step + '.log'))`""
)
if ($Step -notin @('Test','Preview')) { $unityArguments += '-quit' }
if ($Step -in @('Android', 'Quest', 'QuestProfile')) { $unityArguments += @('-buildTarget', 'Android') }
$process = Start-Process -FilePath $UnityEditor -ArgumentList $unityArguments -WindowStyle Hidden -PassThru -Wait
if ($process.ExitCode -ne 0) {
    throw "Unity $Step failed. See the log in $logDirectory."
}
Write-Output "Unity $Step completed."
