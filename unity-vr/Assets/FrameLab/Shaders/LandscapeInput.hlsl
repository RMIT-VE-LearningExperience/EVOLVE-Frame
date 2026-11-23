#ifndef FRAME_LAB_LANDSCAPE_INPUT
#define FRAME_LAB_LANDSCAPE_INPUT
#define InitializeStandardLitSurfaceData InitializeLandscapeBase
#include "Packages/com.unity.render-pipelines.universal/Shaders/LitInput.hlsl"
#undef InitializeStandardLitSurfaceData

float LandscapeHash(float2 p)
{
    return frac(sin(dot(p, float2(127.1, 311.7))) * 43758.5453);
}

float LandscapeNoise(float2 p)
{
    float2 cell = floor(p);
    float2 f = frac(p);
    f = f * f * (3.0 - 2.0 * f);
    return lerp(lerp(LandscapeHash(cell), LandscapeHash(cell + float2(1,0)), f.x),
        lerp(LandscapeHash(cell + float2(0,1)), LandscapeHash(cell + 1), f.x), f.y);
}

inline void InitializeStandardLitSurfaceData(float2 uv, out SurfaceData surface)
{
    InitializeLandscapeBase(uv, surface);
    // Broad colour variation breaks repetition without grass cards or extra draws.
    float variation = LandscapeNoise(uv * 0.07) * 0.7 + LandscapeNoise(uv * 0.23 + 9) * 0.3;
    half3 meadow = lerp(half3(0.14, 0.21, 0.10), half3(0.25, 0.31, 0.15), variation);
    surface.albedo = lerp(meadow, surface.albedo * half3(0.82, 1.08, 0.82), 0.45);
    surface.smoothness = 0.05;
}
#endif
