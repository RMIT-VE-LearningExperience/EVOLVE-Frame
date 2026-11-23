import { DirectionalLight, HemisphereLight, PCFShadowMap } from 'three';

export const shadowType = PCFShadowMap;
export const environmentIntensity = 0.8;
export function studyLights(detailed: boolean) {
  const sky = new HemisphereLight(0xe6ecff, 0x81756c, 1.05);
  const sun = new DirectionalLight(0xfff2e5, 2.0);
  sun.castShadow = detailed;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.radius = 4;
  sun.shadow.intensity = 0.65;
  sun.shadow.normalBias = 0.012;
  sun.shadow.bias = -0.00012;
  return { sky, sun };
}
