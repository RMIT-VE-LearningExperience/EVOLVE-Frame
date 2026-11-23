#ifndef LEICHHARDT_PORCELAIN_INPUT
#define LEICHHARDT_PORCELAIN_INPUT
#define InitializeStandardLitSurfaceData InitializePorcelainBase
#include "Packages/com.unity.render-pipelines.universal/Shaders/LitInput.hlsl"
#undef InitializeStandardLitSurfaceData

inline void InitializeStandardLitSurfaceData(float2 uv, out SurfaceData surface)
{
    InitializePorcelainBase(uv, surface);
    // UVs are metre-based in the model, scaled by the material's 600 mm module.
    // _Parallax is the existing Lit buffer field, relabelled as tile height.
    // No height/parallax mapping, extra texture samples or runtime lights.
    float2 moduleSize = float2(0.6, _Parallax);
    float2 cell = floor(uv);
    float2 f = frac(uv);
    float2 edge = min(f, 1-f) * moduleSize;
    float aa = max(0.00015, max(fwidth(uv.x)*moduleSize.x, fwidth(uv.y)*moduleSize.y)*0.65);
    float tile = smoothstep(0.00125-aa, 0.00125+aa, min(edge.x,edge.y));
    float variation = frac(sin(dot(cell,float2(127.1,311.7)))*43758.5453);
    // Quiet ceramic variation avoids the checkerboard/paving appearance.
    half3 porcelain = surface.albedo * lerp(0.985,1.015,variation);
    half3 grout = surface.albedo * 0.84;
    surface.albedo = lerp(grout,porcelain,tile);
    surface.smoothness *= lerp(0.3,1.0,tile);
    surface.metallic = 0;
}
#endif
