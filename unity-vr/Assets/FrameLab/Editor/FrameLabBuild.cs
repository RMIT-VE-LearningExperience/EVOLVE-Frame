using System;
using System.IO;
using System.Linq;
using FrameLab;
using Unity.XR.CoreUtils;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEditor.XR.Management;
using UnityEditor.XR.Management.Metadata;
using UnityEditor.XR.OpenXR.Features;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.XR.Interaction.Toolkit;
using UnityEngine.XR.Interaction.Toolkit.Interactables;
using UnityEngine.XR.Interaction.Toolkit.Interactors;
using UnityEngine.XR.Interaction.Toolkit.Interactors.Casters;
using UnityEngine.XR.Interaction.Toolkit.Locomotion.Movement;
using UnityEngine.XR.Interaction.Toolkit.Locomotion;
using UnityEngine.XR.Interaction.Toolkit.Locomotion.Turning;
using UnityEngine.XR.Interaction.Toolkit.Samples.StarterAssets;
using UnityEngine.XR.Management;
using UnityEngine.XR.OpenXR;
using UnityEngine.XR.OpenXR.Features.Interactions;
using Unity.XR.OpenXR.Features.PICOSupport;
using UnityEngine.Events;

public static class FrameLabBuild
{
    public const string AppVersion = "0.4.6";
    public const int AppVersionCode = 14;
    [Serializable] class PartList { public Part[] parts; }
    [Serializable] class InspectionContent { public InspectionText[] parts; }
    [Serializable] class InspectionText { public string id, shortName, title, caption; }
    [Serializable] class Part
    {
        public string name;
        public string title;
        public string note;
        public string material;
        public float[] color;
        public float metallic;
        public float roughness;
    }
    const string ScenePath = "Assets/FrameLab/Scenes/Leichhardt.unity";
    const string Generated = "Assets/FrameLab/Generated";
    const string RigPath = "Assets/Samples/XR Interaction Toolkit/3.6.1/Starter Assets/Prefabs/XR Origin (XR Rig).prefab";

    [MenuItem("Frame Lab/Prepare project and scene")]
    public static void Prepare()
    {
        Directory.CreateDirectory(Generated);
        Directory.CreateDirectory("Assets/FrameLab/Scenes");
        AssetDatabase.Refresh();
        var modelImporter = AssetImporter.GetAtPath("Assets/FrameLab/Models/building.glb");
        var modelSettings = new SerializedObject(modelImporter);
        var lightmapUV = modelSettings.FindProperty("editorImportSettings.generateSecondaryUVSet");
        if (!lightmapUV.boolValue)
        {
            lightmapUV.boolValue = true;
            modelSettings.ApplyModifiedPropertiesWithoutUndo();
            modelImporter.SaveAndReimport();
        }
        ConfigureTextures();
        ConfigureProject();
        CreateScene();
        AssetDatabase.SaveAssets();
        Debug.Log("FRAME_LAB_PREPARED");
    }

