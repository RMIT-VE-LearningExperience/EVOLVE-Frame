using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.XR.OpenXR.Features;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.XR.OpenXR;
using UnityEngine.XR.OpenXR.Features;
using UnityEngine.XR.OpenXR.Features.Interactions;
using UnityEngine.XR.OpenXR.Features.MetaQuestSupport;

// Build the already baked shared scene. Never run Prepare here: it replaces that scene.
public static class FrameLabQuestBuild
{
    internal static bool IsBuilding { get; private set; }
    const string Scene = "Assets/FrameLab/Scenes/Leichhardt.unity";
    const string Output = "Builds/Android/Leichhardt-Quest3-3S.apk";
    const string Evidence = "Builds/Android/Quest-profile.json";

    [Serializable] class ProfileEvidence
    {
        public string version, result, scene, apk;
        public string[] devices, enabledFeatures, excludedPicoPlugins;
        public bool restoredPicoSettings;
    }

    [MenuItem("Frame Lab/Build Quest 3 and 3S APK")]
    public static void BuildAndroid() => WithQuestProfile(true);

    [MenuItem("Frame Lab/Validate Quest profile and restore PICO")]
    public static void ValidateProfile() => WithQuestProfile(false);

    static void WithQuestProfile(bool build)
    {
        if (!File.Exists(Scene)) throw new BuildFailedException("Prepare and bake Leichhardt before building Quest.");
        FeatureHelpers.RefreshFeatures(BuildTargetGroup.Android);
        var xr = OpenXRSettings.GetSettingsForBuildTargetGroup(BuildTargetGroup.Android);
        if (xr == null) throw new BuildFailedException("Android OpenXR settings are missing.");
        var features = xr.GetFeatures().Where(f => f != null).ToArray();
        var before = features.ToDictionary(f => f, f => EditorJsonUtility.ToJson(f));
        var enabledBefore = features.ToDictionary(f => f, f => f.enabled);
        string xrBefore = EditorJsonUtility.ToJson(xr);
        var entryBefore = PlayerSettings.Android.applicationEntry;
        var report = new ProfileEvidence { version = FrameLabBuild.AppVersion, result = "IN_PROGRESS",
            scene = Scene, apk = build ? Output : null, devices = new[] { "Quest 3", "Quest 3S" } };
        Directory.CreateDirectory("Builds/Android");
        try
        {
            foreach (var f in features)
            {
                f.enabled = f is MetaQuestFeature || f is OculusTouchControllerProfile || f is MetaQuestTouchPlusControllerProfile;
                EditorUtility.SetDirty(f);
            }
            var meta = xr.GetFeature<MetaQuestFeature>();
            if (meta == null || xr.GetFeature<OculusTouchControllerProfile>() == null ||
                xr.GetFeature<MetaQuestTouchPlusControllerProfile>() == null)
                throw new BuildFailedException("Required Quest OpenXR features are missing.");
            meta.OnEnable(); // Populate the SDK's known target-device records before selecting them.
            var settings = new SerializedObject(meta);
            var devices = settings.FindProperty("targetDevices");
            int selected = 0;
            for (int i = 0; i < devices.arraySize; i++)
            {
                var device = devices.GetArrayElementAtIndex(i);
                string name = device.FindPropertyRelative("manifestName").stringValue;
                bool use = name == "eureka" || name == "quest3s";
                device.FindPropertyRelative("enabled").boolValue = use;
                if (use) selected++;
            }
            if (selected != 2) throw new BuildFailedException("Quest 3 and Quest 3S target entries were not both found.");
            settings.FindProperty("m_symmetricProjection").boolValue = true;
            settings.FindProperty("m_optimizeBufferDiscards").boolValue = true;
            settings.ApplyModifiedPropertiesWithoutUndo();
            xr.renderMode = OpenXRSettings.RenderMode.SinglePassInstanced;
            PlayerSettings.Android.applicationEntry = AndroidApplicationEntry.GameActivity;
            if (PlayerSettings.Android.targetArchitectures != AndroidArchitecture.ARM64 ||
                PlayerSettings.GetGraphicsAPIs(BuildTarget.Android).First() != GraphicsDeviceType.Vulkan)
                throw new BuildFailedException("The shared mobile profile must use ARM64 and Vulkan.");
            if (PlayerSettings.bundleVersion != FrameLabBuild.AppVersion ||
                PlayerSettings.Android.bundleVersionCode != FrameLabBuild.AppVersionCode)
                throw new BuildFailedException("Build version does not match the prepared scene.");
            report.enabledFeatures = features.Where(f => f.enabled).Select(f => f.GetType().Name).ToArray();
            if (report.enabledFeatures.Length != 3) throw new BuildFailedException("Unexpected extra Quest feature.");
            report.excludedPicoPlugins = PicoPlugins().Select(p => p.assetPath).ToArray();
            EditorUtility.SetDirty(xr);
            AssetDatabase.SaveAssets();
            Debug.Log("LEICHHARDT_QUEST_PROFILE " + JsonUtility.ToJson(report));
            if (build)
            {
                IsBuilding = true;
                var result = BuildPipeline.BuildPlayer(new BuildPlayerOptions {
                    scenes = new[] { Scene }, locationPathName = Output, target = BuildTarget.Android,
                    options = BuildOptions.Development
                });
                if (result.summary.result != BuildResult.Succeeded)
                    throw new BuildFailedException("Quest APK failed with " + result.summary.totalErrors + " errors.");
            }
            report.result = "PASS";
        }
        finally
        {
            IsBuilding = false;
            foreach (var pair in before)
            {
                EditorJsonUtility.FromJsonOverwrite(pair.Value, pair.Key);
                EditorUtility.SetDirty(pair.Key);
            }
            EditorJsonUtility.FromJsonOverwrite(xrBefore, xr);
            EditorUtility.SetDirty(xr);
            PlayerSettings.Android.applicationEntry = entryBefore;
            foreach (var importer in PicoPlugins()) importer.SetIncludeInBuildDelegate(null);
            AssetDatabase.SaveAssets();
            report.restoredPicoSettings = features.All(f => f.enabled == enabledBefore[f]) &&
                PlayerSettings.Android.applicationEntry == entryBefore;
            File.WriteAllText(Evidence, JsonUtility.ToJson(report, true));
            if (!report.restoredPicoSettings) throw new BuildFailedException("Could not restore the original PICO settings.");
            Debug.Log("LEICHHARDT_PICO_SETTINGS_RESTORED");
        }
        Debug.Log(build ? "LEICHHARDT_QUEST_APK_SUCCESS" : "LEICHHARDT_QUEST_PROFILE_PASS");
    }

    internal static PluginImporter[] PicoPlugins() => PluginImporter.GetAllImporters()
        .Where(p => p.assetPath.StartsWith("Packages/com.unity.xr.openxr.picoxr/", StringComparison.Ordinal)).ToArray();
}

// Run after Unity's OpenXR native-library selection, without editing package import settings.
public sealed class FrameLabQuestNativePlugins : IPreprocessBuildWithReport
{
    public int callbackOrder => 10000;
    public void OnPreprocessBuild(BuildReport report)
    {
        if (!FrameLabQuestBuild.IsBuilding) return;
        foreach (var importer in FrameLabQuestBuild.PicoPlugins())
            importer.SetIncludeInBuildDelegate(path => false);
    }
}
