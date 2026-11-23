using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using FrameLab;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit.Interactors;
using UnityEngine.XR.Interaction.Toolkit.Interactables;

// Exercises the normal session entry points before packaging the headset build.
public static class FrameLabSmokeTest
{
    public static void Run()
    {
        SessionState.SetBool("FrameLabSmokeTest", true);
        EditorSceneManager.OpenScene("Assets/FrameLab/Scenes/Leichhardt.unity");
        EditorApplication.EnterPlaymode();
    }

    [InitializeOnLoadMethod]
    static void Register()
    {
        EditorApplication.playModeStateChanged += state =>
        {
            if (state == PlayModeStateChange.EnteredPlayMode && SessionState.GetBool("FrameLabSmokeTest", false))
            {
                SessionState.SetBool("FrameLabSmokeTest", false);
                new GameObject("Session smoke test").AddComponent<FrameLabSmokeRunner>();
            }
        };
    }
}

public class FrameLabSmokeRunner : MonoBehaviour
{
    bool failed;
    [Serializable] class DoorChecks { public DoorCheck[] doors; }
    [Serializable] class DoorCheck { public string name; public Vector3 position, normal; public float clear_width_m, height_m; public bool storage; }
    [Serializable] class ReviewShot { public string file, title, category; public Vector3 position, target; public float fieldOfView; }
    [Serializable] class ReviewSet { public ReviewShot[] shots; }
    [Serializable] class GlazingChecks { public GlazingSample[] glazing_samples; }
    [Serializable] class GlazingSample { public string window; public Vector3 position, direction; }

    void OnEnable() => Application.logMessageReceived += HandleLog;
    void OnDisable() => Application.logMessageReceived -= HandleLog;

    void HandleLog(string message, string stack, LogType type)
    {
        // This known batch-editor indexing failure is outside the player and tested scene.
        // Keep it visible separately; do not mask any gameplay or rendering exceptions.
        if (type == LogType.Exception && stack.Contains("UnityEditor.Search.SearchDatabase") &&
            stack.Contains("UnityEditor.Search.SearchInit.IndexationOnStartup"))
        {
            File.AppendAllText("Builds/Preview/editor-indexing-warning.txt", message + "\n" + stack + "\n");
            return;
        }
        if (type == LogType.Exception || type == LogType.Error || type == LogType.Assert) failed = true;
    }