    static void ConfigureProject()
    {
        PlayerSettings.companyName = "EVOLVE Learning";
        PlayerSettings.productName = "Leichhardt";
        PlayerSettings.bundleVersion = AppVersion;
        PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Android, "au.edu.evolve.framelab");
        PlayerSettings.SetScriptingBackend(NamedBuildTarget.Android, ScriptingImplementation.IL2CPP);
        PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
        PlayerSettings.Android.minSdkVersion = AndroidSdkVersions.AndroidApiLevel29;
        PlayerSettings.Android.targetSdkVersion = AndroidSdkVersions.AndroidApiLevelAuto;
        PlayerSettings.Android.bundleVersionCode = AppVersionCode;
        PlayerSettings.defaultInterfaceOrientation = UIOrientation.LandscapeLeft;
        PlayerSettings.colorSpace = ColorSpace.Linear;
        PlayerSettings.runInBackground = true;
        PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android, false);
        PlayerSettings.SetGraphicsAPIs(BuildTarget.Android, new[] { GraphicsDeviceType.Vulkan });
        PlayerSettings.stripUnusedMeshComponents = true;
        var playerSettings = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/ProjectSettings.asset")[0]);
        playerSettings.FindProperty("activeInputHandler").intValue = 1;
        playerSettings.ApplyModifiedPropertiesWithoutUndo();

        const string xrPath = "Assets/FrameLab/Generated/XRSettings.asset";
        var xr = AssetDatabase.LoadAssetAtPath<XRGeneralSettingsPerBuildTarget>(xrPath);
        if (xr == null)
        {
            xr = ScriptableObject.CreateInstance<XRGeneralSettingsPerBuildTarget>();
            AssetDatabase.CreateAsset(xr, xrPath);
        }
        EditorBuildSettings.AddConfigObject(XRGeneralSettings.settingsKey, xr, true);
        if (!xr.HasManagerSettingsForBuildTarget(BuildTargetGroup.Android))
            xr.CreateDefaultManagerSettingsForBuildTarget(BuildTargetGroup.Android);
        var manager = xr.ManagerSettingsForBuildTarget(BuildTargetGroup.Android);
        if (!XRPackageMetadataStore.AssignLoader(manager, "UnityEngine.XR.OpenXR.OpenXRLoader", BuildTargetGroup.Android))
            throw new InvalidOperationException("Cannot assign the Android OpenXR loader.");
        xr.SettingsForBuildTarget(BuildTargetGroup.Android).InitManagerOnStart = true;
        FeatureHelpers.RefreshFeatures(BuildTargetGroup.Android);
        var openxr = OpenXRSettings.GetSettingsForBuildTargetGroup(BuildTargetGroup.Android);
        if (openxr == null) throw new InvalidOperationException("OpenXR settings were not created.");
        openxr.renderMode = OpenXRSettings.RenderMode.SinglePassInstanced;
        var pico = openxr.GetFeature<PICOFeature>();
        var controller = openxr.GetFeature<PICO4UltraControllerProfile>();
        if (pico == null || controller == null) throw new InvalidOperationException("PICO OpenXR features missing.");
        pico.enabled = true;
        controller.enabled = true;
        EditorUtility.SetDirty(openxr);
        EditorUtility.SetDirty(xr);

        var pipeline = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(Generated + "/MobilePipeline.asset");
        if (pipeline == null)
        {
            var renderer = ScriptableObject.CreateInstance<UniversalRendererData>();
            AssetDatabase.CreateAsset(renderer, Generated + "/MobileRenderer.asset");
            pipeline = UniversalRenderPipelineAsset.Create(renderer);
            AssetDatabase.CreateAsset(pipeline, Generated + "/MobilePipeline.asset");
        }
        pipeline.supportsHDR = false;
        pipeline.msaaSampleCount = 4;
        pipeline.renderScale = 1;
        pipeline.supportsCameraDepthTexture = false;
        pipeline.supportsCameraOpaqueTexture = false;
        pipeline.shadowDistance = 55;
        var pipelineSettings = new SerializedObject(pipeline);
        pipelineSettings.FindProperty("m_SoftShadowsSupported").boolValue = true;
        pipelineSettings.FindProperty("m_ReflectionProbeBoxProjection").boolValue = true;
        pipelineSettings.ApplyModifiedPropertiesWithoutUndo();
        pipeline.shadowDepthBias = 0.4f;
        pipeline.shadowNormalBias = 0.25f;
        pipeline.shadowCascadeCount = 2;
        GraphicsSettings.defaultRenderPipeline = pipeline;
        int activeQuality = QualitySettings.GetQualityLevel();
        for (int i = 0; i < QualitySettings.names.Length; i++)
        {
            QualitySettings.SetQualityLevel(i, false);
            QualitySettings.renderPipeline = pipeline;
        }
        QualitySettings.SetQualityLevel(activeQuality, false);
        QualitySettings.vSyncCount = 0;
        QualitySettings.shadows = UnityEngine.ShadowQuality.All;
        EditorUtility.SetDirty(pipeline);
        AddAlwaysIncludedShader("FrameLab/ComfortFade");
        AddAlwaysIncludedShader("Universal Render Pipeline/Unlit");
    }

    static void AddAlwaysIncludedShader(string name)
    {
        var settings = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/GraphicsSettings.asset")[0]);
        var shaders = settings.FindProperty("m_AlwaysIncludedShaders");
        Shader shader = Shader.Find(name);
        if (shader == null) throw new InvalidOperationException("Missing required runtime shader: " + name);
        for (int i = 0; i < shaders.arraySize; i++)
            if (shaders.GetArrayElementAtIndex(i).objectReferenceValue == shader) return;
        shaders.InsertArrayElementAtIndex(shaders.arraySize);
        shaders.GetArrayElementAtIndex(shaders.arraySize - 1).objectReferenceValue = shader;
        settings.ApplyModifiedPropertiesWithoutUndo();
    }

    static void CreateScene()
    {
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        RenderSettings.ambientMode = AmbientMode.Trilight;
        RenderSettings.ambientSkyColor = new Color(0.72f, 0.76f, 0.80f);
        RenderSettings.ambientEquatorColor = new Color(0.62f, 0.62f, 0.61f);
        RenderSettings.ambientGroundColor = new Color(0.32f, 0.32f, 0.30f);
        var sky = AssetDatabase.LoadAssetAtPath<Material>(Generated + "/Soft horizon.mat");
        if (sky == null)
        {
            sky = new Material(Shader.Find("FrameLab/SoftHorizon"));
            AssetDatabase.CreateAsset(sky, Generated + "/Soft horizon.mat");
        }
        sky.shader = Shader.Find("FrameLab/SoftHorizon");
        sky.SetColor("_HorizonColor", new Color(0.84f, 0.86f, 0.88f));
        sky.SetColor("_ZenithColor", new Color(0.69f, 0.79f, 0.88f));
        RenderSettings.skybox = sky;
        EditorUtility.SetDirty(sky);
        RenderSettings.fog = true;
        RenderSettings.fogMode = FogMode.Linear;
        RenderSettings.fogColor = new Color(0.84f, 0.86f, 0.88f);
        RenderSettings.fogStartDistance = 45;
        RenderSettings.fogEndDistance = 120;
        var sun = new GameObject("Leichhardt sun").AddComponent<Light>();
        sun.type = LightType.Directional;
        sun.color = new Color(1, 0.97f, 0.93f);
        sun.intensity = 1.2f;
        sun.shadows = LightShadows.Soft;
        sun.shadowBias = 0.2f;
        sun.shadowNormalBias = 0.35f;
        LeichhardtSiteLighting.Configure(sun);
        RenderSettings.sun = sun;

        var groundMaterial = Material("Ground", new Color(0.68f, 0.67f, 0.64f));
        groundMaterial.shader = Shader.Find("Universal Render Pipeline/Lit");
        groundMaterial.SetTexture("_BaseMap", null);
        groundMaterial.SetTexture("_BumpMap", null);
        groundMaterial.DisableKeyword("_NORMALMAP");
        var floorMaterial = Material("Concrete", new Color(0.95f, 0.94f, 0.91f));
        floorMaterial.SetTexture("_BaseMap", Texture("concrete_clean_albedo.png"));
        floorMaterial.SetTextureScale("_BaseMap", Vector2.one);
        floorMaterial.SetTexture("_BumpMap", null);
        floorMaterial.DisableKeyword("_NORMALMAP");
        Box("Plain ground", new Vector3(-12, -0.16f, 0), new Vector3(300, 0.2f, 300), groundMaterial);
        Box("Ground floor slab", new Vector3(-16.685f, -0.11f, -3.94f), new Vector3(20.61f, 0.22f, 7.88f), floorMaterial);
        Box("Entry approach", new Vector3(-29.6f, -0.13f, -5.33f), new Vector3(5.22f, 0.26f, 2.3f), floorMaterial);
        // Complete the L-shaped landing beneath the second canopy post.
        // This abuts the existing approach at z=-6.48 without overlapping it.
        Box("Porch landing extension", new Vector3(-27.72f, -.13f, -7.2475f), new Vector3(1.46f, .26f, 1.535f), floorMaterial);
        Box("Exterior viewing pad", new Vector3(-16, -0.13f, 2.6f), new Vector3(7, 0.26f, 4.8f), floorMaterial);
        Box("Garage slab", new Vector3(-3.19f, -0.11f, -5.915f), new Vector3(6.38f, 0.22f, 6.91f), floorMaterial);

        GameObject building = Model("building");
        var renderers = building.GetComponentsInChildren<MeshRenderer>(true);
        foreach (var renderer in renderers)
        {
            renderer.gameObject.layer = 8;
            var filter = renderer.GetComponent<MeshFilter>();
            var collider = renderer.gameObject.AddComponent<MeshCollider>();
            collider.sharedMesh = filter.sharedMesh;
        }
        var walls = renderers.Where(r => (int.Parse(r.name.Substring(0, 2)) >= 23 && int.Parse(r.name.Substring(0, 2)) <= 27) || r.name.StartsWith("29")).Cast<Renderer>().ToArray();
        var roof = renderers.Where(r => int.Parse(r.name.Substring(0, 2)) >= 20 && int.Parse(r.name.Substring(0, 2)) <= 22).Cast<Renderer>().ToArray();
        GameObject detailModel = Model("window");
        detailModel.transform.position = new Vector3(10, 0, 10);
        var detail = new GameObject("Window study");
        var detailBounds = detailModel.GetComponentsInChildren<MeshRenderer>().Select(r => r.bounds).ToArray();
        Bounds combined = detailBounds[0]; foreach (var bounds in detailBounds.Skip(1)) combined.Encapsulate(bounds);
        detail.transform.position = combined.center; detailModel.transform.SetParent(detail.transform, true);
        detail.transform.localScale = Vector3.one * .85f;
        detail.transform.position = new Vector3(combined.center.x, combined.center.y * .85f + .04f, combined.center.z);
        var studyFloorMaterial = Material("Inspection floor", new Color(.28f, .31f, .33f));
        var detailFloor = Box("Detail inspection floor", new Vector3(10, -0.11f, 9), new Vector3(10, 0.22f, 10), studyFloorMaterial);
        var plinth = Box("Window study plinth", new Vector3(10, .02f, 10), new Vector3(3.4f, .04f, 3.4f), Material("Study plinth", new Color(.20f, .23f, .25f)));
        plinth.transform.SetParent(detailFloor.transform, true);
        var studyLight = new GameObject("Inspection daylight").AddComponent<Light>();
        studyLight.type = LightType.Directional; studyLight.lightmapBakeType = LightmapBakeType.Realtime;
        studyLight.color = new Color(1, .97f, .93f); studyLight.intensity = .9f;
        studyLight.shadows = LightShadows.Soft; studyLight.shadowStrength = .65f;
        studyLight.transform.SetParent(detailFloor.transform, true); studyLight.transform.rotation = Quaternion.Euler(45, -30, 0);

        var rigObject = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(RigPath));
        var rig = rigObject.GetComponent<XROrigin>();
        rig.RequestedTrackingOriginMode = XROrigin.TrackingOriginMode.Floor;
        rig.Camera.nearClipPlane = 0.05f;
        rig.Camera.farClipPlane = 650;
        rig.Camera.backgroundColor = RenderSettings.fogColor;
        rig.Camera.clearFlags = CameraClearFlags.Skybox;
        rig.Camera.GetUniversalAdditionalCameraData().renderPostProcessing = false;
        foreach (var locomotion in rigObject.GetComponentsInChildren<LocomotionProvider>(true))
            locomotion.enabled = locomotion is SnapTurnProvider;
        foreach (var turn in rigObject.GetComponentsInChildren<SnapTurnProvider>(true)) turn.turnAmount = 30;
        foreach (var ray in rigObject.GetComponentsInChildren<XRRayInteractor>(true)) ray.raycastMask |= 1 << 8;
        foreach (var caster in rigObject.GetComponentsInChildren<CurveInteractionCaster>(true)) caster.raycastMask |= 1 << 8;
        foreach (var caster in rigObject.GetComponentsInChildren<SphereInteractionCaster>(true)) caster.physicsLayerMask |= 1 << 8;
        foreach (var input in rigObject.GetComponentsInChildren<ControllerInputActionManager>(true))
        {
            // Keep the ordinary selection ray available. Locomotion uses validated destination buttons.
            input.enabled = false;
        }
        foreach (var child in rigObject.GetComponentsInChildren<Transform>(true))
            if (child.name == "Teleport Interactor") child.gameObject.SetActive(false);
        if (UnityEngine.Object.FindAnyObjectByType<XRInteractionManager>() == null)
            new GameObject("XR interaction manager", typeof(XRInteractionManager));

        var session = new GameObject("Frame Lab session", typeof(FrameLabTelemetry)).AddComponent<FrameLabSession>();
        session.rig = rig;
        session.building = building;
        session.detail = detail;
        session.detailFloor = detailFloor;
        session.walls = walls;
        session.roof = roof;
        session.enclosure = walls.Concat(roof).ToArray();
        session.fittings = session.gameObject.AddComponent<FrameLabFittings>();
        string[] fittingLabels = { "Kitchen", "Laundry", "Wardrobes & linen", "Vanities & mirrors", "Showers", "Toilets" };
        session.fittings.groups = fittingLabels.Select((label, index) => new FrameLabFittings.Group {
            label = label, surfaces = renderers.Where(r => r.name.StartsWith((30 + index).ToString())).Cast<Renderer>().ToArray()
        }).ToArray();
        if (session.fittings.groups.Any(g => g.surfaces.Length == 0)) throw new InvalidOperationException("Missing fitting visibility group");
        session.stairPaintedStructure = renderers.Where(r => r.name.StartsWith("12") && r.sharedMaterial.name.Contains("warm white lining")).Cast<Renderer>().ToArray();
        session.stairFinishMaterial = session.stairPaintedStructure.First().sharedMaterial;
        session.stairTimberMaterial = renderers.First(r => r.name.StartsWith("12") && r.sharedMaterial.name.Contains("Stair oak timber")).sharedMaterial;
        session.tour = JsonUtility.FromJson<FrameLabTour>(File.ReadAllText("Assets/FrameLab/Content/tour.json"));
        foreach (var stop in session.tour.rooms.Concat(session.tour.studies))
        {
            string path = "Assets/FrameLab/Audio/Tour/" + stop.id + ".mp3";
            stop.audio = AssetDatabase.LoadAssetAtPath<AudioClip>(path);
            if (stop.audio == null) throw new InvalidOperationException("Missing offline narration: " + stop.id);
            var importer = (AudioImporter)AssetImporter.GetAtPath(path);
            var audioSettings = importer.defaultSampleSettings;
            audioSettings.loadType = AudioClipLoadType.CompressedInMemory;
            audioSettings.compressionFormat = AudioCompressionFormat.Vorbis;
            audioSettings.quality = 0.65f;
            importer.defaultSampleSettings = audioSettings;
            importer.forceToMono = true;
            importer.SaveAndReimport();
        }
        session.obstructionMask = 1 << 8;
        session.lighting = session.gameObject.AddComponent<FrameLabLightingState>();
        AddDetailInteractions(detail, session);
        session.destinations = session.tour.rooms.Select(stop => Destination(stop.title, stop.position, stop.yaw)).ToArray();
        session.detailDestination = Destination("Window inspection", new Vector3(10, 0, 6.5f), 0);
        var probes = new GameObject("Room daylight probes").AddComponent<LightProbeGroup>();
        probes.probePositions = session.destinations.SelectMany(d => new[] {
            d.position + new Vector3(-0.3f, 0.6f, -0.3f), d.position + new Vector3(0.3f, 0.6f, 0.3f),
            d.position + new Vector3(-0.3f, 2.1f, 0.3f), d.position + new Vector3(0.3f, 2.1f, -0.3f) })
            .Concat(new[] { new Vector3(8, .5f, 6), new Vector3(12, .5f, 6), new Vector3(8, 3, 6), new Vector3(12, 3, 6),
                new Vector3(8, .5f, 12), new Vector3(12, .5f, 12), new Vector3(8, 3, 12), new Vector3(12, 3, 12) }).ToArray();
        // Next/Previous and Rooms provide navigation without raised floor markers.
        rigObject.transform.SetPositionAndRotation(session.destinations[0].position, session.destinations[0].rotation);
        detail.SetActive(false);
        detailFloor.SetActive(false);
        EditorSceneManager.SaveScene(scene, ScenePath);
        EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
        detailFloor.SetActive(true);
        ValidateScene(session);
        detailFloor.SetActive(false);
        DynamicGI.UpdateEnvironment();
        RenderPreview(rig.Camera, new Vector3(-35, 13, 15), new Vector3(-15, 2, -4), "overview.png");
        RenderPreview(rig.Camera, new Vector3(-14.5f, 1.65f, -3), new Vector3(-20, 1.4f, -5), "interior.png");
    }

    static GameObject Model(string name)
    {
        var asset = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/FrameLab/Models/" + name + ".glb");
        if (asset == null) throw new InvalidOperationException("Model import failed for " + name);
        var instance = (GameObject)PrefabUtility.InstantiatePrefab(asset);
        instance.name = name;
        var metadata = JsonUtility.FromJson<PartList>(File.ReadAllText("Assets/FrameLab/Models/" + name + ".parts.json"));
        foreach (var renderer in instance.GetComponentsInChildren<MeshRenderer>(true))
        {
            Part part = metadata.parts.FirstOrDefault(p => p.name == renderer.name);
            if (part == null) throw new InvalidOperationException("Unmapped model part " + renderer.name);
            var material = Material(part.material, new Color(part.color[0], part.color[1], part.color[2], 1));
            material.SetFloat("_Metallic", part.metallic);
            material.SetFloat("_Smoothness", 1 - part.roughness);
            if (part.material.ToLowerInvariant().Contains("glazing") || part.material.ToLowerInvariant().Contains("glass"))
            {
                bool obscure = part.material.ToLowerInvariant().Contains("obscure");
                material.SetColor("_BaseColor", obscure ? new Color(.78f, .79f, .79f, .97f) : new Color(0.6f, 0.8f, 0.85f, 0.18f));
                if (obscure)
                {
                    // Static frosted-daylight approximation, without a second
                    // camera or screen-space blur on the standalone headset.
                    material.SetFloat("_Smoothness", .15f);
                    material.EnableKeyword("_EMISSION");
                    material.SetColor("_EmissionColor", new Color(.43f,.44f,.44f));
                    material.globalIlluminationFlags = MaterialGlobalIlluminationFlags.BakedEmissive;
                }
                material.SetFloat("_Surface", 1);
                material.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
                material.SetFloat("_DstBlend", (float)BlendMode.OneMinusSrcAlpha);
                material.SetFloat("_ZWrite", 0);
                material.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
                material.renderQueue = (int)RenderQueue.Transparent;
                renderer.shadowCastingMode = ShadowCastingMode.Off;
            }
            StyleMaterial(material, part.material);
            EditorUtility.SetDirty(material);
            renderer.sharedMaterial = material;
            if (part.material.ToLowerInvariant().Contains("brick")) SetMasonryUVs(renderer, name);
            if (name == "building" && (part.material.ToLowerInvariant().Contains("plaster") || part.material.ToLowerInvariant().Contains("ceiling") || part.material.ToLowerInvariant().Contains("white cabinetry") || part.material.ToLowerInvariant().Contains("render") || part.material.ToLowerInvariant().Contains("garage metal roof") || part.material.ToLowerInvariant().Contains("porcelain")))
                SetFinishLightmapUVs(renderer);
        }
        return instance;
    }

    const string Textures = "Assets/FrameLab/Textures/";

    static Texture2D Texture(string name) => AssetDatabase.LoadAssetAtPath<Texture2D>(Textures + name);

    static void ConfigureTextures()
    {
        foreach (string path in Directory.GetFiles(Textures))
        {
            if (AssetImporter.GetAtPath(path) is not TextureImporter importer) continue;
            bool normal = path.Contains("_nor_gl_");
            importer.textureType = normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
            importer.sRGBTexture = !normal && !path.EndsWith(".hdr");
            importer.maxTextureSize = path.EndsWith(".hdr") ? 2048 : 1024;
            importer.mipmapEnabled = true;
            importer.anisoLevel = 4;
            importer.wrapMode = TextureWrapMode.Repeat;
            importer.SaveAndReimport();
        }
    }

    static void ApplyTexture(Material material, string source, Vector2 scale, float strength)
    {
        var baseMap = Texture(source + "_diff_1k.jpg") ?? Texture(source + "_col_1k.jpg");
        var normalMap = Texture(source + "_nor_gl_1k.jpg");
        if (baseMap == null || normalMap == null) throw new InvalidOperationException("Texture missing: " + source);
        material.SetTexture("_BaseMap", baseMap);
        material.SetTextureScale("_BaseMap", scale);
        material.SetTexture("_BumpMap", normalMap);
        material.SetFloat("_BumpScale", strength);
        material.EnableKeyword("_NORMALMAP");
        material.SetFloat("_Smoothness", 0.18f);
        EditorUtility.SetDirty(material);
    }

    static void StyleMaterial(Material material, string name)
    {
        string kind = name.ToLowerInvariant();
        if (kind.Contains("porcelain"))
        {
            bool wall = kind.Contains("wall porcelain");
            material.shader = Shader.Find("FrameLab/Porcelain");
            if (material.shader == null) throw new InvalidOperationException("Porcelain shader missing");
            material.SetTexture("_BaseMap", null);
            material.SetTextureScale("_BaseMap", new Vector2(1f/.6f,1f/(wall ? .3f : .6f)));
            material.SetColor("_BaseColor", wall ? new Color(.80f,.79f,.76f) : new Color(.67f,.66f,.63f));
            // Shared URP Lit buffer slot is relabelled Tile height in this shader.
            material.SetFloat("_Parallax", wall ? .3f : .6f);
            material.SetFloat("_Smoothness", wall ? .30f : .22f);
            material.SetFloat("_Metallic", 0);
            material.SetTexture("_BumpMap", null);
            material.DisableKeyword("_NORMALMAP");
            material.DisableKeyword("_PARALLAXMAP");
        }
        else if (kind.Contains("finished door"))
        {
            material.SetTexture("_BaseMap", Texture("pine_clean_albedo.png"));
            material.SetTextureScale("_BaseMap", new Vector2(1.8f, .35f));
            material.SetTexture("_BumpMap", null); material.DisableKeyword("_NORMALMAP");
            material.SetColor("_BaseColor", new Color(.56f, .46f, .35f));
            material.SetFloat("_Smoothness", .4f);
        }
        else if (kind.Contains("pine") || kind.Contains("timber"))
        {
            // Continuous fine grain, with a pale neutral material tint; matte unfinished timber.
            material.SetTexture("_BaseMap", Texture("pine_clean_albedo.png"));
            material.SetTextureScale("_BaseMap", new Vector2(1, 0.5f));
            material.SetTexture("_BumpMap", null);
            material.DisableKeyword("_NORMALMAP");
            material.SetColor("_BaseColor", new Color(0.80f, 0.81f, 0.80f));
            material.SetFloat("_Smoothness", 0.18f);
        }
        else if (name.Contains("LVL") || name.Contains("Floor board"))
        {
            ApplyTexture(material, "plywood", new Vector2(0.5f, 0.5f), 0.12f);
            material.SetColor("_BaseColor", new Color(1.48f, 1.43f, 1.30f));
        }
        else if (kind.Contains("ceiling")) material.SetColor("_BaseColor", new Color(.89f,.89f,.88f));
        else if (kind.Contains("plaster") || kind.Contains("lining")) material.SetColor("_BaseColor", new Color(.84f,.835f,.82f));
        else if (kind.Contains("mirror"))
        {
            material.SetColor("_BaseColor", new Color(.90f,.90f,.90f));
            material.SetFloat("_Smoothness", .94f);
        }
        else if (kind.Contains("flashing"))
        {
            material.SetColor("_BaseColor", new Color(0.48f, 0.52f, 0.55f));
            material.SetFloat("_Metallic", 0.55f);
            material.SetFloat("_Smoothness", 0.35f);
        }
        else if (kind.Contains("decking"))
        {
            material.SetTexture("_BaseMap", Texture("pine_clean_albedo.png"));
            material.SetTextureScale("_BaseMap", new Vector2(0.7f, 0.7f));
            material.SetColor("_BaseColor", new Color(.86f,.87f,.86f));
        }
        else if (kind.Contains("wrap") || kind.Contains("wall membrane")) material.SetColor("_BaseColor", new Color(0.72f, 0.76f, 0.77f));
        else if (kind.Contains("render")) material.SetColor("_BaseColor", new Color(.79f,.79f,.77f));
        else if (kind.Contains("brick"))
        {
            material.shader = Shader.Find("FrameLab/Masonry");
            material.SetColor("_BaseColor", new Color(0.72f, 0.69f, 0.61f));
            material.SetTexture("_BaseMap", null);
            material.SetTextureScale("_BaseMap", Vector2.one);
            material.SetTexture("_BumpMap", null);
            material.DisableKeyword("_NORMALMAP");
        }
        else if (name.Contains("Metal roof")) material.SetColor("_BaseColor", new Color(0.30f, 0.36f, 0.40f));
        else if (name.Contains("Galvanised"))
        {
            material.SetColor("_BaseColor", new Color(0.65f, 0.68f, 0.70f));
            material.SetFloat("_Smoothness", 0.38f);
        }
    }

    static void SetFinishLightmapUVs(MeshRenderer renderer)
    {
        var filter = renderer.GetComponent<MeshFilter>();
        var mesh = LeichhardtPlanarUV.Build(filter.sharedMesh);
        string path = Generated + "/" + renderer.name + " finish lightmap mesh.asset";
        var saved = AssetDatabase.LoadAssetAtPath<Mesh>(path);
        if (saved == null) { AssetDatabase.CreateAsset(mesh, path); saved = mesh; }
        else { EditorUtility.CopySerialized(mesh, saved); UnityEngine.Object.DestroyImmediate(mesh); }
        filter.sharedMesh = saved;
    }

    static void SetMasonryUVs(MeshRenderer renderer, string model)
    {
        var filter = renderer.GetComponent<MeshFilter>();
        var mesh = UnityEngine.Object.Instantiate(filter.sharedMesh);
        var vertices = mesh.vertices;
        var uv = new Vector2[vertices.Length];
        for (int i = 0; i < vertices.Length; i++)
        {
            Vector3 point = renderer.transform.TransformPoint(vertices[i]);
            uv[i] = new Vector2(point.x + point.z, point.y);
        }
        mesh.uv = uv;
        mesh.RecalculateTangents();
        string path = Generated + "/" + model + " " + renderer.name + " masonry mesh.asset";
        var saved = AssetDatabase.LoadAssetAtPath<Mesh>(path);
        if (saved == null) { AssetDatabase.CreateAsset(mesh, path); saved = mesh; }
        else { EditorUtility.CopySerialized(mesh, saved); UnityEngine.Object.DestroyImmediate(mesh); }
        filter.sharedMesh = saved;
    }

    static void AddDetailInteractions(GameObject detail, FrameLabSession session)
    {
        var content = JsonUtility.FromJson<InspectionContent>(File.ReadAllText("Assets/FrameLab/Content/inspection.json"));
        var surfaces = detail.GetComponentsInChildren<MeshRenderer>(true);
        foreach (var renderer in detail.GetComponentsInChildren<MeshRenderer>(true))
        {
            renderer.gameObject.layer = 8;
            var collider = renderer.gameObject.AddComponent<MeshCollider>();
            collider.sharedMesh = renderer.GetComponent<MeshFilter>().sharedMesh;
            StyleInspection(renderer);
        }
        var body = detail.AddComponent<Rigidbody>(); body.isKinematic = true; body.useGravity = false;
        var grab = detail.AddComponent<XRGrabInteractable>();
        grab.movementType = XRBaseInteractable.MovementType.Instantaneous;
        grab.useDynamicAttach = true; grab.matchAttachPosition = true; grab.matchAttachRotation = true;
        grab.snapToColliderVolume = false; grab.throwOnDetach = false; grab.attachEaseInTime = .08f;
        grab.colliders.Clear(); grab.colliders.AddRange(detail.GetComponentsInChildren<Collider>());
        session.inspection = detail.AddComponent<FrameLabInspection>(); session.inspection.grab = grab;
        session.inspection.parts = content.parts.Select(p => new FrameLabInspection.Part {
            id = p.id, shortName = p.shortName, title = p.title, description = p.caption,
            surface = surfaces.First(r => r.name == p.id),
            audio = AssetDatabase.LoadAssetAtPath<AudioClip>("Assets/FrameLab/Audio/Tour/part_" + p.id + ".mp3") }).ToArray();
        foreach (var part in session.inspection.parts)
        {
            if (part.audio == null) throw new InvalidOperationException("Missing component narration " + part.id);
            var importer = (AudioImporter)AssetImporter.GetAtPath(AssetDatabase.GetAssetPath(part.audio));
            var audioSettings = importer.defaultSampleSettings;
            audioSettings.loadType = AudioClipLoadType.CompressedInMemory; audioSettings.compressionFormat = AudioCompressionFormat.Vorbis; audioSettings.quality = .65f;
            importer.defaultSampleSettings = audioSettings; importer.forceToMono = true; importer.SaveAndReimport();
        }
    }

    static void StyleInspection(MeshRenderer surface)
    {
        string id = surface.name;
        Color color = id switch {
            "frame" => new Color(.68f, .53f, .36f), "wrap" => new Color(.16f, .32f, .31f),
            "sill" => new Color(.39f, .46f, .50f), "jamb" => new Color(.28f, .36f, .42f),
            "head" => new Color(.34f, .42f, .48f), "window" => new Color(.10f, .14f, .17f),
            "glass" => new Color(.20f, .43f, .55f, .60f), "brick" => new Color(.53f, .27f, .17f),
            _ => new Color(.76f, .75f, .70f) };
        var material = Material("Inspection " + id, color);
        material.SetFloat("_Smoothness", id == "glass" ? .4f : .2f);
        material.SetFloat("_Metallic", id is "window" or "sill" or "jamb" or "head" ? .3f : 0);
        if (id == "frame") material.SetTexture("_BaseMap", Texture("pine_clean_albedo.png"));
        if (id == "brick") material.shader = Shader.Find("FrameLab/Masonry");
        if (id == "glass")
        {
            material.SetFloat("_Surface", 1); material.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
            material.SetFloat("_DstBlend", (float)BlendMode.OneMinusSrcAlpha); material.SetFloat("_ZWrite", 0);
            material.EnableKeyword("_SURFACE_TYPE_TRANSPARENT"); material.renderQueue = (int)RenderQueue.Transparent;
        }
        surface.sharedMaterial = material; EditorUtility.SetDirty(material);
        surface.lightProbeUsage = LightProbeUsage.Off;
    }

    static Transform Destination(string name, Vector3 position, float yaw)
    {
        var target = new GameObject(name).transform;
        target.SetPositionAndRotation(position, Quaternion.Euler(0, yaw, 0));
        return target;
    }

    static Material Material(string name, Color color)
    {
        string path = Generated + "/" + name + ".mat";
        var material = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (material == null)
        {
            material = new Material(Shader.Find("Universal Render Pipeline/Lit"));
            AssetDatabase.CreateAsset(material, path);
        }
        material.SetColor("_BaseColor", color);
        material.SetFloat("_Smoothness", 0.15f);
        return material;
    }

    static void CreateLandscape(Material material)
    {
        // Keep the building pad flat, with a gentle horizon outside the learning route.
        const int cells = 80;
        const float span = 600;
        var vertices = new Vector3[(cells + 1) * (cells + 1)];
        var uv = new Vector2[vertices.Length];
        var indices = new int[cells * cells * 6];
        for (int z = 0; z <= cells; z++)
        for (int x = 0; x <= cells; x++)
        {
            float px = (x / (float)cells - 0.5f) * span;
            float pz = (z / (float)cells - 0.5f) * span;
            float distance = new Vector2(px, pz).magnitude;
            float blend = Mathf.SmoothStep(0, 1, Mathf.InverseLerp(40, 130, distance));
            float height = blend * (3 + Mathf.PerlinNoise(x * 0.065f + 4, z * 0.065f + 9) * 16);
            int i = z * (cells + 1) + x;
            vertices[i] = new Vector3(px - 14, height - 0.15f, pz - 4);
            uv[i] = new Vector2(x / (float)cells, z / (float)cells);
            if (x == cells || z == cells) continue;
            int j = (z * cells + x) * 6;
            indices[j] = i; indices[j + 1] = i + cells + 1; indices[j + 2] = i + 1;
            indices[j + 3] = i + 1; indices[j + 4] = i + cells + 1; indices[j + 5] = i + cells + 2;
        }
        var mesh = new Mesh { name = "Landscape", vertices = vertices, uv = uv, triangles = indices };
        mesh.RecalculateNormals(); mesh.RecalculateTangents(); mesh.RecalculateBounds();
        string path = Generated + "/Landscape.asset";
        var saved = AssetDatabase.LoadAssetAtPath<Mesh>(path);
        if (saved == null) { AssetDatabase.CreateAsset(mesh, path); saved = mesh; }
        else { EditorUtility.CopySerialized(mesh, saved); UnityEngine.Object.DestroyImmediate(mesh); }
        var ground = new GameObject("Natural grass and distant hills", typeof(MeshFilter), typeof(MeshRenderer), typeof(MeshCollider));
        ground.GetComponent<MeshFilter>().sharedMesh = saved;
        ground.GetComponent<MeshCollider>().sharedMesh = saved;
        ground.GetComponent<MeshRenderer>().sharedMaterial = material;
    }

    static GameObject Box(string name, Vector3 position, Vector3 size, Material material)
    {
        var box = GameObject.CreatePrimitive(PrimitiveType.Cube);
        box.name = name;
        box.layer = 8;
        box.transform.position = position;
        box.transform.localScale = size;
        // Give concrete top surfaces metre-based UVs instead of stretching one tile over a slab.
        var mesh = UnityEngine.Object.Instantiate(box.GetComponent<MeshFilter>().sharedMesh);
        var uv = mesh.uv;
        var normals = mesh.normals;
        for (int i = 0; i < uv.Length; i++)
        {
            Vector2 scale = Mathf.Abs(normals[i].y) > 0.5f ? new Vector2(size.x, size.z) :
                Mathf.Abs(normals[i].x) > 0.5f ? new Vector2(size.z, size.y) : new Vector2(size.x, size.y);
            uv[i] = Vector2.Scale(uv[i], scale / 2);
        }
        mesh.uv = uv;
        string meshPath = Generated + "/" + name + ".asset";
        var savedMesh = AssetDatabase.LoadAssetAtPath<Mesh>(meshPath);
        if (savedMesh == null) { AssetDatabase.CreateAsset(mesh, meshPath); savedMesh = mesh; }
        else { EditorUtility.CopySerialized(mesh, savedMesh); UnityEngine.Object.DestroyImmediate(mesh); }
        box.GetComponent<MeshFilter>().sharedMesh = savedMesh;
        box.GetComponent<Renderer>().sharedMaterial = material;
        return box;
    }

    static void ValidateScene(FrameLabSession session)
    {
        Physics.SyncTransforms();
        var checks = session.destinations.Append(session.detailDestination).Select(t => new
        {
            name = t.name,
            overlaps = Physics.OverlapCapsule(t.position + Vector3.up * 0.4f,
                t.position + Vector3.up * 1.7f, 0.3f, 1 << 8, QueryTriggerInteraction.Ignore),
            supported = Physics.Raycast(t.position + Vector3.up * 0.1f, Vector3.down, 0.2f, 1 << 8)
        }).ToArray();
        var failures = checks.Where(c => c.overlaps.Length > 0 || !c.supported).ToArray();
        if (failures.Length > 0) throw new InvalidOperationException("Destination clearance/support: " +
            string.Join("; ", failures.Select(c => c.name + " hits=" + string.Join(",", c.overlaps.Select(o => o.name)) + " floor=" + c.supported)));
        Debug.Log("FRAME_LAB_DESTINATIONS_PASS " + checks.Length);
    }

    public static void RenderPreview(Camera camera, Vector3 position, Vector3 target, string filename)
    {
        Vector3 oldPosition = camera.transform.position;
        Quaternion oldRotation = camera.transform.rotation;
        camera.transform.position = position;
        camera.transform.LookAt(target);
        var texture = new RenderTexture(1600, 1000, 24) { antiAliasing = 4 };
        camera.targetTexture = texture;
        var request = new UniversalRenderPipeline.SingleCameraRequest { destination = texture };
        RenderPipeline.SubmitRenderRequest(camera, request);
        var resolved = new RenderTexture(1600, 1000, 0);
        Graphics.Blit(texture, resolved);
        RenderTexture.active = resolved;
        var image = new Texture2D(1600, 1000, TextureFormat.RGB24, false);
        image.ReadPixels(new Rect(0, 0, 1600, 1000), 0, 0);
        image.Apply();
        Directory.CreateDirectory("Builds/Preview");
        File.WriteAllBytes("Builds/Preview/" + filename, image.EncodeToPNG());
        camera.targetTexture = null;
        RenderTexture.active = null;
        UnityEngine.Object.DestroyImmediate(image);
        UnityEngine.Object.DestroyImmediate(texture);
        UnityEngine.Object.DestroyImmediate(resolved);
        camera.transform.SetPositionAndRotation(oldPosition, oldRotation);
    }

    [MenuItem("Frame Lab/Build PICO APK")]
    public static void BuildAndroid()
    {
        var xr = OpenXRSettings.GetSettingsForBuildTargetGroup(BuildTargetGroup.Android);
        if (xr == null || !xr.GetFeature<PICOFeature>().enabled ||
            xr.GetFeature<UnityEngine.XR.OpenXR.Features.MetaQuestSupport.MetaQuestFeature>().enabled)
            throw new BuildFailedException("The PICO build requires the PICO profile. Run Prepare or restore its settings first.");
        PlayerSettings.bundleVersion = AppVersion;
        PlayerSettings.Android.bundleVersionCode = AppVersionCode;
        // Runtime-created hotspot leaders have no scene material reference.
        // Retain their shader even when building an already prepared/baked scene.
        AddAlwaysIncludedShader("FrameLab/ComfortFade");
        AddAlwaysIncludedShader("Universal Render Pipeline/Unlit");
        AssetDatabase.SaveAssets();
        Directory.CreateDirectory("Builds/Android");
        var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
        {
            scenes = new[] { ScenePath },
            locationPathName = "Builds/Android/Leichhardt-PICO.apk",
            target = BuildTarget.Android,
            options = BuildOptions.Development
        });
        if (report.summary.result != BuildResult.Succeeded)
            throw new BuildFailedException("Android build failed with " + report.summary.totalErrors + " errors.");
        Debug.Log("FRAME_LAB_APK_SUCCESS " + report.summary.totalSize);
    }
}
