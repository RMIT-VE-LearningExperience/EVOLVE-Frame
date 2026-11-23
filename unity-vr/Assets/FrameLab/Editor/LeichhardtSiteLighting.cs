using System;
using System.IO;
using UnityEditor;
using UnityEngine;

// Architectural sheet 03: north points left/down, rotated by the boundary
// bearing 05d24m40s. Import mapping: Blender (x,y,z) -> Unity (-x,z,-y).
// Reference: 15 Leichhardt Avenue, Burnside Heights, -37.7329067, 144.7542880.
// Sheets 26-32 specify 22 September. 2026 and 15:00 AEST are declared defaults.
// Solar values use NOAA's published equations; evidence and assumptions are in
// output/vr/architectural-review-2026-11-20/sun-orientation-audit.json.
public static class LeichhardtSiteLighting
{
    public const float NorthBearingDegrees = 5f + 24f / 60f + 40f / 3600f;
    public const float DefaultAzimuthDegrees = 305.066f;
    public const float DefaultElevationDegrees = 35.820f;

    public static Vector3 DirectionToSun(float azimuthDegrees, float elevationDegrees)
    {
        float bearing = NorthBearingDegrees * Mathf.Deg2Rad;
        var north = new Vector3(Mathf.Cos(bearing), 0, Mathf.Sin(bearing));
        var east = new Vector3(Mathf.Sin(bearing), 0, -Mathf.Cos(bearing));
        float azimuth = azimuthDegrees * Mathf.Deg2Rad;
        float elevation = elevationDegrees * Mathf.Deg2Rad;
        return (Mathf.Cos(elevation) * (north * Mathf.Cos(azimuth) + east * Mathf.Sin(azimuth))
            + Vector3.up * Mathf.Sin(elevation)).normalized;
    }

    public static void Configure(Light sun)
    {
        if (sun == null) throw new ArgumentNullException(nameof(sun));
        sun.name = "Leichhardt sun - 22 September 15:00 AEST";
        sun.type = LightType.Directional;
        // Unity light.forward is the direction the rays travel, away from the sun.
        sun.transform.rotation = Quaternion.LookRotation(
            -DirectionToSun(DefaultAzimuthDegrees, DefaultElevationDegrees), Vector3.up);
    }

    [MenuItem("Leichhardt/Verify site sun orientation")]
    public static void Verify()
    {
        var morning = DirectionToSun(60.959f, 31.152f);
        var noon = DirectionToSun(5.511f, 51.499f);
        var afternoon = DirectionToSun(DefaultAzimuthDegrees, DefaultElevationDegrees);
        Require(Vector3.Distance(morning, new Vector3(.484145f, .517309f, -.705688f)) < .0001f, "09:00 reference");
        Require(Vector3.Distance(noon, new Vector3(.622526f, .782598f, -.001083f)) < .0001f, "12:00 reference");
        Require(Vector3.Distance(afternoon, new Vector3(.401196f, .585237f, .704656f)) < .0001f, "15:00 reference");
        // Plan shadow diagrams: morning right/down, noon right, afternoon right/up.
        // Unity shadow x/z -> drawing right/up = -x/-z.
        Require(morning.x > 0 && morning.z < 0, "sheet 26 morning shadow quadrant");
        Require(noon.x > 0 && Mathf.Abs(noon.z) < .005f, "sheet 29 noon shadow direction");
        Require(afternoon.x > 0 && afternoon.z > 0, "sheet 32 afternoon shadow quadrant");
        var probe = new GameObject("Site sun verification").AddComponent<Light>();
        try
        {
            Configure(probe);
            Require(Vector3.Dot(probe.transform.forward, -afternoon) > .99999f, "light ray direction");
            Require(probe.transform.forward.y < 0, "sun casts toward the ground");
        }
        finally { UnityEngine.Object.DestroyImmediate(probe.gameObject); }
        const string report = "PASS: Leichhardt site sun. 8 checks: 09:00/12:00/15:00 numerical references, "
            + "three drawing shadow directions, Unity light ray direction and ground-facing rays. "
            + "Default 22 September 2026 15:00 AEST; azimuth 305.066 deg, elevation 35.820 deg. "
            + "Source configuration checked; scene rebake and headset appearance remain pending.";
        Directory.CreateDirectory("Builds/Preview");
        File.WriteAllText("Builds/Preview/site-sun-verification.txt", report);
        Debug.Log(report);
    }

    private static void Require(bool condition, string check)
    {
        if (!condition) throw new InvalidOperationException("Site sun failed: " + check);
    }
}
