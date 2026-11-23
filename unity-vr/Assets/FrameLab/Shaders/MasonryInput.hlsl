#ifndef FRAME_LAB_MASONRY_INPUT
#define FRAME_LAB_MASONRY_INPUT
#define InitializeStandardLitSurfaceData InitializeMasonryBase
#include "Packages/com.unity.render-pipelines.universal/Shaders/LitInput.hlsl"
#undef InitializeStandardLitSurfaceData

inline void InitializeStandardLitSurfaceData(float2 uv, out SurfaceData surface)
{
    InitializeMasonryBase(uv, surface);
    // Metre-based running bond: 230 x 76 mm brick with nominal 10 mm joints.
    float row = floor(uv.y / 0.086);
    float2 grid = float2(uv.x / 0.24 + frac(row * 0.5), uv.y / 0.086);
    float2 cell = floor(grid);
    float2 f = frac(grid);
    float2 edge = min(f, 1 - f) * float2(0.24, 0.086);
    float aa = max(0.0003, max(fwidth(uv.x), fwidth(uv.y)) * 0.65);
    float brick = smoothstep(0.005 - aa, 0.0065 + aa, min(edge.x, edge.y));
    float variation = frac(sin(dot(cell, float2(127.1, 311.7))) * 43758.5453);
    half3 clay = surface.albedo * lerp(0.87, 1.04, variation);
    surface.albedo = lerp(half3(0.43, 0.44, 0.42), clay, brick);
    float2 bevel = (1 - smoothstep(0.005, 0.009, edge)) * step(0.004, edge);
    surface.normalTS = normalize(half3(bevel * sign(f - 0.5) * 0.25, 1));
    surface.metallic = 0;
    surface.smoothness = 0.12;
}
#endif