    IEnumerator Start()
    {
        yield return null;
        yield return null;
        yield return new WaitForSecondsRealtime(0.8f);
        var session = FindAnyObjectByType<FrameLabSession>();
        Require(session != null, "Session exists");
        session.rig.CameraFloorOffsetObject.transform.localPosition = Vector3.up * 1.65f;
        session.rig.Camera.transform.localPosition = Vector3.zero;
        session.Guide.Place();
        var doors = JsonUtility.FromJson<DoorChecks>(File.ReadAllText("Assets/FrameLab/Models/opening-clearances.json"));
        foreach (var door in doors.doors)
        {
            if (door.storage)
            {
                // Storage has shelves and vertical dividers behind its opening;
                // it is not a walking destination. Keep the finished opening clear.
                Vector3 side = Vector3.Cross(Vector3.up, door.normal);
                foreach (float u in new[] { -.5f * door.clear_width_m + .08f, 0, .5f * door.clear_width_m - .08f })
                    foreach (float height in new[] { .15f, 1.1f, 2.2f })
                    {
                        Vector3 centre = door.position + side * u + Vector3.up * height;
                        Require(!Physics.Raycast(centre - door.normal * .065f, door.normal, .13f, 1 << 8),
                            "Storage aperture clearance " + door.name + " height=" + height + " offset=" + u);
                    }
                continue;
            }
            foreach (float offset in new[] { -.18f, 0, .18f })
            {
                Vector3 foot = door.position + door.normal * offset;
                var hits = Physics.OverlapCapsule(foot + Vector3.up * .35f, foot + Vector3.up * 1.95f, .25f, 1 << 8, QueryTriggerInteraction.Ignore);
                Require(hits.Length == 0, "Doorway clearance " + door.name + " offset=" + offset + "; " + string.Join(",", Array.ConvertAll(hits, hit => hit.name)));
                Require(Physics.Raycast(foot + Vector3.up * .08f, Vector3.down, .12f, 1 << 8), "Continuous threshold floor " + door.name);
            }
            if (door.name.Contains("Bed 5 door") || door.name.Contains("Bathroom door"))
            {
                float scheduled = door.name.Contains("Bed 5 door") ? .826f : .726f;
                Require(Mathf.Abs(door.clear_width_m - scheduled) < .001f, "Scheduled leaf plus side reveals " + door.name);
                Require(Mathf.Abs(door.height_m - 2.346f) < .001f, "Door head above finished deck " + door.name);
                Vector3 side = Vector3.Cross(Vector3.up, door.normal);
                foreach (float height in new[] { .15f, 1.1f, 2.28f })
                    foreach (float offset in new[] { -.5f * scheduled + .08f, 0, .5f * scheduled - .08f })
                    {
                        Vector3 point = door.position + Vector3.up * height + side * offset;
                        Require(!Physics.Raycast(point + door.normal * .18f, -door.normal, .23f, 1 << 8),
                            "Finished portal ray grid " + door.name + " height=" + height + " offset=" + offset);
                    }
            }
        }
        Require(session.Guide.HasClearPlacement(), "Welcome guide has clear geometry and sight lines");
        // Cast through the actual imported model from both sides of W03/W10.
        // A stud, steel post or incorrectly patched wall must not replace glass.
        var glazingChecks = JsonUtility.FromJson<GlazingChecks>(File.ReadAllText("Assets/FrameLab/Models/powder-window-coordination.json"));
        Require(glazingChecks.glazing_samples.Length == 60, "Both registered windows sampled from both sides");
        foreach (var sample in glazingChecks.glazing_samples)
                    {
                        bool found = Physics.Raycast(sample.position, sample.direction, out var hit, .7f, 1 << 8);
                        var surface = found ? hit.collider.GetComponent<MeshRenderer>() : null;
                        Require(surface != null && surface.sharedMaterial.HasProperty("_Surface") &&
                            surface.sharedMaterial.GetFloat("_Surface") > .5f,
                            "Clear imported glazing " + sample.window + " at=" + sample.position);
                    }
        session.HandleMenuInput(false); session.HandleMenuInput(true);
        Require(!session.Guide.IsVisible, "A press hides guide");
        session.HandleMenuInput(true);
        Require(!session.Guide.IsVisible, "Holding A does not repeat toggle");
        session.HandleMenuInput(false); session.HandleMenuInput(true); session.HandleMenuInput(false);
        Require(session.Guide.IsVisible && session.Guide.HasClearPlacement(), "A release and press recalls clear guide");
        Require(session.lighting.wallsShown.colors.Length > 0 && session.lighting.wallsHidden.colors.Length > 0, "Both lighting states baked");
        Require(session.lighting.wallsShownRoofHidden.colors.Length > 0 && session.lighting.wallsHiddenRoofHidden.colors.Length > 0, "Both roof-hidden lighting states baked");
        Require(Vector3.Dot(-RenderSettings.sun.transform.forward, new Vector3(.401196f,.585237f,.704656f)) > .99999f,
            "Scene sun matches the declared Leichhardt 15:00 site reference");
        var roomReflections = FindObjectsByType<ReflectionProbe>(FindObjectsSortMode.None);
        Require(roomReflections.Length == 5, "Five static interior reflection probes");
        foreach (var probe in roomReflections)
            Require(probe.mode == UnityEngine.Rendering.ReflectionProbeMode.Custom && probe.customBakedTexture != null,
                "Offline reflection texture retained: " + probe.name);
        var ground = GameObject.Find("Plain ground").GetComponent<MeshRenderer>();
        foreach (var state in new[] { session.lighting.wallsShown, session.lighting.wallsHidden,
            session.lighting.wallsShownRoofHidden, session.lighting.wallsHiddenRoofHidden,
            session.lighting.emptyWallsShown, session.lighting.emptyWallsHidden,
            session.lighting.emptyWallsShownRoofHidden, session.lighting.emptyWallsHiddenRoofHidden })
        {
            var surface = Array.Find(state.surfaces, item => item.renderer == ground);
            Require(surface != null && surface.index >= 0 && surface.index < state.colors.Length,
                "Ground receives baked lighting/shadows in each visibility state");
        }
        Require(LightmapSettings.lightmaps[0].lightmapColor == session.lighting.wallsShown.colors[0], "Enclosed lighting is active on entry");
        Require(session.fittings.groups.Length == 6 && session.stairPaintedStructure.Length > 0, "Six fittings groups and structural stair surfaces mapped");
        session.Guide.ShowFittings(true); ValidateText(session);
        for (int group = 0; group < session.fittings.groups.Length; group++)
        {
            var button = Array.Find(session.Guide.Panel.GetComponentsInChildren<UnityEngine.UI.Button>(true), b => b.name == "Fitting " + group + " button");
            Require(button != null, "Fittings button exists " + group); button.onClick.Invoke();
            Require(!session.fittings.groups[group].shown, "Button hides selected group " + group);
            for (int other = 0; other < session.fittings.groups.Length; other++)
                foreach (var surface in session.fittings.groups[other].surfaces)
                {
                    Require(surface.enabled == (other != group), "Independent fitting visibility " + group + "/" + other);
                    foreach (var collider in surface.GetComponents<Collider>()) Require(collider.enabled == surface.enabled, "Fitting collider follows visibility");
                    if (surface.enabled && surface.sharedMaterial.GetFloat("_Surface") < .5f)
                        Require(surface.lightmapIndex >= session.lighting.emptyWallsShown.colors.Length && surface.lightmapIndex < LightmapSettings.lightmaps.Length,
                            "Remaining fixture retains valid baked shading");
                }
            foreach (var surface in session.walls) Require(surface.enabled, "Fittings preserve walls and floor finishes");
            Require(LightmapSettings.lightmaps[0].lightmapColor == session.lighting.emptyWallsShown.colors[0], "Hidden fitting uses empty-room lighting");
            button.onClick.Invoke(); ValidateText(session);
        }
        session.SetAllFittings(false);
        foreach (var surface in session.fittings.Surfaces) Require(!surface.enabled, "Hide all fittings");
        session.ToggleFraming(); session.ToggleRoof();
        Require(LightmapSettings.lightmaps[0].lightmapColor == session.lighting.emptyWallsHiddenRoofHidden.colors[0], "Empty frame uses matching lighting");
        foreach (var surface in session.stairPaintedStructure)
            Require(surface.enabled && surface.sharedMaterial == session.stairTimberMaterial, "Walls hidden expose timber stair structure");
        foreach (var surface in session.walls) Require(!surface.enabled, "Stair finishes and walls are hidden together");
        session.ToggleFraming(); session.ToggleRoof();
        foreach (var surface in session.stairPaintedStructure) Require(surface.sharedMaterial == session.stairFinishMaterial, "Stair painted finish restored");
        session.SetAllFittings(true); session.Guide.ShowFittings(false);
        ValidateText(session);
        Require(session.IsSpeaking && session.GetComponent<AudioSource>().clip == session.tour.rooms[0].audio, "Introduction starts automatically");
        foreach (var stop in session.tour.rooms) Require(stop.audio != null && stop.audio.length > 5, "Room narration: " + stop.id);
        foreach (var stop in session.tour.studies) Require(stop.audio != null && stop.audio.length > 5, "Study narration: " + stop.id);
        session.ToggleFitting(2);
        for (int i = 1; i < session.destinations.Length; i++)
        {
            session.Next();
            yield return new WaitForSecondsRealtime(0.5f);
            Require(!session.IsChanging && session.Location == i, "Next reaches room " + i);
            if (i == 1)
            {
                Require(!session.fittings.groups[2].shown, "Fitting choice persists between rooms");
                session.ToggleFitting(2);
            }
            Vector3 head = session.rig.Camera.transform.position - Vector3.up * session.rig.CameraInOriginSpaceHeight;
            Require(Vector3.Distance(head, session.destinations[i].position) < 0.02f, "Tracked head reaches floor at room " + i);
            Require(session.GetComponent<AudioSource>().clip == session.tour.rooms[i].audio && session.IsSpeaking, "Arrival narration at room " + i);
            ValidateText(session);
            Require(session.Guide.HasClearPlacement(), "Enclosed guide clear in room " + session.Current.id);
            session.ToggleFraming();
            Require(session.Guide.HasClearPlacement(), "Exposed guide clear in room " + session.Current.id);
            session.ToggleFraming();
        }
        session.ToggleFraming();
        Require(session.IsFraming, "Frame reveal enabled");
        Require(LightmapSettings.lightmaps[0].lightmapColor == session.lighting.wallsHidden.colors[0], "Hidden walls swap to exposed lighting");
        foreach (var surface in session.walls)
        {
            Require(!surface.enabled, "Enclosure hidden");
            foreach (var collider in surface.GetComponents<Collider>()) Require(!collider.enabled, "Hidden enclosure collision disabled");
        }
        foreach (var surface in session.roof) Require(surface.enabled, "Walls do not toggle roof");
        session.ToggleRoof();
        Require(LightmapSettings.lightmaps[0].lightmapColor == session.lighting.wallsHiddenRoofHidden.colors[0], "Roof and walls hidden use matching baked shadows");
        session.ToggleFraming();
        Require(LightmapSettings.lightmaps[0].lightmapColor == session.lighting.wallsShownRoofHidden.colors[0], "Roof alone hidden uses matching baked shadows");
        session.ToggleRoof(); session.ToggleFraming();
        foreach (var surface in session.building.GetComponentsInChildren<MeshRenderer>())
            if (surface.name.StartsWith("28")) Require(surface.enabled && surface.GetComponent<Collider>().enabled, "Upper floor remains present");
        session.Next();
        yield return new WaitForSecondsRealtime(0.6f);
        Require(session.IsInDetail && session.detail.activeSelf && !session.building.activeSelf, "Detail transition");
        ValidateText(session);
        Vector3 panelDirection = Vector3.ProjectOnPlane(session.Guide.Panel.position - session.rig.Camera.transform.position, Vector3.up);
        Require(Vector3.Angle(panelDirection, session.detailDestination.forward) > 45, "Guide docks clear of window centre");
        session.Guide.Toggle();
        Require(!session.Guide.IsVisible, "Guide hides without a floating corner button");
        session.Guide.Toggle();
        Require(session.Guide.IsVisible, "Guide can be recalled");
        session.Next();
        Require(session.IsExploded, "Window layers separate");
        var layers = session.detail.GetComponentsInChildren<MeshRenderer>();
        for (int i = 0; i < layers.Length; i++)
        for (int j = i + 1; j < layers.Length; j++)
            Require(!session.inspection.LocalBounds(layers[i]).Intersects(session.inspection.LocalBounds(layers[j])), "Exploded layer bounds do not overlap");
        var inspection = session.inspection;
        Require(inspection.HotspotCount == 9 && inspection.VisiblePartCount == 9, "Nine inspectable components and hotspots");
        var sliders = session.Guide.Panel.GetComponentsInChildren<UnityEngine.UI.Slider>();
        var slider = Array.Find(sliders, s => s.name == "Explosion slider");
        var rotationSlider = Array.Find(sliders, s => s.name == "Rotation slider");
        Require(slider != null, "Inspection slider is present");
        Require(rotationSlider != null && rotationSlider.minValue == -180 && rotationSlider.maxValue == 180, "Rotation slider covers a full turn");
        slider.value = .45f;
        Require(Mathf.Abs(inspection.Explosion - .45f) < .001f, "Slider sets intermediate explosion");
        inspection.Zoom(1.15f); inspection.Rotate(30);
        Require(inspection.ZoomLevel > 1.1f && Quaternion.Angle(inspection.transform.rotation, inspection.HomeRotation) > 29, "Inspection zoom and rotation change the whole model");
        foreach (float degrees in new[] { -180f, -90f, 0f, 90f, 180f })
        {
            rotationSlider.value = degrees;
            Require(Mathf.Abs(inspection.RotationDegrees - degrees) < .01f &&
                Quaternion.Angle(inspection.transform.rotation, Quaternion.AngleAxis(degrees, Vector3.up) * inspection.HomeRotation) < .01f,
                "Rotation slider sets absolute angle " + degrees);
            Require(Mathf.Abs(inspection.Explosion - .45f) < .001f && inspection.ZoomLevel > 1.1f,
                "Rotation preserves explosion and zoom at " + degrees);
        }
        for (int i = 0; i < inspection.parts.Length; i++)
        {
            inspection.SelectPart(i); inspection.ToggleIsolation();
            Require(inspection.IsIsolated && inspection.VisiblePartCount == 1 && inspection.parts[i].surface.enabled, "Isolate component " + i);
            Require(inspection.Current.audio != null && session.IsSpeaking && session.GetComponent<AudioSource>().clip == inspection.Current.audio, "Hotspot narration " + i);
            Vector3 isolatedCentre = inspection.Current.surface.bounds.center;
            rotationSlider.value = i % 2 == 0 ? -90 : 90;
            Require(Vector3.Distance(isolatedCentre, inspection.Current.surface.bounds.center) < .001f,
                "Rotation pivots on isolated component " + i);
            ValidateText(session); inspection.ShowAll();
        }
        session.ToggleNarration(); inspection.SelectPart(1);
        Require(!session.IsSpeaking, "Component narration respects mute"); session.ToggleNarration();
        inspection.ResetAll();
        Require(!session.IsExploded && inspection.VisiblePartCount == 9 && inspection.Selected == -1 &&
            Mathf.Abs(inspection.ZoomLevel - 1) < .001f && Vector3.Distance(inspection.transform.position, inspection.HomePosition) < .001f &&
            Quaternion.Angle(inspection.transform.rotation, inspection.HomeRotation) < .01f && rotationSlider.value == 0,
            "Reset restores complete inspection pose and assembly and centres rotation slider");
        // Exercise the same XRI grab transformer used by controller grip selection.
        var hand = new GameObject("Inspection test hand");
        hand.transform.position = inspection.transform.position + Vector3.back;
        hand.AddComponent<SphereCollider>().isTrigger = true;
        var rb = hand.AddComponent<Rigidbody>(); rb.isKinematic = true; rb.useGravity = false;
        var interactor = hand.AddComponent<XRDirectInteractor>();
        yield return null;
        interactor.StartManualInteraction((IXRSelectInteractable)inspection.grab);
        yield return new WaitForSecondsRealtime(.2f);
        Vector3 beforeGrab = inspection.transform.position;
        Quaternion beforeRotation = inspection.transform.rotation;
        hand.transform.position += new Vector3(.3f, .2f, 0); hand.transform.Rotate(0, 25, 0);
        yield return new WaitForSecondsRealtime(.3f);
        Require(Vector3.Distance(beforeGrab, inspection.transform.position) > .15f && Quaternion.Angle(beforeRotation, inspection.transform.rotation) > 15, "Grip grab moves and rotates whole assembly");
        Require(Mathf.Abs(rotationSlider.value - inspection.RotationDegrees) < .01f && Mathf.Abs(rotationSlider.value) > 15,
            "Rotation slider follows hand rotation without callback feedback");
        interactor.EndManualInteraction(); Destroy(hand); inspection.ResetAll();
        session.SetExplosionAmount(1);
        session.ToggleExploded();
        session.ReplayNarration();
        Require(session.GetComponent<AudioSource>().clip != null, "Offline narration loaded");
        session.Next();
        session.Next();
        yield return new WaitForSecondsRealtime(0.6f);
        Require(session.Study == 2 && !session.IsInDetail && session.IsSpeaking, "Tour finishes with completion narration");
        session.ToggleNarration();
        session.GoTo(4);
        yield return new WaitForSecondsRealtime(0.6f);
        Require(!session.IsSpeaking, "Mute persists on room changes");
        session.ToggleNarration();
        session.SetAllFittings(false);
        session.ResetSession();
        yield return new WaitForSecondsRealtime(0.6f);
        Require(!session.IsInDetail && !session.IsFraming && !session.IsChanging, "Reset restores session state");
        Require(session.IsSpeaking && session.Location == 0, "Restart returns to narrated introduction");
        foreach (var surface in session.enclosure) Require(surface.enabled, "Reset restores enclosure");
        foreach (var surface in session.fittings.Surfaces) Require(surface.enabled && surface.GetComponent<Collider>().enabled, "Restart restores every fitting");
        Directory.CreateDirectory("Builds/Preview");
        FrameLabBuild.RenderPreview(session.rig.Camera, new Vector3(-29.1f, 1.65f, -5.33f),
            new Vector3(-20, 1.5f, -5.33f), "session.png");
        FrameLabBuild.RenderPreview(session.rig.Camera, new Vector3(-35, 13, 15), new Vector3(-15, 2, -4), "overview.png");
        FrameLabBuild.RenderPreview(session.rig.Camera, new Vector3(-14.5f, 1.65f, -3), new Vector3(-20, 1.4f, -5), "interior.png");
        FrameLabBuild.RenderPreview(session.rig.Camera, new Vector3(-26.2f, 1.65f, -7.12f), new Vector3(-22.3f, 2.1f, -7.12f), "staircase.png");
        FrameLabBuild.RenderPreview(session.rig.Camera, new Vector3(-20.45f, 4.809f, -7.2f), new Vector3(-23.0f, 2.5f, -7.2f), "staircase-landing.png");
        FrameLabBuild.RenderPreview(session.rig.Camera, new Vector3(-3, 1.65f, -5.8f), new Vector3(-5, 2.2f, -8), "garage.png");
        FrameLabBuild.RenderPreview(session.rig.Camera, new Vector3(-15.1f, 1.65f, -1.8f), new Vector3(-10.8f, 1.2f, -3.4f), "alfresco.png");
        FrameLabBuild.RenderPreview(session.rig.Camera, new Vector3(-25.7f, 4.809f, -2.4f), new Vector3(-23.6f, 3.9f, -1.8f), "theatre.png");
        session.ToggleFraming();
        session.ToggleRoof();
        FrameLabBuild.RenderPreview(session.rig.Camera, new Vector3(-25.5f, 1.65f, -5.7f), new Vector3(-22.3f, 2.1f, -7.1f), "staircase-framing.png");
        FrameLabBuild.RenderPreview(session.rig.Camera, new Vector3(-31, 5.5f, 8), new Vector3(-17, 3, -3), "framing.png");
        session.ToggleFraming();
        session.ToggleRoof();
        session.ToggleDetail();
        yield return new WaitForSecondsRealtime(0.6f);
        FrameLabBuild.RenderPreview(session.rig.Camera, new Vector3(10, 1.65f, 6.5f), new Vector3(10, 1.65f, 10), "window-guide.png");
        FrameLabBuild.RenderPreview(session.rig.Camera, session.rig.Camera.transform.position,
            session.Guide.Panel.position, "guide-readable.png");
        session.SetExplosionAmount(1); yield return null;
        FrameLabBuild.RenderPreview(session.rig.Camera, new Vector3(10, 1.65f, 6.5f), new Vector3(10, 1.3f, 10), "window-exploded.png");
        inspection.SelectPart(3); inspection.ToggleIsolation(); yield return null;
        FrameLabBuild.RenderPreview(session.rig.Camera, new Vector3(10, 1.65f, 7.2f), new Vector3(10, 1.3f, 10), "window-isolated.png");
        // Clean, labelled review photographs from the actual baked Unity scene.
        session.ResetSession(); yield return new WaitForSecondsRealtime(.6f);
        if (session.Guide.IsVisible) session.Guide.Toggle();
        Directory.CreateDirectory("Builds/Preview/Review");
        var shots = new List<ReviewShot>();
        void Photograph(string file, string title, string category, Vector3 position, Vector3 target)
        {
            FrameLabBuild.RenderPreview(session.rig.Camera, position, target, "Review/" + file + ".png");
            shots.Add(new ReviewShot { file = file + ".png", title = title, category = category,
                position = position, target = target, fieldOfView = session.rig.Camera.fieldOfView });
        }
        Photograph("01-exterior-entry", "Entry and long elevation", "Exterior", new Vector3(-35,10,15), new Vector3(-15,2,-4));
        Photograph("02-exterior-alfresco", "Alfresco and garage end", "Exterior", new Vector3(-3,9,13), new Vector3(-15,2,-4));
        Photograph("03-exterior-rear-entry", "Rear elevation from entry end", "Exterior", new Vector3(-35,9,-20), new Vector3(-15,2,-4));
        Photograph("04-exterior-rear-garage", "Rear elevation from garage end", "Exterior", new Vector3(6,10,-18), new Vector3(-12,2,-4));
        Photograph("05-canopy-under", "Entry canopy fascia and underside", "Details", new Vector3(-30.5f,2.2f,-3.4f), new Vector3(-27.7f,2.7f,-6.1f));
        Photograph("06-canopy-top", "Entry canopy roof and gutter", "Details", new Vector3(-30,4.2f,-6.2f), new Vector3(-27.8f,2.9f,-6.2f));
        Photograph("07-alfresco-edge", "Alfresco fascia and soffit", "Details", new Vector3(-9.5f,2.1f,3), new Vector3(-9.5f,2.8f,-1.5f));
        Photograph("08-stairs", "Complete stair and wall-side string", "Details", new Vector3(-26.2f,1.65f,-7.12f), new Vector3(-22.3f,2.1f,-7.12f));
        Photograph("09-stair-junction", "Stair-to-wall junction close-up", "Details", new Vector3(-25.6f,1.4f,-7.3f), new Vector3(-23.8f,1.3f,-7.75f));
        Photograph("10-stair-landing", "Upper stair landing and balustrade", "Details", new Vector3(-20.45f,4.809f,-7.2f), new Vector3(-23,2.5f,-7.2f));
        for (int i = 0; i < session.tour.rooms.Length; i++)
        {
            var room = session.tour.rooms[i]; var point = session.destinations[i];
            Vector3 eye = point.position + Vector3.up * 1.65f;
            float field = session.rig.Camera.fieldOfView;
            session.rig.Camera.fieldOfView = 75;
            Vector3 forward = point.forward;
            // Version0.4.1 intentionally uses authored room directions. Keep
            // the original0.4.0 gallery as before evidence; no same-camera claim.
            if (i == 21) Photograph("room-22-" + room.id, room.title, "Rooms",new Vector3(-34,1.65f,9),new Vector3(-16,2,-4));
            else Photograph("room-" + (i+1).ToString("00") + "-" + room.id, room.title, "Rooms", eye, eye + forward * 4 - Vector3.up * .15f);
            session.rig.Camera.fieldOfView = field;
        }
        session.ToggleFraming(); session.ToggleRoof();
        if (session.Guide.IsVisible) session.Guide.Toggle();
        Photograph("33-frame-overview", "Frame with walls and roof hidden", "Structure", new Vector3(-31,5.5f,8), new Vector3(-17,3,-3));
        Photograph("34-frame-stairs", "Stair framing and floor connections", "Structure", new Vector3(-25.5f,1.65f,-5.7f), new Vector3(-22.3f,2.1f,-7.1f));
        session.ToggleFraming(); session.ToggleRoof();
        if (session.Guide.IsVisible) session.Guide.Toggle();
        float entryField = session.rig.Camera.fieldOfView;
        session.rig.Camera.fieldOfView = 100;
        Photograph("35-bedroom5-from-hall", "Bedroom 5 entry from hall", "Entries", new Vector3(-15.56f,4.809f,-3.55f), new Vector3(-15.56f,4.4f,-5.4f));
        session.rig.Camera.fieldOfView = 75;
        Photograph("36-bedroom5-from-room", "Bedroom 5 entry and completed return", "Entries", new Vector3(-16.4f,4.809f,-6.25f), new Vector3(-15.6f,4.4f,-4.52f));
        session.rig.Camera.fieldOfView = 100;
        Photograph("37-upperbath-from-hall", "Upper bathroom entry from hall", "Entries", new Vector3(-12.76f,4.809f,-3.55f), new Vector3(-12.76f,4.4f,-5.6f));
        session.rig.Camera.fieldOfView = 75;
        Photograph("38-upperbath-from-room", "Upper bathroom wall and ceiling junction", "Entries", new Vector3(-12.92f,4.809f,-6.25f), new Vector3(-12.75f,4.5f,-4.52f));
        session.rig.Camera.fieldOfView = 65;
        Photograph("39-powder-window", "Powder window and privacy glazing", "Details", new Vector3(-20.85f,1.45f,-6.4f), new Vector3(-21.1577f,1.4f,-7.925f));
        Photograph("40-upper-stair-window", "Coordinated upper stair window", "Details", new Vector3(-20.05f,4.6f,-6.4f), new Vector3(-20.2387f,4.5f,-7.925f));
        session.ToggleFraming(); session.ToggleRoof();
        if (session.Guide.IsVisible) session.Guide.Toggle();
        Photograph("41-window-pier-structure", "Retained C2 pier and connected head", "Structure", new Vector3(-21.6f,3.4f,-5.7f), new Vector3(-20.7087f,3.1f,-7.835f));
        session.ToggleFraming(); session.ToggleRoof();
        if (session.Guide.IsVisible) session.Guide.Toggle();
        session.rig.Camera.fieldOfView = 75;
        Photograph("42-kitchen-fitout", "Kitchen island, bench and bulkhead", "Fitout", new Vector3(-17.2f,1.65f,-4.3f), new Vector3(-15.4f,1.2f,-6.6f));
        Photograph("43-ensuite-fitout", "Ensuite vanity and shower", "Fitout", new Vector3(-19.72f,1.65f,-1.95f), new Vector3(-18.7f,1.25f,-2.35f));
        Photograph("44-laundry-fitout", "Laundry cabinetry and appliances", "Fitout", new Vector3(-7.6f,1.65f,-5.4f), new Vector3(-8.5f,1.2f,-6.6f));
        Photograph("45-bath2-fitout", "Bathroom 2 shower and fittings", "Fitout", new Vector3(-11.7f,4.809f,-.95f), new Vector3(-11.1f,4.3f,-1.7f));
        Photograph("46-upperbath-fitout", "Upper bathroom vanity and shower", "Fitout", new Vector3(-13.15f,4.809f,-5.65f), new Vector3(-14.0f,4.3f,-6.75f));
        Photograph("47-robe-fitout", "Main robe shelves and drawer towers", "Fitout", new Vector3(-21.6f,1.65f,-1.8f), new Vector3(-20.9f,1.3f,-3.3f));
        Photograph("48-powder-fitout", "Powder vanity and mirror", "Fitout", new Vector3(-21.07f,1.65f,-6.65f), new Vector3(-20.25f,1.2f,-6.1f));
        session.rig.Camera.fieldOfView = 70;
        Photograph("49-bedroom5-robe-check", "Bedroom 5 robe junction — original camera", "Details",new Vector3(-17.1f,4.809f,-6.2f),new Vector3(-14.271573f,4.659f,-3.371573f));
        Photograph("50-powder-door-check", "Powder doorway and corridor bulkhead — original camera", "Details",new Vector3(-21.07f,1.65f,-6.65f),new Vector3(-21.07f,1.5f,-2.65f));
        Photograph("51-bathroom-tile-floor", "Upper bathroom tile floor and shower junction", "Fitout",new Vector3(-12.90f,4.50f,-5.70f),new Vector3(-13.30f,3.162f,-6.80f));
        Photograph("52-bathroom-tile-return", "Upper bathroom tiled walls and doorway", "Fitout",new Vector3(-13.20f,4.80f,-7.05f),new Vector3(-12.95f,4.15f,-4.70f));
        Photograph("53-kitchen-cupboard-handles", "Kitchen overhead cupboard handles", "Fitout",new Vector3(-15.3f,1.58f,-6.25f),new Vector3(-15.3f,1.84f,-7.39f));
        Photograph("54-kitchen-pantry-handles", "Kitchen pantry handle height", "Fitout",new Vector3(-19.34f,1.55f,-6.10f),new Vector3(-19.34f,1.10f,-7.17f));
        session.rig.Camera.fieldOfView = 75;
        session.ToggleFitting(0);
        Photograph("55-kitchen-hidden", "Kitchen hidden — same camera as 42", "Visibility",new Vector3(-17.2f,1.65f,-4.3f),new Vector3(-15.4f,1.2f,-6.6f));
        session.ToggleFitting(0); session.ToggleFitting(4);
        Photograph("56-shower-hidden", "Shower hidden, vanity retained", "Visibility",new Vector3(-13.15f,4.809f,-5.65f),new Vector3(-14.0f,4.3f,-6.75f));
        session.SetAllFittings(false);
        Photograph("57-bathroom-fittings-hidden", "All fittings hidden, tiles retained", "Visibility",new Vector3(-13.15f,4.809f,-5.65f),new Vector3(-14.0f,4.3f,-6.75f));
        session.ToggleFraming(); session.ToggleRoof();
        Photograph("58-stair-timber-only", "Walls hidden — timber stair construction", "Visibility",new Vector3(-25.5f,1.65f,-5.7f),new Vector3(-22.3f,2.1f,-7.1f));
        session.ToggleFraming(); session.ToggleRoof(); session.SetAllFittings(true);
        Photograph("59-entry-void-lining", "Entry void floor-edge lining", "Photo corrections",new Vector3(-25.7f,1.7f,-6.1f),new Vector3(-25.5f,3.0f,-4.69f));
        Photograph("60-bedroom1-door-corner", "Bedroom corner clear of front door", "Photo corrections",new Vector3(-25.2f,1.6f,-3.3f),new Vector3(-26.88f,1.5f,-4.58f));
        Photograph("61-suite-door-jambs", "Suite passage and bedroom door junction", "Photo corrections",new Vector3(-24.1f,1.6f,-2.9f),new Vector3(-22.95f,1.5f,-4.25f));
        Photograph("62-laundry-linen", "Laundry linen divider and finished northern corner", "Photo corrections",new Vector3(-7.65f,1.6f,-6.2f),new Vector3(-6.49f,1.35f,-7.0f));
        Photograph("63-ensuite-shower-hardware", "Ensuite shower door and mixer", "Photo corrections",new Vector3(-19.85f,1.55f,-2.22f),new Vector3(-19.25f,1.25f,-3.65f));
        Photograph("64-wet-door-threshold", "Tiled threshold between ensuite and WC", "Photo corrections",new Vector3(-19.88f,1.3f,-1.6f),new Vector3(-19.88f,.01f,-1.035f));
        Photograph("65-lined-eave", "Bedroom 4 west window and lined eave", "Photo corrections",new Vector3(-7.5f,4.8f,-6.15f),new Vector3(-6.05f,5.5f,-6.15f));
        session.ToggleFraming(); session.ToggleRoof();
        Photograph("66-entry-perimeter-frame", "Continuous perimeter framing above entry void", "Photo corrections",new Vector3(-24.0f,1.65f,-4.9f),new Vector3(-24.0f,3.2f,-7.835f));
        session.ToggleFraming(); session.ToggleRoof();
        session.Guide.Show(); session.Guide.ShowFittings(true); session.Guide.Place();
        ValidateText(session);
        FrameLabBuild.RenderPreview(session.rig.Camera,session.rig.Camera.transform.position,session.Guide.Panel.position,"fittings-controls.png");
        session.Guide.ShowFittings(false); session.Guide.Toggle();
        session.rig.Camera.fieldOfView = entryField;
        File.WriteAllText("Builds/Preview/Review/manifest.json", JsonUtility.ToJson(new ReviewSet { shots = shots.ToArray() }, true));
        yield return null;
        yield return null;
        File.WriteAllText("Builds/Preview/session-tests.txt", failed ? "FAIL\n" : "PASS\n22 room arrivals, automatic narration, walls/roof, floor retention, window slider, separated-layer bounds, nine hotspots/audio/isolation, zoom/rotation/reset, XRI grab movement and rotation, full-panel room clearance with walls shown/hidden, A-button press/hold/release recall, completion, mute and restart.\n");
        Debug.Log(failed ? "FRAME_LAB_SMOKE_FAIL" : "FRAME_LAB_SMOKE_PASS");
        EditorApplication.Exit(failed ? 1 : 0);
    }

