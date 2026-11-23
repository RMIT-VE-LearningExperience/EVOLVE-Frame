using System;
using System.IO;
using System.Linq;
using FrameLab;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

public static class FrameLabLighting
{
    public static void Bake()
    {
        var scene = EditorSceneManager.OpenScene("Assets/FrameLab/Scenes/Leichhardt.unity");
        var session = UnityEngine.Object.FindAnyObjectByType<FrameLabSession>();
        var garageCover = session.building.GetComponentsInChildren<MeshFilter>()
            .Where(f => f.name.StartsWith("20"))
            .SelectMany(f => f.sharedMesh.vertices.Select(v => f.transform.TransformPoint(v)))
            .Where(v => v.x > -6.4f && v.x < .26f && v.z > -9.58f && v.z < -2.25f && v.y < 4).ToArray();
        if (garageCover.Length == 0 || garageCover.Min(v => v.y - (3.547f + (-v.z - 9.05f) * Mathf.Tan(5 * Mathf.Deg2Rad))) < .038f)
            throw new InvalidOperationException("Garage covering must sit above its battens; refresh the imported model.");
        var settings = new LightingSettings
        {
            name = "Soft daylight bounce",
            bakedGI = true,
            realtimeGI = false,
            lightmapper = LightingSettings.Lightmapper.ProgressiveGPU,
            mixedBakeMode = MixedLightingMode.Subtractive,
            directionalityMode = LightmapsMode.NonDirectional,
            lightmapResolution = 24,
            lightmapMaxSize = 2048,
            maxBounces = 4,
            directSampleCount = 64,
            indirectSampleCount = 512,
            environmentSampleCount = 512,
            ao = true,
            aoMaxDistance = 0.04f,
            aoExponentIndirect = 0.2f,
            aoExponentDirect = 0
        };
        const string settingsPath = "Assets/FrameLab/Generated/Daylight bake.asset";
        var saved = AssetDatabase.LoadAssetAtPath<LightingSettings>(settingsPath);
        if (saved == null) { AssetDatabase.CreateAsset(settings, settingsPath); saved = settings; }
        else { EditorUtility.CopySerialized(settings, saved); UnityEngine.Object.DestroyImmediate(settings); }
        Lightmapping.lightingSettings = saved;
        LeichhardtSiteLighting.Configure(RenderSettings.sun);
        RenderSettings.sun.lightmapBakeType = LightmapBakeType.Baked;
        RenderSettings.sun.shadowAngle = 5.0f;
        RenderSettings.subtractiveShadowColor = new Color(.30f, .33f, .37f);
        foreach (var renderer in session.building.GetComponentsInChildren<MeshRenderer>())
        {
            // Transparent glazing must transmit daylight, rather than being
            // treated as an opaque occluder by the static lightmapper.
            var material = renderer.sharedMaterial;
            if (material.HasProperty("_Surface") && material.GetFloat("_Surface") > .5f)
            {
                GameObjectUtility.SetStaticEditorFlags(renderer.gameObject, 0);
                renderer.receiveGI = ReceiveGI.LightProbes;
                renderer.shadowCastingMode = ShadowCastingMode.Off;
                continue;
            }
            GameObjectUtility.SetStaticEditorFlags(renderer.gameObject, StaticEditorFlags.ContributeGI);
            renderer.receiveGI = ReceiveGI.Lightmaps;
            bool skirting = material.name.Contains("skirting trim");
            renderer.shadowCastingMode = skirting ? ShadowCastingMode.Off : ShadowCastingMode.On;
            renderer.scaleInLightmap = material.name.Contains("junction returns") || skirting ? 4f : material.name.Contains("white cabinetry") ? 1.5f : 1f;
        }
        foreach (var name in new[] { "Plain ground", "Ground floor slab", "Entry approach", "Porch landing extension", "Exterior viewing pad", "Garage slab" })
        {
            var surface = GameObject.Find(name);
            GameObjectUtility.SetStaticEditorFlags(surface, StaticEditorFlags.ContributeGI);
            surface.GetComponent<MeshRenderer>().receiveGI = ReceiveGI.Lightmaps;
            // Broad shadows need far less density than the building details.
            // Keep the 300 m plain ground inexpensive while receiving sunlight.
            surface.GetComponent<MeshRenderer>().scaleInLightmap = name == "Plain ground" ? .15f : 1;
            var mesh = surface.GetComponent<MeshFilter>().sharedMesh;
            Unwrapping.GenerateSecondaryUVSet(mesh);
            EditorUtility.SetDirty(mesh);
        }
        // Bake every visibility combination so roof changes never leave ghost shadows.
        RenderSettings.ambientMode = AmbientMode.Skybox;
        RenderSettings.ambientIntensity = .8f;
        // Broad, neutral baked fill keeps the learning interior readable without
        // adding runtime lights. Stable frame geometry receives the soft shading.
        for (int level = 0; level < 3; level++)
        {
            string name = "Baked daylight fill " + level;
            var existing = GameObject.Find(name);
            var fill = existing != null ? existing.GetComponent<Light>() : new GameObject(name).AddComponent<Light>();
            fill.type = LightType.Rectangle;
            fill.enabled = true;
            fill.lightmapBakeType = LightmapBakeType.Baked;
            fill.areaSize = level == 2 ? new Vector2(6.1f, 6.5f) : new Vector2(20.7f, 7.9f);
            fill.color = Color.white;
            fill.intensity = level == 2 ? .8f : .9f;
            fill.range = 12;
            fill.shadows = LightShadows.Soft;
            fill.transform.SetPositionAndRotation(level == 2 ? new Vector3(-3.19f, 2.634f, -5.9f) : new Vector3(-16.7f, level == 0 ? 2.72f : 5.69f, -3.94f),
                Quaternion.LookRotation(Vector3.down, Vector3.forward));
        }
        AddFitoutFill();
        // Baked upward fill offsets the timber floor's coloured bounce. It adds
        // no runtime lights and is removed with the other fill in open modes.
        for (int level = 0; level < 2; level++)
        {
            string name = "Baked daylight fill ceiling " + level;
            var existing = GameObject.Find(name);
            var light = existing != null ? existing.GetComponent<Light>() : new GameObject(name).AddComponent<Light>();
            light.type = LightType.Rectangle;
            light.lightmapBakeType = LightmapBakeType.Baked;
            light.areaSize = new Vector2(19.5f,6.8f);
            light.color = Color.white;
            light.intensity = .55f;
            light.range = 8;
            light.shadows = LightShadows.Soft;
            light.transform.SetPositionAndRotation(new Vector3(-16.7f,level == 0 ? .2f : 3.36f,-3.94f),Quaternion.LookRotation(Vector3.up,Vector3.forward));
        }
        EditorSceneManager.SaveScene(scene);
        try
        {
            foreach (bool empty in new[] { false, true })
            {
                session.fittings.SetAll(!empty);
                string prefix = empty ? "Empty" : "";
                foreach (var renderer in session.roof) renderer.enabled = true;
                foreach (var renderer in session.walls) renderer.enabled = true;
                session.SetStairTimber(false); SetFill(true);
                if (!Lightmapping.Bake()) throw new InvalidOperationException(prefix + " enclosed lighting bake failed.");
                var enclosed = Capture(prefix + "WallsShown");
                SetFill(false); session.SetStairTimber(true);
                foreach (var renderer in session.walls) renderer.enabled = false;
                if (!Lightmapping.Bake()) throw new InvalidOperationException(prefix + " exposed lighting bake failed.");
                var exposed = Capture(prefix + "WallsHidden");
                foreach (var renderer in session.roof) renderer.enabled = false;
                if (!Lightmapping.Bake()) throw new InvalidOperationException(prefix + " open frame lighting bake failed.");
                var frame = Capture(prefix + "WallsHiddenRoofHidden");
                foreach (var renderer in session.walls) renderer.enabled = true;
                session.SetStairTimber(false);
                if (!Lightmapping.Bake()) throw new InvalidOperationException(prefix + " open roof lighting bake failed.");
                var openRoof = Capture(prefix + "WallsShownRoofHidden");
                if (empty)
                {
                    session.lighting.emptyWallsShown = enclosed; session.lighting.emptyWallsHidden = exposed;
                    session.lighting.emptyWallsHiddenRoofHidden = frame; session.lighting.emptyWallsShownRoofHidden = openRoof;
                }
                else
                {
                    session.lighting.wallsShown = enclosed; session.lighting.wallsHidden = exposed;
                    session.lighting.wallsHiddenRoofHidden = frame; session.lighting.wallsShownRoofHidden = openRoof;
                }
            }
        }
        finally
        {
            foreach (var renderer in session.enclosure) renderer.enabled = true;
            session.fittings.SetAll(true); session.SetStairTimber(false);
            session.lighting.Apply(true);
            // Static building shadows are fully baked. The movable inspection
            // assembly has a separate light, enabled only in that study.
            foreach (var renderer in session.building.GetComponentsInChildren<MeshRenderer>())
                renderer.shadowCastingMode = ShadowCastingMode.Off;
            EditorUtility.SetDirty(session.lighting);
            EditorSceneManager.SaveScene(scene);
        }
        BakeInteriorReflections();
        session.fittings.SetAll(false); session.lighting.Apply(true, true, true);
        BakeInteriorReflections(true);
        session.fittings.SetAll(true); session.lighting.Apply(true);
        EditorSceneManager.SaveScene(scene);
        AssetDatabase.SaveAssets();
        Debug.Log("FRAME_LAB_BAKE_PASS maps=" + LightmapSettings.lightmaps.Length);
    }

