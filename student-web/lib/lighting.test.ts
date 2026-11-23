import { test } from 'node:test';
import assert from 'node:assert/strict';
import { PCFShadowMap } from 'three';
import { studyLights, shadowType, environmentIntensity } from './lighting.ts';
void test('soft lighting uses radius-aware filtering and balanced fill', () => {
  const { sky, sun } = studyLights(true);
  assert.equal(shadowType, PCFShadowMap);
  assert.equal(sun.shadow.radius, 4);
  assert.ok(sun.shadow.intensity < 1);
  assert.ok(sky.intensity >= 1 && environmentIntensity > 0.55);
  assert.equal(sun.shadow.mapSize.x, 2048);
  assert.equal(sun.castShadow, true);
  assert.equal(studyLights(false).sun.castShadow, false);
});
