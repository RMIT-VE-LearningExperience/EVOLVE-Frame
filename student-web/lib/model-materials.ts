import * as T from 'three';

/** Procedural display finishes, not product specifications. No remote textures. */
export function displayMaterial(
  source: T.MeshStandardMaterial,
  kind: string,
  detailed: boolean,
) {
  const m = new T.MeshPhysicalMaterial({
    color: source.color,
    roughness: 0.7,
    metalness: 0,
    side: T.FrontSide,
  });
  m.name = source.name;
  if (kind === 'wood') {
    m.color.set('#c49b62');
    m.roughness = 0.8;
  }
  if (kind === 'brick') {
    m.color.set('#996345');
    m.roughness = 0.94;
  }
  if (kind === 'render') {
    m.color.set('#dedbd1');
    m.roughness = 0.9;
  }
  if (kind === 'metal') {
    m.metalness = 0.7;
    m.roughness = 0.32;
  }
  if (kind === 'glass') {
    m.color.set('#c4e0e4');
    m.roughness = 0.12;
    m.metalness = 0.05;
    m.ior = 1.45;
    if (detailed) {
      m.transmission = 0.78;
      m.thickness = 0.006;
    } else {
      m.transparent = true;
      m.opacity = 0.48;
    }
  }
  if (detailed && (kind === 'wood' || kind === 'brick')) {
    m.onBeforeCompile = (shader) => {
      shader.vertexShader =
        'varying vec3 vLabPosition;\nvarying vec2 vLabUV;\n' +
        shader.vertexShader;
      shader.vertexShader = shader.vertexShader.replace(
        '#include <worldpos_vertex>',
        '#include <worldpos_vertex>\nvLabPosition=(modelMatrix*vec4(transformed,1.0)).xyz; vLabUV=uv;',
      );
      shader.fragmentShader =
        'varying vec3 vLabPosition;\nvarying vec2 vLabUV;\n' +
        shader.fragmentShader;
      const finish =
        kind === 'wood'
          ? `
    float grainPhase=vLabUV.x*900.0+sin(vLabUV.y*7.0+vLabUV.x*31.0)*2.5;
    float grain=sin(grainPhase)*exp(-fwidth(grainPhase)*.6);
    diffuseColor.rgb*=.95+.075*grain;
   `
          : `
    vec2 brickCoord=vec2((vLabPosition.x+vLabPosition.z)/.23,vLabPosition.y/.086);
    float row=floor(brickCoord.y); brickCoord.x+=mod(row,2.0)*.5;
    vec2 cell=fract(brickCoord), aa=max(fwidth(brickCoord),vec2(.001));
    vec2 joint=smoothstep(vec2(.018),vec2(.018)+aa,min(cell,1.0-cell));
    float brickMask=joint.x*joint.y;
    float variation=fract(sin(dot(floor(brickCoord),vec2(12.9898,78.233)))*43758.5453);
    diffuseColor.rgb=mix(vec3(.30,.29,.26),diffuseColor.rgb*(.87+.24*variation),brickMask);
   `;
      shader.fragmentShader = shader.fragmentShader.replace(
        '#include <color_fragment>',
        '#include <color_fragment>\n' + finish,
      );
    };
    m.customProgramCacheKey = () => `frame-lab-${kind}-v2`;
  }
  return m;
}
