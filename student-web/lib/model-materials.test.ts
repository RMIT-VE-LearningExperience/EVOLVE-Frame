import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  MeshStandardMaterial,
  ShaderLib,
  type WebGLProgramParametersWithUniforms,
  type WebGLRenderer,
} from 'three';
import { displayMaterial } from './model-materials.ts';
void test('finishes preserve the source material and distinguish glass quality modes', () => {
  const source = new MeshStandardMaterial({ color: 0x123456 });
  const glass = displayMaterial(source, 'glass', true),
    light = displayMaterial(source, 'glass', false);
  assert.equal(source.color.getHex(), 0x123456);
  assert.ok(glass.transmission > 0.5);
  assert.equal(light.transmission, 0);
  assert.ok(light.transparent);
  assert.ok(light.opacity < 1);
  assert.ok(
    displayMaterial(source, 'brick', true).roughness >
      displayMaterial(source, 'metal', true).roughness,
  );
});
for (const kind of ['wood', 'brick'])
  void test(`${kind}: shader hooks target current Three.js chunks`, () => {
    const m = displayMaterial(new MeshStandardMaterial(), kind, true);
    const shader = {
      vertexShader: ShaderLib.physical.vertexShader,
      fragmentShader: ShaderLib.physical.fragmentShader,
      uniforms: {},
    } as WebGLProgramParametersWithUniforms;
    m.onBeforeCompile(shader, {} as WebGLRenderer);
    assert.ok(shader.vertexShader.includes('vLabUV=uv'));
    assert.ok(shader.vertexShader.includes('vLabPosition=(modelMatrix'));
    assert.ok(
      shader.fragmentShader.includes(
        kind === 'wood' ? 'grainPhase' : 'brickMask',
      ),
    );
    assert.ok(shader.fragmentShader.includes('diffuseColor.rgb'));
  });