    static Vector3 ReviewDirection(Vector3 eye, Vector3 preferred)
    {
        Vector3 best = preferred; float bestScore = -1;
        for (int angle = 0; angle < 360; angle += 15)
        {
            Vector3 forward = Quaternion.Euler(0, angle, 0) * Vector3.forward;
            float score = 0;
            foreach (float offset in new[] { -40f, -25f, -10f, 0f, 10f, 25f, 40f })
            {
                var ray = Quaternion.Euler(0, offset, 0) * forward;
                float distance = Physics.Raycast(eye, ray, out var hit, 9, 1 << 8, QueryTriggerInteraction.Ignore) ? hit.distance : 9;
                score += Mathf.Min(distance, 7) * (offset == 0 ? 1.5f : 1);
                if (distance < .75f) score -= 4;
            }
            if (score > bestScore) { bestScore = score; best = forward; }
        }
        return best;
    }

    void Require(bool condition, string name)
    {
        if (condition) return;
        failed = true;
        Debug.LogError("Session test failed: " + name);
    }

    void ValidateText(FrameLabSession session)
    {
        Canvas.ForceUpdateCanvases();
        foreach (var label in session.Guide.Panel.GetComponentsInChildren<UnityEngine.UI.Text>())
            Require(label.preferredHeight <= label.rectTransform.rect.height + 2, "Guide text fits: " + session.Current.id + " / " + label.text.Substring(0, Math.Min(30, label.text.Length)));
    }
}
