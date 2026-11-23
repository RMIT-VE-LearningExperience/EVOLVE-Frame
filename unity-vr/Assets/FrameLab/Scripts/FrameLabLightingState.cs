using System;
using UnityEngine;

namespace FrameLab
{
    // Each wall/roof combination has its own baked lighting and soft shadows.
    public class FrameLabLightingState : MonoBehaviour
    {
        [Serializable] public class Surface
        {
            public Renderer renderer;
            public int index;
            public Vector4 scaleOffset;
        }
        [Serializable] public class State
        {
            public Texture2D[] colors;
            public Surface[] surfaces;
        }
        public State wallsShown, wallsHidden, wallsShownRoofHidden, wallsHiddenRoofHidden;
        public State emptyWallsShown, emptyWallsHidden, emptyWallsShownRoofHidden, emptyWallsHiddenRoofHidden;
        public ReflectionProbe[] reflectionProbes;
        public Cubemap[] furnishedReflections, emptyReflections;
        void Start() => Apply(true);
        public void Apply(bool shown, bool roofShown = true, bool anyFittingsHidden = false)
        {
            State furnished = roofShown ? (shown ? wallsShown : wallsHidden) : (shown ? wallsShownRoofHidden : wallsHiddenRoofHidden);
            State state = anyFittingsHidden ? (roofShown ? (shown ? emptyWallsShown : emptyWallsHidden) :
                (shown ? emptyWallsShownRoofHidden : emptyWallsHiddenRoofHidden)) : furnished;
            if (state == null || state.colors == null || state.colors.Length == 0) return;
            // Mixed selections use the empty-room shell plus each remaining
            // fitting's original shading. This avoids 64 combinations per room.
            int extra = anyFittingsHidden ? furnished.colors.Length : 0;
            var maps = new LightmapData[state.colors.Length + extra];
            for (int i = 0; i < state.colors.Length; i++) maps[i] = new LightmapData { lightmapColor = state.colors[i] };
            for (int i = 0; i < extra; i++) maps[state.colors.Length+i] = new LightmapData { lightmapColor = furnished.colors[i] };
            LightmapSettings.lightmapsMode = LightmapsMode.NonDirectional;
            LightmapSettings.lightmaps = maps;
            foreach (var surface in state.surfaces)
            {
                surface.renderer.lightmapIndex = surface.index;
                surface.renderer.lightmapScaleOffset = surface.scaleOffset;
            }
            if (anyFittingsHidden)
                foreach (var surface in furnished.surfaces)
                    if (surface.renderer != null && int.TryParse(surface.renderer.name.Substring(0, Math.Min(2, surface.renderer.name.Length)), out int group) && group >= 30 && group <= 35)
                    {
                        surface.renderer.lightmapIndex = surface.index >= 0 && surface.index < furnished.colors.Length ? surface.index + state.colors.Length : -1;
                        surface.renderer.lightmapScaleOffset = surface.scaleOffset;
                    }
            if (reflectionProbes != null)
                for (int i = 0; i < reflectionProbes.Length; i++)
                {
                    reflectionProbes[i].enabled = shown && roofShown;
                    var textures = anyFittingsHidden ? emptyReflections : furnishedReflections;
                    if (textures != null && i < textures.Length) reflectionProbes[i].customBakedTexture = textures[i];
                }
        }
    }
}
