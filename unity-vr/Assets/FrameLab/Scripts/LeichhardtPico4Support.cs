using System;
using System.Runtime.InteropServices;
using UnityEngine;
using UnityEngine.XR.OpenXR;
using UnityEngine.XR.OpenXR.Features;

namespace FrameLab
{
    // Use standard OpenXR on PICO OS 5.9.9. No calls into the newer PICO native SDK.
#if UNITY_EDITOR
    [UnityEditor.XR.OpenXR.Features.OpenXRFeature(
        UiName = "Leichhardt PICO 4 Enterprise (standard OpenXR)",
        BuildTargetGroups = new[] { UnityEditor.BuildTargetGroup.Android },
        Company = "EVOLVE Learning", Version = "1.0.0",
        OpenxrExtensionStrings = "XR_FB_display_refresh_rate",
        FeatureId = "au.edu.evolve.pico4.standard-openxr")]
#endif
    public sealed class LeichhardtPico4Support : OpenXRFeature
    {
        [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
        delegate int GetProcAddress(ulong instance, [MarshalAs(UnmanagedType.LPStr)] string name, out IntPtr function);
        [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
        delegate int EnumerateRates(ulong session, uint capacity, out uint count, [Out] float[] rates);
        [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
        delegate int RequestRate(ulong session, float rate);
        EnumerateRates enumerateRates;
        RequestRate requestRate;

        protected override bool OnInstanceCreate(ulong instance)
        {
            if (OpenXRRuntime.IsExtensionEnabled("XR_FB_display_refresh_rate"))
            {
                var getProc = Marshal.GetDelegateForFunctionPointer<GetProcAddress>(xrGetInstanceProcAddr);
                if (getProc(instance, "xrEnumerateDisplayRefreshRatesFB", out var enumerate) == 0 && enumerate != IntPtr.Zero)
                    enumerateRates = Marshal.GetDelegateForFunctionPointer<EnumerateRates>(enumerate);
                if (getProc(instance, "xrRequestDisplayRefreshRateFB", out var request) == 0 && request != IntPtr.Zero)
                    requestRate = Marshal.GetDelegateForFunctionPointer<RequestRate>(request);
            }
            Debug.Log("LEICHHARDT_PICO4_STANDARD_OPENXR runtime=" + OpenXRRuntime.name + " version=" + OpenXRRuntime.version);
            return true;
        }

        protected override void OnSessionBegin(ulong session)
        {
            // Refresh selection is optional. Unsupported refresh rates must never block startup.
            if (enumerateRates == null || requestRate == null ||
                enumerateRates(session, 0, out uint count, null) != 0 || count == 0 || count > 32)
            {
                Debug.LogWarning("LEICHHARDT_PICO4_REFRESH using runtime default; enumeration unavailable.");
                return;
            }
            var rates = new float[count];
            if (enumerateRates(session, count, out uint returned, rates) == 0)
                for (int i = 0; i < Math.Min(returned, count); i++)
                    if (Mathf.Abs(rates[i] - 72) < 0.1f)
                    {
                        Debug.Log("LEICHHARDT_PICO4_REFRESH requested=72 result=" + requestRate(session, 72));
                        return;
                    }
            Debug.LogWarning("LEICHHARDT_PICO4_REFRESH 72 Hz unavailable; retaining runtime default.");
        }

        protected override void OnInstanceDestroy(ulong instance)
        {
            enumerateRates = null;
            requestRate = null;
        }
    }
}