    static void BakeInteriorReflections(bool empty = false)
    {
        // Static 128px room captures replace outdoor-sky reflections indoors.
        // Mirrors are approximate cubemap reflections; no runtime render cameras.
        string folder = "Assets/FrameLab/Lighting/Reflections/" + (empty ? "Empty" : "Furnished");
        foreach (var renderer in UnityEngine.Object.FindObjectsByType<MeshRenderer>(FindObjectsInactive.Include, FindObjectsSortMode.None))
            if (renderer.gameObject.layer == 8)
                GameObjectUtility.SetStaticEditorFlags(renderer.gameObject,
                    GameObjectUtility.GetStaticEditorFlags(renderer.gameObject) | StaticEditorFlags.ReflectionProbeStatic);
        Directory.CreateDirectory(folder);
        AssetDatabase.Refresh();
        void Room(string name, Vector3 eye, Vector3 centre, Vector3 size, int importance)
        {
            string objectName = "Baked reflection " + name;
            var existing = GameObject.Find(objectName);
            var probe = existing != null ? existing.GetComponent<ReflectionProbe>() : new GameObject(objectName).AddComponent<ReflectionProbe>();
            probe.transform.position = eye;
            probe.center = centre - eye;
            probe.size = size;
            probe.mode = ReflectionProbeMode.Baked;
            probe.resolution = 128;
            probe.hdr = true;
            probe.boxProjection = true;
            probe.blendDistance = .15f;
            probe.importance = importance;
            probe.intensity = 1.2f;
            probe.cullingMask = 1 << 8;
            probe.nearClipPlane = .05f;
            probe.farClipPlane = 40;
            probe.clearFlags = ReflectionProbeClearFlags.Skybox;
            string path = folder + "/" + name + ".exr";
            if (!Lightmapping.BakeReflectionProbe(probe, path)) throw new InvalidOperationException("Reflection bake failed: " + name);
            AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceSynchronousImport);
            var texture = AssetDatabase.LoadAssetAtPath<Cubemap>(path);
            if (texture == null) throw new InvalidOperationException("Missing baked cubemap: " + path);
            probe.customBakedTexture = texture;
            probe.mode = ReflectionProbeMode.Custom;
            EditorUtility.SetDirty(probe);
        }
        Room("Interior",new Vector3(-16.4f,1.5f,-6.65f),new Vector3(-16.7f,2.8f,-3.94f),new Vector3(20.6f,5.6f,7.9f),1);
        Room("Ensuite",new Vector3(-19.72f,1.5f,-1.95f),new Vector3(-19.46f,1.37f,-1.98f),new Vector3(1.8f,2.74f,3.78f),10);
        Room("Powder",new Vector3(-21.07f,1.5f,-6.65f),new Vector3(-20.82f,1.37f,-6.495f),new Vector3(1.6f,2.74f,2.59f),10);
        Room("Bathroom2",new Vector3(-11.7f,4.65f,-1),new Vector3(-11.74f,4.454f,-1.145f),new Vector3(2.2f,2.59f,2.11f),10);
        Room("UpperBathroom",new Vector3(-13.3f,4.65f,-6.1f),new Vector3(-13.33f,4.454f,-6.19f),new Vector3(2,2.59f,3.2f),10);
        var lighting = UnityEngine.Object.FindAnyObjectByType<FrameLabLightingState>();
        lighting.reflectionProbes = UnityEngine.Object.FindObjectsByType<ReflectionProbe>(FindObjectsSortMode.None).OrderBy(p => p.name).ToArray();
        var cubes = lighting.reflectionProbes.Select(p => p.customBakedTexture as Cubemap).ToArray();
        if (empty) lighting.emptyReflections = cubes; else lighting.furnishedReflections = cubes;
        Debug.Log("LEICHHARDT_REFLECTION_BAKE_PASS probes=5 resolution=128 mode=Custom");
    }

    public static void RefreshReflections()
    {
        var scene = EditorSceneManager.OpenScene("Assets/FrameLab/Scenes/Leichhardt.unity");
        var session = UnityEngine.Object.FindAnyObjectByType<FrameLabSession>();
        foreach (var renderer in session.enclosure) renderer.enabled = true;
        session.lighting.Apply(true);
        BakeInteriorReflections();
        EditorSceneManager.SaveScene(scene);
        AssetDatabase.SaveAssets();
    }

    static void SetFill(bool enabled)
    {
        foreach (var light in UnityEngine.Object.FindObjectsByType<Light>(FindObjectsSortMode.None))
            if (light.name.StartsWith("Baked daylight fill ")) light.enabled = enabled;
    }

    static void AddFitoutFill()
    {
        // Broad static fill under dropped ceilings and within compact wet rooms.
        // These are lighting aids, not claims about the electrical fixture setout.
        void Fill(string name, Vector3 position, Vector2 size, float intensity)
        {
            string objectName = "Baked daylight fill " + name;
            var existing = GameObject.Find(objectName);
            var light = existing != null ? existing.GetComponent<Light>() : new GameObject(objectName).AddComponent<Light>();
            light.type = LightType.Rectangle;
            light.lightmapBakeType = LightmapBakeType.Baked;
            light.enabled = true;
            light.areaSize = size;
            light.color = new Color(1,.985f,.97f);
            light.intensity = intensity;
            light.range = 10;
            light.shadows = LightShadows.Soft;
            light.transform.SetPositionAndRotation(position,Quaternion.LookRotation(Vector3.down,Vector3.forward));
        }
        Fill("Kitchen",new Vector3(-16.4f,2.38f,-6.4f),new Vector2(6.2f,2.2f),1.6f);
        Fill("Ensuite vanity",new Vector3(-18.88f,2.38f,-1.98f),new Vector2(.5f,1.7f),2f);
        Fill("Ensuite",new Vector3(-19.8f,2.71f,-2.0f),new Vector2(.8f,2.9f),1.5f);
        Fill("Powder",new Vector3(-20.82f,2.71f,-6.50f),new Vector2(1.25f,2.2f),1.5f);
        Fill("Upper bath",new Vector3(-13.33f,5.68f,-6.2f),new Vector2(1.55f,2.6f),1.5f);
        Fill("Bath 2",new Vector3(-11.74f,5.68f,-1.15f),new Vector2(1.7f,1.65f),1.5f);
        Fill("Laundry",new Vector3(-7.6f,2.71f,-6.2f),new Vector2(1.7f,2.65f),1.5f);
        Fill("Robe",new Vector3(-21.67f,2.71f,-1.98f),new Vector2(1.7f,3.2f),1f);
    }

    static FrameLabLightingState.State Capture(string name)
    {
        string folder = "Assets/FrameLab/Lighting/" + name;
        Directory.CreateDirectory(folder);
        AssetDatabase.Refresh();
        var colors = LightmapSettings.lightmaps.Select((map, index) =>
        {
            string source = AssetDatabase.GetAssetPath(map.lightmapColor);
            string target = folder + "/Lightmap" + index + Path.GetExtension(source);
            if (AssetDatabase.LoadAssetAtPath<Texture2D>(target) != null) AssetDatabase.DeleteAsset(target);
            if (!AssetDatabase.CopyAsset(source, target)) throw new InvalidOperationException("Cannot preserve lighting " + target);
            var importer = (TextureImporter)AssetImporter.GetAtPath(target);
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.SetPlatformTextureSettings(new TextureImporterPlatformSettings {
                name = "Android", overridden = true, maxTextureSize = 2048,
                format = TextureImporterFormat.ASTC_4x4, compressionQuality = 100 });
            importer.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(target);
        }).ToArray();
        var surfaces = UnityEngine.Object.FindObjectsByType<MeshRenderer>(FindObjectsInactive.Include, FindObjectsSortMode.None)
            .Select(r => new FrameLabLightingState.Surface { renderer = r, index = r.lightmapIndex, scaleOffset = r.lightmapScaleOffset }).ToArray();
        Debug.Log("FRAME_LAB_LIGHTING_STATE " + name + " maps=" + colors.Length);
        return new FrameLabLightingState.State { colors = colors, surfaces = surfaces };
    }
}
