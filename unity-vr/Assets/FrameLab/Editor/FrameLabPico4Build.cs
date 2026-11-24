using System;
using System.IO;
using System.Linq;
using System.Xml;
using FrameLab;
using UnityEditor;
using UnityEditor.Android;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.XR.OpenXR.Features;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.XR.OpenXR;
using UnityEngine.XR.OpenXR.Features.Interactions;

// Target the original PICO 4 Enterprise without regenerating the baked scene.
public static class FrameLabPico4Build
{
    internal static bool IsBuilding { get; private set; }
    const string Scene = "Assets/FrameLab/Scenes/Leichhardt.unity";
    const string Output = "Builds/Android/Leichhardt-PICO4-Enterprise.apk";
    const string Evidence = "Builds/Android/PICO4-Enterprise-profile.json";

    [Serializable] class ProfileEvidence
    {
        public string version, result, scene, apk;
        public string device = "PICO 4 Enterprise (original, not Ultra)";
        public string targetPicoOS = "5.9.9";
        public string loader = "Unity/Khronos standard OpenXR Android loader (PICO OS 5.9.0+)";
        public string physicalDeviceValidation = "NOT TESTED: no original PICO 4 Enterprise connected.";
        public int versionCode, requestedRefreshHz = 72, msaa;
        public float renderScale;
        public string[] enabledFeatures, excludedPicoPlugins;
        public bool restoredOriginalSettings;
    }

    [MenuItem("Frame Lab/Build original PICO 4 Enterprise APK")]
    public static void BuildAndroid() => WithProfile(true);

    [MenuItem("Frame Lab/Validate original PICO 4 Enterprise profile")]
    public static void ValidateProfile() => WithProfile(false);

    static void WithProfile(bool build)
    {
        if (!File.Exists(Scene)) throw new BuildFailedException("Prepare and bake Leichhardt first.");
        FeatureHelpers.RefreshFeatures(BuildTargetGroup.Android);
        var xr = OpenXRSettings.GetSettingsForBuildTargetGroup(BuildTargetGroup.Android);
        if (xr == null) throw new BuildFailedException("Missing Android OpenXR settings.");
        var features = xr.GetFeatures().Where(f => f != null).ToArray();
        // Asset objects can be unloaded during BuildPlayer; restore saved files, not stale references.
        string[] settingsPaths = { AssetDatabase.GetAssetPath(xr), "ProjectSettings/ProjectSettings.asset" };
        var before = settingsPaths.ToDictionary(path => path, File.ReadAllBytes);
        var report = new ProfileEvidence { version = FrameLabBuild.AppVersion,
            versionCode = FrameLabBuild.AppVersionCode, result = "IN_PROGRESS", scene = Scene,
            apk = build ? Output : null };
        Directory.CreateDirectory("Builds/Android");
        try
        {
            foreach (var feature in features)
            {
                feature.enabled = feature is LeichhardtPico4Support || feature is PICO4ControllerProfile;
                EditorUtility.SetDirty(feature);
            }
            if (xr.GetFeature<LeichhardtPico4Support>() == null || xr.GetFeature<PICO4ControllerProfile>() == null)
                throw new BuildFailedException("Missing original PICO 4 controller or standard OpenXR support.");
            xr.renderMode = OpenXRSettings.RenderMode.SinglePassInstanced;
            PlayerSettings.Android.applicationEntry = AndroidApplicationEntry.Activity;
            if (PlayerSettings.Android.targetArchitectures != AndroidArchitecture.ARM64 ||
                PlayerSettings.GetScriptingBackend(NamedBuildTarget.Android) != ScriptingImplementation.IL2CPP ||
                !PlayerSettings.GetGraphicsAPIs(BuildTarget.Android).SequenceEqual(new[] { GraphicsDeviceType.Vulkan }))
                throw new BuildFailedException("Expected the existing ARM64 IL2CPP/Vulkan mobile settings.");
            if (PlayerSettings.bundleVersion != FrameLabBuild.AppVersion ||
                PlayerSettings.Android.bundleVersionCode != FrameLabBuild.AppVersionCode)
                throw new BuildFailedException("Project and prepared scene version differ.");
            var pipeline = GraphicsSettings.defaultRenderPipeline as UniversalRenderPipelineAsset;
            if (pipeline == null) throw new BuildFailedException("Mobile URP pipeline is missing.");
            report.msaa = pipeline.msaaSampleCount;
            report.renderScale = pipeline.renderScale;
            report.enabledFeatures = features.Where(f => f.enabled).Select(f => f.GetType().Name).ToArray();
            if (report.enabledFeatures.Length != 2) throw new BuildFailedException("Unexpected PICO 4 feature set.");
            report.excludedPicoPlugins = FrameLabQuestBuild.PicoPlugins().Select(p => p.assetPath).ToArray();
            EditorUtility.SetDirty(xr);
            AssetDatabase.SaveAssets();
            Debug.Log("LEICHHARDT_PICO4_PROFILE " + JsonUtility.ToJson(report));
            if (build)
            {
                IsBuilding = true;
                var result = BuildPipeline.BuildPlayer(new BuildPlayerOptions {
                    scenes = new[] { Scene }, locationPathName = Output, target = BuildTarget.Android,
                    options = BuildOptions.Development,
                    extraScriptingDefines = new[] { "LEICHHARDT_PICO4_ENTERPRISE" }
                });
                if (result.summary.result != BuildResult.Succeeded)
                    throw new BuildFailedException("PICO 4 Enterprise APK failed: " + result.summary.totalErrors + " errors.");
            }
            report.result = "PASS";
        }
        finally
        {
            IsBuilding = false;
            foreach (var importer in FrameLabQuestBuild.PicoPlugins()) importer.SetIncludeInBuildDelegate(null);
            foreach (var pair in before)
            {
                File.WriteAllBytes(pair.Key, pair.Value);
                AssetDatabase.ImportAsset(pair.Key, ImportAssetOptions.ForceUpdate);
            }
            report.restoredOriginalSettings = before.All(p => File.ReadAllBytes(p.Key).SequenceEqual(p.Value));
            File.WriteAllText(Evidence, JsonUtility.ToJson(report, true));
            if (!report.restoredOriginalSettings) throw new BuildFailedException("Failed to restore original XR settings.");
        }
        Debug.Log(build ? "LEICHHARDT_PICO4_APK_SUCCESS" : "LEICHHARDT_PICO4_PROFILE_PASS");
    }
}

public sealed class FrameLabPico4NativePlugins : IPreprocessBuildWithReport, IPostGenerateGradleAndroidProject
{
    public int callbackOrder => 10000;
    public void OnPreprocessBuild(BuildReport report)
    {
        if (!FrameLabPico4Build.IsBuilding) return;
        foreach (var importer in FrameLabQuestBuild.PicoPlugins()) importer.SetIncludeInBuildDelegate(path => false);
    }

    public void OnPostGenerateGradleAndroidProject(string path)
    {
        if (!FrameLabPico4Build.IsBuilding) return;
        string manifest = Path.Combine(path, "src/main/AndroidManifest.xml");
        var xml = new XmlDocument();
        xml.Load(manifest);
        var app = xml.SelectSingleNode("/manifest/application");
        const string android = "http://schemas.android.com/apk/res/android";
        foreach (var pair in new[] { ("pvr.app.type", "vr"), ("controller", "1") })
        {
            var node = xml.CreateElement("meta-data");
            node.SetAttribute("name", android, pair.Item1);
            node.SetAttribute("value", android, pair.Item2);
            app.AppendChild(node);
        }
        xml.Save(manifest);
    }
}
