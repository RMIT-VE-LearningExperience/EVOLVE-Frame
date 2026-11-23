using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR;

namespace FrameLab
{
    // Development-build diagnostics only; nothing is uploaded or shown in the lesson.
    public class FrameLabTelemetry : MonoBehaviour
    {
        readonly List<XRDisplaySubsystem> displays = new List<XRDisplaySubsystem>();
        readonly List<float> intervals = new List<float>(2000);
        float elapsed;
        float gpuSeconds;
        int gpuSamples;
        float started;

        void Start()
        {
            if (!Debug.isDebugBuild || !Application.isMobilePlatform) { enabled = false; return; }
            started = Time.realtimeSinceStartup;
            SubsystemManager.GetSubsystems(displays);
            Debug.Log("FRAME_LAB_TELEMETRY_STARTED " + Application.version);
        }

        void Update()
        {
            if (Time.realtimeSinceStartup - started < 5 || !Application.isFocused) return;
            XRDisplaySubsystem display = displays.Find(d => d.running);
            if (display == null) return;
            float delta = Time.unscaledDeltaTime;
            intervals.Add(delta * 1000);
            elapsed += delta;
            if (display.TryGetAppGPUTimeLastFrame(out float gpu) && gpu > 0)
            {
                gpuSeconds += gpu;
                gpuSamples++;
            }
            if (elapsed < 20) return;
            intervals.Sort();
            display.TryGetDisplayRefreshRate(out float refresh);
            Debug.Log(string.Format(System.Globalization.CultureInfo.InvariantCulture,
                "FRAME_LAB_METRICS frames={0} fps={1:F1} frame_p95_ms={2:F2} gpu_ms={3:F2} refresh_hz={4:F1}",
                intervals.Count, intervals.Count / elapsed,
                intervals[Math.Min(intervals.Count - 1, (int)(intervals.Count * 0.95f))],
                gpuSamples > 0 ? gpuSeconds / gpuSamples * 1000 : -1, refresh));
            intervals.Clear(); elapsed = 0; gpuSeconds = 0; gpuSamples = 0;
        }

        void OnApplicationPause(bool pause)
        {
            intervals.Clear(); elapsed = 0; gpuSeconds = 0; gpuSamples = 0;
            started = Time.realtimeSinceStartup;
        }
    }
}
